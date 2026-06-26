import json
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
            # 1. Planner Agent Execution Step
            planner_res_raw = self.planner.run(project_context)
            self._log_step(analysis_id, self.planner.name, project_context, planner_res_raw)
            planner_data = json.loads(planner_res_raw)
            selected_agents = planner_data.get("selected_agents", [])

            # Dynamic execution contexts setup
            research_res = "{}"
            analysis_res = "{}"

            # 2. Dynamic Execution Loop Based on Planner Rules
            if "Research" in selected_agents:
                research_res = self.research_agent.run(project_context)
                self._log_step(analysis_id, self.research_agent.name, project_context, research_res)

            if "Analysis" in selected_agents:
                analysis_input = f"Context: {project_context}\n\nMarket Research Data: {research_res}"
                analysis_res = self.analysis_agent.run(analysis_input)
                self._log_step(analysis_id, self.analysis_agent.name, analysis_input, analysis_res)

            # 3. Final Strategy Synthesis Phase
            if "Strategy" in selected_agents or (not research_res and not analysis_res):
                strategy_input = (
                    f"Core Context: {project_context}\n\n"
                    f"Planner Reason: {planner_data.get('reasoning')}\n\n"
                    f"Research Findings: {research_res}\n\n"
                    f"Analytical Vectors: {analysis_res}"
                )
                final_report = self.strategy_agent.run(strategy_input)
                self._log_step(analysis_id, self.strategy_agent.name, strategy_input, final_report)
                analysis.final_report = final_report
            else:
                analysis.final_report = (
                    f"# Orchestration Complete\n\n"
                    f"The internal Planner bypassed final report rendering.\n\n"
                    f"### Intermediate Metrics Generated\n"
                    f"- **Research Module Output**: {research_res}\n"
                    f"- **Analysis Module Output**: {analysis_res}"
                )

            analysis.status = "completed"

        except Exception as e:
            analysis.status = "failed"
            analysis.final_report = f"Execution workflow terminated unexpectedly: {str(e)}"
        
        self.db.commit()

    def _log_step(self, analysis_id: int, agent_name: str, inp: str, outp: str):
        log = models.AgentLog(analysis_id=analysis_id, agent_name=agent_name, input_data=inp, output_data=outp)
        self.db.add(log)
        self.db.commit()