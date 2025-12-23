# SKILL: Analyze (Insight Synthesis)

## Setup for Analyze Module
To begin work on the Analyze module, follow these initialization steps:

### 1. Files to Read
- **Global Context**: `AGENTS.md`, `docs/00-product-orchestration.md`
- **Domain Specification**: `docs/02-analyze/overview.md`
- **Active Tasks**: `docs/02-analyze/tasks.md`

### 2. Main Goal
Review discovered VODs and match data (RIB/VLR) to synthesize tactical insights, detect team tendencies, and generate interactive visualizations for the coaching dashboard.

### 3. Steps to Take
1. **Contextualize**: Reference the `VodResult[]` list generated in a "Find" session.
2. **Execute**: Implement the synthesis logic using Gemini 3 Flash and build visualization data loaders in `src/components/dashboard/analyze-view.tsx`.
3. **Verify**: Ensure every tactical claim is cited with a valid `round_id` and that the UI charts render correctly.
4. **Log**: Update `docs/02-analyze/changelog.md` and check off completed items in `docs/02-analyze/tasks.md`.

---

## Capabilities
- **Data Cross-Referencing**: Sync rib.gg rounds with VLR.gg performance metrics.
- **Trend Detection**: Identify shifts in team positioning or utility usage (e.g., "A-Long aggression").
- **Visualization**: Generate data for frontend charts (Trend success deltas).
- **Synthesis**: Produce natural language tactical summaries with citations.

## Data Schemas
- Input: `VodResult[]` from Find session.
- Output: `TacticalAnalysis` and `ChartData[]`.

## Operational Constraints
- **Traceability**: Every claim must cite a `round_id`.
- **Latency**: Synthesis must use Gemini 3 Flash for fast streaming responses.