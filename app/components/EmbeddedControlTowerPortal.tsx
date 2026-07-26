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
  LogOut,
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
  ZohoPortalAuthSession,
  ZohoPortalConfig,
  ZohoPortalConfigEnvelope,
  ZohoPortalDashboardUrlOverrides,
  ZohoPortalFilter,
  ZohoPortalFilterBinding,
  ZohoPortalMetric,
  ZohoPortalPanel,
  ZohoPortalPreview,
  ZohoPortalUrlOverrides,
  ZohoPortalUrlMaps,
} from "../lib/zoho-portal-types";
import {
  getReportFilterBindings,
  isViewVisibleForFilters,
} from "../lib/zoho-report-embed-contract";
import {
  buildZohoPortalHandoff,
  handoffToUrlMaps,
  isSecuredZohoUrl,
  normalizeZohoPortalHandoff,
} from "../lib/zoho-portal-handoff";

const portal = portalSnapshot as unknown as ZohoPortalConfig;
const urlStorageKey = "abnah-zoho-view-handoff-v4";

type PortalMode = "blueprint" | "live";
type FilterValues = Record<string, string>;
type PageFilterValues = Record<string, FilterValues>;
type PortalView = ZohoPortalMetric | ZohoPortalPanel;
type AuthLoadState = "loading" | "ready" | "error";

const portalPanels = portal.pages.flatMap((page) =>
  page.panels.map((panel) => ({ ...panel, pageId: page.id })),
);

const emptySession: ZohoPortalAuthSession = {
  authenticated: false,
  configured: false,
  canConfigure: false,
};

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
  bindings: ZohoPortalFilterBinding[],
  values: FilterValues,
) {
  if (!baseUrl) return baseUrl;
  const clauses = bindings.flatMap((binding) => {
    const value = values[binding.filterId];
    if (!value || value === "ALL") return [];
    const comparison =
      binding.operator === "contains"
        ? `LIKE '%${escapeLiteral(value)}%'`
        : `= '${escapeLiteral(value)}'`;
    return [
      `("${escapeIdentifier(binding.criteriaTable)}"."${escapeIdentifier(binding.criteriaColumn)}" ${comparison})`,
    ];
  });
  try {
    const url = new URL(baseUrl);
    if (clauses.length) {
      url.searchParams.set("ZOHO_CRITERIA", clauses.join(" AND "));
    } else {
      url.searchParams.delete("ZOHO_CRITERIA");
    }
    return url.toString();
  } catch {
    return baseUrl;
  }
}

function storedUrlMaps(value: unknown): ZohoPortalUrlMaps {
  return handoffToUrlMaps(normalizeZohoPortalHandoff(value, portal), portal);
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

function ReportEmbed({
  baseUrl,
  pageId,
  title,
  values,
  view,
}: {
  baseUrl: string;
  pageId: string;
  title: string;
  values: FilterValues;
  view: PortalView;
}) {
  const src = useMemo(
    () =>
      buildCriteriaUrl(
        baseUrl,
        getReportFilterBindings(pageId, view),
        values,
      ),
    [baseUrl, pageId, values, view],
  );

  return (
    <div className="portal-report-embed">
      <iframe
        key={src}
        src={src}
        title={`${title} - Zoho Analytics`}
        loading="lazy"
        referrerPolicy="strict-origin-when-cross-origin"
        allowFullScreen
      />
    </div>
  );
}

function FilteredViewNotice() {
  return (
    <div className="portal-filtered-view">
      <span>Excluded by the selected risk scope</span>
    </div>
  );
}

function AccessGate({
  authState,
  error,
  onRetry,
  session,
  standalone,
}: {
  authState: AuthLoadState;
  error: string;
  onRetry: () => void;
  session: ZohoPortalAuthSession;
  standalone: boolean;
}) {
  const isLoading = authState === "loading";
  const needsSetup = authState !== "loading" && !session.configured;
  return (
    <section className={`portal-access-gate${standalone ? " is-standalone" : ""}`}>
      <div className="portal-access-card">
        <span className="portal-access-mark">
          <ShieldCheck aria-hidden="true" size={22} />
        </span>
        <p className="section-kicker">
          {needsSetup ? "Server configuration required" : "Verified analytics access"}
        </p>
        <h1>{portal.portalName}</h1>
        <p>
          {isLoading
            ? "Checking this browser for a verified Zoho Analytics session."
            : needsSetup
              ? "The portal is locked until its server-side Zoho OAuth connection and allowed workspace are configured."
              : "Continue through Zoho. The portal opens only after Zoho confirms that your account can access the configured ABNAH Analytics workspace."}
        </p>
        {error ? <p className="portal-access-error">{error}</p> : null}
        {needsSetup && session.missingEnvironment?.length ? (
          <p className="portal-access-environment">
            Missing: {session.missingEnvironment.join(", ")}
          </p>
        ) : null}
        {!isLoading ? (
          <div>
            {!needsSetup ? (
              <a href="/api/zoho-auth/start">
                <LogIn aria-hidden="true" size={15} />
                Continue with Zoho
              </a>
            ) : null}
            <button type="button" onClick={onRetry}>
              <RefreshCcw aria-hidden="true" size={15} />
              Check again
            </button>
          </div>
        ) : (
          <span className="portal-access-checking">
            <RefreshCcw aria-hidden="true" size={15} />
            Verifying session
          </span>
        )}
        <small>
          The app never receives your Zoho password. It verifies the OAuth
          session and workspace membership on the server before loading any
          saved report URL.
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
  const [filters, setFilters] = useState<PageFilterValues>(initialFilters);
  const [appliedFilters, setAppliedFilters] =
    useState<PageFilterValues>(initialFilters);
  const [urlOverrides, setUrlOverrides] = useState<ZohoPortalUrlOverrides>({});
  const [draftUrls, setDraftUrls] = useState<ZohoPortalUrlOverrides>({});
  const [dashboardUrls, setDashboardUrls] =
    useState<ZohoPortalDashboardUrlOverrides>({});
  const [draftDashboardUrls, setDraftDashboardUrls] =
    useState<ZohoPortalDashboardUrlOverrides>({});
  const [configOpen, setConfigOpen] = useState(false);
  const [configMessage, setConfigMessage] = useState("");
  const [configVersion, setConfigVersion] = useState(0);
  const [configUpdatedAt, setConfigUpdatedAt] = useState<string | null>(null);
  const [configUpdatedBy, setConfigUpdatedBy] = useState<string | null>(null);
  const [configBusy, setConfigBusy] = useState(false);
  const [authSession, setAuthSession] =
    useState<ZohoPortalAuthSession>(emptySession);
  const [authState, setAuthState] = useState<AuthLoadState>("loading");
  const [authError, setAuthError] = useState("");
  const [authAttempt, setAuthAttempt] = useState(0);
  const handoffInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let cancelled = false;
    const hydrate = async () => {
      setAuthState("loading");
      const callbackError = new URL(globalThis.location.href).searchParams.get(
        "auth_error",
      );
      setAuthError(callbackError ?? "");
      try {
        const response = await fetch("/api/zoho-auth/session", {
          credentials: "same-origin",
          cache: "no-store",
        });
        if (!response.ok) {
          throw new Error("The secured authentication service is unavailable.");
        }
        const session = (await response.json()) as ZohoPortalAuthSession;
        if (cancelled) return;
        setAuthSession(session);
        setAuthState("ready");
        if (!session.authenticated) return;

        try {
          const configResponse = await fetch("/api/zoho-portal-config", {
            credentials: "same-origin",
            cache: "no-store",
          });
          const payload = (await configResponse.json()) as
            | ZohoPortalConfigEnvelope
            | { error?: string };
          if (!configResponse.ok || !("handoff" in payload)) {
            throw new Error(
              "error" in payload && payload.error
                ? payload.error
                : "The shared URL handoff could not be loaded.",
            );
          }
          const handoff = normalizeZohoPortalHandoff(payload.handoff, portal);
          const maps = handoffToUrlMaps(handoff, portal);
          if (cancelled) return;
          setUrlOverrides(maps.reports);
          setDraftUrls(maps.reports);
          setDashboardUrls(maps.dashboards);
          setDraftDashboardUrls(maps.dashboards);
          setConfigVersion(payload.version);
          setConfigUpdatedAt(payload.updatedAt);
          setConfigUpdatedBy(payload.updatedBy);
          globalThis.localStorage?.setItem(
            urlStorageKey,
            JSON.stringify(handoff),
          );
        } catch (configError) {
          const stored = globalThis.localStorage?.getItem(urlStorageKey);
          if (stored) {
            try {
              const maps = storedUrlMaps(JSON.parse(stored));
              setUrlOverrides(maps.reports);
              setDraftUrls(maps.reports);
              setDashboardUrls(maps.dashboards);
              setDraftDashboardUrls(maps.dashboards);
            } catch {
              globalThis.localStorage?.removeItem(urlStorageKey);
            }
          }
          setConfigMessage(
            configError instanceof Error
              ? `${configError.message} A browser cache was used when available.`
              : "The shared URL handoff could not be loaded.",
          );
        }
      } catch (error) {
        if (cancelled) return;
        setAuthSession(emptySession);
        setAuthState("error");
        setAuthError(
          error instanceof Error
            ? error.message
            : "The Zoho session could not be verified.",
        );
      }
    };
    void hydrate();
    return () => {
      cancelled = true;
    };
  }, [authAttempt]);

  const page = portal.pages.find((item) => item.id === pageId) ?? portal.pages[0]!;
  const configPage =
    portal.pages.find((item) => item.id === configPageId) ?? portal.pages[0]!;
  const configuredCount = portalPanels.filter(
    (panel) => urlOverrides[panel.id],
  ).length;
  const configuredPageCount = page.panels.filter(
    (panel) => urlOverrides[panel.id],
  ).length;

  const openConfiguration = () => {
    setConfigPageId(page.id);
    setDraftUrls(urlOverrides);
    setDraftDashboardUrls(dashboardUrls);
    setConfigOpen(true);
    setConfigMessage("");
  };

  const configuredUrlFor = (panel: ZohoPortalPanel) =>
    urlOverrides[panel.id] || panel.embedUrl || "";

  const viewIsVisible = (view: PortalView) =>
    isViewVisibleForFilters(
      page.id,
      view,
      appliedFilters[page.id] ?? {},
    );

  const renderPanelBody = (panel: ZohoPortalPanel) => {
    const configuredUrl = configuredUrlFor(panel);
    if (mode === "live" && configuredUrl) {
      if (!viewIsVisible(panel)) return <FilteredViewNotice />;
      return (
        <ReportEmbed
          baseUrl={configuredUrl}
          pageId={page.id}
          title={panel.title}
          values={appliedFilters[page.id] ?? {}}
          view={panel}
        />
      );
    }
    return <PanelPreview type={panel.preview} />;
  };

  const pageViewCount = page.panels.length;

  const changePage = (nextId: string) => {
    setPageId(nextId);
    const target = portal.pages.find((item) => item.id === nextId);
    if (
      !target ||
      !target.panels.some((panel) => urlOverrides[panel.id])
    ) {
      setMode("blueprint");
    }
  };

  const updateFilter = (filterId: string, value: string) => {
    setFilters((current) => ({
      ...current,
      [page.id]: { ...(current[page.id] ?? {}), [filterId]: value },
    }));
  };

  const applyFilters = () =>
    setAppliedFilters((current) => ({
      ...current,
      [page.id]: filters[page.id] ?? {},
    }));

  const resetFilters = () => {
    const values = Object.fromEntries(
      page.filters.map((filter) => [filter.id, filter.defaultValue]),
    );
    setFilters((current) => ({ ...current, [page.id]: values }));
    setAppliedFilters((current) => ({ ...current, [page.id]: values }));
  };

  const saveUrls = async () => {
    if (!authSession.canConfigure) {
      setConfigMessage(
        "This verified Zoho user can view the portal but cannot edit its shared URL handoff.",
      );
      return;
    }
    const invalidPanel = portalPanels.find(
      (panel) =>
        draftUrls[panel.id] && !isSecuredZohoUrl(draftUrls[panel.id]),
    );
    if (invalidPanel) {
      setConfigMessage(
        `${invalidPanel.zohoViewName}: enter an HTTPS Zoho Analytics URL.`,
      );
      return;
    }
    const invalidDashboard = portal.pages.find(
      (item) =>
        draftDashboardUrls[item.id] &&
        !isSecuredZohoUrl(draftDashboardUrls[item.id]),
    );
    if (invalidDashboard) {
      setConfigMessage(
        `${invalidDashboard.dashboardViewName}: enter an HTTPS Zoho Analytics URL.`,
      );
      return;
    }
    const maps: ZohoPortalUrlMaps = {
      reports: Object.fromEntries(
        portalPanels.map((panel) => [
          panel.id,
          draftUrls[panel.id]?.trim() ?? "",
        ]),
      ),
      dashboards: Object.fromEntries(
        portal.pages.map((item) => [
          item.id,
          draftDashboardUrls[item.id]?.trim() ?? "",
        ]),
      ),
    };
    const handoff = buildZohoPortalHandoff(portal, maps);
    setConfigBusy(true);
    setConfigMessage("Saving the shared URL handoff...");
    try {
      const response = await fetch("/api/zoho-portal-config", {
        method: "PUT",
        credentials: "same-origin",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          handoff,
          expectedVersion: configVersion,
        }),
      });
      const payload = (await response.json()) as
        | ZohoPortalConfigEnvelope
        | { error?: string };
      if (!response.ok || !("handoff" in payload)) {
        throw new Error(
          "error" in payload && payload.error
            ? payload.error
            : "The shared URL handoff could not be saved.",
        );
      }
      const savedHandoff = normalizeZohoPortalHandoff(payload.handoff, portal);
      const savedMaps = handoffToUrlMaps(savedHandoff, portal);
      setUrlOverrides(savedMaps.reports);
      setDraftUrls(savedMaps.reports);
      setDashboardUrls(savedMaps.dashboards);
      setDraftDashboardUrls(savedMaps.dashboards);
      setConfigVersion(payload.version);
      setConfigUpdatedAt(payload.updatedAt);
      setConfigUpdatedBy(payload.updatedBy);
      globalThis.localStorage?.setItem(
        urlStorageKey,
        JSON.stringify(savedHandoff),
      );
      setConfigMessage(
        `Version ${payload.version} saved for every verified portal user.`,
      );
    } catch (error) {
      setConfigMessage(
        error instanceof Error
          ? error.message
          : "The shared URL handoff could not be saved.",
      );
    } finally {
      setConfigBusy(false);
    }
  };

  const clearUrls = () => {
    setDraftUrls({});
    setDraftDashboardUrls({});
    setConfigMessage(
      "All draft URLs cleared. Select Save shared handoff to publish the change.",
    );
  };

  const downloadHandoff = () => {
    const handoff = buildZohoPortalHandoff(portal, {
      reports: draftUrls,
      dashboards: draftDashboardUrls,
    });
    const blob = new Blob([`${JSON.stringify(handoff, null, 2)}\n`], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "abnah-zoho-view-handoff-v4.json";
    anchor.click();
    URL.revokeObjectURL(url);
    setConfigMessage(
      "Transferable v4 handoff downloaded. It contains no credentials, tokens, or report rows.",
    );
  };

  const importHandoff = async (file: File | undefined) => {
    if (!file) return;
    try {
      const handoff = normalizeZohoPortalHandoff(
        JSON.parse(await file.text()),
        portal,
      );
      const maps = handoffToUrlMaps(handoff, portal);
      setDraftUrls(maps.reports);
      setDraftDashboardUrls(maps.dashboards);
      setConfigMessage(
        "Handoff imported as a draft. Review it, then select Save shared handoff.",
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

  const signOut = async () => {
    await fetch("/api/zoho-auth/logout", {
      method: "POST",
      credentials: "same-origin",
    }).catch(() => undefined);
    setAuthSession(emptySession);
    setUrlOverrides({});
    setDashboardUrls({});
    setMode("blueprint");
    setAuthState("ready");
  };

  if (!page) return null;
  if (authState !== "ready" || !authSession.authenticated) {
    return (
      <AccessGate
        authState={authState}
        error={authError}
        onRetry={() => setAuthAttempt((attempt) => attempt + 1)}
        session={authSession}
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
          <span
            className="portal-auth-state"
            title={`${authSession.user?.email ?? "Verified Zoho user"} / ${authSession.workspace?.name ?? "Allowed workspace"}`}
          >
            <ShieldCheck aria-hidden="true" size={15} />
            {authSession.user?.displayName ||
              authSession.user?.email ||
              "Zoho verified"}
          </span>
          {dashboardUrls[page.id] ? (
            <a
              href={dashboardUrls[page.id]}
              target="_blank"
              rel="noreferrer"
              title="Open this page in the native Zoho dashboard"
            >
              <ExternalLink aria-hidden="true" size={15} />
              Native fallback
            </a>
          ) : null}
          <button
            type="button"
            onClick={openConfiguration}
            disabled={!authSession.canConfigure}
            title={
              authSession.canConfigure
                ? "Configure individual secured Zoho report URLs"
                : "This Zoho user has view-only portal access"
            }
          >
            <Settings2 aria-hidden="true" size={15} />
            Configure
          </button>
          <button type="button" onClick={() => void signOut()} title="Sign out">
            <LogOut aria-hidden="true" size={15} />
            Sign out
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
            Live reports
          </button>
        </div>
      </div>

      <div
        className={`portal-blueprint-stage${mode === "live" ? " is-live-reports" : ""}`}
      >
        <div className={`portal-filterbar${mode === "live" ? " is-live" : ""}`}>
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
              onClick={applyFilters}
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
              <p>
                {metric.detail}
                <span className="portal-kpi-value-state">
                  {mode === "live"
                    ? "Validated baseline / live API pending"
                    : "Validated baseline"}
                </span>
              </p>
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
              className={`portal-panel span-${panel.span}${mode === "live" && configuredUrlFor(panel) ? " has-live-view" : ""}`}
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
              {renderPanelBody(panel)}
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

      <nav className="portal-bottom-nav" aria-label="Control tower pages">
        {portal.pages.map((item, index) => (
          <button
            type="button"
            key={item.id}
            className={item.id === page.id ? "is-active" : ""}
            onClick={() => changePage(item.id)}
          >
            <span className="portal-page-index">{index + 1}</span>
            <span className="portal-page-label">{item.label}</span>
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
                <span className="section-kicker">Shared secured configuration</span>
                <h2 id="portal-config-title">Zoho view handoff</h2>
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
                Paste secured-login view URLs only. The saved mapping is shared
                across verified portal users; OAuth secrets and operational
                report rows never enter this handoff.
              </p>
            </div>
            <div className="portal-config-page-tabs">
              {portal.pages.map((item, index) => {
                const total = item.panels.length;
                const connected = item.panels.filter(
                  (panel) => draftUrls[panel.id],
                ).length;
                return (
                  <button
                    type="button"
                    key={item.id}
                    className={item.id === configPage.id ? "is-active" : ""}
                    onClick={() => setConfigPageId(item.id)}
                  >
                    <span>{index + 1}</span>
                    {connected}/{total}
                  </button>
                );
              })}
            </div>
            <div className="portal-config-fields">
              <div className="portal-config-page-heading">
                <strong>{configPage.title}</strong>
                <span>{configPage.panels.length} report slots</span>
              </div>
              <label className="portal-config-dashboard-field">
                <span>Native page fallback</span>
                <small>{configPage.dashboardViewName}</small>
                <input
                  value={draftDashboardUrls[configPage.id] ?? ""}
                  placeholder="https://analytics.zoho.in/open-view/..."
                  onChange={(event) =>
                    setDraftDashboardUrls((current) => ({
                      ...current,
                      [configPage.id]: event.target.value,
                    }))
                  }
                />
              </label>
              <div className="portal-config-section-label">
                Individual chart and table views
              </div>
              {configPage.panels.map((panel) => (
                <label key={panel.id}>
                  <span>{panel.title}</span>
                  <small>{panel.zohoViewName}</small>
                  <input
                    value={draftUrls[panel.id] ?? ""}
                    placeholder="https://analytics.zoho.in/open-view/..."
                    onChange={(event) =>
                      setDraftUrls((current) => ({
                        ...current,
                        [panel.id]: event.target.value,
                      }))
                    }
                  />
                </label>
              ))}
            </div>
            <p className="portal-config-metadata">
              Shared version {configVersion}
              {configUpdatedAt
                ? ` / updated ${new Date(configUpdatedAt).toLocaleString()}`
                : " / not yet published"}
              {configUpdatedBy ? ` / ${configUpdatedBy}` : ""}
            </p>
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
                disabled={configBusy}
                title="Import a v4 Zoho view handoff"
              >
                <Upload aria-hidden="true" size={14} />
                Import
              </button>
              <button
                type="button"
                onClick={downloadHandoff}
                disabled={configBusy}
                title="Download the transferable v4 handoff"
              >
                <Download aria-hidden="true" size={14} />
                Handoff
              </button>
              <button type="button" onClick={clearUrls} disabled={configBusy}>
                <RefreshCcw aria-hidden="true" size={14} />
                Clear
              </button>
              <button
                type="button"
                className="is-primary"
                disabled={configBusy}
                onClick={() => void saveUrls()}
              >
                <Save aria-hidden="true" size={14} />
                {configBusy ? "Saving" : "Save shared handoff"}
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
        {configuredCount} of {portalPanels.length} report views connected /{" "}
        {configuredPageCount} of {pageViewCount} on this page / config v
        {configVersion}
      </span>
    </section>
  );
}
