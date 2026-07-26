import portalSnapshot from "@/config/zoho-portal.json";
import {
  buildZohoPortalHandoff,
  normalizeZohoPortalHandoff,
} from "../../lib/zoho-portal-handoff";
import { resolveZohoSession } from "../../lib/zoho-auth-server";
import type {
  ZohoPortalConfig,
  ZohoPortalConfigEnvelope,
} from "../../lib/zoho-portal-types";
import {
  getZohoPortalConfig,
  PortalConfigConflictError,
  saveZohoPortalConfig,
} from "../../../db/zoho-portal-config";

const portal = portalSnapshot as unknown as ZohoPortalConfig;
const maxBodyBytes = 250_000;

function response(
  payload: unknown,
  status: number,
  refreshedCookie?: string,
) {
  const headers = new Headers({
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  });
  if (refreshedCookie) headers.append("set-cookie", refreshedCookie);
  return new Response(JSON.stringify(payload), { status, headers });
}

function emptyEnvelope(): ZohoPortalConfigEnvelope {
  return {
    handoff: buildZohoPortalHandoff(portal, {
      reports: {},
      dashboards: {},
    }),
    version: 0,
    updatedAt: null,
    updatedBy: null,
  };
}

export async function GET(request: Request) {
  try {
    const resolved = await resolveZohoSession(request);
    if (!resolved.session) {
      return response(
        { error: "Verified Zoho Analytics access is required." },
        401,
        resolved.refreshedCookie,
      );
    }
    const stored = await getZohoPortalConfig();
    const envelope = stored
      ? {
          ...stored,
          handoff: normalizeZohoPortalHandoff(stored.handoff, portal),
        }
      : emptyEnvelope();
    return response(envelope, 200, resolved.refreshedCookie);
  } catch (error) {
    return response(
      {
        error:
          error instanceof Error
            ? error.message
            : "Could not load the Zoho URL handoff.",
      },
      500,
    );
  }
}

export async function PUT(request: Request) {
  try {
    const resolved = await resolveZohoSession(request);
    if (!resolved.session) {
      return response(
        { error: "Verified Zoho Analytics access is required." },
        401,
        resolved.refreshedCookie,
      );
    }
    if (!resolved.publicSession.canConfigure) {
      return response(
        { error: "This Zoho user can view but cannot edit the URL handoff." },
        403,
        resolved.refreshedCookie,
      );
    }
    const text = await request.text();
    if (new TextEncoder().encode(text).length > maxBodyBytes) {
      return response({ error: "The URL handoff is too large." }, 413);
    }
    const payload = JSON.parse(text) as {
      handoff?: unknown;
      expectedVersion?: unknown;
    };
    const handoff = normalizeZohoPortalHandoff(payload.handoff, portal);
    const expectedVersion = Number(payload.expectedVersion ?? 0);
    if (!Number.isInteger(expectedVersion) || expectedVersion < 0) {
      return response({ error: "Invalid configuration version." }, 400);
    }
    const actor =
      resolved.session.email ||
      resolved.session.displayName ||
      "verified-zoho-user";
    const saved = await saveZohoPortalConfig({
      handoff,
      expectedVersion,
      actor,
    });
    return response(saved, 200, resolved.refreshedCookie);
  } catch (error) {
    if (error instanceof PortalConfigConflictError) {
      return response({ error: error.message }, 409);
    }
    if (error instanceof SyntaxError) {
      return response({ error: "The request body is not valid JSON." }, 400);
    }
    return response(
      {
        error:
          error instanceof Error
            ? error.message
            : "Could not save the Zoho URL handoff.",
      },
      500,
    );
  }
}
