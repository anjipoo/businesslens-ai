from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class AgentLogResponse(BaseModel):
    id: int
    agent_name: str
    input_data: Optional[str]
    output_data: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    id: int
    project_id: int
    status: str
    final_report: Optional[str]
    created_at: datetime
    logs: List[AgentLogResponse] = []
    class Config:
        from_attributes = True