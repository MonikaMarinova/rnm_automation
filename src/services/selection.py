"""Business rules for picking the episode and characters used by the tests.

Pure selection functions take an injected `random.Random`, so a seed reproduces a run
and the logic is unit-testable without network access.
"""
import random
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from src.api.client import RickAndMortyClient
from src.models.character import Character
from src.models.episode import Episode
from src.utils.logger import get_logger

log = get_logger("selection")


class NoSuitableEpisodeError(Exception):
    """No episode satisfies the minimum-characters requirement."""


def select_episode(episodes: Sequence[Episode], rng: random.Random, min_characters: int) -> Episode:
    """Random episode among those with at least `min_characters` characters."""
    qualifying = sorted((e for e in episodes if e.character_count >= min_characters), key=lambda e: e.id)
    if not qualifying:
        raise NoSuitableEpisodeError(
            f"None of {len(episodes)} episodes has at least {min_characters} characters")
    return rng.choice(qualifying)  # sorted first: same seed + same data => same pick


def select_character_ids(episode: Episode, rng: random.Random, count: int) -> List[int]:
    """`count` distinct random character ids from the episode."""
    if episode.character_count < count:
        raise ValueError(f"Episode {episode.name!r} has {episode.character_count} characters, need {count}")
    return rng.sample(sorted(episode.character_ids), count)


@dataclass(frozen=True)
class Selection:
    episode: Episode
    characters: Tuple[Character, ...]


class SelectionService:
    """Orchestrates API calls + selection rules: 1 call per episode page, then 1 call for all characters."""

    def __init__(self, client: RickAndMortyClient, rng: random.Random,
                 min_episode_characters: int, characters_to_select: int):
        self._client = client
        self._rng = rng
        self._min_characters = min_episode_characters
        self._count = characters_to_select

    def select(self) -> Selection:
        episodes = [Episode.from_api(raw) for raw in self._client.get_episodes()]
        episode = select_episode(episodes, self._rng, self._min_characters)
        ids = select_character_ids(episode, self._rng, self._count)
        raw_characters = self._client.get_characters(ids)  # single batch request
        characters = tuple(Character.from_api(raw) for raw in raw_characters)
        log.info("Selected episode %r (%d characters) and characters %s",
                 episode.name, episode.character_count, [(c.id, c.name) for c in characters])
        return Selection(episode=episode, characters=characters)