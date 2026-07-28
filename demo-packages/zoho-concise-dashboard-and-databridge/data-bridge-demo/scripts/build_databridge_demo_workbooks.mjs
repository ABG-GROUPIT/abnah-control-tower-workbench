import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputRoot = process.argv[2]
  ? path.resolve(process.argv[2])
  : path.resolve(
      "demo-packages",
      "zoho-concise-dashboard-and-databridge",
      "data-bridge-demo",
    );

const qaRoot = path.join(
  os.tmpdir(),
  `abnah-databridge-qa-${process.pid}`,
);

const deployment = "ABNAH Cafe Connaught Place";
const store = "GK2 Main Store";
const sourceLabel = "Synthetic DataBridge Demo";

const entryHeaders = [
  "Deployment Name",
  "Store/Kitchen Name",
  "User Name",
  "Vendor Name",
  "Date",
  "Transaction Number",
  "Invoice Number",
  "Batch Number",
  "PR Number",
  "PO Number",
  "Invoice Date",
  "Item Code",
  "Item Name",
  "Item Brand",
  "Category Name",
  "Super Category Name",
  "Comment",
  "Quantity",
  "Unit",
  "MRP",
  "Unit Price",
  "Charges Name",
  "Amount",
  "Discount",
  "GST/IGST Rate",
  "GST/IGST Value",
  "CESS Rate",
  "CESS Value",
  "Other Taxes Rate",
  "Other Taxes Value",
  "Total Tax",
  "Item Charges Amount",
  "Total",
  "Source",
];

const closingHeaders = [
  "Deployment",
  "Date",
  "Generation Date",
  "Generation Time",
  "Item Code",
  "Item Name",
  "Super Category Code",
  "Super Category Name",
  "Category Code",
  "Category Name",
  "Unit Name",
  "Average Price",
  "GK2 Main Store",
  "Total Qty",
  "Total Amt",
];

const dailySalesHeaders = [
  "Source Row ID",
  "Deployment",
  "Business Date",
  "Session",
  "Time Slot",
  "Sale Type",
  "Gross Amount",
  "Total Beverage Sale",
  "Total Food Sale",
  "Total Sale",
  "Total Discount",
  "Total Charge Amount",
  "Roundoff",
  "Total Gross",
  "Total Bills",
  "Total Covers",
  "Total APC",
];

const itemCatalog = {
  milk: {
    code: "RM001",
    name: "Whole Milk",
    brand: "FreshDairy",
    categoryCode: "DAIRY",
    category: "Dairy",
    unit: "LTR",
    vendor: "FreshDairy India Pvt Ltd",
    gstRate: 5,
  },
  coffee: {
    code: "RM002",
    name: "Arabica Coffee Beans",
    brand: "BluePeak",
    categoryCode: "BEV-IN",
    category: "Beverage Inputs",
    unit: "KG",
    vendor: "BluePeak Coffee Traders",
    gstRate: 5,
  },
  sugar: {
    code: "RM003",
    name: "Refined Sugar",
    brand: "Madhur",
    categoryCode: "GROC",
    category: "Grocery",
    unit: "KG",
    vendor: "Madhur Sugar Distributors",
    gstRate: 5,
  },
  cake: {
    code: "RM004",
    name: "Vanilla Cake Base",
    brand: "Bakers Choice",
    categoryCode: "BAKE",
    category: "Bakery Inputs",
    unit: "KG",
    vendor: "Bakers Choice Foods",
    gstRate: 18,
  },
  cups: {
    code: "RM005",
    name: "12 oz Paper Cup",
    brand: "EcoServe",
    categoryCode: "PACK",
    category: "Packaging",
    unit: "PCS",
    vendor: "EcoServe Packaging",
    gstRate: 18,
  },
};

function dateUtc(year, month, day) {
  return new Date(Date.UTC(year, month - 1, day));
}

function addDays(date, days) {
  return new Date(date.getTime() + days * 86400000);
}

function entryRow(weekNumber, sequence, date, itemKey, quantity, unitPrice) {
  const item = itemCatalog[itemKey];
  const suffix = `${String(weekNumber).padStart(2, "0")}${String(sequence).padStart(2, "0")}`;
  return [
    deployment,
    store,
    "demo.operator",
    item.vendor,
    date,
    `GRN-W${suffix}`,
    `INV-W${suffix}`,
    `BATCH-W${suffix}`,
    `PR-W${suffix}`,
    `PO-W${suffix}`,
    date,
    item.code,
    item.name,
    item.brand,
    item.category,
    "InGoodCo",
    `Synthetic week ${weekNumber} receipt`,
    quantity,
    item.unit,
    Number((unitPrice * 1.1).toFixed(2)),
    unitPrice,
    "",
    null,
    0,
    item.gstRate,
    null,
    0,
    null,
    0,
    null,
    null,
    0,
    null,
    sourceLabel,
  ];
}

function closingRow(date, itemKey, averagePrice, storeQuantity) {
  const item = itemCatalog[itemKey];
  return [
    deployment,
    date,
    date,
    "23:59:00",
    item.code,
    item.name,
    "INGC",
    "InGoodCo",
    item.categoryCode,
    item.category,
    item.unit,
    averagePrice,
    storeQuantity,
    null,
    null,
  ];
}

function dailySalesRows(weekNumber, startDate, beverage, food, bills, covers) {
  return beverage.map((beverageValue, index) => {
    const businessDate = addDays(startDate, index);
    const discount = Math.round((beverageValue + food[index]) * 0.035);
    const charge = Math.round((beverageValue + food[index]) * 0.012);
    const roundoff = index % 2 === 0 ? -0.25 : 0.25;
    return [
      `DS-W${String(weekNumber).padStart(2, "0")}-${String(index + 1).padStart(2, "0")}`,
      deployment,
      businessDate,
      "All Day",
      "00:00-23:59",
      "Dine-in + Delivery",
      null,
      beverageValue,
      food[index],
      null,
      discount,
      charge,
      roundoff,
      null,
      bills[index],
      covers[index],
      null,
    ];
  });
}

const weeks = [
  {
    code: "week_01",
    start: dateUtc(2026, 7, 6),
    end: dateUtc(2026, 7, 12),
    entry: [
      entryRow(1, 1, dateUtc(2026, 7, 6), "milk", 60, 56),
      entryRow(1, 2, dateUtc(2026, 7, 7), "coffee", 25, 720),
      entryRow(1, 3, dateUtc(2026, 7, 8), "sugar", 40, 44),
      entryRow(1, 4, dateUtc(2026, 7, 9), "cake", 30, 180),
      entryRow(1, 5, dateUtc(2026, 7, 10), "cups", 600, 3.2),
      entryRow(1, 6, dateUtc(2026, 7, 11), "milk", 45, 57),
    ],
    closing: [
      closingRow(dateUtc(2026, 7, 12), "milk", 56.43, 28),
      closingRow(dateUtc(2026, 7, 12), "coffee", 720, 14),
      closingRow(dateUtc(2026, 7, 12), "sugar", 44, 35),
      closingRow(dateUtc(2026, 7, 12), "cake", 180, 12),
      closingRow(dateUtc(2026, 7, 12), "cups", 3.2, 380),
    ],
    dailySales: dailySalesRows(
      1,
      dateUtc(2026, 7, 6),
      [18500, 19200, 19800, 20500, 21800, 26400, 27900],
      [14800, 15100, 15400, 16000, 17100, 21500, 22900],
      [124, 128, 131, 136, 145, 176, 189],
      [161, 166, 170, 177, 188, 226, 242],
    ),
  },
  {
    code: "week_02",
    start: dateUtc(2026, 7, 13),
    end: dateUtc(2026, 7, 19),
    entry: [
      entryRow(2, 1, dateUtc(2026, 7, 13), "milk", 70, 58),
      entryRow(2, 2, dateUtc(2026, 7, 14), "coffee", 22, 760),
      entryRow(2, 3, dateUtc(2026, 7, 15), "sugar", 45, 45),
      entryRow(2, 4, dateUtc(2026, 7, 16), "cake", 24, 186),
      entryRow(2, 5, dateUtc(2026, 7, 17), "cups", 500, 3.25),
      entryRow(2, 6, dateUtc(2026, 7, 18), "milk", 50, 58),
    ],
    closing: [
      closingRow(dateUtc(2026, 7, 19), "milk", 57.5, 18),
      closingRow(dateUtc(2026, 7, 19), "coffee", 742.34, 8),
      closingRow(dateUtc(2026, 7, 19), "sugar", 44.56, 30),
      closingRow(dateUtc(2026, 7, 19), "cake", 182.67, 6),
      closingRow(dateUtc(2026, 7, 19), "cups", 3.23, 240),
    ],
    dailySales: dailySalesRows(
      2,
      dateUtc(2026, 7, 13),
      [20100, 20700, 21400, 22000, 23800, 28600, 30100],
      [15900, 16300, 16800, 17400, 18600, 22900, 24400],
      [131, 136, 140, 145, 156, 188, 201],
      [170, 176, 181, 188, 202, 242, 259],
    ),
  },
  {
    code: "week_03",
    start: dateUtc(2026, 7, 20),
    end: dateUtc(2026, 7, 26),
    entry: [
      entryRow(3, 1, dateUtc(2026, 7, 20), "milk", 85, 59),
      entryRow(3, 2, dateUtc(2026, 7, 21), "coffee", 30, 842),
      entryRow(3, 3, dateUtc(2026, 7, 22), "sugar", 40, 45),
      entryRow(3, 4, dateUtc(2026, 7, 23), "cake", 35, 188),
      entryRow(3, 5, dateUtc(2026, 7, 24), "cups", 700, 3.65),
      entryRow(3, 6, dateUtc(2026, 7, 25), "milk", 45, 59),
    ],
    closing: [
      closingRow(dateUtc(2026, 7, 26), "milk", 58.42, 35),
      closingRow(dateUtc(2026, 7, 26), "coffee", 801.48, 10),
      closingRow(dateUtc(2026, 7, 26), "sugar", 44.73, 24),
      closingRow(dateUtc(2026, 7, 26), "cake", 185.58, 9),
      closingRow(dateUtc(2026, 7, 26), "cups", 3.47, 190),
    ],
    dailySales: dailySalesRows(
      3,
      dateUtc(2026, 7, 20),
      [20800, 21600, 22300, 23100, 24700, 29700, 31600],
      [16500, 17100, 17600, 18300, 19400, 23800, 25500],
      [136, 141, 146, 151, 162, 196, 211],
      [176, 183, 189, 196, 210, 252, 272],
    ),
  },
];

function applyBaseStyle(sheet, lastColumn, lastRow) {
  const used = sheet.getRange(`A1:${lastColumn}${lastRow}`);
  used.format = {
    font: { name: "Aptos", size: 10, color: "#17212B" },
    borders: { preset: "all", style: "thin", color: "#D9E2E7" },
    verticalAlignment: "center",
  };

  const header = sheet.getRange(`A1:${lastColumn}1`);
  header.format = {
    fill: "#0F766E",
    font: { name: "Aptos", size: 10, bold: true, color: "#FFFFFF" },
    wrapText: true,
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "all", style: "thin", color: "#0B5F59" },
    rowHeight: 36,
  };

  if (lastRow > 1) {
    sheet.getRange(`A2:${lastColumn}${lastRow}`).format.rowHeight = 21;
  }
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
}

function setWidths(sheet, lastRow, widths) {
  for (const [column, width] of Object.entries(widths)) {
    sheet.getRange(`${column}1:${column}${lastRow}`).format.columnWidth = width;
  }
}

function addEntrySheet(workbook, rows, tableSuffix) {
  const sheet = workbook.worksheets.add("Enterprise Entry");
  const lastRow = rows.length + 1;
  sheet.getRange(`A1:AH${lastRow}`).values = [entryHeaders, ...rows];

  const formulas = rows.map((_, index) => {
    const row = index + 2;
    return {
      amount: [`=INT(R${row}*U${row}*100+0.5)/100`],
      gst: [`=INT(W${row}*Y${row}+0.5)/100`],
      cess: [`=INT(W${row}*AA${row}+0.5)/100`],
      other: [`=INT(W${row}*AC${row}+0.5)/100`],
      totalTax: [`=INT(SUM(Z${row},AB${row},AD${row})*100+0.5)/100`],
      total: [`=INT((W${row}-X${row}+AE${row}+AF${row})*100+0.5)/100`],
    };
  });

  sheet.getRange(`W2:W${lastRow}`).formulas = formulas.map((x) => x.amount);
  sheet.getRange(`Z2:Z${lastRow}`).formulas = formulas.map((x) => x.gst);
  sheet.getRange(`AB2:AB${lastRow}`).formulas = formulas.map((x) => x.cess);
  sheet.getRange(`AD2:AD${lastRow}`).formulas = formulas.map((x) => x.other);
  sheet.getRange(`AE2:AE${lastRow}`).formulas = formulas.map((x) => x.totalTax);
  sheet.getRange(`AG2:AG${lastRow}`).formulas = formulas.map((x) => x.total);

  applyBaseStyle(sheet, "AH", lastRow);
  setWidths(sheet, lastRow, {
    A: 24, B: 19, C: 15, D: 26, E: 12, F: 15, G: 15, H: 15,
    I: 14, J: 14, K: 12, L: 12, M: 24, N: 16, O: 18, P: 14,
    Q: 23, R: 11, S: 9, T: 12, U: 12, V: 14, W: 13, X: 11,
    Y: 12, Z: 13, AA: 10, AB: 12, AC: 14, AD: 14, AE: 12, AF: 14,
    AG: 14, AH: 23,
  });
  sheet.getRange(`E2:E${lastRow}`).format.numberFormat = "yyyy-mm-dd";
  sheet.getRange(`K2:K${lastRow}`).format.numberFormat = "yyyy-mm-dd";
  sheet.getRange(`R2:R${lastRow}`).format.numberFormat = "0.000";
  sheet.getRange(`T2:U${lastRow}`).format.numberFormat = "₹#,##0.00";
  sheet.getRange(`W2:X${lastRow}`).format.numberFormat = "₹#,##0.00";
  sheet.getRange(`Y2:Y${lastRow}`).format.numberFormat = "0.00";
  sheet.getRange(`Z2:Z${lastRow}`).format.numberFormat = "₹#,##0.00";
  sheet.getRange(`AA2:AA${lastRow}`).format.numberFormat = "0.00";
  sheet.getRange(`AB2:AB${lastRow}`).format.numberFormat = "₹#,##0.00";
  sheet.getRange(`AC2:AC${lastRow}`).format.numberFormat = "0.00";
  sheet.getRange(`AD2:AG${lastRow}`).format.numberFormat = "₹#,##0.00";
  sheet.tables.add(`A1:AH${lastRow}`, true, `Entry_${tableSuffix}`);
  sheet.getRange(`T2:U${lastRow}`).setNumberFormat("₹#,##0.00");
  sheet.getRange(`W2:X${lastRow}`).setNumberFormat("₹#,##0.00");
  sheet.getRange(`Y2:Y${lastRow}`).setNumberFormat("0.00");
  sheet.getRange(`Z2:Z${lastRow}`).setNumberFormat("₹#,##0.00");
  sheet.getRange(`AA2:AA${lastRow}`).setNumberFormat("0.00");
  sheet.getRange(`AB2:AB${lastRow}`).setNumberFormat("₹#,##0.00");
  sheet.getRange(`AC2:AC${lastRow}`).setNumberFormat("0.00");
  sheet.getRange(`AD2:AG${lastRow}`).setNumberFormat("₹#,##0.00");
}

function addClosingSheet(workbook, rows, tableSuffix) {
  const sheet = workbook.worksheets.add("Closing Stock");
  const lastRow = rows.length + 1;
  sheet.getRange(`A1:O${lastRow}`).values = [closingHeaders, ...rows];
  sheet.getRange(`N2:N${lastRow}`).formulas = rows.map((_, index) => [
    `=M${index + 2}`,
  ]);
  sheet.getRange(`O2:O${lastRow}`).formulas = rows.map((_, index) => [
    `=INT(L${index + 2}*N${index + 2}*100+0.5)/100`,
  ]);

  applyBaseStyle(sheet, "O", lastRow);
  setWidths(sheet, lastRow, {
    A: 24, B: 12, C: 14, D: 13, E: 12, F: 24, G: 14, H: 16,
    I: 14, J: 18, K: 11, L: 13, M: 15, N: 12, O: 14,
  });
  sheet.getRange(`B2:C${lastRow}`).format.numberFormat = "yyyy-mm-dd";
  sheet.getRange(`L2:L${lastRow}`).format.numberFormat = "₹#,##0.00";
  sheet.getRange(`M2:N${lastRow}`).format.numberFormat = "0.000";
  sheet.getRange(`O2:O${lastRow}`).format.numberFormat = "₹#,##0.00";
  sheet.tables.add(`A1:O${lastRow}`, true, `Closing_${tableSuffix}`);
  sheet.getRange(`L2:L${lastRow}`).setNumberFormat("₹#,##0.00");
  sheet.getRange(`M2:N${lastRow}`).setNumberFormat("0.000");
  sheet.getRange(`O2:O${lastRow}`).setNumberFormat("₹#,##0.00");
}

function addDailySalesSheet(workbook, rows, tableSuffix) {
  const sheet = workbook.worksheets.add("Daily Sales");
  const lastRow = rows.length + 1;
  sheet.getRange(`A1:Q${lastRow}`).values = [dailySalesHeaders, ...rows];
  sheet.getRange(`G2:G${lastRow}`).formulas = rows.map((_, index) => [
    `=H${index + 2}+I${index + 2}`,
  ]);
  sheet.getRange(`J2:J${lastRow}`).formulas = rows.map((_, index) => [
    `=H${index + 2}+I${index + 2}`,
  ]);
  sheet.getRange(`N2:N${lastRow}`).formulas = rows.map((_, index) => [
    `=J${index + 2}-K${index + 2}+L${index + 2}+M${index + 2}`,
  ]);
  sheet.getRange(`Q2:Q${lastRow}`).formulas = rows.map((_, index) => [
    `=IF(P${index + 2}=0,0,INT(N${index + 2}/P${index + 2}*100+0.5)/100)`,
  ]);

  applyBaseStyle(sheet, "Q", lastRow);
  setWidths(sheet, lastRow, {
    A: 17, B: 24, C: 13, D: 12, E: 16, F: 19, G: 14, H: 16,
    I: 14, J: 13, K: 14, L: 16, M: 11, N: 14, O: 11, P: 12, Q: 12,
  });
  sheet.getRange(`C2:C${lastRow}`).format.numberFormat = "yyyy-mm-dd";
  sheet.getRange(`G2:N${lastRow}`).format.numberFormat = "₹#,##0.00";
  sheet.getRange(`O2:P${lastRow}`).format.numberFormat = "0";
  sheet.getRange(`Q2:Q${lastRow}`).format.numberFormat = "₹#,##0.00";
  sheet.tables.add(`A1:Q${lastRow}`, true, `DailySales_${tableSuffix}`);
  sheet.getRange(`G2:N${lastRow}`).setNumberFormat("₹#,##0.00");
  sheet.getRange(`O2:P${lastRow}`).setNumberFormat("0");
  sheet.getRange(`Q2:Q${lastRow}`).setNumberFormat("₹#,##0.00");
}

async function buildWorkbook(spec) {
  const workbook = Workbook.create();
  addEntrySheet(workbook, spec.entry, spec.tableSuffix);
  addClosingSheet(workbook, spec.closing, spec.tableSuffix);
  addDailySalesSheet(workbook, spec.dailySales, spec.tableSuffix);

  const errorScan = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 300 },
    summary: `${spec.tableSuffix} formula error scan`,
  });
  if (
    errorScan.ndjson
    && errorScan.ndjson.trim()
    && !errorScan.ndjson.includes("matched 0 entries")
  ) {
    throw new Error(
      `Formula error found in ${spec.tableSuffix}: ${errorScan.ndjson}`,
    );
  }

  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await fs.mkdir(path.dirname(spec.outputPath), { recursive: true });
  await exported.save(spec.outputPath);

  const renderDir = path.join(qaRoot, spec.tableSuffix);
  await fs.mkdir(renderDir, { recursive: true });
  for (const sheetName of ["Enterprise Entry", "Closing Stock", "Daily Sales"]) {
    const preview = await workbook.render({
      sheetName,
      autoCrop: "all",
      scale: 0.75,
      format: "png",
    });
    const safeName = sheetName.toLowerCase().replaceAll(" ", "-");
    await fs.writeFile(
      path.join(renderDir, `${safeName}.png`),
      new Uint8Array(await preview.arrayBuffer()),
    );
  }

  return workbook;
}

function cumulativeThrough(index) {
  return {
    entry: weeks.slice(0, index + 1).flatMap((week) => week.entry),
    closing: weeks.slice(0, index + 1).flatMap((week) => week.closing),
    dailySales: weeks.slice(0, index + 1).flatMap((week) => week.dailySales),
  };
}

await fs.mkdir(qaRoot, { recursive: true });

const buildSpecs = [];
for (let index = 0; index < weeks.length; index += 1) {
  const week = weeks[index];
  buildSpecs.push({
    ...week,
    tableSuffix: `Delta_W${index + 1}`,
    outputPath: path.join(
      outputRoot,
      "weekly-deltas",
      week.code,
      "ABNAH_DataBridge_Weekly_Delta.xlsx",
    ),
  });

  const cumulative = cumulativeThrough(index);
  const folder = [
    "step_01_week_01",
    "step_02_weeks_01_02",
    "step_03_weeks_01_03",
  ][index];
  buildSpecs.push({
    ...cumulative,
    tableSuffix: `Current_W1_W${index + 1}`,
    outputPath: path.join(
      outputRoot,
      "cumulative-refresh",
      folder,
      "ABNAH_DataBridge_Current.xlsx",
    ),
  });
}

buildSpecs.push({
  ...cumulativeThrough(0),
  tableSuffix: "Live_Drop",
  outputPath: path.join(
    outputRoot,
    "live-drop",
    "ABNAH_DataBridge_Current.xlsx",
  ),
});

let finalOutputPath;
for (const spec of buildSpecs) {
  await buildWorkbook(spec);
  if (spec.tableSuffix === "Current_W1_W3") {
    finalOutputPath = spec.outputPath;
  }
}

const finalBlob = await FileBlob.load(finalOutputPath);
const reopenedWorkbook = await SpreadsheetFile.importXlsx(finalBlob);
const reopenedErrorScan = await reopenedWorkbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "Reopened three-week workbook formula error scan",
});
if (
  reopenedErrorScan.ndjson
  && reopenedErrorScan.ndjson.trim()
  && !reopenedErrorScan.ndjson.includes("matched 0 entries")
) {
  throw new Error(
    `Formula error found after XLSX re-open: ${reopenedErrorScan.ndjson}`,
  );
}

const finalInspection = await reopenedWorkbook.inspect({
  kind: "workbook,sheet,table,region",
  range: "A1:Q5",
  tableMaxRows: 5,
  tableMaxCols: 17,
  maxChars: 8000,
  summary: "Three-week cumulative workbook verification",
});

const formulaChecks = [];
for (const [sheetId, range] of [
  ["Enterprise Entry", "W2:AG4"],
  ["Closing Stock", "N2:O4"],
  ["Daily Sales", "G2:Q4"],
]) {
  const result = await reopenedWorkbook.inspect({
    kind: "formula",
    sheetId,
    range,
    maxChars: 3000,
    options: { maxResults: 40 },
    summary: `${sheetId} exported formula verification`,
  });
  if (!result.ndjson || !result.ndjson.includes('"formula"')) {
    throw new Error(`Exported formulas were not found in ${sheetId} ${range}.`);
  }
  formulaChecks.push(result.ndjson);
}

for (const spec of buildSpecs) {
  await fs.rm(`${spec.outputPath}.inspect.ndjson`, { force: true });
}

console.log(
  JSON.stringify(
    {
      outputRoot,
      qaRoot,
      workbooksCreated: buildSpecs.length,
      expectedCumulativeRowCounts: {
        enterpriseEntry: 18,
        closingStock: 15,
        dailySales: 21,
      },
      exportedFormulaChecks: formulaChecks.length,
      finalInspection: finalInspection.ndjson,
    },
    null,
    2,
  ),
);
