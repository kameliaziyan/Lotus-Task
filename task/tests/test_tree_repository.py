# Tests for saving and loading the trained tree to and from disk.

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch
from backend.models.tree_node import TreeNode
from backend.repository.tree_repository import save_tree, load_tree


@pytest.fixture
def leaf_node() -> TreeNode:
    return TreeNode(
        is_leaf=True,
        node_id="node_1",
        total_rows=10,
        class_distribution={"Healthy": 10},
        predicted_class="Healthy",
    )


def test_save_and_load_tree_round_trips(tmp_path: pytest.TempPathFactory, leaf_node: TreeNode) -> None:
    tree_path = str(tmp_path / "test_tree.json")
    with patch("backend.repository.tree_repository._TREE_PATH", tree_path):
        save_tree(leaf_node)
        loaded = load_tree()

    assert loaded is not None, "load_tree returned None after a successful save"
    assert loaded.is_leaf == leaf_node.is_leaf
    assert loaded.predicted_class == leaf_node.predicted_class, (
        "Expected predicted_class '{}', got '{}'".format(leaf_node.predicted_class, loaded.predicted_class)
    )
    assert loaded.total_rows == leaf_node.total_rows, (
        "Expected total_rows {}, got {}".format(leaf_node.total_rows, loaded.total_rows)
    )
    assert loaded.class_distribution == leaf_node.class_distribution
