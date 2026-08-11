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
  assert.match(bundle, /10-query governed lean foundation/);
  assert.match(bundle, /Period measures flow\. Snapshot measures state\./);
  assert.match(bundle, /RPT_V2_R08B_7_Day_Inventory_Shortage_Action_Table/);
  assert.match(bundle, /QT_02_Numerical_Risk_Center\.as_of_date/);
  assert.match(bundle, /See more details: build/);
  assert.match(bundle, /DB_02_ABNAH_SCM_Control_Tower_Final/);
  assert.match(bundle, /NEW_RPT_FC04R_PVT_Daily_Net_Sales_Forecast_7D/);
  assert.match(bundle, /AF_Flow_Theoretical_Gross_Margin_Pct/);
  assert.match(bundle, /Add > Aggregate Formula/);
  assert.match(bundle, /Ask Zia is governed by two acceptance gates/);
  assert.match(bundle, /ZIA_01_Strict_Overdue_PO/);
  assert.match(bundle, /ZIA_01A_Strict_Overdue_Vendor_Summary/);
  assert.match(bundle, /PRIVATE_CLIENT_BINDING/);
  assert.match(bundle, /LIVE_REMEDIATION_HELPER_CONVERSATIONALLY_BLOCKED/);
  assert.match(bundle, /56,175\.0572 \/ 10 POs \/ 29 days/);
  assert.match(bundle, /Business-readable SQL purpose/);
  assert.match(bundle, /ZLD009, corrected ZLD037 and the governed aggregate formula remain read back/);
  assert.match(bundle, /aggregate formula is verified/);
  assert.match(bundle, /standard descriptions remain uncertified/);
  assert.match(bundle, /Do not repeat the WF08 or WF04 smoke without a new causal semantic or presentation change/);
  assert.match(bundle, /7 PASS \/ 9 PARTIAL \/ 6 FAIL/);
  assert.match(bundle, /7 PASS \/ 9 PARTIAL \/ 50 FAIL/);
  assert.match(bundle, /67 ordered actions/);
  assert.match(bundle, /66 tests across 11 workflows/);
  assert.match(bundle, /SCOPED READBACK/);
  assert.doesNotMatch(bundle, /LOCAL PLAN ONLY|66 NOT_RUN/);
  assert.match(bundle, /expected_delivery_date = 27 Jan/);
  assert.match(bundle, /WF08 live field/);
  assert.match(bundle, /zero workflows are presentation-ready/i);
  assert.match(bundle, /RPT_V2_P08_Delivery_Breach_Action_Top10/);
  assert.doesNotMatch(bundle, /every conversational workflow NOT_RUN/);
  assert.match(bundle, /Weather sits beside the unchanged operational core/);
  assert.match(bundle, /RPT_WX04_Menu_Demand_Weather_Matrix_DEMO/);
  assert.match(bundle, /QT_09_Latest_Weather_Outlook\.forecast_as_of_date/);
  assert.match(bundle, /DataBridge Update\/Add/);
  assert.match(bundle, /Portable knowledge, guarded execution/);
  assert.match(bundle, /public website and repository project pack contain no private discovery images/);
  assert.match(bundle, /historical private audit reviewed 182 images/i);
  assert.match(bundle, /retains 95 strict schema-only images/);
  assert.match(bundle, /excludes 87 value-bearing images/);
  assert.match(bundle, /cover 64 of 94 historically evidenced report groups/);
  assert.match(bundle, /leaving 30 image-pending/);
  assert.match(bundle, /27 have separately verified text schemas covering 530 fields/);
  assert.match(bundle, /3 remain text-pending/);
  assert.match(bundle, /Text-schema cards never count as screenshots/);
  assert.match(bundle, /schema-captured/);
  assert.match(bundle, /20 selected report schemas/);
  assert.match(bundle, /17 structurally captured, 1 partial and 2 pending/);
  assert.match(bundle, /Open green Discovery/);
  assert.match(bundle, /Inject at runtime; never package/);
  assert.match(bundle, /TEST before promotion/);
  assert.match(bundle, /Library/);
  assert.match(bundle, /Budget DSR Report/);
  assert.match(bundle, /Blank table structure/);
  assert.doesNotMatch(
    bundle,
    /codex-preview|Your site is taking shape|react-loading-skeleton/i,
  );
});

test("keeps architecture extension counts and Zia contracts explicit", async () => {
  const [component, extensionData, leanData, filterGuides, prChecks] = await Promise.all([
    readFile(new URL("../app/components/ArchitectureGraphWorkspace.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/lib/architecture-extension-data.ts", import.meta.url), "utf8"),
    readFile(new URL("../app/lib/lean-architecture-data.ts", import.meta.url), "utf8"),
    readFile(new URL("../app/lib/zoho-build-guides.ts", import.meta.url), "utf8"),
    readFile(new URL("../.github/workflows/pr-checks.yml", import.meta.url), "utf8"),
  ]);

  assert.match(component, /<b>10<\/b><small>extension queries<\/small>/);
  assert.match(leanData, /governedLeanFoundationQueryTables:\s*10/);
  assert.match(leanData, /broaderHistoricalLiveModelTables:\s*38/);
  assert.match(extensionData, /actionCount:\s*67/);
  assert.match(extensionData, /BASE_67_READ_BACK_FIVE_CAUSAL_HELPERS_DEPLOYED_WAT08_RETRY_NO_IMPROVEMENT_REMAINING_TARGETED_WAT_PENDING_GATE_UNCHANGED/);
  assert.match(extensionData, /ZIA_QT_06_Provisional_Expiry_Only/);
  assert.match(extensionData, /ZIA_QT_07_Current_Red_Inventory/);
  assert.match(extensionData, /ZIA_QT_08_Positive_Open_Vendor_Material/);
  assert.match(extensionData, /ZIA_QT_09_PO_Delivery_UOM_Safe/);
  assert.match(extensionData, /ZIA_QT_10_PO_Delivery_Value_By_PO/);
  assert.match(extensionData, /ordered_quantity as non-additive text beside source_uom/);
  assert.match(extensionData, /replacement QT09 ordered_quantity, source_uom and ordered_value_pre_tax readback passed 3\/3/);
  assert.match(extensionData, /indexed WAT08 retry still selected the raw PO source and generated unsafe cross-UOM output/);
  assert.match(extensionData, /Do not repeat the WF08 or WF04 smoke without a new causal semantic or presentation change/i);
  assert.match(extensionData, /testCount:\s*22/);
  assert.match(extensionData, /testCount:\s*66/);
  assert.match(extensionData, /currentLedger:\s*"7 PASS \/ 9 PARTIAL \/ 6 FAIL"/);
  assert.match(extensionData, /currentLedger:\s*"7 PASS \/ 9 PARTIAL \/ 50 FAIL"/);
  assert.match(extensionData, /presentationReadyWorkflowCount:\s*0/);
  assert.equal((extensionData.match(/presentationStatus:\s*"BLOCKED/g) ?? []).length, 11);
  assert.doesNotMatch(extensionData, /presentationStatus:\s*"SAFE/);
  assert.match(extensionData, /dateContract:\s*"expected_delivery_date = 27 Jan/);
  assert.doesNotMatch(extensionData, /dateContract:\s*"Expected Delivery Date = 27 Jan/);
  assert.match(filterGuides, /"Menu Item":\s*\{[\s\S]*?tabs:\s*"01 Executive Control · 03 Sales & Menu Economics"/);
  assert.match(filterGuides, /"Menu Category":\s*\{[\s\S]*?tabs:\s*"01 Executive Control · 03 Sales & Menu Economics"/);
  assert.match(filterGuides, /procurement:\s*\{[\s\S]*?Row 1 · Reporting Period · Snapshot As Of · Outlet"/);
  assert.doesNotMatch(filterGuides, /procurement:\s*\{[\s\S]*?Row 1 · Reporting Period · Snapshot As Of · Outlet · Menu Item · Menu Category/);
  assert.match(prChecks, /pull_request:/);
  assert.match(prChecks, /contents:\s*read/);
  assert.match(prChecks, /npm test/);
  assert.doesNotMatch(prChecks, /pages:\s*write|deploy-pages|workflow_dispatch/);
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
  assert.equal(
    workspace.schema_status_semantics,
    "Structural transcription state; not current strict schema-only image coverage.",
  );
  assert.equal(workspace.reports.length, atlas.summary.reports);
  assert.equal(atlas.summary.historical_p1_ocr_index_items, 161);
  assert.equal("evidence_items" in atlas.summary, false);
  const discoveryBoundary = atlas.discovery_evidence_boundary;
  assert.equal(discoveryBoundary.catalog_reports, 318);
  assert.equal(discoveryBoundary.historical_image_audit_universe, 182);
  assert.equal(discoveryBoundary.strict_schema_only_images_retained, 95);
  assert.equal(discoveryBoundary.operational_value_images_excluded, 87);
  assert.equal(discoveryBoundary.schema_only_image_report_groups_covered, 64);
  assert.equal(discoveryBoundary.report_groups_pending_schema_only_image, 30);
  assert.equal(discoveryBoundary.pending_image_groups_with_verified_text_schema, 27);
  assert.equal(discoveryBoundary.pending_image_groups_still_text_pending, 3);
  assert.equal(discoveryBoundary.verified_text_schema_fields, 530);
  assert.equal(discoveryBoundary.text_cards_count_as_screenshots, false);
  assert.equal(discoveryBoundary.public_website_screenshot_assets, 0);
  assert.equal(
    discoveryBoundary.schema_only_image_report_groups_covered
      + discoveryBoundary.report_groups_pending_schema_only_image,
    discoveryBoundary.historically_evidenced_report_groups,
  );
  assert.equal(
    discoveryBoundary.strict_schema_only_images_retained
      + discoveryBoundary.operational_value_images_excluded,
    discoveryBoundary.historical_image_audit_universe,
  );
  assert.equal(
    discoveryBoundary.pending_image_groups_with_verified_text_schema
      + discoveryBoundary.pending_image_groups_still_text_pending,
    discoveryBoundary.report_groups_pending_schema_only_image,
  );
  assert.match(discoveryBoundary.release_gate, /^BLOCKED_/);
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
  assert.equal(presentation.stories.filter((story) => story.kind === "chart").length, 22);
  assert.equal(presentation.stories.filter((story) => story.kind === "table").length, 21);
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
  assert.equal(projectPack.summary.files, 781);
  assert.equal(projectPack.summary.csvFiles, 349);
  assert.equal(projectPack.summary.sqlFiles, 133);
  assert.equal(projectPack.summary.guideFiles, 99);
  assert.equal(projectPack.categories.length, 10);
  assert.equal(new Set(projectPack.files.map((file) => file.path)).size, 781);
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
