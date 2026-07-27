import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the editable ABNAH schema workspace", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>ABNAH Schema Workspace<\/title>/i);
  assert.match(html, /Schema Workspace/);
  assert.match(html, /Discovery/);
  assert.match(html, /API validation/);
  assert.match(html, /Control tower/);
  assert.match(html, /Data quality/);
  assert.match(html, /Architecture/);
  assert.match(html, /Library/);
  assert.match(html, /Budget DSR Report/);
  assert.match(html, /Blank table structure/);
  assert.match(html, /318/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);
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
  assert.equal(projectPack.summary.files, 733);
  assert.equal(projectPack.summary.csvFiles, 349);
  assert.equal(projectPack.summary.sqlFiles, 132);
  assert.equal(projectPack.summary.guideFiles, 91);
  assert.equal(projectPack.categories.length, 10);
  assert.equal(new Set(projectPack.files.map((file) => file.path)).size, 733);
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
