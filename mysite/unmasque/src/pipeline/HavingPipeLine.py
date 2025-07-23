import copy

from ...src.pipeline.ExtractionPipeLine import ExtractionPipeLine
from ..core.elapsed_time import create_zero_time_profile
from ...src.util.constants import RUNNING, ERROR, START, SAMPLING, RESTORE_DB, DONE, DB_MINIMIZATION, EQUALITY, GROUP_BY, FILTER, INEQUALITY, PROJECTION, AGGREGATE, LIMIT, ORDER_BY
from ...src.core.db_restorer import DbRestorer
from ...src.core.cs2 import Cs2
from ...src.core.bruteforce_minimizer import BruteForceMinimizer
from ...src.obsolete.equi_join import EquiJoin
from ...src.core.having_groupby import GroupBy
from ...src.core.having_predicate_extraction import PredicateExtractor
from ...src.core.equi_join import U2EquiJoin
from ...src.core.aoa import InequalityPredicate
from ...src.core.filter import Filter
from ...src.core.dataclass.genPipeline_context import GenPipelineContext
from ...src.core.dataclass.pgao_context import PGAOcontext
from ...src.core.projection import Projection
from ...src.core.aggregation import Aggregation
from ...src.core.orderby_clause import OrderBy 
from ...src.core.limit import Limit 
from ...src.core.having_predicate_separator import PredicateSeparator

class HavingPipeLine(ExtractionPipeLine):
    def __init__(self, connectionHelper, name="Having PipeLine"):
        super().__init__(connectionHelper, name)
        self.pgao_ctx = PGAOcontext()
    
    def _after_from_clause_extract(self, query, core_relations):
        time_profile = create_zero_time_profile()
        
        check, time_profile = self._mutation_pipeline(core_relations, query, time_profile)
        if not check:
            self.error += "Some problem in Regular mutation pipeline. Aborting extraction!"
            self.logger.error(self.error)
            self.update_state(ERROR)
            self.time_profile.update(time_profile)
            return None
        
        self.time_profile.update(time_profile)
        self.__gen_pipeline_preprocess(core_relations)

        '''
        Projection Extraction
        '''
        self.update_state(PROJECTION + START)
        self.pj = Projection(self.connectionHelper, self.genPipelineCtx)

        self.update_state(PROJECTION + RUNNING)
        check = self.pj.doJob(query)
        self.update_state(PROJECTION + DONE)
        self.time_profile.update_for_projection(self.pj.local_elapsed_time, self.pj.app_calls)
        self.info[PROJECTION] = {'names': self.pj.projection_names, 'attribs': self.pj.projected_attribs}
        if not check:
            self.update_state(ERROR)
            self.info[PROJECTION] = None
            self.logger.error("Cannot find projected attributes. ")
            return None
        if not self.pj.done:
            self.update_state(ERROR)
            self.info[PROJECTION] = None
            self.error = check if check else self.error_string
            self.logger.error(self.error)
            return None
        self.pgao_ctx.projection = self.pj

        self.pgao_ctx.group_by = self.group_by
        
        self.update_state(AGGREGATE + START)
        agg = Aggregation(self.connectionHelper, self.genPipelineCtx, self.pgao_ctx)
        self.update_state(AGGREGATE + RUNNING)
        check = agg.doJob(query)
        self.update_state(AGGREGATE + DONE)
        self.time_profile.update_for_aggregate(agg.local_elapsed_time, agg.app_calls)
        self.info[AGGREGATE] = agg.global_aggregated_attributes
        if not check:
            self.update_state(ERROR)
            self.info[AGGREGATE] = None
            self.logger.info("Cannot find aggregations.")
        if not agg.done:
            self.update_state(ERROR)
            self.info[AGGREGATE] = None
            self.error = check if check else self.error_string
            self.logger.error(self.error)
            return None
        self.pgao_ctx.aggregate = agg
        
        ps = PredicateSeparator(self.connectionHelper, self.genPipelineCtx, self.pgao_ctx)
        ps.doJob(query)
        self.time_profile.update_for_predicate_separation(ps.local_elapsed_time, ps.app_calls)

        self.update_state(ORDER_BY + START)
        ob = OrderBy(self.connectionHelper, self.genPipelineCtx, self.pgao_ctx)
        self.update_state(ORDER_BY + RUNNING)
        ob.doJob(query)
        self.update_state(ORDER_BY + DONE)
        self.time_profile.update_for_order_by(ob.local_elapsed_time, ob.app_calls)
        self.info[ORDER_BY] = ob.orderBy_string
        if not ob.has_orderBy:
            self.update_state(ERROR)
            self.info[ORDER_BY] = None
            self.logger.info("Cannot find aggregations.")
        if not ob.done:
            self.update_state(ERROR)
            self.info[ORDER_BY] = None
            self.error = check if check else self.error_string
            self.logger.error(self.error)
            return None
        self.pgao_ctx.order_by = ob

        self.update_state(LIMIT + START)
        lm = Limit(self.connectionHelper, self.genPipelineCtx, self.pgao_ctx)
        self.update_state(LIMIT + RUNNING)
        lm.doJob(query)
        self.update_state(LIMIT + DONE)
        self.time_profile.update_for_limit(lm.local_elapsed_time, lm.app_calls)
        self.info[LIMIT] = lm.limit
        if lm.limit is None:
            self.update_state(ERROR)
            self.info[LIMIT] = None
            self.logger.info("Cannot find limit.")
        if not lm.done:
            self.update_state(ERROR)
            self.info[LIMIT] = None
            self.error = check if check else self.error_string
            self.logger.error(self.error)
            return None
        
        having_attribs = [(p[0], p[1]) for p in self.genPipelineCtx.having_predicates]
        aoa_arth_eq = self.aoa.arithmetic_eq_predicates
        aoa_arth_in = self.aoa.arithmetic_ineq_predicates
        
        aoa_arth_eq = [p for p in aoa_arth_eq if (p[0], p[1]) not in having_attribs]
        aoa_arth_in = [p for p in aoa_arth_in if (p[0], p[1]) not in having_attribs]
        
        self.aoa.arithmetic_eq_predicates = aoa_arth_eq
        self.aoa.arithmetic_ineq_predicates = aoa_arth_in
        
        self.q_generator.get_datatype = self.filter_extractor.get_datatype  # method
        self.q_generator.from_clause = core_relations
        self.q_generator.algebraic_predicates = self.aoa
        self.q_generator.arithmetic_disjunctions = self.genPipelineCtx
        
        self.q_generator.pgaoCtx = self.pgao_ctx
        self.q_generator.limit = lm
        self.q_generator.having_predicates = self.genPipelineCtx.having_predicates
        eq = self.q_generator.formulate_query_string()
        self.logger.debug("extracted query:\n", eq)

        return eq
    
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
        time_profile.update_for_bruteforce_minimization(bfm.local_elapsed_time, bfm.app_calls)
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
        time_profile.update_for_where_clause(self.equi_join.local_elapsed_time, self.equi_join.app_calls)
        self.update_state(EQUALITY + DONE)
        
        """
        Group by extraction
        """
        self.update_state(GROUP_BY + START)
        self.group_by = GroupBy(self.connectionHelper, self.core_relations, self.global_all_attribs, self.all_sizes, self.equi_join.global_join_graph2)
        self.update_state(GROUP_BY + RUNNING)
        check = self.group_by.doJob(query)
        time_profile.update_for_group_by(self.group_by.local_elapsed_time, self.group_by.app_calls)
        self.update_state(GROUP_BY + DONE)
        
        """
        Predicate Extraction
        """
        self.pred_extraction = PredicateExtractor(self.connectionHelper, self.core_relations, self.global_all_attribs, self.group_by.attrib_types_dict, self.group_by.groupby_attribs, self.all_sizes, self.global_pk_dict, self.equi_join.global_join_graph2)
        check = self.pred_extraction.doJob(query)
        time_profile.update_for_predicate_extraction(self.pred_extraction.local_elapsed_time, self.pred_extraction.app_calls)
        
        """
        Now that we have a database instance with just one row, to maintain compat. with the
        existing generation pipeline code, we run both the Filter extractor and AOA extractor.
        NOTE: THIS IS A HACK; EVENTUALLY, WE **NEED** A BETTER WAY OF DOING THIS
        
        Filter Extraction
        """
        self.populate_dict_info()

        self.update_state(FILTER + START)
        self.filter_extractor = Filter(self.connectionHelper, core_relations, self.global_min_instance_dict)
        self.update_state(FILTER + RUNNING)
        check = self.filter_extractor.doJob(query)
        self.update_state(FILTER + DONE)
        time_profile.update_for_where_clause(self.filter_extractor.local_elapsed_time,
                                             self.filter_extractor.app_calls)
        if not self.filter_extractor.done:
            self.update_state(ERROR)
            self.info[FILTER] = None
            self.error = check if check else self.error_string
            self.logger.error(self.error)
            return False, time_profile
        if not check:
            self.info[FILTER] = None
            self.logger.info("No filter found")
        self.info[FILTER] = self.filter_extractor.filter_predicates

        '''
        Equality Relations (Equi-join + Constant Equality filters) Extraction
        '''
        self.equi_join2 = U2EquiJoin(self.connectionHelper, core_relations, self.filter_extractor.filter_predicates,
                                    self.filter_extractor, self.global_min_instance_dict)
        check = self.equi_join2.doJob(query)
        time_profile.update_for_where_clause(self.equi_join2.local_elapsed_time, self.equi_join2.app_calls)
        if not self.equi_join2.done:
            self.update_state(ERROR)
            self.info[EQUALITY] = None
            self.error = check if check else self.error_string
            self.logger.error(self.error)
            return False, time_profile
        if not check:
            self.info[EQUALITY] = None
            self.logger.info("No Equality predicate found")
        combined_eq_predicates = self.equi_join2.algebraic_eq_predicates + self.equi_join2.arithmetic_eq_predicates
        self.info[EQUALITY] = combined_eq_predicates

        '''
        AOA Extraction
        '''
        self.update_state(INEQUALITY + START)
        self.aoa = InequalityPredicate(self.connectionHelper, core_relations, self.equi_join2.pending_predicates,
                                       self.equi_join2.arithmetic_eq_predicates,
                                       self.equi_join2.algebraic_eq_predicates, self.filter_extractor,
                                       self.global_min_instance_dict)
        self.update_state(INEQUALITY + RUNNING)
        self.connectionHelper.begin_transaction()
        check = self.aoa.doJob(query)
        self.connectionHelper.rollback_transaction()
        self.update_state(INEQUALITY + DONE)
        time_profile.update_for_where_clause(self.aoa.local_elapsed_time, self.aoa.app_calls)
        self.info[INEQUALITY] = self.aoa.aoa_predicates + self.aoa.aoa_less_thans + self.aoa.arithmetic_ineq_predicates
        if not check:
            self.info[INEQUALITY] = None
            self.logger.info("Cannot find inequality Predicates.")
        if not self.aoa.done:
            self.info[INEQUALITY] = None
            self.error = check if check else self.error_string
            self.logger.error(self.error)
            self.update_state(ERROR)
            return False, time_profile

        
        return True, time_profile

    def __gen_pipeline_preprocess(self, core_relations):
        self.logger.debug("aoa post-process.")
        self.genPipelineCtx = GenPipelineContext(core_relations, self.aoa,
                                                 self.filter_extractor, self.global_min_instance_dict,
                                                 [])
        self.logger.debug(self.genPipelineCtx.arithmetic_filters)
        self.logger.debug(self.genPipelineCtx.global_join_graph)
        self.logger.debug(self.genPipelineCtx.filter_in_predicates)
        self.logger.debug(self.genPipelineCtx.filter_attrib_dict)
        self.genPipelineCtx.doJob()

        self.genPipelineCtx.is_having_pipeline = True
        self.genPipelineCtx.filter_predicates = self.pred_extraction.filter_predicates
        self.genPipelineCtx.having_predicates = self.pred_extraction.having_predicates
        self.genPipelineCtx.joined_graph2 = self.equi_join.global_join_graph2

        self.logger.debug("after doJob...")
        self.logger.debug(self.genPipelineCtx.arithmetic_filters)
        self.logger.debug(self.genPipelineCtx.global_join_graph)
        self.logger.debug(self.genPipelineCtx.filter_in_predicates)
        self.logger.debug(self.genPipelineCtx.filter_attrib_dict)

    def populate_dict_info(self):
        # POPULATE MIN INSTANCE DICT
        import pandas as pd
        for tabname in self.core_relations:
            self.global_min_instance_dict[tabname] = []
            sql_query = pd.read_sql_query(self.connectionHelper.queries.get_star(tabname), self.connectionHelper.conn)
            df = pd.DataFrame(sql_query)
            self.global_min_instance_dict[tabname].append(tuple(df.columns))
            for index, row in df.iterrows():
                self.global_min_instance_dict[tabname].append(tuple(row))