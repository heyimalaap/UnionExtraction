from ..core.abstract.MinimizerBase import Minimizer
from ..util.utils import get_val_plus_delta, get_format
from ..util.constants import TEXT_TYPES
from copy import deepcopy

class GroupBy(Minimizer):
    def __init__(self, connectionHelper, 
                core_relations,
                all_attribs,
                all_sizes,
                join_graph):
        super().__init__(connectionHelper, 
                         core_relations, 
                         all_sizes, 
                         "Group_By")
        self.all_attribs = all_attribs
        self.attrib_types_dict = self.init_attrib_types_dict()
        self.groupby_attribs = []
        self.groupby_attribs_join_reduced = []
        self.join_graph = join_graph
        
    def doActualJob(self, args):
        self.query = self.extract_params_from_args(args)
        
        for table in self.core_relations:
            for attrib in self.all_attribs[table]:
                has_groupby = self.check_groupby_attrib(table, attrib)
                
                if has_groupby:
                    self.groupby_attribs.append((table, attrib))
        
        self.groupby_attribs_join_reduced = self.join_reduce_groupby()
        
    def init_attrib_types_dict(self):
        """Enquire the database about the types of all the attributes in each table
        """
        attrib_types_dict = dict()
        for table in self.core_relations:
            res, _ = self.connectionHelper.execute_sql_fetchall(
                self.connectionHelper.queries.get_column_details_for_table(self.connectionHelper.config.schema, table))
            
            this_attribs = [(table, row[0].lower(), row[1].lower()) for row in res]
            for entry in this_attribs:
                attrib_types_dict[(entry[0], entry[1])] = entry[2]
        return attrib_types_dict
    
    def get_datatype(self, table, attrib):
        """Returns the datatype of table.attrib

        Args:
            table (str): Name of the table
            attrib (str): Name of the attribute

        Returns:
            str: Datatype of the attribute
        """
        return self.attrib_types_dict[(table, attrib)]

    def join_reduce_groupby(self):
        """Returns a reduced set of group by list, where only one attribute from each join is present
        in case multiple attributes belong to the same join.

        Returns:
            list: New list of reduced group by attributes in the format [(tab, attrib), ...]
        """
        groupby_attribs_join_reduced = deepcopy(self.groupby_attribs)
        for join in self.join_graph:
            for j in join:
                if j in groupby_attribs_join_reduced:
                    to_remove = deepcopy(join)
                    to_remove.remove(j)
                    
                    for r in to_remove:
                        if r in groupby_attribs_join_reduced:
                            groupby_attribs_join_reduced.remove(r)
        
        return groupby_attribs_join_reduced
                        
                    
    def join_graph_closure_sql_updates(self, table, attrib, value):
        """Generates a set of SQL to add a copy of table at the end of itself 
        except with (table.attrib) having a new value `value`

        Args:
            table (str): Name of the table
            attrib (str): Name of the attribute
            value (any): value to append

        Returns:
            list: List of SQL queries to achieve this
        """
        updates = []
        
        for join in self.join_graph:
            if (table, attrib) in join:
                for j_table, j_attrib in join:
                    fq_j_table = self.get_fully_qualified_table_name(j_table)
                    fq_tmp_j_table = f"{fq_j_table}_tmp"
                    updates.append(self.connectionHelper.queries.create_table_as_select_star_from(fq_tmp_j_table, fq_j_table))
                    updates.append(self.connectionHelper.queries.update_tab_attrib_with_value(fq_j_table, j_attrib, value))
                    updates.append(self.connectionHelper.queries.insert_into_tab_select_star_fromtab(fq_j_table, fq_tmp_j_table))
                    updates.append(self.connectionHelper.queries.drop_table(fq_tmp_j_table))
                return updates
        
        # (table, attrib) not in join (because there was no early return)
        fq_table_name = self.get_fully_qualified_table_name(table)
        fq_tmp_table_name = f"{fq_table_name}_tmp"
        updates.append(self.connectionHelper.queries.create_table_as_select_star_from(fq_tmp_table_name, fq_table_name))
        updates.append(self.connectionHelper.queries.update_tab_attrib_with_value(fq_table_name, attrib, value))
        updates.append(self.connectionHelper.queries.insert_into_tab_select_star_fromtab(fq_table_name, fq_tmp_table_name))
        updates.append(self.connectionHelper.queries.drop_table(fq_tmp_table_name))
        return updates
        
    def check_groupby_attrib(self, table, attrib):
        """Check if table.attrib has group by on it or not.

        Args:
            table (str): Name of the table
            attrib (str): Name of the attribute

        Returns:
            bool: returns True if table.attrib is a group by attribute, False otherwise.
        """
        datatype = self.get_datatype(table, attrib)
        fq_table_name = self.get_fully_qualified_table_name(table)
        has_groupby = False
        
        # If the attribute `attrib` does not have the same value in all rows of the
        # table `table`, then the attribute `attrib` is definately not a group by attribute
        # If not, let the common value be `val`
        val = self.get_common_attrib_value(table, attrib)
        if val is None:
            return False
        
        if datatype in TEXT_TYPES:
            val_plus_one = get_format(datatype, 'a') if val != 'a' else get_format(datatype, 'b')
            val_minus_one = get_format(datatype, 'a') if val != 'a' else get_format(datatype, 'b')
        else:
            val_plus_one = get_format(datatype, get_val_plus_delta(datatype, val, 1))
            val_minus_one = get_format(datatype, get_val_plus_delta(datatype, val, -1))

        self.connectionHelper.begin_transaction()
        self.connectionHelper.execute_sql(self.join_graph_closure_sql_updates(table, attrib, val_plus_one))
        res, _ = self.connectionHelper.execute_sql_fetchall(self.query)
        if len(res) >= 2:
            has_groupby = True
        self.connectionHelper.rollback_transaction()
        
        if has_groupby:
            return has_groupby
        
        self.connectionHelper.begin_transaction()
        self.connectionHelper.execute_sql(self.join_graph_closure_sql_updates(table, attrib, val_minus_one))
        res, _ = self.connectionHelper.execute_sql_fetchall(self.query)
        if len(res) >= 2:
            has_groupby = True
        self.connectionHelper.rollback_transaction()
        return has_groupby
        
    def get_common_attrib_value(self, table:str, attrib: str):
        """This function gets the value in table.attrib if all the rows in the table
        `table` has the same value. Otherwise, this function returns NULL

        Args:
            table (str): Name of the table
            attrib (str): Name of the attribute
        """
        
        vals, _ = self.connectionHelper.execute_sql_fetchall(
            self.connectionHelper.queries.select_attribs_from_relation(
                [attrib], table
                )
            )
        vals = list(map(lambda x: x[0], vals))

        v0 = vals[0] if len(vals) != 0 else None
        if all([v == v0 for v in vals]):
            return v0

        return None