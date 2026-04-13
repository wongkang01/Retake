"""Scraper for VLR.gg match VOD data.

Extracts per-map YouTube VOD URLs + start offsets from VLR.gg match pages.
Used by the ingestion pipeline to enrich rounds with VOD links when rib.gg
has no VOD data, and by the backfill script for already-ingested tournaments.
"""
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

from app.services.scraper import get_scraper_service

logger = logging.getLogger(__name__)


def extract_youtube_info(url: str) -> Optional[Tuple[str, int]]:
    """Extract (video_id, start_seconds) from a YouTube URL.

    Handles youtu.be/VIDEO_ID?t=123 and youtube.com/watch?v=VIDEO_ID&t=123s.
    Returns None for non-YouTube or malformed URLs.
    """
    parsed = urlparse(url)
    if not parsed.hostname:
        return None

    if "youtu.be" in parsed.hostname:
        video_id = parsed.path.lstrip("/")
        t_str = parse_qs(parsed.query).get("t", ["0"])[0]
        return video_id, int(str(t_str).replace("s", ""))

    if "youtube.com" in parsed.hostname:
        qs = parse_qs(parsed.query)
        video_id = qs.get("v", [None])[0]
        if not video_id:
            return None
        t_str = qs.get("t", ["0"])[0]
        return video_id, int(str(t_str).replace("s", ""))

    return None


async def fetch_event_matches(event_url: str) -> List[Dict[str, Any]]:
    """Fetch all match entries from a VLR.gg event page.

    Returns list of dicts: {vlr_match_id, vlr_match_url, team_a, team_b, score, date}
    """
    scraper = get_scraper_service()
    html = await scraper.fetch_page(event_url)
    soup = BeautifulSoup(html, "html.parser")
    matches = []

    for a in soup.select("a.match-item, a.wf-module-item"):
        href = a.get("href", "")
        match_id_match = re.match(r"^/(\d+)/", href)
        if not match_id_match:
            continue

        vlr_id = match_id_match.group(1)
        teams = a.select(".match-item-vs-team-name, .text-of")
        team_names = [t.get_text(strip=True) for t in teams]

        score_el = a.select(".match-item-vs-team-score, .score")
        scores = [s.get_text(strip=True) for s in score_el]

        date_el = a.select_one(".match-item-date")
        date_str = date_el.get_text(strip=True) if date_el else ""

        matches.append({
            "vlr_match_id": vlr_id,
            "vlr_match_url": f"https://www.vlr.gg{href}",
            "team_a": team_names[0] if len(team_names) > 0 else "",
            "team_b": team_names[1] if len(team_names) > 1 else "",
            "score": f"{scores[0]}-{scores[1]}" if len(scores) >= 2 else "",
            "date": date_str,
        })

    logger.info(f"VLR: Found {len(matches)} matches on event page")
    return matches


async def fetch_match_vods(match_url: str) -> Dict[str, Any]:
    """Fetch per-map VOD data from a VLR.gg match page.

    Returns dict: {team_a, team_b, maps: [{map_name, map_index, youtube_video_id, start_seconds}]}
    """
    scraper = get_scraper_service()
    html = await scraper.fetch_page(match_url)
    soup = BeautifulSoup(html, "html.parser")

    team_els = soup.select(".match-header-link-name .wf-title-med")
    team_a = team_els[0].get_text(strip=True) if len(team_els) > 0 else ""
    team_b = team_els[1].get_text(strip=True) if len(team_els) > 1 else ""

    map_names = []
    for el in soup.select(".vm-stats-game-header .map span, .map-name-indicator"):
        name = el.get_text(strip=True)
        if not name or name.isdigit():
            continue
        name = re.sub(r'\s*(PICK|BAN|DECIDER)\s*$', '', name).strip()
        if name:
            map_names.append(name)

    youtube_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "youtu" in href:
            info = extract_youtube_info(href)
            if info:
                youtube_links.append(info)

    # Deduplicate and sort by start time
    unique_links = sorted(dict.fromkeys(youtube_links), key=lambda x: x[1])

    maps = []
    for i, (vid, start) in enumerate(unique_links):
        map_name = map_names[i] if i < len(map_names) else f"Map {i+1}"
        maps.append({
            "map_index": i,
            "map_name": map_name,
            "youtube_video_id": vid,
            "start_seconds": start,
        })

    logger.info(f"VLR: {team_a} vs {team_b} — {len(maps)} map VODs found")
    return {"team_a": team_a, "team_b": team_b, "maps": maps}
