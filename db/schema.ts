import { sql } from "drizzle-orm";
import { index, integer, sqliteTable, text, uniqueIndex } from "drizzle-orm/sqlite-core";

export const workspaceDocuments = sqliteTable(
  "workspace_documents",
  {
    reportId: text("report_id").primaryKey(),
    name: text("name").notNull(),
    page: text("page").notNull(),
    section: text("section").notNull(),
    domain: text("domain").notNull(),
    workflowStatus: text("workflow_status").notNull().default("draft"),
    version: integer("version").notNull().default(1),
    isArchived: integer("is_archived", { mode: "boolean" }).notNull().default(false),
    payload: text("payload").notNull(),
    createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
    updatedAt: text("updated_at").notNull().default(sql`CURRENT_TIMESTAMP`),
    updatedBy: text("updated_by").notNull(),
  },
  (table) => [
    index("workspace_documents_page_section_idx").on(table.page, table.section),
    index("workspace_documents_workflow_idx").on(table.workflowStatus),
  ],
);

export const workspaceRevisions = sqliteTable(
  "workspace_revisions",
  {
    id: text("id").primaryKey(),
    reportId: text("report_id").notNull(),
    version: integer("version").notNull(),
    workflowStatus: text("workflow_status").notNull(),
    action: text("action").notNull(),
    payload: text("payload").notNull(),
    actor: text("actor").notNull(),
    createdAt: text("created_at").notNull().default(sql`CURRENT_TIMESTAMP`),
  },
  (table) => [
    uniqueIndex("workspace_revisions_report_version_idx").on(table.reportId, table.version),
    index("workspace_revisions_report_created_idx").on(table.reportId, table.createdAt),
    index("workspace_revisions_published_idx").on(table.reportId, table.workflowStatus),
  ],
);
