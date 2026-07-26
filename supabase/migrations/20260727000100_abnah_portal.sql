create table if not exists public.abnah_portal_oauth_states (
  state_hash text primary key,
  return_url text not null,
  expires_at timestamptz not null,
  created_at timestamptz not null default now()
);

create index if not exists abnah_portal_oauth_states_expires_idx
  on public.abnah_portal_oauth_states (expires_at);

create table if not exists public.abnah_portal_sessions (
  session_hash text primary key,
  email text not null default '',
  display_name text not null,
  workspace_id text not null,
  workspace_name text not null,
  organization_id text not null default '',
  access_token_ciphertext text not null,
  refresh_token_ciphertext text not null default '',
  access_token_expires_at timestamptz not null,
  session_expires_at timestamptz not null,
  created_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  revoked_at timestamptz
);

create index if not exists abnah_portal_sessions_expiry_idx
  on public.abnah_portal_sessions (session_expires_at)
  where revoked_at is null;

create table if not exists public.abnah_zoho_portal_config (
  config_key text primary key,
  version integer not null check (version > 0),
  payload jsonb not null,
  updated_at timestamptz not null default now(),
  updated_by text not null
);

alter table public.abnah_portal_oauth_states enable row level security;
alter table public.abnah_portal_sessions enable row level security;
alter table public.abnah_zoho_portal_config enable row level security;

revoke all on public.abnah_portal_oauth_states from anon, authenticated;
revoke all on public.abnah_portal_sessions from anon, authenticated;
revoke all on public.abnah_zoho_portal_config from anon, authenticated;

grant all on public.abnah_portal_oauth_states to service_role;
grant all on public.abnah_portal_sessions to service_role;
grant all on public.abnah_zoho_portal_config to service_role;

comment on table public.abnah_portal_oauth_states is
  'One-time hashes for the ABNAH Zoho OAuth authorization flow.';
comment on table public.abnah_portal_sessions is
  'Opaque ABNAH portal sessions. Zoho tokens are encrypted before storage.';
comment on table public.abnah_zoho_portal_config is
  'Versioned map of secured Zoho report URLs. Contains no report rows or credentials.';
