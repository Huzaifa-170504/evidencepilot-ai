import { FormEvent, useState } from "react";

import { supabase, supabaseConfigured } from "../lib/supabase";

interface AuthPanelProps {
  onDemo: () => void;
}

export function AuthPanel({ onDemo }: AuthPanelProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [message, setMessage] = useState("");
  const [working, setWorking] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!supabase) return;
    setWorking(true);
    setMessage("");
    const result =
      mode === "signin"
        ? await supabase.auth.signInWithPassword({ email, password })
        : await supabase.auth.signUp({ email, password });
    setWorking(false);
    if (result.error) setMessage(result.error.message);
    else if (mode === "signup") setMessage("Account created. Check your email if confirmation is enabled.");
  }

  return (
    <section className="auth-screen">
      <div className="auth-card">
        <span className="phase-badge">Evidence-first AI research</span>
        <h1>EvidencePilot AI</h1>
        <p>
          Coordinate specialist agents, inspect every source, upload private PDFs, and export a
          claim-checked technical report.
        </p>
        {supabaseConfigured ? (
          <form onSubmit={submit}>
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              minLength={8}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
            {message && <p className="form-message">{message}</p>}
            <button className="run-button" type="submit" disabled={working}>
              {working ? "Please wait…" : mode === "signin" ? "Sign in" : "Create account"}
            </button>
            <button
              className="text-button"
              type="button"
              onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
            >
              {mode === "signin" ? "Create a free account" : "Already have an account? Sign in"}
            </button>
          </form>
        ) : (
          <div className="configuration-note">
            Supabase public configuration is not present in this build. The recruiter snapshot still works.
          </div>
        )}
        <div className="auth-divider"><span>or</span></div>
        <button className="demo-button" type="button" onClick={onDemo}>Try the recruiter demo</button>
        <small>Do not upload confidential, medical, legal, or classified material.</small>
      </div>
    </section>
  );
}
