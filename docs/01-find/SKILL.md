# SKILL: Find (Discovery & Retrieval)

## Setup for Find Module

### 1. Main Goal
Maintain and query a high-quality library of tactical round documents. Users query this pre-indexed dataset (e.g., VCT Champions 2025) to retrieve precise, timestamped VOD results.

### 2. Capabilities
- **Recursive Crawling**: Drill down into rib.gg events using Playwright to find match IDs.
- **Hybrid Retrieval**: Extract intent (Team, Map, Round Type) using Gemini and apply hard metadata filters before semantic search.
- **Data Fidelity**: Track running match scores and tactical round ceremonies (Thrifty, Flawless).
- **Interactive VOD**: Auto-seek YouTube players based on game-time offsets.

### 3. Data Schemas
- **Input**: Natural Language Query (e.g., "PRX flawless rounds on Sunset").
- **Intent**: `{ team_slug: 'paperrex', map: 'Sunset', round_type: 'flawless' }`.
- **Output**: `MatchResult[]` with `vod_timestamp`, `video_id`, and `score_a/b`.

### 4. Operational Constraints
- **Deduplication**: Always deduplicate results by `round_id` from the source.
- **Relevance**: Apply a cosine distance threshold of 0.60 to maintain clip quality.
- **VOD Precision**: Timestamps must be calculated via `vod_start + (round_gametime - match_start_gametime)`.
