from espncricinfo.match import Match


class Summary:
    """
    Provides a list of recent matches as :class:`~espncricinfo.match_ref.MatchRef` objects.

    Uses Match.get_recent_matches() which scrapes the ESPN Cricinfo
    results page via Playwright. Pass an optional date string (YYYY-MM-DD
    or DD-MM-YYYY) to get matches for a specific day; defaults to today.

    Example::

        from espncricinfo.summary import Summary

        for ref in Summary().matches:
            m = ref.to_match()
            print(m.description)

        # Tuple unpacking also works:
        for series_id, match_id in Summary().matches:
            print(series_id, match_id)
    """

    def __init__(self, date=None):
        self.matches = Match.get_recent_matches(date)
