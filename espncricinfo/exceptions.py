#!/usr/bin/env python

"""
This module contains various exceptions raised by python-espncricinfo.
"""


class NoMatchFoundError(TypeError):
    """
    Exception raised if a match_id is not valid or does not exist.
    """
    pass

class NoScorecardError(TypeError):
    """
    Exception raised if a match has no scorecard
    """
    pass
