# Design: MatchRef Dataclass

**Date:** 2026-02-22
**Status:** Approved

## Goal

Give users a typed, serializable value object for storing and passing around
ESPN Cricinfo match references (the `series_id` + `match_id` pair needed to
construct a `Match`). Replace the bare `(series_id, match_id)` tuples currently
returned by `get_recent_matches()` and `Summary().matches`.

## `MatchRef` — `espncricinfo/match_ref.py`

A `@dataclass` with two `int` fields:

```python
@dataclass
class MatchRef:
    series_id: int
    match_id: int
```

Both fields stored as `int`, consistent with `Match.__init__` which coerces
`match_id` and `series_id` to `int` on construction.

### Serialization

| Method | Returns | Notes |
|--------|---------|-------|
| `to_dict()` | `{"series_id": 1478874, "match_id": 1478914}` | Keys are stable strings |
| `from_dict(d)` *(classmethod)* | `MatchRef(...)` | Accepts any mapping with those keys |
| `to_csv_row()` | `["1478874", "1478914"]` | Strings; order: series_id, match_id |
| `from_csv_row(row)` *(classmethod)* | `MatchRef(...)` | Accepts any 2-element sequence |

### Convenience

- `to_match()` → `Match(self.match_id, self.series_id)` — hydrates a full
  `Match` object (triggers Playwright fetch)
- `__iter__` → yields `self.series_id`, then `self.match_id` — preserves
  tuple-unpacking backward compatibility:
  `series_id, match_id = ref` continues to work

### Repr

Dataclass default: `MatchRef(series_id=1478874, match_id=1478914)`

## Return Type Changes

### `match.py` — `get_recent_matches()`

Change the `results.append((series_id, match_id))` line to
`results.append(MatchRef(series_id=series_id, match_id=match_id))`.
Return type annotation (if added) becomes `list[MatchRef]`.

### `summary.py` — `Summary.matches`

Inherited automatically. Update the docstring example to show `MatchRef` and
demonstrate `to_match()`:

```python
for ref in Summary().matches:
    m = ref.to_match()
    print(m.description)
```

## Tests — `tests/test_match_ref.py` (new file)

- Fields are coerced to `int`
- `to_dict()` returns correct keys and `int` values
- `from_dict()` round-trips correctly
- `to_csv_row()` returns `list` of `str`
- `from_csv_row()` round-trips correctly
- `to_match()` calls `Match` with `(match_id, series_id)` in correct order (mocked)
- Tuple unpacking works: `series_id, match_id = MatchRef(1478874, 1478914)`
- `from_dict` / `from_csv_row` accept string values (coerce to int)

### Updates to existing tests

- `test_summary.py`: `FAKE_MATCHES` changed to list of `MatchRef`; assertions
  updated to check for `MatchRef` instances
- `test_match.py` (integration): any `get_recent_matches` assertion updated
  to expect `MatchRef` objects

## Out of Scope

- CSV file I/O (reading/writing files) — left to callers
- JSON file I/O — left to callers
- Equality/hashing beyond dataclass defaults
- `MatchRef` collections / stores
