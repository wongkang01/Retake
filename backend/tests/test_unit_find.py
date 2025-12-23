import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.discovery import DiscoveryService
from app.services.ingestion import IngestionService
from app.services.processor import MatchDataProcessor

# --- MatchDataProcessor Tests ---

def test_processor_get_vod_start_time():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123s"
    assert MatchDataProcessor.get_vod_start_time(url) == 123

    url = "https://youtu.be/dQw4w9WgXcQ?t=60"
    assert MatchDataProcessor.get_vod_start_time(url) == 60

    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert MatchDataProcessor.get_vod_start_time(url) == 0

def test_processor_process_series_data_empty():
    assert MatchDataProcessor.process_series_data({}) == []
    assert MatchDataProcessor.process_series_data({"props": {"pageProps": {"series": None}}}) == []

def test_processor_process_series_data_valid():
    # Minimal mock of rib.gg data
    mock_series_data = {
        "props": {
            "pageProps": {
                "series": {
                    "team1": {"name": "Team A"},
                    "team2": {"name": "Team B"},
                    "stats": {
                        "kills": [
                            {"roundId": 101, "gameTimeMillis": 100000, "roundTimeMillis": 5000}, # Round started at 95000
                            {"roundId": 102, "gameTimeMillis": 200000, "roundTimeMillis": 10000} # Round started at 190000
                        ]
                    },
                    "matches": [
                        {
                            "id": 1,
                            "completed": True,
                            "map": {"name": "Ascent"},
                            "vodUrl": "https://youtu.be/video?t=100s",
                            "rounds": [
                                {
                                    "id": 101,
                                    "number": 1,
                                    "winningTeamNumber": 1,
                                    "winCondition": "elimination",
                                    "ceremony": "none"
                                },
                                {
                                    "id": 102,
                                    "number": 2,
                                    "winningTeamNumber": 2,
                                    "winCondition": "defuse",
                                    "ceremony": "flawless"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    rounds = MatchDataProcessor.process_series_data(mock_series_data)
    
    assert len(rounds) == 2
    
    # Check Round 1
    r1 = rounds[0]
    assert r1["round_num"] == 1
    assert r1["winning_team"] == "Team A"
    assert r1["vod_timestamp"] == 100 # First round anchors to VOD start time
    
    # Check Round 2
    r2 = rounds[1]
    assert r2["round_num"] == 2
    assert r2["winning_team"] == "Team B"
    # Round 1 started at 95000ms
    # Round 2 started at 190000ms
    # Diff = 95000ms = 95s
    # VOD Start = 100s
    # Expected = 195s
    assert r2["vod_timestamp"] == 195 


# --- IngestionService Tests ---

@patch("app.services.ingestion.get_chroma_service")
def test_ingest_batch(mock_get_chroma):
    # Mock Chroma Client and Collection
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.get_collection.return_value = mock_collection
    mock_get_chroma.return_value = mock_client

    service = IngestionService()
    
    rounds = [
        {"round_num": 1, "map_name": "Ascent", "winning_team": "Team A", "match_id": 123},
        {"round_num": 2, "map_name": "Ascent", "winning_team": "Team B", "match_id": 123}
    ]
    
    ids = service.ingest_batch(rounds)
    
    assert len(ids) == 2
    mock_collection.upsert.assert_called_once()
    
    # Verify upsert call structure
    call_args = mock_collection.upsert.call_args
    assert "ids" in call_args.kwargs
    assert "documents" in call_args.kwargs
    assert "metadatas" in call_args.kwargs
    assert len(call_args.kwargs["documents"]) == 2


# --- DiscoveryService Tests ---

@pytest.mark.asyncio
async def test_discover_matches_jit():
    with patch("app.services.discovery.get_scraper_service") as mock_get_scraper, \
         patch("app.services.ingestion.IngestionService") as mock_ingestion_cls:
         
        # Mock Scraper
        mock_scraper = MagicMock()
        mock_get_scraper.return_value = mock_scraper
        
        # Mock Ingestion Service
        mock_ingestion = MagicMock()
        mock_ingestion_cls.return_value = mock_ingestion

        # Mock Search Result
        mock_search_html = "<html>...</html>"
        mock_scraper.fetch_page = AsyncMock(return_value=mock_search_html)
        mock_scraper.extract_next_data.side_effect = [
            # 1. Search Result Data
            {
                "props": {
                    "pageProps": {
                        "results": {
                            "series": [{"id": 999}] 
                        }
                    }
                }
            },
                            # 2. Series Page Data (for process_series)
                            {
                                "props": {
                                    "pageProps": {
                                                                    "series": {
                                                                        "team1": {"name": "A"},
                                                                        "team2": {"name": "B"},
                                                                        "stats": {
                                                                            "kills": [
                                                                                {"roundId": 1, "gameTimeMillis": 1000, "roundTimeMillis": 0}
                                                                            ]
                                                                        },
                                                                        "matches": [
                                                                            {
                                                                                "id": 100,
                                        
                                                    "completed": True,
                                                    "map": {"name": "Ascent"},
                                                    "vodUrl": "http://vod.url",
                                                    "rounds": [
                                                        {"id": 1, "number": 1, "winningTeamNumber": 1, "winCondition": "elimination"}
                                                    ]
                                                }
                                            ] 
                                        }
                                    }
                                }
                            }
            
        ]

        service = DiscoveryService()
        results = await service.discover_matches("test query")
        
        # Verifications
        assert mock_scraper.fetch_page.call_count == 2 # 1 for search, 1 for series
        mock_ingestion.ingest_batch.assert_called() # Should verify ingestion was called
        
        # Verify URLs
        search_call = mock_scraper.fetch_page.call_args_list[0]
        assert "/search?query=test%20query" in search_call[0][0]
        
        series_call = mock_scraper.fetch_page.call_args_list[1]
        assert "/series/999" in series_call[0][0]

