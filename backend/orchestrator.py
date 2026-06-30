import json
import datetime
from sqlalchemy.orm import Session
from agents import PlannerAgent, ResearchAgent, AnalysisAgent, StrategyAgent
import models

class ConsultingOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.planner = PlannerAgent()
        self.research_agent = ResearchAgent()
        self.analysis_agent = AnalysisAgent()
        self.strategy_agent = StrategyAgent()

    def run_workflow(self, analysis_id: int, project_context: str):
        analysis = self.db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
        if not analysis:
            return

        analysis.status = "processing"
        self.db.commit()

        try:
            # 1. Execute Planner Agent Module
            log_id = self._initialize_log(analysis_id, self.planner.name, project_context)
            try:
                planner_res_raw = self.planner.run(project_context)
                self._finalize_log(log_id, planner_res_raw, success=True)
            except Exception as e:
                self._finalize_log(log_id, f"Planner optimization block faulted: {str(e)}", success=False)
                raise e

            # Parse structural JSON routing directives
            planner_data = json.loads(planner_res_raw)
            run_research = planner_data.get("run_research", False)
            run_analysis = planner_data.get("run_analysis", False)
            run_strategy = planner_data.get("run_strategy", False)

            research_res = "{}"
            analysis_res = "{}"

            # 2. Conditional Research Node Execution Block
            if run_research:
                log_id = self._initialize_log(analysis_id, self.research_agent.name, project_context)
                try:
                    research_res = self.research_agent.run(project_context)
                    self._finalize_log(log_id, research_res, success=True)
                except Exception as e:
                    self._finalize_log(log_id, f"Research block crashed: {str(e)}", success=False)
                    raise e
            else:
                self._log_skipped_node(analysis_id, self.research_agent.name)

            # 3. Conditional Analysis Node Execution Block
            if run_analysis:
                analysis_input = f"Context: {project_context}\n\nPrior Research Telemetry: {research_res}"
                log_id = self._initialize_log(analysis_id, self.analysis_agent.name, analysis_input)
                try:
                    analysis_res = self.analysis_agent.run(analysis_input)
                    self._finalize_log(log_id, analysis_res, success=True)
                except Exception as e:
                    self._finalize_log(log_id, f"Analysis block crashed: {str(e)}", success=False)
                    raise e
            else:
                self._log_skipped_node(analysis_id, self.analysis_agent.name)

            # 4. Conditional Strategy Node Execution Block
            if run_strategy:
                strategy_input = (
                    f"Core Context: {project_context}\n\n"
                    f"Planner Matrix Reasoning: {planner_data.get('reasoning')}\n\n"
                    f"Research Stream Output: {research_res}\n\n"
                    f"Analysis Stream Output: {analysis_res}"
                )
                log_id = self._initialize_log(analysis_id, self.strategy_agent.name, strategy_input)
                try:
                    final_report = self.strategy_agent.run(strategy_input)
                    self._finalize_log(log_id, final_report, success=True)
                    analysis.final_report = final_report
                except Exception as e:
                    self._finalize_log(log_id, f"Strategy generation failed: {str(e)}", success=False)
                    raise e
            else:
                self._log_skipped_node(analysis_id, self.strategy_agent.name)
                analysis.final_report = (
                    f"# Orchestration Complete\n\n"
                    f"The routing Planner dynamically bypassed final report synthesis.\n\n"
                    f"### Operational Diagnostics Logged:\n"
                    f"- **Research Module Ran**: `{run_research}`\n"
                    f"- **Analysis Module Ran**: `{run_analysis}`\n"
                    f"- **Reasoning**: {planner_data.get('reasoning')}"
                )

            analysis.status = "completed"

        except Exception as e:
            analysis.status = "failed"
            if not analysis.final_report:
                analysis.final_report = f"Execution workflow aborted: {str(e)}"
        
        self.db.commit()

    def _initialize_log(self, analysis_id: int, agent_name: str, input_data: str) -> int:
        log = models.AgentLog(
            analysis_id=analysis_id,
            agent_name=agent_name,
            input_data=input_data,
            output_data="PENDING_EXECUTION_STREAM",
            created_at=datetime.datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log.id

    def _finalize_log(self, log_id: int, output_data: str, success: bool):
        log = self.db.query(models.AgentLog).filter(models.AgentLog.id == log_id).first()
        if log:
            log.output_data = output_data if success else f"CRITICAL_NODE_FAILURE: {output_data}"
            self.db.commit()

    def _log_skipped_node(self, analysis_id: int, agent_name: str):
        """Logs an explicit pipeline bypass entry."""
        log = models.AgentLog(
            analysis_id=analysis_id,
            agent_name=agent_name,
            input_data="SYSTEM_ROUTING_BYPASS",
            output_data="NODE_BYPASS_DIRECTIVE",
            created_at=datetime.datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()