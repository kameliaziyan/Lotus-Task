# Tests for the entropy and information gain calculations.

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.models.data_row import DataRow
from backend.services.entropy import entropy, information_gain


def _rows(outcomes: list) -> list:
    return [DataRow(sleep=7, meetings=5, weekends="No", stress=4, outcome=outcome) for outcome in outcomes]


def test_entropy_pure_set_is_zero() -> None:
    rows = _rows(["Healthy" for _ in range(10)])
    assert math.isclose(entropy(rows), 0, abs_tol=1e-9), "Expected entropy 0 for a pure set"


def test_entropy_uniform_two_classes() -> None:
    healthy = ["Healthy" for _ in range(5)]
    critical = ["Critical condition" for _ in range(5)]
    result = entropy(_rows(healthy + critical))
    assert math.isclose(result, 1.0, abs_tol=1e-9), "Expected 1.0, got {}".format(result)


def test_entropy_empty_list() -> None:
    assert math.isclose(entropy([]), 0, abs_tol=1e-9), "Expected entropy 0 for an empty list"


def test_entropy_four_equal_classes() -> None:
    outcomes = (
        ["Healthy" for _ in range(5)]
        + ["Risk of burnout" for _ in range(5)]
        + ["Vacation required" for _ in range(5)]
        + ["Critical condition" for _ in range(5)]
    )
    result = entropy(_rows(outcomes))
    assert math.isclose(result, 2.0, abs_tol=1e-9), "Expected 2.0, got {}".format(result)


def test_information_gain_perfect_split() -> None:
    healthy = ["Healthy" for _ in range(5)]
    critical = ["Critical condition" for _ in range(5)]
    parent = _rows(healthy + critical)
    left = _rows(healthy)
    right = _rows(critical)
    ig = information_gain(parent, left, right)
    assert math.isclose(ig, 1.0, abs_tol=1e-9), "Expected IG = 1.0, got {}".format(ig)


def test_information_gain_no_improvement() -> None:
    healthy = ["Healthy" for _ in range(2)]
    critical = ["Critical condition" for _ in range(2)]
    parent = _rows(healthy + critical + healthy + critical)
    left = _rows(healthy + critical)
    right = _rows(healthy + critical)
    ig = information_gain(parent, left, right)
    assert math.isclose(ig, 0, abs_tol=1e-9), "Expected IG = 0, got {}".format(ig)


def test_information_gain_empty_child_is_zero() -> None:
    healthy = ["Healthy" for _ in range(4)]
    critical = ["Critical condition" for _ in range(4)]
    parent = _rows(healthy + critical)
    ig = information_gain(parent, parent, [])
    assert math.isclose(ig, 0, abs_tol=1e-9), "Expected IG = 0 for empty child, got {}".format(ig)
