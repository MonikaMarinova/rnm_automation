"""Shared fixtures. Session-scoped selection fixtures are added in later steps."""
import random

import pytest

from config.settings import settings
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
