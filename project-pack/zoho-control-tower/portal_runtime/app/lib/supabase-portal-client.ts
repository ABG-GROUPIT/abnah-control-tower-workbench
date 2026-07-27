import runtimeSnapshot from "@/config/supabase-portal.json";
import type {
  ZohoPortalAuthSession,
  ZohoPortalConfigEnvelope,
  ZohoPortalHandoff,
} from "./zoho-portal-types";
import type {
  PortalDemoData,
  PortalPageData,
  PortalPageId,
} from "./control-tower-portal-data";

interface SupabasePortalRuntime {
  functionBaseUrl: string;
  returnUrl: string;
}

interface PortalBackendStatus {
  configured: boolean;
  missingEnvironment?: string[];
}

const runtime = runtimeSnapshot as SupabasePortalRuntime;
const sessionStorageKey = "abnah-portal-session-v1";
const placeholderProjectRef = "YOUR_PROJECT_REF";

function validFunctionBaseUrl(value: string) {
  try {
    const url = new URL(value);
    const isSupabase =
      url.protocol === "https:" &&
      url.hostname.toLowerCase().endsWith(".supabase.co");
    const isLocal =
      url.protocol === "http:" &&
      ["127.0.0.1", "localhost"].includes(url.hostname.toLowerCase());
    return (
      (isSupabase || isLocal) &&
      url.pathname.endsWith("/functions/v1/abnah-portal")
    );
  } catch {
    return false;
  }
}

export const portalFunctionBaseUrl = runtime.functionBaseUrl
  .trim()
  .replace(/\/+$/, "");

export const portalReturnUrl = runtime.returnUrl.trim();

export function isPortalBackendConfigured() {
  return (
    !portalFunctionBaseUrl.includes(placeholderProjectRef) &&
    validFunctionBaseUrl(portalFunctionBaseUrl)
  );
}

function endpoint(path: string) {
  if (!isPortalBackendConfigured()) {
    throw new Error(
      "The Supabase portal backend URL has not been configured.",
    );
  }
  return `${portalFunctionBaseUrl}/${path.replace(/^\/+/, "")}`;
}

export function portalSignInUrl() {
  return isPortalBackendConfigured() ? endpoint("auth/start") : "";
}

function browserSessionStorage() {
  return typeof globalThis.sessionStorage === "undefined"
    ? null
    : globalThis.sessionStorage;
}

export function getPortalSessionToken() {
  return browserSessionStorage()?.getItem(sessionStorageKey) ?? "";
}

export function clearPortalSessionToken() {
  browserSessionStorage()?.removeItem(sessionStorageKey);
}

export function consumePortalCallback() {
  if (typeof globalThis.location === "undefined") {
    return { error: "", receivedSession: false };
  }

  const url = new URL(globalThis.location.href);
  const fragment = new URLSearchParams(url.hash.replace(/^#/, ""));
  const token = fragment.get("portal_session")?.trim() ?? "";
  let error = url.searchParams.get("auth_error")?.trim() ?? "";
  let receivedSession = false;
  let changed = false;

  if (token) {
    if (!/^[A-Za-z0-9_-]{40,256}$/.test(token)) {
      clearPortalSessionToken();
      error =
        "The returned portal session was malformed. Please sign in again.";
    } else {
      browserSessionStorage()?.setItem(sessionStorageKey, token);
      receivedSession = true;
    }
    fragment.delete("portal_session");
    changed = true;
  }

  if (url.searchParams.has("auth_error")) {
    url.searchParams.delete("auth_error");
    changed = true;
  }

  if (changed) {
    const nextFragment = fragment.toString();
    url.hash = nextFragment ? `#${nextFragment}` : "";
    globalThis.history?.replaceState(
      null,
      "",
      `${url.pathname}${url.search}${url.hash}`,
    );
  }

  return { error, receivedSession };
}

async function readJson<T>(response: Response, fallback: string) {
  const payload = (await response.json().catch(() => null)) as
    | T
    | { error?: string }
    | null;
  if (!response.ok) {
    const errorPayload =
      payload && typeof payload === "object"
        ? (payload as { error?: string })
        : null;
    const message =
      errorPayload?.error
        ? errorPayload.error
        : fallback;
    throw new Error(message);
  }
  if (!payload) throw new Error(fallback);
  return payload as T;
}

function authorizationHeaders(includeJson = false) {
  const token = getPortalSessionToken();
  const headers = new Headers();
  if (token) headers.set("authorization", `Bearer ${token}`);
  if (includeJson) headers.set("content-type", "application/json");
  return headers;
}

export async function getPortalBackendStatus() {
  const response = await fetch(endpoint("status"), {
    cache: "no-store",
  });
  return readJson<PortalBackendStatus>(
    response,
    "The Supabase portal backend is unavailable.",
  );
}

export async function getPortalAuthSession() {
  const token = getPortalSessionToken();
  if (!token) {
    return {
      authenticated: false,
      configured: true,
      canConfigure: false,
    } satisfies ZohoPortalAuthSession;
  }

  const response = await fetch(endpoint("session"), {
    headers: authorizationHeaders(),
    cache: "no-store",
  });
  if (response.status === 401) {
    clearPortalSessionToken();
    return {
      authenticated: false,
      configured: true,
      canConfigure: false,
    } satisfies ZohoPortalAuthSession;
  }
  return readJson<ZohoPortalAuthSession>(
    response,
    "The Zoho session could not be verified.",
  );
}

export async function getSharedPortalConfig() {
  const response = await fetch(endpoint("config"), {
    headers: authorizationHeaders(),
    cache: "no-store",
  });
  return readJson<ZohoPortalConfigEnvelope>(
    response,
    "The shared URL handoff could not be loaded.",
  );
}

export async function saveSharedPortalConfig(
  handoff: ZohoPortalHandoff,
  expectedVersion: number,
) {
  const response = await fetch(endpoint("config"), {
    method: "PUT",
    headers: authorizationHeaders(true),
    body: JSON.stringify({ handoff, expectedVersion }),
  });
  return readJson<ZohoPortalConfigEnvelope>(
    response,
    "The shared URL handoff could not be saved.",
  );
}

export async function revokePortalSession() {
  if (!getPortalSessionToken() || !isPortalBackendConfigured()) {
    clearPortalSessionToken();
    return;
  }
  await fetch(endpoint("logout"), {
    method: "POST",
    headers: authorizationHeaders(),
  }).catch(() => undefined);
  clearPortalSessionToken();
}

export async function getControlTowerPageData(
  page: PortalPageId,
  start: string,
  end: string,
) {
  const parameters = new URLSearchParams({ page, start, end });
  const response = await fetch(endpoint(`data?${parameters.toString()}`), {
    headers: authorizationHeaders(),
    cache: "no-store",
  });
  return readJson<PortalPageData>(
    response,
    "The selected control-tower data could not be loaded.",
  );
}

export async function getControlTowerDemoData() {
  const path =
    typeof globalThis.location === "undefined"
      ? "/"
      : globalThis.location.pathname.replace(
          /\/portal(?:\/index\.html)?\/?$/,
          "/",
        );
  const base = path.endsWith("/") ? path : `${path}/`;
  const response = await fetch(
    `${base}data/control-tower-portal-demo.json`,
    { cache: "no-store" },
  );
  return readJson<PortalDemoData>(
    response,
    "The validation data could not be loaded.",
  );
}
