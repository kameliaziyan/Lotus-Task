export interface DataRow {
  sleep: number;
  meetings: number;
  weekends: "Yes" | "No";
  stress: number;
  outcome: Outcome;
}

export type Outcome =
  | "Healthy"
  | "Risk of burnout"
  | "Vacation required"
  | "Critical condition";

export interface TreeNode {
  is_leaf: boolean;
  node_id: string;
  total_rows: number;
  class_distribution: Record<Outcome, number>;
  // internal node
  feature?: string;
  condition?: string;
  threshold?: number;
  split_value?: string;
  left?: TreeNode;
  right?: TreeNode;
  // leaf node
  predicted_class?: Outcome;
}

export interface PredictInput {
  sleep: number;
  meetings: number;
  weekends: "Yes" | "No";
  stress: number;
}

export interface PredictionResponse {
  outcome: Outcome;
  path: string[];
}
