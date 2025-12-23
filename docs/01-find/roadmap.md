# Development Roadmap & Milestones

## Current Progress: v2 Scaling

### Phase 1: Foundation (Completed)
- [x] Scaffold TanStack Start + Tailwind v4.
- [x] Refactor Scraper to use Playwright (anti-bot bypass).
- [x] Implement Gemini Ingestion pipeline.

### Phase 2: Tournament Library & Retrieval (Completed)
- [x] **Tournament Crawler**: Recursive event discovery.
- [x] **Hybrid Retrieval**: Hard metadata pre-filtering + semantic search.
- [x] **UI Polish**: Precision VOD player and match results.

### Phase 3: Production Access (Weeks 5-6) - **NEXT**
- [ ] Centralized Database: **Supabase (pgvector)** migration.
- [ ] Matryoshka Dim-Reduction for retrieval speed.
- [ ] Redis/Embedding Caching.

### Phase 4: Insights & Analysis (Weeks 7-8)
- [ ] Cross-referencing VLR.gg stats.
- [ ] Tactical synthesis with Gemini 3 Pro.
- [ ] ElevenLabs Voice proxy.