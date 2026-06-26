from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database
from orchestrator import ConsultingOrchestrator

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="BusinessLens AI Architecture")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/projects", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    db_project = models.Project(name=project.name, description=project.description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.post("/projects/{project_id}/analyze", response_model=schemas.AnalysisResponse)
def run_analysis(project_id: int, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project context record target missing")
        
    analysis = models.Analysis(project_id=project_id, status="pending")
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    orchestrator = ConsultingOrchestrator(db)
    context_str = f"Project Name: {project.name}. Briefing Details: {project.description}"
    background_tasks.add_task(orchestrator.run_workflow, analysis.id, context_str)

    return analysis

@app.get("/analyses/{analysis_id}", response_model=schemas.AnalysisResponse)
def get_analysis(analysis_id: int, db: Session = Depends(database.get_db)):
    analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Target analysis session could not be tracked")
    return analysis