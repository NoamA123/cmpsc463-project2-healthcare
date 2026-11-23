import type { Dataset, GeneratorParams, PolicyInfo, SimulationRequest, SimulationResponse } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    throw new Error(typeof detail === "string" ? detail : `${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  policies: () => request<PolicyInfo[]>("/policies"),
  listDatasets: () => request<string[]>("/datasets"),
  getDataset: (name: string) => request<Dataset>(`/datasets/${encodeURIComponent(name)}`),
  generateDataset: (params: GeneratorParams) =>
    request<Dataset>("/datasets/generate", { method: "POST", body: JSON.stringify(params) }),
  simulate: (req: SimulationRequest) =>
    request<SimulationResponse>("/simulate", { method: "POST", body: JSON.stringify(req) }),
};
