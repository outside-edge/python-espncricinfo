# python-espncricinfo

A Python 3 client for ESPNCricinfo's match, summary and player information.

### Description

The splendid espncricinfo.com site not only provides [individual HTML pages](http://www.espncricinfo.com/caribbean-premier-league-2015/engine/match/857713.html) of cricket matches, it also provides a [JSON representation of data](http://www.espncricinfo.com/caribbean-premier-league-2015/engine/match/857713.json) from each match. This Python library provides access to many of those JSON attributes as well as some helper functions. All you need is the match ID, which is the number at the end of a match page URL. See the Usage section for instructions, and see `match.py` for individual functions.

Disclaimer: This library is not intended for commercial use and neither it nor its creator has any affiliation with ESPNCricInfo. The [LICENSE](LICENSE.txt) for this library applies only to the code, not to the data.

The current version of this library is 0.5.0. It is very much a work in progress, and bug reports and feature requests are welcomed.

### Installation

```python
pip3 install python-espncricinfo
```

### Usage

For a summary of live matches, create an instance of the `Summary` class:

```python
>>> from espncricinfo.summary import Summary
>>> s = Summary()
>>> s.match_ids
['68079', '68209', '68081', '61375', '65429']
```

For individual matches, pass in the ID as a string:

```python
>>> from espncricinfo.match import Match
>>> m = Match('64148')
>>> m.description
'England [Marylebone Cricket Club] tour of Australia, Only ODI: Australia v England at Melbourne, Jan 5, 1971'
```

More recent matches will have more methods available to them (for older matches, those methods will return `None`). A full list of methods available to an instance of the `Match` class is in [the code](https://github.com/dwillis/python-espncricinfo/blob/master/espncricinfo/match.py).

For player details, pass in the player ID (found in a player's URL - for example, [Ajinkya Rahane](http://www.espncricinfo.com/west-indies-v-india-2016/content/player/277916.html) is '277916'):

```python
>>> from espncricinfo.player import Player
>>> p = Player('277916')
>>> p.name
'Ajinkya Rahane'
```

A full list of methods available to an instance of the `Player` class is in [the code](https://github.com/dwillis/python-espncricinfo/blob/master/espncricinfo/player.py).

For series (or league) details, pass in the series ID (found in a match URL, for example, [India's 2018 tour of England](http://www.espncricinfo.com/series/18018/game/1119549/england-vs-india-1st-test-ind-in-eng-2018) is '18018'):

```python
>>> from espncricinfo.series import Series
>>> s = Series('18018')
>>> s.name
'India tour of Ireland and England 2018'
```

### Tests

To run the tests:

```shell
python tests.py
```

### Requirements

See requirements.txt
