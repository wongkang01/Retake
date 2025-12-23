import asyncio
import os
from dotenv import load_dotenv
from app.services.ingestion import IngestionService

load_dotenv(dotenv_path="../.env")

async def test_cloud_write():
    print("--- TESTING SUPABASE CLOUD WRITE ---")
    service = IngestionService()
    
    dummy_round = {
        "round_num": 99,
        "map_name": "Ascent",
        "winning_team": "DEBUG_TEAM",
        "winner_slug": "debugteam",
        "match_id": "99999",
        "vod_url": "https://youtube.com",
        "vod_timestamp": 0,
        "score_a": 0,
        "score_b": 0,
        "round_type": "default",
        "is_pistol": False
    }
    
    try:
        ids = service.ingest_batch([dummy_round])
        print(f"✅ Successfully triggered dual-ingestion. IDs: {ids}")
    except Exception as e:
        print(f"❌ Cloud Write Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_cloud_write())
