# Calculates entropy and information gain used to evaluate candidate splits during tree building.

import math
from typing import List
from backend.models.data_row import DataRow


def entropy(rows: List[DataRow]) -> float:

    # empty partition has no disorder, and avoids log(0)
    if not rows:
        return 0

    total = len(rows)

    counts: dict = {}
    for row in rows:
        counts[row.outcome] = counts.get(row.outcome, 0) + 1

    # -Σ p*log2(p)
    result: float = 0
    for count in counts.values():
        prob = count / total
        result -= prob * math.log2(prob)
    return result


def information_gain(parent: List[DataRow], left: List[DataRow], right: List[DataRow]) -> float:

    # a split that empties one side gains nothing and would divide by zero
    if not left or not right:
        return 0

    total = len(parent)
    left_weight = len(left) / total
    right_weight = len(right) / total
    weighted_child_entropy = (left_weight * entropy(left)) + (right_weight * entropy(right))

    return entropy(parent) - weighted_child_entropy
