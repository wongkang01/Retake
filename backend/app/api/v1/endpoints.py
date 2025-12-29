from fastapi import APIRouter, HTTPException, Depends, Security, Header
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging

from app.core.config import get_settings
from app.models.match import RawMatchData
from app.services.ingestion import IngestionService
from app.services.discovery import DiscoveryService
from app.core.db import get_chroma_service
from app.core.supabase import get_supabase
from app.services.processor import MatchDataProcessor

from google import genai
from google.genai import types

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    # Bypassing for development
    return True

# Models for Request/Response
class QueryRequest(BaseModel):
    query_text: str
    n_results: int = 5
    filters: Optional[Dict[str, Any]] = None
    jit_index: bool = False

class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    intent: Optional[Dict[str, Any]] = None

class IngestRequest(BaseModel):
    match_data: RawMatchData

class EventIngestRequest(BaseModel):
    event_url: str

class UrlIngestRequest(BaseModel):
    url: str

# Hardcoded map of common abbreviations to canonical slugs
TEAM_MAP = {
    "prx": "paperrex",
    "paper rex": "paperrex",
    "drx": "drx",
    "fnc": "fnatic",
    "fnatic": "fnatic",
    "nrg": "nrg",
    "sen": "sentinels",
    "sentinels": "sentinels",
    "th": "teamheretics",
    "heretics": "teamheretics",
    "lev": "leviatán",
    "leviatán": "leviatán",
    "loud": "loud",
    "tl": "teamliquid",
    "liquid": "teamliquid",
}

@router.post("/query", response_model=QueryResponse, dependencies=[Depends(get_api_key)])
async def query_matches(request: QueryRequest):
    settings = get_settings()
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    supabase = get_supabase()
    
    # 1. Hybrid Intent Detection (Keywords + LLM)
    detected_team_slug = None
    query_lower = request.query_text.lower()
    
    for kw, slug in TEAM_MAP.items():
        if kw in query_lower:
            detected_team_slug = slug
            break
            
    try:
        intent_prompt = (
            f"Given the Valorant search query: '{request.query_text}', extract: "
            "1. 'team_slug' (return 'paperrex', 'drx', 'fnatic', 'nrg', 'sentinels', 'teamheretics', 'leviatán', 'loud', 'teamliquid'). "
            "2. 'map' (ascent, bind, haven, lotus, sunset, abyss, split, fracture, icebox, breeze). "
            "3. 'round_type' (thrifty, flawless, pistol, clutch, ace). "
            "Return as JSON. Use null if not found."
        )
        
        intent_response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=intent_prompt,
            config=types.GenerateContentConfig(response_mime_type='application/json')
        )
        
        intent_data = json.loads(intent_response.text)
        if not detected_team_slug:
            detected_team_slug = intent_data.get("team_slug")
        
        detected_map = intent_data.get("map")
        detected_round_type = intent_data.get("round_type")

    except Exception as e:
        print(f"Intent parsing failed: {e}")
        detected_map = None
        detected_round_type = None

    # 2. Generate Vector for Query
    try:
        embed_resp = client.models.embed_content(
            model="models/text-embedding-004",
            contents=request.query_text,
            config={"task_type": "RETRIEVAL_QUERY"}
        )
        query_vector = embed_resp.embeddings[0].values
    except Exception as e:
        print(f"Embedding failed: {e}")
        query_vector = None

    # 3. Execute Search (Supabase Cloud Priority)
    formatted_results = []
    
    if supabase and query_vector:
        try:
            # Prepare RPC parameters - only include non-None values
            rpc_params = {
                "query_embedding": query_vector,
                "match_threshold": 0.5,
                "match_count": 20,
            }
            if detected_team_slug:
                rpc_params["filter_team_slug"] = detected_team_slug
            if detected_map:
                rpc_params["filter_map_name"] = detected_map.capitalize()
            if detected_round_type:
                rpc_params["filter_round_type"] = detected_round_type.lower()
            if detected_round_type == "pistol":
                rpc_params["filter_is_pistol"] = True

            rpc_res = supabase.rpc("match_rounds", rpc_params).execute()
            
            for row in rpc_res.data:
                formatted_results.append({
                    "id": row["external_id"],
                    "document": row["summary"],
                    "metadata": {
                        "team_a": row.get("team_a", "Unknown"), # Need to ensure these are in function return
                        "team_b": row.get("team_b", "Unknown"),
                        "score_a": row["score_a"],
                        "score_b": row["score_b"],
                        "map_name": row["map_name"],
                        "round_num": row["round_num"],
                        "winning_team": row["winning_team"],
                        "round_type": row["round_type"],
                        "vod_url": row["vod_url"],
                        "vod_timestamp": row.get("vod_timestamp") # Handled via metadata usually
                    },
                    "distance": 1 - row["similarity"] # Convert back to distance for UI consistency
                })
                
            logger.info(f"Supabase Cloud: Found {len(formatted_results)} results.")
            
        except Exception as e:
            logger.error(f"Supabase Search failed, falling back to Chroma: {e}")

    # 4. Fallback to ChromaDB if cloud search yielded nothing or failed
    if not formatted_results and settings.USE_CHROMA:
        try:
            chroma_service = get_chroma_service()
            collection = chroma_service.get_collection("matches")
            
            # (ChromaDB Filter Logic)
            filter_list = []
            if detected_team_slug:
                filter_list.append({"$or": [{"winner_slug": {"$eq": detected_team_slug}},{"team_a_slug": {"$eq": detected_team_slug}},{"team_b_slug": {"$eq": detected_team_slug}}]})
            if detected_map:
                filter_list.append({"map_name": {"$eq": detected_map.capitalize()}})
            
            final_filters = {"$and": filter_list} if len(filter_list) > 1 else (filter_list[0] if filter_list else None)

            results = collection.query(query_texts=[request.query_text], n_results=25, where=final_filters)
            
            seen_round_ids = set()
            for i in range(len(results['ids'][0])):
                meta = results['metadatas'][0][i]
                dist = results['distances'][0][i]
                if meta.get("round_id") in seen_round_ids: continue
                if dist <= 0.60:
                    seen_round_ids.add(meta.get("round_id"))
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": meta,
                        "distance": float(dist)
                    })
        except Exception as e:
            logger.warning(f"Local Chroma fallback failed: {e}")

    formatted_results.sort(key=lambda x: x["distance"])
            
    return {
        "results": formatted_results[:12],
        "intent": {
            "team": detected_team_slug,
            "map": detected_map,
            "round_type": detected_round_type
        }
    }

@router.post("/ingest", dependencies=[Depends(get_api_key)])
async def ingest_match(request: IngestRequest):
    ingestion_service = IngestionService()
    if request.match_data.raw_data:
        rounds = MatchDataProcessor.process_series_data(request.match_data.raw_data)
        if not rounds:
            raise HTTPException(status_code=422, detail="Failed to process raw match data")
        ids = ingestion_service.ingest_batch(rounds)
    else:
        rounds = [{"round_num": 1, "outcome": "win"}, {"round_num": 2, "outcome": "loss"}]
        metadata = {
            "match_id": request.match_data.match_id,
            "team_a": request.match_data.team_a,
            "team_b": request.match_data.team_b,
            "map_name": request.match_data.map_name
        }
        ids = ingestion_service.ingest_batch(rounds, metadata)
    return {"message": "Ingestion successful", "ingested_ids": ids}

@router.post("/ingest/url", dependencies=[Depends(get_api_key)])
async def ingest_from_url(request: UrlIngestRequest):
    discovery_service = DiscoveryService()
    rounds = await discovery_service.process_series(request.url)
    if not rounds:
        raise HTTPException(status_code=400, detail="Failed to scrape or process the provided URL")
    ingestion_service = IngestionService()
    ids = ingestion_service.ingest_batch(rounds)
    return {"message": f"Successfully ingested {len(ids)} rounds from URL", "ingested_ids": ids, "url": request.url}

@router.get("/events", dependencies=[Depends(get_api_key)])
async def list_events():
    """
    Returns a list of all ingested events in the library.
    """
    supabase = get_supabase()
    if not supabase:
        return []
    
    try:
        res = supabase.table("events").select("*").order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/ingest-event", dependencies=[Depends(get_api_key)])
async def ingest_event(request: EventIngestRequest):
    discovery_service = DiscoveryService()
    try:
        total_rounds = await discovery_service.ingest_tournament(request.event_url)
        return {
            "status": "success",
            "message": f"Successfully ingested {total_rounds} rounds from the tournament.",
            "url": request.event_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))