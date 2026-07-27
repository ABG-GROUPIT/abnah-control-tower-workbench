const oauthScopes = [
  "ZohoAnalytics.metadata.read",
  "ZohoAnalytics.data.read",
  "profile.userinfo.READ",
].join(",");

export interface ZohoEnvironment {
  clientId: string;
  clientSecret: string;
  allowedWorkspaceId: string;
  redirectUri: string;
  accountsBaseUrl: string;
  analyticsApiBaseUrl: string;
  profileBaseUrl: string;
}

interface ZohoTokenResponse {
  access_token?: string;
  refresh_token?: string;
  expires_in?: number | string;
  error?: string;
}

export interface ZohoWorkspace {
  workspaceId: string;
  workspaceName: string;
  organizationId: string;
}

function recursivelyFindString(value: unknown, keys: Set<string>): string {
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

function findWorkspace(
  value: unknown,
  workspaceId: string,
  inheritedOrganizationId = "",
): ZohoWorkspace | null {
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

async function requestToken(
  environment: ZohoEnvironment,
  values: Record<string, string>,
) {
  const response = await fetch(
    `${environment.accountsBaseUrl}/oauth/v2/token`,
    {
      method: "POST",
      headers: {
        "content-type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        client_id: environment.clientId,
        client_secret: environment.clientSecret,
        ...values,
      }),
    },
  );
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

export function createZohoAuthorizationUrl(
  environment: ZohoEnvironment,
  state: string,
) {
  const url = new URL(`${environment.accountsBaseUrl}/oauth/v2/auth`);
  url.searchParams.set("scope", oauthScopes);
  url.searchParams.set("client_id", environment.clientId);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("access_type", "offline");
  url.searchParams.set("prompt", "consent");
  url.searchParams.set("redirect_uri", environment.redirectUri);
  url.searchParams.set("state", state);
  return url.toString();
}

export async function exchangeZohoAuthorizationCode(
  environment: ZohoEnvironment,
  code: string,
) {
  return requestToken(environment, {
    grant_type: "authorization_code",
    code,
    redirect_uri: environment.redirectUri,
  });
}

export async function refreshZohoAccessToken(
  environment: ZohoEnvironment,
  refreshToken: string,
) {
  return requestToken(environment, {
    grant_type: "refresh_token",
    refresh_token: refreshToken,
  });
}

export async function fetchZohoWorkspace(
  environment: ZohoEnvironment,
  accessToken: string,
) {
  const response = await fetch(
    `${environment.analyticsApiBaseUrl}/restapi/v2/workspaces`,
    {
      headers: {
        Authorization: `Zoho-oauthtoken ${accessToken}`,
      },
    },
  );
  const payload = (await response.json().catch(() => null)) as unknown;
  if (!response.ok) {
    throw new Error("Zoho Analytics workspace verification failed.");
  }
  const workspace = findWorkspace(payload, environment.allowedWorkspaceId);
  if (!workspace) {
    throw new Error(
      "This Zoho account does not have access to the configured ABNAH workspace.",
    );
  }
  return workspace;
}

export async function fetchZohoProfile(
  environment: ZohoEnvironment,
  accessToken: string,
) {
  try {
    const response = await fetch(
      `${environment.profileBaseUrl}/api/v1/user/self/profile?include=emails,locale`,
      {
        headers: {
          Authorization: `Zoho-oauthtoken ${accessToken}`,
        },
      },
    );
    if (!response.ok) return { email: "", displayName: "" };
    const payload = (await response.json()) as unknown;
    return {
      email: recursivelyFindString(
        payload,
        new Set(["primary_email", "primaryemail", "email"]),
      ).toLowerCase(),
      displayName: recursivelyFindString(
        payload,
        new Set(["display_name", "displayname", "full_name", "fullname"]),
      ),
    };
  } catch {
    return { email: "", displayName: "" };
  }
}
