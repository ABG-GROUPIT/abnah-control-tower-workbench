"use client";

import {
  Braces,
  Database,
  Download,
  Eye,
  FileSpreadsheet,
  LayoutDashboard,
  Network,
  Pencil,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { normalizeTable } from "../lib/grid-operations";
import type { AtlasData } from "../lib/atlas-types";
import type {
  ReportWorkspaceDocument,
  SchemaStatus,
  WorkspaceDocumentIndexEntry,
  WorkspaceRevision,
  WorkspaceSeed,
} from "../lib/workspace-types";
import type { ControlTowerArchitecture } from "../lib/architecture-types";
import type { ControlTowerRequirements } from "../lib/control-tower-types";
import type { ControlTowerEvidence } from "../lib/control-tower-evidence-types";
import type { ControlTowerFidelity } from "../lib/control-tower-fidelity-types";
import { ApiRegistry } from "./ApiRegistry";
import { ArchitectureGraphWorkspace } from "./ArchitectureGraphWorkspace";
import { ControlTowerWorkspace } from "./ControlTowerWorkspace";
import { DataQualityWorkspace } from "./DataQualityWorkspace";
import { ReportNavigator } from "./ReportNavigator";
import { ReportWorkspacePanel, type ReportTab } from "./ReportWorkspacePanel";

interface AtlasWorkspaceProps {
  atlas: AtlasData;
  workspaceSeed: WorkspaceSeed;
  architecture: ControlTowerArchitecture;
  controlTower: ControlTowerRequirements;
  controlTowerEvidence: ControlTowerEvidence;
  controlTowerFidelity: ControlTowerFidelity;
  persistenceMode?: "auto" | "browser";
}

type Surface = "discovery" | "api" | "control_tower" | "data_quality" | "architecture";

const defaultReportId = "report:p1_main:06_misc:03_budget_dsr_report";
const browserStorageKey = "abnah-schema-workspace-browser-v1";

function documentRecord(reports: ReportWorkspaceDocument[]) {
  return Object.fromEntries(reports.map((report) => [report.id, report]));
}

function stubDocument(entry: WorkspaceDocumentIndexEntry): ReportWorkspaceDocument {
  return {
    id: entry.reportId,
    name: entry.name,
    page: entry.page,
    section: entry.section,
    domain: entry.domain,
    priority: "P2",
    schemaStatus: "pending",
    verificationStatus: "needs_review",
    layoutKind: "freeform",
    captureMethod: "manual_workspace_entry",
    sourcePolicy: "Schema definitions only. Local screenshots, paths, and source images are excluded.",
    workflowStatus: entry.workflowStatus,
    version: entry.version,
    isArchived: entry.isArchived,
    isCustom: true,
    fields: [],
    tables: [normalizeTable({ id: "primary", name: "Schema pending", rows: 1, columns: 1, columnWidths: [150], cells: [] })],
    apiTests: [],
    notes: [],
    updatedAt: entry.updatedAt,
    updatedBy: entry.updatedBy,
  };
}

function customReport(page: string, section: string): ReportWorkspaceDocument {
  const suffix = globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`;
  return {
    id: `custom:${suffix}`,
    name: "Untitled report",
    page,
    section,
    domain: "unclassified",
    priority: "P2",
    schemaStatus: "pending",
    verificationStatus: "needs_review",
    layoutKind: "freeform",
    captureMethod: "manual_workspace_entry",
    sourcePolicy: "Schema definitions only. Local screenshots, paths, and source images are excluded.",
    workflowStatus: "draft",
    version: 0,
    isArchived: false,
    isCustom: true,
    fields: [],
    tables: [normalizeTable({ id: `table:${suffix}`, name: "Primary structure", rows: 3, columns: 4, columnWidths: [150, 150, 150, 150], cells: [] })],
    apiTests: [],
    notes: [],
    updatedAt: "",
    updatedBy: "",
  };
}

export function AtlasWorkspace({
  atlas,
  workspaceSeed,
  architecture,
  controlTower,
  controlTowerEvidence,
  controlTowerFidelity,
  persistenceMode = "auto",
}: AtlasWorkspaceProps) {
  const baseline = useMemo(() => documentRecord(workspaceSeed.reports), [workspaceSeed.reports]);
  const [documents, setDocuments] = useState<Record<string, ReportWorkspaceDocument>>(() => documentRecord(workspaceSeed.reports));
  const [publishedDocuments, setPublishedDocuments] = useState<Record<string, ReportWorkspaceDocument>>({});
  const [selectedId, setSelectedId] = useState(baseline[defaultReportId] ? defaultReportId : workspaceSeed.reports[0]?.id ?? "");
  const [activePage, setActivePage] = useState(baseline[defaultReportId]?.page ?? workspaceSeed.reports[0]?.page ?? "p1_main");
  const [surface, setSurface] = useState<Surface>("discovery");
  const [activeTab, setActiveTab] = useState<ReportTab>("structure");
  const [presentationMode, setPresentationMode] = useState(false);
  const [query, setQuery] = useState("");
  const [schemaFilter, setSchemaFilter] = useState<"all" | SchemaStatus>("all");
  const [showArchived, setShowArchived] = useState(false);
  const [dirtyIds, setDirtyIds] = useState<Set<string>>(new Set());
  const dirtyIdsRef = useRef(dirtyIds);
  const [persistenceState, setPersistenceState] = useState<"loading" | "ready" | "browser">(
    persistenceMode === "browser" ? "browser" : "loading",
  );
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [revisions, setRevisions] = useState<Record<string, WorkspaceRevision[]>>({});
  const loadedCurrent = useRef<Set<string>>(new Set());
  const loadedPublished = useRef<Set<string>>(new Set());

  useEffect(() => { dirtyIdsRef.current = dirtyIds; }, [dirtyIds]);

  useEffect(() => {
    if (persistenceMode === "browser") {
      const handle = globalThis.setTimeout(() => {
        try {
          const stored = globalThis.localStorage?.getItem(browserStorageKey);
          if (!stored) return;
          const parsed = JSON.parse(stored) as { documents?: ReportWorkspaceDocument[] };
          if (Array.isArray(parsed.documents)) {
            setDocuments((current) => ({
              ...current,
              ...documentRecord(parsed.documents ?? []),
            }));
          }
        } catch {
          globalThis.localStorage?.removeItem(browserStorageKey);
        }
      }, 0);
      return () => globalThis.clearTimeout(handle);
    }
    let cancelled = false;
    fetch("/api/workspace")
      .then(async (response) => {
        if (!response.ok) throw new Error("Workspace persistence is unavailable.");
        return response.json() as Promise<{ documents: WorkspaceDocumentIndexEntry[] }>;
      })
      .then(({ documents: index }) => {
        if (cancelled) return;
        setDocuments((current) => {
          const next = { ...current };
          index.forEach((entry) => {
            if (!next[entry.reportId]) next[entry.reportId] = stubDocument(entry);
            else next[entry.reportId] = {
              ...next[entry.reportId],
              name: entry.name,
              page: entry.page,
              section: entry.section,
              domain: entry.domain,
              workflowStatus: entry.workflowStatus,
              version: entry.version,
              isArchived: entry.isArchived,
              updatedAt: entry.updatedAt,
              updatedBy: entry.updatedBy,
            };
          });
          return next;
        });
        setPersistenceState("ready");
      })
      .catch(() => {
        if (cancelled) return;
        try {
          const stored = globalThis.localStorage?.getItem(browserStorageKey);
          if (stored) {
            const parsed = JSON.parse(stored) as { documents?: ReportWorkspaceDocument[] };
            if (Array.isArray(parsed.documents)) {
              setDocuments((current) => ({
                ...current,
                ...documentRecord(parsed.documents ?? []),
              }));
            }
          }
        } catch {
          globalThis.localStorage?.removeItem(browserStorageKey);
        }
        setPersistenceState("browser");
      });
    return () => { cancelled = true; };
  }, [persistenceMode]);

  useEffect(() => {
    if (!selectedId || persistenceState !== "ready") return;
    const targetSet = presentationMode ? loadedPublished.current : loadedCurrent.current;
    if (targetSet.has(selectedId) || (!presentationMode && dirtyIdsRef.current.has(selectedId))) return;
    const controller = new AbortController();
    const params = new URLSearchParams({ report_id: selectedId });
    if (presentationMode) params.set("view", "published");
    fetch(`/api/workspace?${params}`, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error("Could not load the stored report revision.");
        return response.json() as Promise<{ document: ReportWorkspaceDocument | null }>;
      })
      .then(({ document }) => {
        targetSet.add(selectedId);
        if (!document) return;
        if (presentationMode) setPublishedDocuments((current) => ({ ...current, [selectedId]: document }));
        else setDocuments((current) => ({ ...current, [selectedId]: document }));
      })
      .catch((error) => {
        if (error instanceof Error && error.name !== "AbortError") setMessage(error.message);
      });
    return () => controller.abort();
  }, [persistenceState, presentationMode, selectedId]);

  const reports = useMemo(() => Object.values(documents), [documents]);
  const workspaceDocument = documents[selectedId];
  const displayedDocument = presentationMode
    ? publishedDocuments[selectedId] ?? baseline[selectedId] ?? workspaceDocument
    : workspaceDocument;

  const updateDocument = (document: ReportWorkspaceDocument) => {
    if (presentationMode) return;
    const next = document.workflowStatus === "in_review" || document.workflowStatus === "published"
      ? { ...document, workflowStatus: "draft" as const }
      : document;
    setDocuments((current) => ({ ...current, [next.id]: next }));
    if (next.id === selectedId && next.page !== activePage) setActivePage(next.page);
    setDirtyIds((current) => new Set(current).add(next.id));
    setMessage("");
  };

  const save = async (action: "save_draft" | "submit_review" | "publish" | "return_to_draft") => {
    const document = documents[selectedId];
    if (!document || persistenceState === "loading") return;
    if (persistenceState === "browser") {
      const workflowStatus =
        action === "submit_review"
          ? "in_review"
          : action === "publish"
            ? "published"
            : action === "return_to_draft"
              ? "draft"
              : document.workflowStatus;
      const saved: ReportWorkspaceDocument = {
        ...document,
        workflowStatus,
        version: document.version + 1,
        updatedAt: new Date().toISOString(),
        updatedBy: "browser workspace",
      };
      const nextDocuments = { ...documents, [saved.id]: saved };
      setDocuments(nextDocuments);
      if (workflowStatus === "published") {
        setPublishedDocuments((current) => ({ ...current, [saved.id]: saved }));
      }
      setDirtyIds((current) => {
        const next = new Set(current);
        next.delete(saved.id);
        return next;
      });
      setRevisions((current) => ({
        ...current,
        [saved.id]: [
          {
            id: `browser:${saved.id}:${saved.version}`,
            reportId: saved.id,
            version: saved.version,
            workflowStatus: saved.workflowStatus,
            action,
            createdAt: saved.updatedAt,
            actor: saved.updatedBy,
          },
          ...(current[saved.id] ?? []),
        ],
      }));
      globalThis.localStorage?.setItem(
        browserStorageKey,
        JSON.stringify({ documents: Object.values(nextDocuments) }),
      );
      setMessage(
        action === "save_draft"
          ? "Draft saved in this browser."
          : action === "submit_review"
            ? "Submitted for browser-local review."
            : action === "publish"
              ? "Published revision saved in this browser."
              : "Returned to draft in this browser.",
      );
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch("/api/workspace", {
        method: action === "save_draft" ? "PUT" : "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ document, expectedVersion: document.version, ...(action === "save_draft" ? {} : { action }) }),
      });
      const payload = await response.json() as { document?: ReportWorkspaceDocument; error?: string };
      if (!response.ok || !payload.document) throw new Error(payload.error ?? "The report could not be saved.");
      const saved = payload.document;
      setDocuments((current) => ({ ...current, [saved.id]: saved }));
      setDirtyIds((current) => {
        const next = new Set(current);
        next.delete(saved.id);
        return next;
      });
      loadedCurrent.current.add(saved.id);
      if (saved.workflowStatus === "published") {
        setPublishedDocuments((current) => ({ ...current, [saved.id]: saved }));
        loadedPublished.current.add(saved.id);
      }
      setMessage(action === "save_draft" ? "Draft saved." : action === "submit_review" ? "Submitted for review." : action === "publish" ? "Published revision saved." : "Returned to draft.");
      void loadHistory(saved.id, true);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The report could not be saved.");
    } finally {
      setBusy(false);
    }
  };

  const loadHistory = async (reportId = selectedId, force = false) => {
    if (!reportId || persistenceState === "browser" || (!force && revisions[reportId])) return;
    try {
      const response = await fetch(`/api/workspace?report_id=${encodeURIComponent(reportId)}&history=1`);
      if (!response.ok) throw new Error("History is unavailable.");
      const payload = await response.json() as { revisions: WorkspaceRevision[] };
      setRevisions((current) => ({ ...current, [reportId]: payload.revisions }));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "History is unavailable.");
    }
  };

  const selectReport = (reportId: string) => {
    const report = documents[reportId];
    setSelectedId(reportId);
    if (report) setActivePage(report.page);
    setMessage("");
  };

  const addReport = () => {
    const current = documents[selectedId];
    const report = customReport(activePage, current?.section ?? "new_reports");
    setDocuments((items) => ({ ...items, [report.id]: report }));
    setDirtyIds((items) => new Set(items).add(report.id));
    loadedCurrent.current.add(report.id);
    setSelectedId(report.id);
    setActiveTab("settings");
    setMessage("");
  };

  const changePage = (page: string) => {
    setActivePage(page);
    const first = reports.find((report) => report.page === page && !report.isArchived);
    if (first) setSelectedId(first.id);
  };

  const openApiReport = (reportId: string) => {
    selectReport(reportId);
    setSurface("discovery");
    setActiveTab("api");
  };

  const openDiscoveryReport = (reportId: string) => {
    selectReport(reportId);
    setSurface("discovery");
    setActiveTab("structure");
  };

  const exportBackup = async () => {
    setMessage("");
    if (persistenceState === "browser") {
      const body = JSON.stringify(
        {
          exportedAt: new Date().toISOString(),
          storage: "browser",
          documents: Object.values(documents),
          revisions,
        },
        null,
        2,
      );
      const blob = new Blob([`${body}\n`], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "abnah-schema-workspace-browser-backup.json";
      anchor.click();
      URL.revokeObjectURL(url);
      setMessage("Browser workspace backup exported.");
      return;
    }
    try {
      const response = await fetch("/api/workspace?export=1");
      if (!response.ok) throw new Error("Workspace backup is unavailable.");
      const blob = await response.blob();
      const disposition = response.headers.get("content-disposition") ?? "";
      const fileName = disposition.match(/filename="([^"]+)"/)?.[1] ?? "abnah-schema-workspace.json";
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = fileName;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Workspace backup is unavailable.");
    }
  };

  return (
    <main className={`atlas-app${presentationMode ? " is-presentation" : ""}`}>
      <header className="app-topbar">
        <div className="app-brand">
          <Database aria-hidden="true" size={20} />
          <span><strong>ABNAH</strong><small>Schema Workspace</small></span>
        </div>
        <nav className="app-nav" aria-label="Workspace surfaces">
          <button type="button" className={surface === "discovery" ? "is-active" : ""} onClick={() => setSurface("discovery")}><FileSpreadsheet aria-hidden="true" size={15} /> Discovery</button>
          <button type="button" className={surface === "api" ? "is-active" : ""} onClick={() => setSurface("api")}><Braces aria-hidden="true" size={15} /> API validation</button>
          <button type="button" className={surface === "control_tower" ? "is-active" : ""} onClick={() => setSurface("control_tower")}><LayoutDashboard aria-hidden="true" size={15} /> Control tower</button>
          <button type="button" className={surface === "data_quality" ? "is-active" : ""} onClick={() => setSurface("data_quality")}><ShieldCheck aria-hidden="true" size={15} /> Data quality</button>
          <button type="button" className={surface === "architecture" ? "is-active" : ""} onClick={() => setSurface("architecture")}><Network aria-hidden="true" size={15} /> Architecture</button>
        </nav>
        <div className="app-summary"><span><b>{atlas.summary.reports}</b> reports</span><span><b>{workspaceSeed.reports.filter((report) => report.schemaStatus === "captured").length}</b> captured</span><span className={`persistence-indicator state-${persistenceState}`}>{persistenceState === "ready" ? "Stored" : persistenceState === "loading" ? "Connecting" : "Browser saved"}</span></div>
        <button type="button" className="backup-button" onClick={() => void exportBackup()} disabled={persistenceState === "loading"} title="Export current documents and revision history"><Download aria-hidden="true" size={14} /> Backup</button>
        <div className="view-switch" role="group" aria-label="Workspace view">
          <button type="button" className={!presentationMode ? "is-active" : ""} aria-pressed={!presentationMode} onClick={() => setPresentationMode(false)}><Pencil aria-hidden="true" size={14} /> Workspace</button>
          <button type="button" className={presentationMode ? "is-active" : ""} aria-pressed={presentationMode} onClick={() => setPresentationMode(true)}><Eye aria-hidden="true" size={14} /> Published</button>
        </div>
      </header>

      {surface === "discovery" && (
        <div className="discovery-layout">
          <ReportNavigator
            reports={reports}
            selectedId={selectedId}
            activePage={activePage}
            query={query}
            schemaFilter={schemaFilter}
            showArchived={showArchived}
            readOnly={presentationMode}
            onSelect={selectReport}
            onPageChange={changePage}
            onQueryChange={setQuery}
            onSchemaFilterChange={setSchemaFilter}
            onShowArchivedChange={setShowArchived}
            onAddReport={addReport}
          />
          {displayedDocument ? (
            <ReportWorkspacePanel
              key={displayedDocument.id}
              document={displayedDocument}
              readOnly={presentationMode}
              dirty={dirtyIds.has(selectedId)}
              busy={busy}
              message={message}
              activeTab={activeTab}
              revisions={revisions[selectedId] ?? []}
              persistenceState={persistenceState}
              onTabChange={setActiveTab}
              onChange={updateDocument}
              onSave={() => void save("save_draft")}
              onTransition={(action) => void save(action)}
              onLoadHistory={() => void loadHistory()}
            />
          ) : (
            <section className="empty-state"><strong>No report selected</strong></section>
          )}
        </div>
      )}
      {surface === "api" && <ApiRegistry reports={reports.filter((report) => !report.isArchived)} onOpenReport={openApiReport} />}
      {surface === "control_tower" && (
        <ControlTowerWorkspace
          requirements={controlTower}
          evidence={controlTowerEvidence}
          fidelity={controlTowerFidelity}
          onOpenReport={openDiscoveryReport}
        />
      )}
      {surface === "data_quality" && (
        <DataQualityWorkspace
          evidence={controlTowerEvidence}
          onOpenReport={openDiscoveryReport}
        />
      )}
      {surface === "architecture" && <ArchitectureGraphWorkspace architecture={architecture} requirements={controlTower} onOpenReport={openDiscoveryReport} />}
    </main>
  );
}
