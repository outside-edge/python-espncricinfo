# python-espncricinfo

A Python 3 client for ESPN Cricinfo's match, summary and player information.

### Description

The splendid espncricinfo.com site not only provides [individual HTML pages](http://www.espncricinfo.com/caribbean-premier-league-2015/engine/match/857713.html) of cricket matches, it also provides a [JSON representation of data](http://www.espncricinfo.com/caribbean-premier-league-2015/engine/match/857713.json) from each match. This Python library provides access to many of those JSON attributes as well as some helper functions. All you need is the match ID, which is the number at the end of a match page URL. See the Usage section for instructions, and see `match.py` for individual functions.

Disclaimer: This library is not intended for commercial use and neither it nor its creator has any affiliation with ESPNCricInfo. The [LICENSE](LICENSE.txt) for this library applies only to the code, not to the data.

### Installation

```python
pip install python-espncricinfo
```

### Usage

For a summary of live matches, create an instance of the `Summary` class:

```python
>>> from espncricinfo.summary import Summary
>>> s = Summary()
>>> s.match_ids
[u'68079', u'68209', u'68081', u'61375', u'65429']
```

For individual matches, pass in the ID as a string:

```python
>>> from espncricinfo.match import Match
>>> m = Match('64148')
>>> m.description
u'England [Marylebone Cricket Club] tour of Australia, Only ODI: Australia v England at Melbourne, Jan 5, 1971'
```

A full list of methods available to an instance of the `Match` class is in [the code](https://github.com/dwillis/python-espncricinfo/blob/master/espncricinfo/match.py).

For player details, pass in the player ID (found in a player's URL - for example, [Ajinkya Rahane](http://www.espncricinfo.com/west-indies-v-india-2016/content/player/277916.html) is '277916'):

```python
>>> from espncricinfo.player import Player
>>> p = Player('277916')
>>> p.name
u'Ajinkya Rahane'
```

A full list of methods available to an instance of the `Player` class is in [the code](https://github.com/dwillis/python-espncricinfo/blob/master/espncricinfo/player.py).

### Tests

To run the tests:

```shell
python tests.py
```

### Requires

See requirements.txt
