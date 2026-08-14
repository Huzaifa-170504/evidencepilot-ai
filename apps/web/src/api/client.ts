import { createDemoRun, demoRun } from "../data/demo";
import type { ApiResult, ResearchRequest, ResearchRun } from "../types/research";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`EvidencePilot API returned ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function loadDemoWorkspace(): Promise<ApiResult> {
  try {
    const run = await request<ResearchRun>("/api/v1/demo");
    return { run, connected: true };
  } catch {
    return { run: demoRun, connected: false };
  }
}

export async function createResearchRun(payload: ResearchRequest): Promise<ApiResult> {
  try {
    const run = await request<ResearchRun>("/api/v1/research/demo", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return { run, connected: true };
  } catch {
    await new Promise((resolve) => window.setTimeout(resolve, 650));
    return { run: createDemoRun(payload.question, payload.depth), connected: false };
  }
}
