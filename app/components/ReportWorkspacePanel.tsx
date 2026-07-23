"use client";

import {
  Archive,
  ArrowLeft,
  Braces,
  Check,
  Download,
  FileClock,
  FileText,
  Plus,
  Save,
  Send,
  Settings2,
  Table2,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { normalizeTable } from "../lib/grid-operations";
import type {
  ReportWorkspaceDocument,
  SchemaTable,
  WorkspaceRevision,
} from "../lib/workspace-types";
import { ApiTestEditor } from "./ApiTestEditor";
import { DataPointEditor } from "./DataPointEditor";
import { NotesEditor } from "./NotesEditor";
import { SchemaGridEditor } from "./SchemaGridEditor";

export type ReportTab = "schema" | "structure" | "api" | "notes" | "settings" | "history";

interface ReportWorkspacePanelProps {
  document: ReportWorkspaceDocument;
  readOnly: boolean;
  dirty: boolean;
  busy: boolean;
  message: string;
  activeTab: ReportTab;
  revisions: WorkspaceRevision[];
  persistenceState: "loading" | "ready" | "browser";
  onTabChange: (tab: ReportTab) => void;
  onChange: (document: ReportWorkspaceDocument) => void;
  onSave: () => void;
  onTransition: (action: "submit_review" | "publish" | "return_to_draft") => void;
  onLoadHistory: () => void;
}

const tabs: Array<{ id: ReportTab; label: string; icon: typeof Table2 }> = [
  { id: "schema", label: "Data points", icon: FileText },
  { id: "structure", label: "Table structure", icon: Table2 },
  { id: "api", label: "API & tests", icon: Braces },
  { id: "notes", label: "Notes", icon: FileClock },
  { id: "settings", label: "Report settings", icon: Settings2 },
  { id: "history", label: "History", icon: FileClock },
];

function friendly(value: string) {
  return value.replace(/^\d+_/, "").replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function newTable(): SchemaTable {
  const suffix = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`;
  return normalizeTable({
    id: `table:${suffix}`,
    name: "New structural table",
    rows: 3,
    columns: 4,
    columnWidths: [150, 150, 150, 150],
    cells: [],
  });
}

export function ReportWorkspacePanel({
  document,
  readOnly,
  dirty,
  busy,
  message,
  activeTab,
  revisions,
  persistenceState,
  onTabChange,
  onChange,
  onSave,
  onTransition,
  onLoadHistory,
}: ReportWorkspacePanelProps) {
  const [tableId, setTableId] = useState(document.tables[0]?.id ?? "");
  const activeTable = document.tables.find((table) => table.id === tableId) ?? document.tables[0];
  const canPersist = persistenceState === "ready" || persistenceState === "browser";
  const update = (patch: Partial<ReportWorkspaceDocument>) => onChange({ ...document, ...patch });
  const updateTable = (table: SchemaTable) => update({ tables: document.tables.map((item) => (item.id === table.id ? table : item)) });

  const exportDocument = () => {
    const blob = new Blob([`${JSON.stringify(document, null, 2)}\n`], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = window.document.createElement("a");
    link.href = url;
    link.download = `${document.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "report"}-schema.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className={`report-workspace-panel${readOnly ? " is-readonly" : ""}`}>
      <header className="report-header">
        <div className="report-heading-copy">
          <div className="report-breadcrumb"><span>{friendly(document.page)}</span><i>/</i><span>{friendly(document.section)}</span></div>
          <h1>{document.name}</h1>
          <div className="report-status-row">
            <span className={`status-label status-${document.schemaStatus}`}>{document.schemaStatus}</span>
            <span className={`status-label status-${document.workflowStatus}`}>{document.workflowStatus.replaceAll("_", " ")}</span>
            <span className="plain-label">{document.layoutKind.replaceAll("_", " ")}</span>
            <span className="plain-label">{document.fields.length} fields</span>
          </div>
        </div>
        <div className="workflow-actions">
          {dirty && <span className="dirty-label">Unsaved draft</span>}
          {!readOnly && (
            <>
              <button type="button" className="secondary-button" disabled={!dirty || busy || !canPersist} onClick={onSave}>
                <Save aria-hidden="true" size={15} /> Save draft
              </button>
              {document.workflowStatus === "draft" && (
                <button type="button" className="primary-button" disabled={busy || !canPersist} onClick={() => onTransition("submit_review")}>
                  <Send aria-hidden="true" size={15} /> Submit review
                </button>
              )}
              {document.workflowStatus === "in_review" && (
                <>
                  <button type="button" className="secondary-button" disabled={busy} onClick={() => onTransition("return_to_draft")}><ArrowLeft aria-hidden="true" size={15} /> Return</button>
                  <button type="button" className="primary-button" disabled={busy} onClick={() => onTransition("publish")}><Check aria-hidden="true" size={15} /> Publish</button>
                </>
              )}
            </>
          )}
        </div>
      </header>

      {message && <div className={`workspace-message${message.toLowerCase().includes("saved") || message.toLowerCase().includes("published") ? " is-success" : ""}`} role="status">{message}</div>}

      <nav className="report-tabs" aria-label="Report workspace sections">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              type="button"
              key={tab.id}
              className={activeTab === tab.id ? "is-active" : ""}
              aria-pressed={activeTab === tab.id}
              onClick={() => {
                onTabChange(tab.id);
                if (tab.id === "history") onLoadHistory();
              }}
            >
              <Icon aria-hidden="true" size={15} />{tab.label}
              {tab.id === "api" && <span>{document.apiTests.length}</span>}
              {tab.id === "notes" && <span>{document.notes.length}</span>}
            </button>
          );
        })}
      </nav>

      <div className="report-tab-content">
        {activeTab === "schema" && (
          <DataPointEditor reportId={document.id} fields={document.fields} readOnly={readOnly} onChange={(fields) => update({ fields })} />
        )}

        {activeTab === "structure" && (
          <section className="structure-panel">
            <div className="section-heading-row structure-heading">
              <div><span className="section-kicker">Rendered POS schema</span><h2>Blank table structure</h2></div>
              {!readOnly && (
                <div className="structure-actions">
                  <button type="button" className="secondary-button" onClick={() => {
                    const table = newTable();
                    update({ tables: [...document.tables, table] });
                    setTableId(table.id);
                  }}><Plus aria-hidden="true" size={15} /> Add table</button>
                  <button type="button" className="icon-button danger" data-tooltip="Delete table" aria-label="Delete table" disabled={document.tables.length <= 1} onClick={() => update({ tables: document.tables.filter((table) => table.id !== activeTable?.id) })}><Trash2 aria-hidden="true" size={15} /></button>
                </div>
              )}
            </div>
            <div className="table-switcher">
              {document.tables.map((table) => <button type="button" key={table.id} className={table.id === activeTable?.id ? "is-active" : ""} onClick={() => setTableId(table.id)}>{table.name}</button>)}
            </div>
            {activeTable && (
              <>
                {!readOnly && <label className="table-name-field"><span>Table name</span><input value={activeTable.name} onChange={(event) => updateTable({ ...activeTable, name: event.target.value })} /></label>}
                <SchemaGridEditor key={`${document.id}:${activeTable.id}`} table={activeTable} readOnly={readOnly} onChange={updateTable} />
              </>
            )}
          </section>
        )}

        {activeTab === "api" && <ApiTestEditor reportId={document.id} tests={document.apiTests} readOnly={readOnly} onChange={(apiTests) => update({ apiTests })} />}
        {activeTab === "notes" && <NotesEditor reportId={document.id} notes={document.notes} readOnly={readOnly} onChange={(notes) => update({ notes })} />}

        {activeTab === "settings" && (
          <section className="settings-panel">
            <div className="section-heading-row"><div><span className="section-kicker">Discovery record</span><h2>Report settings</h2></div><button type="button" className="secondary-button" onClick={exportDocument}><Download aria-hidden="true" size={15} /> Export JSON</button></div>
            <div className="settings-grid">
              <label><span>Report name</span>{readOnly ? <strong>{document.name}</strong> : <input value={document.name} onChange={(event) => update({ name: event.target.value })} />}</label>
              <label><span>Stable report ID</span><code>{document.id}</code></label>
              <label><span>Page</span>{readOnly ? <span>{document.page}</span> : <input value={document.page} onChange={(event) => update({ page: event.target.value })} />}</label>
              <label><span>Section</span>{readOnly ? <span>{document.section}</span> : <input value={document.section} onChange={(event) => update({ section: event.target.value })} />}</label>
              <label><span>Domain</span>{readOnly ? <span>{document.domain}</span> : <select value={document.domain} onChange={(event) => update({ domain: event.target.value })}><option value="inventory_consumption">Inventory and consumption</option><option value="vendor_procurement">Vendor and procurement</option><option value="sales_revenue">Sales and revenue</option><option value="unclassified">Unclassified</option></select>}</label>
              <label><span>Priority</span>{readOnly ? <span>{document.priority}</span> : <select value={document.priority} onChange={(event) => update({ priority: event.target.value as ReportWorkspaceDocument["priority"] })}><option>P0</option><option>P1</option><option>P2</option></select>}</label>
              <label><span>Schema state</span>{readOnly ? <span>{document.schemaStatus}</span> : <select value={document.schemaStatus} onChange={(event) => update({ schemaStatus: event.target.value as ReportWorkspaceDocument["schemaStatus"] })}><option value="captured">Captured</option><option value="partial">Partial</option><option value="pending">Pending</option><option value="unavailable">Unavailable</option></select>}</label>
              <label><span>Verification</span>{readOnly ? <span>{document.verificationStatus}</span> : <select value={document.verificationStatus} onChange={(event) => update({ verificationStatus: event.target.value as ReportWorkspaceDocument["verificationStatus"] })}><option value="needs_review">Needs review</option><option value="reviewed">Reviewed</option><option value="uat_verified">UAT verified</option></select>}</label>
              <label><span>Layout class</span>{readOnly ? <span>{document.layoutKind}</span> : <select value={document.layoutKind} onChange={(event) => update({ layoutKind: event.target.value as ReportWorkspaceDocument["layoutKind"] })}><option value="flat">Flat</option><option value="grouped_columns">Grouped columns</option><option value="grouped_rows">Grouped rows</option><option value="mixed">Mixed</option><option value="freeform">Freeform</option></select>}</label>
              <label><span>Capture method</span>{readOnly ? <span>{document.captureMethod}</span> : <input value={document.captureMethod} onChange={(event) => update({ captureMethod: event.target.value })} />}</label>
              <label className="settings-wide"><span>Source policy</span><p>{document.sourcePolicy}</p></label>
              {!readOnly && <label className="archive-control"><input type="checkbox" checked={document.isArchived} onChange={(event) => update({ isArchived: event.target.checked })} /><Archive aria-hidden="true" size={15} /> Archive this report</label>}
            </div>
          </section>
        )}

        {activeTab === "history" && (
          <section className="history-panel">
            <div className="section-heading-row"><div><span className="section-kicker">Immutable revisions</span><h2>Change history</h2></div></div>
            {revisions.length ? (
              <div className="history-list">
                {revisions.map((revision) => (
                  <div key={revision.id}><b>v{revision.version}</b><span className={`status-label status-${revision.workflowStatus}`}>{revision.workflowStatus.replaceAll("_", " ")}</span><strong>{revision.action.replaceAll("_", " ")}</strong><span>{revision.actor}</span><time>{new Date(revision.createdAt).toLocaleString("en-IN")}</time></div>
                ))}
              </div>
            ) : (
              <div className="empty-state compact-empty"><strong>No stored revision yet</strong><span>The generated baseline is version 0.</span></div>
            )}
          </section>
        )}
      </div>

      <aside className="report-context-rail">
        <section><span className="section-kicker">Coverage</span><dl><div><dt>Data points</dt><dd>{document.fields.length}</dd></div><div><dt>Tables</dt><dd>{document.tables.length}</dd></div><div><dt>API records</dt><dd>{document.apiTests.length}</dd></div><div><dt>Notes</dt><dd>{document.notes.length}</dd></div></dl></section>
        <section><span className="section-kicker">Revision</span><dl><div><dt>Version</dt><dd>{document.version}</dd></div><div><dt>State</dt><dd>{document.workflowStatus.replaceAll("_", " ")}</dd></div><div><dt>Updated by</dt><dd>{document.updatedBy || "Generated baseline"}</dd></div></dl></section>
        <section className="policy-section"><span className="section-kicker">Evidence policy</span><p>{document.sourcePolicy}</p></section>
      </aside>
    </section>
  );
}
