# BusinessLens AI

BusinessLens AI is a multi-agent business consulting platform that helps organizations analyze business challenges and generate actionable strategic recommendations using Google's Gemini API.

Users provide a business description and the challenges they are facing. A Planner Agent determines which specialist agents are required, orchestrates the workflow, and combines their outputs into a structured executive consulting report.

The platform also provides a modern dashboard with live agent execution tracking, business health visualization, and report export capabilities.

---

## Features

- Multi-agent workflow powered by Google Gemini
- Dynamic Planner Agent that selects downstream agents based on the problem
- Specialized Research, Analysis, and Strategy agents
- Live execution timeline showing agent status
- Business Health Score dashboard
- Executive consulting report generation
- Export reports as PDF, Markdown, and TXT
- SQLite-backed persistence for projects and reports
- Modern React + Tailwind dashboard
- FastAPI REST backend

---

## Architecture

```
                   User
                     │
                     ▼
          React + Tailwind Frontend
                     │
                     ▼
              FastAPI Backend
                     │
                     ▼
              Planner Agent
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
 Research Agent  Analysis Agent  Strategy Agent
      │              │              │
      └──────────────┼──────────────┘
                     ▼
         Executive Consulting Report
                     │
                     ▼
                 SQLite Database
```

---

## Agent Workflow

### Planner Agent
- Understands the business problem
- Decides which specialist agents should execute
- Creates the execution plan

### Research Agent
- Analyzes the industry
- Identifies competitors
- Finds market trends and opportunities

### Analysis Agent
- Evaluates operational, financial, and marketing issues
- Identifies potential risks
- Estimates business impact

### Strategy Agent
- Combines insights from previous agents
- Generates the final consulting report
- Creates recommendations and implementation roadmap

---

## Dashboard Features

### Live Agent Timeline

Track every stage of execution in real time.

```
✓ Planner
✓ Research
✓ Analysis
✓ Strategy
```

Each agent displays one of the following states:

- Pending
- Running
- Completed
- Bypassed
- Failed

---

### Business Health Dashboard

The generated report includes health scores across four business dimensions.

- Finance
- Marketing
- Operations
- Growth

These scores provide a quick overview of the organization's current state.

---

### Report Export

Export consulting reports in multiple formats.

- PDF
- Markdown (.md)
- Plain Text (.txt)

---

## Tech Stack

### Frontend

- React
- Vite
- Tailwind CSS

### Backend

- FastAPI
- SQLAlchemy
- Pydantic

### AI

- Google Gemini API
- Multi-Agent Orchestration

### Database

- SQLite

---

## Project Structure

```
businesslens-ai/

backend/
│
├── agents.py
├── orchestrator.py
├── gemini.py
├── database.py
├── models.py
├── schemas.py
└── main.py

frontend/
│
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
│
├── package.json
├── vite.config.js
└── tailwind.config.js

README.md
.env.example
.gitignore
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/anjipoo/businesslens-ai.git
cd businesslens-ai
```

### Backend

```bash
cd backend

python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file.

```env
GEMINI_API_KEY=YOUR_API_KEY
```

Run the backend.

```bash
uvicorn main:app --reload
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

The application will be available at:

```
http://localhost:5173
```

---

## Future Improvements

- Web search tools for richer market research
- Historical report comparison
- Interactive analytics dashboard
- Team workspaces
- Cloud database support
- Additional business specialist agents

---

## Why BusinessLens AI?

BusinessLens AI demonstrates how agent-based AI systems can solve real-world business problems by breaking complex analysis into specialized tasks. Instead of relying on a single prompt, the platform coordinates multiple agents that collaborate to produce structured, explainable, and actionable business recommendations.

This project was built as part of the **Kaggle 5-Day AI Agents Intensive Capstone** using Google's Gemini ecosystem.