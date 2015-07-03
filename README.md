# python-espncricinfo

A Python client for ESPNCricInfo's Match API

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
