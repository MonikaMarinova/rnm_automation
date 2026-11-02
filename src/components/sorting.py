"""Sorting components.

Component A sorts two numbers; Component B sorts four numbers using ONLY Component A.
Neither uses sort()/sorted()/min()/max() (enforced by a test).
"""
import math
from numbers import Real
from typing import List


def _require_number(value) -> None:
    """Reject non-numbers, booleans and NaN (NaN has no meaningful ordering)."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"Expected a number, got {value!r} ({type(value).__name__})")
    if math.isnan(value):
        raise ValueError("NaN cannot be sorted")


def component_a(first: float, second: float) -> List[float]:
    """Return the two numbers in ascending order. component_a(7, 3) -> [3, 7]."""
    _require_number(first)
    _require_number(second)
    return [first, second] if first <= second else [second, first]


def component_b(first: float, second: float, third: float, fourth: float) -> List[float]:
    """Return the four numbers in ascending order, built purely from Component A.

    A 4-input sorting network, 5 calls to Component A, which is the minimum for 4 elements:

        (first, second) -> a <= b      (third, fourth) -> c <= d     # sort each pair
        (a, c)          -> lowest, x                                  # lowest is the global minimum
        (b, d)          -> y, highest                                 # highest is the global maximum
        (x, y)          -> middle_low, middle_high                    # order the two middle values
    """
    a, b = component_a(first, second)
    c, d = component_a(third, fourth)
    lowest, x = component_a(a, c)
    y, highest = component_a(b, d)
    middle_low, middle_high = component_a(x, y)
    return [lowest, middle_low, middle_high, highest]