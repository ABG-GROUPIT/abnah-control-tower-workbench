"use client";

import portalSnapshot from "@/config/zoho-portal.json";
import {
  ArrowLeft,
  Check,
  Download,
  ExternalLink,
  Info,
  LayoutTemplate,
  LogIn,
  Monitor,
  RefreshCcw,
  Save,
  Settings2,
  ShieldCheck,
  Upload,
  X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type {
  ZohoPortalCapability,
  ZohoPortalConfig,
  ZohoPortalFilter,
  ZohoPortalHandoff,
  ZohoPortalPage,
  ZohoPortalPreview,
  ZohoPortalUrlOverrides,
} from "../lib/zoho-portal-types";

const portal = portalSnapshot as unknown as ZohoPortalConfig;
const urlStorageKey = "abnah-zoho-portal-urls-v1";
const handoffSchema = "abnah-zoho-secured-embed-handoff/v1";

type PortalMode = "blueprint" | "live";
type FilterValues = Record<string, string>;
type PageFilterValues = Record<string, FilterValues>;

const capabilityLabels: Record<ZohoPortalCapability, string> = {
  native: "Zoho native",
  native_better: "Zoho enhanced",
  custom_required: "Custom finish",
};

function initialFilters(): PageFilterValues {
  return Object.fromEntries(
    portal.pages.map((page) => [
      page.id,
      Object.fromEntries(
        page.filters.map((filter) => [filter.id, filter.defaultValue]),
      ),
    ]),
  );
}

function escapeIdentifier(value: string) {
  return value.replaceAll('"', '""');
}

function escapeLiteral(value: string) {
  return value.replaceAll("'", "''");
}

function buildCriteriaUrl(
  baseUrl: string,
  page: ZohoPortalPage,
  values: FilterValues,
) {
  if (!baseUrl || page.filterStrategy !== "url_criteria") return baseUrl;
  const clauses = Object.entries(values).flatMap(([filterId, value]) => {
    const column = page.criteriaColumns[filterId];
    if (!column || !value || value === "ALL") return [];
    return [
      `("${escapeIdentifier(page.criteriaTable)}"."${escapeIdentifier(column)}" = '${escapeLiteral(value)}')`,
    ];
  });
  if (!clauses.length) return baseUrl;
  try {
    const url = new URL(baseUrl);
    url.searchParams.set("ZOHO_CRITERIA", clauses.join(" AND "));
    return url.toString();
  } catch {
    return baseUrl;
  }
}

function isSecuredZohoUrl(value: string) {
  if (!value) return true;
  try {
    const url = new URL(value);
    const host = url.hostname.toLowerCase();
    const approvedHost =
      /^analytics\.zoho\.(com|in|eu|jp|ca|sa)$/.test(host) ||
      host === "analytics.zoho.com.au";
    return url.protocol === "https:" && approvedHost;
  } catch {
    return false;
  }
}

function sanitizeUrlOverrides(value: unknown): ZohoPortalUrlOverrides {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};
  const candidate = value as Record<string, unknown>;
  return Object.fromEntries(
    portal.pages.flatMap((page) => {
      const rawUrl = candidate[page.id];
      if (typeof rawUrl !== "string") return [];
      const cleanUrl = rawUrl.trim();
      return cleanUrl && isSecuredZohoUrl(cleanUrl)
        ? [[page.id, cleanUrl]]
        : [];
    }),
  );
}

function buildHandoff(urls: ZohoPortalUrlOverrides): ZohoPortalHandoff {
  return {
    schema: handoffSchema,
    generatedAt: new Date().toISOString(),
    authMode: "zoho_secured_login",
    note:
      "Secured Zoho iframe src URLs only. This file must not contain passwords, OAuth tokens, client secrets, or operational rows.",
    dashboards: Object.fromEntries(
      portal.pages.map((page) => [
        page.id,
        {
          dashboardViewName: page.dashboardViewName,
          securedEmbedUrl: urls[page.id]?.trim() ?? "",
        },
      ]),
    ),
  };
}

function parseHandoff(value: unknown): ZohoPortalUrlOverrides {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("The selected file is not a Zoho portal handoff.");
  }
  const candidate = value as Partial<ZohoPortalHandoff>;
  if (
    candidate.schema !== handoffSchema ||
    candidate.authMode !== "zoho_secured_login" ||
    !candidate.dashboards ||
    typeof candidate.dashboards !== "object"
  ) {
    throw new Error("Use an ABNAH secured-embed handoff v1 JSON file.");
  }
  const urls = Object.fromEntries(
    portal.pages.map((page) => {
      const dashboard = candidate.dashboards?.[page.id];
      const url =
        dashboard && typeof dashboard.securedEmbedUrl === "string"
          ? dashboard.securedEmbedUrl.trim()
          : "";
      if (url && !isSecuredZohoUrl(url)) {
        throw new Error(`${page.label}: the embed URL is not an approved HTTPS Zoho Analytics URL.`);
      }
      return [page.id, url];
    }),
  );
  return sanitizeUrlOverrides(urls);
}

function FilterControl({
  filter,
  value,
  onChange,
}: {
  filter: ZohoPortalFilter;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="portal-filter-control">
      <span>{filter.label}</span>
      {filter.kind === "select" ? (
        <select value={value} onChange={(event) => onChange(event.target.value)}>
          {(filter.options ?? []).map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          value={value}
          placeholder={filter.placeholder}
          onChange={(event) => onChange(event.target.value)}
        />
      )}
    </label>
  );
}

function PlaceholderTable() {
  return (
    <div className="portal-preview-table" aria-hidden="true">
      <div className="portal-preview-table-head">
        <span />
        <span />
        <span />
        <span />
      </div>
      {[78, 58, 88, 67, 74].map((width, index) => (
        <div className="portal-preview-table-row" key={width}>
          <i style={{ width: `${width}%` }} />
          <i style={{ width: `${46 + index * 6}%` }} />
          <i style={{ width: `${82 - index * 7}%` }} />
          <b className={`state-${index % 3}`} />
        </div>
      ))}
    </div>
  );
}

function PanelPreview({ type }: { type: ZohoPortalPreview }) {
  if (type === "map") {
    return (
      <div className="portal-preview-map" aria-hidden="true">
        <span className="portal-map-region">Delhi NCR</span>
        <i style={{ left: "39%", top: "35%" }} />
        <i style={{ left: "54%", top: "48%" }} />
        <i style={{ left: "45%", top: "63%" }} />
        <b className="portal-map-ring" />
      </div>
    );
  }
  if (type === "queue") {
    return (
      <div className="portal-preview-queue" aria-hidden="true">
        {[
          ["Raise purchase order", "Due today", "purple"],
          ["Expedite existing PO", "Due today", "red"],
          ["Validate outlet cover", "Due in 3 days", "amber"],
        ].map(([label, due, state]) => (
          <div key={label}>
            <i className={`state-${state}`} />
            <span><strong>{label}</strong><small>{due}</small></span>
            <b>Procurement</b>
          </div>
        ))}
      </div>
    );
  }
  if (type === "funnel") {
    return (
      <div className="portal-preview-funnel" aria-hidden="true">
        {[
          ["Ordered", 100],
          ["Processed", 85],
          ["Pending", 47],
          ["Delayed", 31],
        ].map(([label, width]) => (
          <div key={label}>
            <span>{label}</span>
            <i style={{ width: `${width}%` }} />
          </div>
        ))}
      </div>
    );
  }
  if (type === "scorecard") {
    return (
      <div className="portal-preview-scorecard" aria-hidden="true">
        {["Vendor exposure", "Weighted OTIF", "Fill rate", "Lead deviation"].map(
          (label, index) => (
            <div key={label}>
              <span>{label}</span>
              <strong>{[86, 54, 86, 32][index]}{index === 3 ? "" : "%"}</strong>
              <i><b style={{ width: `${[86, 54, 86, 32][index]}%` }} /></i>
            </div>
          ),
        )}
      </div>
    );
  }
  if (type === "line" || type === "combo") {
    return (
      <div className={`portal-preview-series preview-${type}`} aria-hidden="true">
        {[36, 58, 44, 72, 61, 84, 75, 92].map((height, index) => (
          <i key={`${height}-${index}`} style={{ height: `${height}%` }} />
        ))}
        <b />
      </div>
    );
  }
  if (type === "movement" || type === "butterfly") {
    return (
      <div className={`portal-preview-diverge preview-${type}`} aria-hidden="true">
        {[42, -64, 78, -34, 57].map((value, index) => (
          <div key={`${value}-${index}`}>
            <span />
            <i
              className={value < 0 ? "is-negative" : ""}
              style={{ width: `${Math.abs(value)}%` }}
            />
          </div>
        ))}
      </div>
    );
  }
  if (type === "waterfall") {
    return (
      <div className="portal-preview-waterfall" aria-hidden="true">
        {[78, 42, 24, -18, -10, -36, 54].map((value, index) => (
          <i
            className={value < 0 ? "is-negative" : ""}
            key={`${value}-${index}`}
            style={{ height: `${Math.abs(value)}%` }}
          />
        ))}
      </div>
    );
  }
  if (type === "bcg") {
    return (
      <div className="portal-preview-bcg" aria-hidden="true">
        <span className="axis-x" />
        <span className="axis-y" />
        {[
          [26, 28, 20],
          [71, 22, 15],
          [34, 69, 12],
          [76, 72, 24],
          [56, 49, 10],
        ].map(([left, top, size]) => (
          <i
            key={`${left}-${top}`}
            style={{ left: `${left}%`, top: `${top}%`, width: size, height: size }}
          />
        ))}
      </div>
    );
  }
  if (type === "heatmap") {
    return (
      <div className="portal-preview-heatmap" aria-hidden="true">
        {Array.from({ length: 40 }, (_, index) => (
          <i className={`tone-${index % 5}`} key={index} />
        ))}
      </div>
    );
  }
  if (type === "quality") {
    return (
      <div className="portal-preview-quality" aria-hidden="true">
        {[
          ["Negative stock", "1", "red"],
          ["Zero stock + demand", "2", "amber"],
          ["Missing recipe", "0", "green"],
          ["Missing expected date", "3", "red"],
          ["UOM conversion", "0", "green"],
          ["Missing item master", "0", "green"],
        ].map(([label, value, state]) => (
          <div key={label} className={`state-${state}`}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    );
  }
  return <PlaceholderTable />;
}

export function EmbeddedControlTowerPortal({
  standalone = false,
}: {
  standalone?: boolean;
}) {
  const [pageId, setPageId] = useState(portal.pages[0]?.id ?? "p1");
  const [mode, setMode] = useState<PortalMode>("blueprint");
  const [filters, setFilters] = useState<PageFilterValues>(initialFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<PageFilterValues>(initialFilters);
  const [urlOverrides, setUrlOverrides] = useState<ZohoPortalUrlOverrides>({});
  const [draftUrls, setDraftUrls] = useState<ZohoPortalUrlOverrides>({});
  const [configOpen, setConfigOpen] = useState(false);
  const [configMessage, setConfigMessage] = useState("");
  const handoffInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const hydrateStoredUrls = globalThis.setTimeout(() => {
      try {
        const stored = globalThis.localStorage?.getItem(urlStorageKey);
        if (!stored) return;
        const parsed = sanitizeUrlOverrides(JSON.parse(stored));
        setUrlOverrides(parsed);
        setDraftUrls(parsed);
      } catch {
        globalThis.localStorage?.removeItem(urlStorageKey);
      }
    }, 0);
    return () => globalThis.clearTimeout(hydrateStoredUrls);
  }, []);

  const page = portal.pages.find((item) => item.id === pageId) ?? portal.pages[0]!;
  const configuredUrl = urlOverrides[page.id] || page.dashboardEmbedUrl;
  const configuredCount = portal.pages.filter(
    (item) => urlOverrides[item.id] || item.dashboardEmbedUrl,
  ).length;
  const liveUrl = useMemo(
    () =>
      buildCriteriaUrl(
        configuredUrl,
        page,
        appliedFilters[page.id] ?? {},
      ),
    [appliedFilters, configuredUrl, page],
  );

  const changePage = (nextId: string) => {
    setPageId(nextId);
    const target = portal.pages.find((item) => item.id === nextId);
    if (!(urlOverrides[nextId] || target?.dashboardEmbedUrl)) {
      setMode("blueprint");
    }
  };

  const updateFilter = (filterId: string, value: string) => {
    setFilters((current) => ({
      ...current,
      [page.id]: { ...(current[page.id] ?? {}), [filterId]: value },
    }));
  };

  const resetFilters = () => {
    const values = Object.fromEntries(
      page.filters.map((filter) => [filter.id, filter.defaultValue]),
    );
    setFilters((current) => ({ ...current, [page.id]: values }));
    setAppliedFilters((current) => ({ ...current, [page.id]: values }));
  };

  const saveUrls = () => {
    const invalidPage = portal.pages.find(
      (item) => draftUrls[item.id] && !isSecuredZohoUrl(draftUrls[item.id]),
    );
    if (invalidPage) {
      setConfigMessage(`${invalidPage.label}: enter an HTTPS Zoho Analytics URL.`);
      return;
    }
    const cleaned = Object.fromEntries(
      Object.entries(draftUrls).map(([key, value]) => [key, value.trim()]),
    );
    setUrlOverrides(cleaned);
    globalThis.localStorage?.setItem(urlStorageKey, JSON.stringify(cleaned));
    setConfigMessage("Zoho view URLs saved in this browser.");
  };

  const clearUrls = () => {
    setDraftUrls({});
    setUrlOverrides({});
    setMode("blueprint");
    globalThis.localStorage?.removeItem(urlStorageKey);
    setConfigMessage("Browser-local Zoho view URLs cleared.");
  };

  const downloadHandoff = () => {
    const handoff = buildHandoff({ ...urlOverrides, ...draftUrls });
    const blob = new Blob([`${JSON.stringify(handoff, null, 2)}\n`], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "abnah-zoho-secured-embed-handoff.json";
    anchor.click();
    URL.revokeObjectURL(url);
    setConfigMessage("One-file handoff downloaded. It contains no credentials or report rows.");
  };

  const importHandoff = async (file: File | undefined) => {
    if (!file) return;
    try {
      const urls = parseHandoff(JSON.parse(await file.text()));
      setDraftUrls(urls);
      setUrlOverrides(urls);
      globalThis.localStorage?.setItem(urlStorageKey, JSON.stringify(urls));
      setConfigMessage(
        `${Object.keys(urls).length} secured Zoho dashboard URLs imported and saved in this browser.`,
      );
    } catch (error) {
      setConfigMessage(
        error instanceof Error ? error.message : "The Zoho handoff file could not be read.",
      );
    } finally {
      if (handoffInputRef.current) handoffInputRef.current.value = "";
    }
  };

  if (!page) return null;

  return (
    <section
      className={`zoho-portal-surface portal-page-${page.id}${standalone ? " is-standalone" : ""}`}
    >
      <header className="portal-command-header">
        <div className="portal-command-title">
          <span className="section-kicker">Embedded delivery portal</span>
          <h1>{portal.portalName}</h1>
          <p>{page.title} / {page.subtitle}</p>
        </div>
        <div className="portal-command-actions">
          {standalone ? (
            <a
              className="portal-atlas-link"
              href="../"
              title="Return to the Schema Atlas"
            >
              <ArrowLeft aria-hidden="true" size={15} />
              Atlas
            </a>
          ) : null}
          <span className="portal-auth-state">
            <ShieldCheck aria-hidden="true" size={15} />
            Zoho secured login
          </span>
          <a
            href={portal.auth.loginUrl}
            target="_blank"
            rel="noreferrer"
            title="Open Zoho Analytics sign-in"
          >
            <LogIn aria-hidden="true" size={15} />
            Sign in
          </a>
          <button
            type="button"
            onClick={() => {
              setDraftUrls(urlOverrides);
              setConfigOpen(true);
              setConfigMessage("");
            }}
            title="Configure secured Zoho dashboard URLs"
          >
            <Settings2 aria-hidden="true" size={15} />
            Configure
          </button>
        </div>
      </header>

      <div className="portal-page-toolbar">
        <div>
          <span>Page {portal.pages.findIndex((item) => item.id === page.id) + 1}</span>
          <strong>{page.title}</strong>
          <small>{portal.baselineLabel}</small>
        </div>
        <div className="portal-mode-switch" role="group" aria-label="Portal display mode">
          <button
            type="button"
            className={mode === "blueprint" ? "is-active" : ""}
            onClick={() => setMode("blueprint")}
          >
            <LayoutTemplate aria-hidden="true" size={14} />
            Blueprint
          </button>
          <button
            type="button"
            className={mode === "live" ? "is-active" : ""}
            disabled={!configuredUrl}
            onClick={() => setMode("live")}
          >
            <Monitor aria-hidden="true" size={14} />
            Live Zoho
          </button>
        </div>
      </div>

      {mode === "live" && configuredUrl ? (
        <div className="portal-live-stage">
          {page.filterStrategy === "url_criteria" ? (
            <div className="portal-filterbar is-live">
              {page.filters.map((filter) => (
                <FilterControl
                  filter={filter}
                  key={filter.id}
                  value={filters[page.id]?.[filter.id] ?? filter.defaultValue}
                  onChange={(value) => updateFilter(filter.id, value)}
                />
              ))}
              <div className="portal-filter-actions">
                <button
                  type="button"
                  className="is-primary"
                  onClick={() =>
                    setAppliedFilters((current) => ({
                      ...current,
                      [page.id]: filters[page.id] ?? {},
                    }))
                  }
                >
                  <Check aria-hidden="true" size={14} />
                  Apply
                </button>
                <button type="button" onClick={resetFilters}>
                  <RefreshCcw aria-hidden="true" size={14} />
                  Reset
                </button>
              </div>
            </div>
          ) : null}
          <iframe
            key={liveUrl}
            src={liveUrl}
            title={`${page.title} - Zoho Analytics`}
            loading="eager"
            referrerPolicy="strict-origin-when-cross-origin"
            allowFullScreen
          />
        </div>
      ) : (
        <div className="portal-blueprint-stage">
          <div className="portal-filterbar">
            {page.filters.map((filter) => (
              <FilterControl
                filter={filter}
                key={filter.id}
                value={filters[page.id]?.[filter.id] ?? filter.defaultValue}
                onChange={(value) => updateFilter(filter.id, value)}
              />
            ))}
            <div className="portal-filter-actions">
              <button
                type="button"
                className="is-primary"
                onClick={() =>
                  setAppliedFilters((current) => ({
                    ...current,
                    [page.id]: filters[page.id] ?? {},
                  }))
                }
              >
                <Check aria-hidden="true" size={14} />
                Apply
              </button>
              <button type="button" onClick={resetFilters}>
                <RefreshCcw aria-hidden="true" size={14} />
                Reset
              </button>
            </div>
          </div>

          <div className="portal-kpi-grid">
            {page.metrics.map((metric) => (
              <article className="portal-kpi" key={metric.id}>
                <header>
                  <span>{metric.title}</span>
                  <i
                    className={`capability-${metric.capability}`}
                    title={capabilityLabels[metric.capability]}
                  />
                </header>
                <strong>{metric.expectedValue}</strong>
                <p>{metric.detail}</p>
                <footer title={`${metric.sourceQuery} / ${metric.sourceField} / ${metric.aggregation}`}>
                  {metric.zohoViewName}
                </footer>
              </article>
            ))}
          </div>

          <div className="portal-panel-grid">
            {page.panels.map((panel) => (
              <article
                className={`portal-panel span-${panel.span}`}
                key={panel.id}
              >
                <header>
                  <div>
                    <h2>{panel.title}</h2>
                    <p>{panel.subtitle}</p>
                  </div>
                  <span className={`capability-label state-${panel.capability}`}>
                    {capabilityLabels[panel.capability]}
                  </span>
                </header>
                <PanelPreview type={panel.preview} />
                <footer>
                  <code>{panel.zohoViewName}</code>
                  <span title={panel.sourceFields.join(", ")}>
                    <Info aria-hidden="true" size={12} />
                    {panel.sourceFields.length} fields
                  </span>
                </footer>
              </article>
            ))}
          </div>
        </div>
      )}

      <nav className="portal-bottom-nav" aria-label="Control tower pages">
        {portal.pages.map((item, index) => (
          <button
            type="button"
            key={item.id}
            className={item.id === page.id ? "is-active" : ""}
            onClick={() => changePage(item.id)}
          >
            <span>{index + 1}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {configOpen ? (
        <div className="portal-config-backdrop" role="presentation">
          <aside
            className="portal-config-drawer"
            role="dialog"
            aria-modal="true"
            aria-labelledby="portal-config-title"
          >
            <header>
              <div>
                <span className="section-kicker">Browser-local configuration</span>
                <h2 id="portal-config-title">Zoho dashboard embeds</h2>
              </div>
              <button
                type="button"
                onClick={() => setConfigOpen(false)}
                title="Close configuration"
              >
                <X aria-hidden="true" size={17} />
              </button>
            </header>
            <div className="portal-config-security">
              <ShieldCheck aria-hidden="true" size={16} />
              <p>
                Use secured-login embed URLs only. Access remains controlled by
                the Zoho users with whom each dashboard is shared. No API key
                or OAuth secret is required for this delivery mode.
              </p>
            </div>
            <div className="portal-config-fields">
              {portal.pages.map((item, index) => (
                <label key={item.id}>
                  <span>Page {index + 1} / {item.label}</span>
                  <small>{item.dashboardViewName}</small>
                  <input
                    value={draftUrls[item.id] ?? ""}
                    placeholder="https://analytics.zoho.in/open-view/..."
                    onChange={(event) =>
                      setDraftUrls((current) => ({
                        ...current,
                        [item.id]: event.target.value,
                      }))
                    }
                  />
                </label>
              ))}
            </div>
            {configMessage ? <p className="portal-config-message">{configMessage}</p> : null}
            <footer>
              <input
                ref={handoffInputRef}
                type="file"
                accept="application/json,.json"
                hidden
                onChange={(event) => void importHandoff(event.target.files?.[0])}
              />
              <button
                type="button"
                onClick={() => handoffInputRef.current?.click()}
                title="Import all four secured Zoho URLs from one handoff file"
              >
                <Upload aria-hidden="true" size={14} />
                Import
              </button>
              <button
                type="button"
                onClick={downloadHandoff}
                title="Download a transferable four-dashboard handoff file"
              >
                <Download aria-hidden="true" size={14} />
                Handoff
              </button>
              <button type="button" onClick={clearUrls}>
                <RefreshCcw aria-hidden="true" size={14} />
                Clear
              </button>
              <button type="button" className="is-primary" onClick={saveUrls}>
                <Save aria-hidden="true" size={14} />
                Save locally
              </button>
            </footer>
            <a href={portal.auth.loginUrl} target="_blank" rel="noreferrer">
              Open Zoho Analytics
              <ExternalLink aria-hidden="true" size={13} />
            </a>
          </aside>
        </div>
      ) : null}

      <span className="portal-config-count" aria-live="polite">
        {configuredCount} of {portal.pages.length} Zoho pages connected
      </span>
    </section>
  );
}
