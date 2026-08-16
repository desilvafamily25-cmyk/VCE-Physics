import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { useAuth } from "./AuthContext";
import { migrateLocalProgressIfNeeded } from "../lib/migrateLocalProgress";
import { isSupabaseConfigured, supabaseConfigError } from "../lib/supabaseClient";

/**
 * Renders the sign-in/sign-up form when there's no authenticated Supabase
 * session, and the app (children) once there is one. Also fires the
 * one-time local-progress migration right after a session appears.
 */
export function AuthGate({ children }: { children: ReactNode }) {
  const { session, user, loading } = useAuth();
  const migratedForUser = useRef<string | null>(null);

  useEffect(() => {
    if (!user) return;
    if (migratedForUser.current === user.id) return;
    migratedForUser.current = user.id;
    void migrateLocalProgressIfNeeded(user.id);
  }, [user]);

  if (!isSupabaseConfigured) {
    return <ConfigErrorScreen />;
  }

  if (loading) {
    return (
      <div className="boot-screen">
        <div className="boot-mark" aria-hidden="true">
          <svg viewBox="0 0 48 48" width="40" height="40">
            <circle cx="24" cy="24" r="4.5" fill="currentColor" />
            <ellipse cx="24" cy="24" rx="20" ry="8" fill="none" stroke="currentColor" strokeWidth="2.5" />
            <ellipse
              cx="24"
              cy="24"
              rx="20"
              ry="8"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              transform="rotate(60 24 24)"
            />
            <ellipse
              cx="24"
              cy="24"
              rx="20"
              ry="8"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              transform="rotate(120 24 24)"
            />
          </svg>
        </div>
        <p>Loading…</p>
      </div>
    );
  }

  if (!session) {
    return <SignInForm />;
  }

  return <>{children}</>;
}

function ConfigErrorScreen() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Configuration needed</h1>
        <p className="auth-error">{supabaseConfigError}</p>
      </div>
    </div>
  );
}

function SignInForm() {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState<"sign-in" | "sign-up">("sign-in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setInfo(null);
    setSubmitting(true);
    try {
      if (mode === "sign-up") {
        const result = await signUp(email, password);
        if (result.error) {
          setError(result.error);
        } else if (result.needsEmailConfirmation) {
          setInfo("Account created — check your email to confirm it, then sign in.");
          setMode("sign-in");
        }
      } else {
        const result = await signIn(email, password);
        if (result.error) setError(result.error);
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-side" aria-hidden="true">
        <div className="auth-side-glow" />
        <div className="auth-side-content">
          <div className="brand-mark brand-mark-lg">
            <OrbitIcon />
            <span>VCE Physics 50</span>
          </div>
          <h2>Practice like it's the real exam.</h2>
          <p>
            Every real VCAA past paper, rendered exactly as printed, with official examination-report answers,
            topic-tagged drills and a formula sheet a tap away.
          </p>
          <ul className="auth-side-points">
            <li>Timed Mode with a wall-clock countdown that survives a refresh</li>
            <li>Practice Mode with official marking guides, not guesses</li>
            <li>Progress tracked by Area of Study, so you know exactly what to revise</li>
          </ul>
        </div>
      </div>
      <form className="auth-card" onSubmit={handleSubmit}>
        <div className="brand-mark auth-card-brand">
          <OrbitIcon />
          <span>VCE Physics 50</span>
        </div>
        <p className="page-intro">{mode === "sign-in" ? "Welcome back — sign in to continue" : "Create your free account"}</p>

        {error && <p className="auth-error">{error}</p>}
        {info && <p className="auth-info">{info}</p>}

        <label className="auth-field">
          <span>Email</span>
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        <label className="auth-field">
          <span>Password</span>
          <input
            type="password"
            required
            minLength={6}
            autoComplete={mode === "sign-in" ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
          {submitting ? "Please wait…" : mode === "sign-in" ? "Sign in" : "Create account"}
        </button>

        <button
          type="button"
          className="btn btn-ghost btn-block"
          onClick={() => {
            setMode(mode === "sign-in" ? "sign-up" : "sign-in");
            setError(null);
            setInfo(null);
          }}
        >
          {mode === "sign-in" ? "Need an account? Sign up" : "Already have an account? Sign in"}
        </button>
      </form>
    </div>
  );
}

export function OrbitIcon() {
  return (
    <svg viewBox="0 0 48 48" width="24" height="24" aria-hidden="true">
      <circle cx="24" cy="24" r="4.5" fill="currentColor" />
      <ellipse cx="24" cy="24" rx="20" ry="8" fill="none" stroke="currentColor" strokeWidth="3" />
      <ellipse cx="24" cy="24" rx="20" ry="8" fill="none" stroke="currentColor" strokeWidth="3" transform="rotate(60 24 24)" />
      <ellipse cx="24" cy="24" rx="20" ry="8" fill="none" stroke="currentColor" strokeWidth="3" transform="rotate(120 24 24)" />
    </svg>
  );
}
