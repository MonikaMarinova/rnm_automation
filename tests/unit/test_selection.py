import random

import pytest

from src.models.episode import Episode, id_from_url
from src.services.selection import NoSuitableEpisodeError, select_character_ids, select_episode


def make_episode(episode_id, n_chars):
    return Episode(id=episode_id, name=f"Ep {episode_id}", code="", air_date="",
                   character_ids=tuple(range(1, n_chars + 1)))


EPISODES = [make_episode(1, 5), make_episode(2, 30), make_episode(3, 29), make_episode(4, 41)]


@pytest.mark.unit
def test_episode_from_api_extracts_character_ids():
    raw = {"id": 3, "name": "Anatomy Park", "episode": "S01E03", "air_date": "x",
           "characters": ["https://x/api/character/10", "https://x/api/character/2/"]}
    assert Episode.from_api(raw).character_ids == (10, 2)


@pytest.mark.unit
def test_id_from_url_rejects_garbage():
    with pytest.raises(ValueError):
        id_from_url("https://x/api/character/abc")


@pytest.mark.unit
def test_select_episode_only_picks_qualifying_ones():
    picked = {select_episode(EPISODES, random.Random(s), 30).id for s in range(200)}
    assert picked == {2, 4}  # 30 is inclusive, 29 is not


@pytest.mark.unit
def test_select_episode_raises_when_none_qualify():
    with pytest.raises(NoSuitableEpisodeError):
        select_episode(EPISODES, random.Random(0), 100)


@pytest.mark.unit
def test_selection_is_reproducible_with_same_seed():
    assert select_episode(EPISODES, random.Random(7), 30) == select_episode(EPISODES, random.Random(7), 30)
    episode = EPISODES[3]
    assert select_character_ids(episode, random.Random(7), 2) == select_character_ids(episode, random.Random(7), 2)


@pytest.mark.unit
def test_select_character_ids_are_distinct_and_in_episode():
    for seed in range(50):
        ids = select_character_ids(EPISODES[1], random.Random(seed), 2)
        assert len(set(ids)) == 2 and set(ids) <= set(EPISODES[1].character_ids)


@pytest.mark.unit
def test_select_character_ids_needs_enough_characters():
    with pytest.raises(ValueError):
        select_character_ids(make_episode(9, 1), random.Random(0), 2)