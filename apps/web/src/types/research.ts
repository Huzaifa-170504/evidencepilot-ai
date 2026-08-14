export type ResearchDepth = "quick" | "standard" | "deep";
export type AgentStatus = "queued" | "running" | "completed" | "skipped" | "failed";
export type ClaimVerdict = "verified" | "partial" | "unsupported" | "conflicting";

export interface PlanTask {
  id: string;
  title: string;
  agent: string;
  objective: string;
  status: AgentStatus;
}

export interface AgentEvent {
  sequence: number;
  agent: string;
  status: AgentStatus;
  summary: string;
  duration_ms: number;
}

export interface Source {
  id: string;
  title: string;
  source_type: string;
  url: string | null;
  publisher: string;
  year: number;
  authors?: string[];
  doi?: string | null;
  arxiv_id?: string | null;
  document_id?: string | null;
  page_number?: number | null;
  excerpt?: string | null;
}

export interface Claim {
  id: string;
  text: string;
  verdict: ClaimVerdict;
  confidence: number;
  source_ids: string[];
  rationale?: string | null;
}

export interface RunMetrics {
  sources_found: number;
  papers_analyzed: number;
  claims_verified: number;
  agents_executed: number;
  total_duration_ms: number;
}

export interface ResearchRun {
  id: string;
  question: string;
  depth: ResearchDepth;
  status: "queued" | "running" | "completed" | "failed";
  created_at: string;
  plan: PlanTask[];
  events: AgentEvent[];
  sources: Source[];
  claims: Claim[];
  metrics: RunMetrics;
  report_markdown: string;
  demo: boolean;
  limitations?: string[];
  selected_agents?: string[];
  correlation_id?: string | null;
}

export interface ResearchRequest {
  question: string;
  depth: ResearchDepth;
}

export interface ApiResult {
  run: ResearchRun;
  connected: boolean;
}

export interface Project {
  id: string;
  owner_id: string;
  name: string;
  description: string;
  is_public_demo: boolean;
  created_at: string;
  updated_at: string;
}

export type DocumentStatus = "uploaded" | "processing" | "ready" | "failed";

export interface ResearchDocument {
  id: string;
  project_id: string;
  owner_id: string;
  filename: string;
  storage_path: string;
  mime_type: string;
  size_bytes: number;
  checksum_sha256: string | null;
  page_count: number | null;
  status: DocumentStatus;
  processing_error: string | null;
  created_at: string;
  updated_at: string;
}

export interface SavedMemory {
  id: string;
  project_id: string | null;
  owner_id: string;
  memory_type: string;
  title: string;
  content: string;
  enabled: boolean;
  created_at: string;
}
