# Tests for building the decision tree and running predictions.

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from backend.models.data_row import DataRow
from backend.models.tree_node import TreeNode
from backend.services.tree_builder import build_tree, predict, tree_depth, leaf_count


def _row(sleep: float = 7.0, meetings: int = 5, weekends: str = "No", stress: float = 4.0, outcome: str = "Healthy") -> DataRow:
    return DataRow(sleep=sleep, meetings=meetings, weekends=weekends, stress=stress, outcome=outcome)


@pytest.fixture
def simple_dataset() -> list:
    return (
        [_row(stress=2.0, outcome="Healthy") for _ in range(10)]
        + [_row(stress=9.0, outcome="Critical condition") for _ in range(10)]
    )


def test_tree_predicts_on_simple_dataset(simple_dataset: list) -> None:
    tree = build_tree(simple_dataset)
    for row in simple_dataset:
        predicted, _ = predict(tree, row)
        assert predicted == row.outcome, "Expected {}, got {}".format(row.outcome, predicted)


def test_pure_dataset_produces_single_leaf() -> None:
    rows = [_row(outcome="Healthy") for _ in range(8)]
    tree = build_tree(rows)
    assert tree.is_leaf, "Expected a single leaf node for a pure dataset"
    assert tree.predicted_class == "Healthy", (
        "Expected predicted_class 'Healthy', got '{}'".format(tree.predicted_class)
    )


def test_max_depth_is_respected(simple_dataset: list) -> None:
    rows = simple_dataset * 3
    tree = build_tree(rows, max_depth=1)
    depth = tree_depth(tree)
    assert depth <= 1, "Expected tree depth <= 1, got {}".format(depth)


def test_leaf_count_positive(simple_dataset: list) -> None:
    tree = build_tree(simple_dataset)
    count = leaf_count(tree)
    assert count >= 1, "Expected at least one leaf, got {}".format(count)


def test_predict_returns_path(simple_dataset: list) -> None:
    tree = build_tree(simple_dataset)
    _, path = predict(tree, _row(stress=2.0))
    assert isinstance(path, list), "Expected predict() to return a list as the path"
    assert len(path) >= 1, "Expected the path to contain at least one node id"


def _check_node(node: TreeNode) -> None:
    total = sum(node.class_distribution.values())
    assert total == node.total_rows, (
        "node {}: distribution sum {} != total_rows {}".format(node.node_id, total, node.total_rows)
    )
    if not node.is_leaf:
        assert node.left is not None
        assert node.right is not None
        _check_node(node.left)
        _check_node(node.right)


def test_class_distribution_sums_to_total_rows(simple_dataset: list) -> None:
    tree = build_tree(simple_dataset)
    _check_node(tree)


def test_four_class_dataset_builds_without_error() -> None:
    rows = (
        [_row(stress=2.0, sleep=8.0, outcome="Healthy") for _ in range(6)]
        + [_row(stress=5.0, sleep=6.0, outcome="Risk of burnout") for _ in range(6)]
        + [_row(stress=7.0, sleep=4.5, outcome="Vacation required") for _ in range(6)]
        + [_row(stress=9.5, sleep=3.0, outcome="Critical condition") for _ in range(6)]
    )
    tree = build_tree(rows)
    assert not tree.is_leaf or tree.predicted_class is not None, (
        "Expected a valid tree or leaf with a predicted class"
    )
