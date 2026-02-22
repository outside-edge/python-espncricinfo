#!/usr/bin/env python
"""
Re-fetch fixture files from the live ESPN Cricinfo site.

ESPN's API endpoints (matches/engine, hs-consumer-api) are blocked by Akamai
for scripted requests. We use Playwright (WebKit) to load match pages and extract
the __NEXT_DATA__ JSON embedded by Next.js.

Usage:
    uv run python scripts/refresh_fixtures.py

Requirements:
    uv add --dev playwright
    uv run playwright install webkit
"""
import asyncio
import json
import re
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"

# AUS Women vs IND Women 3rd T20I 2025-26 — completed match with full scorecard
MATCH_ID = 1478914
SERIES_ID = 1478874

# Virat Kohli — core.espnuk.org still works for player JSON
PLAYER_ID = 253802


def save(name, data):
    path = FIXTURES / name
    with open(path, "w") as f:
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f, indent=2)
    print(f"  Saved {path} ({path.stat().st_size:,} bytes)")


async def _playwright_fetch_next_data(url):
    """Fetch a page via Playwright WebKit and extract __NEXT_DATA__."""
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.webkit.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/16.0 Safari/605.1.15"
            ),
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"  Navigation note: {e}")
        content = await page.content()
        await browser.close()

    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', content, re.DOTALL)
    if not m:
        raise RuntimeError(f"No __NEXT_DATA__ found at {url}")
    return json.loads(m.group(1))


def fetch_match():
    url = f"https://www.espncricinfo.com/series/x-{SERIES_ID}/x-{MATCH_ID}/full-scorecard"
    print(f"  Fetching: {url}")
    next_data = asyncio.run(_playwright_fetch_next_data(url))

    # Save the full __NEXT_DATA__ for reference
    save(f"match_{MATCH_ID}_next_data.json", next_data)

    # Navigate to inner data
    app_data = next_data["props"]["appPageProps"]["data"]
    if "match" in app_data and "content" in app_data:
        data = app_data
    else:
        data = app_data["data"]

    # Save match object
    if "match" in data:
        save(f"match_{MATCH_ID}_match.json", data["match"])

    # Save content sub-objects
    content = data.get("content", {})
    if "innings" in content:
        save(f"match_{MATCH_ID}_innings.json", content["innings"])
    if "matchPlayers" in content:
        save(f"match_{MATCH_ID}_players.json", content["matchPlayers"])


def fetch_player():
    import requests
    headers = {"user-agent": "Mozilla/5.0"}

    # core.espnuk.org still works
    url = f"http://core.espnuk.org/v2/sports/cricket/athletes/{PLAYER_ID}"
    print(f"  Fetching: {url}")
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    save(f"player_{PLAYER_ID}.json", r.json())

    # hs-consumer-api is Akamai-blocked — keep synthetic fixture
    new_path = FIXTURES / f"player_{PLAYER_ID}_new.json"
    if not new_path.exists():
        synthetic = {
            "content": {
                "teams": [
                    {"team": {"longName": "India"}},
                    {"team": {"longName": "Royal Challengers Bangalore"}},
                ]
            }
        }
        save(f"player_{PLAYER_ID}_new.json", synthetic)
        print("  (created synthetic player_new.json — hs-consumer-api is blocked)")
    else:
        print(f"  (keeping existing {new_path.name})")


if __name__ == "__main__":
    FIXTURES.mkdir(exist_ok=True)
    print("Fetching match fixtures via Playwright (WebKit)...")
    fetch_match()
    print("Fetching player fixtures...")
    fetch_player()
    print("Done.")
