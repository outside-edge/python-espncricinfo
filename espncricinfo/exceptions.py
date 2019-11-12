#!/usr/bin/env python

"""
This module contains various exceptions raised by python-espncricinfo.
"""


class MatchNotFoundError(TypeError):
    """
    Exception raised if a match_id is not valid or does not exist.
    """
    pass

class PlayerNotFoundError(TypeError):
    """
    Exception raised if a player_id is not valid or does not exist.
    """
    pass

class GroundNotFoundError(TypeError):
    """
    Exception raised if a ground_id is not valid or does not exist.
    """
    pass

class NoScorecardError(TypeError):
    """
    Exception raised if a match has no scorecard
    """
    pass

class NoSeriesError(TypeError):
    """
    Exception raised if a series_id is not valid or does not exist.
    """
    pass
