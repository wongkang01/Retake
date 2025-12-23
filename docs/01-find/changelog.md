# Changelog: Find (Discovery & Retrieval)

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
