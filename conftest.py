"""Shared fixtures."""
import random

import pytest

from config.settings import settings
from src.api.client import RickAndMortyClient
from src.services.selection import Selection, SelectionService
from src.utils.logger import get_logger

log = get_logger("conftest")


def pytest_addoption(parser):
    parser.addoption("--seed", type=int, default=settings.seed,
                     help="Seed for random episode/character selection (reproducible runs).")
    parser.addoption("--headless", action="store_true", default=settings.headless,
                     help="Run Chrome headless.")


@pytest.fixture(scope="session", autouse=True)
def output_dirs():
    """Make sure output folders exist before any test writes to them."""
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.screenshots_dir.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def seed(request) -> int:
    """Seed for this run: from --seed / RM_SEED, otherwise freshly generated. Always logged."""
    value = request.config.getoption("--seed")
    if value is None:
        value = random.SystemRandom().randrange(2**32)
    log.info("Random seed for this run: %s (re-run with --seed %s to reproduce)", value, value)
    return value


@pytest.fixture(scope="session")
def rng(seed) -> random.Random:
    """Single RNG used for every random choice, so one seed reproduces the whole run."""
    return random.Random(seed)


@pytest.fixture(scope="session")
def api_client():
    with RickAndMortyClient.from_settings() as client:
        yield client


@pytest.fixture(scope="session")
def selection(api_client, rng) -> Selection:
    """Episode + two characters, selected ONCE per run and shared by API and UI tests."""
    result = SelectionService(
        api_client, rng, settings.min_episode_characters, settings.characters_to_select).select()
    print(f"Episode: {result.episode.name}")
    print(f"Characters in episode: {result.episode.character_count}")
    return result


@pytest.fixture(scope="session")
def selected_episode(selection):
    return selection.episode


@pytest.fixture(scope="session")
def selected_characters(selection):
    return selection.characters
