"""Verification rules, kept free of pytest so both outcomes can be unit-tested deterministically."""
from dataclasses import dataclass
from typing import Optional

from src.models.character import Character


@dataclass(frozen=True)
class LocationCheck:
    same: Optional[bool]
    message: str


def check_same_location(first: Character, second: Character) -> LocationCheck:
    """Compare current locations, returning None when either location is unknown."""
    first_location = first.location.name
    second_location = second.location.name
    if any(not location.strip() or location.strip().casefold() == "unknown"
           for location in (first_location, second_location)):
        return LocationCheck(
            None,
            f"Cannot verify whether {first.name} and {second.name} share a location: "
            f"at least one location is unknown "
            f"({first.name}: '{first_location}', {second.name}: '{second_location}').",
        )
    if first_location == second_location:
        return LocationCheck(True, f"Both characters are from {first_location}.")
    return LocationCheck(
        False,
        f"Characters are from different locations: "
        f"{first.name} is from '{first_location}', "
        f"{second.name} is from '{second_location}'.",
    )
