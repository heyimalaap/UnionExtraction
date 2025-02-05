import copy

from ...src.pipeline.ExtractionPipeLine import ExtractionPipeLine
from ..core.elapsed_time import create_zero_time_profile
from ...src.util.constants import RUNNING, ERROR, START, SAMPLING, RESTORE_DB, DONE, DB_MINIMIZATION, EQUALITY, GROUP_BY
from ...src.core.db_restorer import DbRestorer
from ...src.core.cs2 import Cs2
from ...src.core.bruteforce_minimizer import BruteForceMinimizer
from ...src.obsolete.equi_join import EquiJoin
from ...src.core.having_groupby import GroupBy

class HavingPipeLine(ExtractionPipeLine):
    def __init__(self, connectionHelper, name="Having PipeLine"):
        super().__init__(connectionHelper, name)
    
    def _after_from_clause_extract(self, query, core_relations):
        time_profile = create_zero_time_profile()
        
        check, time_profile = self._mutation_pipeline(core_relations, query, time_profile)
    
    def _mutation_pipeline(self, core_relations, query, time_profile, restore_details=None):
        self.update_state(RESTORE_DB + START)
        self.db_restorer = DbRestorer(self.connectionHelper, core_relations)
        self.db_restorer.set_data_schema()
        self.db_restorer.set_all_sizes(self.all_sizes)
        # for tab in core_relations:
        #    self.db_restorer.last_restored_size[tab] = self.all_sizes[tab]
        self.update_state(RESTORE_DB + RUNNING)
        check = self.db_restorer.doJob(restore_details)
        self.update_state(RESTORE_DB + DONE)
        time_profile.update_for_db_restore(self.db_restorer.local_elapsed_time, self.db_restorer.app_calls)
        if not check or not self.db_restorer.done:
            self.info[RESTORE_DB] = None
            self.logger.info("DB restore failed!")
            return False, time_profile
        self.info[RESTORE_DB] = {'size': self.db_restorer.last_restored_size}

        """
        Correlated Sampling
        """
        self.update_state(SAMPLING + START)
        cs2 = Cs2(self.connectionHelper, self.all_sizes, core_relations, self.key_lists, perc_based_cutoff=True)
        self.update_state(SAMPLING + RUNNING)
        check = cs2.doJob(query)
        self.update_state(SAMPLING + DONE)
        time_profile.update_for_cs2(cs2.local_elapsed_time, cs2.app_calls)
        if not check or not cs2.done:
            self.info[SAMPLING] = None
            self.logger.info("Sampling failed!")
        if not self.connectionHelper.config.use_cs2:
            self.info[SAMPLING] = SAMPLING + "DISABLED"
            self.logger.info("Sampling is disabled!")
        else:
            self.info[SAMPLING] = {'sample': cs2.sample, 'size': cs2.sizes}

        """
        Brute-force minimizer: Having
        """
        self.update_state(DB_MINIMIZATION + START)
        bfm = BruteForceMinimizer(self.connectionHelper, core_relations, self.db_restorer.last_restored_size, cs2.passed)
        self.update_state(DB_MINIMIZATION + RUNNING)
        check = bfm.doJob(query)
        self.update_state(DB_MINIMIZATION + DONE)
        time_profile.update_for_view_minimization(bfm.local_elapsed_time, bfm.app_calls)
        if not check or not bfm.done:
            self.error = "Cannot do database minimization"
            self.logger.error(self.error)
            self.update_state(ERROR)
            self.info[DB_MINIMIZATION] = None
            return False, time_profile
        self.db_restorer.update_last_restored_size(bfm.all_sizes)
        self.info[DB_MINIMIZATION] = bfm.global_min_instance_dict
        self.global_min_instance_dict = copy.deepcopy(bfm.global_min_instance_dict)
        self.global_all_attribs = bfm.global_all_attribs
        
        """
        EquiJoin extraction (U1)
        """
        self.update_state(EQUALITY + START)
        self.update_state(EQUALITY + RUNNING)
        self.equi_join = EquiJoin(self.connectionHelper, self.key_lists, self.core_relations, self.global_min_instance_dict)
        check = self.equi_join.doJob(query)
        self.update_state(EQUALITY + DONE)
        time_profile.update_for_where_clause(self.equi_join.local_elapsed_time, self.equi_join.app_calls)
        
        """
        Group by extraction
        """
        self.update_state(GROUP_BY + START)
        self.group_by = GroupBy(self.connectionHelper, self.core_relations, self.global_all_attribs, self.all_sizes, self.equi_join.global_join_graph2)
        self.update_state(GROUP_BY + RUNNING)
        check = self.group_by.doJob(query)
        self.update_state(GROUP_BY + DONE)

        return False, time_profile