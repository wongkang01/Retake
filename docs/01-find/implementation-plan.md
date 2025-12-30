# Implementation Plan: Find (Discovery & Retrieval)

## Phase 1: Architectural Foundation (Completed)
1. **Scraper Service Refactor**
   - Implemented `httpx` with **Playwright** (Chromium) smart fallback.
   - Standardized `RawMatchData` Pydantic models.
2. **ChromaDB Integration**
   - Configured `google-genai` (text-embedding-004) for semantic search.
   - Implemented idempotent ingestion via MD5 hashing of round data.
3. **API Core**
   - FastAPI `/query` and `/ingest` endpoints secured by API key (optional).

## Phase 2: Tournament Library & Hybrid Search (Completed)
1. **Tournament Ingestion**
   - Developed `TournamentCrawler` for recursive event discovery.
   - Implemented canonical deduplication for unique Series IDs.
   - Built `/admin/ingest-event` for bulk population.
2. **Hybrid Retrieval Pipeline**
   - Built an **Intent Agent** to extract Team Slugs and Map names.
   - Implemented **Hard Pre-filtering** to solve Team Name confusion (PRX vs DRX).
   - Applied strict distance thresholding (0.60) to eliminate low-quality results.
3. **Core Find UI**
   - Search interface for the Champions 2025 Library.
   - Precision VOD player with YouTube iframe API integration.

## Phase 3: Scaling & Optimization (Completed)
1. **Database Migration**
   - Migrated from local ChromaDB to **Supabase (pgvector)** for production access.
   - Created `round_embeddings` table with team names, slugs, and VOD metadata.
   - Implemented `match_rounds` RPC function with conditional threshold logic.
2. **Hybrid Search Fix**
   - Fixed metadata filters to act as **hard pre-filters** (no threshold when filters present).
   - Similarity threshold (0.5) now only applies to pure semantic queries.
   - Resolved PostgREST compatibility by accepting `float[]` and casting to `vector(768)`.
3. **Data Fidelity**
   - Added `team_a`, `team_b`, `vod_timestamp` columns to round embeddings.
   - Fixed VOD URL construction with proper YouTube video ID extraction.

## Phase 4: Future Optimizations
1. **Performance**
   - Implement Matryoshka learning hooks (3072 -> 768 dim).
   - Add embedding cache to reduce Gemini API costs.
2. **Advanced Filtering**
   - Add agent-based filtering support.
   - Implement round economy/loadout filtering.