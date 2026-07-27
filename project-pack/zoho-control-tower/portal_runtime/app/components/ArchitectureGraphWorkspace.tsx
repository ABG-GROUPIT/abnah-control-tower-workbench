"use client";

import {
  ArrowRight,
  BadgeCheck,
  BarChart3,
  BookOpen,
  Braces,
  Database,
  ExternalLink,
  FileCode2,
  Filter,
  GitMerge,
  Layers3,
  Monitor,
  Search,
  ShieldCheck,
  Table2,
  Target,
} from "lucide-react";
import { useMemo, useState } from "react";
import type {
  ControlTowerModel,
  ControlTowerPresentation,
  PresentationSourceReport,
  PresentationStory,
  PresentationStoryKind,
} from "../lib/control-tower-presentation-types";
import type { ReportWorkspaceDocument } from "../lib/workspace-types";

interface ArchitectureGraphWorkspaceProps {
  presentation: ControlTowerPresentation;
  model: ControlTowerModel;
  reports: ReportWorkspaceDocument[];
  onOpenReport: (reportId: string) => void;
}

type WorkspaceMode = "story" | "model";
type KindFilter = "all" | PresentationStoryKind;

const kindLabel: Record<PresentationStoryKind, string> = {
  kpi: "KPI",
  chart: "Chart",
  table: "Detail",
};

const kindIcon = {
  kpi: Target,
  chart: BarChart3,
  table: Table2,
};

function compactName(value: string) {
  return value.replace(/\.sql$/i, "");
}

function normalizedFieldLabel(value: string) {
  return value.toLowerCase().replace(/&/g, "and").replace(/[^a-z0-9]+/g, "");
}

function sourceFieldDisplay(
  source: PresentationSourceReport,
  report: ReportWorkspaceDocument | undefined,
) {
  const usedKeys = new Set(source.fields.map(normalizedFieldLabel));
  const fields = report?.fields.length
    ? report.fields.map((field) => field.label)
    : source.fields;
  const uniqueFields = fields.filter((field, index, all) => (
    all.findIndex((candidate) => normalizedFieldLabel(candidate) === normalizedFieldLabel(field)) === index
  ));
  const capturedKeys = new Set(uniqueFields.map(normalizedFieldLabel));

  for (const mappedField of source.fields) {
    if (!capturedKeys.has(normalizedFieldLabel(mappedField))) uniqueFields.push(mappedField);
  }

  return uniqueFields.map((field) => ({
    field,
    used: usedKeys.has(normalizedFieldLabel(field)),
    mappedAlias: Boolean(report) && !capturedKeys.has(normalizedFieldLabel(field)),
  }));
}

function matchesStory(story: PresentationStory, query: string) {
  const search = query.trim().toLowerCase();
  if (!search) return true;
  return [
    story.id,
    story.name,
    story.question,
    story.visual,
    story.sourceTable,
    story.formula,
    ...story.finalFields,
  ].some((value) => value.toLowerCase().includes(search));
}

function EvidenceStage({
  story,
  presentation,
  reports,
  onOpenReport,
}: {
  story: PresentationStory;
  presentation: ControlTowerPresentation;
  reports: ReportWorkspaceDocument[];
  onOpenReport: (reportId: string) => void;
}) {
  const profile = presentation.sourceProfiles[story.sourceTable];
  const reportById = new Map(reports.map((report) => [report.id, report]));
  return (
    <article className="lineage-story-stage" data-stage="evidence">
      <header>
        <span><Database aria-hidden="true" size={16} /></span>
        <div><b>01</b><strong>Original evidence</strong><small>POSIST reports and governed inputs</small></div>
      </header>
      <div className="lineage-story-stage-body lineage-source-list">
        <div className="lineage-field-legend" aria-label="Source field legend">
          <span><i className="is-used" />Used in selected lineage</span>
          <span><i />Other captured data point</span>
        </div>
        {profile.reports.map((source) => {
          const report = source.reportId ? reportById.get(source.reportId) : undefined;
          const displayedFields = sourceFieldDisplay(source, report);
          const usedCount = displayedFields.filter((field) => field.used).length;
          return (
            <section key={`${source.name}:${source.evidence}`} className="lineage-source-entry">
              <div>
                <span className={`lineage-evidence-mark ${source.evidence === "synthetic_model_input" ? "is-synthetic" : ""}`}>
                  {source.evidence === "synthetic_model_input" ? "AUX" : "POS"}
                </span>
                <p>
                  <strong>{source.name}</strong>
                  <small>{source.role}</small>
                  <small className="lineage-source-field-count">
                    <b>{usedCount}</b> used / <b>{displayedFields.length}</b> {report ? "captured fields" : "mapped input fields"}
                  </small>
                </p>
                {source.reportId ? (
                  <button
                    type="button"
                    title={`Open ${source.name} in schema discovery`}
                    onClick={() => onOpenReport(source.reportId)}
                  >
                    <ExternalLink aria-hidden="true" size={14} />
                  </button>
                ) : null}
              </div>
              <ul>
                {displayedFields.map(({ field, used, mappedAlias }, index) => (
                  <li
                    key={`${source.name}:${field}:${index}`}
                    className={used ? "is-used" : ""}
                    title={mappedAlias ? "Mapped lineage label; verify against the captured source label" : undefined}
                  >
                    {used ? <BadgeCheck aria-hidden="true" size={9} /> : null}
                    <span>{field}</span>
                  </li>
                ))}
              </ul>
            </section>
          );
        })}
      </div>
    </article>
  );
}

function RelationshipStage({
  story,
  presentation,
}: {
  story: PresentationStory;
  presentation: ControlTowerPresentation;
}) {
  const profile = presentation.sourceProfiles[story.sourceTable];
  return (
    <article className="lineage-story-stage" data-stage="relationship">
      <header>
        <span><GitMerge aria-hidden="true" size={16} /></span>
        <div><b>02</b><strong>Relationship</strong><small>Route, grain, lookups, and join</small></div>
      </header>
      <div className="lineage-story-stage-body">
        <section className="lineage-stage-section">
          <label>Model route</label>
          <ol className="lineage-route-list">
            {profile.route.map((step, index) => (
              <li key={`${step}:${index}`}>
                <span>{index + 1}</span><code>{step}</code>
                {index < profile.route.length - 1 ? <ArrowRight aria-hidden="true" size={12} /> : null}
              </li>
            ))}
          </ol>
        </section>
        <section className="lineage-stage-section">
          <label>Final grain</label>
          <p>{profile.grain}</p>
        </section>
        <section className="lineage-stage-section">
          <label>Join logic</label>
          <p>{profile.joinLogic}</p>
        </section>
        <section className="lineage-stage-section">
          <label>Zoho lookups</label>
          {profile.lookups.length ? (
            <ul className="lineage-rule-list">
              {profile.lookups.map((lookup) => <li key={lookup}><code>{lookup}</code></li>)}
            </ul>
          ) : <p>No lookup is created at this grain.</p>}
        </section>
      </div>
    </article>
  );
}

function CalculationStage({ story }: { story: PresentationStory }) {
  return (
    <article className="lineage-story-stage" data-stage="calculation">
      <header>
        <span><Braces aria-hidden="true" size={16} /></span>
        <div><b>03</b><strong>Calculation</strong><small>Fields, formula, and aggregation</small></div>
      </header>
      <div className="lineage-story-stage-body">
        <section className="lineage-stage-section">
          <label>Final fields</label>
          <ul className="lineage-field-list">
            {story.finalFields.map((field) => <li key={field}>{field}</li>)}
          </ul>
        </section>
        <section className="lineage-stage-section">
          <label>Formula</label>
          <pre className="lineage-formula"><code>{story.formula}</code></pre>
        </section>
        <section className="lineage-stage-section">
          <label>Aggregation</label>
          <p>{story.aggregation}</p>
        </section>
        <section className="lineage-stage-section">
          <label>Physical Query Table</label>
          <code className="lineage-table-reference">{story.sourceTable}</code>
        </section>
      </div>
    </article>
  );
}

function ZohoStage({ story }: { story: PresentationStory }) {
  return (
    <article className="lineage-story-stage" data-stage="output">
      <header>
        <span><BarChart3 aria-hidden="true" size={16} /></span>
        <div><b>04</b><strong>Zoho output</strong><small>Exact report-designer configuration</small></div>
      </header>
      <div className="lineage-story-stage-body">
        <section className="lineage-output-visual">
          <span>{kindLabel[story.kind]}</span>
          <strong>{story.visual}</strong>
          <small>{story.id}</small>
        </section>
        <section className="lineage-stage-section">
          <label>Shelves / columns</label>
          <ul className="lineage-rule-list">
            {story.zoho.shelves.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </section>
        <section className="lineage-stage-section">
          <label>Fixed report filters</label>
          {story.zoho.fixedFilters.length ? (
            <ul className="lineage-rule-list">
              {story.zoho.fixedFilters.map((item) => <li key={item}>{item}</li>)}
            </ul>
          ) : <p>None. Global/page filters remain available.</p>}
        </section>
        <details className="lineage-output-details">
          <summary>Sort, tooltips, formatting, and user filters</summary>
          <div>
            <label>Sort</label><p>{story.zoho.sort}</p>
            {story.zoho.tooltips.length ? <><label>Tooltips</label><p>{story.zoho.tooltips.join(" | ")}</p></> : null}
            {story.zoho.formatting.length ? <><label>Formatting</label><p>{story.zoho.formatting.join(" | ")}</p></> : null}
            <label>User filters</label><p>{story.zoho.userFilters.join(" | ")}</p>
          </div>
        </details>
      </div>
    </article>
  );
}

function DeliveryStage({ story }: { story: PresentationStory }) {
  const available = ["p1", "p2"].includes(story.pageId);
  return (
    <article className="lineage-story-stage" data-stage="delivery">
      <header>
        <span><Monitor aria-hidden="true" size={16} /></span>
        <div><b>05</b><strong>Custom delivery</strong><small>Secured operational presentation layer</small></div>
      </header>
      <div className="lineage-story-stage-body">
        <section className="lineage-stage-section">
          <label>Runtime route</label>
          <ol className="lineage-route-list">
            <li><span>1</span><code>{story.sourceTable}</code><ArrowRight aria-hidden="true" size={12} /></li>
            <li><span>2</span><code>Zoho Analytics API</code><ArrowRight aria-hidden="true" size={12} /></li>
            <li><span>3</span><code>Supabase OAuth gateway</code><ArrowRight aria-hidden="true" size={12} /></li>
            <li><span>4</span><code>GitHub Pages portal</code></li>
          </ol>
        </section>
        <section className="lineage-stage-section">
          <label>Filter execution</label>
          <p>
            Date, outlet, category, and page-specific choices are applied to
            API rows in the custom portal. Exact Zoho criteria are carried
            into governed drill-through links.
          </p>
        </section>
        <section className="lineage-stage-section">
          <label>Delivery status</label>
          <p>
            {available
              ? "Live on the secured P1/P2 portal."
              : "Modelled and ready for a later portal release."}
          </p>
        </section>
        {available ? (
          <a
            className="lineage-delivery-link"
            href="./portal/"
            target="_blank"
            rel="noreferrer"
          >
            Open live portal
            <ExternalLink aria-hidden="true" size={13} />
          </a>
        ) : null}
      </div>
    </article>
  );
}

function StoryWorkspace({
  presentation,
  reports,
  onOpenReport,
}: {
  presentation: ControlTowerPresentation;
  reports: ReportWorkspaceDocument[];
  onOpenReport: (reportId: string) => void;
}) {
  const [pageId, setPageId] = useState(presentation.pages[0]?.id ?? "all");
  const [kind, setKind] = useState<KindFilter>("all");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(presentation.stories[0]?.id ?? "");

  const filtered = useMemo(
    () => presentation.stories.filter((item) => (
      (pageId === "all" || item.pageId === pageId)
      && (kind === "all" || item.kind === kind)
      && matchesStory(item, query)
    )),
    [kind, pageId, presentation.stories, query],
  );

  const selected = filtered.find((item) => item.id === selectedId) ?? filtered[0];
  const page = presentation.pages.find((item) => item.id === selected?.pageId);
  const profile = selected ? presentation.sourceProfiles[selected.sourceTable] : undefined;

  return (
    <div className="lineage-story-layout">
      <aside className="lineage-story-nav">
        <div className="lineage-search">
          <Search aria-hidden="true" size={14} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search KPI, chart, field, formula"
            aria-label="Search KPI and chart stories"
          />
        </div>
        <div className="lineage-page-tabs" aria-label="Filter by Control Tower page">
          {presentation.pages.map((item) => (
            <button
              key={item.id}
              type="button"
              className={pageId === item.id ? "is-active" : ""}
              onClick={() => setPageId(item.id)}
              title={item.purpose}
            >
              <b>{item.number}</b>
              <span>{item.name}</span>
              <small>{presentation.stories.filter((story) => story.pageId === item.id).length}</small>
            </button>
          ))}
        </div>
        <div className="lineage-kind-tabs" aria-label="Filter by object type">
          {(["all", "kpi", "chart", "table"] as KindFilter[]).map((value) => (
            <button
              key={value}
              type="button"
              className={kind === value ? "is-active" : ""}
              onClick={() => setKind(value)}
            >
              {value === "all" ? "All" : kindLabel[value]}
            </button>
          ))}
        </div>
        <div className="lineage-story-count">
          <span>{filtered.length} objects</span><small>one story at a time</small>
        </div>
        <nav className="lineage-story-list" aria-label="KPI and chart stories">
          {filtered.map((item) => {
            const Icon = kindIcon[item.kind];
            return (
              <button
                key={item.id}
                type="button"
                className={selected?.id === item.id ? "is-active" : ""}
                onClick={() => setSelectedId(item.id)}
              >
                <Icon aria-hidden="true" size={14} />
                <span><strong>{item.name}</strong><small>{item.visual} / {compactName(item.sourceTable)}</small></span>
                <ArrowRight aria-hidden="true" size={13} />
              </button>
            );
          })}
        </nav>
      </aside>

      {selected && profile ? (
        <section className="lineage-story-workspace">
          <header className="lineage-story-heading">
            <div>
              <span className="section-kicker">Page {page?.number} / {page?.name} / {kindLabel[selected.kind]}</span>
              <h2>{selected.name}</h2>
              <p>{selected.question}</p>
            </div>
            <dl>
              <div><dt>Evidence</dt><dd>{profile.reports.filter((item) => item.evidence === "captured_posist_report").length} POSIST reports</dd></div>
              <div><dt>Model</dt><dd>{compactName(selected.sourceTable)}</dd></div>
              <div><dt>Grain</dt><dd>{profile.grain}</dd></div>
            </dl>
          </header>

          <div className="lineage-story-flow">
            <EvidenceStage story={selected} presentation={presentation} reports={reports} onOpenReport={onOpenReport} />
            <RelationshipStage story={selected} presentation={presentation} />
            <CalculationStage story={selected} />
            <ZohoStage story={selected} />
            <DeliveryStage story={selected} />
          </div>

          <footer className="lineage-story-footer">
            <section>
              <BookOpen aria-hidden="true" size={16} />
              <div><strong>How to explain it</strong><p>{selected.talkTrack}</p></div>
            </section>
            <section>
              <ShieldCheck aria-hidden="true" size={16} />
              <div>
                <strong>Publication guardrails</strong>
                <ul>
                  {[...profile.guardrails, ...selected.caveats].filter((value, index, all) => all.indexOf(value) === index).map((item) => <li key={item}>{item}</li>)}
                </ul>
              </div>
            </section>
          </footer>
        </section>
      ) : (
        <section className="lineage-story-empty"><Search aria-hidden="true" size={22} /><strong>No matching story</strong><span>Clear the search or change the page/type filter.</span></section>
      )}
    </div>
  );
}

function ModelWorkspace({ model }: { model: ControlTowerModel }) {
  const [query, setQuery] = useState("");
  const [layer, setLayer] = useState("all");
  const [selectedName, setSelectedName] = useState(model.tables[0]?.physicalName ?? "");

  const filtered = useMemo(() => {
    const search = query.trim().toLowerCase();
    return model.tables.filter((item) => (
      (layer === "all" || item.layer === layer)
      && (!search || [
        item.physicalName,
        item.logicalName,
        item.purpose,
        ...item.sources,
      ].some((value) => value.toLowerCase().includes(search)))
    ));
  }, [layer, model.tables, query]);

  const selected = filtered.find((item) => item.physicalName === selectedName) ?? filtered[0];
  return (
    <div className="lineage-model-layout">
      <aside className="lineage-model-nav">
        <div className="lineage-search">
          <Search aria-hidden="true" size={14} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search table, purpose, dependency"
            aria-label="Search Query Tables"
          />
        </div>
        <div className="lineage-layer-tabs">
          <button type="button" className={layer === "all" ? "is-active" : ""} onClick={() => setLayer("all")}>All <small>{model.tables.length}</small></button>
          {model.layers.filter((item) => item.id !== "raw").map((item) => (
            <button
              key={item.id}
              type="button"
              className={layer === item.id ? "is-active" : ""}
              onClick={() => setLayer(item.id)}
            >
              {item.shortLabel}<small>{model.tables.filter((table) => table.layer === item.id).length}</small>
            </button>
          ))}
        </div>
        <nav className="lineage-model-list" aria-label="Query Table library">
          {filtered.map((item) => (
            <button
              key={item.physicalName}
              type="button"
              className={selected?.physicalName === item.physicalName ? "is-active" : ""}
              onClick={() => setSelectedName(item.physicalName)}
            >
              <span>{String(item.buildOrder).padStart(2, "0")}</span>
              <p><strong>{compactName(item.physicalName)}</strong><small>{item.logicalName}</small></p>
              <i data-layer={item.layer}>{item.layer.slice(0, 3)}</i>
            </button>
          ))}
        </nav>
      </aside>

      <section className="lineage-model-workspace">
        <div className="lineage-layer-strip">
          {model.layers.map((item) => (
            <article key={item.id} data-layer={item.id}>
              <span>{item.order + 1}</span>
              <div><strong>{item.label}</strong><p>{item.purpose}</p><small>{item.example}</small></div>
            </article>
          ))}
        </div>
        {selected ? (
          <div className="lineage-model-detail">
            <header>
              <div>
                <span className="section-kicker">{selected.layer} / build {String(selected.buildOrder).padStart(2, "0")} / dependency level {selected.dependencyLevel}</span>
                <h2>{compactName(selected.physicalName)}</h2>
                <p>{selected.purpose}</p>
              </div>
              <span className="lineage-model-logical">{selected.logicalName}</span>
            </header>
            <div className="lineage-model-dependencies">
              <section>
                <label>Inputs</label>
                <div>{selected.sources.map((item) => <code key={item}>{item}</code>)}</div>
              </section>
              <section>
                <label>Downstream tables</label>
                <div>
                  {model.tables.filter((item) => item.dependencies.includes(selected.physicalName)).map((item) => (
                    <button key={item.physicalName} type="button" onClick={() => setSelectedName(item.physicalName)}>{item.physicalName}</button>
                  ))}
                  {!model.tables.some((item) => item.dependencies.includes(selected.physicalName)) ? <span>Final reporting surface</span> : null}
                </div>
              </section>
            </div>
            <div className="lineage-sql-panel">
              <header><span><FileCode2 aria-hidden="true" size={15} /> Exact Zoho Query Table SQL</span><small>{selected.sql.split(/\r?\n/).length} lines</small></header>
              <pre><code>{selected.sql}</code></pre>
            </div>
          </div>
        ) : null}
      </section>
    </div>
  );
}

export function ArchitectureGraphWorkspace({
  presentation,
  model,
  reports,
  onOpenReport,
}: ArchitectureGraphWorkspaceProps) {
  const [mode, setMode] = useState<WorkspaceMode>("story");
  return (
    <section className="lineage-v2-surface">
      <header className="lineage-v2-header">
        <div>
          <span className="section-kicker">Source-to-decision architecture</span>
          <h1>Control Tower lineage</h1>
          <p>Trace one final object without graph clutter, or inspect the complete layered model and exact SQL.</p>
        </div>
        <div className="lineage-v2-metrics" aria-label="Architecture counts">
          <span><b>{presentation.counts.stories}</b><small>KPI / chart stories</small></span>
          <span><b>{model.tables.length}</b><small>Query Tables</small></span>
          <span><b>{model.layers.length}</b><small>model layers</small></span>
        </div>
        <div className="lineage-v2-mode" role="tablist" aria-label="Architecture workspace mode">
          <button type="button" className={mode === "story" ? "is-active" : ""} onClick={() => setMode("story")}>
            <Target aria-hidden="true" size={15} /><span>Object story</span>
          </button>
          <button type="button" className={mode === "model" ? "is-active" : ""} onClick={() => setMode("model")}>
            <Layers3 aria-hidden="true" size={15} /><span>Model & SQL</span>
          </button>
        </div>
      </header>
      <div className="lineage-v2-assurance">
        <BadgeCheck aria-hidden="true" size={14} />
        <span>One governed contract drives this view and the searchable handbooks.</span>
        <Filter aria-hidden="true" size={13} />
        <small>No screenshots or full operational rows are hosted.</small>
      </div>
      {mode === "story" ? (
        <StoryWorkspace presentation={presentation} reports={reports} onOpenReport={onOpenReport} />
      ) : (
        <ModelWorkspace model={model} />
      )}
    </section>
  );
}
