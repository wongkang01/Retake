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

## 2. Result Display Logic
- **Precision Cards**: Each result shows the score at the **start of the round**, the round number, and the specific win condition.
- **Match %**: Displays a semantic similarity confidence score (1 - distance).
- **Interactive VOD**: Clicking "Watch VOD" triggers a functional YouTube embed that auto-seeks to the specific round start.

## 3. Ingestion Architecture
1.  **Crawl**: Recursive `TournamentCrawler` using **Playwright** identifies all unique Series IDs.
2.  **Deduplicate**: Canonical URL enforcement prevents processing the same match twice.
3.  **Process**: `MatchDataProcessor` extracts running scores, win conditions, and VOD offsets.
4.  **Index**: `IngestionService` generates semantic descriptions (e.g., "This was a thrifty round...") and stores them in ChromaDB.
