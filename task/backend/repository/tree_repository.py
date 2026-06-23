# Persists the trained decision tree to disk and loads it back on demand.

import json
import os
from typing import Optional
from backend.models.tree_node import TreeNode, node_to_dict, node_from_dict

_TREE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trained_tree.json")
_TREE_PATH = os.path.normpath(_TREE_PATH)


def save_tree(tree: TreeNode) -> None:
    # creates the data dir on first run if it doesn't exist yet
    
    os.makedirs(os.path.dirname(_TREE_PATH), exist_ok=True)
    with open(_TREE_PATH, "w") as tree_file:
        json.dump(node_to_dict(tree), tree_file, indent=2)


def load_tree() -> Optional[TreeNode]:
    if not os.path.exists(_TREE_PATH):
        return None
    with open(_TREE_PATH) as tree_file:
        data = json.load(tree_file)
    return node_from_dict(data)

