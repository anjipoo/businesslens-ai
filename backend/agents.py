from pydantic import BaseModel, Field
from typing import List
from gemini import gemini_client

# --- Upgraded Dynamic Planner Pydantic Rule Engine ---
class PlannerDecision(BaseModel):
    run_research: bool = Field(
        description="Set to true if external macroeconomic, trends, or competitive industry validation metrics are required."
    )
    run_analysis: bool = Field(
        description="Set to true if internal corporate diagnostics, capital burn vulnerabilities, runway longevity calculations, or talent dependency evaluations are required."
    )
    run_strategy: bool = Field(
        description="Set to true if a synthesized final high-level corporate management consulting report should be generated based on available inputs."
    )
    reasoning: str = Field(
        description="Rigorous analytical explanation detailing precisely why specific agents are assigned to run or skip based on the profile context."
    )

class ResearchOutput(BaseModel):
    market_size: str = Field(description="Target market size estimate and addressable metrics.")
    competitors: List[str] = Field(description="Key industry players or market alternatives identified.")
    trends: List[str] = Field(description="Top technological or economic trends driving the market segment.")

class AnalysisOutput(BaseModel):
    strengths: List[str] = Field(description="Core company advantages or value vectors.")
    weaknesses: List[str] = Field(description="Structural vulnerabilities, data overhead risks, or resource gaps.")
    capital_efficiency: str = Field(description="Assessment of unit economics, cost structures, or estimated runway.")

# --- Base Agent Class Core ---
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

# --- Updated Planner Architecture Persona ---
class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Planner",
            system_instruction=(
                "You are the supreme Orchestration Director of BusinessLens AI. Analyze the input text profile. "
                "Determine exactly which expert modules (Research, Analysis, Strategy) are essential to solve the request. "
                "Do NOT always execute every node. If the context contains sufficient internal metrics but lacks market landscape data, "
                "run Research and skip Analysis. If the request only asks for a basic audit structure or focuses on an internal operational bottleneck, "
                "skip external Research. Output your configuration strictly according to the boolean schema flags."
            ),
            response_schema=PlannerDecision
        )

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research",
            system_instruction="You are a primary market research agent. Extract demographic scale metrics, competitor landscapes, and industry trends based on the input text profile.",
            response_schema=ResearchOutput
        )

class AnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analysis",
            system_instruction="You are a financial and corporate risk analyst. Evaluate core unit economics vectors, project liabilities, operational bottlenecks, and internal corporate structure gaps.",
            response_schema=AnalysisOutput
        )

class StrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Strategy",
            system_instruction="You are the lead business strategist. Review all preceding agent inputs, structured logs, and data points to generate a comprehensive, Markdown-formatted professional consulting report outlining structural recommendations and corporate direction."
        )