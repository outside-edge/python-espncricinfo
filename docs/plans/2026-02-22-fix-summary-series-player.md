# Fix summary.py, series.py, player.py Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix three modules broken by the Match API change: rewrite Summary around get_recent_matches(), fix a silent raise bug in Series, and deprecate unreimplementable per-match methods on Player.

**Architecture:** summary.py becomes a one-method wrapper around Match.get_recent_matches(); series.py gets a one-line raise fix; player.py's three broken per-match methods are deprecated with warnings.warn + NotImplementedError. All changes are test-driven.

**Tech Stack:** Python 3, pytest, unittest.mock, warnings stdlib module

---

### Task 1: Fix series.py raise bug

**Files:**
- Modify: `espncricinfo/series.py:31`
- Test: `tests/test_series.py` (create)

**Step 1: Write the failing test**

Create `tests/test_series.py`:

```python
import unittest
from unittest.mock import MagicMock, patch

from espncricinfo.exceptions import NoSeriesError
from espncricinfo.series import Series


def _mock_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {}
    return mock


class TestSeriesNotFound(unittest.TestCase):

    def test_series_not_found_raises_no_series_error(self):
        with patch("espncricinfo.series.requests.get",
                   return_value=_mock_response(status_code=404)):
            with self.assertRaises(NoSeriesError):
                Series(9999999)
```

**Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_series.py -v
```
Expected: FAIL — `NoSeriesError` is not raised because `raise "Not Found"` is a no-op in Python 3.

**Step 3: Fix series.py**

In `espncricinfo/series.py`, in the `get_json` method, replace:
```python
raise "Not Found"
```
with:
```python
raise NoSeriesError("Series not found")
```

`NoSeriesError` is already imported at the top of the file.

**Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_series.py -v
```
Expected: PASS

**Step 5: Run full suite**

```bash
uv run pytest tests/ -k "not integration" -q
```
Expected: all existing tests still pass, plus the new series test.

**Step 6: Commit**

```bash
git add espncricinfo/series.py tests/test_series.py
git commit -m "fix: raise NoSeriesError on 404 in Series.get_json (was silent no-op)"
```

---

### Task 2: Deprecate broken player per-match methods

**Files:**
- Modify: `espncricinfo/player.py` (lines ~85-108: in_team_for_match, batting_for_match, bowling_for_match)
- Test: `tests/test_player.py` (modify — add 3 new tests)

**Step 1: Write the failing tests**

Add to `tests/test_player.py` inside a new class `TestPlayerDeprecatedMethods`:

```python
import warnings


class TestPlayerDeprecatedMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.player = _make_player()

    def test_in_team_for_match_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.player.in_team_for_match(1478914, 1478874)

    def test_batting_for_match_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.player.batting_for_match(1478914, 1478874)

    def test_bowling_for_match_raises_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.player.bowling_for_match(1478914, 1478874)

    def test_in_team_for_match_emits_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                self.player.in_team_for_match(1478914, 1478874)
            except NotImplementedError:
                pass
            self.assertTrue(any(issubclass(x.category, DeprecationWarning) for x in w))
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_player.py::TestPlayerDeprecatedMethods -v
```
Expected: FAIL — methods still have old signatures and broken bodies.

**Step 3: Update player.py**

Add `import warnings` at the top of `espncricinfo/player.py`.

Replace the three methods with:

```python
def in_team_for_match(self, match_id, series_id):
    """
    .. deprecated::
        This method is not implemented against the current ESPN Cricinfo API.
        Use Match(match_id, series_id).team_1_players and .team_2_players directly.
    """
    warnings.warn(
        "in_team_for_match is deprecated and not implemented against the current API.",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError(
        "in_team_for_match is not implemented against the current ESPN Cricinfo API. "
        "Use Match(match_id, series_id).team_1_players and .team_2_players directly."
    )

def batting_for_match(self, match_id, series_id):
    """
    .. deprecated::
        This method is not implemented against the current ESPN Cricinfo API.
        Use Match(match_id, series_id).batsmen(innings) directly.
    """
    warnings.warn(
        "batting_for_match is deprecated and not implemented against the current API.",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError(
        "batting_for_match is not implemented against the current ESPN Cricinfo API. "
        "Use Match(match_id, series_id).batsmen(innings) directly."
    )

def bowling_for_match(self, match_id, series_id):
    """
    .. deprecated::
        This method is not implemented against the current ESPN Cricinfo API.
        Use Match(match_id, series_id).bowlers(innings) directly.
    """
    warnings.warn(
        "bowling_for_match is deprecated and not implemented against the current API.",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError(
        "bowling_for_match is not implemented against the current ESPN Cricinfo API. "
        "Use Match(match_id, series_id).bowlers(innings) directly."
    )
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_player.py -v
```
Expected: all player tests pass including the new deprecation tests.

**Step 5: Run full suite**

```bash
uv run pytest tests/ -k "not integration" -q
```
Expected: all tests pass.

**Step 6: Commit**

```bash
git add espncricinfo/player.py tests/test_player.py
git commit -m "deprecate: mark in_team_for_match/batting_for_match/bowling_for_match as NotImplemented"
```

---

### Task 3: Rewrite summary.py around get_recent_matches()

**Files:**
- Modify: `espncricinfo/summary.py` (full rewrite)
- Test: `tests/test_summary.py` (create)

**Step 1: Write the failing tests**

Create `tests/test_summary.py`:

```python
import unittest
from unittest.mock import patch

from espncricinfo.summary import Summary


FAKE_MATCHES = [
    (1478874, 1478914),
    (1234567, 1234568),
]


class TestSummary(unittest.TestCase):

    def test_summary_matches_is_list(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=FAKE_MATCHES):
            s = Summary()
            self.assertIsInstance(s.matches, list)

    def test_summary_matches_returns_tuples(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=FAKE_MATCHES):
            s = Summary()
            self.assertEqual(s.matches, FAKE_MATCHES)

    def test_summary_passes_date_to_get_recent_matches(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=[]) as mock_grm:
            Summary(date="2026-02-22")
            mock_grm.assert_called_once_with("2026-02-22")

    def test_summary_no_date_calls_get_recent_matches_with_none(self):
        with patch("espncricinfo.summary.Match.get_recent_matches",
                   return_value=[]) as mock_grm:
            Summary()
            mock_grm.assert_called_once_with(None)
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_summary.py -v
```
Expected: FAIL — `Summary` still has the old RSS-based implementation.

**Step 3: Rewrite summary.py**

Replace the entire contents of `espncricinfo/summary.py` with:

```python
from espncricinfo.match import Match


class Summary:
    """
    Returns recent matches as a list of (series_id, match_id) tuples.

    Uses Match.get_recent_matches() which scrapes the ESPN Cricinfo
    results page via Playwright. Pass an optional date string (YYYY-MM-DD
    or DD-MM-YYYY) to get matches for a specific day; defaults to today.

    Example::

        from espncricinfo.summary import Summary
        from espncricinfo.match import Match

        for series_id, match_id in Summary().matches:
            m = Match(match_id, series_id)
            print(m.description)
    """

    def __init__(self, date=None):
        self.matches = Match.get_recent_matches(date)
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_summary.py -v
```
Expected: all 4 tests pass.

**Step 5: Run full suite**

```bash
uv run pytest tests/ -k "not integration" -q
```
Expected: all tests pass.

**Step 6: Commit**

```bash
git add espncricinfo/summary.py tests/test_summary.py
git commit -m "feat: rewrite Summary to wrap Match.get_recent_matches() (drop dead RSS feed)"
```

---

### Task 4: Final verification

**Step 1: Run full suite one last time**

```bash
uv run pytest tests/ -k "not integration" -v
```
Expected: all tests pass, 0 failures, 0 errors.

**Step 2: Confirm test count is sane**

The suite should have grown by roughly 8 tests (1 series + 4 deprecated player + 4 summary) on top of the existing 76.

**Step 3: Commit if anything was missed**

If any stray changes exist:
```bash
git add -p
git commit -m "chore: cleanup after summary/series/player fixes"
```
