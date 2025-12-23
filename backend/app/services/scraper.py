import httpx
import logging
import asyncio
import time
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from bs4 import BeautifulSoup
import json
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class ScraperService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScraperService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        self.force_browser_mode = False
        self.initialized = True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.RequestError)
    )
    async def fetch_page(self, url: str) -> str:
        """
        Fetches a page content using httpx with retries.
        Falls back to Playwright if 403 Forbidden is detected.
        """
        if self.force_browser_mode:
            logger.info(f"Browser mode enforced. Using Playwright for {url}")
            return await self._fetch_with_playwright(url)

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    logger.warning(f"403 Forbidden for {url}. Switching to Playwright mode.")
                    self.force_browser_mode = True
                    return await self._fetch_with_playwright(url)
                raise
            except httpx.RequestError as e:
                # Fallback to playwright on connection errors as well for robustness
                logger.warning(f"Request error for {url}: {e}. Trying Playwright.")
                return await self._fetch_with_playwright(url)

    async def _fetch_with_playwright(self, url: str) -> str:
        """
        Fetches page content using Playwright (Chromium).
        Handles dynamic rendering and bypasses simple bot detection.
        """
        logger.info(f"Fetching with Playwright: {url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.headers["User-Agent"])
            page = await context.new_page()
            
            try:
                # Use domcontentloaded for speed, then a small sleep for hydration
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3) # Wait for JS execution/hydration
                content = await page.content()
                return content
            except Exception as e:
                logger.error(f"Playwright failed for {url}: {e}")
                raise e
            finally:
                await browser.close()

    def extract_next_data(self, html_content: str) -> Dict[str, Any]:
        """
        Extracts the JSON data from the __NEXT_DATA__ script tag.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        
        if script_tag and script_tag.string:
            try:
                return json.loads(script_tag.string)
            except json.JSONDecodeError:
                logger.error("Failed to parse __NEXT_DATA__ JSON")
        
        return {}

# Global Accessor
def get_scraper_service() -> ScraperService:
    return ScraperService()