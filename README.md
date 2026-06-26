# BusinessLens AI — Multi-Agent Consulting Platform

A high-performance, single-file multi-agent strategic business consulting architecture built specifically for the **Kaggle AI Agents Capstone**. This implementation features a clean, highly scannable UI layer powered by FastAPI, SQLite, React, and Vite, orchestrated using the official **Google GenAI SDK (`google-genai`)** with Gemini 2.5 Flash.

---

## 🎛️ Multi-Agent Architecture Trace

The workflow operates sequentially through four specialized agent nodes:
1. **Planner**: Ingests context prompts and uses structured JSON formatting to decide which down-line systems must run.
2. **Research**: Gathers external trends, competitors, and demographic scaling criteria into a strict JSON data structure.
3. **Analysis**: Evaluates internal company financial stability, unit economics metrics, and operational bottlenecks.
4. **Strategy**: Combines previous telemetry logs to generate an authoritative corporate consulting blueprint in clean Markdown.

---

## 🚀 Execution & Setup Protocol

### 1. Backend Ingestion Layer
Navigate to the server directory, establish a isolated virtual execution environment, and install your core system libraries:
```bash
cd backend
python -m venv venv
source venv/bin/activate # Windows Terminal: .\venv\Scripts\activate

# Install essential dependencies
pip install fastapi uvicorn sqlalchemy pydantic google-genai
```
Export your Google API validation key to the shell execution stack:
```bash
export GEMINI_API_KEY="AIzaSyYourKeyGoesHere"
# Windows PowerShell: $env:GEMINI_API_KEY="AIzaSyYourKeyGoesHere"
```
Fire up the FastAPI production development thread:
```bash
uvicorn main:app --reload --port 8000
```


### 2. Frontend User Workspace
In a fresh concurrent terminal window, activate the asset server:
```bash
cd frontend
npm install
npm run dev -- --force
```

Open `http://localhost:5173` to launch the upgraded user workbench.

## 🌐 Production Deployment Guide
Backend: Render / DigitalOcean App Platform
1. Set up a Git sub-tree repository mapping exclusively to the /backend directory.
2. Define the execution base image runtime stack as Python 3.11+.
3. Configure the start command to launch your application server:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```
4. **CRITICAL STEP**: Add your production GEMINI_API_KEY directly inside the deployment dashboard's Environment Variables panel to keep it safe and hidden.