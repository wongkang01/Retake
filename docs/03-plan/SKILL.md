# SKILL: Plan (Strategic Planning)

## Setup for Plan Module
To begin work on the Plan module, follow these initialization steps:

### 1. Files to Read
- **Global Context**: `AGENTS.md`, `docs/00-product-orchestration.md`
- **Domain Specification**: `docs/03-plan/overview.md`
- **Active Tasks**: `docs/03-plan/tasks.md`

### 2. Main Goal
Generate actionable, probabilistic counter-strategies against specific opponents based on the behavioral trends identified in the Analyze module.

### 3. Steps to Take
1. **Contextualize**: Load the `TacticalAnalysis` summary from the previous "Analyze" session.
2. **Execute**: Build the strategy card generator and habit checklist components in `src/components/dashboard/plan-view.tsx`.
3. **Verify**: Ensure predicted success rates are grounded in actual historical data and that steps are tactically sound for Valorant.
4. **Log**: Update `docs/03-plan/changelog.md` and check off completed items in `docs/03-plan/tasks.md`.

---

## Capabilities
- **Counter-Strategy Generation**: Propose specific executes/holds to punish detected opponent habits.
- **Scenario Simulation**: Estimate success rates based on similar-but-successful historical rounds.
- **Playbook Formatting**: Generate step-by-step instructions for team briefings.

## Data Schemas
- Input: `TacticalAnalysis` from Analyze session.
- Output: `StrategyCard[]` and `HabitChecklist`.

## Operational Constraints
- **Probabilistic Accuracy**: Predictions must be grounded in actual retrieved data, not hallucinated.
- **Actionability**: Plans must be specific to Valorant tactical domains (Utility, Timing, Spacing).