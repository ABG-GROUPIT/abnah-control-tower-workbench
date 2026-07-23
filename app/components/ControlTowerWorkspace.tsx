"use client";

import {
  AlertTriangle,
  ArrowRight,
  Braces,
  CircleDot,
  DatabaseZap,
  ExternalLink,
  FileCheck2,
  FileSpreadsheet,
  ScanSearch,
  Layers3,
  ListChecks,
  Route,
  ShieldCheck,
} from "lucide-react";
import { useMemo, useState } from "react";
import type {
  CaptureGroup,
  ControlTowerKpi,
  ControlTowerRequirements,
} from "../lib/control-tower-types";
import type { ControlTowerEvidence } from "../lib/control-tower-evidence-types";
import { ControlTowerEvidenceView } from "./ControlTowerEvidence";

interface ControlTowerWorkspaceProps {
  requirements: ControlTowerRequirements;
  evidence: ControlTowerEvidence;
  onOpenReport: (reportId: string) => void;
}

type ControlTowerView = "pages" | "sources" | "evidence" | "delivery";

const statusLabel = (value: string) => value.replaceAll("_", " ");

function StatusPill({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`ct-pill tone-${tone}`}>{children}</span>;
}

function KpiTable({ kpis }: { kpis: ControlTowerKpi[] }) {
  return (
    <div className="ct-table-wrap">
      <table className="ct-table ct-kpi-table">
        <thead>
          <tr>
            <th>KPI</th>
            <th>Definition</th>
            <th>Formula</th>
            <th>Grain</th>
            <th>Owner / gate</th>
          </tr>
        </thead>
        <tbody>
          {kpis.map((kpi) => (
            <tr key={kpi.id}>
              <td><strong>{kpi.name}</strong><code>{kpi.id}</code></td>
              <td>{kpi.businessDefinition}</td>
              <td><code>{kpi.formula}</code></td>
              <td>{kpi.grain}</td>
              <td>
                <strong>{kpi.owner}</strong>
                <StatusPill tone="blue">{statusLabel(kpi.validationStatus)}</StatusPill>
                {kpi.caveats[0] ? <small>{kpi.caveats[0]}</small> : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PageRequirements({ requirements }: { requirements: ControlTowerRequirements }) {
  const [pageId, setPageId] = useState(requirements.pages[0]?.id ?? "");
  const page = requirements.pages.find((item) => item.id === pageId) ?? requirements.pages[0];
  const pageKpis = useMemo(
    () => requirements.kpis.filter((kpi) => page?.kpiIds.includes(kpi.id)),
    [page, requirements.kpis],
  );

  if (!page) return null;

  return (
    <div className="ct-page-browser">
      <aside className="ct-page-index" aria-label="Control tower pages">
        <span className="section-kicker">Four-page control tower</span>
        {requirements.pages.map((item) => (
          <button
            key={item.id}
            type="button"
            className={item.id === page.id ? "is-active" : ""}
            onClick={() => setPageId(item.id)}
          >
            <span>Page {item.number}</span>
            <strong>{item.name}</strong>
            <small>{item.audiences.join(" / ")}</small>
          </button>
        ))}
        <div className="ct-terminology-note">
          <FileCheck2 aria-hidden="true" size={16} />
          <div><strong>Terminology fixed</strong><span>Page 3 uses consumption, not yield.</span></div>
        </div>
      </aside>

      <div className="ct-page-detail">
        <header className="ct-page-heading">
          <div>
            <span className="section-kicker">Page {page.number} / {pageKpis.length} draft KPI definitions</span>
            <h2>{page.name}</h2>
            <p>{page.purpose}</p>
          </div>
          <StatusPill tone="amber">Source validation pending</StatusPill>
        </header>

        <section className="ct-flow-band" aria-label={`${page.name} decision flow`}>
          <header><Route aria-hidden="true" size={15} /><strong>Decision flow</strong></header>
          <ol>
            {page.decisionFlow.map((step, index) => (
              <li key={step}>
                <span>{index + 1}</span><strong>{step}</strong>
                {index < page.decisionFlow.length - 1 ? <ArrowRight aria-hidden="true" size={14} /> : null}
              </li>
            ))}
          </ol>
        </section>

        <section className="ct-section">
          <div className="ct-section-heading">
            <div><ListChecks aria-hidden="true" size={16} /><span><strong>Required visual modules</strong><small>Business question and approved calculation intent</small></span></div>
            <StatusPill>{page.visualModules.length} modules</StatusPill>
          </div>
          <div className="ct-table-wrap">
            <table className="ct-table ct-module-table">
              <thead><tr><th>#</th><th>Module</th><th>Question</th><th>Calculation intent</th></tr></thead>
              <tbody>
                {page.visualModules.map((module) => (
                  <tr key={`${page.id}:${module.order}`}>
                    <td><b>{module.order}</b></td>
                    <td><strong>{module.name}</strong></td>
                    <td>{module.question}</td>
                    <td>{module.logic}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="ct-section">
          <div className="ct-section-heading">
            <div><AlertTriangle aria-hidden="true" size={16} /><span><strong>Decision and publication rules</strong><small>Conditions that prevent misleading output</small></span></div>
          </div>
          <div className="ct-rule-grid">
            {page.rules.map((rule) => (
              <div key={`${page.id}:${rule.label}`}>
                <StatusPill tone={rule.label.toLowerCase()}>{rule.label}</StatusPill>
                <strong>{rule.meaning}</strong>
                <code>{rule.condition}</code>
              </div>
            ))}
          </div>
        </section>

        <section className="ct-section">
          <div className="ct-section-heading">
            <div><CircleDot aria-hidden="true" size={16} /><span><strong>Draft KPI register</strong><small>Business rules received; source relationships are not selected yet</small></span></div>
            <StatusPill tone="blue">Draft</StatusPill>
          </div>
          <KpiTable kpis={pageKpis} />
        </section>
      </div>
    </div>
  );
}

function CaptureGroupSection({ group, onOpenReport }: { group: CaptureGroup; onOpenReport: (id: string) => void }) {
  return (
    <section className="ct-capture-group">
      <header>
        <StatusPill tone={group.priority === "P0" ? "rose" : "amber"}>{group.priority}</StatusPill>
        <div><strong>{group.purpose}</strong><span>{group.reports.length} named candidates retained for field and grain comparison</span></div>
      </header>
      <div className="ct-table-wrap">
        <table className="ct-table ct-source-table">
          <thead><tr><th>Report</th><th>Role</th><th>Why it remains in scope</th><th aria-label="Open report" /></tr></thead>
          <tbody>
            {group.reports.map((report) => (
              <tr key={report.reportId}>
                <td><strong>{report.name}</strong><code>{report.reportId}</code></td>
                <td><StatusPill tone={report.role === "primary_candidate" ? "green" : "neutral"}>{statusLabel(report.role)}</StatusPill></td>
                <td>{report.reason}</td>
                <td><button type="button" className="icon-button" onClick={() => onOpenReport(report.reportId)} data-tooltip="Open in Discovery" aria-label={`Open ${report.name} in Discovery`}><ExternalLink aria-hidden="true" size={14} /></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="ct-decision-gate"><ShieldCheck aria-hidden="true" size={14} /><span><strong>Selection gate:</strong> {group.decisionGate}</span></p>
    </section>
  );
}

function SourcePlan({
  requirements,
  onOpenReport,
}: Pick<ControlTowerWorkspaceProps, "requirements" | "onOpenReport">) {
  return (
    <div className="ct-reading-column">
      <section className="ct-progress-band">
        <FileSpreadsheet aria-hidden="true" size={19} />
        <div>
          <span className="section-kicker">Reported collection checkpoint</span>
          <strong>{requirements.discoveryProgress.reportedCheckpoint}</strong>
          <p>{requirements.discoveryProgress.note}</p>
        </div>
        <StatusPill tone="amber">Awaiting ingestion</StatusPill>
      </section>

      <section className="ct-section ct-principles">
        <div className="ct-section-heading">
          <div><ListChecks aria-hidden="true" size={16} /><span><strong>Capture rules</strong><small>Detailed without collecting duplicate reports blindly</small></span></div>
        </div>
        <ol>{requirements.capturePlan.principles.map((item, index) => <li key={item}><b>{index + 1}</b><span>{item}</span></li>)}</ol>
      </section>

      {requirements.capturePlan.groups.map((group) => (
        <CaptureGroupSection key={group.id} group={group} onOpenReport={onOpenReport} />
      ))}

      <section className="ct-section ct-deferred-band">
        <div className="ct-section-heading">
          <div><Layers3 aria-hidden="true" size={16} /><span><strong>Deferred from current discovery</strong><small>Retained in the full catalog; not deleted</small></span></div>
        </div>
        <div>{requirements.capturePlan.deferredAreas.map((area) => <span key={area}>{area}</span>)}</div>
      </section>
    </div>
  );
}

function DeliveryPlan({ requirements }: { requirements: ControlTowerRequirements }) {
  const deliveryRows = [
    ["POC ingestion", requirements.deliveryPlan.pocIngestion],
    ["Production ingestion", requirements.deliveryPlan.productionIngestion],
    ["Analytics", requirements.deliveryPlan.analytics],
    ["Presentation", requirements.deliveryPlan.presentation],
  ];
  const modelColumns = [
    ["Retain", requirements.modelRevision.retain],
    ["Revise", requirements.modelRevision.revise],
    ["Add", requirements.modelRevision.add],
    ["Defer", requirements.modelRevision.defer],
  ] as const;

  return (
    <div className="ct-reading-column">
      <section className="ct-decision-banner">
        <DatabaseZap aria-hidden="true" size={22} />
        <div>
          <span className="section-kicker">Architecture decision</span>
          <h2>Revise the existing 37-query model</h2>
          <p>{requirements.modelRevision.rationale}</p>
        </div>
        <StatusPill tone="green">Decision recorded</StatusPill>
      </section>

      <section className="ct-section">
        <div className="ct-section-heading">
          <div><Braces aria-hidden="true" size={16} /><span><strong>Hybrid source strategy</strong><small>Public documentation is candidate evidence; ABNAH UAT is still required</small></span></div>
          <StatusPill tone="amber">0 UAT verified</StatusPill>
        </div>
        <div className="ct-table-wrap">
          <table className="ct-table ct-api-fit-table">
            <thead><tr><th>Endpoint</th><th>Best fit</th><th>Documented coverage</th><th>Known gaps</th></tr></thead>
            <tbody>
              {requirements.apiAssessment.endpoints.map((endpoint) => (
                <tr key={endpoint.endpointId}>
                  <td><strong>{endpoint.name}</strong><code>{endpoint.endpointId}</code><StatusPill tone="blue">{endpoint.status}</StatusPill></td>
                  <td>{endpoint.fit}</td>
                  <td>{endpoint.coverage.join("; ")}</td>
                  <td>{endpoint.gaps.join("; ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="ct-section">
        <div className="ct-section-heading">
          <div><Layers3 aria-hidden="true" size={16} /><span><strong>Model change register</strong><small>Scope for the revised Zoho layer after source schemas are validated</small></span></div>
        </div>
        <div className="ct-model-grid">
          {modelColumns.map(([label, items]) => (
            <section key={label}>
              <header>{label}<b>{items.length}</b></header>
              <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
            </section>
          ))}
        </div>
      </section>

      <section className="ct-section">
        <div className="ct-section-heading">
          <div><DatabaseZap aria-hidden="true" size={16} /><span><strong>Delivery boundary</strong><small>Zoho-first implementation with a measured custom-shell decision</small></span></div>
        </div>
        <div className="ct-delivery-matrix">
          {deliveryRows.map(([label, body]) => <div key={label}><strong>{label}</strong><p>{body}</p></div>)}
        </div>
      </section>

      <section className="ct-section ct-validation-sequence">
        <div className="ct-section-heading">
          <div><ShieldCheck aria-hidden="true" size={16} /><span><strong>Validation sequence</strong><small>Publication gates from source capture to approved KPI</small></span></div>
        </div>
        <ol>{requirements.deliveryPlan.validationSequence.map((step, index) => <li key={step}><b>{index + 1}</b><span>{step}</span></li>)}</ol>
      </section>
    </div>
  );
}

export function ControlTowerWorkspace({ requirements, evidence, onOpenReport }: ControlTowerWorkspaceProps) {
  const [view, setView] = useState<ControlTowerView>("pages");
  const approvedKpis = requirements.kpis.filter((kpi) => kpi.approvalStatus === "approved").length;

  return (
    <section className="control-tower-surface">
      <header className="surface-header ct-surface-header">
        <div>
          <span className="section-kicker">Business requirements / source validation workspace</span>
          <h1>Supply Chain Control Tower</h1>
          <p>{requirements.pages.length} pages / {requirements.kpis.length} draft KPI definitions / {approvedKpis} approved / 0 UAT-verified endpoints</p>
        </div>
        <div className="ct-header-state"><ShieldCheck aria-hidden="true" size={15} /><span><strong>Requirements received</strong><small>Lineage remains unselected</small></span></div>
      </header>

      <nav className="ct-view-tabs" aria-label="Control tower planning views">
        <button type="button" className={view === "pages" ? "is-active" : ""} onClick={() => setView("pages")}><ListChecks aria-hidden="true" size={15} /> Page requirements</button>
        <button type="button" className={view === "sources" ? "is-active" : ""} onClick={() => setView("sources")}><FileSpreadsheet aria-hidden="true" size={15} /> Source capture plan</button>
        <button type="button" className={view === "evidence" ? "is-active" : ""} onClick={() => setView("evidence")}><ScanSearch aria-hidden="true" size={15} /> Selected sources & audit</button>
        <button type="button" className={view === "delivery" ? "is-active" : ""} onClick={() => setView("delivery")}><DatabaseZap aria-hidden="true" size={15} /> Model & delivery</button>
      </nav>

      {view === "pages" ? <PageRequirements requirements={requirements} /> : null}
      {view === "sources" ? <SourcePlan requirements={requirements} onOpenReport={onOpenReport} /> : null}
      {view === "evidence" ? <ControlTowerEvidenceView evidence={evidence} onOpenReport={onOpenReport} /> : null}
      {view === "delivery" ? <DeliveryPlan requirements={requirements} /> : null}
    </section>
  );
}
