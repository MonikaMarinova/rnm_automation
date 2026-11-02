import pytest

from src.models.character import Character

RICK = {
    "id": 1, "name": "Rick Sanchez", "status": "Alive", "species": "Human", "type": "",
    "gender": "Male",
    "origin": {"name": "Earth (C-137)", "url": "https://rickandmortyapi.com/api/location/1"},
    "location": {"name": "Citadel of Ricks", "url": "https://rickandmortyapi.com/api/location/3"},
    "image": "https://rickandmortyapi.com/api/character/avatar/1.jpeg",
    "episode": ["https://rickandmortyapi.com/api/episode/1"],
    "url": "https://rickandmortyapi.com/api/character/1",
    "created": "2017-11-04T18:48:46.250Z",
}
MORTY = {**RICK, "id": 2, "name": "Morty Smith",
         "origin": {"name": "unknown", "url": ""}}


@pytest.mark.unit
def test_from_api_maps_all_fields():
    rick = Character.from_api(RICK)
    assert (rick.id, rick.name, rick.status, rick.species) == (1, "Rick Sanchez", "Alive", "Human")
    assert rick.location.name == "Citadel of Ricks"
    assert rick.origin.url.endswith("/location/1")
    assert rick.episode_urls == ("https://rickandmortyapi.com/api/episode/1",)


@pytest.mark.unit
def test_from_api_tolerates_missing_optional_fields():
    character = Character.from_api({"id": 7, "name": "Abadango Cluster Princess"})
    assert character.location.name == "" and character.episode_urls == ()


@pytest.mark.unit
def test_from_api_rejects_payload_without_id():
    with pytest.raises(ValueError, match="id"):
        Character.from_api({"name": "No Id"})


@pytest.mark.unit
def test_introduction_matches_task_example():
    assert Character.from_api(RICK).introduction() == \
        "Hi! I'm Rick Sanchez, My ID is 1, I'm from Earth (C-137)."


@pytest.mark.unit
def test_hello_appends_for_multiple_characters(tmp_path):
    target = tmp_path / "intro.txt"
    for data in (RICK, MORTY):  # same method, no duplicated code per character
        Character.from_api(data).hello(target)
    assert target.read_text(encoding="utf-8").splitlines() == [
        "Hi! I'm Rick Sanchez, My ID is 1, I'm from Earth (C-137).",
        "Hi! I'm Morty Smith, My ID is 2, I'm from unknown.",
    ]


@pytest.mark.unit
def test_hello_can_overwrite(tmp_path):
    target = tmp_path / "intro.txt"
    Character.from_api(RICK).hello(target)
    Character.from_api(MORTY).hello(target, append=False)
    assert target.read_text(encoding="utf-8").count("\n") == 1