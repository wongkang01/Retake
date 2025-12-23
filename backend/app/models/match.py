from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RawMatchData(BaseModel):
    """
    Standardized model for match data extracted from rib.gg/VLR.gg.
    Designed to capture the raw structure before semantic processing.
    """
    match_id: str
    series_id: Optional[str] = None
    tournament_id: Optional[str] = None
    
    team_a: str
    team_b: str
    winner: Optional[str] = None
    
    map_name: str
    score_a: int
    score_b: int
    
    start_time: datetime
    
    # Raw JSON dump from __NEXT_DATA__ or similar script tags
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    source_url: HttpUrl
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ScrapedSeries(BaseModel):
    series_id: str
    title: str
    matches: List[str] # List of match URLs or IDs
    timestamp: datetime
