"use client";

import { CircleDot, LockKeyhole, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";
import type { AtlasData } from "../lib/atlas-types";
import type { KpiLineageContract, LineageNode } from "../lib/lineage-types";

interface KpiLineageWorkspaceProps {
  atlas: AtlasData;
  lineage: KpiLineageContract;
}

const lanes = [
  { id: "source", label: "Source reports", kinds: ["source_report"] },
  { id: "raw", label: "RAW", kinds: ["raw"] },
  { id: "std", label: "STD", kinds: ["std"] },
  { id: "dim_fact", label: "DIM / FACT", kinds: ["dimension", "fact"] },
  { id: "sum", label: "SUM", kinds: ["summary"] },
  { id: "kpi", label: "KPI", kinds: ["kpi"] },
  { id: "chart", label: "Chart", kinds: ["chart"] },
] as const;

const humanStatus = (value: string) => value.replaceAll("_", " ");

export function KpiLineageWorkspace({ atlas, lineage }: KpiLineageWorkspaceProps) {
  const [selectedId, setSelectedId] = useState(lineage.kpis[0]?.id ?? "");
  const selectedKpi = lineage.kpis.find((kpi) => kpi.id === selectedId) ?? lineage.kpis[0];
  const selectedNodes = useMemo(
    () => lineage.nodes.filter((node) => node.kpiId === selectedKpi?.id),
    [lineage.nodes, selectedKpi?.id],
  );
  const selectedEdges = useMemo(
    () => lineage.edges.filter((edge) => edge.kpiId === selectedKpi?.id),
    [lineage.edges, selectedKpi?.id],
  );
  const draftCount = lineage.kpis.filter((kpi) => kpi.approvalStatus === "draft").length;
  const approvedCount = lineage.kpis.filter((kpi) => kpi.approvalStatus === "approved").length;
  const constrainedCount = lineage.kpis.filter((kpi) => ["blocked", "partial", "provisional"].includes(kpi.approvalStatus)).length;

  const nodesForLane = (kinds: readonly string[]) => selectedNodes.filter((node) => kinds.includes(node.kind));

  return (
    <section className="lineage-surface">
      <header className="surface-header">
        <div>
          <span className="section-kicker">One KPI at a time / factual source-to-chart mapping</span>
          <h1>KPI lineage</h1>
          <p>{draftCount} draft / {constrainedCount} constrained / {approvedCount} approved / {lineage.publications.length} published lineage maps / {atlas.reports.length} report candidates available</p>
        </div>
        <span className="locked-label"><LockKeyhole aria-hidden="true" size={14} /> Read-only mapping</span>
      </header>

      <div className="lineage-selector-band">
        <label>
          <span>KPI</span>
          <select value={selectedKpi?.id ?? ""} onChange={(event) => setSelectedId(event.target.value)} disabled={!lineage.kpis.length}>
            {lineage.kpis.length ? lineage.kpis.map((kpi) => <option key={kpi.id} value={kpi.id}>{kpi.name}</option>) : <option>No KPI definition available</option>}
          </select>
        </label>
        {selectedKpi ? <div className="lineage-definition-state"><span className={`status-label status-${selectedKpi.approvalStatus}`}>{selectedKpi.approvalStatus}</span><span>{humanStatus(selectedKpi.validationStatus)}</span></div> : null}
      </div>

      {selectedKpi ? (
        <section className="lineage-kpi-definition">
          <div><span>Business definition</span><p>{selectedKpi.businessDefinition}</p></div>
          <div><span>Formula</span><code>{selectedKpi.formula}</code></div>
          <div><span>Output grain</span><p>{selectedKpi.grain}</p></div>
          <div><span>Owner</span><p>{selectedKpi.owner}</p></div>
        </section>
      ) : null}

      <div className="lineage-canvas" aria-label="KPI lineage architecture">
        {lanes.map((lane) => {
          const laneNodes = nodesForLane(lane.kinds);
          return (
            <section key={lane.id} className="lineage-lane">
              <header><span>{lane.label}</span><b>{laneNodes.length}</b></header>
              <div className="lineage-lane-body">
                {laneNodes.map((node: LineageNode) => <div key={node.id} className="lineage-node"><CircleDot aria-hidden="true" size={13} /><strong>{node.label}</strong><small>{node.notes}</small></div>)}
              </div>
            </section>
          );
        })}
        {!selectedNodes.length ? (
          <div className="lineage-empty">
            <ShieldCheck aria-hidden="true" size={22} />
            <strong>Definition received; mapping not selected</strong>
            <span>Source candidates, joins, transformations, and chart edges stay empty until report schemas and UAT payloads validate the required grain.</span>
          </div>
        ) : null}
      </div>
      {selectedEdges.length ? <p className="lineage-edge-count">{selectedEdges.length} reviewed edges in this lineage.</p> : null}
    </section>
  );
}
