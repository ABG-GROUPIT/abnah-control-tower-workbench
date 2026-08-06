import assert from "node:assert/strict";
import { access, readdir, readFile } from "node:fs/promises";
import test from "node:test";

async function pagesBundleText() {
  const assets = await readdir(
    new URL("../pages-dist/assets/", import.meta.url),
    { withFileTypes: true },
  );
  const scripts = await Promise.all(
    assets
      .filter((entry) => entry.isFile() && entry.name.endsWith(".js"))
      .map((entry) =>
        readFile(
          new URL(`../pages-dist/assets/${entry.name}`, import.meta.url),
          "utf8",
        ),
      ),
  );
  return scripts.join("\n");
}

test("builds the editable ABNAH workspace for GitHub Pages", async () => {
  const html = await readFile(
    new URL("../pages-dist/index.html", import.meta.url),
    "utf8",
  );
  const bundle = await pagesBundleText();
  assert.match(html, /<title>ABNAH Control Tower Workbench<\/title>/i);
  assert.match(html, /Content-Security-Policy/);
  assert.match(html, /frame-src https:\/\/analytics\.zoho\.in/);
  assert.doesNotMatch(html, /frame-src\s+\*/);
  assert.match(bundle, /Control Tower Workbench/);
  assert.match(bundle, /Discovery/);
  assert.match(bundle, /API validation/);
  assert.match(bundle, /Control tower/);
  assert.match(bundle, /Live portal/);
  assert.match(bundle, /Data quality/);
  assert.match(bundle, /Architecture/);
  assert.match(bundle, /From source reports to daily decisions/);
  assert.match(bundle, /10 Query Tables/);
  assert.match(bundle, /Period measures flow\. Snapshot measures state\./);
  assert.match(bundle, /RPT_V2_R08B_7_Day_Inventory_Shortage_Action_Table/);
  assert.match(bundle, /QT_02_Numerical_Risk_Center\.as_of_date/);
  assert.match(bundle, /See more details: build/);
  assert.match(bundle, /DB_02_ABNAH_SCM_Control_Tower_Final/);
  assert.match(bundle, /NEW_RPT_FC04R_PVT_Daily_Net_Sales_Forecast_7D/);
  assert.match(bundle, /AF_Flow_Theoretical_Gross_Margin_Pct/);
  assert.match(bundle, /Add > Aggregate Formula/);
  assert.match(bundle, /Library/);
  assert.match(bundle, /Budget DSR Report/);
  assert.match(bundle, /Blank table structure/);
  assert.doesNotMatch(
    bundle,
    /codex-preview|Your site is taking shape|react-loading-skeleton/i,
  );
});

test("publishes the exact ten-query SQL handover", async () => {
  const sqlDirectory = new URL("../pages-dist/architecture/sql/", import.meta.url);
  const sqlFiles = (await readdir(sqlDirectory, { withFileTypes: true }))
    .filter((entry) => entry.isFile() && entry.name.endsWith(".sql"));

  assert.equal(sqlFiles.length, 10);
  const numericalRisk = await readFile(
    new URL("02_numerical_risk_center.sql", sqlDirectory),
    "utf8",
  );
  assert.match(numericalRisk, /Query Table\s*:\s*QT_02_Numerical_Risk_Center/i);
});

test("publishes the secured delivery portal as a GitHub Pages route", async () => {
  const [rootHtml, portalHtml, bundle] = await Promise.all([
    readFile(new URL("../pages-dist/index.html", import.meta.url), "utf8"),
    readFile(new URL("../pages-dist/portal/index.html", import.meta.url), "utf8"),
    pagesBundleText(),
  ]);
  assert.equal(portalHtml, rootHtml);
  assert.match(bundle, /SCM CONTROL TOWER/);
  assert.match(bundle, /Risk Action Center/);
  assert.match(
    bundle,
    /Sign in with your approved Zoho Analytics account to continue/,
  );
  assert.match(bundle, /Portal access is being prepared/);
  assert.match(bundle, /Coming soon/);
  assert.doesNotMatch(bundle, /Continue after sign-in/);
  assert.match(bundle, /UNDERLYING EVIDENCE/);
  assert.match(bundle, /Zoho native visual/);
  assert.match(bundle, /ZOHO_CRITERIA/);
  assert.match(bundle, /Rendered from governed query-table data; open the source for Zoho detail\./);
  assert.match(bundle, /Matching validated March rows are shown temporarily/);
});

test("ships the secured data gateway and backward-compatible handoff contract", async () => {
  const [handoff, runtime, edgeFunction, dataGateway, migration, client] = await Promise.all([
    readFile(
      new URL(
        "../config/zoho-secured-embed-handoff.example.json",
        import.meta.url,
      ),
      "utf8",
    ),
    readFile(
      new URL("../config/supabase-portal.json", import.meta.url),
      "utf8",
    ),
    readFile(
      new URL(
        "../supabase/functions/abnah-portal/index.ts",
        import.meta.url,
      ),
      "utf8",
    ),
    readFile(
      new URL(
        "../supabase/functions/_shared/zoho-data.ts",
        import.meta.url,
      ),
      "utf8",
    ),
    readFile(
      new URL(
        "../supabase/migrations/20260727000100_abnah_portal.sql",
        import.meta.url,
      ),
      "utf8",
    ),
    readFile(
      new URL("../app/lib/supabase-portal-client.ts", import.meta.url),
      "utf8",
    ),
  ]).then(([handoffText, runtimeText, ...rest]) => [
    JSON.parse(handoffText),
    JSON.parse(runtimeText),
    ...rest,
  ]);
  assert.equal(handoff.schema, "abnah-zoho-view-handoff/v4");
  assert.equal(
    handoff.integrationMode,
    "individual_report_views_with_dashboard_fallbacks",
  );
  assert.equal(Object.keys(handoff.pages).length, 4);
  assert.equal(
    Object.values(handoff.pages).reduce(
      (total, page) => total + Object.keys(page.reports).length,
      0,
    ),
    19,
  );
  assert.match(
    runtime.returnUrl,
    /^https:\/\/abg-groupit\.github\.io\/abnah-control-tower-workbench\/portal\/$/,
  );
  assert.match(runtime.functionBaseUrl, /\.supabase\.co\/functions\/v1\/abnah-portal$/);
  assert.match(edgeFunction, /ZOHO_ALLOWED_WORKSPACE_ID/);
  assert.match(edgeFunction, /ZOHO_PORTAL_ADMIN_EMAILS/);
  assert.match(edgeFunction, /abnah_portal_sessions/);
  assert.match(edgeFunction, /fetchControlTowerPageData/);
  assert.match(dataGateway, /27_fact_ct_inventory_risk\.sql/);
  assert.match(dataGateway, /28_fact_ct_menu_impact\.sql/);
  assert.match(dataGateway, /38_fact_ct_expiry_risk\.sql/);
  assert.match(dataGateway, /22_fact_ct_purchase_order\.sql/);
  assert.match(dataGateway, /31_sum_ct_price_movement\.sql/);
  assert.match(dataGateway, /responseFormat: "json"/);
  assert.match(dataGateway, /for \(const spec of pageExports\[page\]\)/);
  assert.doesNotMatch(dataGateway, /Promise\.allSettled/);
  assert.match(migration, /enable row level security/);
  assert.match(migration, /revoke all .* from anon, authenticated/);
  assert.doesNotMatch(edgeFunction, /adminEmails\.size === 0/);
  assert.match(client, /sessionStorage/);
  assert.match(client, /`Bearer \$\{token\}`/);
  assert.doesNotMatch(client, /\/api\/zoho-auth|\/api\/zoho-portal-config/);
  await assert.rejects(
    access(new URL("../.openai/hosting.json", import.meta.url)),
    /ENOENT/,
  );
});

test("ships one validated URL and authentication handoff contract", async () => {
  const handoff = JSON.parse(
    await readFile(
      new URL(
        "../portal-handoff/ABNAH_PORTAL_HANDOFF_TEMPLATE.json",
        import.meta.url,
      ),
      "utf8",
    ),
  );
  const reports = Object.values(handoff.securedVisualUrls)
    .flatMap((page) => Object.values(page.reports));

  assert.equal(handoff.schema, "abnah-portal-handoff/v1");
  assert.equal(Object.keys(handoff.securedVisualUrls).length, 4);
  assert.equal(reports.length, 19);
  assert.deepEqual(
    handoff.publicConfiguration.zohoOAuthScopes,
    [
      "ZohoAnalytics.metadata.read",
      "ZohoAnalytics.data.read",
      "profile.userinfo.READ",
    ],
  );
  assert.ok(reports.every((report) => report.viewName && report.queryTable));
  assert.ok(reports.every((report) => report.securedViewUrl === ""));
  assert.equal(handoff.privateConfiguration.zohoOAuthClientSecret, "");
  assert.equal(handoff.privateConfiguration.zohoTokenEncryptionKey, "");
  assert.equal("supabaseProjectAnonKey" in handoff.publicConfiguration, false);
  assert.equal("supabaseServiceRoleKey" in handoff.privateConfiguration, false);
});

test("ships screenshot-free workspace and control-tower contracts", async () => {
  const [workspaceText, atlasText, controlTowerText, evidenceText, fidelityText, architectureText, presentationText, modelText, lineageText, projectPackText, migration, packageJson] = await Promise.all([
    readFile(new URL("../schema-pack/generated/workspace.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/atlas.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/control-tower-requirements.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/control-tower-evidence.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/control-tower-fidelity.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/control-tower-architecture.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/control-tower-presentation.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/control-tower-model.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/kpi-lineage.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/project-pack-index.json", import.meta.url), "utf8"),
    readFile(new URL("../drizzle/0000_faulty_leader.sql", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
  ]);
  const workspace = JSON.parse(workspaceText);
  const atlas = JSON.parse(atlasText);
  const controlTower = JSON.parse(controlTowerText);
  const evidence = JSON.parse(evidenceText);
  const fidelity = JSON.parse(fidelityText);
  const architecture = JSON.parse(architectureText);
  const presentation = JSON.parse(presentationText);
  const model = JSON.parse(modelText);
  const lineage = JSON.parse(lineageText);
  const projectPack = JSON.parse(projectPackText);
  const misc = workspace.reports.filter((report) => report.page === "p1_main" && report.section === "06_misc");

  assert.equal(workspace.contractVersion, "1.0.0");
  assert.equal(workspace.reports.length, atlas.summary.reports);
  assert.equal(misc.filter((report) => report.schemaStatus === "captured").length, 17);
  assert.equal(misc.filter((report) => report.schemaStatus === "unavailable" && !report.isArchived).length, 8);
  assert.equal(misc.filter((report) => report.isArchived).length, 2);
  assert.doesNotMatch(workspaceText, /\.png\b|AppData\\Local\\Temp|Downloads\\06_misc/i);
  assert.equal(controlTower.pages.length, 4);
  assert.equal(controlTower.kpis.length, 35);
  assert.equal(controlTower.terminology.preferredTerm, "consumption");
  assert.equal(architecture.status, "planned_architecture_under_feasibility_validation");
  assert.equal(architecture.sourceNodes.filter((node) => node.kind === "report").length, 20);
  assert.equal(architecture.sourceNodes.filter((node) => node.kind === "master").length, 1);
  assert.equal(architecture.sourceNodes.filter((node) => node.kind === "derived_reference").length, 2);
  assert.equal(architecture.modelNodes.length, 58);
  assert.equal(new Set(architecture.kpiRoutes.flatMap((route) => route.kpiIds)).size, 35);
  assert.equal(presentation.pages.length, 4);
  assert.equal(presentation.stories.length, 76);
  assert.equal(presentation.stories.filter((story) => story.kind === "kpi").length, 33);
  assert.equal(presentation.stories.filter((story) => story.kind === "chart").length, 23);
  assert.equal(presentation.stories.filter((story) => story.kind === "table").length, 20);
  assert.equal(model.layers.length, 5);
  assert.equal(model.tables.length, 38);
  assert.deepEqual(model.tables.map((table) => table.buildOrder), Array.from({ length: 38 }, (_, index) => index + 1));
  assert.ok(model.tables.every((table) => table.sql.includes("-- Query Table:")));
  assert.ok(architecture.sourceNodes.some(
    (node) => node.id === "src_purchase_order"
      && node.label === "Enterprise Purchase Order Report"
      && node.reportId === "report:p4_stock_admin:01_enterprise_reports:06_enterprise_purchase_order",
  ));
  assert.equal(evidence.summary.selectedSourceCount, 19);
  assert.equal(evidence.summary.auditedReportCount, 20);
  assert.equal(evidence.summary.auditedFileCount, 26);
  assert.equal(evidence.summary.schemaVisualMatches, 20);
  assert.equal(evidence.summary.headerOnlyReportCount, 2);
  assert.equal(evidence.summary.semanticFindingCount, 19);
  assert.equal(evidence.summary.criticalFindingCount, 11);
  assert.equal(evidence.summary.majorFindingCount, 7);
  assert.equal(evidence.summary.minorFindingCount, 1);
  assert.equal(evidence.summary.passedControlCount, 23);
  assert.equal(evidence.summary.failedControlCount, 0);
  assert.ok(evidence.businessReview.controls.some(
    (control) => control.id === "transfer_pair_reconciliation" && control.status === "passed",
  ));
  assert.ok(evidence.businessReview.controls.some(
    (control) => control.id === "po_entry_identifier_check" && control.status === "definition_gate",
  ));
  assert.equal(evidence.zohoReadiness.requiredLandingTableCount, 12);
  assert.equal(evidence.zohoReadiness.queryTableCount, 36);
  assert.equal(evidence.privacy.fullRowsIncluded, false);
  assert.equal(evidence.privacy.sensitiveValuesIncluded, false);
  assert.equal(fidelity.status, "verified");
  assert.equal(fidelity.reports.length, 21);
  assert.equal(fidelity.summary.exactHeaderReports, 21);
  assert.equal(fidelity.summary.currentUatAuditedReportContracts, 20);
  assert.equal(fidelity.summary.historicalSchemaContracts, 1);
  assert.equal(fidelity.summary.ignoredNoSignalFields, 69);
  assert.equal(fidelity.summary.headerOnlyReportContracts, 2);
  assert.equal(fidelity.summary.gatedReportContracts, 2);
  assert.equal(fidelity.summary.auxiliaryModelTables, 2);
  assert.ok(fidelity.reports.some((report) => (
    report.displayName === "Vendor Report"
    && report.evidenceScope === "historical_abnah_export"
    && report.rowPatternStatus === "historical_schema_with_structural_quality_gate"
  )));
  assert.ok(fidelity.reports.every((report) => report.headerMatch));
  assert.ok(fidelity.reports.every((report) => (
    report.ignoredFields.every((field) => field.observedState === field.syntheticState)
  )));
  assert.equal(lineage.status, "requirements_received");
  assert.equal(lineage.kpis.filter((kpi) => kpi.approvalStatus === "draft").length, 29);
  assert.equal(lineage.kpis.filter((kpi) => kpi.approvalStatus === "blocked").length, 4);
  assert.equal(lineage.kpis.filter((kpi) => kpi.approvalStatus === "provisional").length, 1);
  assert.equal(lineage.kpis.filter((kpi) => kpi.approvalStatus === "partial").length, 1);
  assert.equal(lineage.nodes.length, 0);
  assert.equal(lineage.edges.length, 0);
  assert.equal(projectPack.summary.files, 780);
  assert.equal(projectPack.summary.csvFiles, 349);
  assert.equal(projectPack.summary.sqlFiles, 133);
  assert.equal(projectPack.summary.guideFiles, 99);
  assert.equal(projectPack.categories.length, 10);
  assert.equal(new Set(projectPack.files.map((file) => file.path)).size, 780);
  assert.ok(projectPack.files.filter((file) => file.featuredOrder !== null).length >= 6);
  assert.ok(projectPack.files.every((file) => /^[a-f0-9]{64}$/.test(file.sha256)));
  assert.doesNotMatch(projectPackText, /\.png\b|\.jpe?g\b|AppData\\Local\\Temp|Downloads\\/i);
  assert.doesNotMatch(controlTowerText, /\.png\b|AppData\\Local\\Temp|Downloads\\/i);
  assert.doesNotMatch(evidenceText, /\.png\b|\.jpe?g\b|[A-Za-z]:\\|Downloads\\|file_sha256|file_name/i);
  assert.doesNotMatch(fidelityText, /\.png\b|\.jpe?g\b|[A-Za-z]:\\|Downloads\\/i);
  assert.doesNotMatch(architectureText, /\.png\b|\.jpe?g\b|AppData\\Local\\Temp|Downloads\\/i);
  assert.doesNotMatch(presentationText, /\.png\b|\.jpe?g\b|[A-Za-z]:\\|Downloads\\/i);
  assert.doesNotMatch(modelText, /\.png\b|\.jpe?g\b|[A-Za-z]:\\|Downloads\\/i);
  assert.doesNotMatch(atlasText, /Raw Material Item Detail/i);

  const budget = workspace.reports.find((report) => report.id === "report:p1_main:06_misc:03_budget_dsr_report");
  const cashier = workspace.reports.find((report) => report.id === "report:p1_main:06_misc:02_cashier_report");
  assert.equal(budget.layoutKind, "grouped_rows");
  assert.equal(budget.tables.length, 2);
  assert.ok(budget.tables.find((table) => table.id === "primary").rows >= 44);
  assert.equal(cashier.layoutKind, "grouped_columns");
  assert.ok(cashier.tables[0].cells.some((cell) => cell.columnSpan > 1));

  assert.match(migration, /CREATE TABLE `workspace_documents`/);
  assert.match(migration, /CREATE TABLE `workspace_revisions`/);
  assert.match(packageJson, /"data:workspace"/);
  assert.match(packageJson, /"build:pages"/);
  assert.match(packageJson, /package_github_pages\.py/);
  assert.match(packageJson, /validate_pages_artifact\.py/);
});
