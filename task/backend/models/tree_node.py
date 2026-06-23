# Data model for a decision tree node, plus helpers to serialize/deserialize nodes to dicts.

from dataclasses import dataclass, field
from typing import Optional




@dataclass
class TreeNode:
    is_leaf: bool
    node_id: str

    total_rows: int = 0
    class_distribution: dict = field(default_factory=dict)

    feature: Optional[str] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    split_value: Optional[str] = None
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None

    predicted_class: Optional[str] = None


def node_to_dict(node: TreeNode) -> dict:
        result: dict = {
            "is_leaf": node.is_leaf,
            "node_id": node.node_id,
            "total_rows": node.total_rows,
            "class_distribution": node.class_distribution,
        }
        if node.is_leaf:
            result["predicted_class"] = node.predicted_class
        else:
            result["feature"] = node.feature
            result["condition"] = node.condition
            result["threshold"] = node.threshold
            result["split_value"] = node.split_value

            if node.left is None:
                result["left"] = None
            else:
                result["left"] = node_to_dict(node.left)

            if node.right is None:
                result["right"] = None
            else:
                result["right"] = node_to_dict(node.right)
        
        return result


def node_from_dict(data: dict) -> TreeNode:
     
    node = TreeNode(
          is_leaf=data["is_leaf"],
          node_id=data["node_id"],
          total_rows=data.get("total_rows", 0),
          class_distribution=data.get("class_distribution", {}),
     )
    if node.is_leaf:
          
        node.predicted_class = data.get("predicted_class")
    else:
        node.feature = data.get("feature")
        node.condition = data.get("condition")
        node.threshold = data.get("threshold")
        node.split_value = data.get("split_value")

        # recursively rebuild each subtree from the nested dict
        left_data = data.get("left")
        if left_data is None:
            node.left = None
        else:
            node.left = node_from_dict(left_data)

        right_data = data.get("right")
        if right_data is None:
            node.right = None
        else:
            node.right = node_from_dict(right_data)

    return node

        

                
                


