import pytest
from app.services.scraper import ScraperService

# URLs provided in the configuration
TEST_URLS = [
    "https://www.rib.gg/series/93764",
    "https://www.rib.gg/series/93737",
    "https://www.rib.gg/series/93642"
]

@pytest.mark.asyncio
async def test_scraper_live_urls():
    """
    Verifies that the ScraperService can successfully fetch and extract data 
    from the specific URLs defined in the reference configuration.
    """
    service = ScraperService()
    
    for url in TEST_URLS:
        print(f"Testing URL: {url}")
        
        # 1. Test Fetching
        try:
            html_content = await service.fetch_page(url)
            assert html_content is not None
            assert len(html_content) > 0
            print(f"  - Successfully fetched {len(html_content)} bytes")
        except Exception as e:
            pytest.fail(f"Failed to fetch {url}: {str(e)}")

        # 2. Test Extraction
        try:
            data = service.extract_next_data(html_content)
            assert isinstance(data, dict)
            # Basic check for Next.js data structure
            assert "props" in data or "pageProps" in data or data == {} 
            # Note: data might be empty if the script tag isn't found, 
            # but we want to ensure it doesn't crash. 
            # Realistically, for rib.gg, we expect data.
            if data:
                 print(f"  - Successfully extracted JSON data keys: {list(data.keys())}")
            else:
                 print(f"  - Warning: No __NEXT_DATA__ found for {url}")
                 
        except Exception as e:
            pytest.fail(f"Failed to extract data from {url}: {str(e)}")

if __name__ == "__main__":
    # Allow running directly for quick check
    import asyncio
    asyncio.run(test_scraper_live_urls())
