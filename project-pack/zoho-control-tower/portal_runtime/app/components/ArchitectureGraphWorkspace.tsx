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
  FileCode2,
  FileSpreadsheet,
  Filter,
  Gauge,
  GitBranch,
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

function SourceInputs() {
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

const stageContent: Record<JourneyStageId, () => React.ReactNode> = {
  inputs: SourceInputs,
  controls: GovernedControls,
  model: LeanModel,
  calculations: Calculations,
  forecasting: Forecasting,
  outputs: DecisionOutputs,
  filters: FilterContract,
};

export function ArchitectureGraphWorkspace() {
  const [stage, setStage] = useState<JourneyStageId>("inputs");
  const ActiveStage = stageContent[stage];
  return (
    <section className="journey-surface">
      <header className="journey-hero">
        <div>
          <span className="section-kicker">Zoho Analytics implementation journey</span>
          <h1>From source reports to daily decisions</h1>
          <p>A visual handover of the current lean architecture: what enters the workspace, how the 10 Query Tables transform it, and how each final dashboard object stays filter-safe.</p>
        </div>
        <div className="journey-hero-metrics" aria-label="Current architecture counts">
          <span><b>26</b><small>landing tables</small></span>
          <span><b>10</b><small>Query Tables</small></span>
          <span><b>14</b><small>active metrics</small></span>
          <span><b>27</b><small>final objects</small></span>
        </div>
        <div className="journey-hero-badge"><PackageCheck size={16} /><span><strong>Lean foundation</strong><small>Physical dates · governed controls · exact mappings</small></span></div>
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
      <div className="journey-stage-body" key={stage}><ActiveStage /></div>
      <footer className="journey-footer">
        <BookOpen aria-hidden="true" size={16} />
        <span><strong>Handover rule:</strong> start with the journey, then open only the selected table, metric or report for exact build detail.</span>
        <Target aria-hidden="true" size={15} />
        <small>No multi-date state totals. No cross-UOM quantity totals. Provisional expiry remains disclosed.</small>
      </footer>
    </section>
  );
}
