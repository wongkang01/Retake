# AGENTS.md - AI Agent Operational Guide

This file provides machine-readable context for AI coding agents (Gemini, Claude, Copilot) working on the **Retake** project.

## Project Mission
Retake is a tactical intelligence platform for Valorant coaches. It uses a three-stage RAG pipeline: **Find** (Discovery), **Analyze** (Synthesis), and **Plan** (Strategy).

## System Orchestration
Agents must adhere to the linear data flow defined in [docs/00-product-orchestration.md](docs/00-product-orchestration.md).

### Domain-Specific Skills
Each core feature is treated as an autonomous "Skill". Agents should load the corresponding `SKILL.md` before performing tasks in these directories:
- **Find**: [docs/01-find/SKILL.md](docs/01-find/SKILL.md)
- **Analyze**: [docs/02-analyze/SKILL.md](docs/02-analyze/SKILL.md)
- **Plan**: [docs/03-plan/SKILL.md](docs/03-plan/SKILL.md)

## Tech Stack & Conventions
- **Frontend**: TanStack Start (React 19), Tailwind v4, Bun.
- **Backend**: FastAPI (Python 3.10), ChromaDB.
- **AI Models**: Gemini 3 Pro/Flash, ElevenLabs (Voice), gemini-embedding-001.
- **Styling**: Sharp, "Rounded-None" aesthetic, dark-mode only.

## Development Workflow
1. **Initialize**: Read this file and `docs/00-product-orchestration.md`.
2. **Contextualize**: Load the relevant `SKILL.md` and `implementation-plan.md`.
3. **Verify**: Run `bun run dev` for frontend changes or `pytest` for backend logic.
4. **Log**: Update the `changelog.md` and `tasks.md` in the feature directory after every task.

## Critical Harnesses
- **Session Context**: The primary mechanism for state transfer between Find, Analyze, and Plan.
- **Discovery Service**: The agentic layer that handles on-demand ingestion from rib.gg.
