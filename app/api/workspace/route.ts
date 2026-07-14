import type { WorkflowStatus } from "../../lib/workspace-types";
import { sanitizeWorkspaceDocument, WorkspaceValidationError } from "../../lib/workspace-validation";
import {
  getWorkspaceDocument,
  exportWorkspaceBackup,
  listWorkspaceDocuments,
  listWorkspaceRevisions,
  saveWorkspaceDocument,
  WorkspaceConflictError,
} from "../../../db/workspace";

const MAX_BODY_BYTES = 2_000_000;

function actorForRequest(request: Request): string | null {
  const email = request.headers.get("oai-authenticated-user-email")?.trim();
  if (email) return email;
  const hostname = new URL(request.url).hostname;
  if (hostname === "localhost" || hostname === "127.0.0.1" || hostname === "0.0.0.0" || hostname === "[::1]") {
    return "local-editor@abnah";
  }
  return null;
}

async function readPayload(request: Request): Promise<Record<string, unknown>> {
  const text = await request.text();
  if (new TextEncoder().encode(text).length > MAX_BODY_BYTES) {
    throw new WorkspaceValidationError("The report document exceeds the 2 MB request limit.");
  }
  const value = JSON.parse(text) as unknown;
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new WorkspaceValidationError("Request body must be an object.");
  }
  return value as Record<string, unknown>;
}

function routeError(error: unknown) {
  if (error instanceof WorkspaceConflictError) {
    return Response.json({ error: error.message }, { status: 409 });
  }
  if (error instanceof WorkspaceValidationError || error instanceof SyntaxError) {
    return Response.json({ error: error.message }, { status: 400 });
  }
  const message = error instanceof Error ? error.message : "Unexpected workspace error.";
  return Response.json({ error: message }, { status: 500 });
}

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    if (url.searchParams.get("export") === "1") {
      if (!actorForRequest(request)) {
        return Response.json({ error: "Authentication is required to export the workspace." }, { status: 401 });
      }
      const backup = await exportWorkspaceBackup();
      return new Response(JSON.stringify(backup, null, 2), {
        headers: {
          "content-type": "application/json; charset=utf-8",
          "content-disposition": `attachment; filename="abnah-schema-workspace-${backup.exportedAt.slice(0, 10)}.json"`,
          "cache-control": "no-store",
        },
      });
    }
    const reportId = url.searchParams.get("report_id");
    if (!reportId) return Response.json({ documents: await listWorkspaceDocuments() });
    if (url.searchParams.get("history") === "1") {
      return Response.json({ revisions: await listWorkspaceRevisions(reportId) });
    }
    const view = url.searchParams.get("view") === "published" ? "published" : "current";
    return Response.json({ document: await getWorkspaceDocument(reportId, view) });
  } catch (error) {
    return routeError(error);
  }
}

export async function PUT(request: Request) {
  try {
    const actor = actorForRequest(request);
    if (!actor) return Response.json({ error: "Authentication is required to edit the atlas." }, { status: 401 });
    const payload = await readPayload(request);
    const document = sanitizeWorkspaceDocument(payload.document);
    const expectedVersion = Number(payload.expectedVersion ?? 0);
    const saved = await saveWorkspaceDocument({
      document,
      expectedVersion,
      workflowStatus: "draft",
      action: "save_draft",
      actor,
    });
    return Response.json({ document: saved });
  } catch (error) {
    return routeError(error);
  }
}

export async function POST(request: Request) {
  try {
    const actor = actorForRequest(request);
    if (!actor) return Response.json({ error: "Authentication is required to change workflow state." }, { status: 401 });
    const payload = await readPayload(request);
    const document = sanitizeWorkspaceDocument(payload.document);
    const expectedVersion = Number(payload.expectedVersion ?? 0);
    const action = String(payload.action ?? "");
    const transitions: Record<string, WorkflowStatus> = {
      submit_review: "in_review",
      publish: "published",
      return_to_draft: "draft",
    };
    const workflowStatus = transitions[action];
    if (!workflowStatus) throw new WorkspaceValidationError("Unsupported workflow transition.");
    const current = await getWorkspaceDocument(document.id, "current");
    if (action === "publish" && current?.workflowStatus !== "in_review") {
      throw new WorkspaceValidationError("Only an in-review revision can be published.");
    }
    if (action === "return_to_draft" && current?.workflowStatus !== "in_review") {
      throw new WorkspaceValidationError("Only an in-review revision can be returned to draft.");
    }
    const saved = await saveWorkspaceDocument({ document, expectedVersion, workflowStatus, action, actor });
    return Response.json({ document: saved });
  } catch (error) {
    return routeError(error);
  }
}
