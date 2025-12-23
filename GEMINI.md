# GEMINI.md - Project Context: Retake

## Project Overview
**Retake** is an AI-powered intelligence platform designed for Valorant esports coaches. It transforms manual VOD review into a semantic search experience, allowing coaches to find specific tactical moments and receive AI-generated analysis with direct, timestamped VOD links.

The project is currently migrating from a prototype phase (v1) to a production-ready architecture (v2).

### Core Workflow
1. **Find**: On-demand discovery and ingestion of professional match data based on query intent.
2. **Analyze**: Processing VODs and stats (rib.gg/VLR) to generate visualizations and tactical insights.
3. **Plan**: Proposing strategic playbooks based on analysis results for specific opponents.

## Technology Stack
- **Frontend**: React 19, TypeScript, TanStack Start, Tailwind CSS v4, shadcn/ui, Bun.
- **Backend**: Python 3.10+, FastAPI, Pydantic.
- **AI/ML**: Google Gemini (gemini-embedding-001 / gemini-3-pro), ElevenLabs (Voice), ChromaDB.
- **Data Pipeline**: httpx, Selenium, BeautifulSoup4.

## Project Structure
- `src/`: v2 Frontend implementation (TanStack Start).
  - `components/dashboard/`: Modular views for Home, Find, Analyze, and Plan.
- `docs/`: Consolidated project documentation (Source of Truth).
  - `00-product-orchestration.md`: Workflow and data flow between stages.
  - `01-vision-and-scope.md`: Mission, objectives, and KPIs.
  - `02-architecture-and-stack.md`: System design and technology choices.
  - `03-feature-guide.md`: User stories and feature details.
  - `01-find/`: Implementation plans, tasks, and changelogs for Discovery & Retrieval.
  - `02-analyze/`: Implementation plans, tasks, and changelogs for Analysis & Insights.
  - `03-plan/`: Implementation plans, tasks, and changelogs for Strategic Planning.
  - `shared/`: Shared schemas, types, and technical specs.

## Building and Running
- **Frontend**: `bun install` -> `bun run dev` (Port 3000).
- **Backend**: Legacy scripts in `reference_archive/`. v2 FastAPI refactor in progress.

## Development Conventions
- **Domain-Driven Docs**: Always check the specific feature folder (`docs/01-find/`, etc.) for current tasks.
- **Session Continuity**: Every build step must ensure compatibility with the `Product Orchestration` data flow.
- **Dark Mode Only**: The UI is enforced in dark mode via the root document.