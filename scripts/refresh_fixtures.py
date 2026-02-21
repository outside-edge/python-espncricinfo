#!/usr/bin/env python
"""
Re-fetch fixture files from the live ESPN API.
Run: python scripts/refresh_fixtures.py
"""
import json
import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"
HEADERS = {"user-agent": "Mozilla/5.0"}

MATCH_ID = 857713      # CPL 2015 T20 (completed, non-dormant)
PLAYER_ID = 253802     # Virat Kohli


def save(name, data):
    path = FIXTURES / name
    with open(path, "w") as f:
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f, indent=2)
    print(f"Saved {path}")


def fetch_match():
    json_url = f"https://www.espncricinfo.com/matches/engine/match/{MATCH_ID}.json"
    html_url = f"https://www.espncricinfo.com/matches/engine/match/{MATCH_ID}.html"

    r = requests.get(json_url, headers=HEADERS)
    r.raise_for_status()
    save("match_857713.json", r.json())

    r = requests.get(html_url, headers=HEADERS)
    r.raise_for_status()
    # Save the raw HTML so we can replay get_html() and get_comms_json()
    save("match_857713.html", r.text)


def fetch_player():
    json_url = f"http://core.espnuk.org/v2/sports/cricket/athletes/{PLAYER_ID}"
    new_json_url = f"https://hs-consumer-api.espncricinfo.com/v1/pages/player/home?playerId={PLAYER_ID}"
    html_url = f"https://www.espncricinfo.com/player/player-name-{PLAYER_ID}"

    r = requests.get(json_url, headers=HEADERS)
    r.raise_for_status()
    save("player_253802.json", r.json())

    r = requests.get(new_json_url, headers=HEADERS)
    r.raise_for_status()
    save("player_253802_new.json", r.json())

    r = requests.get(html_url, headers=HEADERS)
    r.raise_for_status()
    save("player_253802.html", r.text)


if __name__ == "__main__":
    FIXTURES.mkdir(exist_ok=True)
    print("Fetching match fixtures...")
    fetch_match()
    print("Fetching player fixtures...")
    fetch_player()
    print("Done.")
