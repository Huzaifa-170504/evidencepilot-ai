import {
  Activity,
  BarChart3,
  BookOpenCheck,
  Bot,
  BrainCircuit,
  ChevronDown,
  CircleUserRound,
  Download,
  FileStack,
  FlaskConical,
  FolderKanban,
  Github,
  Library,
  LogOut,
  Menu,
  Network,
  Play,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import type { Session } from "@supabase/supabase-js";
import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  createProject,
  createProjectRun,
  createResearchRun,
  deleteMemory,
  listDocuments,
  listMemories,
  listProjects,
  loadDemoWorkspace,
} from "./api/client";
import { AgentTimeline } from "./components/AgentTimeline";
import { AuthPanel } from "./components/AuthPanel";
import { DocumentsPanel } from "./components/DocumentsPanel";
import { MetricCard } from "./components/MetricCard";
import { ReportView } from "./components/ReportView";
import { SourceList } from "./components/SourceList";
import { defaultQuestion, demoRun } from "./data/demo";
import { supabase, supabaseConfigured } from "./lib/supabase";
import type {
  Project,
  ResearchDepth,
  ResearchDocument,
  ResearchRun,
  SavedMemory,
} from "./types/research";

type View = "workspace" | "documents" | "sources" | "claims" | "report" | "memory" | "engineering" | "settings";

const navigation: Array<{ label: string; view: View; icon: typeof FolderKanban }> = [
  { label: "Workspace", view: "workspace", icon: FolderKanban },
  { label: "Documents", view: "documents", icon: FileStack },
  { label: "Sources", view: "sources", icon: Library },
  { label: "Claims", view: "claims", icon: BookOpenCheck },
  { label: "Memory", view: "memory", icon: BrainCircuit },
  { label: "Engineering", view: "engineering", icon: Network },
];

function downloadMarkdown(run: ResearchRun) {
  const blob = new Blob([run.report_markdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `evidencepilot-${run.id}.md`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function App() {
  const [run, setRun] = useState<ResearchRun>(demoRun);
  const [question, setQuestion] = useState(defaultQuestion);
  const [depth, setDepth] = useState<ResearchDepth>("standard");
  const [view, setView] = useState<View>("workspace");
  const [running, setRunning] = useState(false);
  const [connected, setConnected] = useState<boolean | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [demoEntered, setDemoEntered] = useState(!supabaseConfigured);
  const [session, setSession] = useState<Session | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<ResearchDocument[]>([]);
  const [memories, setMemories] = useState<SavedMemory[]>([]);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    if (!supabase) return;
    void supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      if (nextSession) setDemoEntered(true);
    });
    return () => data.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    let active = true;
    void loadDemoWorkspace().then((result) => {
      if (!active) return;
      setRun(result.run);
      setConnected(result.connected);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!session) {
      setProjects([]);
      setActiveProject(null);
      return;
    }
    void listProjects(session.access_token)
      .then((items) => {
        setProjects(items);
        setActiveProject((current) => current ?? items[0] ?? null);
      })
      .catch(() => setNotice("The API is waking up. The cached demo remains available."));
  }, [session]);

  useEffect(() => {
    if (!session || !activeProject) return;
    void Promise.all([
      listDocuments(session.access_token, activeProject.id),
      listMemories(session.access_token, activeProject.id),
    ]).then(([docs, saved]) => {
      setDocuments(docs);
      setMemories(saved);
    }).catch(() => setNotice("Project data could not be refreshed yet."));
  }, [session, activeProject]);

  const verifiedPercentage = useMemo(() => {
    if (!run.claims.length) return 0;
    const linked = run.claims.filter((claim) => claim.source_ids.length > 0 && claim.verdict !== "unsupported").length;
    return Math.round((linked / run.claims.length) * 100);
  }, [run.claims]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (question.trim().length < 12 || running) return;
    setRunning(true);
    setNotice("");
    try {
      if (session && activeProject) {
        const result = await createProjectRun(session.access_token, activeProject.id, {
          question: question.trim(),
          depth,
        });
        setRun(result);
        setConnected(true);
      } else {
        const result = await createResearchRun({ question: question.trim(), depth });
        setRun(result.run);
        setConnected(result.connected);
      }
      setView("workspace");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Research run failed.");
    } finally {
      setRunning(false);
    }
  }

  async function newProject() {
    if (!session) {
      setNotice("Sign in to create persistent projects and upload private PDFs.");
      return;
    }
    const name = window.prompt("Project name", "New research project")?.trim();
    if (!name) return;
    const project = await createProject(session.access_token, name, "EvidencePilot research workspace");
    setProjects([project, ...projects]);
    setActiveProject(project);
    setDocuments([]);
    setMemories([]);
    setView("workspace");
  }

  if (!demoEntered && !session) return <AuthPanel onDemo={() => setDemoEntered(true)} />;

  const projectName = activeProject?.name ?? "Mamba-YOLO Intelligence";

  return (
    <div className="app-shell">
      <button className="mobile-menu" type="button" aria-label="Open navigation" onClick={() => setSidebarOpen(true)}><Menu size={20} /></button>
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="brand">
          <span className="brand-mark"><Network size={22} /></span>
          <span><strong>EvidencePilot</strong><small>Research intelligence</small></span>
          <button className="sidebar-close" type="button" aria-label="Close navigation" onClick={() => setSidebarOpen(false)}><X size={19} /></button>
        </div>
        <button className="new-project" type="button" onClick={() => void newProject()}><Sparkles size={17} /> New research</button>
        <nav aria-label="Primary navigation">
          <span className="nav-label">Workspace</span>
          {navigation.map(({ label, view: target, icon: Icon }) => (
            <button className={view === target ? "active" : ""} type="button" key={target} onClick={() => { setView(target); setSidebarOpen(false); }}>
              <Icon size={17} /> {label}
              {target === "documents" && <span className="nav-badge">{documents.length}</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-project">
          <span className="nav-label">Active project</span>
          <button type="button" onClick={() => projects.length && setActiveProject(projects[(projects.indexOf(activeProject as Project) + 1) % projects.length])}>
            <span className="project-monogram">{projectName.split(/\s+/).slice(0, 2).map((word) => word[0]).join("")}</span>
            <span><strong>{projectName}</strong><small>{session ? "Supabase workspace" : "Cached public demo"}</small></span>
            <ChevronDown size={15} />
          </button>
        </div>
        <div className="sidebar-footer">
          <button type="button" onClick={() => setView("settings")}><Settings size={17} /> Settings & privacy</button>
          <div className="profile">
            <CircleUserRound size={28} />
            <span><strong>{session?.user.email ?? "Recruiter demo"}</strong><small>{session ? "Authenticated" : "Read-only snapshot"}</small></span>
            {session && <button className="icon-button" type="button" aria-label="Sign out" onClick={() => void supabase?.auth.signOut()}><LogOut size={15} /></button>}
          </div>
        </div>
      </aside>
      {sidebarOpen && <button className="scrim" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}

      <main className="main-content">
        <header className="topbar">
          <div><span className="eyebrow">Research project</span><h1>{projectName}</h1></div>
          <div className="topbar-actions">
            <span className={`connection ${connected ? "online" : "offline"}`}><span />{connected === null ? "Checking API" : connected ? "API connected" : "Cached demo"}</span>
            <a href="https://github.com/Huzaifa-170504/evidencepilot-ai" target="_blank" rel="noreferrer"><Github size={17} /> GitHub</a>
          </div>
        </header>

        {notice && <div className="global-notice" role="status">{notice}<button type="button" onClick={() => setNotice("")}><X size={15} /></button></div>}

        {view === "workspace" && (
          <>
            <section className="research-hero">
              <div className="hero-copy">
                <span className="phase-badge">Production MVP · evidence trace enabled</span>
                <h2>Direct a research department, not a chatbot.</h2>
                <p>The supervisor routes bounded specialists, records every safe action, verifies material claims, and refuses invented citation identifiers.</p>
              </div>
              <form className="research-form" onSubmit={handleSubmit}>
                <label htmlFor="research-question">Research question</label>
                <div className="question-field"><Search size={20} /><textarea id="research-question" value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} maxLength={2000} /></div>
                <div className="form-footer">
                  <div className="depth-control" aria-label="Research depth">
                    {(["quick", "standard", "deep"] as ResearchDepth[]).map((option) => <button type="button" className={depth === option ? "active" : ""} onClick={() => setDepth(option)} key={option}>{option}</button>)}
                  </div>
                  <button className="run-button" type="submit" disabled={running || question.trim().length < 12}>{running ? <Activity className="spin" size={18} /> : <Play size={18} fill="currentColor" />}{running ? "Coordinating agents" : "Start research"}</button>
                </div>
              </form>
            </section>
            <section className="metric-grid" aria-label="Research run metrics">
              <MetricCard label="Sources found" value={run.metrics.sources_found} icon={Library} detail="Canonical records" />
              <MetricCard label="Papers analyzed" value={run.metrics.papers_analyzed} icon={FlaskConical} detail="Primary literature" />
              <MetricCard label="Citation coverage" value={`${verifiedPercentage}%`} icon={ShieldCheck} detail="Evidence-linked claims" />
              <MetricCard label="Agent stages" value={run.metrics.agents_executed} icon={Bot} detail={`${run.metrics.total_duration_ms}ms trace`} />
            </section>
            <div className="view-tabs" role="tablist">
              <button className="active"><Activity size={16} /> Agent activity</button>
              <button onClick={() => setView("claims")}><BookOpenCheck size={16} /> Claims</button>
              <button onClick={() => setView("report")}><BarChart3 size={16} /> Report</button>
            </div>
            <div className="workspace-grid"><AgentTimeline plan={run.plan} events={run.events} /><SourceList sources={run.sources} /></div>
          </>
        )}

        {view === "documents" && (session && activeProject ? <DocumentsPanel accessToken={session.access_token} projectId={activeProject.id} userId={session.user.id} documents={documents} onChange={setDocuments} /> : <LockedPanel title="Private PDF research" message="Sign in and create a project to upload PDFs. The recruiter snapshot does not accept files." />)}
        {view === "sources" && <section className="standalone-panel"><SourceList sources={run.sources} /></section>}
        {view === "claims" && <ClaimsPanel run={run} />}
        {view === "report" && <ReportPanel run={run} />}
        {view === "memory" && <MemoryPanel memories={memories} signedIn={Boolean(session && activeProject)} onDelete={async (id) => { if (!session) return; await deleteMemory(session.access_token, id); setMemories(memories.filter((memory) => memory.id !== id)); }} />}
        {view === "engineering" && <EngineeringPanel />}
        {view === "settings" && <SettingsPanel session={session} />}

        <footer className="app-footer"><span>EvidencePilot AI · Built by Huzaifa Waqar Butt</span><span>{session ? "Private Supabase workspace" : "Cached recruiter snapshot"}</span></footer>
      </main>
    </div>
  );
}

function LockedPanel({ title, message }: { title: string; message: string }) {
  return <section className="panel locked-panel"><ShieldCheck size={28} /><h2>{title}</h2><p>{message}</p></section>;
}

function ClaimsPanel({ run }: { run: ResearchRun }) {
  return <section className="panel claim-panel"><div className="panel-header"><div><span className="eyebrow">Fact-check output</span><h2>Claim-evidence matrix</h2></div><span className="panel-count">{run.claims.length} material claims</span></div><div className="claim-list">{run.claims.map((claim) => <article className="claim" key={claim.id}><div className="claim-copy"><span className={`verdict ${claim.verdict}`}>{claim.verdict}</span><p>{claim.text}</p><small>Evidence: {claim.source_ids.join(", ") || "No supporting source"}</small>{claim.rationale && <small>{claim.rationale}</small>}</div><strong>{Math.round(claim.confidence * 100)}%</strong></article>)}</div></section>;
}

function ReportPanel({ run }: { run: ResearchRun }) {
  return <section className="panel report-panel"><div className="panel-header"><div><span className="eyebrow">Generated deliverable</span><h2>Referenced technical report</h2></div><div className="export-actions"><button type="button" onClick={() => downloadMarkdown(run)}><Download size={15} /> Markdown</button><button type="button" onClick={() => window.print()}><Download size={15} /> Print / PDF</button></div></div><ReportView markdown={run.report_markdown} /></section>;
}

function MemoryPanel({ memories, signedIn, onDelete }: { memories: SavedMemory[]; signedIn: boolean; onDelete: (id: string) => Promise<void> }) {
  if (!signedIn) return <LockedPanel title="Inspectable project memory" message="Sign in to inspect, disable, or delete saved long-term memory." />;
  return <section className="panel memory-panel"><div className="panel-header"><div><span className="eyebrow">User controlled</span><h2>Project memory</h2></div><span className="panel-count">{memories.length} saved items</span></div><p className="panel-intro">EvidencePilot stores concise findings and preferences—not private chain-of-thought.</p>{memories.length === 0 ? <div className="empty-state">No long-term memory has been saved.</div> : memories.map((memory) => <article className="memory-row" key={memory.id}><div><span className="verdict verified">{memory.memory_type}</span><h3>{memory.title}</h3><p>{memory.content}</p></div><button type="button" onClick={() => void onDelete(memory.id)}>Delete</button></article>)}</section>;
}

function EngineeringPanel() {
  const rows = [
    ["Orchestration", "LangGraph supervisor → conditional specialists → critic → fact checker → report"],
    ["RAG", "PyMuPDF parsing → page chunks → hashing/Gemini embeddings → pgvector + FTS → RRF"],
    ["Data", "Supabase Auth, PostgreSQL, private Storage, Realtime, pgvector, RLS"],
    ["Tools", "Tavily, arXiv, Crossref, direct Python functions, read-only MCP server"],
    ["Deployment", "GitHub Pages frontend, Render FastAPI backend, GitHub Actions CI/CD"],
    ["Fallback", "Versioned Mamba-YOLO snapshot when free providers sleep or exhaust quotas"],
  ];
  return <section className="panel engineering-panel"><div className="panel-header"><div><span className="eyebrow">Recruiter inspection</span><h2>Engineering & evaluation</h2></div><span className="panel-count">v1.0 architecture</span></div><p className="panel-intro">Agents use pretrained models with typed prompts and tools; none are trained separately. RAG indexes evidence at request time.</p><div className="engineering-grid">{rows.map(([label, value]) => <article key={label}><strong>{label}</strong><p>{value}</p></article>)}</div><div className="evaluation-strip"><span><strong>25</strong> evaluation questions</span><span><strong>0</strong> fabricated citation IDs target</span><span><strong>≥90%</strong> material claim coverage target</span><span><strong>100%</strong> cross-user denial target</span></div><a className="docs-link" href="https://github.com/Huzaifa-170504/evidencepilot-ai#readme" target="_blank" rel="noreferrer"><Github size={17} /> Open implementation and documentation</a></section>;
}

function SettingsPanel({ session }: { session: Session | null }) {
  return <section className="panel settings-panel"><div className="panel-header"><div><span className="eyebrow">Privacy and providers</span><h2>Settings</h2></div></div><div className="settings-list"><article><strong>Authentication</strong><span>{session ? `Signed in as ${session.user.email}` : "Recruiter demo; no private persistence"}</span></article><article><strong>Long-term memory</strong><span>User inspectable and deletable; enabled per authenticated profile</span></article><article><strong>Provider mode</strong><span>Deterministic fallback until Gemini and Tavily backend keys are configured</span></article><article><strong>Document privacy</strong><span>Private bucket, owner/project path policy, RLS, 10 MB and 150-page limits</span></article></div></section>;
}

export default App;
