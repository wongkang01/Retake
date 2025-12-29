import hashlib
import json
from typing import Dict, Any, List, Optional
import logging
from app.core.db import get_chroma_service
from app.core.supabase import get_supabase
from app.core.config import get_settings
from google import genai

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self):
        self.settings = get_settings()
        self.chroma = None
        self.collection = None

        if self.settings.USE_CHROMA:
            self.chroma = get_chroma_service()
            self.collection = self.chroma.get_collection("matches")
        else:
            logger.info("ChromaDB is disabled. Skipping local vector store initialization.")

        self.supabase = get_supabase()

        # Initialize Gemini client for embeddings
        self.gemini_client = None
        if self.settings.GEMINI_API_KEY:
            self.gemini_client = genai.Client(api_key=self.settings.GEMINI_API_KEY)

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector using Gemini."""
        if not self.gemini_client:
            return None
        try:
            result = self.gemini_client.models.embed_content(
                model="models/text-embedding-004",
                contents=text,
                config={"task_type": "RETRIEVAL_DOCUMENT"}
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def _generate_id(self, data: Dict[str, Any]) -> str:
        """Deterministic MD5 hash for idempotency."""
        content_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(content_str.encode('utf-8')).hexdigest()

    def ingest_batch(self, rounds: List[Dict[str, Any]], common_metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        if not rounds:
            return []

        # 1. Identify Match and Event context
        # We assume the first round contains the match-level metadata
        first_round = rounds[0]
        match_id_rib = str(first_round.get('match_id'))
        
        # 2. Supabase: Ensure Match exists in DB
        match_uuid = None
        if self.supabase:
            try:
                # Upsert Match
                match_data = {
                    "external_id": match_id_rib,
                    "event_id": common_metadata.get("event_id") if common_metadata else None,
                    "team_a": first_round.get("team_a"),
                    "team_b": first_round.get("team_b"),
                    "team_a_slug": first_round.get("team_a_slug"),
                    "team_b_slug": first_round.get("team_b_slug"),
                    "map_name": first_round.get("map_name"),
                }
                match_res = self.supabase.table("matches").upsert(match_data, on_conflict="external_id").execute()
                match_uuid = match_res.data[0]["id"]
                logger.info(f"Supabase: Ensured match record {match_id_rib}")
            except Exception as e:
                logger.error(f"Supabase Match Ingestion failed: {e}")

        # 3. Prepare data for Rounds
        ids, documents, metadatas = [], [], []
        supabase_rounds = []

        for r in rounds:
            # Semantic description
            round_num_text = f"round {r.get('round_num')}" if r.get('round_num') not in [1, 13] else "pistol round"
            win_cond = r.get('win_condition', 'unknown')
            round_type = r.get('round_type', 'default')
            type_note = f" This was a {round_type} round." if round_type != "default" else ""
            score_text = f"The score was {r.get('score_a')}-{r.get('score_b')}."
            
            doc_text = (
                f"On the map {r.get('map_name')} in match {r.get('match_id')}, "
                f"{score_text} {round_num_text.capitalize()} was won by {r.get('winning_team')} by {win_cond}. "
                f"{type_note} The VOD for this round starts at approximately {r.get('vod_timestamp')} seconds."
            )
            
            doc_id = self._generate_id(r)
            ids.append(doc_id)
            documents.append(doc_text)
            
            # clean metadata for Chroma
            cleaned_meta = {k: v for k, v in r.items() if isinstance(v, (str, int, float, bool))}
            metadatas.append(cleaned_meta)

            # Generate embedding for Supabase
            embedding = self._generate_embedding(doc_text)

            # Supabase Record
            supabase_record = {
                "external_id": doc_id,
                "match_id": match_uuid,
                "match_id_rib": match_id_rib,
                "round_num": r.get('round_num'),
                "summary": doc_text,
                "vod_url": r.get('vod_url'),
                "winning_team": r.get('winning_team'),
                "winner_slug": r.get('winner_slug'),
                "team_a_slug": r.get('team_a_slug'),
                "team_b_slug": r.get('team_b_slug'),
                "team_a": r.get('team_a'),
                "team_b": r.get('team_b'),
                "vod_timestamp": r.get('vod_timestamp'),
                "round_type": round_type,
                "is_pistol": r.get('is_pistol', False),
                "score_a": r.get('score_a'),
                "score_b": r.get('score_b'),
                "map_name": r.get('map_name')
            }
            if embedding:
                supabase_record["embedding"] = embedding
            supabase_rounds.append(supabase_record)

        # 4. Finalize Ingestion
        if self.collection:
            try:
                self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
                logger.info(f"Local ChromaDB: Ingested {len(ids)} rounds")
            except Exception as e:
                logger.error(f"Local Ingestion failed: {e}")

        if self.supabase and match_uuid:
            try:
                self.supabase.table("round_embeddings").upsert(supabase_rounds, on_conflict="external_id").execute()
                logger.info(f"Supabase: Ingested {len(supabase_rounds)} rounds linked to match {match_uuid}")
            except Exception as e:
                logger.error(f"Supabase Round Ingestion failed: {e}")
        
        return ids
