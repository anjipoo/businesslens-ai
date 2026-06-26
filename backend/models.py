import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    status = Column(String, default="pending")  # pending, processing, completed, failed
    final_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="analyses")
    logs = relationship("AgentLog", back_populates="analysis", cascade="all, delete-orphan")

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    agent_name = Column(String, nullable=False)
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("Analysis", back_populates="logs")