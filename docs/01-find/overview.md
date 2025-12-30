# 01 - Find: Discovery & Retrieval Spec (v2)

## Core Objectives
- **Event Library Model**: Transitioned from on-the-fly scraping to a pre-indexed tournament library for instant search (<500ms).
- **Hybrid Retrieval**: Combining hard metadata pre-filtering (Team Slugs, Maps) with semantic vector search to eliminate "noise" (e.g., preventing PRX results from showing DRX).
- **Tactical Precision**: Retrieving specific round states (Thrifty, Pistol, Flawless) with exact VOD timestamps.

## 1. Search & Intent Logic
The search bar uses a **Hybrid Intent Agent** (Gemini 3 Flash) to parse queries:
| Intent Component | Logic | Example |
|-----------------|-------|---------|
| **Team Slug** | Hard Pre-filter (e.g., `paperrex`) | "PRX rounds..." |
| **Map Name** | Hard Pre-filter (e.g., `Sunset`) | "...on Sunset" |
| **Round Type** | Hard Pre-filter (`thrifty`, `pistol`) | "thrifty rounds" |
| **Semantic Query**| Vector Similarity (Cosine) | "fast A executes" |

### Hybrid Search Logic
The `match_rounds` PostgreSQL function implements a **conditional threshold** strategy:

| Query Type | Metadata Filters | Threshold Applied | Behavior |
|------------|------------------|-------------------|----------|
| **Filtered** | team/map/round_type present | **No** | Hard pre-filters only, ranked by similarity |
| **Semantic** | None present | **Yes (0.5)** | Threshold gates results, ranked by similarity |

This ensures:
- Filtered queries (e.g., "prx thrifty haven") return ALL matching rounds regardless of semantic similarity
- Pure semantic queries (e.g., "fast A executes") are gated by quality threshold

## 2. Result Display Logic
- **Precision Cards**: Each result shows the score at the **start of the round**, the round number, and the specific win condition.
- **Match %**: Displays a semantic similarity confidence score (1 - distance).
- **Interactive VOD**: Clicking "Watch VOD" triggers a functional YouTube embed that auto-seeks to the specific round start.

## 3. Ingestion Architecture
1.  **Crawl**: Recursive `TournamentCrawler` using **Playwright** identifies all unique Series IDs.
2.  **Deduplicate**: Canonical URL enforcement prevents processing the same match twice.
3.  **Process**: `MatchDataProcessor` extracts running scores, win conditions, and VOD offsets.
4.  **Embed**: Gemini `text-embedding-004` generates 768-dim vectors for each round summary.
5.  **Index**: `IngestionService` stores rounds in **Supabase (pgvector)** with ChromaDB as fallback.

## 4. Database Architecture
- **Primary**: Supabase PostgreSQL with `pgvector` extension
  - `round_embeddings` table stores vectors and metadata
  - `match_rounds` RPC function handles hybrid search
- **Fallback**: Local ChromaDB for development/offline use
- **Schema**: `team_a`, `team_b`, `team_a_slug`, `team_b_slug`, `winner_slug`, `map_name`, `round_type`, `vod_url`, `vod_timestamp`, `embedding`
