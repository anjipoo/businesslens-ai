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
            # 1. Planner Node Lifecycle
            log_id = self._initialize_log(analysis_id, self.planner.name, project_context)
            try:
                planner_res_raw = self.planner.run(project_context)
                self._finalize_log(log_id, planner_res_raw, success=True)
            except Exception as e:
                self._finalize_log(log_id, f"Planner failed: {str(e)}", success=False)
                raise e

            planner_data = json.loads(planner_res_raw)
            selected_agents = planner_data.get("selected_agents", [])

            research_res = "{}"
            analysis_res = "{}"

            # 2. Research Node Lifecycle
            if "Research" in selected_agents:
                log_id = self._initialize_log(analysis_id, self.research_agent.name, project_context)
                try:
                    research_res = self.research_agent.run(project_context)
                    self._finalize_log(log_id, research_res, success=True)
                except Exception as e:
                    self._finalize_log(log_id, f"Research execution aborted: {str(e)}", success=False)
                    raise e

            # 3. Analysis Node Lifecycle
            if "Analysis" in selected_agents:
                analysis_input = f"Context: {project_context}\n\nMarket Research Data: {research_res}"
                log_id = self._initialize_log(analysis_id, self.analysis_agent.name, analysis_input)
                try:
                    analysis_res = self.analysis_agent.run(analysis_input)
                    self._finalize_log(log_id, analysis_res, success=True)
                except Exception as e:
                    self._finalize_log(log_id, f"Analysis execution aborted: {str(e)}", success=False)
                    raise e

            # 4. Strategy Node Lifecycle
            if "Strategy" in selected_agents or (not research_res and not analysis_res):
                strategy_input = (
                    f"Core Context: {project_context}\n\n"
                    f"Planner Reason: {planner_data.get('reasoning')}\n\n"
                    f"Research Findings: {research_res}\n\n"
                    f"Analytical Vectors: {analysis_res}"
                )
                log_id = self._initialize_log(analysis_id, self.strategy_agent.name, strategy_input)
                try:
                    final_report = self.strategy_agent.run(strategy_input)
                    self._finalize_log(log_id, final_report, success=True)
                    analysis.final_report = final_report
                except Exception as e:
                    self._finalize_log(log_id, f"Strategy execution aborted: {str(e)}", success=False)
                    raise e
            else:
                analysis.final_report = "# Orchestration Paused\n\nPlanner opted out of standard Strategy Generation."

            analysis.status = "completed"

        except Exception as e:
            analysis.status = "failed"
            if not analysis.final_report:
                analysis.final_report = f"Pipeline workflow crashed at active node block: {str(e)}"
        
        self.db.commit()

    def _initialize_log(self, analysis_id: int, agent_name: str, input_data: str) -> int:
        """Creates a live running tracking pointer entry inside SQLite."""
        log = models.AgentLog(
            analysis_id=analysis_id,
            agent_name=agent_name,
            input_data=input_data,
            output_data="PENDING_EXECUTION_STREAM",  # Handshake token mapped by frontend
            created_at=datetime.datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log.id

    def _finalize_log(self, log_id: int, output_data: str, success: bool):
        """Updates the tracking pointer entry inside SQLite upon node termination."""
        log = self.db.query(models.AgentLog).filter(models.AgentLog.id == log_id).first()
        if log:
            log.output_data = output_data if success else f"CRITICAL_NODE_FAILURE: {output_data}"
            self.db.commit()