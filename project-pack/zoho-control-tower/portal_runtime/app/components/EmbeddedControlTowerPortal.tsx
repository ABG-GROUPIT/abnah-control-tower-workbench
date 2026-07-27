"use client";

import {
  AlertTriangle,
  ArrowLeft,
  ChartNoAxesCombined,
  Database,
  ExternalLink,
  LoaderCircle,
  LogIn,
  LogOut,
  RefreshCw,
  ShieldCheck,
  ShoppingCart,
  Table2,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import portalSnapshot from "@/config/zoho-portal.json";
import {
  clearPortalSessionToken,
  consumePortalCallback,
  getControlTowerDemoData,
  getControlTowerPageData,
  getPortalAuthSession,
  getPortalBackendStatus,
  getSharedPortalConfig,
  isPortalBackendConfigured,
  portalSignInUrl,
  revokePortalSession,
} from "../lib/supabase-portal-client";
import { handoffToUrlMaps } from "../lib/zoho-portal-handoff";
import type {
  ZohoPortalConfig,
  ZohoPortalUrlMaps,
} from "../lib/zoho-portal-types";
import type {
  PortalDemoData,
  PortalPageData,
  PortalPageId,
} from "../lib/control-tower-portal-data";
import { ProcurementPage } from "./control-tower-portal/ProcurementPage";
import { RiskActionPage } from "./control-tower-portal/RiskActionPage";

type NavigationPage = PortalPageId | "p3" | "p4";
type AccessState =
  | "checking"
  | "local-preview"
  | "authenticated"
  | "signed-out"
  | "not-configured"
  | "unavailable";

const pageDefinitions: Array<{
  id: NavigationPage;
  icon: LucideIcon;
  shortLabel: string;
  label: string;
  title: string;
  subtitle: string;
  available: boolean;
}> = [
  {
    id: "p1",
    icon: AlertTriangle,
    shortLabel: "Risk",
    label: "Risk Action Center",
    title: "Risk Action Center",
    subtitle: "Stockout, expiry, menu impact and action ownership",
    available: true,
  },
  {
    id: "p2",
    icon: ShoppingCart,
    shortLabel: "Procurement",
    label: "Procurement & Vendor",
    title: "Procurement, Vendor & Capital Control",
    subtitle: "Purchase exposure, supplier performance and price movement",
    available: true,
  },
  {
    id: "p3",
    icon: ChartNoAxesCombined,
    shortLabel: "Consumption",
    label: "Consumption & Menu",
    title: "Consumption Variance & Menu Profitability",
    subtitle: "Actual versus theoretical consumption and menu economics",
    available: false,
  },
  {
    id: "p4",
    icon: Table2,
    shortLabel: "Explorer",
    label: "Explorer & Quality",
    title: "SCM Descriptive Explorer & Data Quality",
    subtitle: "Trend, drilldown and model-quality exceptions",
    available: false,
  },
];

const portalDefinition = portalSnapshot as unknown as ZohoPortalConfig;

function staticVisualMaps(): ZohoPortalUrlMaps {
  return {
    reports: Object.fromEntries(
      portalDefinition.pages.flatMap((page) =>
        page.panels.map((panel) => [panel.id, panel.embedUrl || ""]),
      ),
    ),
    dashboards: Object.fromEntries(
      portalDefinition.pages.map((page) => [
        page.id,
        page.dashboardEmbedUrl || "",
      ]),
    ),
  };
}

function configuredInitialRange() {
  const configured = portalDefinition.defaultRange;
  if (
    configured &&
    /^\d{4}-\d{2}-\d{2}$/.test(configured.start) &&
    /^\d{4}-\d{2}-\d{2}$/.test(configured.end) &&
    configured.start <= configured.end
  ) {
    return { ...configured };
  }

  const now = new Date();
  const end = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, "0"),
    String(now.getDate()).padStart(2, "0"),
  ].join("-");
  const start = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-01`;
  return { start, end };
}

function isLoopbackHost() {
  if (typeof globalThis.location === "undefined") return false;
  return ["localhost", "127.0.0.1"].includes(
    globalThis.location.hostname.toLowerCase(),
  );
}

function atlasUrl() {
  if (typeof globalThis.location === "undefined") return "/";
  const path = globalThis.location.pathname.replace(
    /\/portal(?:\/index\.html)?\/?$/,
    "/",
  );
  return path.endsWith("/") ? path : `${path}/`;
}

function formatRefreshTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not yet refreshed";
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function AccessGate({
  state,
  message,
}: {
  state: AccessState;
  message: string;
}) {
  const canSignIn =
    state === "signed-out" && isPortalBackendConfigured() && portalSignInUrl();

  return (
    <main className="ct-access-stage">
      <section className="ct-access-panel">
        <div className="ct-access-mark">
          {state === "checking" ? (
            <LoaderCircle aria-hidden="true" className="ct-spin" size={27} />
          ) : (
            <ShieldCheck aria-hidden="true" size={27} />
          )}
        </div>
        <span className="ct-eyebrow">ABNAH SUPPLY CHAIN</span>
        <h1>Control Tower</h1>
        <p>{message}</p>
        {canSignIn ? (
          <a className="ct-access-button" href={canSignIn}>
            <LogIn aria-hidden="true" size={17} />
            Sign in with Zoho
          </a>
        ) : null}
        <a className="ct-access-secondary" href={atlasUrl()}>
          <ArrowLeft aria-hidden="true" size={15} />
          Return to Data Atlas
        </a>
      </section>
    </main>
  );
}

function ComingSoon({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  return (
    <main className="ct-coming-stage">
      <section>
        <span className="ct-eyebrow">NEXT RELEASE</span>
        <h2>{title}</h2>
        <p>{subtitle}</p>
        <div className="ct-coming-rail" aria-label="Planned page status">
          <span className="is-complete">Data model</span>
          <span className="is-complete">KPI lineage</span>
          <span>Portal build</span>
        </div>
        <strong>Coming soon</strong>
      </section>
    </main>
  );
}

export function EmbeddedControlTowerPortal({
  standalone = false,
}: {
  standalone?: boolean;
}) {
  const [activePage, setActivePage] = useState<NavigationPage>("p1");
  const [accessState, setAccessState] = useState<AccessState>("checking");
  const [accessMessage, setAccessMessage] = useState(
    "Verifying your approved workspace access.",
  );
  const [userName, setUserName] = useState("");
  const [pageData, setPageData] = useState<
    Partial<Record<PortalPageId, PortalPageData>>
  >({});
  const [demoData, setDemoData] = useState<PortalDemoData | null>(null);
  const [loadingData, setLoadingData] = useState(false);
  const [dataMessage, setDataMessage] = useState("");
  const [refreshVersion, setRefreshVersion] = useState(0);
  const [requestRange, setRequestRange] = useState(configuredInitialRange);
  const [visualUrls, setVisualUrls] =
    useState<ZohoPortalUrlMaps>(staticVisualMaps);

  useEffect(() => {
    let active = true;
    const establishAccess = async () => {
      const callback = consumePortalCallback();
      if (callback.error && active) {
        setDataMessage(callback.error);
      }

      if (!isPortalBackendConfigured()) {
        if (isLoopbackHost()) {
          try {
            const demo = await getControlTowerDemoData();
            if (!active) return;
            setDemoData(demo);
            setRequestRange(demo.defaultRange);
            setAccessState("local-preview");
            setUserName("Local validation");
            setAccessMessage("");
          } catch {
            if (!active) return;
            setAccessState("unavailable");
            setAccessMessage(
              "The validation dataset could not be opened on this device.",
            );
          }
          return;
        }
        if (!active) return;
        setAccessState("not-configured");
        setAccessMessage(
          "Portal access is being prepared. Contact the workspace administrator.",
        );
        return;
      }

      try {
        const status = await getPortalBackendStatus();
        if (!active) return;
        if (!status.configured) {
          setAccessState("not-configured");
          setAccessMessage(
            "Portal access is being prepared. Contact the workspace administrator.",
          );
          return;
        }
        const session = await getPortalAuthSession();
        if (!active) return;
        if (!session.authenticated) {
          setAccessState("signed-out");
          setAccessMessage(
            "Sign in with your approved Zoho Analytics account to continue.",
          );
          return;
        }
        setAccessState("authenticated");
        setUserName(session.user?.displayName || session.user?.email || "Signed in");
        setAccessMessage("");
      } catch {
        if (!active) return;
        setAccessState("unavailable");
        setAccessMessage(
          "The control tower is temporarily unavailable. Please try again shortly.",
        );
      }
    };

    void establishAccess();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    if (accessState !== "authenticated") {
      return () => {
        active = false;
      };
    }
    void getSharedPortalConfig()
      .then((envelope) => {
        if (!active) return;
        setVisualUrls(
          handoffToUrlMaps(envelope.handoff, portalDefinition),
        );
      })
      .catch(() => {
        if (!active) return;
        setVisualUrls(staticVisualMaps());
        setDataMessage(
          "Zoho visual links could not be loaded. API-backed tables remain available.",
        );
      });
    return () => {
      active = false;
    };
  }, [accessState]);

  const loadPage = useCallback(
    async (page: PortalPageId) => {
      if (accessState === "local-preview") return;
      if (accessState !== "authenticated") return;
      setLoadingData(true);
      setDataMessage("");
      try {
        const data = await getControlTowerPageData(
          page,
          requestRange.start,
          requestRange.end,
        );
        setPageData((current) => ({ ...current, [page]: data }));
        const datasetErrors = Object.keys(data.datasetErrors ?? {});
        const rowCount = Object.values(data.datasets).reduce(
          (total, rows) => total + rows.length,
          0,
        );
        if (datasetErrors.length && rowCount === 0) {
          setDataMessage(
            "Zoho returned no usable rows because the selected source exports failed. Refresh or inspect the source diagnostics.",
          );
        } else if (datasetErrors.length) {
          setDataMessage(
            "Some source views could not be refreshed. Available sections remain current.",
          );
        } else if (rowCount === 0) {
          setDataMessage(
            `No Zoho rows are available from ${requestRange.start} to ${requestRange.end}. Select a populated date range.`,
          );
        }
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "The selected page could not be refreshed.";
        if (/session|sign in|unauthorized/i.test(message)) {
          clearPortalSessionToken();
          setAccessState("signed-out");
          setAccessMessage(
            "Your session has ended. Sign in with Zoho to continue.",
          );
        } else {
          setDataMessage(
            "The selected page could not be refreshed. Please try again.",
          );
        }
      } finally {
        setLoadingData(false);
      }
    },
    [accessState, requestRange.end, requestRange.start],
  );

  useEffect(() => {
    if (activePage !== "p1" && activePage !== "p2") return;
    if (accessState !== "authenticated") return;
    const timer = globalThis.setTimeout(() => {
      void loadPage(activePage);
    }, 0);
    return () => globalThis.clearTimeout(timer);
  }, [accessState, activePage, loadPage, refreshVersion]);

  const selectedPage =
    pageDefinitions.find((page) => page.id === activePage) ?? pageDefinitions[0];
  const currentData =
    activePage === "p1" || activePage === "p2"
      ? accessState === "local-preview"
        ? demoData?.pages[activePage]
        : pageData[activePage]?.datasets
      : undefined;
  const generatedAt =
    activePage === "p1" || activePage === "p2"
      ? accessState === "local-preview"
        ? demoData?.generatedAt
        : pageData[activePage]?.generatedAt
      : "";
  const sourceLabel =
    accessState === "local-preview"
      ? "Synthetic validation baseline"
      : "Live governed workspace data";

  const canShowPortal = ["local-preview", "authenticated"].includes(accessState);
  const pageStatus = useMemo(
    () => `${selectedPage.available ? "Available" : "Planned"} / Page ${pageDefinitions.findIndex((page) => page.id === activePage) + 1}`,
    [activePage, selectedPage.available],
  );
  const activeDashboardUrl = visualUrls.dashboards[activePage] ?? "";

  if (!canShowPortal) {
    return <AccessGate state={accessState} message={accessMessage} />;
  }

  const signOut = async () => {
    await revokePortalSession();
    setPageData({});
    setUserName("");
    setAccessState("signed-out");
    setAccessMessage(
      "Sign in with your approved Zoho Analytics account to continue.",
    );
  };

  return (
    <div
      className={`control-tower-portal${standalone ? " is-standalone" : ""}`}
    >
      <header className="ct-command-header">
        <div className="ct-brand-lockup">
          <span className="ct-brand-symbol">
            <Database aria-hidden="true" size={19} />
          </span>
          <span>
            <strong>ABNAH</strong>
            <small>SCM CONTROL TOWER</small>
          </span>
        </div>
        <div className="ct-page-heading">
          <span>{pageStatus}</span>
          <h1>{selectedPage.title}</h1>
          <p>{selectedPage.subtitle}</p>
        </div>
        <div className="ct-command-actions">
          <span className="ct-user-state">
            <ShieldCheck aria-hidden="true" size={14} />
            {userName}
          </span>
          {selectedPage.available ? (
            <button
              type="button"
              onClick={() => setRefreshVersion((current) => current + 1)}
              disabled={loadingData}
              title="Refresh page data"
            >
              <RefreshCw
                aria-hidden="true"
                className={loadingData ? "ct-spin" : ""}
                size={16}
              />
              Refresh
            </button>
          ) : null}
          <a href={atlasUrl()} target="_blank" rel="noreferrer">
            Data Atlas
            <ExternalLink aria-hidden="true" size={14} />
          </a>
          {activeDashboardUrl ? (
            <a
              href={activeDashboardUrl}
              target="_blank"
              rel="noreferrer"
              title="Open the governed Zoho dashboard"
            >
              Zoho dashboard
              <ExternalLink aria-hidden="true" size={14} />
            </a>
          ) : null}
          {accessState === "authenticated" ? (
            <button type="button" onClick={() => void signOut()} title="Sign out">
              <LogOut aria-hidden="true" size={16} />
              Sign out
            </button>
          ) : null}
        </div>
      </header>

      <div className="ct-runtime-strip">
        <span className={accessState === "local-preview" ? "is-preview" : ""}>
          {sourceLabel}
        </span>
        <span>
          Refreshed {generatedAt ? formatRefreshTime(generatedAt) : "on request"}
        </span>
        <span>Read-only operational view</span>
      </div>

      {dataMessage ? (
        <div className="ct-data-message" role="status">
          {dataMessage}
        </div>
      ) : null}

      <div className="ct-workspace-frame">
        <nav className="ct-page-navigation" aria-label="Control tower pages">
          {pageDefinitions.map((page, index) => {
            const Icon = page.icon;
            return (
              <button
                type="button"
                key={page.id}
                className={page.id === activePage ? "is-active" : ""}
                onClick={() => setActivePage(page.id)}
              >
                <span>
                  <Icon aria-hidden="true" size={16} />
                  <small>{String(index + 1).padStart(2, "0")}</small>
                </span>
                <strong>{page.shortLabel}</strong>
                <small>{page.available ? page.label : "Coming soon"}</small>
              </button>
            );
          })}
        </nav>

        <div className="ct-page-stage">
          {selectedPage.available ? (
            currentData ? (
              activePage === "p1" ? (
                <RiskActionPage
                  datasets={currentData}
                  sourceLabel={sourceLabel}
                  range={requestRange}
                  onRangeChange={setRequestRange}
                  visualUrls={visualUrls}
                />
              ) : (
                <ProcurementPage
                  datasets={currentData}
                  sourceLabel={sourceLabel}
                  range={requestRange}
                  onRangeChange={setRequestRange}
                  visualUrls={visualUrls}
                />
              )
            ) : (
              <div className="ct-loading-stage">
                <LoaderCircle aria-hidden="true" className="ct-spin" size={28} />
                <span>Loading control-tower data</span>
              </div>
            )
          ) : (
            <ComingSoon
              title={selectedPage.title}
              subtitle={selectedPage.subtitle}
            />
          )}
        </div>
      </div>
    </div>
  );
}
