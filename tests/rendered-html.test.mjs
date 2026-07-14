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
  assert.match(html, /KPI lineage/);
  assert.match(html, /Budget DSR Report/);
  assert.match(html, /Blank table structure/);
  assert.match(html, /319/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/i);
});

test("ships a screenshot-free structural workspace contract", async () => {
  const [workspaceText, atlasText, migration, packageJson] = await Promise.all([
    readFile(new URL("../schema-pack/generated/workspace.json", import.meta.url), "utf8"),
    readFile(new URL("../schema-pack/generated/atlas.json", import.meta.url), "utf8"),
    readFile(new URL("../drizzle/0000_faulty_leader.sql", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
  ]);
  const workspace = JSON.parse(workspaceText);
  const atlas = JSON.parse(atlasText);
  const misc = workspace.reports.filter((report) => report.page === "p1_main" && report.section === "06_misc");

  assert.equal(workspace.contractVersion, "1.0.0");
  assert.equal(workspace.reports.length, atlas.summary.reports);
  assert.equal(misc.filter((report) => report.schemaStatus === "captured").length, 17);
  assert.equal(misc.filter((report) => report.schemaStatus === "unavailable" && !report.isArchived).length, 8);
  assert.equal(misc.filter((report) => report.isArchived).length, 2);
  assert.doesNotMatch(workspaceText, /\.png\b|AppData\\Local\\Temp|Downloads\\06_misc/i);

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
});
