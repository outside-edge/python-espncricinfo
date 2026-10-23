"""Grounds (ESPN "venues") from the ESPN core API."""

from typing import Any

from espncricinfo._core import get_json
from espncricinfo.exceptions import NoGroundError

_VENUES = "http://core.espnuk.org/v2/sports/cricket/venues"


class Ground:
    """A cricket ground. Example values are for ``Ground(56293)``."""

    #: ESPNcricinfo ground id, as in ``Match.ground_id``.
    ground_id: int
    #: ``'Adelaide Oval'``.
    name: str
    #: Short name, often the same as ``name``.
    short_name: str | None
    #: ``'Adelaide'``, or None.
    city: str | None
    #: ``'Australia'``, or None.
    country: str | None
    #: Seating capacity, or None if ESPN has none.
    capacity: int | None
    #: True for an indoor ground, or None if unknown.
    indoor: bool | None
    #: The core API venue record.
    json: dict[str, Any]

    def __init__(self, ground_id: int | str) -> None:
        """Load the ground record.

        Args:
            ground_id: ESPNcricinfo ground id, e.g. ``Match.ground_id``.
        """
        self.ground_id = int(ground_id)
        self.json = get_json(f"{_VENUES}/{self.ground_id}", NoGroundError)
        address = self.json.get("address") or {}
        self.name = self.json["fullName"]
        self.short_name = self.json.get("shortName")
        self.city = address.get("city") or None
        self.country = address.get("country") or None
        self.capacity = self.json.get("capacity") or None
        self.indoor = self.json.get("indoor")

    def __str__(self) -> str:
        """Return the ground's name."""
        return self.name

    def __repr__(self) -> str:
        """Return ``Ground(ground_id)``."""
        return f"Ground({self.ground_id})"
