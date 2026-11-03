import ast
import inspect
import itertools
import random

import pytest

from src.components import sorting
from src.components.sorting import component_a, component_b

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------- Component A

@pytest.mark.parametrize("args, expected", [
    ((7, 3), [3, 7]),            # example from the task
    ((3, 7), [3, 7]),            # already ordered
    ((5, 5), [5, 5]),            # equal values
    ((-2, -9), [-9, -2]),        # negatives
    ((0, -1), [-1, 0]),
    ((2.5, 1.5), [1.5, 2.5]),    # floats
    ((1, 0.5), [0.5, 1]),        # mixed int/float
])
def test_component_a(args, expected):
    assert component_a(*args) == expected


@pytest.mark.parametrize("bad", ["3", None, [1], True])
def test_component_a_rejects_non_numbers(bad):
    with pytest.raises(TypeError):
        component_a(bad, 1)


def test_component_a_rejects_nan():
    with pytest.raises(ValueError):
        component_a(float("nan"), 1)


# ---------------------------------------------------------------- Component B

@pytest.mark.parametrize("args, expected", [
    ((4, 3, 2, 1), [1, 2, 3, 4]),        # reversed
    ((1, 2, 3, 4), [1, 2, 3, 4]),        # sorted
    ((2, 1, 4, 3), [1, 2, 3, 4]),        # pairs swapped
    ((9, -1, 5, 0), [-1, 0, 5, 9]),
    ((2, 2, 1, 1), [1, 1, 2, 2]),        # duplicates
    ((7, 7, 7, 7), [7, 7, 7, 7]),
    ((0.5, -3, 2, 1.25), [-3, 0.5, 1.25, 2]),
])
def test_component_b(args, expected):
    assert component_b(*args) == expected


def test_component_b_handles_every_permutation_and_duplicate_pattern():
    """Exhaustive over a small domain: 5^4 inputs, covers all orderings incl. ties."""
    for args in itertools.product(range(5), repeat=4):
        assert component_b(*args) == sorted(args), f"failed for {args}"


def test_component_b_matches_builtin_sort_on_random_input():
    rng = random.Random(1234)  # fixed seed: deterministic unit test
    for _ in range(500):
        args = [rng.uniform(-1000, 1000) for _ in range(4)]
        assert component_b(*args) == sorted(args)


# ------------------------------------------- design constraints from the task

def test_component_b_uses_only_component_a(monkeypatch):
    """B must delegate every comparison to A: exactly 5 two-argument calls."""
    calls = []

    def spy(first, second):
        calls.append((first, second))
        return component_a(first, second)

    monkeypatch.setattr(sorting, "component_a", spy)
    assert sorting.component_b(4, 3, 2, 1) == [1, 2, 3, 4]
    assert len(calls) == 5


def test_sorting_module_does_not_use_builtin_sorting():
    """The task forbids sort(); also keep min/max out so A is the only ordering logic."""
    forbidden = {"sort", "sorted", "min", "max"}
    tree = ast.parse(inspect.getsource(sorting))
    used = {
        node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute))
    }
    assert not used & forbidden, f"Forbidden calls found: {used & forbidden}"