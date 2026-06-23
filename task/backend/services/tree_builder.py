# Recursively builds the decision tree and provides the predict function for classifying new rows.

from typing import List, Optional
from backend.models.data_row import DataRow
from backend.models.tree_node import TreeNode
from backend.services.split_finder import find_best_split, SplitResult

# list wrapper so the int is mutable from within nested calls
_node_counter: list = [0]


def _next_id() -> str:
    _node_counter[0] += 1
    return "node_{}".format(_node_counter[0])


def _class_distribution(rows: List[DataRow]) -> dict:
    dist: dict = {}
    for row in rows:
        dist[row.outcome] = dist.get(row.outcome, 0) + 1
    return dist


def _majority_class(rows: List[DataRow]) -> Optional[str]:
    dist = _class_distribution(rows)
    best_class = None
    best_count = -1
    for class_name, count in dist.items():
        if count > best_count:
            best_count = count
            best_class = class_name
    return best_class


def _make_leaf(rows: List[DataRow]) -> TreeNode:
    return TreeNode(
        is_leaf=True,
        node_id=_next_id(),
        total_rows=len(rows),
        class_distribution=_class_distribution(rows),
        predicted_class=_majority_class(rows),
    )


def _remaining_features(features: List[str], used_feature: str) -> List[str]:
    return [feat for feat in features if feat != used_feature]


def _unique_outcomes(rows: List[DataRow]) -> set:
    return {row.outcome for row in rows}


def _build_internal_node(
    rows: List[DataRow],
    features: List[str],
    max_depth: int,
    min_samples_split: int,
    depth: int,
    split: SplitResult,
) -> TreeNode:
    # numerical features can split again at a different threshold; categorical ones are spent
    if split[3] is None:
        remaining = features
    else:
        remaining = _remaining_features(features, split[0])

    left_child = build_tree(split[4], remaining, max_depth, min_samples_split, depth + 1)
    right_child = build_tree(split[5], remaining, max_depth, min_samples_split, depth + 1)

    return TreeNode(
        is_leaf=False,
        node_id=_next_id(),
        total_rows=len(rows),
        class_distribution=_class_distribution(rows),
        feature=split[0],
        condition=split[1],
        threshold=split[2],
        split_value=split[3],
        left=left_child,
        right=right_child,
    )


def build_tree(
    rows: List[DataRow],
    features: Optional[List[str]] = None,
    max_depth: int = 5,
    min_samples_split: int = 2,
    _depth: int = 0,
) -> TreeNode:
    # reset so node IDs start from 1 for each new tree
    if _depth == 0:
        _node_counter[0] = 0

    if features is None:
        features = ["sleep", "meetings", "weekends", "stress"]

    if len(rows) < min_samples_split:
        return _make_leaf(rows)

    # pure node — nothing to split on
    if len(_unique_outcomes(rows)) == 1:
        return _make_leaf(rows)

    # depth/feature budget exhausted, take the majority class
    if _depth >= max_depth or not features:
        return _make_leaf(rows)

    split = find_best_split(rows, features)

    if split is None:
        return _make_leaf(rows)

    return _build_internal_node(rows, features, max_depth, min_samples_split, _depth, split)


def predict(node: TreeNode, row: DataRow) -> tuple:
    path: list = []
    current: Optional[TreeNode] = node

    # iterative walk instead of recursion to avoid hitting Python's call stack limit on deep trees
    while current is not None and not current.is_leaf:
        path.append(current.node_id)
        assert current.feature is not None
        val = getattr(row, current.feature)

        # categorical: left branch is the matching value; numerical: left is ≤ threshold
        if current.threshold is None:
            go_left = str(val) == current.split_value
        else:
            go_left = float(val) <= current.threshold

        if go_left:
            current = current.left
        else:
            current = current.right

    assert current is not None
    path.append(current.node_id)
    return current.predicted_class, path


def tree_depth(node: TreeNode) -> int:
    if node.is_leaf:
        return 0
    assert node.left is not None and node.right is not None
    return 1 + max(tree_depth(node.left), tree_depth(node.right))


def leaf_count(node: TreeNode) -> int:
    if node.is_leaf:
        return 1
    assert node.left is not None and node.right is not None
    return leaf_count(node.left) + leaf_count(node.right)
