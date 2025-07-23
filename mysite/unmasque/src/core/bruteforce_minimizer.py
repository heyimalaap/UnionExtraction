from .abstract.MinimizerBase import Minimizer
from ..util.constants import NUMBER_TYPES
from typing import Any

def extract_start_and_end_page(logger, rctid):
    min_ctid = rctid[0]
    min_ctid2 = min_ctid.split(",")
    start_page = int(min_ctid2[0][1:])
    max_ctid = rctid[1]
    logger.debug(max_ctid)
    max_ctid2 = max_ctid.split(",")
    end_page = int(max_ctid2[0][1:])
    start_ctid = min_ctid
    end_ctid = max_ctid
    return end_ctid, end_page, start_ctid, start_page

class BruteForceMinimizer(Minimizer):
    def __init__(self, connectionHelper, core_relations, all_sizes, sampling_status):
        super().__init__(connectionHelper, core_relations, all_sizes, "BruteforceMinimizer")
        
        # Get list of columns for all tables
        self.global_all_attribs = dict()
        for table in self.core_relations:
            self.global_all_attribs[table] = self.get_attributes_for_table(table)
        
    def doActualJob(self, args=None):
        self.query = self.extract_params_from_args(args)
        
        # sanity_check returns true if DB(query) gives populated result
        if not self.sanity_check(self.query):
            self.logger.error("Original database is not giving populated result!")
            return False
        
        self.perform_binary_halving()
        
        return self.start_bruteforce_minimization()
    
    def perform_binary_halving(self):
        """
        Performs binary halving to minimize the database till it cannot be done.
        (i.e keeping either halfs give us an empty result). Used as a huristic
        to speed up the minimization.
        """
        core_sizes = self.getCoreSizes()
        for table in self.core_relations:
            view_name = self._get_dirty_name(table) 
            q1 = self.connectionHelper.queries.alter_table_rename_to(self.get_fully_qualified_table_name(table), view_name)
            self.connectionHelper.execute_sql([q1])
            q2 = self.connectionHelper.queries.get_min_max_ctid(self.get_fully_qualified_table_name(view_name))
            rctid = self.connectionHelper.execute_sql_fetchone(q2)
            core_sizes = self.do_interPage_viewBased_binary_halving(core_sizes, self.query, table, rctid, view_name)

    def do_interPage_viewBased_binary_halving(self, core_sizes,
                                              query,
                                              tabname,
                                              rctid,
                                              dirty_tab):
        end_ctid, end_page, start_ctid, start_page = extract_start_and_end_page(self.logger, rctid)
        while start_page < end_page - 1:
            mid_page = int((start_page + end_page) / 2)
            mid_ctid1 = "(" + str(mid_page) + ",1)"
            mid_ctid2 = "(" + str(mid_page) + ",2)"

            nend_ctid, nstart_ctid = self.create_view_execute_app_drop_view(end_ctid,
                                                                            mid_ctid1, mid_ctid2, query,
                                                                            start_ctid, tabname, dirty_tab)
            if nend_ctid is None:
                break
            else:
                start_ctid = nstart_ctid
                end_ctid = nend_ctid
            start_ctid2 = start_ctid.split(",")
            start_page = int(start_ctid2[0][1:])
            end_ctid2 = end_ctid.split(",")
            end_page = int(end_ctid2[0][1:])

        core_sizes = self.update_with_remaining_size(core_sizes, end_ctid, start_ctid, tabname, dirty_tab)
        return core_sizes

    def get_start_and_end_ctids(self, core_sizes, query, tabname, dirty_tab):
        end_ctid, mid_ctid1, mid_ctid2, start_ctid = self.get_mid_ctids(core_sizes, tabname, dirty_tab)

        if mid_ctid1 is None:
            return None, None

        self.logger.debug(start_ctid, mid_ctid1, mid_ctid2, end_ctid)
        end_ctid, start_ctid = self.create_view_execute_app_drop_view(end_ctid,
                                                                      mid_ctid1,
                                                                      mid_ctid2,
                                                                      query,
                                                                      start_ctid,
                                                                      tabname,
                                                                      dirty_tab)
        return end_ctid, start_ctid

    def get_most_frequent_values(self, skip_set: set) -> list[tuple[str, str, Any]]:
        """
        Returns a list of (table, attrib, value) in sorted order of frequency.
        From most frequent to least frequent.
        
        Args:
            skip_set (set): Set of (table, attrib) that has already been minimized

        Returns:
            list[tuple[str, str, Any]]: (table, attrib, value) in sorted order of frequency
        """
        freqs = dict()
        for table in self.core_relations:
            for attrib in self.global_all_attribs[table]:
                # Skip table and attribute if it is already minimized
                if (table, attrib) in skip_set:
                    continue
                qualified_table_name = self.get_fully_qualified_table_name(table)
                res, _ = self.connectionHelper.execute_sql_fetchall(
                    self.connectionHelper.queries.select_column_and_count_group_by_column(
                        qualified_table_name, attrib
                    )
                )
                for row in res:
                    val, freq = row
                    freqs[(table, attrib, val)] = freq
                    
        return sorted([v for v in freqs.keys()], key=lambda x: freqs[x], reverse=True)
        
    def get_attributes_for_table(self, table: str) -> list[str]:
        """
        Given a table name, returns a list of attributes.

        Args:
            table (str): Name of the table

        Returns:
            list[str]: List of attributes for that table
        """
        
        res, _ = self.connectionHelper.execute_sql_fetchall(
            self.connectionHelper.queries.get_column_details_for_table(self.connectionHelper.config.schema, table)
        )
        attribs = []
        for row in res:
            attribs.append(row[0].lower())
        
        return attribs
    
    def try_remove_a_row(self, table) -> bool:
        qtable = self.get_fully_qualified_table_name(table)
        ctid_query = self.connectionHelper.queries.get_ctid_from("", qtable)
        ctids, _ = self.connectionHelper.execute_sql_fetchall(ctid_query)
        ctids = [ctid[0] for ctid in ctids]
        
        for ctid in ctids:
            delete_query = f"DELETE FROM {qtable} WHERE ctid='{ctid}';"
            self.connectionHelper.begin_transaction()
            self.connectionHelper.execute_sql([delete_query])
            if self.sanity_check(self.query, critical=False):
                self.connectionHelper.commit_transaction()
                return True
            else:
                self.connectionHelper.rollback_transaction()

        return False
    
    def start_bruteforce_minimization(self) -> bool:
        """
        Main minimization routine. Returns true on success.

        Returns:
            bool: True if minimization is successful. False otherwise.
        """
        
        is_minimized = False
        minimized_set = set()
        while not is_minimized:
            frequent_values = self.get_most_frequent_values(minimized_set)
            did_shrink = False
            for freq_value in frequent_values:
                table, attrib, value = freq_value
                qualifed_table_name = self.get_fully_qualified_table_name(table)
                should_quote = str(type(value)) not in NUMBER_TYPES 
                
                self.connectionHelper.begin_transaction()
                self.connectionHelper.execute_sql([
                    self.connectionHelper.queries.delete_from_table_where_column_does_not_have_value_val(
                        qualifed_table_name, attrib, value, quoted=should_quote
                    )
                ])
                
                if self.query_result_no_full_nullfree_row(self.query):
                    did_shrink = True
                    self.connectionHelper.commit_transaction()
                    minimized_set.add((table, attrib))
                    self.logger.debug(f"Keeping only {freq_value}")
                    break
                else:
                    self.connectionHelper.rollback_transaction()
            
            is_minimized = not did_shrink
        
        for table in self.core_relations:
            done = False
            while not done:
                done = not self.try_remove_a_row(table)


        self.populate_dict_info()
        self.logger.debug("Finished bruteforce minimizer") 
        return True