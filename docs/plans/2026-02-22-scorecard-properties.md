# Scorecard Properties Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `batting_scorecard` and `bowling_scorecard` as `@property` attributes on `Match`, returning cleaned-up flat dicts for all innings.

**Architecture:** Two private helper methods (`_batting_entry`, `_bowling_entry`) transform raw ESPN dicts into flat snake_case dicts. Two `@property` methods iterate over all innings using the existing `batsmen()` and `bowlers()` methods, calling the helpers. All added to `espncricinfo/match.py`. Tests added to `tests/test_match.py`.

**Tech Stack:** Python 3, pytest, unittest.mock

---

### Task 1: Add `_batting_entry` helper and `batting_scorecard` property

**Files:**
- Modify: `espncricinfo/match.py` (after line 686, before the Static helpers section)
- Test: `tests/test_match.py` (add new class at end)

**Step 1: Write the failing tests**

Add this class to the END of `tests/test_match.py`:

```python
class TestMatchScorecardProperties(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.match = _make_match()

    # ---- batting_scorecard ----

    def test_batting_scorecard_is_list_of_2_innings(self):
        sc = self.match.batting_scorecard
        self.assertIsInstance(sc, list)
        self.assertEqual(len(sc), 2)

    def test_batting_scorecard_innings_are_nonempty_lists(self):
        for innings in self.match.batting_scorecard:
            self.assertIsInstance(innings, list)
            self.assertGreater(len(innings), 0)

    def test_batting_scorecard_entry_has_required_keys(self):
        entry = self.match.batting_scorecard[0][0]
        for key in ("name", "full_name", "player_id", "runs", "balls",
                    "minutes", "fours", "sixes", "strike_rate",
                    "is_out", "dismissal", "batted"):
            self.assertIn(key, entry)

    def test_batting_scorecard_first_batsman_values(self):
        # Smriti Mandhana: 82 runs, 55 balls, out caught Gardner b Sutherland
        entry = self.match.batting_scorecard[0][0]
        self.assertEqual(entry["runs"], 82)
        self.assertEqual(entry["balls"], 55)
        self.assertTrue(entry["is_out"])
        self.assertIn("Gardner", entry["dismissal"])
        self.assertTrue(entry["batted"])
        self.assertIsInstance(entry["player_id"], int)

    def test_batting_scorecard_strike_rate_is_float(self):
        entry = self.match.batting_scorecard[0][0]
        self.assertIsInstance(entry["strike_rate"], float)
```

**Step 2: Run to confirm they fail**

```bash
uv run pytest tests/test_match.py::TestMatchScorecardProperties -v
```

Expected: FAIL with `AttributeError: 'Match' object has no attribute 'batting_scorecard'`

**Step 3: Add `_batting_entry` and `batting_scorecard` to `espncricinfo/match.py`**

Insert after line 686 (after `fows()`, before the `# Static helpers` comment):

```python
    # ------------------------------------------------------------------
    # Scorecard helpers
    # ------------------------------------------------------------------

    def _batting_entry(self, raw: dict) -> dict:
        """Transform a raw inningBatsmen dict into a clean flat dict."""
        player = raw.get("player") or {}
        batted = raw.get("battedType") == "yes"
        is_out = bool(raw.get("isOut"))
        if not batted:
            dismissal = "did not bat"
        elif is_out:
            dismissal = (raw.get("dismissalText") or {}).get("long", "out")
        else:
            dismissal = "not out"
        return {
            "name":        player.get("name"),
            "full_name":   player.get("longName"),
            "player_id":   player.get("objectId"),
            "runs":        raw.get("runs") if batted else None,
            "balls":       raw.get("balls") if batted else None,
            "minutes":     raw.get("minutes") if batted else None,
            "fours":       raw.get("fours") if batted else None,
            "sixes":       raw.get("sixes") if batted else None,
            "strike_rate": raw.get("strikerate") if batted else None,
            "is_out":      is_out,
            "dismissal":   dismissal,
            "batted":      batted,
        }

    @property
    def batting_scorecard(self) -> list:
        """
        Return batting scorecard for all innings as ``list[list[dict]]``.

        Outer list is indexed by innings order; inner list has one entry
        per batsman. Players who did not bat have ``batted=False`` and
        numeric fields as ``None``.

        Example::

            for i, innings in enumerate(m.batting_scorecard, 1):
                print(f"Innings {i}:")
                for b in innings:
                    print(f"  {b['name']}: {b['runs']} ({b['balls']}) - {b['dismissal']}")
        """
        result = []
        for i in range(1, len(self.innings) + 1):
            raw_list = self.batsmen(i)
            if raw_list:
                result.append([self._batting_entry(r) for r in raw_list])
            else:
                result.append([])
        return result
```

**Step 4: Run the tests to verify they pass**

```bash
uv run pytest tests/test_match.py::TestMatchScorecardProperties -v
```

Expected: 5 batting tests PASS

**Step 5: Run full suite**

```bash
uv run pytest tests/ -k "not integration" -q
```

Expected: all tests pass

**Step 6: Commit**

```bash
git add espncricinfo/match.py tests/test_match.py
git commit -m "feat: add batting_scorecard property with _batting_entry helper"
```

---

### Task 2: Add `_bowling_entry` helper and `bowling_scorecard` property

**Files:**
- Modify: `espncricinfo/match.py` (after `batting_scorecard` property)
- Test: `tests/test_match.py` (add to `TestMatchScorecardProperties`)

**Step 1: Write the failing tests**

Add to the `TestMatchScorecardProperties` class:

```python
    # ---- bowling_scorecard ----

    def test_bowling_scorecard_is_list_of_2_innings(self):
        sc = self.match.bowling_scorecard
        self.assertIsInstance(sc, list)
        self.assertEqual(len(sc), 2)

    def test_bowling_scorecard_innings_are_nonempty_lists(self):
        for innings in self.match.bowling_scorecard:
            self.assertIsInstance(innings, list)
            self.assertGreater(len(innings), 0)

    def test_bowling_scorecard_entry_has_required_keys(self):
        entry = self.match.bowling_scorecard[0][0]
        for key in ("name", "full_name", "player_id", "overs", "maidens",
                    "runs", "wickets", "economy", "wides", "no_balls", "dots"):
            self.assertIn(key, entry)

    def test_bowling_scorecard_first_bowler_values(self):
        # Darcie Brown bowled first innings
        entry = self.match.bowling_scorecard[0][0]
        self.assertEqual(entry["name"], "D Brown")
        self.assertIsInstance(entry["wickets"], int)
        self.assertIsInstance(entry["overs"], float)

    def test_bowling_scorecard_economy_is_float_or_none(self):
        entry = self.match.bowling_scorecard[0][0]
        self.assertTrue(
            entry["economy"] is None or isinstance(entry["economy"], float)
        )
```

**Step 2: Run to confirm they fail**

```bash
uv run pytest tests/test_match.py::TestMatchScorecardProperties::test_bowling_scorecard_is_list_of_2_innings -v
```

Expected: FAIL with `AttributeError: 'Match' object has no attribute 'bowling_scorecard'`

**Step 3: Add `_bowling_entry` and `bowling_scorecard` to `espncricinfo/match.py`**

Insert after `batting_scorecard` property:

```python
    def _bowling_entry(self, raw: dict) -> dict:
        """Transform a raw inningBowlers dict into a clean flat dict."""
        player = raw.get("player") or {}
        return {
            "name":      player.get("name"),
            "full_name": player.get("longName"),
            "player_id": player.get("objectId"),
            "overs":     raw.get("overs"),
            "maidens":   raw.get("maidens"),
            "runs":      raw.get("conceded"),
            "wickets":   raw.get("wickets"),
            "economy":   raw.get("economy"),
            "wides":     raw.get("wides"),
            "no_balls":  raw.get("noballs"),
            "dots":      raw.get("dots"),
        }

    @property
    def bowling_scorecard(self) -> list:
        """
        Return bowling scorecard for all innings as ``list[list[dict]]``.

        Outer list is indexed by innings order; inner list has one entry
        per bowler.

        Example::

            for i, innings in enumerate(m.bowling_scorecard, 1):
                print(f"Innings {i}:")
                for b in innings:
                    print(f"  {b['name']}: {b['wickets']}/{b['runs']} ({b['overs']} ov)")
        """
        result = []
        for i in range(1, len(self.innings) + 1):
            raw_list = self.bowlers(i)
            if raw_list:
                result.append([self._bowling_entry(r) for r in raw_list])
            else:
                result.append([])
        return result
```

**Step 4: Run all scorecard tests**

```bash
uv run pytest tests/test_match.py::TestMatchScorecardProperties -v
```

Expected: all 10 tests PASS

**Step 5: Run full suite**

```bash
uv run pytest tests/ -k "not integration" -q
```

Expected: all tests pass (should be ~117)

**Step 6: Commit**

```bash
git add espncricinfo/match.py tests/test_match.py
git commit -m "feat: add bowling_scorecard property with _bowling_entry helper"
```

---

### Task 3: Final verification

**Step 1: Run full suite**

```bash
uv run pytest tests/ -k "not integration" -v
```

Expected: all tests pass, 0 failures

**Step 2: Smoke test from the REPL**

```bash
uv run python -c "
import json
from unittest.mock import patch
from espncricinfo.match import Match

next_data = json.load(open('tests/fixtures/match_1478914_next_data.json'))
with patch('espncricinfo.match._playwright_fetch', return_value=next_data):
    m = Match(1478914, 1478874)

print('Innings count:', len(m.batting_scorecard))
for i, inn in enumerate(m.batting_scorecard, 1):
    print(f'Innings {i}: {len(inn)} batsmen')
    print(' ', inn[0]['name'], inn[0]['runs'], inn[0]['dismissal'])

for i, inn in enumerate(m.bowling_scorecard, 1):
    print(f'Innings {i}: {len(inn)} bowlers')
    print(' ', inn[0]['name'], inn[0]['wickets'], 'wkts')
"
```

Expected: clean output showing both innings for both scorecards

**Step 3: Commit any remaining changes**

```bash
git status
# only commit if there are actual changes
```
