# API Specification

## 1. Tactical Search (`POST /query`)
Primary endpoint for the **Find** module.

**Request:**
```json
{
  "question": "string",
  "top_k": 5,
  "filters": {
    "map": "Haven",
    "team": "Paper Rex",
    "round_type": "pistol",
    "timeframe": "last-90-days"
  },
  "stream": true
}
```

**Response (Chunk):**
```json
{ "text": "AI generated snippet..." }
```

## 2. Dynamic Ingestion (`POST /ingest`)
Triggers the Discovery and Scraper services.

**Request:**
```json
{
  "series_urls": ["string"],
  "auto_discover": true
}
```

## 3. Real-time Voice (`WS /ws/voice`)
WebSocket for ElevenLabs synthesis.
- **In**: Audio PCM chunks.
- **Out**: Transcription + Audio Stream (Eleven Turbo v2.5).

## 4. Metadata (`GET /series`)
Lists all currently indexed series and their round counts.
