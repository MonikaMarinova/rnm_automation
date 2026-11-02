import random

import pytest


@pytest.mark.unit
def test_seed_is_reproducible(seed, rng):
    """Smoke test for the scaffolding: same seed => same random sequence."""
    expected = random.Random(seed)
    assert [rng.random() for _ in range(3)] == [expected.random() for _ in range(3)]