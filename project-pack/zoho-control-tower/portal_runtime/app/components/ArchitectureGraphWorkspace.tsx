"use client";

import {
  ArrowRight,
  BadgeCheck,
  BarChart3,
  BookOpen,
  Braces,
  CalendarDays,
  Check,
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
              <article key={name}><span>{String(index + 1).padStart(2, "0")}</span><div><strong>{name}</strong><small>{base}</small></div><code>{formula}</code><p>{meaning}</p></article>
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
            <span><b>FC04</b><small>Net sales value</small></span>
            <span><b>FC05</b><small>Theoretical margin value</small></span>
            <span><b>FC06</b><small>Expected menu units</small></span>
            <i>7 daily forecast periods</i>
          </div>
        ) : null}
      </article>
    </div>
  );
}

function ObjectDetail({ object }: { object: DashboardObject }) {
  const unmapped = unmappedFilters(object);
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
