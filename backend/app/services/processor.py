import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class MatchDataProcessor:
    """
    Process scraped match data into structured round data with VOD timestamps.
    Ported from legacy MatchDataProcessor.
    """
    
    @staticmethod
    def get_vod_start_time(vod_url: str) -> int:
        """Parse YouTube URL to find the start time in seconds."""
        if not vod_url:
            return 0
        try:
            # Handle standard youtube urls and short urls if needed, though simple query parsing covers most
            query = urlparse(vod_url).query
            params = parse_qs(query)
            # t param usually looks like '123s' or '123'
            t_val = params.get('t', ['0'])[0]
            return int(t_val.replace('s', ''))
        except (ValueError, IndexError):
            return 0
    
    @classmethod
    def process_series_data(cls, series_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert scraped series data into a list of round dictionaries ready for ingestion.
        
        Args:
            series_data: Raw series data from rib.gg (extracted from __NEXT_DATA__)
            
        Returns:
            List of dictionaries, each representing a round with metadata and VOD link.
        """
        try:
            # Navigate the specific rib.gg structure
            # Structure usually: props.pageProps.series
            if 'props' in series_data:
                series_info = series_data.get('props', {}).get('pageProps', {}).get('series', {})
            else:
                # If the data passed is already the 'series' object or flattened
                series_info = series_data

            if not series_info:
                logger.warning("No series info found in data")
                return []

            team1 = series_info.get('team1', {})
            team2 = series_info.get('team2', {})
            team1_name = team1.get('name', 'Team 1')
            team2_name = team2.get('name', 'Team 2')
            
            # Calculate round start times from kills data
            # roundId -> gameTimeMillis (start of round approx)
            round_start_gametimes = {}
            # Stats are usually at the series level in rib.gg JSON for the whole series? 
            # Or per match? Legacy code accessed series_info['stats']['kills'].
            # Let's check the legacy code access pattern: series_info['stats'].get('kills', [])
            
            kills = series_info.get('stats', {}).get('kills', [])
            for kill in kills:
                round_id = kill.get('roundId')
                if round_id not in round_start_gametimes:
                    # roundTimeMillis is time *into* the round the kill happened
                    # gameTimeMillis is time *into* the game the kill happened
                    # start = game - round
                    start_time = kill.get('gameTimeMillis', 0) - kill.get('roundTimeMillis', 0)
                    round_start_gametimes[round_id] = start_time
            
            processed_rounds = []
            
            for match in series_info.get('matches', []):
                if not match.get('completed'):
                    continue
                    
                map_name = match.get('map', {}).get('name', 'Unknown Map')
                match_id = match.get('id')
                map_vod_url = match.get('vodUrl')
                
                # Tracking running score for this match
                running_score_a = 0
                running_score_b = 0
                
                vod_start_sec = cls.get_vod_start_time(map_vod_url)
                
                # Cleanup base URL (strip existing timestamps)
                base_vod_url = map_vod_url
                if base_vod_url:
                    for p in ['?t=', '&t=', '?start=', '&start=']:
                        if p in base_vod_url:
                            base_vod_url = base_vod_url.split(p)[0]
                
                # Sort rounds by number to ensure order
                sorted_rounds = sorted(match.get('rounds', []), key=lambda r: r.get('number', 0))
                
                if not sorted_rounds:
                    continue

                first_round_id = sorted_rounds[0]['id']
                first_round_gametime = round_start_gametimes.get(first_round_id, 0)
                
                for round_info in sorted_rounds:
                    round_number = round_info.get('number')
                    round_id = round_info.get('id')
                    winner_num = round_info.get('winningTeamNumber')
                    
                    if not all([round_number, winner_num, round_id]):
                        continue
                        
                    current_round_gametime = round_start_gametimes.get(round_id, 0)
                    if current_round_gametime == 0:
                        continue

                    offset_ms = current_round_gametime - first_round_gametime
                    round_vod_timestamp_sec = vod_start_sec + (offset_ms / 1000)
                    
                    # Construct specific VOD URL
                    round_vod_url = f"{base_vod_url}&t={int(round_vod_timestamp_sec)}s" if base_vod_url else None
                    winner_name = team1_name if winner_num == 1 else team2_name
                    
                    # Metadata construction
                    # Use the score BEFORE incrementing it to show score at START of round
                    
                    # Unified Round Type logic (Direct from source)
                    ceremony = round_info.get('ceremony', 'default').lower()
                    win_condition = round_info.get('winCondition', 'unknown')
                    round_num = int(round_number)
                    is_pistol = round_num == 1 or round_num == 13

                    # Helper to create consistent slugs for filtering
                    def to_slug(name):
                        return name.lower().replace(" ", "").replace("esports", "").replace(".", "")

                    round_data = {
                        "match_id": match_id,
                        "round_id": round_id,
                        "map_name": map_name,
                        "round_num": round_num,
                        "is_pistol": is_pistol,
                        "winning_team": winner_name,
                        "winner_slug": to_slug(winner_name),
                        "team_a": team1_name,
                        "team_a_slug": to_slug(team1_name),
                        "team_b": team2_name,
                        "team_b_slug": to_slug(team2_name),
                        "score_a": running_score_a,
                        "score_b": running_score_b,
                        "vod_url": round_vod_url,
                        "vod_timestamp": int(round_vod_timestamp_sec),
                        "win_condition": win_condition,
                        "round_type": ceremony,
                    }
                    
                    processed_rounds.append(round_data)

                    # Update running score for the NEXT round
                    if winner_num == 1:
                        running_score_a += 1
                    else:
                        running_score_b += 1
                    
            return processed_rounds
            
        except Exception as e:
            logger.error(f"Failed to process series data: {e}")
            return []
