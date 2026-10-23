# API reference

Each class is importable from its module, e.g.
`from espncricinfo.match import Match`. Every public attribute is typed, and the
package ships a `py.typed` marker, so type checkers and editors see the same
types shown here.

```{eval-rst}
.. currentmodule:: espncricinfo

.. autosummary::
   :nosignatures:

   match.Match
   match_ref.MatchRef
   summary.Summary
   player.Player
   series.Series
   seasons.Season
   teams.Team
```

```{toctree}
:hidden:

matches
players
series
exceptions
```
