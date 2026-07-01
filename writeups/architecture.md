# BusinessLens AI Architecture

## Overview

BusinessLens AI is a multi-agent business consulting platform built using Google ADK, Gemini, FastAPI, React, and SQLite.

Instead of relying on a single LLM prompt, the application divides the problem into specialized agents coordinated by a Planner Agent.

---

## System Architecture

```
                   User
                     │
                     ▼
          React + Tailwind Frontend
                     │
              REST API Requests
                     │
                     ▼
             FastAPI Backend
                     │
             Orchestrator Service
                     │
                     ▼
              Planner Agent
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
 Research Agent          Analysis Agent
        │                         │
        └────────────┬────────────┘
                     ▼
              Strategy Agent
                     │
                     ▼
          Executive Business Report
                     │
                     ▼
              SQLite Database
```

---

## Components

### Frontend

- React
- Vite
- Tailwind CSS

Responsibilities

- Collect business information
- Display live execution timeline
- Display Business Health Dashboard
- Export reports

---

### Backend

Built using FastAPI.

Responsibilities

- API routing
- Background orchestration
- Agent execution
- Database operations

---

### AI Layer

The AI layer consists of four specialized agents.

Planner Agent

- Understands the request
- Decides which agents should execute

Research Agent

- Collects market information
- Uses an ADK tool for structured lookups

Analysis Agent

- Evaluates operational and financial issues

Strategy Agent

- Combines all outputs
- Generates the executive report

---

### Database

SQLite stores

- Projects
- Analyses
- Agent logs

This allows the frontend to monitor execution progress while the backend processes requests asynchronously.

---

## Execution Flow

1. User submits business details.
2. Backend creates a project.
3. Planner Agent evaluates the request.
4. Planner decides which agents execute.
5. Research and Analysis run if required.
6. Strategy Agent generates the final report.
7. Report is stored in SQLite.
8. Frontend displays results.