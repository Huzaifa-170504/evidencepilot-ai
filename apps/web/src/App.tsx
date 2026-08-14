import {
  Activity,
  BarChart3,
  BookOpenCheck,
  Bot,
  BrainCircuit,
  ChevronDown,
  CircleUserRound,
  FileStack,
  FlaskConical,
  FolderKanban,
  History,
  Library,
  Menu,
  Network,
  PanelLeftClose,
  Play,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { createResearchRun, loadDemoWorkspace } from "./api/client";
import { AgentTimeline } from "./components/AgentTimeline";
import { MetricCard } from "./components/MetricCard";
import { ReportView } from "./components/ReportView";
import { SourceList } from "./components/SourceList";
import { defaultQuestion, demoRun } from "./data/demo";
import type { ResearchDepth, ResearchRun } from "./types/research";

type View = "workspace" | "claims" | "report";

const navigation = [
  { label: "Projects", icon: FolderKanban, active: true },
  { label: "History", icon: History },
  { label: "Documents", icon: FileStack },
  { label: "Sources", icon: Library },
  { label: "Memory", icon: BrainCircuit },
];

function App() {
  const [run, setRun] = useState<ResearchRun>(demoRun);
  const [question, setQuestion] = useState(defaultQuestion);
  const [depth, setDepth] = useState<ResearchDepth>("standard");
  const [view, setView] = useState<View>("workspace");
  const [running, setRunning] = useState(false);
  const [connected, setConnected] = useState<boolean | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    let active = true;
    void loadDemoWorkspace().then((result) => {
      if (!active) return;
      setRun(result.run);
      setConnected(result.connected);
    });
    return () => {
      active = false;
    };
  }, []);

  const verifiedPercentage = useMemo(() => {
    if (!run.claims.length) return 0;
    const verified = run.claims.filter((claim) => claim.verdict === "verified").length;
    return Math.round((verified / run.claims.length) * 100);
  }, [run.claims]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (question.trim().length < 12 || running) return;

    setRunning(true);
    const result = await createResearchRun({ question: question.trim(), depth });
    setRun(result.run);
    setConnected(result.connected);
    setRunning(false);
    setView("workspace");
  }

  return (
    <div className="app-shell">
      <button
        className="mobile-menu"
        type="button"
        aria-label="Open navigation"
        onClick={() => setSidebarOpen(true)}
      >
        <Menu size={20} />
      </button>

      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            <Network size={22} />
          </span>
          <span>
            <strong>EvidencePilot</strong>
            <small>Research intelligence</small>
          </span>
          <button
            className="sidebar-close"
            type="button"
            aria-label="Close navigation"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={19} />
          </button>
        </div>

        <button className="new-project" type="button">
          <Sparkles size={17} /> New research
        </button>

        <nav aria-label="Primary navigation">
          <span className="nav-label">Workspace</span>
          {navigation.map(({ label, icon: Icon, active }) => (
            <button className={active ? "active" : ""} type="button" key={label}>
              <Icon size={17} /> {label}
              {label === "Documents" && <span className="nav-badge">0</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-project">
          <span className="nav-label">Active project</span>
          <button type="button">
            <span className="project-monogram">MY</span>
            <span>
              <strong>Mamba-YOLO</strong>
              <small>Updated just now</small>
            </span>
            <ChevronDown size={15} />
          </button>
        </div>

        <div className="sidebar-footer">
          <button type="button">
            <Settings size={17} /> Settings
          </button>
          <div className="profile">
            <CircleUserRound size={28} />
            <span>
              <strong>Huzaifa Waqar Butt</strong>
              <small>Project owner</small>
            </span>
          </div>
        </div>
      </aside>

      {sidebarOpen && <button className="scrim" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">Research project</span>
            <h1>Mamba-YOLO Intelligence</h1>
          </div>
          <div className="topbar-actions">
            <span className={`connection ${connected ? "online" : "offline"}`}>
              <span />
              {connected === null ? "Checking API" : connected ? "API connected" : "Offline demo"}
            </span>
            <a href="https://github.com/Huzaifa-170504/evidencepilot-ai" target="_blank" rel="noreferrer">
              <PanelLeftClose size={17} /> Engineering
            </a>
          </div>
        </header>

        <section className="research-hero">
          <div className="hero-copy">
            <span className="phase-badge">Phase 1 · deterministic vertical slice</span>
            <h2>Direct a research department, not a chatbot.</h2>
            <p>
              Ask a technical question. The supervisor selects bounded specialists, records each action,
              verifies material claims, and produces an evidence-linked brief.
            </p>
          </div>

          <form className="research-form" onSubmit={handleSubmit}>
            <label htmlFor="research-question">Research question</label>
            <div className="question-field">
              <Search size={20} aria-hidden="true" />
              <textarea
                id="research-question"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                rows={3}
                maxLength={2000}
              />
            </div>
            <div className="form-footer">
              <div className="depth-control" aria-label="Research depth">
                {(["quick", "standard", "deep"] as ResearchDepth[]).map((option) => (
                  <button
                    type="button"
                    className={depth === option ? "active" : ""}
                    onClick={() => setDepth(option)}
                    key={option}
                  >
                    {option}
                  </button>
                ))}
              </div>
              <button className="run-button" type="submit" disabled={running || question.trim().length < 12}>
                {running ? <Activity className="spin" size={18} /> : <Play size={18} fill="currentColor" />}
                {running ? "Coordinating agents" : "Start research"}
              </button>
            </div>
          </form>
        </section>

        <section className="metric-grid" aria-label="Research run metrics">
          <MetricCard
            label="Sources found"
            value={run.metrics.sources_found}
            icon={Library}
            detail="Canonical records"
          />
          <MetricCard
            label="Papers analyzed"
            value={run.metrics.papers_analyzed}
            icon={FlaskConical}
            detail="Primary literature"
          />
          <MetricCard
            label="Claim coverage"
            value={`${verifiedPercentage}%`}
            icon={ShieldCheck}
            detail="Strictly verified"
          />
          <MetricCard
            label="Agent stages"
            value={run.metrics.agents_executed}
            icon={Bot}
            detail={`${(run.metrics.total_duration_ms / 1000).toFixed(1)}s simulated`}
          />
        </section>

        <div className="view-tabs" role="tablist" aria-label="Research views">
          <button className={view === "workspace" ? "active" : ""} onClick={() => setView("workspace")}>
            <Activity size={16} /> Live workspace
          </button>
          <button className={view === "claims" ? "active" : ""} onClick={() => setView("claims")}>
            <BookOpenCheck size={16} /> Claim matrix
          </button>
          <button className={view === "report" ? "active" : ""} onClick={() => setView("report")}>
            <BarChart3 size={16} /> Final report
          </button>
        </div>

        {view === "workspace" && (
          <div className="workspace-grid">
            <AgentTimeline plan={run.plan} events={run.events} />
            <SourceList sources={run.sources} />
          </div>
        )}

        {view === "claims" && (
          <section className="panel claim-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">Fact-check output</span>
                <h2>Claim-evidence matrix</h2>
              </div>
              <span className="panel-count">{run.claims.length} material claims</span>
            </div>
            <div className="claim-list">
              {run.claims.map((claim) => (
                <article className="claim" key={claim.id}>
                  <div className="claim-copy">
                    <span className={`verdict ${claim.verdict}`}>{claim.verdict}</span>
                    <p>{claim.text}</p>
                    <small>Evidence: {claim.source_ids.join(", ")}</small>
                  </div>
                  <strong>{Math.round(claim.confidence * 100)}%</strong>
                </article>
              ))}
            </div>
          </section>
        )}

        {view === "report" && (
          <section className="panel report-panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">Generated deliverable</span>
                <h2>Referenced technical brief</h2>
              </div>
              <span className="panel-count">Markdown export · Phase 6</span>
            </div>
            <ReportView markdown={run.report_markdown} />
          </section>
        )}

        <footer className="app-footer">
          <span>EvidencePilot AI · Built by Huzaifa Waqar Butt</span>
          <span>Deterministic mock · No provider keys required</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
