from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from espncricinfo.match import Match


@dataclass
class MatchRef:
    """
    A lightweight reference to an ESPN Cricinfo match.

    Stores the ``series_id`` and ``match_id`` needed to construct a
    :class:`~espncricinfo.match.Match`. Supports dict and CSV serialization
    and tuple unpacking for backward compatibility.

    Example::

        from espncricinfo.match_ref import MatchRef

        ref = MatchRef(series_id=1478874, match_id=1478914)
        series_id, match_id = ref          # tuple unpacking still works
        m = ref.to_match()                 # hydrate a full Match object
        d = ref.to_dict()                  # {"series_id": 1478874, "match_id": 1478914}
        row = ref.to_csv_row()             # ["1478874", "1478914"]
    """

    series_id: int
    match_id: int

    def __post_init__(self):
        self.series_id = int(self.series_id)
        self.match_id = int(self.match_id)

    def __iter__(self):
        """Yield series_id then match_id — enables tuple unpacking."""
        yield self.series_id
        yield self.match_id
