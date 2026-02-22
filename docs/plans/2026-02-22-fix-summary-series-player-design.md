# Design: Fix summary.py, series.py, player.py

**Date:** 2026-02-22
**Status:** Approved

## Background

The `Match` class was rewritten to use Playwright + `__NEXT_DATA__` (the old ESPN engine
API endpoints are permanently 403'd). The new constructor is `Match(match_id, series_id)`.
Three other modules were left in a broken state:

- `summary.py` — calls `Match(m)` with one arg; also hits a dead RSS feed
- `series.py` — `raise "Not Found"` is a silent no-op in Python 3
- `player.py` — three per-match methods call `Match(match_id)` and reference
  `m.full_scorecard` which no longer exists

## Changes

### summary.py — rewrite around `get_recent_matches()`

Replace the entire implementation with a thin wrapper around
`Match.get_recent_matches(date)`. The new `Summary`:

- Accepts an optional `date` parameter (defaults to today via `get_recent_matches`)
- Stores results as `self.matches` — a list of `(series_id, match_id)` tuples
- Does **not** eagerly instantiate `Match` objects (too slow; callers do it themselves)
- Removes: RSS fetch, BeautifulSoup XML parsing, `_match_ids()`, `_build_matches()`

```python
class Summary:
    def __init__(self, date=None):
        self.matches = Match.get_recent_matches(date)
```

### series.py — fix raise bug

In `get_json()`, replace:
```python
raise "Not Found"
```
with:
```python
raise NoSeriesError(f"Series not found")
```

`NoSeriesError` is already imported from `espncricinfo.exceptions`.

### player.py — deprecate broken per-match methods

The three methods `in_team_for_match`, `batting_for_match`, `bowling_for_match`
cannot be fixed without significant reimplementation against the new API (they
relied on `m.full_scorecard` which no longer exists). They are deprecated:

- Signature updated to `(self, match_id, series_id)` to match new `Match` API
- `warnings.warn(..., DeprecationWarning)` added at entry
- Body replaced with `raise NotImplementedError(...)` with a clear message
- Docstring updated to note deprecated status

## Tests

- `test_summary.py` — unit test: mock `Match.get_recent_matches`, assert
  `Summary().matches` returns the mocked list; test with explicit date arg
- `test_series.py` — unit test: mock `requests.get` returning 404, assert
  `NoSeriesError` is raised
- `test_player.py` — add tests asserting the three deprecated methods raise
  `NotImplementedError` (and emit `DeprecationWarning`)
- Existing 76 tests must continue to pass

## Out of scope

- Reimplementing `batting_for_match` / `bowling_for_match` against the new API
- Any changes to `Series` beyond the one-line raise fix
