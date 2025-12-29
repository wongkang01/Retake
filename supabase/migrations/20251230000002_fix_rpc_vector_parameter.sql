-- Fix RPC vector parameter handling for PostgREST compatibility
-- PostgREST handles float[] (JSON array) better than vector type directly

-- Drop existing function variants
DROP FUNCTION IF EXISTS match_rounds(vector(768), float, int, text, text, text, boolean);
DROP FUNCTION IF EXISTS match_rounds(float[], float, int, text, text, text, boolean);
DROP FUNCTION IF EXISTS match_rounds(double precision[], double precision, int, text, text, text, boolean);

-- Recreate the match_rounds function with float[] parameter for PostgREST compatibility
CREATE FUNCTION match_rounds (
  query_embedding float[],
  match_threshold float,
  match_count int,
  filter_team_slug text default null,
  filter_map_name text default null,
  filter_round_type text default null,
  filter_is_pistol boolean default null
) RETURNS TABLE (
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
LANGUAGE plpgsql
AS $$
DECLARE
  query_vec vector(768);
BEGIN
  -- Cast the float array to vector inside the function
  query_vec := query_embedding::vector(768);

  RETURN QUERY
  SELECT
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
    1 - (re.embedding <=> query_vec) as similarity
  FROM round_embeddings re
  WHERE
    (1 - (re.embedding <=> query_vec) > match_threshold)
    AND (filter_team_slug IS NULL OR re.winner_slug = filter_team_slug OR re.team_a_slug = filter_team_slug OR re.team_b_slug = filter_team_slug)
    AND (filter_map_name IS NULL OR re.map_name = filter_map_name)
    AND (filter_round_type IS NULL OR re.round_type = filter_round_type)
    AND (filter_is_pistol IS NULL OR re.is_pistol = filter_is_pistol)
  ORDER BY re.embedding <=> query_vec
  LIMIT match_count;
END;
$$;
