import { LockKeyhole } from "lucide-react";
import type { AtlasData } from "../lib/atlas-types";
import type { KpiLineageContract } from "../lib/lineage-types";

interface KpiLineageWorkspaceProps {
  atlas: AtlasData;
  lineage: KpiLineageContract;
}

const lanes = [
  { id: "source", label: "Source reports" },
  { id: "raw", label: "RAW" },
  { id: "std", label: "STD" },
  { id: "dim_fact", label: "DIM / FACT" },
  { id: "sum", label: "SUM" },
  { id: "kpi", label: "KPI" },
  { id: "chart", label: "Chart" },
];

export function KpiLineageWorkspace({ atlas, lineage }: KpiLineageWorkspaceProps) {
  const countForLane = (id: string) => {
    if (id === "source") return atlas.reports.length;
    if (id === "dim_fact") return atlas.models.filter((model) => ["dim", "fact"].includes(model.layer.toLowerCase())).length;
    if (["raw", "std", "sum"].includes(id)) return atlas.models.filter((model) => model.layer.toLowerCase() === id).length;
    return 0;
  };
  return (
    <section className="lineage-surface">
      <header className="surface-header">
        <div>
          <span className="section-kicker">Approved relational mapping</span>
          <h1>KPI lineage</h1>
          <p>{lineage.kpis.length} approved KPIs / {lineage.publications.length} published lineage maps</p>
        </div>
        <span className="locked-label"><LockKeyhole aria-hidden="true" size={14} /> Read-only</span>
      </header>
      <div className="lineage-selector-band">
        <label><span>KPI</span><select disabled><option>No approved KPI available</option></select></label>
      </div>
      <div className="lineage-canvas" aria-label="Empty KPI lineage architecture">
        {lanes.map((lane) => (
          <section key={lane.id} className="lineage-lane">
            <header><span>{lane.label}</span><b>{countForLane(lane.id)}</b></header>
            <div className="lineage-lane-body" />
          </section>
        ))}
        <div className="lineage-empty">
          <LockKeyhole aria-hidden="true" size={22} />
          <strong>Awaiting approved KPI definitions</strong>
          <span>The mapping canvas remains empty until business logic is confirmed.</span>
        </div>
      </div>
    </section>
  );
}
