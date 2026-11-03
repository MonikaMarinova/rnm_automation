"""Verification rules, kept free of pytest so both outcomes can be unit-tested deterministically."""
from dataclasses import dataclass

from src.models.character import Character


@dataclass(frozen=True)
class LocationCheck:
    same: bool
    message: str


def check_same_location(first: Character, second: Character) -> LocationCheck:
    """Compare the characters' current location by name (unknown places have no URL to compare)."""
    if first.location.name == second.location.name:
        return LocationCheck(True, f"Both characters are from {first.location.name}.")
    return LocationCheck(False, (
        f"Characters are from different locations: "
        f"{first.name} is from '{first.location.name}', "
        f"{second.name} is from '{second.location.name}'"))