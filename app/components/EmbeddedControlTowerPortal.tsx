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
import { useEffect, useRef, useState } from "react";
import type {
  ZohoPortalCapability,
  ZohoPortalConfig,
  ZohoPortalHandoff,
  ZohoPortalPreview,
  ZohoPortalUrlOverrides,
} from "../lib/zoho-portal-types";

const portal = portalSnapshot as unknown as ZohoPortalConfig;
const urlStorageKey = "abnah-zoho-dashboard-urls-v3";
const accessStorageKey = "abnah-zoho-access-preflight-v1";
const handoffSchema = "abnah-zoho-dashboard-embed-handoff/v3";

type PortalMode = "blueprint" | "live";

const capabilityLabels: Record<ZohoPortalCapability, string> = {
  native: "Zoho native",
  native_better: "Zoho enhanced",
  custom_required: "Custom finish",
};

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
    integrationMode: "page_dashboard_views",
    note:
      "Secured Zoho iframe src URLs for the four page dashboards only. This file must not contain passwords, OAuth tokens, client secrets, or operational rows.",
    pages: Object.fromEntries(
      portal.pages.map((page) => [
        page.id,
        {
          dashboardViewName: page.dashboardViewName,
          securedDashboardEmbedUrl: urls[page.id]?.trim() ?? "",
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
    candidate.integrationMode !== "page_dashboard_views" ||
    !candidate.pages ||
    typeof candidate.pages !== "object"
  ) {
    throw new Error(
      "Use an ABNAH page-dashboard secured-embed handoff v3 JSON file.",
    );
  }
  const urls = Object.fromEntries(
    portal.pages.map((page) => {
      const handoffPage = candidate.pages?.[page.id];
      const url =
        handoffPage &&
        typeof handoffPage.securedDashboardEmbedUrl === "string"
          ? handoffPage.securedDashboardEmbedUrl.trim()
          : "";
      if (url && !isSecuredZohoUrl(url)) {
        throw new Error(
          `${page.dashboardViewName}: the embed URL is not an approved HTTPS Zoho Analytics URL.`,
        );
      }
      return [page.id, url];
    }),
  );
  return sanitizeUrlOverrides(urls);
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

function DashboardEmbed({ src, title }: { src: string; title: string }) {
  return (
    <div className="portal-dashboard-embed">
      <iframe
        key={src}
        src={src}
        title={`${title} dashboard - Zoho Analytics`}
        loading="lazy"
        referrerPolicy="strict-origin-when-cross-origin"
        allowFullScreen
      />
    </div>
  );
}

function AccessGate({
  onContinue,
  standalone,
}: {
  onContinue: () => void;
  standalone: boolean;
}) {
  return (
    <section className={`portal-access-gate${standalone ? " is-standalone" : ""}`}>
      <div className="portal-access-card">
        <span className="portal-access-mark">
          <ShieldCheck aria-hidden="true" size={22} />
        </span>
        <p className="section-kicker">Secured analytics access</p>
        <h1>{portal.portalName}</h1>
        <p>
          Sign in with the Zoho Analytics account that has been granted access
          to the ABNAH reports, then return here to open the control tower.
        </p>
        <div>
          <a href={portal.auth.loginUrl} target="_blank" rel="noreferrer">
            <LogIn aria-hidden="true" size={15} />
            Sign in with Zoho
          </a>
          <button type="button" onClick={onContinue}>
            <Check aria-hidden="true" size={15} />
            Continue after sign-in
          </button>
        </div>
        <small>
          Report access is verified by Zoho. The outer portal does not receive
          or store your password.
        </small>
      </div>
    </section>
  );
}

export function EmbeddedControlTowerPortal({
  standalone = false,
}: {
  standalone?: boolean;
}) {
  const [pageId, setPageId] = useState(portal.pages[0]?.id ?? "p1");
  const [configPageId, setConfigPageId] = useState(
    portal.pages[0]?.id ?? "p1",
  );
  const [mode, setMode] = useState<PortalMode>("blueprint");
  const [urlOverrides, setUrlOverrides] = useState<ZohoPortalUrlOverrides>({});
  const [draftUrls, setDraftUrls] = useState<ZohoPortalUrlOverrides>({});
  const [configOpen, setConfigOpen] = useState(false);
  const [configMessage, setConfigMessage] = useState("");
  const [accessReady, setAccessReady] = useState(!standalone);
  const handoffInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const hydrateStoredUrls = globalThis.setTimeout(() => {
      try {
        const stored = globalThis.localStorage?.getItem(urlStorageKey);
        if (stored) {
          const parsed = sanitizeUrlOverrides(JSON.parse(stored));
          setUrlOverrides(parsed);
          setDraftUrls(parsed);
        }
      } catch {
        globalThis.localStorage?.removeItem(urlStorageKey);
      }
      if (
        standalone &&
        globalThis.sessionStorage?.getItem(accessStorageKey) === "ready"
      ) {
        setAccessReady(true);
      }
    }, 0);
    return () => globalThis.clearTimeout(hydrateStoredUrls);
  }, [standalone]);

  const page = portal.pages.find((item) => item.id === pageId) ?? portal.pages[0]!;
  const configPage =
    portal.pages.find((item) => item.id === configPageId) ?? portal.pages[0]!;
  const configuredCount = portal.pages.filter(
    (item) => urlOverrides[item.id] || item.dashboardEmbedUrl,
  ).length;
  const configuredDashboardUrl =
    urlOverrides[page.id] || page.dashboardEmbedUrl;
  const configuredPageCount = configuredDashboardUrl ? 1 : 0;

  const continueAfterSignIn = () => {
    globalThis.sessionStorage?.setItem(accessStorageKey, "ready");
    setAccessReady(true);
  };

  const openConfiguration = () => {
    setConfigPageId(page.id);
    setDraftUrls(urlOverrides);
    setConfigOpen(true);
    setConfigMessage("");
  };

  const changePage = (nextId: string) => {
    setPageId(nextId);
    const target = portal.pages.find((item) => item.id === nextId);
    if (!target || !(urlOverrides[target.id] || target.dashboardEmbedUrl)) {
      setMode("blueprint");
    }
  };

  const saveUrls = () => {
    const invalidPage = portal.pages.find(
      (item) =>
        draftUrls[item.id] && !isSecuredZohoUrl(draftUrls[item.id]),
    );
    if (invalidPage) {
      setConfigMessage(
        `${invalidPage.dashboardViewName}: enter an HTTPS Zoho Analytics URL.`,
      );
      return;
    }
    const cleaned = Object.fromEntries(
      Object.entries(draftUrls)
        .map(([key, value]) => [key, value.trim()])
        .filter(([, value]) => value),
    );
    setUrlOverrides(cleaned);
    globalThis.localStorage?.setItem(urlStorageKey, JSON.stringify(cleaned));
    setConfigMessage(
      `${Object.keys(cleaned).length} Zoho page dashboard URLs saved in this browser.`,
    );
  };

  const clearUrls = () => {
    setDraftUrls({});
    setUrlOverrides({});
    setMode("blueprint");
    globalThis.localStorage?.removeItem(urlStorageKey);
    setConfigMessage("Browser-local Zoho dashboard URLs cleared.");
  };

  const downloadHandoff = () => {
    const handoff = buildHandoff({ ...urlOverrides, ...draftUrls });
    const blob = new Blob([`${JSON.stringify(handoff, null, 2)}\n`], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "abnah-zoho-dashboard-embed-handoff.json";
    anchor.click();
    URL.revokeObjectURL(url);
    setConfigMessage(
      "One-file dashboard handoff downloaded. It contains no credentials or report rows.",
    );
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
        error instanceof Error
          ? error.message
          : "The Zoho handoff file could not be read.",
      );
    } finally {
      if (handoffInputRef.current) handoffInputRef.current.value = "";
    }
  };

  if (!page) return null;
  if (!accessReady) {
    return (
      <AccessGate
        onContinue={continueAfterSignIn}
        standalone={standalone}
      />
    );
  }

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
            onClick={openConfiguration}
            title="Configure secured Zoho page dashboard URLs"
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
            disabled={!configuredPageCount}
            onClick={() => setMode("live")}
          >
            <Monitor aria-hidden="true" size={14} />
            Live dashboard
          </button>
        </div>
      </div>

      {mode === "live" && configuredDashboardUrl ? (
        <div className="portal-live-stage">
          <DashboardEmbed src={configuredDashboardUrl} title={page.title} />
        </div>
      ) : (
        <div className="portal-blueprint-stage">
          <div className="portal-filterbar portal-filter-contract">
            {page.filters.map((filter) => (
              <div className="portal-filter-token" key={filter.id}>
                <span>{filter.label}</span>
                <strong>
                  {page.criteriaColumns[filter.id] ?? "Mapped per dashboard object"}
                </strong>
              </div>
            ))}
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
                <footer
                  title={`${metric.sourceQuery} / ${metric.sourceField} / ${metric.aggregation}`}
                >
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
                <h2 id="portal-config-title">Zoho page dashboards</h2>
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
                the Zoho users with whom each dashboard is shared. Add only
                the iframe src URL; no API key or OAuth secret is required.
              </p>
            </div>
            <div className="portal-config-page-tabs">
              {portal.pages.map((item, index) => (
                <button
                  type="button"
                  key={item.id}
                  className={item.id === configPage.id ? "is-active" : ""}
                  onClick={() => setConfigPageId(item.id)}
                >
                  <span>{index + 1}</span>
                  {draftUrls[item.id] || item.dashboardEmbedUrl ? "1/1" : "0/1"}
                </button>
              ))}
            </div>
            <div className="portal-config-fields">
              <div className="portal-config-page-heading">
                <strong>{configPage.title}</strong>
                <span>1 secured page dashboard</span>
              </div>
              <label>
                <span>Page dashboard</span>
                <small>{configPage.dashboardViewName}</small>
                <input
                  value={draftUrls[configPage.id] ?? ""}
                  placeholder="https://analytics.zoho.in/open-view/..."
                  onChange={(event) =>
                    setDraftUrls((current) => ({
                      ...current,
                      [configPage.id]: event.target.value,
                    }))
                  }
                />
              </label>
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
                title="Import the four secured Zoho dashboard URLs"
              >
                <Upload aria-hidden="true" size={14} />
                Import
              </button>
              <button
                type="button"
                onClick={downloadHandoff}
                title="Download the transferable dashboard handoff file"
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
        {configuredCount} of {portal.pages.length} Zoho page dashboards connected
      </span>
    </section>
  );
}
