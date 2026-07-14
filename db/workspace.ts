import { and, desc, eq } from "drizzle-orm";
import type {
  ReportWorkspaceDocument,
  WorkflowStatus,
  WorkspaceDocumentIndexEntry,
  WorkspaceRevision,
} from "../app/lib/workspace-types";
import { getD1, getDb } from ".";
import { workspaceDocuments, workspaceRevisions } from "./schema";

let initialized = false;

async function ensureWorkspaceSchema() {
  if (initialized) return;
  const d1 = await getD1();
  await d1.batch([
    d1.prepare(`CREATE TABLE IF NOT EXISTS workspace_documents (
      report_id TEXT PRIMARY KEY NOT NULL,
      name TEXT NOT NULL,
      page TEXT NOT NULL,
      section TEXT NOT NULL,
      domain TEXT NOT NULL,
      workflow_status TEXT DEFAULT 'draft' NOT NULL,
      version INTEGER DEFAULT 1 NOT NULL,
      is_archived INTEGER DEFAULT 0 NOT NULL,
      payload TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
      updated_by TEXT NOT NULL
    )`),
    d1.prepare("CREATE INDEX IF NOT EXISTS workspace_documents_page_section_idx ON workspace_documents (page, section)"),
    d1.prepare("CREATE INDEX IF NOT EXISTS workspace_documents_workflow_idx ON workspace_documents (workflow_status)"),
    d1.prepare(`CREATE TABLE IF NOT EXISTS workspace_revisions (
      id TEXT PRIMARY KEY NOT NULL,
      report_id TEXT NOT NULL,
      version INTEGER NOT NULL,
      workflow_status TEXT NOT NULL,
      action TEXT NOT NULL,
      payload TEXT NOT NULL,
      actor TEXT NOT NULL,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL
    )`),
    d1.prepare("CREATE UNIQUE INDEX IF NOT EXISTS workspace_revisions_report_version_idx ON workspace_revisions (report_id, version)"),
    d1.prepare("CREATE INDEX IF NOT EXISTS workspace_revisions_report_created_idx ON workspace_revisions (report_id, created_at)"),
    d1.prepare("CREATE INDEX IF NOT EXISTS workspace_revisions_published_idx ON workspace_revisions (report_id, workflow_status)"),
  ]);
  initialized = true;
}

function parseDocument(payload: string): ReportWorkspaceDocument {
  return JSON.parse(payload) as ReportWorkspaceDocument;
}

export async function listWorkspaceDocuments(): Promise<WorkspaceDocumentIndexEntry[]> {
  await ensureWorkspaceSchema();
  const db = await getDb();
  return db
    .select({
      reportId: workspaceDocuments.reportId,
      name: workspaceDocuments.name,
      page: workspaceDocuments.page,
      section: workspaceDocuments.section,
      domain: workspaceDocuments.domain,
      workflowStatus: workspaceDocuments.workflowStatus,
      version: workspaceDocuments.version,
      isArchived: workspaceDocuments.isArchived,
      updatedAt: workspaceDocuments.updatedAt,
      updatedBy: workspaceDocuments.updatedBy,
    })
    .from(workspaceDocuments)
    .orderBy(workspaceDocuments.page, workspaceDocuments.section, workspaceDocuments.name) as Promise<WorkspaceDocumentIndexEntry[]>;
}

export async function getWorkspaceDocument(
  reportId: string,
  view: "current" | "published" = "current",
): Promise<ReportWorkspaceDocument | null> {
  await ensureWorkspaceSchema();
  const db = await getDb();
  if (view === "published") {
    const [revision] = await db
      .select({ payload: workspaceRevisions.payload })
      .from(workspaceRevisions)
      .where(and(eq(workspaceRevisions.reportId, reportId), eq(workspaceRevisions.workflowStatus, "published")))
      .orderBy(desc(workspaceRevisions.version))
      .limit(1);
    return revision ? parseDocument(revision.payload) : null;
  }
  const [document] = await db
    .select({ payload: workspaceDocuments.payload })
    .from(workspaceDocuments)
    .where(eq(workspaceDocuments.reportId, reportId))
    .limit(1);
  return document ? parseDocument(document.payload) : null;
}

export async function listWorkspaceRevisions(reportId: string): Promise<WorkspaceRevision[]> {
  await ensureWorkspaceSchema();
  const db = await getDb();
  const rows = await db
    .select({
      id: workspaceRevisions.id,
      reportId: workspaceRevisions.reportId,
      version: workspaceRevisions.version,
      workflowStatus: workspaceRevisions.workflowStatus,
      action: workspaceRevisions.action,
      actor: workspaceRevisions.actor,
      createdAt: workspaceRevisions.createdAt,
    })
    .from(workspaceRevisions)
    .where(eq(workspaceRevisions.reportId, reportId))
    .orderBy(desc(workspaceRevisions.version))
    .limit(100);
  return rows as WorkspaceRevision[];
}

export async function exportWorkspaceBackup() {
  await ensureWorkspaceSchema();
  const db = await getDb();
  const documents = await db
    .select({ payload: workspaceDocuments.payload })
    .from(workspaceDocuments)
    .orderBy(workspaceDocuments.page, workspaceDocuments.section, workspaceDocuments.name);
  const revisions = await db
    .select({
      id: workspaceRevisions.id,
      reportId: workspaceRevisions.reportId,
      version: workspaceRevisions.version,
      workflowStatus: workspaceRevisions.workflowStatus,
      action: workspaceRevisions.action,
      actor: workspaceRevisions.actor,
      createdAt: workspaceRevisions.createdAt,
      payload: workspaceRevisions.payload,
    })
    .from(workspaceRevisions)
    .orderBy(workspaceRevisions.reportId, workspaceRevisions.version);
  return {
    contractVersion: "1.0.0",
    exportedAt: new Date().toISOString(),
    documents: documents.map((row) => parseDocument(row.payload)),
    revisions: revisions.map((row) => ({ ...row, document: parseDocument(row.payload), payload: undefined })),
  };
}

export class WorkspaceConflictError extends Error {}

export async function saveWorkspaceDocument(options: {
  document: ReportWorkspaceDocument;
  expectedVersion: number;
  workflowStatus: WorkflowStatus;
  action: string;
  actor: string;
}): Promise<ReportWorkspaceDocument> {
  await ensureWorkspaceSchema();
  const db = await getDb();
  const [current] = await db
    .select({ version: workspaceDocuments.version })
    .from(workspaceDocuments)
    .where(eq(workspaceDocuments.reportId, options.document.id))
    .limit(1);

  const currentVersion = current?.version ?? 0;
  if (currentVersion !== options.expectedVersion) {
    throw new WorkspaceConflictError(`Expected revision ${options.expectedVersion}, found ${currentVersion}.`);
  }

  const nextVersion = currentVersion + 1;
  const updatedAt = new Date().toISOString();
  const document: ReportWorkspaceDocument = {
    ...options.document,
    workflowStatus: options.workflowStatus,
    version: nextVersion,
    updatedAt,
    updatedBy: options.actor,
  };
  const payload = JSON.stringify(document);
  const revisionId = `${document.id}:revision:${nextVersion}`;
  const d1 = await getD1();

  if (current) {
    const results = await d1.batch([
      d1.prepare(`UPDATE workspace_documents
        SET name = ?, page = ?, section = ?, domain = ?, workflow_status = ?, version = ?,
            is_archived = ?, payload = ?, updated_at = ?, updated_by = ?
        WHERE report_id = ? AND version = ?`)
        .bind(
          document.name,
          document.page,
          document.section,
          document.domain,
          document.workflowStatus,
          document.version,
          document.isArchived ? 1 : 0,
          payload,
          updatedAt,
          options.actor,
          document.id,
          options.expectedVersion,
        ),
      d1.prepare(`INSERT INTO workspace_revisions
        (id, report_id, version, workflow_status, action, payload, actor, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)`)
        .bind(revisionId, document.id, nextVersion, document.workflowStatus, options.action, payload, options.actor, updatedAt),
    ]);
    if (!results[0].meta.changes) {
      throw new WorkspaceConflictError("The report changed before this save completed.");
    }
  } else {
    await d1.batch([
      d1.prepare(`INSERT INTO workspace_documents
        (report_id, name, page, section, domain, workflow_status, version, is_archived, payload, created_at, updated_at, updated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`)
        .bind(
          document.id,
          document.name,
          document.page,
          document.section,
          document.domain,
          document.workflowStatus,
          document.version,
          document.isArchived ? 1 : 0,
          payload,
          updatedAt,
          updatedAt,
          options.actor,
        ),
      d1.prepare(`INSERT INTO workspace_revisions
        (id, report_id, version, workflow_status, action, payload, actor, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)`)
        .bind(revisionId, document.id, nextVersion, document.workflowStatus, options.action, payload, options.actor, updatedAt),
    ]);
  }
  return document;
}
