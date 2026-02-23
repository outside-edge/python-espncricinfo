# Design: batting_scorecard and bowling_scorecard Properties

**Date:** 2026-02-22
**Status:** Approved

## Goal

Add `batting_scorecard` and `bowling_scorecard` as `@property` attributes on `Match`,
returning cleaned-up flat dicts for all innings.

## Approach

Properties on `Match` (Option A). No new files, no new classes. Consistent with
existing `innings`, `team_1_players`, etc. Return type is `list[list[dict]]` —
outer list indexed by innings order, inner list is per-player entries.

## `Match.batting_scorecard`

`@property` returning `list[list[dict]]`.

Each batting dict:

```python
{
    "name":        str,    # player.name (short)
    "full_name":   str,    # player.longName
    "player_id":   int,    # player.objectId
    "runs":        int | None,    # None if did not bat
    "balls":       int | None,
    "minutes":     int | None,
    "fours":       int | None,
    "sixes":       int | None,
    "strike_rate": float | None,
    "is_out":      bool,
    "dismissal":   str,    # dismissalText.long if out, "not out", or "did not bat"
    "batted":      bool,   # battedType == "yes"
}
```

Private helper: `_batting_entry(raw: dict) -> dict`

## `Match.bowling_scorecard`

`@property` returning `list[list[dict]]`.

Each bowling dict:

```python
{
    "name":      str,          # player.name
    "full_name": str,          # player.longName
    "player_id": int,          # player.objectId
    "overs":     float | None,
    "maidens":   int | None,
    "runs":      int | None,   # conceded
    "wickets":   int | None,
    "economy":   float | None,
    "wides":     int | None,
    "no_balls":  int | None,
    "dots":      int | None,
}
```

Private helper: `_bowling_entry(raw: dict) -> dict`

## Error Handling

- If `batsmen(i)` or `bowlers(i)` returns `None` for an innings, that innings
  contributes an empty list `[]` — the property never raises.
- Missing individual fields default to `None`.

## Tests

New class `TestMatchScorecardProperties` in `tests/test_match.py`:

- `batting_scorecard` is a list of length 2
- Each inner list is non-empty
- First innings, first batsman: correct keys, `runs=82`, `balls=55`, `is_out=True`,
  `dismissal` contains "Gardner", `batted=True`, `player_id` is an int
- `bowling_scorecard` is a list of length 2
- First innings, first bowler: correct keys, `wickets` is an int, `economy` is a float
- Both properties return `[]` inner lists gracefully if innings data missing

## Out of Scope

- Fall of wickets in scorecard (already available via `fows()`)
- Dismissal fielder names (available in raw data but not needed here)
- Partnership data
