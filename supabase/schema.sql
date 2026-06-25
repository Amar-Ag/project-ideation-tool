-- Zoomcamp Project Ideation Tool — Supabase Schema
-- Run this in the Supabase SQL Editor after creating your project.

-- Sessions table
create table if not exists sessions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users(id) on delete cascade not null,
    mode text check (mode in ('personal', 'domain', 'both')) default null,
    status text check (status in ('active', 'completed')) default 'active',
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Messages table (stores raw conversation for display + LLM context rebuild)
create table if not exists messages (
    id uuid primary key default gen_random_uuid(),
    session_id uuid references sessions(id) on delete cascade not null,
    role text check (role in ('user', 'assistant')) not null,
    content text not null,
    created_at timestamptz default now()
);

-- Briefs table (generated project cards)
create table if not exists briefs (
    id uuid primary key default gen_random_uuid(),
    session_id uuid references sessions(id) on delete cascade not null,
    problem_statement text,
    project_title text,
    project_card text,
    interview_line text,
    created_at timestamptz default now()
);

-- Indexes for performance
create index if not exists idx_sessions_user_id on sessions(user_id);
create index if not exists idx_messages_session_id on messages(session_id);
create index if not exists idx_messages_session_created on messages(session_id, created_at);
create index if not exists idx_briefs_session_id on briefs(session_id);

-- Row Level Security
alter table sessions enable row level security;
alter table messages enable row level security;
alter table briefs enable row level security;

-- Users can only see their own data
create policy "Users see own sessions"
    on sessions for all
    using (auth.uid() = user_id);

create policy "Users see own messages"
    on messages for all
    using (session_id in (
        select id from sessions where user_id = auth.uid()
    ));

create policy "Users see own briefs"
    on briefs for all
    using (session_id in (
        select id from sessions where user_id = auth.uid()
    ));

-- Auto-update updated_at on sessions
create or replace function update_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger sessions_updated_at
    before update on sessions
    for each row
    execute function update_updated_at();
