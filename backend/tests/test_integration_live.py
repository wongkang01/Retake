import httpx
import asyncio
import sys

# Configuration
API_URL = "http://localhost:8000/api/v1"
API_KEY = "dev_key"

async def test_api_health():
    print(f"Testing API Health at {API_URL}/health...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://localhost:8000/health")
            if resp.status_code == 200:
                print("✅ Health Check Passed")
            else:
                print(f"❌ Health Check Failed: {resp.status_code}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

async def test_query_endpoint():
    print(f"\nTesting Query Endpoint at {API_URL}/query...")
    headers = {"X-API-Key": API_KEY}
    payload = {
        "query_text": "pistol rounds",
        "n_results": 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_URL}/query", json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ Query Successful. Results found: {len(data.get('results', []))}")
            else:
                print(f"❌ Query Failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

async def main():
    print("=== STARTING INTEGRATION TEST ===")
    await test_api_health()
    await test_query_endpoint()
    print("=== END ===")

if __name__ == "__main__":
    asyncio.run(main())
