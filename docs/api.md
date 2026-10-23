# API reference

## Matches

```{eval-rst}
.. autoclass:: espncricinfo.match.Match
   :members: get_recent_matches, batting_scorecard, bowling_scorecard, batsmen, bowlers, extras, fows, innings_comms_url, match_json

.. autoclass:: espncricinfo.match_ref.MatchRef
   :members:

.. autoclass:: espncricinfo.summary.Summary
```

## Players

```{eval-rst}
.. autoclass:: espncricinfo.player.Player
   :members: major_teams, get_data, get_career_summary, get_career_averages
```

## Series, seasons and teams

```{eval-rst}
.. autoclass:: espncricinfo.series.Series
   :members: season_objects, current_season, matches, current_matches

.. autoclass:: espncricinfo.seasons.Season
   :members: teams, match_refs, series, from_reference

.. autoclass:: espncricinfo.teams.Team
   :members: players, from_reference
```

## Exceptions

```{eval-rst}
.. automodule:: espncricinfo.exceptions
   :members:
```
