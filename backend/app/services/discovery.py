import logging
import json
import asyncio
from typing import List, Optional, Dict, Any
from google import genai
from google.genai import types
from urllib.parse import quote
import re

from app.core.config import get_settings
from app.services.scraper import get_scraper_service
from app.services.processor import MatchDataProcessor

logger = logging.getLogger(__name__)
settings = get_settings()

class DiscoveryService:
    def __init__(self):
        self.scraper = get_scraper_service()
        self.base_url = "https://rib.gg"
        
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            logger.warning("GEMINI_API_KEY not set. Discovery Service will fail.")
            self.client = None

    async def discover_matches(self, query: str) -> List[Dict[str, Any]]:
        """
        Uses Gemini Agent with Google Search to discover match URLs, then scrapes them.
        """
        if not self.client:
            logger.error("Cannot discover matches: No API Key.")
            return []

        from app.services.ingestion import IngestionService
        
        logger.info(f"Agentic Discovery for query: {query}")
        
        try:
            # 1. Agent Search Step
            prompt = (
                f"Search for the Valorant match/series URLs on 'rib.gg' that match this user request: '{query}'. "
                "Focus on finding the main Series page URLs (e.g., https://rib.gg/series/...). "
                "Return the result as a JSON object with a single key 'urls' which is a list of strings."
            )
            
            logger.info(f"Sending prompt to Agent: {prompt}")

            response = await self.client.aio.models.generate_content(
                model='gemini-3-flash-preview', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    response_mime_type='application/json'
                )
            )
            
            if not response.text:
                logger.warning("Agent returned no text.")
                return []
            
            logger.info(f"Agent Raw Response: {response.text}")
                
            try:
                result_json = json.loads(response.text)
                urls = result_json.get("urls", [])
                logger.info(f"Agent found {len(urls)} URLs: {urls}")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse Agent JSON: {response.text}")
                return []

            if not urls:
                return []

            # 3. Ingestion Step
            discovered_rounds = []
            ingestion_service = IngestionService()
            
            for url in urls[:3]:
                if "rib.gg/series/" not in url:
                    logger.warning(f"Skipping invalid URL: {url}")
                    continue
                    
                logger.info(f"JIT Ingesting discovered series: {url}")
                rounds = await self.process_series(url)
                
                if rounds:
                    ingestion_service.ingest_batch(rounds)
                    discovered_rounds.extend(rounds)
            
            return discovered_rounds
            
        except Exception as e:
            logger.error(f"Error during agentic discovery: {e}")
            return []

    async def process_series(self, series_url: str) -> List[Dict[str, Any]]:
        """
        Fetches and processes a specific series URL.
        """
        try:
            html = await self.scraper.fetch_page(series_url)
            raw_data = self.scraper.extract_next_data(html)
            
            if raw_data:
                processed_rounds = MatchDataProcessor.process_series_data(raw_data)
                logger.info(f"Processed {len(processed_rounds)} rounds from {series_url}")
                return processed_rounds
            
            return []
        except Exception as e:
            logger.error(f"Error processing series {series_url}: {e}")
            return []

    async def crawl_tournament(self, event_url: str) -> List[str]:
        """
        Crawls a rib.gg event page to find all series links.
        Recursively checks child events (e.g. Group Stage, Playoffs).
        Ensures only unique canonical Series URLs are returned.
        """
        logger.info(f"Crawling tournament: {event_url}")
        unique_series_ids = set()
        
        try:
            # Force browser mode for discovery to ensure we see all dynamic links
            html = await self.scraper._fetch_with_playwright(event_url)
            data = self.scraper.extract_next_data(html)
            
            props = data.get("props", {}).get("pageProps", {})
            event_data = props.get("event", {})
            
            # 1. Look for direct series in this event (JSON Data)
            for key in ["series", "allSeries", "results"]:
                items = event_data.get(key, [])
                for item in items:
                    if isinstance(item, dict) and "id" in item:
                        unique_series_ids.add(str(item['id']))

            # 2. Check for child events and crawl them recursively
            child_events = event_data.get("childEvents", [])
            for child in child_events:
                child_id = child.get("id")
                if child_id:
                    child_url = f"{self.base_url}/events/_/{child_id}"
                    logger.info(f"Found child event {child_id}, crawling...")
                    child_links = await self.crawl_tournament(child_url)
                    for link in child_links:
                        match_id = link.split("/")[-1]
                        unique_series_ids.add(match_id)
            
            # 3. Fallback: Parse DOM for any /series/ links missed in JSON
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                match = re.search(r"/series/.*?(\d+)$", href)
                if match:
                    unique_series_ids.add(match.group(1))

            canonical_urls = [f"{self.base_url}/series/{sid}" for sid in unique_series_ids]
            return canonical_urls
            
        except Exception as e:
            logger.error(f"Failed to crawl tournament {event_url}: {e}")
            return [f"{self.base_url}/series/{sid}" for sid in unique_series_ids]

    async def ingest_tournament(self, event_url: str):
        """
        Crawls a tournament and ingests ALL matches found.
        """
        from app.services.ingestion import IngestionService
        from app.core.supabase import get_supabase
        
        # 1. Register the Event in Supabase
        event_uuid = None
        supabase = get_supabase()
        if supabase:
            try:
                ext_id = event_url.rstrip("/").split("/")[-1]
                name_slug = event_url.split("/events/")[-1].split("/")[0].replace("-", " ").title()
                
                event_data = {
                    "external_id": ext_id,
                    "name": name_slug,
                    "url": event_url
                }
                event_res = supabase.table("events").upsert(event_data, on_conflict="external_id").execute()
                event_uuid = event_res.data[0]["id"]
                logger.info(f"Supabase: Registered event {name_slug} ({event_uuid})")
            except Exception as e:
                logger.error(f"Event registration failed: {e}")

        # 2. Crawl and Process Matches
        urls = await self.crawl_tournament(event_url)
        logger.info(f"Tournament crawler found {len(urls)} series. Starting bulk ingestion...")
        
        ingestion_service = IngestionService()
        total_rounds = 0
        
        for url in urls:
            rounds = await self.process_series(url)
            if rounds:
                ingestion_service.ingest_batch(rounds, common_metadata={"event_id": event_uuid})
                total_rounds += len(rounds)
        
        logger.info(f"Bulk ingestion complete. Ingested {total_rounds} rounds from {len(urls)} series.")
        return total_rounds