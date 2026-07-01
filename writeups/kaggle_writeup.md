# BusinessLens AI
### How a Planner Agent Learned to Stop Running Every Analysis, Every Time

**Track: Agents for Business**

---

## 1. Introduction

Every founder has, at some point, been handed a piece of generic business advice and thought: *this doesn't actually know my situation.* That's the gap BusinessLens AI was built to close. It's a multi-agent executive intelligence console: you describe your business and what's going on with it, and instead of a single chatbot improvising a response, a team of specialized agents — coordinated by a planning agent that decides which of them are even needed — produces a structured, explainable consulting report.

I built it for the **Agents for Business** track because the problem is unmistakably a business one: companies burn time and money getting advice that's either too generic to act on or too expensive to get from a real consultant on every question. The bet behind BusinessLens AI is that an agentic system, built on the **Google Agent Development Kit (ADK)**, can sit in that gap — cheaper and faster than a human consultant, but far more targeted than a single LLM prompt.

## 2. Problem Statement

Business analysis is hard for a reason that has nothing to do with intelligence: it's a *triage* problem before it's a *reasoning* problem. A company asking "why is my burn rate too high" needs an internal audit. A company asking "should we enter this new region" needs market research. A company asking both needs both — but most tools don't ask the question at all. They just run everything.

Generic LLM chatbots make this worse, not better, in three specific ways:

- **They don't distinguish request types.** A chatbot will happily generate a market analysis for a question that was never about the market, padding the answer with irrelevant sections because it has no mechanism to decide otherwise.
- **They don't ground themselves in anything external.** Ask a chatbot for market size or CAGR figures and it will produce plausible-sounding numbers with no real source behind them — a serious problem when a business might actually act on those numbers.
- **They don't show their work.** A single prompt-response exchange gives you no visibility into *why* the model focused on what it did, which makes the output hard to trust for anything consequential.

What's actually needed is a workflow that behaves the way a real consulting engagement behaves: someone triages the request first, brings in the right specialists only when they're relevant, grounds external claims in real data, and hands you a report you can see was built deliberately — not generated as a reflex.

## 3. Solution Overview

BusinessLens AI answers this with a **planner-routed multi-agent pipeline**. A user submits a business profile — company context, challenges, financial details, whatever they have. A **Planner Agent** reads that profile first and outputs a structured decision about which specialist agents the situation actually calls for. Only those agents run. A **Research Agent** and an **Analysis Agent** are gated behind that decision; a **Strategy Agent** always runs last to synthesize whatever specialist input is actually available into a final executive report.

The dynamic-planning piece is the whole point. It's what separates BusinessLens AI from "an LLM wrapped in a nice UI": the system's behavior visibly changes based on what you tell it, and that change is auditable — every agent, run or skipped, is logged with an explicit state, so a user watching the live execution timeline sees exactly what the system decided to do and can see the Planner's reasoning for why.

The second piece is grounding: when the Research Agent runs, it doesn't just generate market figures from its own priors — it calls a real tool to retrieve sector-specific benchmark data, and its final output is built on top of that tool response. That's a small detail with an outsized effect on trust: numbers a user might actually put in a deck came from somewhere traceable, not from the model's imagination.

## 4. System Architecture

BusinessLens AI is a decoupled three-tier system:

```
                       User
                        │
                        ▼
             React + Tailwind Frontend
             (submits profile, polls status)
                        │
                        ▼
                  FastAPI Backend
          (REST endpoints + async orchestrator)
                        │
                        ▼
             Google ADK Planner Agent
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
   Research Agent   Analysis Agent      │
   (+ market tool)                      │
         └──────────────┼───────────────┘
                        ▼
                 Strategy Agent
              (always synthesizes)
                        │
                        ▼
        Executive Strategic Blueprint (Markdown)
                        │
                        ▼
                 SQLite Database
         (projects / analyses / agent_logs)
```

- **Frontend (React + Vite + Tailwind CSS):** a single-page client that submits business profiles and short-polls the backend every 1500ms to update a live execution timeline, health dashboard, and final report.
- **Backend (FastAPI + SQLAlchemy + Pydantic):** exposes endpoints to register a project, trigger an asynchronous multi-agent run, and fetch current status plus full agent logs.
- **Database (SQLite):** three tables — `projects`, `analyses`, `agent_logs` — act as the shared state layer between the async background pipeline and the polling frontend, since there's no persistent socket connection.
- **AI Layer (Google ADK):** four `LlmAgent` instances plus one bound tool, described in detail below.

**Data flow:** the frontend posts a business profile → FastAPI writes it to `projects` and kicks off `run_orchestration_pipeline` as a background task → the Planner Agent runs first and writes its routing decision to `agent_logs` → Research and/or Analysis run conditionally, each writing their own log entry (`completed` or `bypassed`) → the Strategy Agent always runs last, consuming everything upstream produced → the final Markdown report is written to `analyses.final_report` and the frontend's next poll picks up the `completed` status and renders it.

## 5. Agent Design

**Planner Agent.** The routing brain. It reads the raw business profile and returns a structured `PlannerDecision` — `run_research`, `run_analysis` booleans plus a `reasoning` string — rather than free text. It exists because triage has to happen *before* any specialist work, or you're back to running everything by default.

**Research Agent.** Exists to ground external claims. It's only invoked when the Planner decides the situation needs outside context, and its instructions require it to call a bound tool, `market_search_lookup`, before compiling a market-size, competitor, and trend summary. It exists because a business report making market claims with no traceable source isn't trustworthy enough to act on.

**Analysis Agent.** The internal auditor. It combines the original profile with whatever research context is available and evaluates strengths, weaknesses, and capital efficiency. It exists because internal diagnostic work — burn rate, operational bottlenecks, resource dependency — is a fundamentally different skill from external market research, and conflating the two in one prompt produces shallower output on both.

**Strategy Agent.** The synthesizer, and the only agent that isn't schema-constrained, because its job is a long-form Markdown report, not a typed object. It exists because someone has to reconcile whatever mix of specialist input actually got produced — full pipeline or partial — into one coherent executive document, explicitly organized into Financial Operations, Strategic Market Interventions, and Risk Mitigations sections.

Splitting these into four narrow agents rather than one large prompt keeps each agent's instructions focused, keeps failures isolated and diagnosable (a Research failure doesn't have to take down Analysis), and — most importantly — makes the Planner's routing decision meaningful, since there's an actual boundary between "ran" and "didn't run" for each specialist role.

## 6. Google AI Concepts Used

This project was built to directly exercise several of the course's core concepts, not just reference them:

- **Google ADK (Agent Development Kit):** every specialist — Planner, Research, Analysis, Strategy — is implemented as a `google.adk.agents.LlmAgent`, not a bare API wrapper, giving each node a consistent `model` / `name` / `description` / `instruction` / `output_schema` / `tools` interface.
- **Gemini API:** all four agents run on `gemini-2.5-flash` under the hood, accessed through ADK.
- **Multi-Agent Orchestration:** an async orchestrator (`run_orchestration_pipeline`) sequences the four agents, passing each one's output forward as context for the next, and logging state transitions to a relational database.
- **Tool Calling:** the Research Agent is bound to a real Python function tool, `market_search_lookup(company_name, industry_sector)`. The model autonomously decides to call it, infers the correct arguments from unstructured input text, and incorporates the tool's response into its structured output — rather than fabricating market figures.
- **Structured Outputs:** the Planner, Research, and Analysis agents each declare a Pydantic `output_schema` (`PlannerDecision`, `ResearchOutput`, `AnalysisOutput`), so ADK enforces valid, typed responses at the model boundary before any application logic branches on them.
- **Dynamic Routing:** the Planner's `run_research` / `run_analysis` flags directly determine which agents execute for a given request — the pipeline shape itself changes based on model reasoning, not a fixed script.

## 7. Features

- **Live Execution Timeline** — real-time visibility into each agent's state (`running`, `completed`, `bypassed`, `failed`) as the pipeline executes.
- **Dynamic Agent Routing** — the Planner decides which specialists run, so two similar-looking requests can take genuinely different paths through the system.
- **Tool-Grounded Research** — market figures in the report trace back to an explicit tool call rather than model guesswork.
- **Business Health Dashboard** — a quantitative scorecard across Finance, Marketing, Operations, and Growth.
- **Multi-Format Report Export** — PDF, Markdown, and plain text, so the output is usable outside the app.

## 8. Technical Challenges

**Making a non-deterministic decision safe to branch on.** Early free-text planning output was unreliable to parse and occasionally self-contradictory. Binding a strict `output_schema` to the ADK `LlmAgent` fixed this almost entirely — the trade-off is a small amount of extra generation latency, which is worth it since a wrong-but-well-formed decision is recoverable while an unparseable one crashes the pipeline.

**Giving a tool worth calling, without an unbounded dependency.** `market_search_lookup` is a deterministic, sector-keyed lookup rather than a live web search. That was a deliberate choice: it lets the demo prove out real ADK tool-calling mechanics — the model choosing to call the tool and correctly inferring arguments — fully reproducibly, without the evaluation depending on third-party API uptime.

**Context drift across a variable-length pipeline.** Because Analysis and Strategy depend on outputs from agents that might not have run, bypassed nodes write an explicit `NODE_BYPASS_DIRECTIVE` into the log rather than leaving a silent gap, so downstream agents — and a human reading the logs later — always know whether missing context means "not analyzed" or "genuinely bypassed."

## 9. Results

A completed run produces an "Executive Strategic Blueprint" — a Markdown report with distinct sections for Financial Operations, Strategic Market Interventions, and Risk Mitigations — plus a Business Health Score across four dimensions. What makes the report useful isn't length; it's that its contents are traceable: a market claim in the Strategic Market Interventions section can be traced back to a specific `market_search_lookup` call, and an internal risk claim can be traced back to the Analysis Agent's own reasoning over the original profile, all visible in the agent logs behind the report.

The dynamic routing is visibly real, not decorative: business profiles emphasizing internal operational problems bypass the Research Agent entirely and get a leaner, faster report; profiles lacking competitive context trigger it and get the full pipeline. Two similar-looking submissions can produce meaningfully different execution paths and different reports, and that divergence is fully visible in the timeline rather than hidden inside one opaque model call — which is the core proof point the whole project is built around.

## 10. Future Work

- **Live web search / real MCP integration** — replacing the deterministic `market_search_lookup` with a live data source, exposed as a proper MCP server so the Research Agent's tool access is portable and swappable without touching agent code.
- **Retrieval-Augmented Generation** — letting users upload internal documents and grounding Analysis Agent output in retrieved passages rather than a single text profile.
- **Historical Report Comparison** — tracking a company's health scores and reports over time to surface trend lines, not just point-in-time snapshots.
- **Team Collaboration** — shared workspaces so multiple stakeholders can review and comment on the same analysis.
- **Real-time updates** — replacing 1500ms short-polling with Server-Sent Events or WebSockets.

## Closing

BusinessLens AI isn't trying to prove an LLM can write a business report — that's table stakes. It's trying to prove something narrower: that a planner-routed, tool-grounded multi-agent system, built on a real agent framework, can make a visible, justified decision about which work a situation actually needs, ground its claims in something real when it makes them, and show that reasoning the whole way through — instead of running everything, every time, and hoping nobody notices the padding.