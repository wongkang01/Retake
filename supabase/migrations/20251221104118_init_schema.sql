-- Enable the pgvector extension to work with embeddings
create extension if not exists vector;

-- Table for Match metadata
create table if not exists matches (
  id uuid primary key default gen_random_uuid(),
  external_id text unique not null,
  event_name text,
  team_a text,
  team_b text,
  team_a_slug text,
  team_b_slug text,
  map_name text,
  metadata jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Table for Round embeddings and tactical data
create table if not exists round_embeddings (
  id uuid primary key default gen_random_uuid(),
  external_id text unique not null,
  match_id uuid references matches(id) on delete cascade,
  match_id_rib text,
  round_num int,
  summary text,
  embedding vector(768),
  vod_url text,
  outcome text,
  winning_team text,
  winner_slug text,
  round_type text,
  is_pistol boolean,
  score_a int,
  score_b int,
  map_name text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create HNSW index for fast vector search
create index on round_embeddings using hnsw (embedding vector_cosine_ops);
