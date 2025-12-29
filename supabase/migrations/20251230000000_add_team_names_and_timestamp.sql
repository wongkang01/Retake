-- Add missing columns to round_embeddings for team names and VOD timestamp
alter table round_embeddings
add column if not exists team_a text,
add column if not exists team_b text,
add column if not exists vod_timestamp int;

-- Drop the old function first (required when changing return type)
drop function if exists match_rounds(vector(768), float, int, text, text, text, boolean);

-- Recreate the match_rounds function with new columns
create or replace function match_rounds (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  filter_team_slug text default null,
  filter_map_name text default null,
  filter_round_type text default null,
  filter_is_pistol boolean default null
) returns table (
  id uuid,
  external_id text,
  match_id_rib text,
  round_num int,
  summary text,
  vod_url text,
  winning_team text,
  winner_slug text,
  round_type text,
  is_pistol boolean,
  score_a int,
  score_b int,
  map_name text,
  team_a text,
  team_b text,
  vod_timestamp int,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    re.id,
    re.external_id,
    re.match_id_rib,
    re.round_num,
    re.summary,
    re.vod_url,
    re.winning_team,
    re.winner_slug,
    re.round_type,
    re.is_pistol,
    re.score_a,
    re.score_b,
    re.map_name,
    re.team_a,
    re.team_b,
    re.vod_timestamp,
    1 - (re.embedding <=> query_embedding) as similarity
  from round_embeddings re
  where
    (1 - (re.embedding <=> query_embedding) > match_threshold)
    and (filter_team_slug is null or re.winner_slug = filter_team_slug or re.team_a_slug = filter_team_slug or re.team_b_slug = filter_team_slug)
    and (filter_map_name is null or re.map_name = filter_map_name)
    and (filter_round_type is null or re.round_type = filter_round_type)
    and (filter_is_pistol is null or re.is_pistol = filter_is_pistol)
  order by re.embedding <=> query_embedding
  limit match_count;
end;
$$;
