from espncricinfo.match import Match


class Summary:
    """
    Returns recent matches as a list of (series_id, match_id) tuples.

    Uses Match.get_recent_matches() which scrapes the ESPN Cricinfo
    results page via Playwright. Pass an optional date string (YYYY-MM-DD
    or DD-MM-YYYY) to get matches for a specific day; defaults to today.

    Example::

        from espncricinfo.summary import Summary
        from espncricinfo.match import Match

        for series_id, match_id in Summary().matches:
            m = Match(match_id, series_id)
            print(m.description)
    """

    def __init__(self, date=None):
        self.matches = Match.get_recent_matches(date)
