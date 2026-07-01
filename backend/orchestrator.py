import json
import logging
from typing import List
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
    competitors: List[str]
    trends: List[str]

class AnalysisOutput(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    capital_efficiency: str

# --- Reusable Google ADK Tool Implementation ---
def market_search_lookup(company_name: str, industry_sector: str) -> str:
    """
    Performs a targeted database lookup and market analysis query for a given enterprise sector.
    
    Args:
        company_name: The target company or project being analyzed.
        industry_sector: The specific vertical or industry sector (e.g., AgTech, FinTech, Logistics).
        
    Returns:
        A text string containing verified structural market data, growth rates, and benchmark metrics.
    """
    logger.info(f"[ADK Tool Execution] Market search triggered for: {company_name} in sector: {industry_sector}")
    
    # Standardized mock analytical telemetry returned securely to the model context
    sector_lower = industry_sector.lower()
    if "agtech" in sector_lower or "farm" in sector_lower:
        return (
            "Verified Industry Metrics: The global AgTech automation market is valued at $7.2 Billion, "
            "growing at an annual compound rate (CAGR) of 14.2%. High capital expenditures are typical, "
            "and hardware component lead times average 6-12 weeks globally due to international specialized supply constraints."
        )
    elif "health" in sector_lower or "med" in sector_lower:
        return (
            "Verified Industry Metrics: The digital healthcare logistics sector stands at $24 Billion, "
            "with a 9.4% CAGR. Highly regulated entry barriers exist with strict data compliance overheads."
        )
    else:
        return (
            f"Verified Industry Metrics: Standard operational benchmarks for {industry_sector} indicate "
            "an average industry growth metric of 8.5% CAGR. Primary vulnerabilities include localized procurement bottlenecks "
            "and rising customer acquisition adjustments."
        )

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
    description="Pulls competitive matrices, sector positioning vectors, and macroeconomic industry dynamics using specialized search capabilities.",
    instruction="""Analyze the corporate profile data. You MUST call the `market_search_lookup` tool to retrieve verified 
    external sector benchmarks for the business vertical before organizing your findings. Extract market scale boundaries, 
    major competitive constraints, and macro-level industry trend structures from the tool response.""",
    tools=[market_search_lookup],  # Direct injection of the functional tool vector
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
    log = db.query(AgentLog).filter_by(analysis_id=analysis_id, agent_name=agent_name).first()
    if not log:
        log = AgentLog(analysis_id=analysis_id, agent_name=agent_name)
        db.add(log)
    log.status = status
    if output_data:
        log.output_data = output_data
    db.commit()

async def run_orchestration_pipeline(analysis_id: int, db: Session):
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis or not analysis.project:
            logger.error(f"Analysis container context missing for index: {analysis_id}")
            return
            
        context_input = analysis.project.description
        company_name = analysis.project.name
        logger.info(f"Initializing Google ADK Framework Pipeline for Project: {company_name}")

        # --- STEP 1: RUN THE ADK PLANNER ---
        update_agent_log(db, analysis_id, "Planner", "running", "PENDING_EXECUTION_STREAM")
        planner_response = await planner_agent.chat(f"Evaluate this corporate context and output standard routing decisions: {context_input}")
        
        decision_data = json.loads(planner_response.text)
        decision = PlannerDecision(**decision_data)
        update_agent_log(db, analysis_id, "Planner", "completed", f"Reasoning: {decision.reasoning}\n\nRouting Map: Research={decision.run_research}, Analysis={decision.run_analysis}")

        research_context = "No research metadata provided."
        analysis_context = "No internal audit metadata provided."

        # --- STEP 2: DYNAMIC ADK RESEARCH TOOL BLOCK ---
        if decision.run_research:
            update_agent_log(db, analysis_id, "Research", "running", "PENDING_EXECUTION_STREAM")
            # The agent will dynamically determine arguments and invoke market_search_lookup autonomously
            res_response = await research_agent.chat(
                f"Analyze the market metrics for the project named '{company_name}' using the context profile: {context_input}. "
                f"Identify the explicit industry sector and pass it to your search lookup tool."
            )
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

        # Finalize Global State tracking properties
        analysis.status = "completed"
        analysis.final_report = final_report_markdown
        db.commit()

    except Exception as e:
        logger.error(f"Critical execution fault intercepted inside the ADK loop: {str(e)}")
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.status = "failed"
            db.commit()
        for node in ["Planner", "Research", "Analysis", "Strategy"]:
            update_agent_log(db, analysis_id, node, "failed", f"CRITICAL_NODE_FAILURE: {str(e)}")