import json
import logging
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Analysis, AgentLog
from google.adk.agents import LlmAgent

logger = logging.getLogger("uvicorn.error")

# --- Explicit Structured ADK Schemas ---
class PlannerDecision(BaseModel):
    run_research: bool = Field(description="Set to true if macro industry, competitor vectors, or trends are needed.")
    run_analysis: bool = Field(description="Set to true if capital burn, internal operations, or asset bottlenecks are highlighted.")
    run_strategy: bool = Field(default=True, description="Always true to synthesize the finalized executive document.")
    reasoning: str = Field(description="Detailed planning justification token.")

class ResearchOutput(BaseModel):
    market_size: str
    competitors: list[str]
    trends: list[str]

class AnalysisOutput(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    capital_efficiency: str

# --- Instantiating the Google ADK Specialist Nodes ---
planner_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="PlannerAgent",
    description="Orchestrator that reviews core descriptions and determines dynamic sub-agent execution paths.",
    instruction="Analyze the corporate profile text. Determine exactly which down-line consulting specialist nodes must run based on user priority indicators.",
    output_schema=PlannerDecision
)

research_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="ResearchAgent",
    description="Pulls competitive matrices, sector positioning vectors, and macroeconomic industry dynamics.",
    instruction="Analyze the corporate profile data. Extract market scale boundaries, major competitive constraints, and macro-level industry trend structures.",
    output_schema=ResearchOutput
)

analysis_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="AnalysisAgent",
    description="Performs corporate risk audits, runway estimates, and structural operations checks.",
    instruction="Evaluate internal organizational characteristics. Audit capital burn indicators, runtime constraints, and identify supply-chain or workflow failure nodes.",
    output_schema=AnalysisOutput
)

strategy_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="StrategyAgent",
    description="Combines active node feedback lines into publication-grade Markdown documentation.",
    instruction="""Synthesize the historical outputs from your peer sub-agents. 
Generate a publication-grade, deep Executive Strategic Blueprint report completely structured in pure Markdown. 
Incorporate explicit sections for Financial Operations, Strategic Market Interventions, and Risk Mitigations. Use clean bold elements or list indicators."""
)

def update_agent_log(db: Session, analysis_id: int, agent_name: str, status: str, output_data: str = None):
    """Utility synchronization function tracking agent steps within the relational layer for client polling."""
    log = db.query(AgentLog).filter_by(analysis_id=analysis_id, agent_name=agent_name).first()
    if not log:
        log = AgentLog(analysis_id=analysis_id, agent_name=agent_name)
        db.add(log)
    log.status = status
    if output_data:
        log.output_data = output_data
    db.commit()

async def run_orchestration_pipeline(analysis_id: int, db: Session):
    """Executes the specialized multi-agent routing routine using the refactored Google ADK pipeline."""
    try:
        # 1. Fetch original inputs from SQLite
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis or not analysis.project:
            logger.error(f"Analysis container context missing for index: {analysis_id}")
            return
            
        context_input = analysis.project.description
        logger.info(f"Initializing Google ADK Framework Pipeline for Project: {analysis.project.name}")

        # --- STEP 1: RUN THE ADK PLANNER ---
        update_agent_log(db, analysis_id, "Planner", "running", "PENDING_EXECUTION_STREAM")
        planner_response = await planner_agent.chat(f"Evaluate this corporate context and output standard routing decisions: {context_input}")
        
        # Parse the structured JSON response dictated by the output_schema
        decision_data = json.loads(planner_response.text)
        decision = PlannerDecision(**decision_data)
        
        update_agent_log(db, analysis_id, "Planner", "completed", f"Reasoning: {decision.reasoning}\n\nRouting Map: Research={decision.run_research}, Analysis={decision.run_analysis}")

        # Context accumulation objects
        research_context = "No research metadata provided."
        analysis_context = "No internal audit metadata provided."

        # --- STEP 2: DYNAMIC ADK RESEARCH TOOL BLOCK ---
        if decision.run_research:
            update_agent_log(db, analysis_id, "Research", "running", "PENDING_EXECUTION_STREAM")
            res_response = await research_agent.chat(f"Gather sector metrics for: {context_input}")
            research_context = res_response.text
            update_agent_log(db, analysis_id, "Research", "completed", research_context)
        else:
            update_agent_log(db, analysis_id, "Research", "bypassed", "NODE_BYPASS_DIRECTIVE")

        # --- STEP 3: DYNAMIC ADK RISK AUDIT BLOCK ---
        if decision.run_analysis:
            update_agent_log(db, analysis_id, "Analysis", "running", "PENDING_EXECUTION_STREAM")
            combined_input = f"Base Context: {context_input}\n\nUpstream Research Output: {research_context}"
            ana_response = await analysis_agent.chat(combined_input)
            analysis_context = ana_response.text
            update_agent_log(db, analysis_id, "Analysis", "completed", analysis_context)
        else:
            update_agent_log(db, analysis_id, "Analysis", "bypassed", "NODE_BYPASS_DIRECTIVE")

        # --- STEP 4: ADK STRATEGY COMPILATION ---
        update_agent_log(db, analysis_id, "Strategy", "running", "PENDING_EXECUTION_STREAM")
        final_aggregation_prompt = f"""
        Core Context: {context_input}
        Planner Blueprint Guidance: {decision.reasoning}
        Research Metrics Node Output: {research_context}
        Operational Risks Node Output: {analysis_context}
        """
        strat_response = await strategy_agent.chat(final_aggregation_prompt)
        final_report_markdown = strat_response.text
        
        update_agent_log(db, analysis_id, "Strategy", "completed", "Synthesis document complete.")

        # 2. Finalize Global State tracking properties
        analysis.status = "completed"
        analysis.final_report = final_report_markdown
        db.commit()
        logger.info("Google ADK pipeline resolution cycle completed successfully.")

    except Exception as e:
        logger.error(f"Critical execution fault intercepted inside the ADK loop: {str(e)}")
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.status = "failed"
            db.commit()
        # Fallback trace recovery across active elements
        for node in ["Planner", "Research", "Analysis", "Strategy"]:
            update_agent_log(db, analysis_id, node, "failed", f"CRITICAL_NODE_FAILURE: {str(e)}")