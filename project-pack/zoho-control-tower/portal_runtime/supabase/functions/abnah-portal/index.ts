import { createClient } from "npm:@supabase/supabase-js@2";
import {
  decryptSecret,
  encryptSecret,
  hashOpaqueValue,
  randomOpaqueValue,
} from "../_shared/crypto.ts";
import {
  createZohoAuthorizationUrl,
  exchangeZohoAuthorizationCode,
  fetchZohoProfile,
  fetchZohoWorkspace,
  refreshZohoAccessToken,
  type ZohoEnvironment,
} from "../_shared/zoho.ts";
import {
  fetchControlTowerPageData,
  type PortalDataPage,
} from "../_shared/zoho-data.ts";

const configKey = "production";
const maxBodyBytes = 250_000;
const sessionDays = 30;

const expectedViews = {
  p1: {
    dashboardViewName: "CT_PAGE_1_Risk_Action_Center",
    reports: {
      "p1-risk-map": "CT_P1_Outlet_Risk_Map",
      "p1-action-queue": "CT_P1_Action_Center",
      "p1-stockout-detail": "CT_P1_Stockout_Risk_Detail",
      "p1-menu-detail": "CT_P1_Menu_Impact_Detail",
      "p1-expiry-detail": "CT_P1_Expiry_Risk_Detail_Demo",
      "p1-po-mitigation": "CT_P1_Vendor_PO_Risk",
    },
  },
  p2: {
    dashboardViewName: "CT_PAGE_2_Procurement_Vendor_Capital",
    reports: {
      "p2-funnel": "CT_P2_Procurement_Funnel",
      "p2-scorecard": "CT_P2_Vendor_Scorecard",
      "p2-price-trend": "CT_P2_Ingredient_Price_Trend",
      "p2-price-movement": "CT_P2_Top_Price_Movement",
      "p2-pending-vendor": "CT_P2_Pending_By_Vendor",
      "p2-breach": "CT_P2_Expected_Delivery_Breach",
    },
  },
  p3: {
    dashboardViewName: "CT_PAGE_3_Consumption_Menu_Profitability",
    reports: {
      "p3-bridge": "CT_P3_Consumption_Bridge",
      "p3-variance": "CT_P3_Consumption_Variance",
      "p3-bcg": "CT_P3_Menu_BCG",
      "p3-heatmap": "CT_P3_Outlet_Item_Heatmap",
    },
  },
  p4: {
    dashboardViewName: "CT_PAGE_4_SCM_Explorer_Data_Quality",
    reports: {
      "p4-trend": "CT_P4_SCM_Monthly_Trend",
      "p4-quality": "CT_P4_Data_Quality_Detail",
      "p4-explorer": "CT_P4_Descriptive_Explorer",
    },
  },
} as const;

interface RuntimeEnvironment {
  configured: boolean;
  missing: string[];
  supabaseUrl: string;
  serviceRoleKey: string;
  tokenEncryptionKey: string;
  allowedOrigin: string;
  returnUrl: string;
  adminEmails: Set<string>;
  zoho: ZohoEnvironment;
}

interface SessionRow {
  session_hash: string;
  email: string;
  display_name: string;
  workspace_id: string;
  workspace_name: string;
  organization_id: string;
  access_token_ciphertext: string;
  refresh_token_ciphertext: string;
  access_token_expires_at: string;
  session_expires_at: string;
  revoked_at: string | null;
}

function cleanBaseUrl(value: string | undefined, fallback: string) {
  return (value?.trim() || fallback).replace(/\/+$/, "");
}

function loadEnvironment(): RuntimeEnvironment {
  const supabaseUrl = Deno.env.get("SUPABASE_URL")?.trim() ?? "";
  const serviceRoleKey =
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")?.trim() ?? "";
  const clientId = Deno.env.get("ZOHO_OAUTH_CLIENT_ID")?.trim() ?? "";
  const clientSecret =
    Deno.env.get("ZOHO_OAUTH_CLIENT_SECRET")?.trim() ?? "";
  const allowedWorkspaceId =
    Deno.env.get("ZOHO_ALLOWED_WORKSPACE_ID")?.trim() ?? "";
  const tokenEncryptionKey =
    Deno.env.get("ZOHO_TOKEN_ENCRYPTION_KEY")?.trim() ?? "";
  const allowedOrigin =
    Deno.env.get("PORTAL_ALLOWED_ORIGIN")?.trim().replace(/\/+$/, "") ?? "";
  const returnUrl = Deno.env.get("PORTAL_RETURN_URL")?.trim() ?? "";
  const redirectUri =
    Deno.env.get("ZOHO_OAUTH_REDIRECT_URI")?.trim() ||
    (supabaseUrl
      ? `${supabaseUrl.replace(/\/+$/, "")}/functions/v1/abnah-portal/auth/callback`
      : "");
  const required = {
    SUPABASE_URL: supabaseUrl,
    SUPABASE_SERVICE_ROLE_KEY: serviceRoleKey,
    ZOHO_OAUTH_CLIENT_ID: clientId,
    ZOHO_OAUTH_CLIENT_SECRET: clientSecret,
    ZOHO_ALLOWED_WORKSPACE_ID: allowedWorkspaceId,
    ZOHO_TOKEN_ENCRYPTION_KEY: tokenEncryptionKey,
    PORTAL_ALLOWED_ORIGIN: allowedOrigin,
    PORTAL_RETURN_URL: returnUrl,
    ZOHO_OAUTH_REDIRECT_URI: redirectUri,
  };
  const missing = Object.entries(required).flatMap(([key, value]) =>
    value ? [] : [key]
  );
  const adminEmails = new Set(
    (Deno.env.get("ZOHO_PORTAL_ADMIN_EMAILS") ?? "")
      .split(/[;,]/)
      .map((email) => email.trim().toLowerCase())
      .filter(Boolean),
  );

  return {
    configured: missing.length === 0,
    missing,
    supabaseUrl,
    serviceRoleKey,
    tokenEncryptionKey,
    allowedOrigin,
    returnUrl,
    adminEmails,
    zoho: {
      clientId,
      clientSecret,
      allowedWorkspaceId,
      redirectUri,
      accountsBaseUrl: cleanBaseUrl(
        Deno.env.get("ZOHO_ACCOUNTS_BASE_URL"),
        "https://accounts.zoho.in",
      ),
      analyticsApiBaseUrl: cleanBaseUrl(
        Deno.env.get("ZOHO_ANALYTICS_API_BASE_URL"),
        "https://analyticsapi.zoho.in",
      ),
      profileBaseUrl: cleanBaseUrl(
        Deno.env.get("ZOHO_PROFILE_BASE_URL"),
        "https://profile.zoho.in",
      ),
    },
  };
}

function corsHeaders(request: Request, environment: RuntimeEnvironment) {
  const requestOrigin = request.headers.get("origin")?.replace(/\/+$/, "") ?? "";
  const allowOrigin =
    environment.allowedOrigin || requestOrigin || "null";
  return {
    "access-control-allow-origin": allowOrigin,
    "access-control-allow-headers": "authorization, content-type",
    "access-control-allow-methods": "GET, PUT, POST, OPTIONS",
    "access-control-max-age": "86400",
    vary: "Origin",
  };
}

function json(
  request: Request,
  environment: RuntimeEnvironment,
  payload: unknown,
  status = 200,
) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      ...corsHeaders(request, environment),
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function redirect(location: string) {
  return new Response(null, {
    status: 302,
    headers: {
      location,
      "cache-control": "no-store",
      "referrer-policy": "no-referrer",
    },
  });
}

function portalErrorUrl(environment: RuntimeEnvironment, message: string) {
  const url = new URL(environment.returnUrl);
  url.searchParams.set("auth_error", message);
  return url.toString();
}

function assertAllowedOrigin(
  request: Request,
  environment: RuntimeEnvironment,
) {
  const origin = request.headers.get("origin")?.replace(/\/+$/, "") ?? "";
  if (origin && origin !== environment.allowedOrigin) {
    throw new Error("This portal origin is not allowed.");
  }
}

function database(environment: RuntimeEnvironment) {
  return createClient(
    environment.supabaseUrl,
    environment.serviceRoleKey,
    {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    },
  );
}

function routePath(request: Request) {
  const pathname = new URL(request.url).pathname;
  const marker = "/abnah-portal";
  const markerIndex = pathname.indexOf(marker);
  if (markerIndex < 0) return "/";
  return pathname.slice(markerIndex + marker.length) || "/";
}

function bearerToken(request: Request) {
  const authorization = request.headers.get("authorization") ?? "";
  const match = authorization.match(/^Bearer\s+([A-Za-z0-9_-]{40,256})$/i);
  return match?.[1] ?? "";
}

function canConfigure(row: SessionRow, environment: RuntimeEnvironment) {
  return environment.adminEmails.has(row.email.toLowerCase());
}

function publicSession(row: SessionRow, environment: RuntimeEnvironment) {
  return {
    authenticated: true,
    configured: true,
    canConfigure: canConfigure(row, environment),
    expiresAt: Date.parse(row.access_token_expires_at),
    user: {
      displayName: row.display_name,
      email: row.email,
    },
    workspace: {
      id: row.workspace_id,
      name: row.workspace_name,
      organizationId: row.organization_id,
    },
  };
}

async function resolveSession(
  request: Request,
  environment: RuntimeEnvironment,
) {
  const token = bearerToken(request);
  if (!token) return null;
  const client = database(environment);
  const sessionHash = await hashOpaqueValue(token);
  const now = new Date().toISOString();
  const { data, error } = await client
    .from("abnah_portal_sessions")
    .select("*")
    .eq("session_hash", sessionHash)
    .is("revoked_at", null)
    .gt("session_expires_at", now)
    .maybeSingle();
  if (error) throw new Error("The portal session could not be read.");
  if (!data) return null;

  let row = data as SessionRow;
  if (Date.parse(row.access_token_expires_at) <= Date.now()) {
    const refreshToken = await decryptSecret(
      row.refresh_token_ciphertext,
      environment.tokenEncryptionKey,
    );
    if (!refreshToken) {
      await client
        .from("abnah_portal_sessions")
        .update({ revoked_at: now })
        .eq("session_hash", sessionHash);
      return null;
    }
    try {
      const tokenResponse = await refreshZohoAccessToken(
        environment.zoho,
        refreshToken,
      );
      const workspace = await fetchZohoWorkspace(
        environment.zoho,
        tokenResponse.access_token!,
      );
      const expiresAt = new Date(
        Date.now() +
          Math.max(300, Number(tokenResponse.expires_in ?? 3600) - 60) * 1000,
      ).toISOString();
      const update = {
        access_token_ciphertext: await encryptSecret(
          tokenResponse.access_token!,
          environment.tokenEncryptionKey,
        ),
        access_token_expires_at: expiresAt,
        workspace_id: workspace.workspaceId,
        workspace_name: workspace.workspaceName,
        organization_id: workspace.organizationId,
        last_seen_at: now,
      };
      const { data: refreshed, error: refreshError } = await client
        .from("abnah_portal_sessions")
        .update(update)
        .eq("session_hash", sessionHash)
        .select("*")
        .single();
      if (refreshError || !refreshed) {
        throw new Error("The refreshed portal session could not be stored.");
      }
      row = refreshed as SessionRow;
    } catch {
      await client
        .from("abnah_portal_sessions")
        .update({ revoked_at: now })
        .eq("session_hash", sessionHash);
      return null;
    }
  } else {
    await client
      .from("abnah_portal_sessions")
      .update({ last_seen_at: now })
      .eq("session_hash", sessionHash);
  }
  if (row.workspace_id !== environment.zoho.allowedWorkspaceId) return null;
  return row;
}

function securedZohoUrl(value: unknown, label: string) {
  if (typeof value !== "string") return "";
  const clean = value.trim();
  if (!clean) return "";
  const url = new URL(clean);
  const host = url.hostname.toLowerCase();
  const approvedHost =
    /^analytics\.zoho\.(com|in|eu|jp|ca|sa)$/.test(host) ||
    host === "analytics.zoho.com.au";
  if (url.protocol !== "https:" || !approvedHost) {
    throw new Error(`${label}: enter an HTTPS Zoho Analytics URL.`);
  }
  return clean;
}

function normalizeHandoff(value: unknown) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("The URL handoff must be an object.");
  }
  const candidate = value as Record<string, unknown>;
  if (
    candidate.schema !== "abnah-zoho-view-handoff/v4" ||
    candidate.authMode !== "zoho_secured_login" ||
    candidate.integrationMode !==
      "individual_report_views_with_dashboard_fallbacks"
  ) {
    throw new Error("Use the ABNAH secured individual-view handoff v4.");
  }
  const candidatePages =
    candidate.pages &&
    typeof candidate.pages === "object" &&
    !Array.isArray(candidate.pages)
      ? (candidate.pages as Record<string, unknown>)
      : {};

  return {
    schema: "abnah-zoho-view-handoff/v4",
    generatedAt: new Date().toISOString(),
    authMode: "zoho_secured_login",
    integrationMode:
      "individual_report_views_with_dashboard_fallbacks",
    note:
      typeof candidate.note === "string"
        ? candidate.note.slice(0, 2_000)
        : "",
    pages: Object.fromEntries(
      Object.entries(expectedViews).map(([pageId, expected]) => {
        const pageCandidate =
          candidatePages[pageId] &&
          typeof candidatePages[pageId] === "object" &&
          !Array.isArray(candidatePages[pageId])
            ? (candidatePages[pageId] as Record<string, unknown>)
            : {};
        const reportsCandidate =
          pageCandidate.reports &&
          typeof pageCandidate.reports === "object" &&
          !Array.isArray(pageCandidate.reports)
            ? (pageCandidate.reports as Record<string, unknown>)
            : {};
        return [
          pageId,
          {
            dashboardViewName: expected.dashboardViewName,
            securedDashboardFallbackUrl: securedZohoUrl(
              pageCandidate.securedDashboardFallbackUrl,
              expected.dashboardViewName,
            ),
            reports: Object.fromEntries(
              Object.entries(expected.reports).map(
                ([reportId, viewName]) => {
                  const reportCandidate =
                    reportsCandidate[reportId] &&
                    typeof reportsCandidate[reportId] === "object" &&
                    !Array.isArray(reportsCandidate[reportId])
                      ? (reportsCandidate[reportId] as Record<string, unknown>)
                      : {};
                  return [
                    reportId,
                    {
                      viewName,
                      securedViewUrl: securedZohoUrl(
                        reportCandidate.securedViewUrl,
                        viewName,
                      ),
                    },
                  ];
                },
              ),
            ),
          },
        ];
      }),
    ),
  };
}

function emptyHandoff() {
  return normalizeHandoff({
    schema: "abnah-zoho-view-handoff/v4",
    authMode: "zoho_secured_login",
    integrationMode: "individual_report_views_with_dashboard_fallbacks",
    pages: {},
  });
}

async function handleStatus(
  request: Request,
  environment: RuntimeEnvironment,
) {
  return json(request, environment, {
    configured: environment.configured,
    missingEnvironment: environment.missing,
  });
}

async function handleAuthStart(
  request: Request,
  environment: RuntimeEnvironment,
) {
  assertAllowedOrigin(request, environment);
  const client = database(environment);
  const state = randomOpaqueValue();
  const stateHash = await hashOpaqueValue(state);
  const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString();
  await client
    .from("abnah_portal_oauth_states")
    .delete()
    .lt("expires_at", new Date().toISOString());
  const { error } = await client.from("abnah_portal_oauth_states").insert({
    state_hash: stateHash,
    return_url: environment.returnUrl,
    expires_at: expiresAt,
  });
  if (error) throw new Error("The Zoho sign-in state could not be created.");
  return redirect(createZohoAuthorizationUrl(environment.zoho, state));
}

async function handleAuthCallback(
  request: Request,
  environment: RuntimeEnvironment,
) {
  const url = new URL(request.url);
  if (url.searchParams.get("error")) {
    return redirect(
      portalErrorUrl(
        environment,
        "Zoho sign-in was cancelled or denied. Please retry.",
      ),
    );
  }
  const state = url.searchParams.get("state")?.trim() ?? "";
  const code = url.searchParams.get("code")?.trim() ?? "";
  if (!state || !code) {
    return redirect(
      portalErrorUrl(environment, "Zoho did not return a valid sign-in code."),
    );
  }
  const client = database(environment);
  const stateHash = await hashOpaqueValue(state);
  const { data: stateRow, error: stateError } = await client
    .from("abnah_portal_oauth_states")
    .delete()
    .eq("state_hash", stateHash)
    .gt("expires_at", new Date().toISOString())
    .select("return_url")
    .maybeSingle();
  if (stateError || !stateRow) {
    return redirect(
      portalErrorUrl(
        environment,
        "The Zoho sign-in request expired. Please start again.",
      ),
    );
  }

  try {
    const token = await exchangeZohoAuthorizationCode(
      environment.zoho,
      code,
    );
    const workspace = await fetchZohoWorkspace(
      environment.zoho,
      token.access_token!,
    );
    const profile = await fetchZohoProfile(
      environment.zoho,
      token.access_token!,
    );
    const opaqueSession = randomOpaqueValue();
    const sessionHash = await hashOpaqueValue(opaqueSession);
    const expiresIn = Math.max(
      300,
      Number(token.expires_in ?? 3600) - 60,
    );
    const accessTokenExpiresAt = new Date(
      Date.now() + expiresIn * 1000,
    ).toISOString();
    const sessionExpiresAt = new Date(
      token.refresh_token
        ? Date.now() + sessionDays * 24 * 60 * 60 * 1000
        : Date.now() + expiresIn * 1000,
    ).toISOString();
    const { error: insertError } = await client
      .from("abnah_portal_sessions")
      .insert({
        session_hash: sessionHash,
        email: profile.email,
        display_name:
          profile.displayName || profile.email || "Verified Zoho user",
        workspace_id: workspace.workspaceId,
        workspace_name: workspace.workspaceName,
        organization_id: workspace.organizationId,
        access_token_ciphertext: await encryptSecret(
          token.access_token!,
          environment.tokenEncryptionKey,
        ),
        refresh_token_ciphertext: await encryptSecret(
          token.refresh_token ?? "",
          environment.tokenEncryptionKey,
        ),
        access_token_expires_at: accessTokenExpiresAt,
        session_expires_at: sessionExpiresAt,
      });
    if (insertError) {
      throw new Error("The verified portal session could not be stored.");
    }
    const returnUrl = new URL(
      String(stateRow.return_url || environment.returnUrl),
    );
    returnUrl.hash = new URLSearchParams({
      portal_session: opaqueSession,
    }).toString();
    return redirect(returnUrl.toString());
  } catch (error) {
    const message =
      error instanceof Error &&
      error.message.includes("does not have access")
        ? error.message
        : "Zoho access could not be verified. Please retry.";
    return redirect(portalErrorUrl(environment, message));
  }
}

async function handleSession(
  request: Request,
  environment: RuntimeEnvironment,
) {
  assertAllowedOrigin(request, environment);
  const session = await resolveSession(request, environment);
  if (!session) {
    return json(
      request,
      environment,
      { error: "Verified Zoho Analytics access is required." },
      401,
    );
  }
  return json(request, environment, publicSession(session, environment));
}

function validIsoDate(value: string) {
  return /^\d{4}-\d{2}-\d{2}$/.test(value) &&
    !Number.isNaN(Date.parse(`${value}T00:00:00Z`));
}

async function handleData(
  request: Request,
  environment: RuntimeEnvironment,
) {
  assertAllowedOrigin(request, environment);
  const session = await resolveSession(request, environment);
  if (!session) {
    return json(
      request,
      environment,
      { error: "Verified Zoho Analytics access is required." },
      401,
    );
  }
  const url = new URL(request.url);
  const page = url.searchParams.get("page")?.trim() as PortalDataPage;
  const start = url.searchParams.get("start")?.trim() ?? "";
  const end = url.searchParams.get("end")?.trim() ?? "";
  if (!["p1", "p2"].includes(page)) {
    return json(request, environment, { error: "Invalid portal page." }, 400);
  }
  if (!validIsoDate(start) || !validIsoDate(end) || start > end) {
    return json(request, environment, { error: "Invalid date range." }, 400);
  }
  const rangeDays =
    (Date.parse(`${end}T00:00:00Z`) - Date.parse(`${start}T00:00:00Z`)) /
    86_400_000;
  if (rangeDays > 366) {
    return json(
      request,
      environment,
      { error: "Select a date range of 366 days or fewer." },
      400,
    );
  }
  const accessToken = await decryptSecret(
    session.access_token_ciphertext,
    environment.tokenEncryptionKey,
  );
  if (!accessToken) {
    return json(
      request,
      environment,
      { error: "The verified analytics session has expired." },
      401,
    );
  }
  const data = await fetchControlTowerPageData(
    environment.zoho,
    session,
    accessToken,
    page,
    start,
    end,
  );
  return json(request, environment, {
    schema: "abnah-control-tower-portal-page/v1",
    page,
    generatedAt: new Date().toISOString(),
    source: "zoho_analytics",
    dataBoundary:
      "Rows are read from the approved Zoho Analytics workspace and are not stored by this gateway.",
    ...data,
  });
}

async function handleLogout(
  request: Request,
  environment: RuntimeEnvironment,
) {
  assertAllowedOrigin(request, environment);
  const token = bearerToken(request);
  if (token) {
    const client = database(environment);
    await client
      .from("abnah_portal_sessions")
      .update({ revoked_at: new Date().toISOString() })
      .eq("session_hash", await hashOpaqueValue(token));
  }
  return json(request, environment, { ok: true });
}

async function handleConfig(
  request: Request,
  environment: RuntimeEnvironment,
) {
  assertAllowedOrigin(request, environment);
  const session = await resolveSession(request, environment);
  if (!session) {
    return json(
      request,
      environment,
      { error: "Verified Zoho Analytics access is required." },
      401,
    );
  }
  const client = database(environment);
  if (request.method === "GET") {
    const { data, error } = await client
      .from("abnah_zoho_portal_config")
      .select("version,payload,updated_at,updated_by")
      .eq("config_key", configKey)
      .maybeSingle();
    if (error) throw new Error("The shared URL handoff could not be loaded.");
    return json(
      request,
      environment,
      data
        ? {
            handoff: normalizeHandoff(data.payload),
            version: data.version,
            updatedAt: data.updated_at,
            updatedBy: data.updated_by,
          }
        : {
            handoff: emptyHandoff(),
            version: 0,
            updatedAt: null,
            updatedBy: null,
          },
    );
  }

  if (request.method !== "PUT") {
    return json(request, environment, { error: "Method not allowed." }, 405);
  }
  if (!canConfigure(session, environment)) {
    return json(
      request,
      environment,
      { error: "This Zoho user can view but cannot edit the URL handoff." },
      403,
    );
  }
  const text = await request.text();
  if (new TextEncoder().encode(text).length > maxBodyBytes) {
    return json(request, environment, { error: "The URL handoff is too large." }, 413);
  }
  let payload: { handoff?: unknown; expectedVersion?: unknown };
  try {
    payload = JSON.parse(text);
  } catch {
    return json(request, environment, { error: "The request is not valid JSON." }, 400);
  }
  const handoff = normalizeHandoff(payload.handoff);
  const expectedVersion = Number(payload.expectedVersion ?? 0);
  if (!Number.isInteger(expectedVersion) || expectedVersion < 0) {
    return json(request, environment, { error: "Invalid configuration version." }, 400);
  }
  const updatedAt = new Date().toISOString();
  const updatedBy = session.email || session.display_name;
  const nextVersion = expectedVersion + 1;

  if (expectedVersion === 0) {
    const { data, error } = await client
      .from("abnah_zoho_portal_config")
      .insert({
        config_key: configKey,
        version: nextVersion,
        payload: handoff,
        updated_at: updatedAt,
        updated_by: updatedBy,
      })
      .select("version,payload,updated_at,updated_by")
      .maybeSingle();
    if (error || !data) {
      return json(
        request,
        environment,
        { error: "The URL handoff changed. Reload it before saving." },
        409,
      );
    }
    return json(request, environment, {
      handoff: normalizeHandoff(data.payload),
      version: data.version,
      updatedAt: data.updated_at,
      updatedBy: data.updated_by,
    });
  }

  const { data, error } = await client
    .from("abnah_zoho_portal_config")
    .update({
      version: nextVersion,
      payload: handoff,
      updated_at: updatedAt,
      updated_by: updatedBy,
    })
    .eq("config_key", configKey)
    .eq("version", expectedVersion)
    .select("version,payload,updated_at,updated_by")
    .maybeSingle();
  if (error || !data) {
    return json(
      request,
      environment,
      { error: "The URL handoff changed. Reload it before saving." },
      409,
    );
  }
  return json(request, environment, {
    handoff: normalizeHandoff(data.payload),
    version: data.version,
    updatedAt: data.updated_at,
    updatedBy: data.updated_by,
  });
}

Deno.serve(async (request) => {
  const environment = loadEnvironment();
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: corsHeaders(request, environment),
    });
  }
  const path = routePath(request);
  if (path === "/status" && request.method === "GET") {
    return handleStatus(request, environment);
  }
  if (!environment.configured) {
    return json(
      request,
      environment,
      {
        error: "The Supabase portal backend is not configured.",
        missingEnvironment: environment.missing,
      },
      503,
    );
  }

  try {
    if (path === "/auth/start" && request.method === "GET") {
      return await handleAuthStart(request, environment);
    }
    if (path === "/auth/callback" && request.method === "GET") {
      return await handleAuthCallback(request, environment);
    }
    if (path === "/session" && request.method === "GET") {
      return await handleSession(request, environment);
    }
    if (path === "/data" && request.method === "GET") {
      return await handleData(request, environment);
    }
    if (path === "/logout" && request.method === "POST") {
      return await handleLogout(request, environment);
    }
    if (path === "/config") {
      return await handleConfig(request, environment);
    }
    return json(request, environment, { error: "Not found." }, 404);
  } catch (error) {
    return json(
      request,
      environment,
      {
        error:
          error instanceof Error
            ? error.message
            : "The portal backend could not complete this request.",
      },
      500,
    );
  }
});
