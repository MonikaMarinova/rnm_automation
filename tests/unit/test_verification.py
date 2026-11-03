import pytest

from src.models.character import Character
from src.services.verification import check_same_location

pytestmark = pytest.mark.unit


def character(char_id, name, location):
    return Character.from_api({"id": char_id, "name": name, "location": {"name": location, "url": ""}})


def test_same_location_reports_shared_place():
    check = check_same_location(character(1, "Rick Sanchez", "Citadel of Ricks"),
                                character(2, "Morty Smith", "Citadel of Ricks"))
    assert check.same
    assert check.message == "Both characters are from Citadel of Ricks."


def test_different_locations_message_names_both_characters_and_locations():
    check = check_same_location(character(495, "Crystal Poacher", "Forbodulon Prime"),
                                character(519, "Wasp Summer", "Earth (Wasp Dimension)"))
    assert not check.same
    assert check.message == (
        "Characters are from different locations: "
        "Crystal Poacher is from 'Forbodulon Prime', Wasp Summer is from 'Earth (Wasp Dimension)'")


def test_location_comparison_is_by_name_so_two_unknowns_match():
    assert check_same_location(character(1, "A", "unknown"), character(2, "B", "unknown")).same