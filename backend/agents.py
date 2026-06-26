from pydantic import BaseModel, Field
from typing import List
from gemini import gemini_client

# --- Strict, Fully Articulated Pydantic Target Nodes ---
class PlannerDecision(BaseModel):
    selected_agents: List[str] = Field(
        description="Explicit agent nodes slated for execution block. Choices strictly bounded by: ['Research', 'Analysis', 'Strategy']."
    )
    reasoning: str = Field(description="Deep chain-of-thought structural diagnostic justifying the inclusion or exclusion of specific agent modules.")

class ResearchOutput(BaseModel):
    market_size: str = Field(description="Total Addressable Market (TAM) validation, segmented growth vectors, and sizing boundaries.")
    competitors: List[str] = Field(description="Granular competitor matrix detailing primary incumbents and secondary disruptive threats.")
    trends: List[str] = Field(description="Macroeconomic, technological, and consumer behavior structural velocity trends.")

class AnalysisOutput(BaseModel):
    strengths: List[str] = Field(description="Core company operational advantages, IP moats, or market leverage vectors.")
    weaknesses: List[str] = Field(description="Internal vulnerabilities, tech debt liabilities, structural capital deficiencies, or talent dependencies.")
    capital_efficiency: str = Field(description="Advanced financial health diagnostics focusing on operational burn velocity, runway leverage, and unit economics.")

# --- Optimized Multi-Stage Agent Prompts ---
class BaseAgent:
    def __init__(self, name: str, system_instruction: str, response_schema=None):
        self.name = name
        self.system_instruction = system_instruction
        self.response_schema = response_schema

    def run(self, context: str) -> str:
        return gemini_client.call_flash(
            prompt=context, 
            system_instruction=self.system_instruction, 
            response_schema=self.response_schema
        )

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Planner",
            system_instruction=(
                "You are the Lead Technical Director of BusinessLens AI. Your task is to ingest raw enterprise briefs "
                "and systematically delegate targets to downstream expert systems. Assess if the context demands external "
                "market research datasets ('Research'), internal structural financial diagnostics ('Analysis'), or both. "
                "Provide a rigorous corporate reason for your execution sequence."
            ),
            response_schema=PlannerDecision
        )

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research",
            system_instruction=(
                "You are an elite quantitative Market Research Agent. Your task is to process context and extract "
                "precise data frameworks. Evaluate target industry addressability, map out primary competitor moats, "
                "and identify high-velocity technological and macroeconomic movements. Output must strictly conform to the JSON schema."
            ),
            response_schema=ResearchOutput
        )

class AnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analysis",
            system_instruction=(
                "You are an expert Corporate CFO and Risk Auditor AI. Your task is to conduct an internal diagnostic audit. "
                "Isolate structural vulnerabilities, key-person risk profiles, capital allocation flaws, and operational friction points. "
                "Provide clear, actionable assessments of cash burn velocity and runway longevity based on the provided data."
            ),
            response_schema=AnalysisOutput
        )

class StrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Strategy",
            system_instruction=(
                "You are the Principal Management Consultant at a top-tier firm. Your task is to synthesize the foundational data "
                "provided by the Planner, Research, and Analysis nodes into an exceptional, publication-grade corporate report.\n\n"
                "CRITICAL FORMATTING INSTRUCTIONS:\n"
                "- Write exclusively in clean, professional Markdown using clear heading hierarchies (`#`, `##`, `###`).\n"
                "- Use bold highlights (`**bold**`) to draw attention to key data and metrics.\n"
                "- Organize your analysis into structural blocks using clear bulleted or numbered lists.\n"
                "- Use horizontal rules (`---`) to break up major thematic components.\n"
                "- Ensure the narrative maintains an objective, strategic, and authoritative consulting tone throughout."
            )
        )