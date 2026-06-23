# Finds the best feature and threshold to split a set of rows, for both numerical and categorical features.

from typing import Any, List, Optional, Tuple
from backend.models.data_row import DataRow
from backend.services.entropy import information_gain

# frozenset so these can't be mutated at runtime
CATEGORICAL_FEATURES: frozenset = frozenset(("weekends",))
NUMERICAL_FEATURES: frozenset = frozenset(("sleep", "meetings", "stress"))

SplitResult = Tuple[
    str, str, Optional[float], Optional[str], List[DataRow], List[DataRow]
]


def _get_value(row: DataRow, feature: str) -> Any:
    return getattr(row, feature)


def _unique_values(rows: List[DataRow], feature: str) -> set:
    return {_get_value(row, feature) for row in rows}


def _split_numerical(
    rows: List[DataRow], feature: str,
) -> Tuple[float, float, List[DataRow], List[DataRow]]:
    values = sorted(_unique_values(rows, feature))
    best: tuple = (-1.0, 0, [], [])

    # midpoints between adjacent values are the only thresholds worth testing
    for idx in range(len(values) - 1):
        threshold = (values[idx] + values[idx + 1]) / 2
        left = [row for row in rows if _get_value(row, feature) <= threshold]
        right = [row for row in rows if _get_value(row, feature) > threshold]
        ig = information_gain(rows, left, right)
        if ig > best[0]:
            best = (ig, threshold, left, right)

    return best[0], best[1], best[2], best[3]


def _compute_categorical_split(
    rows: List[DataRow], feature: str, val: Any,
) -> Tuple[float, List[DataRow], List[DataRow]]:
    left = [row for row in rows if _get_value(row, feature) == val]
    right = [row for row in rows if _get_value(row, feature) != val]
    return information_gain(rows, left, right), left, right


def _split_categorical(
    rows: List[DataRow], feature: str,
) -> Tuple[float, str, List[DataRow], List[DataRow]]:
    best: tuple = (-1.0, "", [], [])
    for val in _unique_values(rows, feature):
        ig, left, right = _compute_categorical_split(rows, feature, val)
        if ig > best[0]:
            best = (ig, val, left, right)
    return best[0], best[1], best[2], best[3]


def _update_best_numerical(
    rows: List[DataRow], feature: str, best_ig: float, best: Optional[SplitResult],
) -> Tuple[float, Optional[SplitResult]]:
    ig, threshold, left, right = _split_numerical(rows, feature)
    if ig <= best_ig or not left or not right:
        return best_ig, best
    condition = "{} <= {}".format(feature, format(threshold, ".4g"))
    return ig, (feature, condition, threshold, None, left, right)


def _update_best_categorical(
    rows: List[DataRow], feature: str, best_ig: float, best: Optional[SplitResult],
) -> Tuple[float, Optional[SplitResult]]:
    ig, val, left, right = _split_categorical(rows, feature)
    if ig <= best_ig or not left or not right:
        return best_ig, best
    condition = "{} == {}".format(feature, val)
    return ig, (feature, condition, None, val, left, right)


def find_best_split(
    rows: List[DataRow], features: List[str],
) -> Optional[SplitResult]:

    best_ig = -1.0
    best: Optional[SplitResult] = None

    for feature in features:
        if feature in NUMERICAL_FEATURES:
            best_ig, best = _update_best_numerical(rows, feature, best_ig, best)
        elif feature in CATEGORICAL_FEATURES:
            best_ig, best = _update_best_categorical(rows, feature, best_ig, best)

    return best
