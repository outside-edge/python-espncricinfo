# python-espncricinfo

A Python client for ESPNCricInfo's Match API

### Description

The splendid espncricinfo.com site not only provides [individual HTML pages](http://www.espncricinfo.com/caribbean-premier-league-2015/engine/match/857713.html) of cricket matches, it also provides a [JSON representation of data](http://www.espncricinfo.com/caribbean-premier-league-2015/engine/match/857713.json) from each match. This Python library provides access to many of those JSON attributes as well as some helper functions. All you need is the match ID, which is the number at the end of a match page URL. See the Usage section for instructions, and see `match.py` for individual functions.

Disclaimer: This library is not intended for commercial use and neither it nor its creator has any affiliation with ESPNCricInfo. The [LICENSE](LICENSE.txt) for this library applies only to the code, not to the data.

### Installation

```python
pip install python-espncricinfo
```

### Usage

```python
>>> from espncricinfo.match import Match
>>> m = Match(64148)
>>> m.description()
u'England [Marylebone Cricket Club] tour of Australia, Only ODI: Australia v England at Melbourne, Jan 5, 1971'
```

### Requires

  * requests
