# Tests for finding the best split across numerical and categorical features.

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.models.data_row import DataRow
from backend.services.entropy import information_gain
from backend.services.split_finder import find_best_split


def _row(sleep: float = 7.0, meetings: int = 5, weekends: str = "No", stress: float = 4.0, outcome: str = "Healthy") -> DataRow:
    return DataRow(sleep=sleep, meetings=meetings, weekends=weekends, stress=stress, outcome=outcome)


def test_numerical_split_finds_correct_threshold() -> None:
    healthy = [_row(stress=2.0, outcome="Healthy") for _ in range(5)]
    critical = [_row(stress=8.0, outcome="Critical condition") for _ in range(5)]
    result = find_best_split(healthy + critical, ["stress"])
    assert result is not None, "Expected a split to be found on a clearly separable stress feature"
    feature = result[0]
    threshold = result[2]
    left = result[4]
    right = result[5]
    assert feature == "stress", "Expected 'stress' to be chosen, got '{}'".format(feature)
    assert threshold is not None, "Expected a numeric threshold for a numerical feature"
    assert len(left) == 5 and len(right) == 5, (
        "Expected each side to have 5 rows, got left={} right={}".format(len(left), len(right))
    )


def test_categorical_split_finds_weekends() -> None:
    yes_rows = [_row(weekends="Yes", outcome="Critical condition") for _ in range(6)]
    no_rows = [_row(weekends="No", outcome="Healthy") for _ in range(6)]
    result = find_best_split(yes_rows + no_rows, ["weekends"])
    assert result is not None, "Expected a split to be found on a perfectly separable weekends feature"
    feature = result[0]
    split_value = result[3]
    left = result[4]
    right = result[5]
    assert feature == "weekends", "Expected 'weekends' to be chosen, got '{}'".format(feature)
    assert split_value in {"Yes", "No"}, "Expected split_value to be 'Yes' or 'No', got '{}'".format(split_value)
    assert len(left) + len(right) == 12, (
        "Expected all 12 rows to be assigned to a side, got {}".format(len(left) + len(right))
    )


def test_best_feature_chosen_over_worse_one() -> None:
    healthy = [_row(stress=2.0, meetings=3, outcome="Healthy") for _ in range(5)]
    critical = [_row(stress=9.0, meetings=3, outcome="Critical condition") for _ in range(5)]
    result = find_best_split(healthy + critical, ["meetings", "stress"])
    assert result is not None, "Expected a split to be found"
    assert result[0] == "stress", "Expected 'stress' to win, got '{}'".format(result[0])


def test_pure_set_yields_no_information_gain() -> None:
    rows = [_row(outcome="Healthy") for _ in range(8)]
    result = find_best_split(rows, ["sleep", "stress", "meetings", "weekends"])
    if result is not None:
        ig = information_gain(rows, result[4], result[5])
        assert math.isclose(ig, 0, abs_tol=1e-9), "Expected zero IG for a pure set, got {}".format(ig)


def test_returns_none_for_empty_features() -> None:
    healthy = [_row(outcome="Healthy") for _ in range(4)]
    critical = [_row(outcome="Critical condition") for _ in range(4)]
    assert find_best_split(healthy + critical, []) is None, "Expected None when the feature list is empty"
