import { createClient } from "@supabase/supabase-js";

// Vite only inlines VITE_-prefixed vars, and only at build time -- so if set,
// these must be present wherever the app is built (locally: .env.local,
// gitignored; on Netlify: Site configuration -> Environment variables,
// followed by a fresh deploy -- adding the vars does NOT retroactively fix
// an already-built deploy).
//
// If they're absent, we fall back to this project's real values below
// instead of failing. That's a deliberate choice, not a shortcut: the
// anon/publishable key is *designed* to be public -- it can only do what Row
// Level Security on each table allows (see supabase/schema.sql), the same
// way a Firebase web config or a Stripe publishable key is meant to ship in
// client bundles. Env vars remain supported so a fork of this project can
// point at a different Supabase project without editing source. See
// docs/DATA-ARCHITECTURE.md. (Mirrors the VCE Chemistry app's approach,
// which this project's architecture is deliberately identical to -- see the
// build brief -- but points at Physics's own, separate Supabase project for
// clean data isolation.)
const FALLBACK_SUPABASE_URL = "https://pgrlteqvwdadnqjletld.supabase.co";
const FALLBACK_SUPABASE_ANON_KEY = "sb_publishable_1sqfXriHVEQ1-XmEx1nbhg_WvX4Diul";

const envUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const envAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

const supabaseUrl = envUrl || FALLBACK_SUPABASE_URL;
const supabaseAnonKey = envAnonKey || FALLBACK_SUPABASE_ANON_KEY;

// Kept for AuthGate/AuthContext -- always false now that there's a built-in
// fallback, but left in place (rather than ripped out) in case a fork
// clears the fallback constants above and wants the visible error screen
// back instead of a silent failure.
export const supabaseConfigError: string | null = null;
export const isSupabaseConfigured = true;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
