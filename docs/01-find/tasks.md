# Tasks: Find (Discovery & Retrieval)

## Backend Tasks (FastAPI / Python)

### Phase 1: Architectural Foundation
- [x] **Scraper Service Refactor**
    - [x] Initialize `backend` directory structure with `uv`.
    - [x] Implement **Playwright** Chromium fallback.
    - [x] Define `RawMatchData` Pydantic models.
- [x] **ChromaDB Optimization**
    - [x] Configure ChromaDB with `google-genai` (text-embedding-004).
    - [x] Implement **Idempotent Ingestion**.
- [x] **API Endpoints**
    - [x] Define `/query` and `/ingest` endpoints.

### Phase 2: Tournament Library & Retrieval
- [x] **Event Library (Bulk Ingestion)**
    - [x] Create `TournamentCrawler` (Recursive + Playwright).
    - [x] Implement **Canonical Deduplication** (18 unique matches found for Champions 2025).
    - [x] Implement `BulkIngestWorker` and `/admin/ingest-event` endpoint.
- [x] **Hybrid Retrieval**
    - [x] Implement **Intent Detection Agent** (Extract slugs, map, round_type).
    - [x] Implement **Hard Metadata Pre-filtering** (Solves PRX vs DRX confusion).
    - [x] Implement **Strict Relevance Threshold** (Distance <= 0.60).
- [x] **Data Refinement**
    - [x] **Running Score**: Track score at start of round.
    - [x] **Tactical Tagging**: Support for thrifty, flawless, and pistol rounds.

### Phase 3: Production Scaling
- [x] **Supabase Migration**: Move to centralized pgvector storage.
    - [x] Create `round_embeddings` table with team names and VOD metadata.
    - [x] Implement `match_rounds` RPC function with conditional threshold.
    - [x] Add `team_a`, `team_b`, `vod_timestamp` columns.
- [x] **Hybrid Search Fix**: Implement correct conditional threshold logic.
    - [x] Metadata filters act as hard pre-filters (no threshold).
    - [x] Semantic-only queries gated by 0.5 similarity threshold.
    - [x] Fix PostgREST compatibility (`float[]` → `vector(768)` cast).
- [ ] **Matryoshka Hooks**: Implement 768-dim truncation.
- [ ] **Embedding Cache**: Cache text-to-vector mappings.

---

## Frontend Tasks (React / TypeScript)

### Phase 2: Core UI & UX
- [x] **Search UI**
    - [x] Build search bar for Champions 2025 library.
    - [x] Display **Detected Intent Badges** (Team, Map, etc.).
- [x] **Result Visualization**
    - [x] Implement `ResultCard` with winner highlighting and Match %.
    - [x] Display round type and running scores.
- [x] **Interactive VOD Player**
    - [x] Functional YouTube Embed with dynamic `videoId` and `start` timestamp.