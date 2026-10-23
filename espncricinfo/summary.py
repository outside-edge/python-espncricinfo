"""Recent-match listing."""

from datetime import date

from espncricinfo.match import Match
from espncricinfo.match_ref import MatchRef


class Summary:
    """Recent matches as :class:`~espncricinfo.match_ref.MatchRef` objects.

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

    #: The listed matches.
    matches: list[MatchRef]

    def __init__(self, date: date | str | None = None) -> None:
        """Fetch the results page for ``date`` (default: today)."""
        self.matches = Match.get_recent_matches(date)
