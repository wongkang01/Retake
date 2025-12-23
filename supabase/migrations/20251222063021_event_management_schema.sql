-- 1. Create Events table
create table if not exists events (
  id uuid primary key default gen_random_uuid(),
  external_id text unique not null, -- rib.gg event ID
  name text not null,
  url text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Ensure matches table is linked to events
-- We add columns if they don't exist and establish relationships
alter table matches add column if not exists event_id uuid references events(id) on delete cascade;
alter table matches add column if not exists team_a_slug text;
alter table matches add column if not exists team_b_slug text;

-- 3. Ensure round_embeddings are linked correctly
alter table round_embeddings add column if not exists team_a_slug text;
alter table round_embeddings add column if not exists team_b_slug text;
