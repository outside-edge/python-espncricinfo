# Robust Test Suite Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the 3-test live-only test suite with a comprehensive hybrid test suite using JSON fixtures for unit tests and optional live integration tests.

**Architecture:** Unit tests live in `tests/` and use `unittest.mock.patch` to intercept all `requests.get` calls, feeding in pre-recorded JSON fixtures. Integration tests in the same files are decorated with `@pytest.mark.integration` and skipped unless `pytest --live` is passed. A `scripts/refresh_fixtures.py` script re-fetches fixtures from the live API.

**Tech Stack:** Python 3.12, pytest 9, unittest.mock, requests, BeautifulSoup4, JSON fixture files

---

### Task 1: Scaffold the test directory and pytest config

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `pytest.ini`

**Step 1: Create `tests/__init__.py`** (empty)

```python
```

**Step 2: Create `tests/conftest.py`**

```python
import json
import os
import pytest
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name):
    with open(FIXTURE_DIR / name) as f:
        return json.load(f)


def load_fixture_text(name):
    with open(FIXTURE_DIR / name) as f:
        return f.read()


def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run integration tests against live ESPN API",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as requiring live ESPN API (run with --live)"
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--live"):
        skip_live = pytest.mark.skip(reason="Pass --live to run integration tests")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_live)
```

**Step 3: Create `pytest.ini`**

```ini
[pytest]
testpaths = tests
markers =
    integration: mark test as requiring live ESPN API (run with --live)
```

**Step 4: Run pytest to verify config loads**

Run: `cd /Users/dwillis/code/python-espncricinfo && pytest --collect-only`
Expected: "no tests ran" or "0 tests collected" — no errors

**Step 5: Commit**

```bash
git add tests/__init__.py tests/conftest.py pytest.ini
git commit -m "test: scaffold tests/ directory with pytest config and --live flag"
```

---

### Task 2: Record fixture files from live API

**Files:**
- Create: `scripts/refresh_fixtures.py`
- Create: `tests/fixtures/` (directory + JSON files)

**Step 1: Create `tests/fixtures/` directory**

```bash
mkdir -p tests/fixtures
```

**Step 2: Create `scripts/refresh_fixtures.py`**

```python
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
```

**Step 3: Run the script to record fixtures**

Run: `cd /Users/dwillis/code/python-espncricinfo && python scripts/refresh_fixtures.py`
Expected: Prints "Saved tests/fixtures/..." for each file. If ESPN returns errors, note which endpoints are down — that itself is useful signal.

**Step 4: Verify fixture files exist**

Run: `ls tests/fixtures/`
Expected: `match_857713.json`, `match_857713.html`, `player_253802.json`, `player_253802_new.json`, `player_253802.html`

**Step 5: Commit**

```bash
git add scripts/refresh_fixtures.py tests/fixtures/
git commit -m "test: add fixture recording script and initial fixture files"
```

---

### Task 3: Write `test_match.py` — unit tests (mocked)

**Files:**
- Create: `tests/test_match.py`

**Context:** `Match.__init__` calls `self.get_json()`, `self.get_html()`, and `self.get_comms_json()`. We patch `requests.get` to return mock responses. `get_html()` uses `BeautifulSoup(r.text, 'html.parser')`. `get_comms_json()` does `self.html.find_all('script')[15].string` — if fixtures don't have a 16th script tag with valid JSON, `comms_json` will be `None`, which is fine (the `try/except` handles it).

**Step 1: Write `tests/test_match.py`**

```python
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from espncricinfo.exceptions import MatchNotFoundError, NoScorecardError
from espncricinfo.match import Match

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _mock_response(json_data=None, text=None, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
        mock.text = json.dumps(json_data)
    elif text is not None:
        mock.text = text
        mock.json.side_effect = ValueError("No JSON")
    else:
        mock.text = ""
        mock.json.side_effect = ValueError("No JSON")
    return mock


def _load_fixture(name):
    with open(FIXTURE_DIR / name) as f:
        if name.endswith(".json"):
            return json.load(f)
        return f.read()


def _make_match(match_id=857713):
    """Construct a Match using fixture data, with requests.get patched."""
    json_data = _load_fixture("match_857713.json")
    html_text = _load_fixture("match_857713.html")

    def side_effect(url, headers=None):
        if url.endswith(".json"):
            return _mock_response(json_data=json_data)
        else:
            return _mock_response(text=html_text)

    with patch("espncricinfo.match.requests.get", side_effect=side_effect):
        return Match(match_id)


class TestMatchAttributes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.match = _make_match()

    # --- identity ---

    def test_str(self):
        self.assertIsInstance(str(self.match), str)
        self.assertGreater(len(str(self.match)), 0)

    def test_repr(self):
        self.assertIn("Match", repr(self.match))
        self.assertIn("857713", repr(self.match))

    def test_match_id(self):
        self.assertEqual(self.match.match_id, 857713)

    # --- description / meta ---

    def test_description_is_string(self):
        self.assertIsInstance(self.match.description, str)
        self.assertGreater(len(self.match.description), 0)

    def test_match_class_is_string(self):
        self.assertIsInstance(self.match.match_class, str)

    def test_season_is_string(self):
        self.assertIsInstance(self.match.season, str)

    def test_status_is_string(self):
        self.assertIsInstance(self.match.status, str)

    def test_date_is_string(self):
        self.assertIsInstance(self.match.date, str)

    def test_result_is_string(self):
        self.assertIsInstance(self.match.result, str)

    def test_series_name_is_string_or_none(self):
        self.assertTrue(
            self.match.series_name is None or isinstance(self.match.series_name, str)
        )

    def test_series_id_is_set(self):
        self.assertIsNotNone(self.match.series_id)

    # --- ground / location ---

    def test_ground_id_is_set(self):
        self.assertIsNotNone(self.match.ground_id)

    def test_ground_name_is_string(self):
        self.assertIsInstance(self.match.ground_name, str)

    def test_continent_is_string_or_none(self):
        self.assertTrue(
            self.match.continent is None or isinstance(self.match.continent, str)
        )

    def test_town_name_is_string_or_none(self):
        self.assertTrue(
            self.match.town_name is None or isinstance(self.match.town_name, str)
        )

    # --- boolean flags ---

    def test_cancelled_match_is_bool(self):
        self.assertIsInstance(self.match.cancelled_match, bool)

    def test_followon_is_bool(self):
        self.assertIsInstance(self.match.followon, bool)

    def test_rain_rule_is_string_or_none(self):
        self.assertTrue(
            self.match.rain_rule is None or isinstance(self.match.rain_rule, str)
        )

    def test_scheduled_overs_is_int_or_none(self):
        self.assertTrue(
            self.match.scheduled_overs is None
            or isinstance(self.match.scheduled_overs, int)
        )

    # --- teams ---

    def test_team_1_is_dict(self):
        self.assertIsInstance(self.match.team_1, dict)

    def test_team_1_id_is_set(self):
        self.assertIsNotNone(self.match.team_1_id)

    def test_team_1_abbreviation_is_string(self):
        self.assertIsInstance(self.match.team_1_abbreviation, str)

    def test_team_1_players_is_list(self):
        self.assertIsInstance(self.match.team_1_players, list)

    def test_team_2_is_dict(self):
        self.assertIsInstance(self.match.team_2, dict)

    def test_team_2_id_is_set(self):
        self.assertIsNotNone(self.match.team_2_id)

    def test_team_2_abbreviation_is_string(self):
        self.assertIsInstance(self.match.team_2_abbreviation, str)

    def test_team_2_players_is_list(self):
        self.assertIsInstance(self.match.team_2_players, list)

    def test_team_ids_are_different(self):
        self.assertNotEqual(self.match.team_1_id, self.match.team_2_id)

    # --- toss (only on non-dormant matches) ---

    def test_toss_winner_is_set(self):
        if self.match.status != "dormant":
            self.assertIsNotNone(self.match.toss_winner)

    def test_toss_decision_is_string_or_empty(self):
        if self.match.status != "dormant":
            self.assertIsInstance(self.match.toss_decision, str)

    def test_toss_decision_name_is_string(self):
        if self.match.status != "dormant":
            self.assertIsInstance(self.match.toss_decision_name, str)

    def test_toss_winner_team_id_is_set(self):
        if self.match.status != "dormant":
            self.assertIsNotNone(self.match.toss_winner_team_id)

    def test_batting_first_is_string(self):
        if self.match.status != "dormant":
            self.assertIsInstance(self.match.batting_first, str)

    def test_match_winner_is_string(self):
        if self.match.status != "dormant":
            self.assertIsInstance(self.match.match_winner, str)

    # --- innings ---

    def test_innings_is_list(self):
        self.assertIsInstance(self.match.innings, list)

    def test_innings_list_is_list_or_none(self):
        self.assertTrue(
            self.match.innings_list is None
            or isinstance(self.match.innings_list, list)
        )

    def test_team_1_run_rate_is_float_or_none(self):
        self.assertTrue(
            self.match.team_1_run_rate is None
            or isinstance(self.match.team_1_run_rate, float)
        )

    def test_team_2_run_rate_is_float_or_none(self):
        self.assertTrue(
            self.match.team_2_run_rate is None
            or isinstance(self.match.team_2_run_rate, float)
        )

    def test_team_1_overs_batted_is_float_or_none(self):
        self.assertTrue(
            self.match.team_1_overs_batted is None
            or isinstance(self.match.team_1_overs_batted, float)
        )

    # --- URL construction ---

    def test_event_url_contains_match_id(self):
        self.assertIn("857713", self.match.event_url)

    def test_espn_api_url_contains_match_id(self):
        if self.match.status != "dormant":
            self.assertIn("857713", self.match.espn_api_url)

    def test_legacy_scorecard_url_is_string(self):
        self.assertIsInstance(self.match.legacy_scorecard_url, str)
        self.assertTrue(self.match.legacy_scorecard_url.startswith("http"))

    def test_details_url_contains_match_id(self):
        self.assertIn("857713", self.match.details_url)

    # --- officials ---

    def test_officials_is_list(self):
        self.assertIsInstance(self.match.officials, list)


class TestMatchErrors(unittest.TestCase):

    def test_404_raises_match_not_found(self):
        mock_404 = _mock_response(status_code=404, text="Not Found")
        with patch("espncricinfo.match.requests.get", return_value=mock_404):
            with self.assertRaises(MatchNotFoundError):
                Match(999999999)

    def test_no_scorecard_raises_error(self):
        mock_no_card = _mock_response(
            status_code=200, text="Scorecard not yet available"
        )
        with patch("espncricinfo.match.requests.get", return_value=mock_no_card):
            with self.assertRaises(NoScorecardError):
                Match(999999998)


class TestMatchIntegration:

    @pytest.mark.integration
    def test_live_match_description(self):
        m = Match(857713)
        assert isinstance(m.description, str)
        assert len(m.description) > 0

    @pytest.mark.integration
    def test_live_match_class(self):
        m = Match(857713)
        assert isinstance(m.match_class, str)

    @pytest.mark.integration
    def test_live_toss_winner(self):
        m = Match(857713)
        assert m.toss_winner is not None

    @pytest.mark.integration
    def test_live_teams_populated(self):
        m = Match(857713)
        assert m.team_1_id is not None
        assert m.team_2_id is not None
        assert m.team_1_id != m.team_2_id

    @pytest.mark.integration
    def test_live_innings_is_list(self):
        m = Match(857713)
        assert isinstance(m.innings, list)
```

**Step 2: Run unit tests to see baseline**

Run: `cd /Users/dwillis/code/python-espncricinfo && pytest tests/test_match.py -v --ignore-glob="*integration*" -k "not integration"`
Expected: Tests will PASS if fixtures exist, or FAIL with FileNotFoundError if fixtures weren't recorded yet. That is expected at this stage.

**Step 3: Commit**

```bash
git add tests/test_match.py
git commit -m "test: add comprehensive Match unit and integration tests"
```

---

### Task 4: Write `test_player.py` — unit tests (mocked)

**Files:**
- Create: `tests/test_player.py`

**Context:** `Player.__init__` makes three HTTP calls: `get_html()` (HTML page), `get_json()` (core ESPN API JSON), `get_new_json()` (hs-consumer API JSON). We patch `requests.get` and dispatch by URL substring.

**Step 1: Write `tests/test_player.py`**

```python
import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from espncricinfo.exceptions import PlayerNotFoundError
from espncricinfo.player import Player

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name):
    with open(FIXTURE_DIR / name) as f:
        if name.endswith(".json"):
            return json.load(f)
        return f.read()


def _mock_response(json_data=None, text=None, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
        mock.text = json.dumps(json_data)
    elif text is not None:
        mock.text = text
        mock.json.side_effect = ValueError("No JSON")
    else:
        mock.text = ""
        mock.json.side_effect = ValueError("No JSON")
    return mock


def _make_player(player_id=253802):
    json_data = _load_fixture("player_253802.json")
    new_json_data = _load_fixture("player_253802_new.json")
    html_text = _load_fixture("player_253802.html")

    def side_effect(url, headers=None):
        if "hs-consumer-api" in url:
            return _mock_response(json_data=new_json_data)
        elif "espnuk.org" in url:
            return _mock_response(json_data=json_data)
        else:
            return _mock_response(text=html_text)

    with patch("espncricinfo.player.requests.get", side_effect=side_effect):
        return Player(player_id)


class TestPlayerAttributes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.player = _make_player()

    def test_cricinfo_id_is_string(self):
        self.assertIsInstance(self.player.cricinfo_id, str)
        self.assertEqual(self.player.cricinfo_id, "253802")

    def test_name_is_string(self):
        self.assertIsInstance(self.player.name, str)
        self.assertGreater(len(self.player.name), 0)

    def test_first_name_is_string(self):
        self.assertIsInstance(self.player.first_name, str)

    def test_full_name_is_string(self):
        self.assertIsInstance(self.player.full_name, str)
        self.assertGreater(len(self.player.full_name), 0)

    def test_date_of_birth_is_set(self):
        self.assertIsNotNone(self.player.date_of_birth)

    def test_current_age_is_set(self):
        self.assertIsNotNone(self.player.current_age)

    def test_playing_role_is_string_or_none(self):
        self.assertTrue(
            self.player.playing_role is None
            or isinstance(self.player.playing_role, str)
        )

    def test_batting_style_is_dict_or_none(self):
        self.assertTrue(
            self.player.batting_style is None
            or isinstance(self.player.batting_style, dict)
        )

    def test_bowling_style_is_dict_or_none(self):
        self.assertTrue(
            self.player.bowling_style is None
            or isinstance(self.player.bowling_style, dict)
        )

    def test_major_teams_is_list(self):
        self.assertIsInstance(self.player.major_teams, list)

    def test_major_teams_are_strings(self):
        for team in self.player.major_teams:
            self.assertIsInstance(team, str)


class TestPlayerErrors(unittest.TestCase):

    def test_404_html_raises_player_not_found(self):
        mock_404 = _mock_response(status_code=404, text="Not Found")
        with patch("espncricinfo.player.requests.get", return_value=mock_404):
            with self.assertRaises(PlayerNotFoundError):
                Player(999999999)


class TestPlayerIntegration:

    @pytest.mark.integration
    def test_live_player_name(self):
        p = Player(253802)
        assert isinstance(p.name, str)
        assert len(p.name) > 0

    @pytest.mark.integration
    def test_live_player_full_name(self):
        p = Player(253802)
        assert isinstance(p.full_name, str)

    @pytest.mark.integration
    def test_live_player_dob(self):
        p = Player(253802)
        assert p.date_of_birth is not None

    @pytest.mark.integration
    def test_live_player_major_teams(self):
        p = Player(253802)
        assert isinstance(p.major_teams, list)
        assert len(p.major_teams) > 0

    @pytest.mark.integration
    def test_live_player_cricinfo_id_is_string(self):
        p = Player(253802)
        assert isinstance(p.cricinfo_id, str)
```

**Step 2: Run player unit tests**

Run: `cd /Users/dwillis/code/python-espncricinfo && pytest tests/test_player.py -v -k "not integration"`
Expected: PASS (if fixtures exist) or FileNotFoundError (if fixtures not yet recorded)

**Step 3: Commit**

```bash
git add tests/test_player.py
git commit -m "test: add comprehensive Player unit and integration tests"
```

---

### Task 5: Write `test_exceptions.py` — error handling tests

**Files:**
- Create: `tests/test_exceptions.py`

**Context:** These tests verify that the right custom exceptions are raised on bad API responses. They don't need fixture files — they just return mock bad responses.

**Step 1: Write `tests/test_exceptions.py`**

```python
import unittest
from unittest.mock import MagicMock, patch

from espncricinfo.exceptions import MatchNotFoundError, NoScorecardError, PlayerNotFoundError
from espncricinfo.match import Match
from espncricinfo.player import Player


def _mock_response(text="", status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = text
    mock.json.side_effect = ValueError("No JSON")
    return mock


class TestMatchExceptions(unittest.TestCase):

    def test_match_not_found_on_404(self):
        with patch(
            "espncricinfo.match.requests.get",
            return_value=_mock_response(status_code=404),
        ):
            with self.assertRaises(MatchNotFoundError):
                Match(1)

    def test_no_scorecard_error_on_message(self):
        with patch(
            "espncricinfo.match.requests.get",
            return_value=_mock_response(text="Scorecard not yet available"),
        ):
            with self.assertRaises(NoScorecardError):
                Match(2)

    def test_match_not_found_is_type_error_subclass(self):
        """MatchNotFoundError must be a TypeError subclass (existing contract)."""
        self.assertTrue(issubclass(MatchNotFoundError, TypeError))

    def test_no_scorecard_error_is_type_error_subclass(self):
        self.assertTrue(issubclass(NoScorecardError, TypeError))


class TestPlayerExceptions(unittest.TestCase):

    def test_player_not_found_on_404(self):
        with patch(
            "espncricinfo.player.requests.get",
            return_value=_mock_response(status_code=404),
        ):
            with self.assertRaises(PlayerNotFoundError):
                Player(1)

    def test_player_not_found_is_type_error_subclass(self):
        self.assertTrue(issubclass(PlayerNotFoundError, TypeError))
```

**Step 2: Run exception tests (no fixtures needed)**

Run: `cd /Users/dwillis/code/python-espncricinfo && pytest tests/test_exceptions.py -v`
Expected: All PASS — these have no fixture dependency

**Step 3: Commit**

```bash
git add tests/test_exceptions.py
git commit -m "test: add exception handling tests for Match and Player"
```

---

### Task 6: Run full suite and triage failures

**Step 1: Run all unit tests together**

Run: `cd /Users/dwillis/code/python-espncricinfo && pytest tests/ -v -k "not integration" 2>&1 | head -80`
Expected: Exception tests PASS. Match and Player tests may fail with `FileNotFoundError` if fixtures weren't recorded, or with assertion errors revealing API shape mismatches — that is fine and expected.

**Step 2: If fixture files are missing, run the refresh script**

Run: `python scripts/refresh_fixtures.py`
Then re-run: `pytest tests/ -v -k "not integration"`

**Step 3: Document any failures in a comment at the top of `tests/test_match.py`**

If certain attributes are consistently `None` or the JSON shape has changed, add a comment block:

```python
# KNOWN FAILURES (as of 2026-02-21):
# - match.rosters returns None (comms_json HTML parsing broke)
# - match.batsmen(1) returns None (same cause)
```

**Step 4: Commit final state**

```bash
git add tests/
git commit -m "test: run full suite, document known fixture-based failures"
```

---

### Task 7: Add `tests/fixtures/.gitkeep` and update README

**Files:**
- Create: `tests/fixtures/.gitkeep` (ensures dir tracked if fixtures excluded)
- Modify: `README.md`

**Step 1: Check whether fixture JSON files should be gitignored**

The fixture files ARE intentional artifacts — commit them. They document the expected API shape at a point in time. Do NOT add them to `.gitignore`.

**Step 2: Add a Testing section to README.md**

Open `README.md` and append:

```markdown
## Testing

### Unit tests (no network required)

```bash
pytest tests/ -k "not integration"
```

### Integration tests (hits live ESPN API)

```bash
pytest tests/ --live
```

### Refreshing fixtures

If the ESPN API changes shape, re-record fixtures:

```bash
python scripts/refresh_fixtures.py
```

Then re-run the unit tests and update any assertions that reflect the new shape.
```

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add Testing section to README"
```

---

## Summary

| Task | What it produces |
|------|-----------------|
| 1 | `tests/` scaffold, `pytest.ini`, `--live` flag |
| 2 | Fixture recording script + committed JSON fixtures |
| 3 | `test_match.py` — 30+ unit assertions + 5 integration tests |
| 4 | `test_player.py` — 12+ unit assertions + 5 integration tests |
| 5 | `test_exceptions.py` — 6 error-path tests (no fixtures needed) |
| 6 | Full suite run, failures triaged and documented |
| 7 | README updated with test instructions |

**To run unit tests:** `pytest tests/ -k "not integration"`
**To run integration tests:** `pytest tests/ --live`
**To refresh fixtures:** `python scripts/refresh_fixtures.py`
