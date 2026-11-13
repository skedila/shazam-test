"""
Quick check that your RapidAPI key works with the Shazam API (by Api Dojo),
and a first look at what the chart, search, and details endpoints return.

Usage:
    python test_api.py                 # uses the US chart and a default search
    python test_api.py "bad bunny"     # custom search term

Every full response is saved to data/raw/ so you can open it and explore.
This script makes 4 API requests per run.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST", "shazam.p.rapidapi.com")
BASE_URL = f"https://{API_HOST}"
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}


def call(name, path, params=None):
    """Make one GET request, print a summary, save the JSON, and return it."""
    print(f"\n=== {name}: GET {path} {params or ''}")
    try:
        r = requests.get(BASE_URL + path, headers=HEADERS, params=params, timeout=30)
    except requests.RequestException as e:
        print(f"  Request failed: {e}")
        return None

    print(f"  Status: {r.status_code}")
    remaining = r.headers.get("x-ratelimit-requests-remaining")
    if remaining is not None:
        print(f"  Requests remaining this period: {remaining}")

    if r.status_code == 401 or r.status_code == 403:
        print("  Your key was rejected. Check that it's correct in .env and that")
        print("  you've subscribed to a plan on the API's Pricing tab.")
        return None
    if r.status_code == 429:
        print("  Rate limit or monthly quota reached.")
        return None

    try:
        data = r.json()
    except ValueError:
        print(f"  Response was not JSON: {r.text[:200]}")
        return None

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RAW_DIR / f"{name}_{stamp}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Saved full response to {out}")

    if r.status_code != 200:
        print(f"  Unexpected status. Response starts with: {str(data)[:200]}")
        return None
    return data


def find_strings(obj, prefix):
    """Recursively collect every string value starting with prefix."""
    found = []
    if isinstance(obj, dict):
        for v in obj.values():
            found += find_strings(v, prefix)
    elif isinstance(obj, list):
        for v in obj:
            found += find_strings(v, prefix)
    elif isinstance(obj, str) and obj.startswith(prefix):
        found.append(obj)
    return found


def main():
    if not API_KEY or API_KEY == "your_key_here":
        sys.exit("No API key found. Copy .env.example to .env and add your key.")

    search_term = sys.argv[1] if len(sys.argv) > 1 else "despacito"

    # 1. List every available chart (call this rarely; save the IDs).
    charts = call("charts_list", "/charts/list")
    chart_ids = find_strings(charts, "ip-country-chart") if charts else []
    if chart_ids:
        print(f"  Found {len(chart_ids)} country chart IDs, e.g. {chart_ids[:5]}")
    us_ids = [c for c in chart_ids if c.endswith("-US")]
    list_id = us_ids[0] if us_ids else "ip-country-chart-US"

    # 2. Pull the top songs from one country chart.
    chart = call("charts_track", "/charts/track",
                 {"listId": list_id, "pageSize": 20, "startFrom": 0})
    tracks = (chart or {}).get("tracks", [])
    for i, t in enumerate(tracks[:10], start=1):
        print(f"  {i:>2}. {t.get('title')} - {t.get('subtitle')} (key {t.get('key')})")
    if chart and not tracks:
        print("  No 'tracks' field found. Open the saved JSON to see the structure.")

    # 3. Search for a song by name.
    results = call("search", "/search", {"term": search_term, "limit": 5})
    hits = (results or {}).get("tracks", {}).get("hits", [])
    for h in hits:
        t = h.get("track", {})
        print(f"  - {t.get('title')} - {t.get('subtitle')} (key {t.get('key')})")

    # 4. Get details for the first track we found.
    track_id = tracks[0].get("key") if tracks else (
        hits[0].get("track", {}).get("key") if hits else None)
    if track_id:
        details = call("song_details", "/songs/v2/get-details", {"id": track_id})
        if details:
            print(f"  Top-level fields: {list(details.keys())}")
            has_lyrics = "lyrics" in json.dumps(details).lower()
            print(f"  Mentions lyrics anywhere: {has_lyrics}")
    else:
        print("\nSkipping details: no track ID found in chart or search results.")

    print("\nDone. Open the files in data/raw/ to explore the full responses.")


if __name__ == "__main__":
    main()
