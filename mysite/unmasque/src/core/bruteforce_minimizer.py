from .abstract.MinimizerBase import Minimizer
from ..util.constants import NUMBER_TYPES
from typing import Any

class BruteForceMinimizer(Minimizer):
    def __init__(self, connectionHelper, core_relations, all_sizes, sampling_status):
        super().__init__(connectionHelper, core_relations, all_sizes, "Brute-force Minimizer")
        
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
        pass

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
                
                if self.sanity_check(self.query):
                    did_shrink = True
                    self.connectionHelper.commit_transaction()
                    minimized_set.add((table, attrib))
                    self.logger.debug(f"Keeping only {freq_value}")
                    break
                else:
                    self.connectionHelper.rollback_transaction()
            
            is_minimized = not did_shrink
        
        self.populate_dict_info()
        self.logger.debug("Finished bruteforce minimizer") 
        return True