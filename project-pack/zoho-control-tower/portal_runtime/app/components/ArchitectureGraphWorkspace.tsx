"use client";

import {
  ArrowRight,
  BadgeCheck,
  BarChart3,
  BookOpen,
  Braces,
  CalendarDays,
  Check,
  ChevronDown,
  ChevronRight,
  CircleDot,
  CloudSun,
  FileCode2,
  FileSpreadsheet,
  Filter,
  Gauge,
  GitBranch,
  MessageSquareText,
  PackageCheck,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  Table2,
  Target,
} from "lucide-react";
import { useMemo, useState } from "react";
import {
  activeAggregateMetrics,
  allDashboardFilters,
  architectureScopeTruth,
  calculationFamilies,
  controlTables,
  dashboardTabs,
  forecastProducts,
  journeyStages,
  queryTables,
  sourceGroups,
  unmappedFilters,
  type DashboardObject,
  type JourneyStageId,
} from "../lib/lean-architecture-data";
import {
  weatherGovernanceGates,
  weatherLandingTables,
  weatherQueryTables,
  weatherReports,
  ziaHelperTables,
  ziaNaturalLanguageLadder,
  ziaPresentationFlows,
  ziaSemanticDeployment,
  ziaWorkflowAcceptanceLedger,
  ziaWorkflows,
} from "../lib/architecture-extension-data";
import {
  aggregateMetricBuildGuides,
  dashboardFilterBuildGuides,
  dashboardObjectBuildGuide,
  dashboardTabBuildGuides,
  forecastProductBuildGuides,
} from "../lib/zoho-build-guides";

const stageIcons = {
  inputs: FileSpreadsheet,
  controls: Settings2,
  model: GitBranch,
  calculations: Braces,
  forecasting: Sparkles,
  outputs: BarChart3,
  filters: Filter,
  zia: MessageSquareText,
  weather: CloudSun,
  handoff: PackageCheck,
} satisfies Record<JourneyStageId, typeof FileSpreadsheet>;

function Pill({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`journey-pill tone-${tone}`}>{children}</span>;
}

function SeeMore({ children, label = "See more details" }: { children: React.ReactNode; label?: string }) {
  return (
    <details className="journey-see-more">
      <summary><span>{label}</span><ChevronDown aria-hidden="true" size={15} /></summary>
      <div className="journey-see-more-body">{children}</div>
    </details>
  );
}

function StepList({ steps }: { steps: readonly string[] }) {
  return <ol className="journey-step-list">{steps.map((step, index) => <li key={`${index}-${step}`}><span>{index + 1}</span><p>{step}</p></li>)}</ol>;
}

function SourceInputs({ onOpenDiscovery }: { onOpenDiscovery?: () => void } = {}) {
  const [selected, setSelected] = useState<(typeof sourceGroups)[number]["id"]>(sourceGroups[0].id);
  const group = sourceGroups.find((item) => item.id === selected) ?? sourceGroups[0];
  return (
    <div className="journey-detail-grid is-source">
      <section className="journey-reading-card journey-intro-card">
        <span className="section-kicker">Source contract</span>
        <h2>Load source-shaped tables first</h2>
        <p>
          The model preserves source labels and physical dates. Operational
          rows are appended; recipe, vendor and control tables are governed
          references. No dashboard formula repairs a missing source grain.
        </p>
        <div className="journey-stat-row">
          <span><b>18</b><small>operational</small></span>
          <span><b>2</b><small>reference</small></span>
          <span><b>1</b><small>provisional</small></span>
          <span><b>5</b><small>control</small></span>
        </div>
        <div className="journey-callout is-amber">
          <ShieldCheck aria-hidden="true" size={16} />
          <div><strong>Expiry boundary</strong><span>The expiry source is a clearly labelled provisional synthetic demonstration until the POSIST expiry export is enabled.</span></div>
        </div>
        <div className="journey-discovery-bridge">
          <div>
            <span className="section-kicker">Architecture → green Discovery</span>
            <strong>20 selected report schemas</strong>
            <p>The handoff coverage checkpoint is 17 structurally captured, 1 partial and 2 pending. Open Discovery for the structural schema record; this status is not private image coverage or production readiness.</p>
          </div>
          <div className="journey-discovery-coverage" aria-label="Selected report schema coverage">
            <span className="is-captured"><b>17</b><small>captured</small></span>
            <span className="is-partial"><b>1</b><small>partial</small></span>
            <span className="is-pending"><b>2</b><small>pending</small></span>
          </div>
          <button type="button" onClick={onOpenDiscovery} disabled={!onOpenDiscovery}><FileSpreadsheet aria-hidden="true" size={14} /> Open green Discovery</button>
        </div>
      </section>
      <section className="journey-browser-card">
        <nav className="journey-segmented" aria-label="Source table family">
          {sourceGroups.map((item) => (
            <button key={item.id} type="button" className={selected === item.id ? "is-active" : ""} onClick={() => setSelected(item.id)}>
              {item.label}<small>{item.items.length}</small>
            </button>
          ))}
        </nav>
        <header className="journey-browser-heading">
          <div><strong>{group.label}</strong><p>{group.summary}</p></div>
          <Pill tone={group.id === "provisional" ? "amber" : "green"}>{group.items.length} tables</Pill>
        </header>
        <div className="journey-chip-grid">
          {group.items.map((item) => <code key={item}>{item}</code>)}
        </div>
      </section>
    </div>
  );
}

function GovernedControls() {
  const [selected, setSelected] = useState<(typeof controlTables)[number]["name"]>(controlTables[0].name);
  const control = controlTables.find((item) => item.name === selected) ?? controlTables[0];
  return (
    <div className="journey-list-detail">
      <aside className="journey-object-list" aria-label="Control tables">
        {controlTables.map((item, index) => (
          <button key={item.name} type="button" className={item.name === control.name ? "is-active" : ""} onClick={() => setSelected(item.name)}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <div><strong>{item.name}</strong><small>{item.role}</small></div>
            <ChevronRight aria-hidden="true" size={15} />
          </button>
        ))}
      </aside>
      <article className="journey-object-detail">
        <header>
          <span><Settings2 aria-hidden="true" size={18} /></span>
          <div><small>{control.role}</small><h2>{control.name}</h2></div>
        </header>
        <div className="journey-two-step">
          <section><label>What is governed</label><p>{control.changes}</p></section>
          <ArrowRight aria-hidden="true" size={18} />
          <section><label>What changes downstream</label><p>{control.effect}</p></section>
        </div>
        <section className="journey-example-band">
          <label>Current examples</label>
          <div>{control.examples.map((item) => <code key={item}>{item}</code>)}</div>
        </section>
        <div className="journey-callout">
          <BadgeCheck aria-hidden="true" size={16} />
          <div><strong>Change once, refresh the model</strong><span>Effective-dated controls keep thresholds and conversion rules editable without hard-coding them independently into every report.</span></div>
        </div>
        <SeeMore label={`See more details: govern ${control.name}`}>
          <div className="journey-detail-facts">
            <section><label>Exact Zoho table</label><code>{control.name}</code></section>
            <section><label>Business role</label><p>{control.role}</p></section>
          </div>
          <section className="journey-detail-section"><label>Fields and current examples</label><div className="journey-detail-chips">{control.examples.map((item) => <code key={item}>{item}</code>)}</div></section>
          <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={[
            `Open Data and locate the existing table named ${control.name}; preserve that exact name.`,
            "Open the active/effective-dated row and change only the approved business value or mapping.",
            "Save the table, then refresh the dependent Query Tables in their documented build order.",
            "Open one downstream KPI/report and reconcile its filtered rows before presenting the change.",
            "Record the approved control change; never repair a control threshold inside an individual report formula.",
          ]} /></section>
        </SeeMore>
      </article>
    </div>
  );
}

function LeanModel() {
  const [selectedName, setSelectedName] = useState(queryTables[0].name);
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return queryTables.filter((item) => !needle || [item.name, item.purpose, item.grain, ...item.dependencies, ...item.derived].some((value) => value.toLowerCase().includes(needle)));
  }, [query]);
  const selected = filtered.find((item) => item.name === selectedName) ?? filtered[0];
  return (
    <div className="journey-model">
      <aside className="journey-model-index">
        <label className="journey-search">
          <Search aria-hidden="true" size={14} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find table, field or dependency" aria-label="Search the ten Query Tables" />
        </label>
        <div className="journey-level-legend">
          <span><i data-level="1" />Level 1 · early aggregation</span>
          <span><i data-level="2" />Level 2 · business evidence</span>
          <span><i data-level="3" />Level 3 · action output</span>
        </div>
        <nav aria-label="Ten Query Tables">
          {filtered.map((item) => (
            <button key={item.name} type="button" className={item.name === selected?.name ? "is-active" : ""} onClick={() => setSelectedName(item.name)}>
              <span data-level={item.level}>{String(item.order).padStart(2, "0")}</span>
              <div><strong>{item.name}</strong><small>Level {item.level} · {item.dateField}</small></div>
              <ChevronRight aria-hidden="true" size={14} />
            </button>
          ))}
        </nav>
      </aside>
      {selected ? (
        <article className="journey-model-detail">
          <header>
            <div>
              <span className="section-kicker">Build {String(selected.order).padStart(2, "0")} / dependency level {selected.level}</span>
              <h2>{selected.name}</h2>
              <p>{selected.purpose}</p>
            </div>
            <Pill tone="blue">{selected.dateField}</Pill>
          </header>
          <dl className="journey-model-facts">
            <div><dt>Contracted grain</dt><dd>{selected.grain}</dd></div>
            <div><dt>Primary date</dt><dd><code>{selected.dateField}</code></dd></div>
          </dl>
          <section className="journey-dependency-band">
            <label>Inputs</label>
            <div>{selected.dependencies.map((item) => <code key={item}>{item}</code>)}</div>
          </section>
          <div className="journey-model-columns">
            <section>
              <label>Key fields produced</label>
              <ul>{selected.derived.map((item) => <li key={item}><Check aria-hidden="true" size={13} /><code>{item}</code></li>)}</ul>
            </section>
            <section>
              <label>Feeds</label>
              <ul>{selected.feeds.map((item) => <li key={item}><ArrowRight aria-hidden="true" size={13} /><span>{item}</span></li>)}</ul>
            </section>
          </div>
          <a className="journey-sql-link" href={`./architecture/sql/${selected.sqlFile}`} target="_blank" rel="noreferrer">
            <FileCode2 aria-hidden="true" size={16} /> Open exact Zoho SQL <small>{selected.sqlFile}</small>
          </a>
          <SeeMore label={`See more details: create ${selected.name}`}>
            <div className="journey-detail-facts">
              <section><label>Exact object name</label><code>{selected.name}</code></section>
              <section><label>Output grain</label><p>{selected.grain}</p></section>
              <section><label>Physical date</label><code>{selected.dateField}</code></section>
              <section><label>Dependency level</label><p>Level {selected.level} · build position {selected.order} of 10</p></section>
            </div>
            <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={[
              "In Zoho Analytics choose Create > New Query Table.",
              `Name it exactly ${selected.name}.`,
              `Open ${selected.sqlFile} from the exact SQL link above and paste the complete statement without renaming source tables or output aliases.`,
              "Execute the query and resolve only real schema errors; do not replace missing data with fabricated constants.",
              `Confirm the physical ${selected.dateField} column, contracted grain, and key output fields shown above.`,
              "Save, refresh its dependents in build order, then verify one filtered downstream object before continuing.",
            ]} /></section>
            <div className="journey-callout is-blue"><ShieldCheck size={15} /><span>Use the downloadable SQL as the source of truth. The short purpose text is a navigation aid, not a substitute for the query.</span></div>
          </SeeMore>
        </article>
      ) : <div className="journey-empty"><Search size={20} /><strong>No matching Query Table</strong></div>}
    </div>
  );
}

function Calculations() {
  const [family, setFamily] = useState<(typeof calculationFamilies)[number]["id"]>(calculationFamilies[0].id);
  const [showMetrics, setShowMetrics] = useState(false);
  const selected = calculationFamilies.find((item) => item.id === family) ?? calculationFamilies[0];
  return (
    <div className="journey-calculations">
      <section className="journey-formula-story">
        <header><span className="section-kicker">SQL formula columns</span><h2>Calculate at the correct row grain first</h2><p>Each chain preserves the physical date and business key before it is summarized in a chart or KPI.</p></header>
        <nav aria-label="Calculation families">
          {calculationFamilies.map((item) => (
            <button key={item.id} type="button" className={item.id === selected.id ? "is-active" : ""} onClick={() => setFamily(item.id)}>
              <strong>{item.label}</strong><small>{item.base}</small>
            </button>
          ))}
        </nav>
        <div className="journey-formula-focus">
          <div><label>Exact business equation</label><code>{selected.formula}</code></div>
          <ArrowRight aria-hidden="true" size={18} />
          <div><label>Result</label><p>{selected.result}</p></div>
        </div>
      </section>
      <section className="journey-metric-register">
        <header>
          <div><span className="section-kicker">Unified Metrics</span><h2>14 active aggregate formulas</h2><p>Only filter-safe sums, distinct counts and ratios of sums remain on production report shelves.</p></div>
          <button type="button" onClick={() => setShowMetrics((value) => !value)} aria-expanded={showMetrics}>{showMetrics ? "Collapse register" : "Open metric register"}<ChevronRight aria-hidden="true" size={15} /></button>
        </header>
        <div className="journey-retired-note"><ShieldCheck size={15} /><span><strong>Timeline-variable AF_SE formulas are retired.</strong> Production state reports map directly to physical <code>as_of_date</code>; flow reports map to their own physical date.</span></div>
        {showMetrics ? (
          <div className="journey-metric-table" role="region" aria-label="Active aggregate formulas">
            {activeAggregateMetrics.map(([name, base, formula, meaning], index) => (
              <article key={name}>
                <span>{String(index + 1).padStart(2, "0")}</span><div><strong>{name}</strong><small>{base}</small></div><code>{formula}</code><p>{meaning}</p>
                <SeeMore label="See more details">
                  {(() => {
                    const guide = aggregateMetricBuildGuides[name];
                    return guide ? <>
                      <div className="journey-detail-facts">
                        <section><label>Owner table</label><code>{base}</code></section>
                        <section><label>Formula name</label><code>{name}</code></section>
                        <section><label>Data type / format</label><p>{guide.dataType} · {guide.display}</p></section>
                        <section><label>Unified Metrics</label><p>{guide.priority} · {guide.synonyms}</p></section>
                      </div>
                      <section className="journey-detail-section"><label>Exact expression</label><pre>{guide.expression}</pre></section>
                      <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={[
                        `Open ${base} in Zoho Analytics.`,
                        "Choose Add > Aggregate Formula, or edit the existing formula through Edit Design > Add / Edit Formulas.",
                        `Enter the formula name exactly as ${name} and paste the exact expression above.`,
                        `Set Data Type to ${guide.dataType} and format it as ${guide.display}.`,
                        `Save, reopen the formula, set Unified Metrics priority ${guide.priority}, add the listed business synonyms, and reconcile one filtered result.`,
                      ]} /></section>
                      <div className="journey-callout is-amber"><ShieldCheck size={15} /><span>{guide.guardrail}</span></div>
                    </> : null;
                  })()}
                </SeeMore>
              </article>
            ))}
          </div>
        ) : (
          <div className="journey-metric-preview">
            {activeAggregateMetrics.slice(0, 4).map(([name, base, formula]) => <article key={name}><strong>{name}</strong><small>{base}</small><code>{formula}</code></article>)}
          </div>
        )}
      </section>
    </div>
  );
}

function Forecasting() {
  const [selectedId, setSelectedId] = useState<(typeof forecastProducts)[number]["id"]>(forecastProducts[0].id);
  const forecast = forecastProducts.find((item) => item.id === selectedId) ?? forecastProducts[0];
  const guide = forecastProductBuildGuides[forecast.id];
  return (
    <div className="journey-forecasting">
      <section className="journey-forecast-cards">
        {forecastProducts.map((item, index) => (
          <button key={item.id} type="button" className={item.id === forecast.id ? "is-active" : ""} onClick={() => setSelectedId(item.id)}>
            <span>{String(index + 1).padStart(2, "0")}</span><Pill tone={item.id === "automl" ? "amber" : "green"}>{item.state}</Pill><strong>{item.label}</strong><p>{item.question}</p>
          </button>
        ))}
      </section>
      <article className="journey-forecast-detail">
        <header><Sparkles aria-hidden="true" size={19} /><div><small>{forecast.state}</small><h2>{forecast.label}</h2></div></header>
        <section><label>How it works</label><p>{forecast.method}</p></section>
        <section><label>Data route</label><code>{forecast.route}</code></section>
        <div className="journey-callout is-blue"><ShieldCheck size={16} /><div><strong>Reuse boundary</strong><span>{forecast.boundary}</span></div></div>
        {forecast.id === "native" ? (
          <div className="journey-native-strip">
            <span><b>FC04R / FC04</b><small>Daily / category net sales</small></span>
            <span><b>FC05</b><small>Category theoretical margin</small></span>
            <span><b>FC06</b><small>Category menu units</small></span>
            <i>7 daily forecast periods</i>
          </div>
        ) : null}
        <SeeMore label={`See more details: build ${forecast.label}`}>
          <section className="journey-detail-section"><label>Exact Zoho entities</label><ul>{guide.entities.map((item) => <li key={item}>{item}</li>)}</ul></section>
          <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={guide.steps} /></section>
        </SeeMore>
      </article>
    </div>
  );
}

function ObjectDetail({ object }: { object: DashboardObject }) {
  const unmapped = unmappedFilters(object);
  const guide = dashboardObjectBuildGuide(object);
  return (
    <article className="journey-report-detail">
      <header>
        <div><Pill tone={object.kind === "KPI" ? "green" : "blue"}>{object.kind}</Pill><h2>{object.name}</h2><p>{object.question}</p></div>
        <code>{object.base}</code>
      </header>
      <div className="journey-report-build">
        <section><label>Measure / shelves</label><p>{object.measure}</p></section>
        <section><label>Fixed report scope</label>{object.fixed.length ? <ul>{object.fixed.map((item) => <li key={item}>{item}</li>)}</ul> : <p>None</p>}</section>
      </div>
      <section className="journey-report-mappings">
        <label>Dashboard filter mapping</label>
        <div>{Object.entries(object.mappings).map(([filter, column]) => <span key={filter}><b>{filter}</b><ArrowRight size={12} /><code>{column}</code></span>)}</div>
      </section>
      <section className="journey-unmapped"><label>Intentionally unmapped</label><p>{unmapped.join(" · ")}</p></section>
      {object.note ? <div className="journey-callout is-amber"><CircleDot size={15} /><span>{object.note}</span></div> : null}
      <SeeMore label={`See more details: build ${object.name}`}>
        <div className="journey-detail-facts">
          <section><label>Create as</label><p>{guide.visual}</p></section>
          <section><label>Exact base table</label><code>{object.base}</code></section>
          <section><label>Live status</label><p>{guide.status}</p></section>
          <section><label>Exact saved title</label><code>{object.name}</code></section>
        </div>
        <section className="journey-detail-section">
          <label>Columns, shelves and aggregation</label>
          <ul>{(guide.shelves ?? [object.measure]).map((item) => <li key={item}>{item}</li>)}</ul>
        </section>
        <section className="journey-detail-section">
          <label>Fixed filters inside the object</label>
          {object.fixed.length ? <ul>{object.fixed.map((item) => <li key={item}>{item}</li>)}</ul> : <p>None. Do not add a fixed date or outlet.</p>}
        </section>
        <section className="journey-detail-section">
          <label>Dashboard user-filter mapping</label>
          <div className="journey-detail-mapping">{Object.entries(object.mappings).map(([filter, column]) => <span key={filter}><b>{filter}</b><ArrowRight size={12} /><code>{column}</code></span>)}</div>
          <p className="journey-muted-line"><strong>Leave unmapped:</strong> {unmapped.join(" · ")}</p>
        </section>
        <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={[
          `${object.kind === "KPI" ? "Edit the dashboard and choose Widget > KPI" : `Choose Create > New Report > ${guide.visual}`} using ${object.base}.`,
          `Set the visible/saved title exactly to ${object.name}.`,
          "Drag the exact columns to the shelves above and select the stated aggregation; do not accept Zoho's automatic aggregation without checking it.",
          object.fixed.length ? "Add only the listed fixed business filters inside the object, then save it." : "Keep the object free of fixed business/date filters, then save it.",
          "Place it on the named dashboard tab, open Customize dashboard filters, and map only the listed compatible controls.",
          "Apply the formatting below, enter View Mode, test All plus one narrowed scope, and inspect Underlying Data before acceptance.",
        ]} /></section>
        {guide.formatting.length ? <section className="journey-detail-section"><label>Formatting</label><ul>{guide.formatting.map((item) => <li key={item}>{item}</li>)}</ul></section> : null}
        <div className="journey-acceptance-grid">
          <section><label>Acceptance proof</label><p>{guide.acceptance}</p></section>
          <section><label>Legitimate No Data</label><p>{guide.noData}</p></section>
        </div>
      </SeeMore>
    </article>
  );
}

function DecisionOutputs() {
  const [tabId, setTabId] = useState(dashboardTabs[0].id);
  const tab = dashboardTabs.find((item) => item.id === tabId) ?? dashboardTabs[0];
  const [objectName, setObjectName] = useState(tab.objects[0].name);
  const selected = tab.objects.find((item) => item.name === objectName) ?? tab.objects[0];
  const selectTab = (id: string) => {
    const next = dashboardTabs.find((item) => item.id === id) ?? dashboardTabs[0];
    setTabId(id);
    setObjectName(next.objects[0].name);
  };
  return (
    <div className="journey-outputs">
      <nav className="journey-dashboard-tabs" aria-label="Final dashboard tabs">
        {dashboardTabs.map((item) => <button key={item.id} type="button" className={item.id === tab.id ? "is-active" : ""} onClick={() => selectTab(item.id)}><span>{item.label.slice(0, 2)}</span><div><strong>{item.label.slice(3)}</strong><small>{item.objects.length} objects</small></div></button>)}
      </nav>
      <header className="journey-tab-purpose"><div><span className="section-kicker">Final dashboard tab</span><h2>{tab.label}</h2><p>{tab.purpose}</p></div><div>{tab.visibleFilters.map((item) => <Pill key={item}>{item}</Pill>)}</div></header>
      <div className="journey-tab-build">
        <SeeMore label={`See more details: assemble ${tab.label}`}>
          {(() => {
            const guide = dashboardTabBuildGuides[tab.id];
            return guide ? <>
              <div className="journey-detail-facts">
                <section><label>Dashboard</label><code>DB_02_ABNAH_SCM_Control_Tower_Final</code></section>
                <section><label>Exact tab</label><code>{tab.label}</code></section>
              </div>
              <section className="journey-detail-section"><label>Filter rows</label><ul>{guide.filters.map((item) => <li key={item}>{item}</li>)}</ul></section>
              <section className="journey-detail-section"><label>Placement blueprint</label><ul>{guide.rows.map((item) => <li key={item}>{item}</li>)}</ul></section>
              <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={guide.steps} /></section>
            </> : null;
          })()}
        </SeeMore>
      </div>
      <div className="journey-output-browser">
        <aside aria-label={`${tab.label} objects`}>
          {tab.objects.map((item) => <button key={item.name} type="button" className={item.name === selected.name ? "is-active" : ""} onClick={() => setObjectName(item.name)}><span data-kind={item.kind}>{item.kind === "KPI" ? <Gauge size={14} /> : item.kind === "Action table" || item.kind === "Pivot" ? <Table2 size={14} /> : <BarChart3 size={14} />}</span><div><strong>{item.name}</strong><small>{item.base}</small></div><ChevronRight size={14} /></button>)}
        </aside>
        <ObjectDetail object={selected} />
      </div>
    </div>
  );
}

function FilterContract() {
  const [filter, setFilter] = useState<(typeof allDashboardFilters)[number]>(allDashboardFilters[0]);
  const guide = dashboardFilterBuildGuides[filter];
  const mapped = dashboardTabs.flatMap((tab) => tab.objects.map((object) => ({ tab, object, column: object.mappings[filter] }))).filter((item) => item.column);
  const grouped = dashboardTabs.map((tab) => ({ tab, objects: mapped.filter((item) => item.tab.id === tab.id) }));
  return (
    <div className="journey-filter-contract">
      <section className="journey-filter-principle">
        <header><CalendarDays size={19} /><div><span className="section-kicker">Non-negotiable date semantics</span><h2>Period measures flow. Snapshot measures state.</h2></div></header>
        <div>
          <article><Pill tone="blue">Reporting Period</Pill><strong>What flowed during this range?</strong><p>Sales, orders, receipts, consumption, margin, price movement and dated data quality map to their own physical date.</p></article>
          <article><Pill tone="green">Snapshot As Of</Pill><strong>What was true on this exact day?</strong><p>Risk, inventory, expiry and open-PO state map to one physical <code>as_of_date</code>. All is disabled; no multi-date summation.</p></article>
        </div>
      </section>
      <section className="journey-filter-browser">
        <header><div><span className="section-kicker">Exact report mapping</span><h2>Select a dashboard filter</h2><p>Only compatible objects receive a mapping. Every omitted mapping is intentional.</p></div><Pill tone="green">{mapped.length} mapped objects</Pill></header>
        <nav aria-label="Dashboard filters">
          {allDashboardFilters.map((item) => <button key={item} type="button" className={item === filter ? "is-active" : ""} onClick={() => setFilter(item)}>{item}</button>)}
        </nav>
        <SeeMore label={`See more details: create ${filter}`}>
          <div className="journey-detail-facts">
            <section><label>Control type</label><p>{guide.control}</p></section>
            <section><label>Seed column</label><code>{guide.seed}</code></section>
            <section><label>Visible tabs</label><p>{guide.tabs}</p></section>
            <section><label>Default</label><p>{guide.defaultValue}</p></section>
          </div>
          <section className="journey-detail-section"><label>Mapping rule</label><p>{guide.mappingRule}</p></section>
          <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={guide.steps} /></section>
          <div className="journey-callout is-amber"><ShieldCheck size={15} /><span>{guide.warning}</span></div>
        </SeeMore>
        <div className="journey-filter-groups">
          {grouped.map(({ tab, objects }) => (
            <article key={tab.id}>
              <header><strong>{tab.label}</strong><small>{objects.length} mapped</small></header>
              {objects.length ? objects.map(({ object, column }) => <div key={object.name}><span>{object.name}</span><ArrowRight size={12} /><code>{column}</code></div>) : <p>Intentionally unmapped from every object on this tab.</p>}
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function ZiaSemanticLayer() {
  const [mode, setMode] = useState<"helpers" | "deployment" | "workflows" | "presentation">("helpers");
  const [helperName, setHelperName] = useState(ziaHelperTables[0].name);
  const [workflowId, setWorkflowId] = useState(ziaWorkflows[0].id);
  const helper = ziaHelperTables.find((item) => item.name === helperName) ?? ziaHelperTables[0];
  const workflow = ziaWorkflows.find((item) => item.id === workflowId) ?? ziaWorkflows[0];

  return (
    <div className="journey-extension">
      <header className="journey-extension-header">
        <div>
          <span className="section-kicker">Curated semantic layer</span>
          <h2>Ask Zia is governed by two acceptance gates</h2>
          <p>Source reconciliation remains PASS, but live conversational evidence is mixed: WAT 22 is {ziaWorkflowAcceptanceLedger.currentLedger}; the 66-test ladder is {ziaNaturalLanguageLadder.currentLedger}. The original semantic contract, ZLD009, corrected ZLD037 and the governed aggregate formula remain read back. Five additive purpose-separated helpers were created or recreated and reconciled; the original 9/9 critical UI readbacks passed, and the replacement QT09 three-field targeted readback passed 3/3. Its indexed WAT08 retry still selected the raw PO source and generated unsafe cross-UOM output. Other targeted smokes remain pending, no workflow is presentation-ready and the gate remains BLOCKED.</p>
        </div>
        <div className="journey-extension-metrics" aria-label="Ask Zia acceptance summary">
          <span className="is-blocked"><b>67</b><small>scoped readback; descriptions uncertified</small></span>
          <span className="is-blocked"><b>7 / 9 / 6</b><small>WAT pass / partial / fail</small></span>
          <span className="is-blocked"><b>7 / 9 / 50</b><small>ladder pass / partial / fail</small></span>
          <span className="is-blocked"><b>BLOCKED</b><small>presentation gate</small></span>
        </div>
      </header>
      <nav className="journey-extension-switcher" aria-label="Ask Zia architecture views">
        <button type="button" className={mode === "helpers" ? "is-active" : ""} onClick={() => setMode("helpers")}>Helper Query Tables</button>
        <button type="button" className={mode === "deployment" ? "is-active" : ""} onClick={() => setMode("deployment")}>67 actions · 66-test ladder</button>
        <button type="button" className={mode === "workflows" ? "is-active" : ""} onClick={() => setMode("workflows")}>11-workflow gate</button>
        <button type="button" className={mode === "presentation" ? "is-active" : ""} onClick={() => setMode("presentation")}>Presentation flows</button>
      </nav>

      {mode === "helpers" ? (
        <div className="journey-model journey-extension-browser">
          <aside className="journey-model-index">
            <div className="journey-extension-note"><ShieldCheck size={15} /><span>These helpers sit beside the ten core Query Tables. None replaces or edits the core model.</span></div>
            <nav aria-label="Ask Zia helper Query Tables">
              {ziaHelperTables.map((item) => (
                <button key={item.name} type="button" className={item.name === helper.name ? "is-active" : ""} onClick={() => setHelperName(item.name)}>
                  <span data-level={item.name.startsWith("ZIA_01") ? 3 : 2}>{String(item.order).padStart(2, "0")}</span>
                  <div><strong>{item.name}</strong><small>{item.workflows.join(" · ")}</small></div>
                  <ChevronRight aria-hidden="true" size={14} />
                </button>
              ))}
            </nav>
          </aside>
          <article className="journey-model-detail">
            <header>
              <div><span className="section-kicker">Live semantic helper</span><h2>{helper.name}</h2><p>{helper.purpose}</p></div>
              <Pill tone={helper.deploymentStatus.includes("REQUIRED") || helper.deploymentStatus.includes("BLOCKED") ? "amber" : "green"}>{helper.deploymentStatus}</Pill>
            </header>
            <dl className="journey-model-facts">
              <div><dt>Contracted grain</dt><dd>{helper.grain}</dd></div>
              <div><dt>Live view ID</dt><dd><code>{helper.viewId}</code></dd></div>
            </dl>
            <section className="journey-dependency-band"><label>Core / curated dependencies</label><div>{helper.dependencies.map((item) => <code key={item}>{item}</code>)}</div></section>
            <div className="journey-model-columns">
              <section><label>Key fields exposed</label><ul>{helper.keyFields.slice(0, 8).map((item) => <li key={item}><Check size={13} /><code>{item}</code></li>)}</ul></section>
              <section><label>Workflows served</label><ul>{helper.workflows.map((item) => <li key={item}><ArrowRight size={13} /><span>{item}</span></li>)}</ul></section>
            </div>
            <div className="journey-callout is-amber"><CircleDot size={15} /><div><strong>Why this helper exists</strong><span>{helper.whyItExists}</span></div></div>
            <SeeMore label={`See more details: govern ${helper.name}`}>
              <div className="journey-detail-facts">
                <section><label>Exact object</label><code>{helper.name}</code></section>
                <section><label>Live view ID</label><code>{helper.viewId}</code></section>
                <section><label>Output grain</label><p>{helper.grain}</p></section>
                <section><label>Source acceptance</label><p>{helper.acceptanceControl}</p></section>
              </div>
              <section className="journey-detail-section"><label>Full curated field set</label><div className="journey-detail-chips">{helper.keyFields.map((item) => <code key={item}>{item}</code>)}</div></section>
              {helper.sqlPurpose ? <section className="journey-detail-section"><label>Business-readable SQL purpose</label><p>{helper.sqlPurpose}</p></section> : null}
              <section className="journey-detail-section"><label>Guardrails</label><ul>{helper.guardrails.map((item) => <li key={item}>{item}</li>)}</ul></section>
              <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={helper.steps} /></section>
            </SeeMore>
          </article>
        </div>
      ) : null}

      {mode === "deployment" ? (
        <div className="journey-zia-plan">
          <section className="journey-zia-plan-column">
            <header>
              <div><span className="section-kicker">Live semantic deployment contract</span><h2>67 ordered actions</h2><p>{ziaSemanticDeployment.liveEvidence}</p></div>
              <Pill tone="amber">SCOPED READBACK</Pill>
            </header>
            <div className="journey-zia-breakdown">
              {ziaSemanticDeployment.actionBreakdown.map((item) => (
                <article key={item.label}><span>{item.count}</span><div><strong>{item.label}</strong><p>{item.detail}</p></div></article>
              ))}
            </div>
            <SeeMore label={`See more details: deploy ${ziaSemanticDeployment.actionCount} semantic actions`}>
              <div className="journey-detail-facts">
                <section><label>Exact artifact</label><code>{ziaSemanticDeployment.artifact}</code></section>
                <section><label>Underlying base contract</label><p>{ziaSemanticDeployment.baseSemanticRowCount} semantic rows</p></section>
                <section><label>Current truth</label><p>{ziaSemanticDeployment.status}</p></section>
                <section><label>WF08 live field</label><code>Expected Delivery</code></section>
              </div>
              <section className="journey-detail-section"><label>Deployment and read-back sequence</label><StepList steps={ziaSemanticDeployment.deploymentSteps} /></section>
            </SeeMore>
          </section>

          <section className="journey-zia-plan-column">
            <header>
              <div><span className="section-kicker">Natural-language acceptance contract</span><h2>66 tests across 11 workflows</h2><p>Six tests per workflow prove ordinary wording, safe routing, context retention and governed refusal—not merely a source calculation.</p></div>
              <Pill tone="amber">7 PASS · 9 PARTIAL · 50 FAIL</Pill>
            </header>
            <div className="journey-zia-tiers">
              {ziaNaturalLanguageLadder.tiers.map((tier) => (
                <article key={tier.id}><span>{tier.id}</span><div><strong>{tier.label}</strong><small>{tier.count} tests</small><p>{tier.rule}</p></div></article>
              ))}
            </div>
            <div className="journey-callout is-amber"><ShieldCheck size={15} /><div><strong>Acceptance remains blocked</strong><span>{ziaNaturalLanguageLadder.acceptanceRule} Current ledger: {ziaNaturalLanguageLadder.currentLedger}.</span></div></div>
            <SeeMore label={`See more details: run the ${ziaNaturalLanguageLadder.testCount}-test ladder`}>
              <div className="journey-detail-facts">
                <section><label>Exact artifact</label><code>{ziaNaturalLanguageLadder.artifact}</code></section>
                <section><label>Workflow coverage</label><p>{ziaNaturalLanguageLadder.workflowCount} workflows × 6 tiers</p></section>
                <section><label>Current truth</label><p>{ziaNaturalLanguageLadder.status}</p></section>
                <section><label>Recorded live ledger</label><p>{ziaNaturalLanguageLadder.currentLedger}</p></section>
              </div>
            </SeeMore>
          </section>
        </div>
      ) : null}

      {mode === "workflows" ? (
        <div className="journey-output-browser journey-zia-workflows">
          <aside aria-label="Ask Zia workflow acceptance matrix">
            {ziaWorkflows.map((item) => (
              <button key={item.id} type="button" className={item.id === workflow.id ? "is-active" : ""} onClick={() => setWorkflowId(item.id)}>
                <span><MessageSquareText size={14} /></span>
                <div><strong>{item.id} · {item.name}</strong><small>{item.primaryObject}</small></div>
                <ChevronRight size={14} />
              </button>
            ))}
          </aside>
          <article className="journey-report-detail journey-zia-detail">
            <header><div><Pill tone="blue">{workflow.id}</Pill><h2>{workflow.name}</h2><p>{workflow.prompt}</p></div><code>{workflow.primaryObject}</code></header>
            <div className="journey-gate-grid">
              <section className="is-pass"><label>Source reconciliation</label><strong>{workflow.sourceStatus}</strong><p>Validated by the live numerical control suite.</p></section>
              <section className="is-blocked"><label>Ask Zia conversation</label><strong>{workflow.conversationStatus} primary / {workflow.followUpStatus} follow-up</strong><p>These are the two WAT results. Full readiness still requires the six-tier ladder, and no workflow has passed that presentation gate.</p></section>
              <section><label>Presentation decision</label><strong>BLOCKED</strong><p>{workflow.presentationStatus}</p></section>
            </div>
            <div className="journey-report-build">
              <section><label>Date contract</label><p>{workflow.dateContract}</p></section>
              <section><label>Filter contract</label><p>{workflow.filterContract}</p></section>
              <section><label>Aggregation contract</label><p>{workflow.aggregationContract}</p></section>
              <section><label>Expected numerical control</label><p>{workflow.expectedControl}</p></section>
            </div>
            <div className="journey-callout is-amber"><MessageSquareText size={15} /><div><strong>Current live evidence</strong><span>{workflow.liveFinding}</span></div></div>
            <div className="journey-callout is-amber"><ShieldCheck size={15} /><div><strong>Negative control</strong><span>{workflow.negativeControl}</span></div></div>
            <SeeMore label={`See more details: test ${workflow.id} end to end`}>
              <section className="journey-detail-section"><label>Exact prompt</label><pre>{workflow.prompt}</pre></section>
              <section className="journey-detail-section"><label>Click-by-click acceptance</label><StepList steps={[
                `Open Ask Zia and start a new conversation for ${workflow.id}.`,
                `Ask the complete atomic prompt against ${workflow.primaryObject}; do not depend on a prior question for date or outlet scope.`,
                "Inspect Report Information and verify the exact source object, date predicate, filters and aggregation contract shown above.",
                "Compare every visible number and row to the expected control and actively reject the negative control.",
                "Ask the documented follow-up, verify retained context, then log PASS, FAIL, PARTIAL or NOT_RUN in the conversational ledger.",
                "Use the workflow in a presentation only when both the primary and follow-up are PASS and the visible narrative matches the table.",
              ]} /></section>
            </SeeMore>
          </article>
        </div>
      ) : null}

      {mode === "presentation" ? (
        <div className="journey-presentation-flows">
          <div className="journey-callout is-amber"><ShieldCheck size={16} /><div><strong>Overall gate BLOCKED</strong><span>These are six governed fallback sequences, not approved Ask Zia demonstrations. WAT 22 is 7 PASS / 9 PARTIAL / 6 FAIL and the full ladder is 7 PASS / 9 PARTIAL / 50 FAIL; zero workflows are presentation-ready. Use only the named governed reports/tables until every required tier passes.</span></div></div>
          <div className="journey-flow-grid">
            {ziaPresentationFlows.map((flow, index) => (
              <article key={flow.title}>
                <header><span>{String(index + 1).padStart(2, "0")}</span><div><strong>{flow.title}</strong><code>{flow.route}</code></div></header>
                <StepList steps={flow.steps} />
                <div><label>Visible control</label><p>{flow.control}</p></div>
                <div><label>Governed fallback</label><p>{flow.fallback}</p></div>
              </article>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function WeatherExtension() {
  const [mode, setMode] = useState<"pipeline" | "reports" | "governance">("pipeline");
  const weatherObjects = [...weatherLandingTables, ...weatherQueryTables];
  const [objectName, setObjectName] = useState(weatherObjects[0].name);
  const [reportName, setReportName] = useState(weatherReports[0].name);
  const object = weatherObjects.find((item) => item.name === objectName) ?? weatherObjects[0];
  const report = weatherReports.find((item) => item.name === reportName) ?? weatherReports[0];

  return (
    <div className="journey-extension">
      <header className="journey-extension-header">
        <div><span className="section-kicker">Open-Meteo evaluation extension</span><h2>Weather sits beside the unchanged operational core</h2><p>Historical provider data explains association; the current outlook shows D+1-D+7 weather. Neither changes the deterministic shortage forecast today.</p></div>
        <div className="journey-extension-metrics" aria-label="Weather extension summary">
          <span><b>3</b><small>live inputs</small></span>
          <span><b>3</b><small>extension queries</small></span>
          <span className="is-pass"><b>4</b><small>QA reports</small></span>
          <span className="is-blocked"><b>0</b><small>production approvals</small></span>
        </div>
      </header>
      <nav className="journey-extension-switcher" aria-label="Weather architecture views">
        <button type="button" className={mode === "pipeline" ? "is-active" : ""} onClick={() => setMode("pipeline")}>API to Query Tables</button>
        <button type="button" className={mode === "reports" ? "is-active" : ""} onClick={() => setMode("reports")}>Live demo reports</button>
        <button type="button" className={mode === "governance" ? "is-active" : ""} onClick={() => setMode("governance")}>Governance & future</button>
      </nav>

      {mode === "pipeline" ? (
        <>
          <div className="journey-weather-route" aria-label="Weather ingestion and analysis route">
            <span><CloudSun size={16} /><strong>Open-Meteo</strong><small>Historical Forecast + Forecast APIs</small></span><ArrowRight size={15} />
            <span><Braces size={16} /><strong>Local normalizer</strong><small>Daily means, keys, status, attribution</small></span><ArrowRight size={15} />
            <span><FileSpreadsheet size={16} /><strong>DataBridge Update/Add</strong><small>Stable CSV into existing tables</small></span><ArrowRight size={15} />
            <span><GitBranch size={16} /><strong>QT_07 / QT_08 / QT_09</strong><small>Daily join, sensitivity, latest outlook</small></span><ArrowRight size={15} />
            <span><BarChart3 size={16} /><strong>Four demo reports</strong><small>Association and D+1-D+7 context</small></span>
          </div>
          <div className="journey-model journey-extension-browser">
            <aside className="journey-model-index">
              <div className="journey-extension-note"><ShieldCheck size={15} /><span>Recommended production route: approved endpoint → local normalizer → DataBridge Update/Add.</span></div>
              <nav aria-label="Weather tables and extension Query Tables">
                {weatherObjects.map((item, index) => (
                  <button key={item.name} type="button" className={item.name === object.name ? "is-active" : ""} onClick={() => setObjectName(item.name)}>
                    <span data-level={index < weatherLandingTables.length ? 1 : 2}>{String(index + 1).padStart(2, "0")}</span>
                    <div><strong>{item.name}</strong><small>{item.rows}</small></div><ChevronRight size={14} />
                  </button>
                ))}
              </nav>
            </aside>
            <article className="journey-model-detail">
              <header><div><span className="section-kicker">Weather data contract</span><h2>{object.name}</h2><p>{object.purpose}</p></div><Pill tone={object.status.includes("LIVE") ? "green" : "amber"}>{object.status}</Pill></header>
              <dl className="journey-model-facts"><div><dt>Contracted grain</dt><dd>{object.grain}</dd></div><div><dt>Live view ID</dt><dd><code>{object.viewId}</code></dd></div></dl>
              <section className="journey-dependency-band"><label>Inputs</label><div>{object.dependencies.map((item) => <code key={item}>{item}</code>)}</div></section>
              <section className="journey-example-band"><label>Key fields</label><div>{object.keyFields.map((item) => <code key={item}>{item}</code>)}</div></section>
              <div className="journey-callout is-amber"><ShieldCheck size={15} /><div><strong>Evidence boundary</strong><span>Approximate coordinates and provider model-grid data are evaluation evidence, not client-approved outlet observation.</span></div></div>
              <SeeMore label={`See more details: build ${object.name}`}>
                <div className="journey-detail-facts"><section><label>Exact object</label><code>{object.name}</code></section><section><label>Verified rows</label><p>{object.rows}</p></section><section><label>Live view ID</label><code>{object.viewId}</code></section><section><label>Grain</label><p>{object.grain}</p></section></div>
                <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={object.steps} /></section>
              </SeeMore>
            </article>
          </div>
        </>
      ) : null}

      {mode === "reports" ? (
        <div className="journey-output-browser journey-weather-reports">
          <aside aria-label="Live weather demo reports">
            {weatherReports.map((item) => (
              <button key={item.name} type="button" className={item.name === report.name ? "is-active" : ""} onClick={() => setReportName(item.name)}>
                <span><BarChart3 size={14} /></span><div><strong>{item.name}</strong><small>{item.base}</small></div><ChevronRight size={14} />
              </button>
            ))}
          </aside>
          <article className="journey-report-detail">
            <header><div><Pill tone="amber">DEMO / EVALUATION</Pill><h2>{report.name}</h2><p>{report.question}</p></div><code>{report.base}</code></header>
            <div className="journey-report-build"><section><label>Visual and shelves</label><ul><li>{report.visual}</li>{report.shelves.map((item) => <li key={item}>{item}</li>)}</ul></section><section><label>Fixed scope</label>{report.fixed.length ? <ul>{report.fixed.map((item) => <li key={item}>{item}</li>)}</ul> : <p>None beyond the extension table’s governed scope.</p>}</section></div>
            <section className="journey-report-mappings"><label>Exact dashboard mapping</label><div>{Object.entries(report.mappings).map(([filterName, column]) => <span key={filterName}><b>{filterName}</b><ArrowRight size={12} /><code>{column}</code></span>)}</div></section>
            <section className="journey-unmapped"><label>Intentionally unmapped</label><p>{report.intentionallyUnmapped.join(" · ")}</p></section>
            <div className="journey-callout is-amber"><CircleDot size={15} /><div><strong>Mandatory disclosure</strong><span>{report.disclosure}</span></div></div>
            <SeeMore label={`See more details: build ${report.name}`}>
              <div className="journey-detail-facts"><section><label>Exact saved report</label><code>{report.name}</code></section><section><label>Live view ID</label><code>{report.viewId}</code></section><section><label>Create as</label><p>{report.visual}</p></section><section><label>Base table</label><code>{report.base}</code></section></div>
              <section className="journey-detail-section"><label>Exact shelves</label><ul>{report.shelves.map((item) => <li key={item}>{item}</li>)}</ul></section>
              <section className="journey-detail-section"><label>Exact filter-column mapping</label><div className="journey-detail-mapping">{Object.entries(report.mappings).map(([filterName, column]) => <span key={filterName}><b>{filterName}</b><ArrowRight size={12} /><code>{column}</code></span>)}</div><p className="journey-muted-line"><strong>Leave unmapped:</strong> {report.intentionallyUnmapped.join(" · ")}</p></section>
              <section className="journey-detail-section"><label>Click-by-click</label><StepList steps={report.steps} /></section>
              <div className="journey-acceptance-grid"><section><label>Visual acceptance</label><p>{report.acceptance}</p></section><section><label>Governance acceptance</label><p>{report.disclosure}</p></section></div>
            </SeeMore>
          </article>
        </div>
      ) : null}

      {mode === "governance" ? (
        <div className="journey-weather-governance">
          <section className="journey-reading-card"><span className="section-kicker">Production gate</span><h2>Mechanics passed; authorization has not</h2><p>The live objects prove the API schema, daily join, Query Table design and report readability. They do not authorize commercial use or establish causal sales lift.</p><div className="journey-callout is-blue"><BadgeCheck size={16} /><div><strong>Validated mechanics</strong><span>270 historical proxy rows, 24 forecast rows, 4,855 live Month-1 joins and 21 D+1-D+7 outlook rows.</span></div></div></section>
          <section className="journey-governance-grid">
            {weatherGovernanceGates.map((gate) => <article key={gate.label} data-status={gate.status}><Pill tone={gate.status === "LIVE DEMO" ? "green" : "amber"}>{gate.status}</Pill><strong>{gate.label}</strong><p>{gate.detail}</p></article>)}
            <SeeMore label="See more details: promote weather from evaluation to production">
              <section className="journey-detail-section"><label>Required sequence</label><StepList steps={[
                "Replace approximate neighbourhood centroids with ABNAH-confirmed outlet coordinates and approval references.",
                "Approve an Open-Meteo commercial customer endpoint or an independently reviewed self-hosted route.",
                "Schedule the local normalizer before DataBridge Update/Add; retain attribution, status and forecast-vintage fields.",
                "Accumulate as-issued historical forecast vintages and longer actual sales history without future leakage.",
                "Validate a weather-aware AutoML model chronologically against the deterministic same-weekday baseline.",
                "Materialize accepted predictions with model/run metadata before allowing them to feed a parallel QT_01-compatible action route.",
              ]} /></section>
            </SeeMore>
          </section>
        </div>
      ) : null}
    </div>
  );
}

function PortableHandoff() {
  const layers = [
    { icon: FileCode2, label: "Source contracts", detail: "Headers, grain, types and provenance. Structural catalog status is separate from private image coverage; the candidate remains blocked." },
    { icon: FileSpreadsheet, label: "Build assets", detail: "Import schemas, controls, ordered SQL and dependency manifests." },
    { icon: BarChart3, label: "Presentation contract", detail: "Exact KPI, report, dashboard and User Filter mappings." },
    { icon: BadgeCheck, label: "Acceptance evidence", detail: "Truth controls, reconciliation outputs and honest execution ledgers." },
    { icon: ShieldCheck, label: "Operating guardrails", detail: "TEST-only validation, promotion gates and external secret injection." },
  ] as const;
  const route = ["Verify pack", "Read contracts", "Load controls + inputs", "Build in order", "Map outputs", "Run gates"];

  return (
    <div className="journey-extension journey-handoff">
      <header className="journey-extension-header">
        <div>
          <span className="section-kicker">Candidate migration handoff</span>
          <h2>Portable knowledge, guarded execution</h2>
          <p>The candidate contains the contracts and guarded build sequence needed for review, but it is not release-ready. The public website and repository project pack contain no private discovery images. The historical private audit reviewed 182 images: the isolated candidate retains 95 strict schema-only images and excludes 87 value-bearing images. Those safe images cover 64 of 94 historically evidenced report groups, leaving 30 image-pending. Of those 30 groups, 27 have separately verified text schemas covering 530 fields and 3 remain text-pending. Text-schema cards never count as screenshots or close an image gap.</p>
        </div>
        <div className="journey-extension-metrics" aria-label="Portable handoff summary">
          <span><b>5</b><small>handoff layers</small></span>
          <span><b>6</b><small>navigation gates</small></span>
          <span className="is-pass"><b>0</b><small>embedded secrets</small></span>
          <span className="is-blocked"><b>TEST</b><small>first validation scope</small></span>
        </div>
      </header>

      <section className="journey-handoff-flow" aria-label="Recommended migration-pack navigation order">
        {route.map((step, index) => (
          <div key={step}><span>{String(index + 1).padStart(2, "0")}</span><strong>{step}</strong>{index < route.length - 1 ? <ArrowRight aria-hidden="true" size={15} /> : null}</div>
        ))}
      </section>

      <section className="journey-handoff-grid">
        {layers.map(({ icon: Icon, label, detail }) => (
          <article key={label}><Icon aria-hidden="true" size={18} /><div><strong>{label}</strong><p>{detail}</p></div></article>
        ))}
      </section>

      <div className="journey-handoff-boundaries">
        <article><ShieldCheck aria-hidden="true" size={18} /><div><label>Secret boundary</label><strong>Inject at runtime; never package</strong><p>OAuth client secrets, refresh/access tokens, passwords, cookies, environment values and real operational rows remain in approved external stores.</p></div></article>
        <article><BadgeCheck aria-hidden="true" size={18} /><div><label>Execution boundary</label><strong>Prove in TEST before promotion</strong><p>Start read-only. Any validation write must target an explicit TEST workspace or allowlisted TEST object, then pass row, grain, metric and presentation controls.</p></div></article>
        <article><FileSpreadsheet aria-hidden="true" size={18} /><div><label>Screenshot boundary</label><strong>Public excluded; private candidate blocked</strong><p>No private discovery images ship in the public website or repository project pack. The isolated candidate retains 95 strict schema-only images, excludes 87 value-bearing images, covers 64 of 94 historically evidenced report groups and leaves 30 groups image-pending. Verified text cards provide structural evidence for 27 pending groups but add zero screenshot coverage.</p></div></article>
      </div>

      <SeeMore label="See more details: recipient navigation and guarded validation">
        <div className="journey-detail-facts">
          <section><label>Recipient gets</label><p>The candidate provides schema contracts, build manifests, SQL, formula/report/filter instructions, synthetic examples, acceptance controls and reusable validators. Its private image subset is limited to 95 audited strict schema-only images; image coverage is 64 of 94 historical report groups, with 30 disclosed gaps. Verified text-schema cards cover 27 of those gaps structurally with 530 fields, while 3 remain text-pending. The candidate is not yet a releasable handoff.</p></section>
          <section><label>Recipient does not get</label><p>Credentials, tokens, browser state, real source rows, unreviewed or excluded historical images, local database files or hard-coded machine paths. Public/project-pack artifacts never contain private discovery images, and excluded images must not be reintroduced through a generated index, archive, mirror or website asset.</p></section>
          <section><label>Portable entry point</label><p>Begin at the pack’s Start Here guide and integrity manifest; follow only the numbered dependency-safe sequence.</p></section>
          <section><label>Promotion rule</label><p>A TEST success is evidence for review, not permission to mutate production. Production needs named owner approval and a fresh reconciliation.</p></section>
        </div>
        <section className="journey-detail-section"><label>Recommended navigation order</label><StepList steps={[
          "Run the portable integrity validator and stop if any required asset, hash or manifest entry differs.",
          "Read the source and grain contracts before viewing SQL so each business date, snapshot and unit boundary is understood.",
          "Load control/reference inputs, then operational inputs, using the import checklist and exact table names.",
          "Build Query Tables in manifest order and execute each table's row-count, key-uniqueness and null-control checks before continuing.",
          "Create the named KPIs and reports, then map every dashboard User Filter to the exact compatible column documented in this journey.",
          "Run numerical reconciliation, visual acceptance, Ask Zia conversational logging and extension-specific governance gates; record NOT_RUN or PARTIAL honestly.",
        ]} /></section>
        <section className="journey-detail-section"><label>Guarded TEST-only validation</label><StepList steps={[
          "Default every automation to inspection or dry-run mode and require an explicit TEST target identifier before allowing a write.",
          "Allowlist object names and permitted operations; reject a production workspace, an unknown object or a request carrying inline credentials.",
          "Write only synthetic or approved test rows, attach a run ID, and retain before/after counts so cleanup and audit are deterministic.",
          "Compare the TEST output to the packaged truth controls and negative controls; a technically successful call is not a semantic PASS.",
          "Promote only the reviewed assets, never the stored session or secret material, and repeat the acceptance checks in the destination.",
        ]} /></section>
        <div className="journey-callout is-amber"><ShieldCheck size={15} /><div><strong>Credential rule</strong><span>The pack documents required secret names and setup boundaries only. It never contains secret values, authorization codes or copied browser sessions.</span></div></div>
      </SeeMore>
    </div>
  );
}

const stageContent: Record<JourneyStageId, () => React.ReactNode> = {
  inputs: SourceInputs,
  controls: GovernedControls,
  model: LeanModel,
  calculations: Calculations,
  forecasting: Forecasting,
  outputs: DecisionOutputs,
  filters: FilterContract,
  zia: ZiaSemanticLayer,
  weather: WeatherExtension,
  handoff: PortableHandoff,
};

export function ArchitectureGraphWorkspace({ onOpenDiscovery }: { onOpenDiscovery?: () => void }) {
  const [stage, setStage] = useState<JourneyStageId>("inputs");
  const ActiveStage = stageContent[stage];
  return (
    <section className="journey-surface">
      <header className="journey-hero">
        <div>
          <span className="section-kicker">Zoho Analytics implementation journey</span>
          <h1>From source reports to daily decisions</h1>
          <p>A visual handover of the governed lean foundation: what enters the workspace, how its {architectureScopeTruth.governedLeanFoundationQueryTables} Query Tables transform it, how each dashboard object stays filter-safe, and where governed Zia and weather extensions sit. The broader historical live v2 registry contains {architectureScopeTruth.broaderHistoricalLiveModelTables} tables and remains a separate compatibility/lineage scope.</p>
        </div>
        <div className="journey-hero-metrics" aria-label="Current architecture counts">
          <span><b>26</b><small>core inputs</small></span>
          <span><b>10</b><small>Query Tables</small></span>
          <span><b>10</b><small>extension queries</small></span>
          <span><b>31</b><small>governed outputs</small></span>
        </div>
        <div className="journey-hero-badge"><PackageCheck size={16} /><span><strong>10-query governed lean foundation · 38-table historical live v2 model</strong><small>Separate scopes · physical dates · exact mappings</small></span></div>
      </header>
      <nav className="journey-stage-rail" aria-label="Architecture journey">
        {journeyStages.map((item, index) => {
          const Icon = stageIcons[item.id];
          return (
            <button key={item.id} type="button" className={stage === item.id ? "is-active" : ""} onClick={() => setStage(item.id)} aria-current={stage === item.id ? "step" : undefined}>
              <span className="journey-stage-icon"><Icon aria-hidden="true" size={17} /></span>
              <div><small>{item.number}</small><strong>{item.label}</strong><p>{item.summary}</p><b>{item.count}</b></div>
              {index < journeyStages.length - 1 ? <ArrowRight className="journey-stage-arrow" aria-hidden="true" size={15} /> : null}
            </button>
          );
        })}
      </nav>
      <div className="journey-stage-body" key={stage}>{stage === "inputs" ? <SourceInputs onOpenDiscovery={onOpenDiscovery} /> : <ActiveStage />}</div>
      <footer className="journey-footer">
        <BookOpen aria-hidden="true" size={16} />
        <span><strong>Handover rule:</strong> start with the journey, then open only the selected table, metric or report for exact build detail.</span>
        <Target aria-hidden="true" size={15} />
        <small>No multi-date state totals. No cross-UOM quantity totals. Provisional expiry and weather remain disclosed. Zia needs a logged conversational PASS.</small>
      </footer>
    </section>
  );
}
