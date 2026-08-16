// Single place that decides which DataRepository implementation the app
// uses -- every route imports `repository` from here, never directly from
// localRepository/supabaseRepository, so this is the only file that needs
// to change if that decision ever changes again. See docs/DATA-ARCHITECTURE.md.
//
// The app requires a signed-in Supabase user (see src/auth/AuthGate.tsx),
// so `repository` is always the Supabase-backed one; `localRepository` is
// exported separately purely so the one-time local-progress migration
// (src/lib/migrateLocalProgress.ts) can read whatever a student accumulated
// before they had an account.
export { supabaseRepository as repository } from "./supabaseRepository";
export { localRepository } from "./localRepository";
