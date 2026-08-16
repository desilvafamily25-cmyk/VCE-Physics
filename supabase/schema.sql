-- VCE Physics Practice Platform -- Supabase schema
--
-- Run this once in the Supabase dashboard: SQL Editor -> New query -> paste
-- this whole file -> Run. It only creates the two tables that hold
-- per-student data (attempts, question_results); everything else (papers,
-- interactions, official answers, curriculum mapping) stays as static JSON
-- served from /public -- see docs/DATA-ARCHITECTURE.md.
--
-- Both tables are scoped to auth.uid() via Row Level Security, so one
-- student can never read or write another student's rows, even though the
-- client only ever holds the public anon/publishable key.
--
-- Mirrors the VCE Chemistry app's schema almost verbatim (see the brief:
-- "copy the schema pattern from the Chemistry project's supabase/schema.sql
-- almost verbatim"), with one addition from day one that Chemistry had to
-- retrofit: question_results.outcome accepts 'withdrawn' as a first-class
-- value, so a VCAA-withdrawn question can be recorded and excluded from
-- scoring without ever being forced into 'incorrect'.

-- ---- attempts -------------------------------------------------------
-- One row per (user, paper): a student has at most one in-progress/submitted
-- attempt per paper at a time (see src/routes/Attempt.tsx's "resume or
-- discard" conflict UI).
create table if not exists public.attempts (
  user_id uuid not null references auth.users (id) on delete cascade,
  paper_id text not null,
  mode text not null check (mode in ('timed', 'practice')),
  answers jsonb not null default '{}'::jsonb,
  checked jsonb not null default '{}'::jsonb,
  started_at timestamptz not null,
  last_saved_at timestamptz not null default now(),
  submitted_at timestamptz,
  writing_ends_at timestamptz,
  primary key (user_id, paper_id)
);

alter table public.attempts enable row level security;

create policy "attempts_select_own" on public.attempts
  for select using (auth.uid() = user_id);

create policy "attempts_insert_own" on public.attempts
  for insert with check (auth.uid() = user_id);

create policy "attempts_update_own" on public.attempts
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "attempts_delete_own" on public.attempts
  for delete using (auth.uid() = user_id);

-- ---- question_results ------------------------------------------------
-- One row per check/self-assessment event (append-only history), feeding
-- the Error Bank and Progress pages. Mirrors src/data/types.ts's
-- QuestionResult shape. 'withdrawn' is included in the outcome check
-- constraint from day one -- see module comment above.
create table if not exists public.question_results (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  canonical_id text not null,
  paper_id text not null,
  interaction_id text not null,
  section text not null check (section in ('A', 'B')),
  mode text not null check (mode in ('timed', 'practice')),
  student_answer text not null default '',
  outcome text not null check (outcome in ('correct', 'incorrect', 'partially_correct', 'withdrawn', 'unknown')),
  self_assessed boolean not null default false,
  checked_at timestamptz not null default now()
);

alter table public.question_results enable row level security;

create policy "question_results_select_own" on public.question_results
  for select using (auth.uid() = user_id);

create policy "question_results_insert_own" on public.question_results
  for insert with check (auth.uid() = user_id);

create index if not exists question_results_user_paper_idx
  on public.question_results (user_id, paper_id);
