# Database Migration: ChromaDB to Supabase (pgvector)

## Overview
To support multi-user production access and relational data integrity, Retake is migrating its vector storage from local ChromaDB instances to a centralized Supabase (PostgreSQL) instance using the `pgvector` extension.

## Why Supabase?
1.  **Centralized Access**: A single source of truth for all coaches and users.
2.  **Hybrid Querying**: Seamlessly combine SQL filters (e.g., `WHERE match_id = '...'`) with semantic search.
3.  **Scalability**: Industry-standard Postgres performance with HNSW indexing for vectors.
4.  **Unified Schema**: Store user data, playbooks, and round embeddings in one database.

## Proposed Schema

### Table: `matches`
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | uuid | Primary Key |
| `external_id` | string | rib.gg / VLR ID |
| `event_name` | string | e.g., "VCT Champions 2025" |
| `team_a` | string | |
| `team_b` | string | |
| `map_name` | string | |
| `metadata` | jsonb | Raw JSON from scraper |

### Table: `round_embeddings`
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | uuid | Primary Key |
| `match_id` | uuid | Foreign Key to `matches` |
| `round_num` | int | |
| `summary` | text | Semantic description of the round |
| `embedding` | vector(768) | Matryoshka vector (Gemini) |
| `vod_url` | text | Precision timestamped link |
| `outcome` | string | win/loss |

## Migration Steps
1.  **Provisioning**: Enable `pgvector` on Supabase project.
2.  **Service Update**: Create `SupabaseService` in `backend/app/core/supabase.py`.
3.  **Dual-Write Phase**: Update `IngestionService` to write to both ChromaDB (local dev) and Supabase (prod).
4.  **Cutover**: Switch `/query` endpoint to pull from Supabase.
