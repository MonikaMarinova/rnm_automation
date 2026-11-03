"""API-level verification of the randomly selected episode and characters.

Run with `-s` to see the printed episode name / character count on the console
(they are also logged and shown in the HTML report).
"""
import pytest

from config.settings import settings
from src.services.verification import check_same_location
from src.utils.logger import get_logger

log = get_logger("api-tests")
pytestmark = pytest.mark.api


def test_episode_has_enough_characters(selected_episode):
    assert selected_episode.character_count >= settings.min_episode_characters, (
        f"Episode {selected_episode.name!r} has {selected_episode.character_count} characters, "
        f"expected at least {settings.min_episode_characters}")


def test_two_distinct_characters_belong_to_episode(selected_episode, selected_characters):
    ids = [c.id for c in selected_characters]
    assert len(selected_characters) == settings.characters_to_select
    assert len(set(ids)) == len(ids), f"Characters are not distinct: {ids}"
    outside = set(ids) - set(selected_episode.character_ids)
    assert not outside, f"Characters {sorted(outside)} are not in episode {selected_episode.name!r}"


def test_characters_have_complete_information(selected_characters):
    for character in selected_characters:
        missing = [field for field in ("name", "status", "species", "gender", "image", "url")
                   if not getattr(character, field)]
        assert not missing, f"{character.name} (id={character.id}) has empty fields: {missing}"
        assert character.location.name and character.origin.name, \
            f"{character.name} (id={character.id}) has no location/origin name"


def test_characters_introduce_themselves(selected_characters):
    settings.intro_file.unlink(missing_ok=True)  # start a fresh file for this run
    for character in selected_characters:
        character.hello()
    written = settings.intro_file.read_text(encoding="utf-8").splitlines()
    assert written == [c.introduction() for c in selected_characters]


def test_selected_characters_location_comparison_is_reported(selected_characters):
    """Report the comparison without making random character selection flaky."""
    first, second = selected_characters
    check = check_same_location(first, second)
    log.info(check.message)
    print(check.message)