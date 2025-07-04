from ...src.core.abstract.GenerationPipeLineBase import GenerationPipeLineBase
from ...src.core.dataclass.genPipeline_context import GenPipelineContext
from ...src.core.dataclass.pgao_context import PGAOcontext
from ..util.utils import get_val_plus_delta
from decimal import Decimal

def fmt(v):
    if (type(v) is not int) or (type(v) is not Decimal) or (type(v) is not float):
        return f"'{v}'"
    else:
        return f"{v}"

class PredicateSeparator(GenerationPipeLineBase):
    def __init__(self, connectionHelper, genPipelineCtx: GenPipelineContext,
                 genCtx: PGAOcontext):
        super().__init__(connectionHelper, "Limit", genPipelineCtx)
        self.genPipelineCtx = genPipelineCtx
        self.genCtx = genCtx

    def query_QJ(self):
        if self.core_relations is None:
            return ''
        core_relation_list = ", ".join([str(r) for r in self.core_relations])
        projection_list = ", ".join([str(r) if aggr is None else f"{aggr}({str(r)})" for r, aggr in self.genCtx.aggregated_attributes])
        predicate = []
        for join in self.genPipelineCtx.joined_graph2:
            predicate.extend([f'{a[0]}.{a[1]} = {b[0]}.{b[1]}' for a, b in zip(join, join[1:])])
        query = f'SELECT {projection_list} FROM {core_relation_list}'
        if predicate:
            query += f'\n\tWHERE {" AND ".join(predicate)}'
        if self.genCtx.group_by_attrib2:
            groupby_list = [f'{table}.{attrib}' for table, attrib in self.genCtx.group_by_attrib2]
            query += f'\n\tGROUP BY {", ".join(groupby_list)}'
        query += ";"
        return query

    def saperation_test(self, sum_predicates, mtable, mattrib, k1, k2, QJ, QH):
        for table in self.core_relations:
            qtable = self.get_fully_qualified_table_name(table)
            table1 = table + '_t1'
            table2 = table + '_t2'
            qtable1 = self.get_fully_qualified_table_name(table1)
            qtable2 = self.get_fully_qualified_table_name(table2)
            
            self.connectionHelper.execute_sql([f"CREATE TABLE {table1} (LIKE {qtable});"])
            self.connectionHelper.execute_sql([f"CREATE TABLE {table2} (LIKE {qtable});"])
            self.connectionHelper.execute_sql([f"INSERT INTO {qtable1} (SELECT * FROM {qtable} LIMIT 1);"])
            self.connectionHelper.execute_sql([f"INSERT INTO {qtable2} (SELECT * FROM {qtable} LIMIT 1);"])
        
        for sp in sum_predicates:
            sp_tab, sp_attrib = sp
            sp_qtab = self.get_fully_qualified_table_name(sp_tab)
            self.connectionHelper.execute_sql([f"UPDATE {sp_qtab}_t2 SET {sp_attrib}=NULL;"])
            
        for join in self.genPipelineCtx.joined_graph2:
            for j in join:
                j_tab, j_attr = j
                j_qtab = self.get_fully_qualified_table_name(j_tab)
                j_dtype = self.get_datatype(j)

                v1 = self.connectionHelper.execute_sql_fetchone_0(f"SELECT {j_attr} FROM {j_qtab};")
                v2 = get_val_plus_delta(j_dtype, v1, 1)
                self.connectionHelper.execute_sql([f"UPDATE {j_qtab}_t1 SET {j_attr}={fmt(v1)};"])
                self.connectionHelper.execute_sql([f"UPDATE {j_qtab}_t2 SET {j_attr}={fmt(v2)};"])
                
        mqtable = self.get_fully_qualified_table_name(mtable)
        self.connectionHelper.execute_sql([f"UPDATE {mqtable}_t1 SET {mattrib}={fmt(k1)};"])
        self.connectionHelper.execute_sql([f"UPDATE {mqtable}_t2 SET {mattrib}={fmt(k2)};"])

        for table in self.core_relations:
            qtable = self.get_fully_qualified_table_name(table)
            table1 = table + '_t1'
            qtable1 = self.get_fully_qualified_table_name(table1)

            self.connectionHelper.execute_sql([f"TRUNCATE TABLE {qtable};"])
            self.connectionHelper.execute_sql([f"INSERT INTO {qtable} (SELECT * FROM {qtable1} LIMIT 1);"])
            self.connectionHelper.execute_sql([f"DROP TABLE {qtable1};"])

        r1, _ = self.connectionHelper.execute_sql_fetchall(QJ)

        for table in self.core_relations:
            qtable = self.get_fully_qualified_table_name(table)
            table2 = table + '_t2'
            qtable2 = self.get_fully_qualified_table_name(table2)

            self.connectionHelper.execute_sql([f"INSERT INTO {qtable} (SELECT * FROM {qtable2} LIMIT 1);"])
            self.connectionHelper.execute_sql([f"DROP TABLE {qtable2};"])

        r2, _ = self.connectionHelper.execute_sql_fetchall(QH)
        
        return r1 == r2
    
    def doExtractJob(self, query):
        join_only_query = self.query_QJ()
        hidden_query = query
        
        sum_preds = [(p[0], p[1]) for p in self.genPipelineCtx.having_predicates if p[2] == "SUM"]
        seperatable_preds = [p for p in self.genPipelineCtx.having_predicates if (p[2] == "MIN" and p[4] is not None) or (p[2] == "MAX" and p[3] is not None)]
        other_having_preds = [p for p in self.genPipelineCtx.having_predicates if p not in seperatable_preds]
        new_filter_preds = []
        
        
        
        for sp in seperatable_preds:
            sp_tab, sp_attr, sp_aggr, sp_l, sp_u = sp
            sp_dtype = self.get_datatype((sp_tab, sp_attr))
            self.connectionHelper.begin_transaction()
            if sp_aggr == 'MIN':
                # Can be MIN or Filter <= b
                b = sp_u
                bp1 = get_val_plus_delta(sp_dtype, b, 1)
                if self.saperation_test(sum_preds, sp_tab, sp_attr, b, bp1, join_only_query, hidden_query):
                    # Filter
                    if sp_l is not None:
                        new_filter_preds.append((sp_tab, sp_attr, '>=', sp_l))
                    new_filter_preds.append((sp_tab, sp_attr, '<=', sp_u))
                else:
                    other_having_preds.append(sp)

            elif sp_aggr == 'MAX':
                # Can be a <= MAX or Filter
                a = sp_l
                am1 = get_val_plus_delta(sp_dtype, a, -1)
                if self.saperation_test(sum_preds, sp_tab, sp_attr, a, am1, join_only_query, hidden_query):
                    # Filter
                    if sp_u is not None:
                        new_filter_preds.append((sp_tab, sp_attr, '<=', sp_u))
                    new_filter_preds.append((sp_tab, sp_attr, '>=', sp_l))
                else:
                    # Having
                    other_having_preds.append(sp)
            self.connectionHelper.rollback_transaction()
        
        self.genPipelineCtx.having_predicates = other_having_preds
        self.genPipelineCtx.filter_predicates.extend(new_filter_preds)

        return True