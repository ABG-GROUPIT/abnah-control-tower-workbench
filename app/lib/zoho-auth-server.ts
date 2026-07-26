import type { ZohoPortalAuthSession } from "./zoho-portal-types";

const sessionCookieName = "abnah_zoho_session_v1";
const stateCookieName = "abnah_zoho_oauth_state_v1";
const oauthScopes = [
  "ZohoAnalytics.metadata.read",
  "ZohoAnalytics.data.read",
  "ZohoAnalytics.embed.read",
  "profile.userinfo.READ",
].join(",");

interface ZohoRuntimeEnvironment {
  ZOHO_OAUTH_CLIENT_ID?: string;
  ZOHO_OAUTH_CLIENT_SECRET?: string;
  ZOHO_SESSION_SECRET?: string;
  ZOHO_ALLOWED_WORKSPACE_ID?: string;
  ZOHO_OAUTH_REDIRECT_URI?: string;
  ZOHO_PORTAL_ADMIN_EMAILS?: string;
  ZOHO_ACCOUNTS_BASE_URL?: string;
  ZOHO_ANALYTICS_API_BASE_URL?: string;
  ZOHO_PROFILE_BASE_URL?: string;
}

export interface ZohoAuthConfiguration {
  configured: boolean;
  missing: string[];
  clientId: string;
  clientSecret: string;
  sessionSecret: string;
  allowedWorkspaceId: string;
  redirectUri: string;
  adminEmails: Set<string>;
  accountsBaseUrl: string;
  analyticsApiBaseUrl: string;
  profileBaseUrl: string;
}

interface ZohoPrivateSession {
  version: 1;
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  displayName: string;
  email: string;
  workspaceId: string;
  workspaceName: string;
  organizationId: string;
}

export interface ResolvedZohoSession {
  session: ZohoPrivateSession | null;
  publicSession: ZohoPortalAuthSession;
  refreshedCookie?: string;
}

interface ZohoTokenResponse {
  access_token?: string;
  refresh_token?: string;
  expires_in?: number | string;
  error?: string;
}

function cleanBaseUrl(value: string | undefined, fallback: string) {
  return (value?.trim() || fallback).replace(/\/+$/, "");
}

async function runtimeEnvironment() {
  try {
    const { env } = await import("cloudflare:workers");
    return env as unknown as ZohoRuntimeEnvironment;
  } catch {
    return (typeof process !== "undefined"
      ? process.env
      : {}) as ZohoRuntimeEnvironment;
  }
}

export async function getZohoAuthConfiguration(
  request: Request,
): Promise<ZohoAuthConfiguration> {
  const env = await runtimeEnvironment();
  const origin = new URL(request.url).origin;
  const clientId = env.ZOHO_OAUTH_CLIENT_ID?.trim() ?? "";
  const clientSecret = env.ZOHO_OAUTH_CLIENT_SECRET?.trim() ?? "";
  const sessionSecret = env.ZOHO_SESSION_SECRET?.trim() ?? "";
  const allowedWorkspaceId =
    env.ZOHO_ALLOWED_WORKSPACE_ID?.trim() ?? "";
  const redirectUri =
    env.ZOHO_OAUTH_REDIRECT_URI?.trim() ||
    `${origin}/api/zoho-auth/callback`;
  const missing = [
    ["ZOHO_OAUTH_CLIENT_ID", clientId],
    ["ZOHO_OAUTH_CLIENT_SECRET", clientSecret],
    ["ZOHO_SESSION_SECRET", sessionSecret],
    ["ZOHO_ALLOWED_WORKSPACE_ID", allowedWorkspaceId],
  ].flatMap(([name, value]) => (value ? [] : [name]));
  const adminEmails = new Set(
    (env.ZOHO_PORTAL_ADMIN_EMAILS ?? "")
      .split(/[;,]/)
      .map((email) => email.trim().toLowerCase())
      .filter(Boolean),
  );

  return {
    configured: missing.length === 0,
    missing,
    clientId,
    clientSecret,
    sessionSecret,
    allowedWorkspaceId,
    redirectUri,
    adminEmails,
    accountsBaseUrl: cleanBaseUrl(
      env.ZOHO_ACCOUNTS_BASE_URL,
      "https://accounts.zoho.in",
    ),
    analyticsApiBaseUrl: cleanBaseUrl(
      env.ZOHO_ANALYTICS_API_BASE_URL,
      "https://analyticsapi.zoho.in",
    ),
    profileBaseUrl: cleanBaseUrl(
      env.ZOHO_PROFILE_BASE_URL,
      "https://profile.zoho.in",
    ),
  };
}

function parseCookies(request: Request) {
  return Object.fromEntries(
    (request.headers.get("cookie") ?? "")
      .split(";")
      .map((part) => part.trim())
      .filter(Boolean)
      .map((part) => {
        const separator = part.indexOf("=");
        const name = separator >= 0 ? part.slice(0, separator) : part;
        const value = separator >= 0 ? part.slice(separator + 1) : "";
        return [name, decodeURIComponent(value)];
      }),
  );
}

function cookie(
  request: Request,
  name: string,
  value: string,
  maxAge: number,
) {
  const secure =
    new URL(request.url).protocol === "https:" ||
    request.headers.get("x-forwarded-proto") === "https";
  return [
    `${name}=${encodeURIComponent(value)}`,
    "Path=/",
    "HttpOnly",
    "SameSite=Lax",
    secure ? "Secure" : "",
    `Max-Age=${maxAge}`,
  ]
    .filter(Boolean)
    .join("; ");
}

function encodeBase64Url(bytes: Uint8Array) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary)
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replace(/=+$/, "");
}

function decodeBase64Url(value: string) {
  const padded = value.replaceAll("-", "+").replaceAll("_", "/");
  const binary = atob(
    padded + "=".repeat((4 - (padded.length % 4 || 4)) % 4),
  );
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

async function encryptionKey(secret: string) {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(secret),
  );
  return crypto.subtle.importKey(
    "raw",
    digest,
    { name: "AES-GCM" },
    false,
    ["encrypt", "decrypt"],
  );
}

async function encryptSession(session: ZohoPrivateSession, secret: string) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const plaintext = new TextEncoder().encode(JSON.stringify(session));
  const ciphertext = new Uint8Array(
    await crypto.subtle.encrypt(
      { name: "AES-GCM", iv },
      await encryptionKey(secret),
      plaintext,
    ),
  );
  const payload = new Uint8Array(iv.length + ciphertext.length);
  payload.set(iv);
  payload.set(ciphertext, iv.length);
  return encodeBase64Url(payload);
}

async function decryptSession(value: string, secret: string) {
  try {
    const payload = decodeBase64Url(value);
    if (payload.length < 29) return null;
    const iv = payload.slice(0, 12);
    const ciphertext = payload.slice(12);
    const plaintext = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv },
      await encryptionKey(secret),
      ciphertext,
    );
    const session = JSON.parse(
      new TextDecoder().decode(plaintext),
    ) as ZohoPrivateSession;
    return session.version === 1 ? session : null;
  } catch {
    return null;
  }
}

function randomState() {
  return encodeBase64Url(crypto.getRandomValues(new Uint8Array(32)));
}

export function createZohoAuthorization(
  request: Request,
  config: ZohoAuthConfiguration,
) {
  const state = randomState();
  const url = new URL(`${config.accountsBaseUrl}/oauth/v2/auth`);
  url.searchParams.set("scope", oauthScopes);
  url.searchParams.set("client_id", config.clientId);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("access_type", "offline");
  url.searchParams.set("prompt", "consent");
  url.searchParams.set("redirect_uri", config.redirectUri);
  url.searchParams.set("state", state);
  return {
    authorizationUrl: url.toString(),
    stateCookie: cookie(request, stateCookieName, state, 600),
  };
}

function recursivelyFindString(
  value: unknown,
  keys: Set<string>,
): string {
  if (!value || typeof value !== "object") return "";
  if (Array.isArray(value)) {
    for (const child of value) {
      const found = recursivelyFindString(child, keys);
      if (found) return found;
    }
    return "";
  }
  for (const [key, child] of Object.entries(value)) {
    if (
      keys.has(key.toLowerCase()) &&
      (typeof child === "string" || typeof child === "number")
    ) {
      return String(child);
    }
  }
  for (const child of Object.values(value)) {
    const found = recursivelyFindString(child, keys);
    if (found) return found;
  }
  return "";
}

interface WorkspaceMatch {
  workspaceId: string;
  workspaceName: string;
  organizationId: string;
}

function findWorkspace(
  value: unknown,
  workspaceId: string,
  inheritedOrganizationId = "",
): WorkspaceMatch | null {
  if (!value || typeof value !== "object") return null;
  if (Array.isArray(value)) {
    for (const child of value) {
      const found = findWorkspace(
        child,
        workspaceId,
        inheritedOrganizationId,
      );
      if (found) return found;
    }
    return null;
  }
  const candidate = value as Record<string, unknown>;
  const organizationId =
    recursivelyFindString(
      {
        orgId: candidate.orgId,
        organizationId: candidate.organizationId,
      },
      new Set(["orgid", "organizationid"]),
    ) || inheritedOrganizationId;
  const candidateId =
    candidate.workspaceId ?? candidate.workspace_id ?? candidate.id;
  if (
    (typeof candidateId === "string" || typeof candidateId === "number") &&
    String(candidateId) === workspaceId
  ) {
    const name =
      candidate.workspaceName ??
      candidate.workspace_name ??
      candidate.name ??
      "ABNAH Analytics";
    return {
      workspaceId,
      workspaceName: String(name),
      organizationId,
    };
  }
  for (const child of Object.values(candidate)) {
    const found = findWorkspace(child, workspaceId, organizationId);
    if (found) return found;
  }
  return null;
}

async function fetchWorkspaceAccess(
  accessToken: string,
  config: ZohoAuthConfiguration,
) {
  const response = await fetch(
    `${config.analyticsApiBaseUrl}/restapi/v2/workspaces`,
    {
      headers: {
        Authorization: `Zoho-oauthtoken ${accessToken}`,
      },
      cache: "no-store",
    },
  );
  const payload = (await response.json().catch(() => null)) as unknown;
  if (!response.ok) {
    throw new Error("Zoho Analytics workspace verification failed.");
  }
  const workspace = findWorkspace(payload, config.allowedWorkspaceId);
  if (!workspace) {
    throw new Error(
      "This Zoho account does not have access to the configured ABNAH workspace.",
    );
  }
  return workspace;
}

async function fetchZohoProfile(
  accessToken: string,
  config: ZohoAuthConfiguration,
) {
  try {
    const response = await fetch(
      `${config.profileBaseUrl}/api/v1/user/self/profile?include=emails,locale`,
      {
        headers: {
          Authorization: `Zoho-oauthtoken ${accessToken}`,
        },
        cache: "no-store",
      },
    );
    if (!response.ok) return { email: "", displayName: "" };
    const payload = (await response.json()) as unknown;
    return {
      email: recursivelyFindString(
        payload,
        new Set(["primary_email", "primaryemail", "email"]),
      ),
      displayName: recursivelyFindString(
        payload,
        new Set(["display_name", "displayname", "full_name", "fullname"]),
      ),
    };
  } catch {
    return { email: "", displayName: "" };
  }
}

async function requestToken(
  config: ZohoAuthConfiguration,
  values: Record<string, string>,
) {
  const response = await fetch(`${config.accountsBaseUrl}/oauth/v2/token`, {
    method: "POST",
    headers: {
      "content-type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      client_id: config.clientId,
      client_secret: config.clientSecret,
      ...values,
    }),
    cache: "no-store",
  });
  const payload = (await response.json().catch(() => ({}))) as ZohoTokenResponse;
  if (!response.ok || !payload.access_token || payload.error) {
    throw new Error(
      payload.error
        ? `Zoho OAuth failed: ${payload.error}.`
        : "Zoho OAuth token exchange failed.",
    );
  }
  return payload;
}

export async function completeZohoAuthorization(
  request: Request,
  config: ZohoAuthConfiguration,
  code: string,
  returnedState: string,
) {
  const expectedState = parseCookies(request)[stateCookieName] ?? "";
  if (!expectedState || !returnedState || expectedState !== returnedState) {
    throw new Error("Zoho sign-in state verification failed. Please retry.");
  }
  const token = await requestToken(config, {
    grant_type: "authorization_code",
    code,
    redirect_uri: config.redirectUri,
  });
  const workspace = await fetchWorkspaceAccess(
    token.access_token!,
    config,
  );
  const profile = await fetchZohoProfile(token.access_token!, config);
  const expiresIn = Number(token.expires_in ?? 3600);
  const session: ZohoPrivateSession = {
    version: 1,
    accessToken: token.access_token!,
    refreshToken: token.refresh_token ?? "",
    expiresAt: Date.now() + Math.max(300, expiresIn - 60) * 1000,
    displayName: profile.displayName || profile.email || "Zoho user",
    email: profile.email.toLowerCase(),
    workspaceId: workspace.workspaceId,
    workspaceName: workspace.workspaceName,
    organizationId: workspace.organizationId,
  };
  return {
    session,
    sessionCookie: cookie(
      request,
      sessionCookieName,
      await encryptSession(session, config.sessionSecret),
      token.refresh_token ? 60 * 60 * 24 * 30 : Math.max(300, expiresIn),
    ),
    clearStateCookie: cookie(request, stateCookieName, "", 0),
  };
}

async function refreshZohoSession(
  request: Request,
  session: ZohoPrivateSession,
  config: ZohoAuthConfiguration,
) {
  if (!session.refreshToken) return null;
  const token = await requestToken(config, {
    grant_type: "refresh_token",
    refresh_token: session.refreshToken,
  });
  const workspace = await fetchWorkspaceAccess(
    token.access_token!,
    config,
  );
  const expiresIn = Number(token.expires_in ?? 3600);
  const refreshed: ZohoPrivateSession = {
    ...session,
    accessToken: token.access_token!,
    expiresAt: Date.now() + Math.max(300, expiresIn - 60) * 1000,
    workspaceId: workspace.workspaceId,
    workspaceName: workspace.workspaceName,
    organizationId: workspace.organizationId,
  };
  return {
    session: refreshed,
    cookie: cookie(
      request,
      sessionCookieName,
      await encryptSession(refreshed, config.sessionSecret),
      60 * 60 * 24 * 30,
    ),
  };
}

function publicSession(
  session: ZohoPrivateSession | null,
  config: ZohoAuthConfiguration,
): ZohoPortalAuthSession {
  if (!session) {
    return {
      authenticated: false,
      configured: config.configured,
      canConfigure: false,
      missingEnvironment: config.missing,
    };
  }
  const normalizedEmail = session.email.toLowerCase();
  return {
    authenticated: true,
    configured: config.configured,
    canConfigure:
      config.adminEmails.size === 0 ||
      config.adminEmails.has(normalizedEmail),
    expiresAt: session.expiresAt,
    user: {
      displayName: session.displayName,
      email: session.email,
    },
    workspace: {
      id: session.workspaceId,
      name: session.workspaceName,
      organizationId: session.organizationId,
    },
  };
}

export async function resolveZohoSession(
  request: Request,
): Promise<ResolvedZohoSession> {
  const config = await getZohoAuthConfiguration(request);
  if (!config.configured) {
    return {
      session: null,
      publicSession: publicSession(null, config),
    };
  }
  const encrypted = parseCookies(request)[sessionCookieName] ?? "";
  let session = encrypted
    ? await decryptSession(encrypted, config.sessionSecret)
    : null;
  let refreshedCookie: string | undefined;
  if (session && session.expiresAt <= Date.now()) {
    try {
      const refreshed = await refreshZohoSession(request, session, config);
      session = refreshed?.session ?? null;
      refreshedCookie = refreshed?.cookie;
    } catch {
      session = null;
    }
  }
  if (
    session &&
    session.workspaceId !== config.allowedWorkspaceId
  ) {
    session = null;
  }
  return {
    session,
    publicSession: publicSession(session, config),
    refreshedCookie,
  };
}

export function clearZohoSessionCookie(request: Request) {
  return cookie(request, sessionCookieName, "", 0);
}
