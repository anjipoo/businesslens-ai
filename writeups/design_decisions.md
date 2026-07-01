# Design Decisions

## Why Google ADK?

Google ADK provides a structured framework for building multi-agent systems.

Instead of manually coordinating prompts, each agent has a clear role, schema, and lifecycle.

This keeps the application modular and easier to maintain.

---

## Why Multiple Agents?

Business consulting involves different kinds of reasoning.

Separating research, analysis, and strategy allows each agent to focus on a single responsibility while the Planner Agent determines which expertise is actually needed.

This reduces unnecessary computation and improves explainability.

---

## Why Dynamic Routing?

Many AI applications execute every component for every request.

BusinessLens AI instead lets the Planner Agent determine which specialist agents are required.

This makes execution more efficient and demonstrates true agent orchestration.

---

## Why Tool Calling?

The Research Agent uses an ADK tool instead of relying entirely on model knowledge.

This grounds market-related information and reduces hallucinations.

---

## Why FastAPI?

FastAPI provides asynchronous request handling, automatic validation, and simple REST APIs that integrate well with AI workflows.

---

## Why React?

React provides a responsive interface capable of updating agent states in real time while keeping the UI modular.

---

## Why SQLite?

SQLite requires no additional infrastructure and is sufficient for storing projects, reports, and execution logs during development and demonstrations.

---

## Why Polling Instead of WebSockets?

Polling is simpler to implement and sufficient for a sequential workflow.

Future versions can replace polling with Server-Sent Events or WebSockets.