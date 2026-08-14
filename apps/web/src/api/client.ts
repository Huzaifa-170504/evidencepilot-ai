import { createDemoRun, demoRun } from "../data/demo";
import type { ApiResult, ResearchRequest, ResearchRun } from "../types/research";
import type { Project, ResearchDocument, SavedMemory } from "../types/research";

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

async function authenticatedRequest<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  return request<T>(path, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      ...init?.headers,
    },
  });
}

export async function loadDemoWorkspace(): Promise<ApiResult> {
  try {
    const run = await request<ResearchRun>("/api/v1/demo");
    return { run, connected: true };
  } catch {
    return { run: demoRun, connected: false };
  }
}

export async function listProjects(token: string): Promise<Project[]> {
  return authenticatedRequest<Project[]>("/api/v1/projects", token);
}

export async function createProject(
  token: string,
  name: string,
  description = "",
): Promise<Project> {
  return authenticatedRequest<Project>("/api/v1/projects", token, {
    method: "POST",
    body: JSON.stringify({ name, description }),
  });
}

export async function listDocuments(token: string, projectId: string): Promise<ResearchDocument[]> {
  return authenticatedRequest<ResearchDocument[]>(`/api/v1/projects/${projectId}/documents`, token);
}

export async function registerDocument(
  token: string,
  projectId: string,
  payload: {
    filename: string;
    storage_path: string;
    mime_type: "application/pdf";
    size_bytes: number;
  },
): Promise<ResearchDocument> {
  return authenticatedRequest<ResearchDocument>(`/api/v1/projects/${projectId}/documents`, token, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function ingestDocument(token: string, documentId: string): Promise<{
  document: ResearchDocument;
  chunk_count: number;
  possible_scan_pages: number[];
}> {
  return authenticatedRequest(`/api/v1/documents/${documentId}/ingest`, token, { method: "POST" });
}

export async function deleteDocument(token: string, documentId: string): Promise<void> {
  await authenticatedRequest(`/api/v1/documents/${documentId}`, token, { method: "DELETE" });
}

export async function createProjectRun(
  token: string,
  projectId: string,
  payload: ResearchRequest,
): Promise<ResearchRun> {
  return authenticatedRequest<ResearchRun>(`/api/v1/projects/${projectId}/runs`, token, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listMemories(token: string, projectId: string): Promise<SavedMemory[]> {
  return authenticatedRequest<SavedMemory[]>(`/api/v1/projects/${projectId}/memories`, token);
}

export async function deleteMemory(token: string, memoryId: string): Promise<void> {
  await authenticatedRequest(`/api/v1/memories/${memoryId}`, token, { method: "DELETE" });
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
