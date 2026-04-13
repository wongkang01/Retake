# Find Module — Structured Query Migration Plan

**Status:** Proposed
**Author:** Architecture review session, 2026-04-08
**Scope:** Find (Discovery & Retrieval) module

## TL;DR

The current Find pipeline embeds templated round summaries into a pgvector column and runs cosine search against them. After auditing the actual rib.gg data source and the actual query outputs, the embeddings are carrying almost no weight — every round produces a near-identical vector because the "summary" is just a templated concatenation of the same 7 categorical fields. Observed cosine distances on successful queries sit in the 0.28–0.37 range *only* for data in the current embedding space; cross-model drift pushed them to ~0.96 and made the system return empty results until the filter path masked the problem.

Meanwhile, rib.gg's `__NEXT_DATA__` payload ships **5–10× more structured data per round** than `processor.py` currently extracts — including every kill event with coordinates, trade chains, economy tiers, NvM clutch situations, per-player per-round statistics, and agent picks. The fields required to answer "hard" compositional queries (entry-frag retakes, eco-string comebacks, single-player thrifty carries) are already in the payload; the current processor just throws them away.

**The migration:** shift Find's NLP layer from "embed → cosine search" to "text-to-structured-query". The LLM becomes a translator from natural language into a typed query object, and the database executes it as a filter + join directly. Embeddings stay in the schema as dead weight for now and only come back if we ever add unbounded text (transcripts, scouting notes, chat).

## Context and Evidence

### What triggered this review

1. `text-embedding-004` deprecated 2026-01-14, breaking `/query` with a 404 at the embedding step.
2. Swap to `gemini-embedding-001` (at 768 dims) restored queries — but only for freshly-ingested data. Pre-existing Champions 2025 vectors are in the old embedding space and comparisons against new query vectors are cross-space garbage (~0.96 distance).
3. A filter-interaction bug was masking the issue: `filter_round_type="pistol"` was being AND-ed with `filter_is_pistol=true` in `match_rounds`, but no row has `round_type="pistol"` (pistol is a round position, not a ceremony). Fixed in commit `abb8a9b`.
4. Audit of the real rib.gg payload revealed the data source is far richer than the current processor assumes.

### What rib.gg actually ships per series

Confirmed via live inspection of `https://rib.gg/series/100138` (Paper Rex vs Team Heretics, Masters Santiago 2026):

- **`series.stats.kills[]`** — 417 kill events for the series. Per kill: `killerId`, `victimId`, `roundTimeMillis`, `gameTimeMillis`, `victimLocationX/Y` (map coordinates), `damageType` (`ability`/`weapon`), `abilityType`, `weapon`, `weaponCategory`, `first` (first blood flag), `tradedByKillId`, `tradedForKillId`, `killerTeamNumber`, `victimTeamNumber`, `side`, `assistants[]`. **68 of 417 kills flagged as traded.**
- **`series.stats.xvys[]`** — 188 NvM situations pre-labeled by rib.gg. Sample distribution from one series: `3v3 ×12`, `5v4 ×11`, `1v3 ×6`, `1v4 ×6`, `5v1 ×2`. Each entry has `situation`, `teamNumber`, `side`, `wins`, `losses`. **14 tough clutches (1v3+) in a single series, all pre-labeled.**
- **`series.stats.rounds[]`** — per round: `ceremony` (`default`, `ace`, `team_ace`, `clutch`, `thrifty`, `flawless`, `closer`), `winCondition` (`kills`, `defuse`, `time`, `detonation`), `team1LoadoutTier` / `team2LoadoutTier` (1=eco, 4=full buy), `attackingTeamNumber`.
- **`series.playerStats[]`** — 600 entries (10 players × ~60 rounds). Per row: `acs`, `kills`, `firstKills`, `deaths`, `firstDeaths`, `assists`, `damage`, `headshots`, `bodyshots`, `legshots`, `plants`, `defusals`, `clutches`, `clutchOpponents`, `clutchOpportunities`, `kastRounds`, `impact`.
- **`match[].players[]`** — agent picks per player per map: `{playerId, agentId, player: {ign}}`.
- **`match[].stats[]`** — series-aggregate per player: `rating`, `attackingRating`, `defendingRating`, `score`, KDA, playtime.

Current `processor.py` extracts only: `map_name`, `match_id`, `round_num`, `winning_team`, `team_a/b`, `score_a/b`, `is_pistol`, `round_type` (from `ceremony` directly, without mapping `team_ace`/`closer`), `vod_url`, `vod_timestamp`, `win_condition`. Everything else above is discarded.

### Why template embeddings were wasted compute

The current ingested `summary` is a templated sentence like:

> *"On the map Ascent in match 216884, The score was 8-9. Round 18 was won by Team Heretics by kills. This was a clutch round. The VOD for this round starts at approximately 2540 seconds."*

Every round in the database is this template with seven slot-fills. The vectors are effectively hash codes for `(map × round_type × winner × win_condition × round_num)` tuples — information that is already present as structured columns in the same row. The embedding model has nothing to latch onto beyond those categoricals, so every "clutch on Ascent won by PRX" vector is near-identical to every other. Sorting by cosine distance within a metadata filter is approximately random.

### Can SQL answer the "hard" queries?

Re-audit of the four queries I previously marked as requiring semantic search:

| Query | Previous verdict | Actual verdict with rib.gg data |
|---|---|---|
| Entry fragger died but team won on retake | ❌ semantic | **✅ clean SQL** — `kills.first`, `kills.victim_id`, `winCondition='defuse'`, side='def' |
| Comebacks after losing pistol + two ecos | ❌ semantic | **✅ trivial SQL** — `rounds.team[12]LoadoutTier` string + final score |
| Thrifty rounds where a single player carried | ❌ semantic | **✅ clean SQL** — `ceremony='thrifty'` + `MAX(playerStats.kills) >= 3` |
| Post-plant holds where the defuser got picked | ❌ semantic | **⚠️ approximate SQL** — data gap (no defuse-start events), not an NLP gap |

**Three of the four are pure SQL** once the events stream is extracted. The one exception ("defuser got picked") fails because rib.gg does not ship defuse-start/interrupted events, not because natural-language parsing is too hard. No amount of embedding work recovers information that isn't in the source payload.

## The Architectural Pivot

### From: embed-and-match

```
query text → embed → cosine search over round vectors → metadata filter → results
              ↑
          both parsing AND matching happen here
```

### To: text-to-structured-query

```
query text → LLM translator → typed query object → SQL / RPC → results
              ↑
          parsing only — matching is pure relational
```

The LLM's job is translation from a bounded natural-language domain to a bounded structured-query domain. The database does the matching. Embeddings are no longer in the hot path.

### Component delta

| Component | Before | After |
|---|---|---|
| Gemini Flash intent extraction | `{team, map, round_type}` JSON | Rich query object (see schema below) |
| Keyword pre-scan (`TEAM_MAP`) | team only | teams, maps, ceremonies, weapons, agents |
| `match_rounds` RPC | 4 filter params | Expanded filters + join-backed computed predicates |
| Query-time embedding call | required | **removed** |
| Ingest-time embedding call | required per round | **removed** |
| `round_embeddings.embedding` column | used | dormant; kept in schema, dropped later |
| Local ChromaDB path | fallback | removed entirely |

## Phased Implementation

### Phase 1 — Structured extraction from rib.gg (unblocks everything)

The single biggest value unlock. Rewrite `processor.py::process_series_data()` to pull from the full `__NEXT_DATA__` payload instead of a narrow slice. Add matching Supabase tables/columns.

**Per-round fields to add** (from `stats.rounds`, `stats.xvys`, `stats.kills`):
- `loadout_tier_a`, `loadout_tier_b`, `loadout_delta` (integers 1–4)
- `attacking_team_number`, `defending_team_number`
- `first_blood_killer_id`, `first_blood_side`, `first_blood_weapon_category`, `first_blood_was_ability`
- `trade_count`, `traded_ratio`
- `max_xvy_for_team_a`, `max_xvy_for_team_b` (e.g., `"1v3"`)
- `xvy_resolved_situation`, `xvy_winner_team_number`
- `multikill_max` (largest single-player kill count in the round)
- `ability_kill_count`, `weapon_kill_count`
- Fix `round_type` mapping to distinguish `team_ace`, `closer`, and `pistol`-derived labels rather than falling through to `default`.

**New child table `round_player_stats`** — one row per player per round. Columns mirror `playerStats[]`: `round_id`, `player_id`, `ign`, `agent_id`, `agent_name`, `team_number`, `side`, `acs`, `kills`, `first_kills`, `deaths`, `first_deaths`, `assists`, `damage`, `headshots`, `bodyshots`, `plants`, `defusals`, `clutches`, `clutch_opponents`, `clutch_opportunities`, `kast_rounds`, `impact`.

**New table `match_players`** — one row per player per map: `match_id`, `player_id`, `ign`, `agent_id`, `agent_name`, `team_number`.

**New table `kills`** — optional but high-value. One row per kill event. Enables spatial queries and retake reconstruction. If storage/write cost is acceptable, include it; otherwise defer until Phase 3.

**Agent lookup table** — tiny static table: `agent_id → agent_name`. One-time seed from rib.gg or hardcoded.

**Migration work:**
1. Author new Supabase migrations adding the tables and columns above.
2. Rewrite `processor.py` to extract the new fields. Preserve the existing output shape as a superset so nothing in `ingestion.py` breaks until Phase 2.
3. Update `ingestion.py::ingest_batch()` to write the new rows/columns alongside the existing ones.
4. Re-ingest one tournament end-to-end (Masters Santiago 2026 is the natural test target since it's already in the new embedding space — or will be purely structured after this phase). Verify counts and spot-check a round's derived fields against the rib.gg UI.

**What this unlocks immediately:**
- Every "filter-only" query gets new vocabulary: economy state, first-blood, trade density, xvy situations, per-player stats, agent compositions, weapon categories.
- The three "hard" queries from the re-audit become expressible as pure SQL.

### Phase 2 — Expand the intent schema

Replace the `{team_slug, map, round_type}` JSON schema with a richer one. The intent extractor still runs as one Gemini Flash call per query — only the prompt and output schema change.

**Proposed intent schema (v2):**

```json
{
  "filters": {
    "team_slug": "paperrex",
    "opponent_slug": null,
    "map_name": "Ascent",
    "ceremony": "clutch",
    "win_condition": "defuse",
    "is_pistol": false,
    "winning_side": "def",
    "loadout_tier_min": null,
    "loadout_tier_max": 2,
    "agent_picks": ["Jett"],
    "weapon_category": null
  },
  "player_predicates": {
    "ign": "f0rsakeN",
    "min_kills_in_round": 3,
    "was_first_blood": null,
    "was_clutcher": true
  },
  "round_predicates": {
    "had_xvy_at_least": "1v3",
    "entry_fragger_died": null,
    "single_player_carry": null,
    "multikill_min": null
  },
  "preconditions": {
    "lost_pistol_round": null,
    "won_pistol_round": null,
    "eco_string_length_min": null
  },
  "event_scope": {
    "event_id": "uuid-or-null"
  }
}
```

Each field maps 1:1 to a SQL predicate on the Phase-1 tables. Unset fields are ignored.

Prompt engineering notes:
- Few-shot examples are mandatory for the nested predicate categories — the model will hallucinate field names otherwise.
- Use `response_mime_type='application/json'` with a schema definition passed to the SDK (Gemini supports structured output constraints).
- Keep the existing `TEAM_MAP` keyword pre-pass; it's a cheap hint that improves intent accuracy and protects against LLM omissions.
- Validate the returned JSON against a Pydantic model in Python before executing. Any unknown field → reject and fall back to a simpler filter set with a warning in the Discovery Log.

### Phase 3 — Execution layer: expanded RPC, then DSL

**Step 3a — Expand `match_rounds`.**
Add parameters to the RPC for every field in the Phase-2 intent schema. This is the "fixed vocabulary" path: fast, debuggable, easy to cache. Migration adds filter columns like `filter_loadout_tier_max`, `filter_entry_fragger_died`, etc. Rewrite the query body to apply the new predicates in the `WHERE` clause and join `round_player_stats` when a player predicate is present.

This alone handles ~90% of expected query patterns. It's what ships first.

**Step 3b — Introduce a query DSL for compositional cases.**
Some predicates don't fit neatly into a flat parameter list (e.g., `eco_string_length_min: 2` requires a window function over rounds by round number). When the intent object includes those, route the execution through a small in-house DSL compiler that produces parameterized SQL.

DSL goals:
- Typed and finite — no open-ended text-to-SQL generation. The DSL grammar is hand-defined; the LLM only picks known DSL nodes.
- Compiled to parameterized queries, never string-interpolated (no SQL injection surface).
- Deterministic and testable: same DSL input → same SQL output.
- Observability built in: every generated SQL query is logged alongside the original natural-language query for audit.

**Explicitly not doing:** free-form LLM-generated SQL. The cost of a hallucinated `DROP TABLE` or a query that leaks data across events is higher than the value of that flexibility, and a well-designed DSL + expanded RPC covers the real query space.

### Phase 4 — Decommission embeddings (or preserve for future text content)

Once Phases 1–3 are live and the query path is structured end-to-end:

**Option A — Full decommission.**
Delete the ingest-side `_generate_embedding` call, drop the `embedding` column from `round_embeddings`, remove the ChromaDB path and the query-side embedding call. Simplest, lowest operational burden, cheapest.

**Option B — Preserve column, disable generation.**
Keep the `embedding` column in the schema but stop populating it. No query-side embedding calls. Lets you revive vector search quickly if unbounded text (transcripts, scouting notes, forum takes) joins the data model.

**Recommendation:** Option B, with a clear note in the schema migration. Reviving vectors later costs one column addition if we decommissioned; keeping the column dormant costs nothing meaningful.

### Phase 5 (optional, speculative) — Vectors for unbounded content

Only pursued if the data model grows to include free-form text that cannot be derived from rib.gg's structured fields. Candidates:

- **VOD audio transcription** — caster/player commentary, team comms where available
- **Scouting notes / coach annotations** — user-generated content
- **Post-match interviews, forum discussions** — external narrative data

For any of these, vector search over their text (not over templated summaries) would be the right tool. At that point, the architecture becomes **dual-index**: structured queries over rib.gg fields, vector queries over the text corpus, and a router that dispatches based on what the query is actually asking for.

This phase is a placeholder — do not build it preemptively.

## Open Questions and Risks

- **Phase 1 re-ingest cost.** Rewriting the processor means every existing tournament needs to be re-ingested (or backfilled via an update-in-place script that re-parses stored `__NEXT_DATA__`, if we start persisting the raw payload). Decide early whether to snapshot `__NEXT_DATA__` at ingest time so future schema expansions don't require re-scraping.
- **Intent-extraction accuracy.** The richer the schema, the more ways the LLM can mis-fill it. Need an eval harness: a fixed set of natural-language queries with expected intent JSON outputs, run against every prompt change. Phase 2 should not ship without this.
- **Event scoping.** The current `/query` endpoint accepts `filters.event_id` but silently ignores it (`endpoints.py:34`, never read). This is a separate bug that Phase 3a must fix as part of the RPC expansion.
- **Hardcoded "Champions 2025" labels in the frontend.** `find-view.tsx:114, 123, 180, 250` hardcode the string. Not part of this plan but should be fixed alongside Phase 3 to match whatever event the user selected.
- **Data gaps we cannot close.** Queries that depend on fields rib.gg does not ship (defuse-start timing, utility usage beyond ability kills, voice comms) are structurally unanswerable regardless of architecture. Document these and do not pretend embeddings would solve them.

## Phase Order Recap

1. **Phase 1 — Structured extraction.** Biggest unlock. Rewrite `processor.py`, add tables, re-ingest one tournament, verify fields.
2. **Phase 2 — Intent schema v2.** New Pydantic model, new LLM prompt, eval harness.
3. **Phase 3a — Expanded `match_rounds` RPC.** Add filter params, rewrite query body, fix `event_id` scoping bug.
4. **Phase 3b — Query DSL.** Introduced only when Phase 3a parameters stop fitting the query patterns.
5. **Phase 4 — Embedding decommission (Option B).** Stop writing, keep column dormant.
6. **Phase 5 — Vectors for unbounded text.** Only if/when free-form content enters the data model.

Phase 1 is the critical path; everything else is layered on top and can be sequenced based on user feedback.
