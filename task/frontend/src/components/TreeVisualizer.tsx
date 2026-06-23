import { useCallback, useEffect, useState, type CSSProperties, type ReactElement } from "react";
import { Link } from "react-router-dom";
import ReactFlow, {
  Controls,
  MiniMap,
  useEdgesState,
  useNodesState,
} from "reactflow";
import "reactflow/dist/style.css";
import { fetchTree } from "../services/api";
import { useAppState } from "../context/AppContext";
import type { Outcome, TreeNode } from "../types";

const OUTCOME_CLASS: Record<Outcome, string> = {
  Healthy: "Healthy",
  "Risk of burnout": "Risk",
  "Vacation required": "Vacation",
  "Critical condition": "Critical",
};

interface FlowNode {
  id: string;
  position: { x: number; y: number };
  data: { label: ReactElement };
  type?: string;
}

interface FlowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  style?: CSSProperties;
  labelStyle?: CSSProperties;
  animated?: boolean;
}



const H_GAP = 200;
const V_GAP = 130;

function treeToFlow(
  root: TreeNode,
  highlightedPath: Set<string>,
): { nodes: FlowNode[]; edges: FlowEdge[] } {
  // Pass 1: assign sequential left-to-right index to every leaf
  const leafIndex = new Map<string, number>();
  let leafCounter = 0;
  function indexLeaves(node: TreeNode): void {
    if (node.is_leaf) { leafIndex.set(node.node_id, leafCounter++); return; }
    if (node.left) indexLeaves(node.left);
    if (node.right) indexLeaves(node.right);
  }
  indexLeaves(root);

  // Pass 2: compute x for every node (bottom-up)
  const xPos = new Map<string, number>();
  function computeX(node: TreeNode): void {
    if (node.is_leaf) {
      xPos.set(node.node_id, (leafIndex.get(node.node_id) ?? 0) * H_GAP);
      return;
    }
    if (node.left) computeX(node.left);
    if (node.right) computeX(node.right);
    const lx = node.left  ? (xPos.get(node.left.node_id)  ?? 0) : null;
    const rx = node.right ? (xPos.get(node.right.node_id) ?? 0) : null;
    if (lx !== null && rx !== null) xPos.set(node.node_id, (lx + rx) / 2);
    else xPos.set(node.node_id, lx ?? rx ?? 0);
  }
  computeX(root);

  // Pass 3: build React Flow arrays in a single top-down walk
  const nodes: FlowNode[] = [];
  const edges: FlowEdge[] = [];

  function walk(node: TreeNode, depth: number): void {
    const x = xPos.get(node.node_id) ?? 0;
    const y = depth * V_GAP;

    const isHighlighted = highlightedPath.has(node.node_id);
    const distLines = Object.entries(node.class_distribution)
      .map(([cls, cnt]) => `${cls}: ${cnt}`)
      .join(" · ");

    let cssClass = "rf-node ";
    if (node.is_leaf && node.predicted_class) {
      cssClass += `rf-node-${OUTCOME_CLASS[node.predicted_class]}`;
    } else {
      cssClass += "rf-node-internal";
    }
    if (isHighlighted) cssClass += " highlighted";

    nodes.push({
      id: node.node_id,
      position: { x, y },
      data: {
        label: <NodeLabel node={node} cssClass={cssClass} distLines={distLines} />,
      },
    });

    if (!node.is_leaf) {
      if (node.left) {
        const leftOnPath = highlightedPath.has(node.node_id) && highlightedPath.has(node.left.node_id);
        edges.push({
          id: `${node.node_id}->${node.left.node_id}`,
          source: node.node_id,
          target: node.left.node_id,
          label: "yes",
          animated: leftOnPath,
          style: leftOnPath
            ? { stroke: "#14919B", strokeWidth: 3 }
            : { stroke: "#cbd5e1", strokeWidth: 1.5 },
          labelStyle: leftOnPath ? { fill: "#14919B", fontWeight: 700 } : undefined,
        });
        walk(node.left, depth + 1);
      }
      if (node.right) {
        const rightOnPath = highlightedPath.has(node.node_id) && highlightedPath.has(node.right.node_id);
        edges.push({
          id: `${node.node_id}->${node.right.node_id}`,
          source: node.node_id,
          target: node.right.node_id,
          label: "no",
          animated: rightOnPath,
          style: rightOnPath
            ? { stroke: "#14919B", strokeWidth: 3 }
            : { stroke: "#cbd5e1", strokeWidth: 1.5 },
          labelStyle: rightOnPath ? { fill: "#14919B", fontWeight: 700 } : undefined,
        });
        walk(node.right, depth + 1);
      }
    }
  }
  walk(root, 0);

  return { nodes, edges };
}

function NodeLabel({
  node,
  cssClass,
  distLines,
}: {
  node: TreeNode;
  cssClass: string;
  distLines: string;
}) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      className={cssClass}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {node.is_leaf ? node.predicted_class : node.condition}
      {hovered && (
        <div className="node-tooltip">
          <strong>Rows: {node.total_rows}</strong>
          <br />
          {distLines}
        </div>
      )}
    </div>
  );
}

export default function TreeVisualizer() {
  const { predictionPath } = useAppState();
  const highlighted = new Set(predictionPath);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const loadTree = useCallback(async () => {
    try {
      const tree = await fetchTree();
      const { nodes: n, edges: e } = treeToFlow(tree, highlighted);
      setNodes(n);
      setEdges(e);
    } catch {
      // tree not ready yet — silently ignore
    }
    // highlighted is derived from predictionPath; including it would cause
    // an infinite loop since setNodes triggers onNodesChange
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setNodes, setEdges]);

  useEffect(() => { loadTree(); }, [loadTree]);

  return (
    <div className="tree-page">
      <div className="tree-toolbar">
        <Link to="/predict" className="back-link">← Try another prediction</Link>
      </div>

      <div className="tree-hint">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true" style={{ flexShrink: 0 }}>
          <circle cx="8" cy="8" r="6.75" stroke="currentColor" strokeWidth="1.5" />
          <path d="M8 7.5v3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <circle cx="8" cy="5.5" r="0.875" fill="currentColor" />
        </svg>
        Hover over any node to see how many training records reached it and their outcome breakdown.
      </div>

      <div className="tree-container" style={{ flex: 1 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          fitViewOptions={{ padding: 0.2 }}
        >
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}
