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
  url: string;
  publisher: string;
  year: number;
}

export interface Claim {
  id: string;
  text: string;
  verdict: ClaimVerdict;
  confidence: number;
  source_ids: string[];
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
}

export interface ResearchRequest {
  question: string;
  depth: ResearchDepth;
}

export interface ApiResult {
  run: ResearchRun;
  connected: boolean;
}
