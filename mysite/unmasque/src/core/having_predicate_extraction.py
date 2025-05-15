from ..core.abstract.MinimizerBase import Minimizer
from ..util.utils import get_min_and_max_val, get_val_plus_delta
from ..util.constants import NUMERIC_TYPES, TEXT_TYPES, INT_TYPES, NUMBER_TYPES
from typing import Literal, Any, Tuple
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
import datetime
import math
from itertools import combinations

# Implementation notes:
# - For now, let us not support having predicates on group by attributes.
#   That is, group by attributes can only have filter predicates on them.

def fmt(v):
    if (type(v) is not int) or (type(v) is not Decimal) or (type(v) is not float):
        return f"'{v}'"
    else:
        return f"{v}"

def all_combs(l):
    res = []
    for i in range(0, len(l) + 1):
        els = [list(x) for x in combinations(l, i)]
        res.extend(els)
    return res

class PredicateExtractor(Minimizer):
    def __init__(self, connectionHelper,
                 core_relations, 
                 all_attribs,
                 attrib_types_dict,
                 groupby_attribs,
                 all_sizes,
                 pk_dict,
                 join_graphs):
        super().__init__(connectionHelper, core_relations, all_sizes, "Predicate Extractor")
        self.all_atribs = all_attribs
        self.attrib_types_dict = attrib_types_dict
        self.groupby_attrib = groupby_attribs
        self.pk_attribs = self.get_pk_attribs(pk_dict)
        self.hidden_query = ''
        self.having_predicates = []
        self.filter_predicates = []
        self.seperable_predicates = []
        self.filter_attrib_dict = dict() # TODO: Document this datastructure better. I'm pretty sure this is redundant.
        self.join_graphs = join_graphs
        
    def get_pk_attribs(self, pk_dict):
        pk_attribs = []
        for key in pk_dict:
            attrib_list = pk_dict[key].split(',')
            for attrib in attrib_list:
                pk_attribs.append((key, attrib))
        
        return pk_attribs
    
    def get_datatype(self, tab_attrib: Tuple[str, str]) -> str:
        if any(x in self.attrib_types_dict[tab_attrib] for x in INT_TYPES):
            return 'int'
        elif 'date' in self.attrib_types_dict[tab_attrib]:
            return 'date'
        elif any(x in self.attrib_types_dict[tab_attrib] for x in TEXT_TYPES):
            return 'str'
        elif any(x in self.attrib_types_dict[tab_attrib] for x in NUMERIC_TYPES):
            return 'numeric'
        else:
            raise ValueError(f"Datatype '{self.attrib_types_dict[tab_attrib]}' for attribute '{tab_attrib[1]}' in table '{tab_attrib[0]}' is not supported.")

    def doActualJob(self, args):
        self.hidden_query = self.extract_params_from_args(args)
        
        for g_table, g_attrib in self.groupby_attrib:
            if not (g_table, g_attrib) in self.pk_attribs:
                predicates = self.get_filter_predicate(g_table, g_attrib)
                if predicates is not None:
                    self.filter_predicates.extend(predicates)
        
        predicate_candidates = []
        for table in self.core_relations:
            for attrib in self.all_atribs[table]:
                tab_attrib = (table, attrib)
                if self.get_datatype((table, attrib)) not in ['int', 'date', 'numeric']:
                    continue
                
                if tab_attrib in self.groupby_attrib:
                    continue
                
                if tab_attrib in self.pk_attribs:
                    continue

                in_join_graph = False
                for jg in self.join_graphs:
                    if tab_attrib in jg:
                        in_join_graph = True
                if in_join_graph:
                    continue

                # TODO: Support MIN/MAX for date types!
                if self.get_datatype((table, attrib)) == 'date':
                    predicates = self.get_filter_predicate(table, attrib)
                    if predicates is not None:
                        self.filter_predicates.extend(predicates)
                    continue

                lb = self.get_lower_bound(table, attrib)
                ub = self.get_upper_bound(table, attrib)
                min_val, max_val = get_min_and_max_val(self.get_datatype((table, attrib)))
                self.filter_attrib_dict[(table, attrib)] = (min_val if lb is None else lb, max_val if ub is None else ub)
                self.logger.debug(f"{table}.{attrib} | LB {lb} | UB {ub}")

                if lb is not None or ub is not None:
                    predicate_candidates.append((table, attrib, lb, ub))
        
        self.logger.info("Finished extracting predicate candidates.")

        check = self.deflate_core_tables(predicate_candidates)
        if not check:
            return False
        self.logger.info("Finished creating deflated database instance")
        
        nonnullable_attributes = self.find_nonnullable_attributes(predicate_candidates)

        filter_preds, having_preds = self.identify_aggregations(predicate_candidates, nonnullable_attributes)
        
        self.filter_predicates.extend(filter_preds)
        self.having_predicates.extend(having_preds)
        return True
    
    def identify_aggregations(self, predicate_candidates, nonnullable_attributes):
        filter_preds = []
        having_preds = []

        for pc in predicate_candidates:
            pc_tab, pc_attrib, pc_lb, pc_ub = pc

            # If its a nonnullable, then we know its a filter predicate
            if (pc_tab, pc_attrib) in nonnullable_attributes:
                if pc_lb is not None:
                    filter_preds.append((pc_tab, pc_attrib, ">=", pc_lb))
                if pc_ub is not None:
                    filter_preds.append((pc_tab, pc_attrib, "<=", pc_ub))
                continue

            aggr = None
            if pc_ub is not None:
                if pc_ub == 0 and pc_lb is not None:
                    aggr = self.identify_aggregations_lb(predicate_candidates, nonnullable_attributes, pc_tab, pc_attrib, pc_lb)
                aggr = self.identify_aggregations_ub(predicate_candidates, nonnullable_attributes, pc_tab, pc_attrib, pc_ub)
            else:
                aggr = self.identify_aggregations_lb(predicate_candidates, nonnullable_attributes, pc_tab, pc_attrib, pc_lb)
            
            having_preds.append((pc_tab, pc_attrib, aggr, pc_lb, pc_ub))
        
        return filter_preds, having_preds
    
    def identify_aggregations_ub(self, predicate_candidates, nonnullables, table, attr, u):
        def cvp(k1, k2):
            return self.check_value_pair(predicate_candidates, nonnullables, table, attr, k1, k2)

        if (u > 0):
            if cvp(2*u, u):
                return "MIN"
            elif cvp(2*u, 0):
                return "AVG"
            elif cvp(u, u):
                return "MAX"
            else:
                return "SUM"
        else:
            if cvp(u/2, u/2):
                return "SUM"
            elif cvp(u, 0):
                return "MIN"
            elif cvp(2*u, 0):
                return "AVG"
            else:
                return "MAX"

    def identify_aggregations_lb(self, predicate_candidates, nonnullables, table, attr, l):
        def cvp(k1, k2):
            return self.check_value_pair(predicate_candidates, nonnullables, table, attr, k1, k2)
        
        if (l > 0):
            if cvp(l/2, l/2):
                return "SUM"
            elif cvp(l, 0):
                return "MAX"
            elif cvp(2*l, 0):
                return "AVG"
            else:
                return "MIN"
        else:
            if cvp(2*l, l):
                return "MAX"
            elif cvp(2*l, 0):
                return "AVG"
            elif cvp(l, l):
                return "MIN"
            else:
                return "SUM"
    
    def check_value_pair(self, predicate_candidates, nonnullables, table, attr, k1, k2):
        qtable = self.get_fully_qualified_table_name(table)
        nullables = [pc[1] for pc in predicate_candidates if pc[0] == table and (pc[0], pc[1]) not in nonnullables]

        self.connectionHelper.begin_transaction()
        self.make_two_row_join(predicate_candidates, nonnullables)
        if len(nonnullables) != 0:
            for nullable in nullables:
                ctids, _= self.connectionHelper.execute_sql_fetchall(f"SELECT ctid FROM {qtable};")
                _, r2 = ctids[0][0], ctids[1][0]
                self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {nullable}=NULL WHERE ctid='{r2}';"])

        ctids, _= self.connectionHelper.execute_sql_fetchall(f"SELECT ctid FROM {qtable};")
        r1, r2 = ctids[0][0], ctids[1][0]
        self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attr}={fmt(k1)} WHERE ctid='{r1}';"])
        self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attr}={fmt(k2)} WHERE ctid='{r2}';"])
        
        res = self.sanity_check(self.hidden_query, critical=False)

        self.connectionHelper.rollback_transaction()
        return res
    
    def make_two_row_join(self, predicate_candidates, nonnullables):
        vmap = dict()
        for table in self.core_relations:
            qtable = self.get_fully_qualified_table_name(table)
            attribs = [p[1] for p in predicate_candidates if p[0] == table]
            
            for attrib in attribs:
                v = self.connectionHelper.execute_sql_fetchone_0(f"SELECT {attrib} FROM {qtable};")
                vmap[(table, attrib)] = v

        for table in self.core_relations:
            qtable = self.get_fully_qualified_table_name(table)
            self.connectionHelper.execute_sql([f"INSERT INTO {qtable} (SELECT * FROM {qtable});"])
            
        for jg in self.join_graphs:
            jg_tab, jg_attr = jg[0]
            jg_qtab = self.get_fully_qualified_table_name(jg_tab)
            jg_dtype = self.get_datatype(jg[0])

            v1 = self.connectionHelper.execute_sql_fetchone_0(f"SELECT {jg_attr} FROM {jg_qtab};")
            v2 = get_val_plus_delta(jg_dtype, v1, 1)
            
            for join in jg:
                j_tab, j_attr = join
                j_qtab = self.get_fully_qualified_table_name(j_tab)
                
                ctids, _ = self.connectionHelper.execute_sql_fetchall(f"SELECT ctid FROM {j_qtab};")
                ctids = sorted([ctid[0] for ctid in ctids])
                r1, r2 = ctids[0], ctids[1]
                
                self.connectionHelper.execute_sql([f"UPDATE {j_qtab} SET {j_attr}={fmt(v1)} WHERE ctid='{r1}';"])
                self.connectionHelper.execute_sql([f"UPDATE {j_qtab} SET {j_attr}={fmt(v2)} WHERE ctid='{r2}';"])

        for table in self.core_relations:
            qtable = self.get_fully_qualified_table_name(table)
            attribs = [p[1] for p in predicate_candidates if p[0] == table]
            for attrib in attribs:
                ctids, _ = self.connectionHelper.execute_sql_fetchall(f"SELECT ctid FROM {qtable};")
                ctids = sorted([ctid[0] for ctid in ctids])
                r1, r2 = ctids[0], ctids[1]
                v = vmap[((table, attrib))]
                self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attrib}={fmt(v)} WHERE ctid='{r1}';"])
                if ((table, attrib) in nonnullables) or (len(nonnullables) == 0):
                    self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attrib}={fmt(v)} WHERE ctid='{r2}';"])
                else:
                    self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attrib}=NULL WHERE ctid='{r2}';"])
                    
            

    def find_nonnullable_attributes(self, predicate_candidates):
        tables = set([p[0] for p in predicate_candidates])
        nonnullable_attributes = []
        
        for table in tables:
            qtable = self.get_fully_qualified_table_name(table)
            attribs = [p[1] for p in predicate_candidates if p[0] == table]
            
            self.connectionHelper.begin_transaction()
            vmap = dict()
            for attrib in attribs:
                v = self.connectionHelper.execute_sql_fetchone_0(f"SELECT {attrib} FROM {qtable};")
                vmap[attrib] = v
            
            self.connectionHelper.execute_sql([f"INSERT INTO {qtable} (SELECT * FROM {qtable});"])
            
            if self.sanity_check(self.hidden_query, critical=False):
                # We have non empty result! Then both rows are participating
                self.connectionHelper.rollback_transaction()
                continue

            attrib_map = dict()
            for attrib in attribs:
                attrib_map[attrib] = False
            
            for comb in all_combs(attribs):
                for attrib in attribs:
                    v = vmap[attrib]
                    self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attrib}={fmt(v)};"])

                    ctids, _= self.connectionHelper.execute_sql_fetchall(f"SELECT ctid FROM {qtable};")
                    _, r2 = ctids[0][0], ctids[1][0]

                    if attrib in comb:
                        self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attrib}=NULL WHERE ctid='{r2}';"])
                    else:
                        self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attrib}={fmt(v)} WHERE ctid='{r2}';"])
                
                if not self.sanity_check(self.hidden_query, critical=False):
                    for a in comb:
                        attrib_map[a] = True
            
            tab_nonnullables = []
            for a in attrib_map:
                if attrib_map[a] == False:
                    tab_nonnullables.append(a)
            
            # There could be <= 1 sum pred in tab_nonnullables
            to_remove = None
            for a in tab_nonnullables:
                for attrib in attribs:
                    v = vmap[attrib]
                    self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attrib}={fmt(v)};"])
                ctids, _= self.connectionHelper.execute_sql_fetchall(f"SELECT ctid FROM {qtable};")
                _, r2 = ctids[0][0], ctids[1][0]
                self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {a}=NULL WHERE ctid='{r2}';"])
                if self.sanity_check(self.hidden_query, critical=False):
                    to_remove = a
                    break

            if to_remove is not None:
                tab_nonnullables.remove(to_remove)

            paired_tab_nonnullables = [(table, a) for a in tab_nonnullables]
            nonnullable_attributes.extend(paired_tab_nonnullables)

            self.connectionHelper.rollback_transaction()
        
        return nonnullable_attributes
    
    def deflate_core_tables(self, predicate_candidates):
        self.connectionHelper.begin_transaction()
        for table in self.core_relations:
            qtable = self.get_fully_qualified_table_name(table)
            self.connectionHelper.execute_sql([f"ALTER TABLE {qtable} RENAME TO {table}_tmp;"])
            self.connectionHelper.execute_sql([f"CREATE TABLE {qtable} (LIKE {qtable}_tmp);"])
            self.connectionHelper.execute_sql([f"INSERT INTO {qtable} (SELECT * FROM {qtable}_tmp LIMIT 1);"])
            self.connectionHelper.execute_sql([f"DROP TABLE {qtable}_tmp;"])

        for pred in self.filter_predicates:
            p_table, p_attrib, _, p_val = pred
            p_qtable = self.get_fully_qualified_table_name(p_table)
            p_val_fmt = fmt(p_val)
            self.connectionHelper.execute_sql([f"UPDATE {p_qtable} SET {p_attrib} = {p_val_fmt};"])

        for pred in predicate_candidates:
            p_table, p_attrib, p_lb, p_ub = pred
            p_qtable = self.get_fully_qualified_table_name(p_table)
            p_val = p_ub if p_ub is not None else p_lb
            if ((type(p_val) is int) or (type(p_val) is float) or (type(p_val) is Decimal)) and (p_val > 0) and (p_lb is not None):
                p_val = p_lb
            p_val_fmt = fmt(p_val)
            self.connectionHelper.execute_sql([f"UPDATE {p_qtable} SET {p_attrib} = {p_val_fmt};"])

        if not self.sanity_check(self.hidden_query, critical=True):
            self.logger.error("Failed to create a deflated database instance")
            return False
        
        self.connectionHelper.commit_transaction()
        return True

                
    def get_lower_bound(self, table: str, attribute: str) -> Any:
        tab_attrib = (table, attribute)
        datatype = self.get_datatype(tab_attrib)
        min_val, _ = get_min_and_max_val(datatype)

        self.connectionHelper.begin_transaction()
        ctid_vals = self.get_ctid_attrib_val(table, attribute, sorted=True)
        v = None
        for _, (ctid, val) in enumerate(ctid_vals):
            v = self.binary_search(table, attribute, min_val, val, 'l', ctid)
            if v <= min_val:
                v_fmted = v
                if type(v) is not int:
                    v_fmted = f"'{v}'"
                qtable = self.get_fully_qualified_table_name(table)
                self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attribute} = {v_fmted} WHERE ctid='{ctid}';"])
                v = None
                continue

            v_fmted = v
            if type(v) is not int:
                v_fmted = f"'{v}'"
            qtable = self.get_fully_qualified_table_name(table)
            self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attribute} = {v_fmted} WHERE ctid='{ctid}';"])
            break

        self.connectionHelper.commit_transaction()
        # self.connectionHelper.rollback_transaction()

        # TODO: This is a hack to get decimal numbers working. Do this properly later
        if type(v) is Decimal:
            v = v.quantize(Decimal('0.00'))

        if v is None:
            return None

        # Check for valid bound
        candidate_bounds = [v]

        if datatype in NUMBER_TYPES:
            qtable = self.get_fully_qualified_table_name(table)
            res = self.connectionHelper.execute_sql_fetchone_0(f'SELECT SUM({qtable}.{attribute}) FROM {qtable};')
            candidate_bounds.append(res)

            res = self.connectionHelper.execute_sql_fetchone_0(f'SELECT AVG({qtable}.{attribute}) FROM {qtable};')
            candidate_bounds.append(res)

        candidate_bounds.sort()

        qtable = self.get_fully_qualified_table_name(table)
        self.connectionHelper.execute_sql([f'ALTER {qtable} ALTER COLUMN {attribute} DROP NOT NULL;'])
        for lb in candidate_bounds:
            self.connectionHelper.begin_transaction()

            self.connectionHelper.execute_sql([f'UPDATE {qtable} SET {attribute}=NULL;'])
            ctid_vals = self.get_ctid_attrib_val(table, attribute, sorted=True)
            first_ctid, _ = ctid_vals[0]

            lb_fmt = lb
            if type(lb) is not int:
                lb_fmt = f"'{lb}'"

            qtable = self.get_fully_qualified_table_name(table)
            self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attribute}={lb_fmt} WHERE ctid='{first_ctid}';"])
            was_empty = self.is_result_empty()

            self.connectionHelper.rollback_transaction()

            if not was_empty:
                return lb

        return v

    def get_upper_bound(self, table: str, attribute: str) -> Any:
        tab_attrib = (table, attribute)
        datatype = self.get_datatype(tab_attrib)
        _, max_val = get_min_and_max_val(datatype)

        self.connectionHelper.begin_transaction()
        ctid_vals = self.get_ctid_attrib_val(table, attribute, sorted=True)
        v = None
        # for i, (ctid, val) in reversed(list(enumerate(ctid_vals))):
        for i in range(len(ctid_vals) - 1, -1, -1):
            ctid, val = self.get_ctid_attrib_val(table, attribute, sorted=True)[i]
            v = self.binary_search(table, attribute, val, max_val, 'r', ctid)
            if v >= max_val:
                v_fmted = v
                if type(v) is not int:
                    v_fmted = f"'{v}'"
                qtable = self.get_fully_qualified_table_name(table)
                self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attribute} = {v_fmted} WHERE ctid='{ctid}';"])
                v = None
                continue

            v_fmted = v
            if type(v) is not int:
                v_fmted = f"'{v}'"
            qtable = self.get_fully_qualified_table_name(table)
            self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attribute} = {v_fmted} WHERE ctid='{ctid}';"])
            break

        self.connectionHelper.commit_transaction()
        # self.connectionHelper.rollback_transaction()

        # TODO: This is a hack to get decimal numbers working. Do this properly later
        if type(v) is Decimal:
            v = v.quantize(Decimal('0.00'))

        if v is None:
            return None

        # Check for valid bound
        candidate_bounds = [v]

        if datatype in NUMBER_TYPES:
            qtable = self.get_fully_qualified_table_name(table)
            res = self.connectionHelper.execute_sql_fetchone_0(f'SELECT SUM({qtable}.{attribute}) FROM {qtable};')
            candidate_bounds.append(res)

            res = self.connectionHelper.execute_sql_fetchone_0(f'SELECT AVG({qtable}.{attribute}) FROM {qtable};')
            candidate_bounds.append(res)

        candidate_bounds.sort(reverse=True)

        qtable = self.get_fully_qualified_table_name(table)
        self.connectionHelper.execute_sql([f'ALTER {qtable} ALTER COLUMN {attribute} DROP NOT NULL;'])

        for ub in candidate_bounds:
            self.connectionHelper.begin_transaction()

            self.connectionHelper.execute_sql([f'UPDATE {qtable} SET {attribute}=NULL;'])
            ctid_vals = self.get_ctid_attrib_val(table, attribute, sorted=True)
            first_ctid, _ = ctid_vals[0]

            ub_fmt = ub
            if type(ub) is not int:
                ub_fmt = f"'{ub}'"

            qtable = self.get_fully_qualified_table_name(table)
            self.connectionHelper.execute_sql([f"UPDATE {qtable} SET {attribute}={ub_fmt} WHERE ctid='{first_ctid}';"])
            was_empty = self.is_result_empty()

            self.connectionHelper.rollback_transaction()

            if not was_empty:
                return ub

        return v

        
    def is_result_empty(self):
        res, _ = self.connectionHelper.execute_sql_fetchall(self.hidden_query)
        return len(res) == 0
        
    def is_result_empty_with_attrib_value(self, table: str, attrib: str, value: Any, ctid = None, along_with_join_group = False):
        attrib_type = self.get_datatype((table, attrib))
        if attrib_type in TEXT_TYPES or attrib_type == 'date':
            value = f"'{value}'"

        self.connectionHelper.begin_transaction()
        qtable = self.get_fully_qualified_table_name(table)
        if ctid is None:
            # TODO: Lift this up to connectionHelper.queries
            self.connectionHelper.execute_sql([f'UPDATE {qtable} SET {attrib} = {value};'])
        else:
            # TODO: Lift this up to connectionHelper.queries
            self.connectionHelper.execute_sql([f'UPDATE {qtable} SET {attrib} = {value} WHERE ctid = \'{ctid}\';'])

        is_empty = self.is_result_empty()
        self.connectionHelper.rollback_transaction()
        return is_empty

    def get_ctid_attrib_val(self, table: str, attribute: str, sorted=True) -> list[tuple[str, Any]]:
        qtable = self.get_fully_qualified_table_name(table)
        res, _ = self.connectionHelper.execute_sql_fetchall(f'SELECT ctid, {attribute} FROM {qtable} ORDER BY {attribute};')
        return res

    def get_attrib_current_value(self, table: str, attrib: str):
        qtable = self.get_fully_qualified_table_name(table)
        res = self.connectionHelper.execute_sql_fetchone_0(f'SELECT DISTINCT({attrib}) from {qtable};')
        return res

    def binary_search(self, table: str, attrib: str, low, high, search_side: Literal['l'] | Literal['r'], ctid = None):
        attrib_type = self.get_datatype((table, attrib))
        min_val, max_val = get_min_and_max_val(attrib_type)
        
        if search_side == 'l':
            def mid_lb(l, h):
                if attrib_type == 'date':   
                    return l + datetime.timedelta(days=math.floor((h - l).days / 2))
                else:
                    if attrib_type in NUMERIC_TYPES:
                        l = Decimal(l)
                        h = Decimal(h)
                    res = math.floor((l + h) / 2)
                    if attrib_type in NUMERIC_TYPES:
                        res = Decimal(res)
                    return res

            # Coarse search
            def coarse_search_lb(low, x):
                if attrib_type != 'date':
                    l = Decimal(low)
                    h = Decimal(x)
                else:
                    l = low
                    h = x

                m = None
                while l < h:
                    m = mid_lb(l, h)
                    if not self.is_result_empty_with_attrib_value(table, attrib, m, ctid):
                        h = m
                    else:
                        m_plus_one = get_val_plus_delta(attrib_type, m, 1)
                        l = min(max_val, m_plus_one)

                if attrib_type != 'date':
                    h = int(h)
                return h


            # Refined search
            def refine_lb(lb, p = 2):
                p = 10 ** p

                l = Decimal(max(lb - 1, min_val))
                h = Decimal(lb)
                p_inv = 1/Decimal(p)

                m = None
                while l < h:
                    m = ((l + h) / 2).quantize(p_inv, rounding=ROUND_FLOOR)
                    if not self.is_result_empty_with_attrib_value(table, attrib, m, ctid):
                        h = m
                    else:
                        l = min(max_val, m + p_inv)

                return h

            lb = coarse_search_lb(low, high)
            if attrib_type in NUMERIC_TYPES:
                lb = refine_lb(lb)
            return lb

        elif search_side == 'r':
            def mid_ub(l, h):
                if attrib_type == 'date':
                    return l + datetime.timedelta(days=math.ceil((h - l).days / 2))
                else:
                    return math.ceil((l + h) / 2)

            # Coarse search
            def coarse_search_ub(x, high):
                if attrib_type != 'date':
                    l = Decimal(x)
                    h = Decimal(high)
                else:
                    l = x
                    h = high

                m = None
                while l < h:
                    m = mid_ub(l, h)
                    if not self.is_result_empty_with_attrib_value(table, attrib, m, ctid):
                        l = m
                    else:
                        m_minus_one = get_val_plus_delta(attrib_type, m, -1)
                        h = max(min_val, m_minus_one)

                if attrib_type != 'date':
                    l = int(l)
                return l

            # Refined search
            def refine_ub(ub, p = 2):
                p = 10 ** p

                l = Decimal(ub)
                h = Decimal(min(ub + 1, max_val))
                p_inv = 1/Decimal(p)

                m = None
                while l < h:
                    m = ((l + h) / 2).quantize(p_inv, rounding=ROUND_CEILING)
                    if not self.is_result_empty_with_attrib_value(table, attrib, m, ctid):
                        l = m
                    else:
                        h = m - p_inv

                return l

            ub = coarse_search_ub(low, high)
            if attrib_type in NUMERIC_TYPES:
                ub = refine_ub(ub)
            return ub
        return None
    
    def get_filter_predicate(self, table: str, attrib: str):
        if self.get_datatype((table, attrib)) in TEXT_TYPES:
            # TODO: Copy the string filter from the usual pipeline
            return None

        attrib_type = self.get_datatype((table, attrib))
        min_val, max_val = get_min_and_max_val(attrib_type)
        val = self.get_attrib_current_value(table, attrib)
        r1_is_phi = self.is_result_empty_with_attrib_value(table, attrib, min_val)
        r2_is_phi = self.is_result_empty_with_attrib_value(table, attrib, max_val)

        if not r1_is_phi and not r2_is_phi:
            return None

        l = None
        r = None
        if r1_is_phi:
            l = self.binary_search(table, attrib, min_val, val, 'l')

        if r2_is_phi:
            r = self.binary_search(table, attrib, val, max_val, 'r')

        self.logger.debug(f'{(table, attrib)}, r1 = {r1_is_phi}, r2 = {r2_is_phi}, l = {l}, r = {r}')
        predicates = []
        if r1_is_phi:
            predicates.append((table, attrib, ">=", l))

        if r2_is_phi:
            predicates.append((table, attrib, "<=", r))

        # TODO: This is here for legacy code compat. Is this even required?
        self.filter_attrib_dict[(table, attrib)] = (min_val if l is None else l, max_val if r is None else r)

        return predicates
