"""Exceptions raised by python-espncricinfo."""


class MatchNotFoundError(TypeError):
    """Raised when a match_id is not valid or does not exist."""


class PlayerNotFoundError(TypeError):
    """Raised when a player_id is not valid or does not exist."""


class NoScorecardError(TypeError):
    """Raised when a match has no scorecard."""


class NoSeriesError(TypeError):
    """Raised when a series_id is not valid or does not exist."""


class NoSeasonError(TypeError):
    """Exception raised if a season does not exist."""


class NoTeamError(TypeError):
    """Exception raised if a team does not exist in a series."""
