# Changelog: Find (Discovery & Retrieval)

## [2025-12-30] - Phase 3 Supabase Migration & Hybrid Search Fix

### Added
- Migrated to **Supabase (pgvector)** as primary database with ChromaDB fallback.
- Created `round_embeddings` table with `team_a`, `team_b`, `vod_timestamp` columns.
- Implemented `match_rounds` PostgreSQL RPC function with conditional threshold logic.
- Added proper team name display (no more "Unknown" teams).

### Changed
- **Hybrid Search Logic**: Metadata filters now act as **hard pre-filters**.
  - Filtered queries (team/map/round_type): No similarity threshold, just pre-filter + rank by similarity.
  - Semantic queries (no filters): Apply 0.5 similarity threshold.
- Function signature changed from `vector(768)` to `float[]` for PostgREST compatibility.
- Embedding conversion: Now explicitly converts to Python list for proper JSON serialization.

### Fixed
- Fixed "prx thrifty haven" returning 0 results (was applying threshold to filtered queries).
- Fixed VOD URL construction with proper YouTube video ID extraction.
- Fixed team names not displaying in query results.

---

## [2025-12-19] - Phase 1 Backend Foundation

### Added
- Initialized `backend/` directory using `uv` for dependency management.
- Implemented `FastAPI` application with `/query`, `/ingest`, and `/health` endpoints.
- Created `ScraperService` with `httpx` and `BeautifulSoup4` for `__NEXT_DATA__` extraction.
- Configured `ChromaDB` persistent client with Gemini embedding function.
- Implemented `IngestionService` with MD5-based idempotency.
- Added `X-API-Key` middleware for internal API security.
- Defined `RawMatchData` Pydantic models for standardized data flow.

### Changed
- Migrated from `requirements.txt` to `pyproject.toml` managed by `uv`.
