import type {
  PredictInput,
  PredictionResponse,
  TreeNode,
} from "../types";

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:5001";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error((body as { error?: string }).error ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

export async function predict(input: PredictInput): Promise<PredictionResponse> {
  const res = await fetch(`${BASE_URL}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return handleResponse<PredictionResponse>(res);
}

export async function fetchTree(): Promise<TreeNode> {
  const res = await fetch(`${BASE_URL}/api/tree`);
  return handleResponse<TreeNode>(res);
}
