"use client";

import { ChevronDown, ChevronRight, Plus, Search } from "lucide-react";
import { useMemo, useState } from "react";
import type { ReportWorkspaceDocument, SchemaStatus } from "../lib/workspace-types";

interface ReportNavigatorProps {
  reports: ReportWorkspaceDocument[];
  selectedId: string;
  activePage: string;
  query: string;
  schemaFilter: "all" | SchemaStatus;
  showArchived: boolean;
  readOnly: boolean;
  onSelect: (reportId: string) => void;
  onPageChange: (page: string) => void;
  onQueryChange: (query: string) => void;
  onSchemaFilterChange: (filter: "all" | SchemaStatus) => void;
  onShowArchivedChange: (show: boolean) => void;
  onAddReport: () => void;
}

const pageLabels: Record<string, string> = {
  p1_main: "P1 Enterprise",
  p2_reports: "P2 Reports",
  p4_stock_admin: "P4 Stock Admin",
};

function sectionLabel(value: string) {
  return value.replace(/^\d+_/, "").replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function ReportNavigator({
  reports,
  selectedId,
  activePage,
  query,
  schemaFilter,
  showArchived,
  readOnly,
  onSelect,
  onPageChange,
  onQueryChange,
  onSchemaFilterChange,
  onShowArchivedChange,
  onAddReport,
}: ReportNavigatorProps) {
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(["06_misc"]));
  const pages = useMemo(() => [...new Set(reports.map((report) => report.page))].sort(), [reports]);
  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return reports
      .filter((report) => report.page === activePage)
      .filter((report) => showArchived || !report.isArchived)
      .filter((report) => schemaFilter === "all" || report.schemaStatus === schemaFilter)
      .filter((report) => `${report.name} ${report.section} ${report.domain}`.toLowerCase().includes(normalized))
      .sort((a, b) => a.section.localeCompare(b.section) || a.name.localeCompare(b.name));
  }, [activePage, query, reports, schemaFilter, showArchived]);
  const grouped = useMemo(() => {
    const map = new Map<string, ReportWorkspaceDocument[]>();
    filtered.forEach((report) => map.set(report.section, [...(map.get(report.section) ?? []), report]));
    return [...map.entries()];
  }, [filtered]);

  return (
    <aside className="report-navigator" aria-label="Report catalogue">
      <div className="navigator-heading">
        <div><span className="section-kicker">Schema discovery</span><h2>Report catalogue</h2></div>
        {!readOnly && <button type="button" className="icon-button" data-tooltip="Add report" aria-label="Add report" onClick={onAddReport}><Plus aria-hidden="true" size={17} /></button>}
      </div>
      <label className="search-control navigator-search">
        <Search aria-hidden="true" size={15} />
        <input type="search" value={query} placeholder="Search reports" onChange={(event) => onQueryChange(event.target.value)} />
      </label>
      <div className="page-tabs" role="tablist" aria-label="Report surfaces">
        {pages.map((page) => (
          <button key={page} type="button" role="tab" aria-selected={activePage === page} className={activePage === page ? "is-active" : ""} onClick={() => onPageChange(page)}>
            {pageLabels[page] ?? page.replaceAll("_", " ")}
            <span>{reports.filter((report) => report.page === page && (showArchived || !report.isArchived)).length}</span>
          </button>
        ))}
      </div>
      <div className="navigator-filters">
        <select aria-label="Schema status" value={schemaFilter} onChange={(event) => onSchemaFilterChange(event.target.value as "all" | SchemaStatus)}>
          <option value="all">All schema states</option>
          <option value="captured">Captured</option>
          <option value="partial">Partial</option>
          <option value="pending">Pending</option>
          <option value="unavailable">Unavailable</option>
        </select>
        <label className="compact-check"><input type="checkbox" checked={showArchived} onChange={(event) => onShowArchivedChange(event.target.checked)} /> Archived</label>
      </div>
      <nav className="report-tree" aria-label={`${pageLabels[activePage] ?? activePage} reports`}>
        {grouped.map(([section, sectionReports]) => {
          const open = Boolean(query.trim()) || openSections.has(section);
          return (
            <section key={section} className="report-section">
              <button
                type="button"
                className="section-toggle"
                aria-expanded={open}
                onClick={() => setOpenSections((current) => {
                  const next = new Set(current);
                  if (next.has(section)) next.delete(section); else next.add(section);
                  return next;
                })}
              >
                {open ? <ChevronDown aria-hidden="true" size={14} /> : <ChevronRight aria-hidden="true" size={14} />}
                <span>{sectionLabel(section)}</span><b>{sectionReports.length}</b>
              </button>
              {open && (
                <div className="report-list">
                  {sectionReports.map((report) => (
                    <button key={report.id} type="button" className={selectedId === report.id ? "is-active" : ""} onClick={() => onSelect(report.id)}>
                      <i className={`schema-dot state-${report.schemaStatus}`} aria-hidden="true" />
                      <span><strong>{report.name}</strong><small>{report.fields.length} fields / {report.tables.length} structure{report.tables.length === 1 ? "" : "s"}</small></span>
                      <em>{report.priority}</em>
                    </button>
                  ))}
                </div>
              )}
            </section>
          );
        })}
        {!grouped.length && <div className="navigator-empty">No reports in this scope</div>}
      </nav>
      <footer className="navigator-footer">
        <span>{filtered.length} visible</span>
        <span>{reports.filter((report) => report.page === activePage && report.schemaStatus === "captured").length} captured</span>
      </footer>
    </aside>
  );
}
