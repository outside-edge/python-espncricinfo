# Changelog

## [Unreleased]

First release since 0.6.1 (2021). The 0.5.x/0.6.x releases call ESPN endpoints
that no longer respond, and 0.6/0.6.1 were uploaded only as eggs, which pip
cannot install.

### Changed

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

- `Match.batting_scorecard` and `Match.bowling_scorecard`.
- Navigation from a `Series` to its seasons, teams, squads and matches.

### Fixed

- `Player.get_data()` raised `TypeError` on every call.
- `Player` statistics methods no longer overwrite `Player.url`.
- `Series` no longer raises `AttributeError` when the series record is empty.
- Every HTTP request has a 30-second timeout, and 5xx responses from ESPN's
  core API are retried up to three times with backoff.

### Removed

- `Player.in_team_for_match`, `batting_for_match` and `bowling_for_match`,
  which only raised `NotImplementedError`. Use `Match.team_1_players`,
  `Match.batsmen()` and `Match.bowlers()`.

## Before 1.0.0

### 2018-08-09

* Added methods for retrieving matches in a series. ([Issue 19](https://github.com/dwillis/python-espncricinfo/issues/19))

### 2018-08-05

* Converted batting and bowling averages into a single dictionary. ([Issue 25](https://github.com/dwillis/python-espncricinfo/issues/25))
