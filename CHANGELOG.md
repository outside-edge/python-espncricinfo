# Changelog

## [Unreleased]

### Fixed

- Match pages and `Summary()` load inside Jupyter and other code that already
  runs an asyncio event loop; they raised `asyncio.run() cannot be called from
  a running event loop` (#55).

### Added

- `Ground` (city, country, capacity, indoor) from ESPN's venue records, and
  `Match.ground` to load a match's ground (#8).
- `Match.get_match_ids(year, match_format)`: every international match id of
  one format in a year, from Statsguru, back to 1877. With `Match(match_id)`
  this loads every scorecard of a format (#34).
- `Match.get_matches_on(date)`: the matches being played on one day, Tests
  included on each of their days (#28).
- `Match(match_id)` works without a series ID: the match page is found from
  the match ID and `series_id` is read from it (#50).
- Each `Match.innings` entry has `fours` and `sixes`: ESPN's innings total,
  else the sum over batters who batted, else None (#54).
- `Match.over_by_over`: runs and wickets per over for each innings, typed as
  `OverEntry` rows; empty where ESPN has no over data (#42).
- `Series.season(key)` finds a season by year or by ESPNcricinfo's two-year
  label (`"2024/25"`), and `Season.label` gives that label. Multi-year seasons
  live under their own series ID, now reachable as `season.series_id` (#76).

## [1.0.1] - 2026-10-23

### Changed

- Gaurav Sood is listed as an author in the package metadata and citation.

## [1.0.0] - 2026-10-23

First release since 0.6.1 (2021). The 0.5.x/0.6.x releases call ESPN endpoints
that no longer respond, and 0.6/0.6.1 were uploaded only as eggs, which pip
cannot install.

### Changed

- `Match.series_id`, `Player.player_id` and `Series.series_id` are ints.
  `Match.cancelled_match` is now `Match.canceled` (a bool).
- `Player.playing_role`, `batting_style` and `bowling_style` are strings such as
  `'Top-order batter'` and `'Right-hand bat'`, not raw ESPN dicts;
  `date_of_birth` is a `datetime.date`; `current_age` is now `age`.
- `Match.match_winner`, `home_team`, `batting_first`, `toss_winner` and
  `toss_decision_name` are `None` when ESPN has no value. `match_winner` used
  to name team 2 for any match without a winner, including draws and unplayed
  matches. These attributes now exist for unplayed matches too.
- `Series(...)` no longer fetches every event record up front; `Series.events`
  loads them on first access.
- Match pages are loaded with Playwright (WebKit), because ESPN's CDN refuses
  plain HTTP clients. Run `playwright install webkit` after installing.
- `Match` takes both `match_id` and `series_id`.
- `Summary().matches` and `Match.get_recent_matches()` return `MatchRef`
  objects, which still unpack as `(series_id, match_id)`.
- `get_recent_matches()` sends dates as DD-MM-YYYY (ESPN rejects YYYY-MM-DD)
  and accepts `datetime.date` or either string form. ESPN returns about two
  weeks of matches ending on that date.
- Requires Python 3.12 or newer.

### Added

- Type hints on the whole public API and a `py.typed` marker
  (`pyright --verifytypes`: 100% of 209 exported symbols).
- `Match.batting_scorecard` and `Match.bowling_scorecard`, with rows typed as
  `BattingEntry` / `BowlingEntry`.
- Navigation from a `Series` to its seasons, teams, squads and matches.

### Fixed

- `Player.get_data()` raised `TypeError` on every call.
- `Player` statistics methods no longer overwrite `Player.url`.
- `Series` no longer raises `AttributeError` when the series record is empty.
- Every HTTP request has a 30-second timeout, and 5xx responses from ESPN's
  core API are retried up to three times with backoff.

### Removed

- `Match` attributes that never held data in this version: `officials`,
  `rain_rule`, `weather_location_code`, `followon`, `continent`,
  `latest_batting`, `latest_bowling`, `latest_innings`, `latest_innings_fow`,
  `html`, `comms_json`. Duplicates of other fields: `current_summary`
  (= `result`), `present_datetime_*` and `start_datetime_local/gmt`
  (= `start_datetime`), `town_area`, `toss_winner_team_id` and
  `toss_choice_team_id` (= `toss_winner`), `toss_decision` (use
  `toss_decision_name`). Also `town_id` (it held the ground id),
  `legacy_scorecard_url`, `series`, `team_*_batting_result`, `match_json()`,
  `innings_comms_url()` (the commentary API no longer resolves) and
  `get_html()` / `get_comms_json()`.
- `Player.get_html()` (ESPN returns 403 for profile pages), `Player.url`,
  `Player.headers` and `Player.cricinfo_id` (use `player_id`).
- `Series.get_json()`, `Series.events_json`.
- `Player.in_team_for_match`, `batting_for_match` and `bowling_for_match`,
  which only raised `NotImplementedError`. Use `Match.team_1_players`,
  `Match.batsmen()` and `Match.bowlers()`.

## Before 1.0.0

### 2018-08-09

* Added methods for retrieving matches in a series. ([Issue 19](https://github.com/dwillis/python-espncricinfo/issues/19))

### 2018-08-05

* Converted batting and bowling averages into a single dictionary. ([Issue 25](https://github.com/dwillis/python-espncricinfo/issues/25))
