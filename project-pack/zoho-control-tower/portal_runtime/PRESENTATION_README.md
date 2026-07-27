# ABNAH Supply Chain Control Tower - Presentation Runbook

## Presentation Position

This is a governed feasibility demonstrator, not a claim that the current
synthetic values are ABNAH production facts.

The demonstration proves that:

1. Restroworks/POSist report schemas can be catalogued and traced.
2. Selected reports can pass through a controlled layered model in Zoho
   Analytics.
3. Each P1/P2 KPI can be traced to exact Query Tables and source fields.
4. Zoho can remain the analytical engine while a separate presentation layer
   provides the ABNAH-requested executive experience.
5. Production replacement is feasible once freshness, cost coverage, expiry
   evidence, outlet geography, and API/CSV ingestion are approved.

## 90-Second Opening

> We began with data discovery rather than dashboard design. We captured the
> available POSIST report catalogue, extracted each report's fields and table
> structure, and created a searchable Atlas so the work can be handed to
> another developer without repeating discovery. We then selected the minimum
> report set needed for ABNAH's four-page Control Tower and audited 26 local
> exports covering 35,128 rows. The files were structurally parseable, but we
> found specific freshness, valuation, cost-coverage, and lineage limitations
> that make them unsafe for a polished multi-outlet production demonstration.
> We therefore built a controlled three-outlet synthetic baseline on the exact
> modeled schema, implemented 38 layered Zoho Query Tables, and validated P1
> Risk Action Center and P2 Procurement, Vendor and Capital Control. The custom
> portal reads the approved Zoho Query Tables through a secured API gateway,
> applies the selected filters, and lets the user drill back to the exact Zoho
> report and Query Table.

## Demo Sequence

1. Open the hosted Data Atlas.
2. Show **Discovery**: report catalogue, captured fields, and editable table
   structures.
3. Show **Data quality**: aggregate findings and privacy boundary.
4. Show **Architecture**: select one KPI and explain the five-stage route:
   original evidence, relationships, calculation, Zoho output, custom delivery.
5. Open the separate **Live portal**.
6. On P1, set `01 Mar 2026` to `31 Mar 2026`; show the action queue, real map,
   stockout impact, expiry exposure, and underlying evidence.
7. Select `OUT001` and then `Dairy` to prove filters recalculate the page.
8. On P2, show purchase value, open and delayed PO exposure, OTIF, price watch,
   vendor scorecard, price trend, and line-level evidence.
9. Open a KPI and use **Open Zoho report** or **Open Query Table** to prove
   lineage.
10. Show only a short glimpse of the original Zoho dashboards as the analytical
    build layer, not the final executive interface.

## Current Delivery Status

| Component | Status |
| --- | --- |
| Report/schema discovery | Complete for the captured scope |
| Transferable Atlas and project library | Hosted |
| Local CSV structural and semantic audit | Complete for 26 exports |
| Layered Zoho model | 38 Query Tables created |
| P1 custom portal | Live |
| P2 custom portal | Live |
| P3/P4 custom portal | Modelled; visual delivery not yet built |
| Zoho OAuth verification | Live through Supabase |
| Exact Zoho report/Query Table drill-through | Implemented |
| Interactive geographic map | Implemented with OpenStreetMap |
| Restroworks UAT API validation | Pending ABNAH/UAT credentials |

## What The Portal Reads

The custom P1/P2 values are not scraped from dashboard pixels and are not
manually copied from public links. The browser requests a selected date range
from the Supabase Edge Function. The function verifies the user's Zoho account
and approved workspace, creates temporary Zoho bulk-export jobs for the exact
Query Tables, normalizes the response, and returns rows to the browser. It does
not persist operational rows.

### P1 Query Tables

| Purpose | Exact Query Table |
| --- | --- |
| Stock position, shortage, severity, action evidence | `27_fact_ct_inventory_risk.sql` |
| Menu items and sales exposure affected by ingredients | `28_fact_ct_menu_impact.sql` |
| Estimated expiry/batch risk demonstrator | `38_fact_ct_expiry_risk.sql` |
| Open PO lines that mitigate an active risk | `36_fact_ct_risky_po.sql` |

### P2 Query Tables

| Purpose | Exact Query Table |
| --- | --- |
| Purchase, open PO and delayed PO values | `22_fact_ct_purchase_order.sql` |
| PO receipt comparison and vendor OTIF | `24_fact_ct_po_receipt_line.sql` |
| Receipt quantity/value and weighted unit-price trend | `23_fact_ct_purchase_receipt.sql` |
| Current versus previous comparable receipt price | `31_sum_ct_price_movement.sql` |

## Validated March Baseline

The command `npm run portal:validate-kpis` recomputes these values directly from
the governed validation dataset. It is also executed during the production
build and fails deployment if the baseline drifts.

### P1 Risk Action Center

| Scope | Risk outlets | Menu items | Stockout sales at risk | Estimated expiry exposure | Priority actions |
| --- | ---: | ---: | ---: | ---: | ---: |
| All outlets | 3 | 110 | INR 411,695.50 | INR 271,399.12 | 6 |
| OUT001 | 1 | 109 | INR 155,161.00 | INR 103,856.36 | 2 |
| OUT002 | 1 | 62 | INR 102,670.47 | INR 91,224.21 | 2 |
| OUT003 | 1 | 75 | INR 153,864.03 | INR 76,318.55 | 2 |
| Dairy | 3 | 62 | INR 122,946.30 | INR 85,934.71 | 2 |
| Bakery | 3 | 0 | INR 0.00 | INR 42,003.08 | 0 |

The all-outlet chart populations are 6 stockout lines, 302 menu-impact rows,
68 expiry-risk rows, and 0 vendor/PO mitigation rows.

### P2 Procurement, Vendor And Capital Control

| Scope | Purchase value | Open PO exposure | Delayed PO value | OTIF | Price-watch items |
| --- | ---: | ---: | ---: | ---: | ---: |
| All outlets | INR 1,565,981.32 | INR 177,145.39 | INR 156,529.83 | 53.70% | 42 |
| OUT001 | INR 562,587.30 | INR 62,631.64 | INR 53,739.41 | 61.67% | 34 |
| OUT002 | INR 505,212.20 | INR 50,677.13 | INR 43,694.22 | 51.92% | 33 |
| OUT003 | INR 498,181.82 | INR 63,836.62 | INR 59,096.20 | 46.00% | 36 |
| Dairy | INR 416,754.79 | INR 41,523.15 | INR 34,691.54 | 36.67% | 5 |
| BeanCraft Roasters Delhi | INR 54,269.90 | INR 1,464.83 | INR 1,464.83 | 66.67% | 1 |

The all-outlet chart populations are 215 PO lines, 215 PO-receipt comparison
lines, 220 receipt rows, and 103 price-movement rows.

## KPI And Chart Logic

### P1

| Display | Logic |
| --- | --- |
| Risk outlets | Distinct outlets with non-green stock risk, expiry risk, or matched risky PO evidence at the selected snapshot |
| Menu items at risk | Distinct menu items in Query 28 linked to ingredients in the selected risk snapshot |
| Stockout sales at risk | Sum of `allocated_forecast_net_sales_at_risk` |
| Estimated expiry exposure | Sum of `expiry_risk_value`; demonstrator only because native batch/expiry evidence is unavailable |
| Priority action queue | Distinct non-green inventory risk records, ordered by governed severity and value |
| Outlet risk map | Outlet coordinates plus highest severity, risk-record count, and total exposure |
| Vendor/PO mitigation | Query 36 intersection of open PO and non-green risk by period, outlet, and item |

### P2

| Display | Logic |
| --- | --- |
| Purchase value | Sum of ordered gross line value |
| Open PO exposure | Sum of unreceived `open_po_value` |
| Delayed PO value | Sum of `open_po_value` only where `delayed_po_flag` is true |
| Vendor OTIF | Successful eligible closed lines divided by eligible closed lines |
| Price watch | Distinct items with a price observation; no-baseline rows stay visible but are not labelled as percentage movement |
| Procurement funnel | Ordered, processed, open, and delayed values from Query 22 |
| Vendor scorecard | Purchase, fill, eligible-line OTIF, delay, and lead-time evidence from Query 24 |
| Price trend | Receipt-value-weighted unit price by receipt date, item, and canonical UOM from Query 23 |

## Why Vendor/PO Mitigation Is Empty

Do not create a replacement table for the current presentation.

`36_fact_ct_risky_po.sql` is intentionally stricter than a list of all open
POs. A row appears only when an open PO line matches a non-green inventory risk
at the same period, outlet, and item. The validated March all-outlet result is
zero. That means there is no proven matching mitigation in the modeled
baseline; it does not mean Query 22 has no open POs.

If ABNAH later wants suggested but unconfirmed mitigation, create a separate
candidate-action table and label it as a recommendation. Do not relabel every
open PO as risk mitigation.

## Three Presentation-Safe Source Findings

### Critical: stale stock snapshot

- Report: `Closing Stock Report`
- Exact example: source CSV row 2
- Stock date: 16 June 2026
- Generation date: 22 July 2026
- Lag: 36 days across all 1,148 captured rows

Say:

> The export can be a valid historical checkpoint, but it cannot safely support
> a current stockout action queue generated on 22 July.

### Critical: June cost-coverage discontinuity

- Report: `Gross/Net Margin Report`
- Exact example: source CSV row 15, item `IGC0052`
- Net sale value: INR 235.00
- Purchase rate/value: INR 0.00 / INR 0.00
- June result: 2,843 of 5,995 non-zero-sales rows, or 47.4%, have zero purchase
  value

Say:

> Zero is ambiguous unless it is backed by an approved no-cost classification.
> We therefore block source-margin publication rather than interpreting those
> lines as free inventory.

### Major: opening quantity without valuation

- Report: `Enterprise Opening Report - Opening Stock`
- Exact example: source CSV row 2, item `7742`
- Opening quantity: 1
- Unit price and subtotal: 0
- All three captured rows have zero valuation

Say:

> The rows can support a quantity bridge, but not opening stock value until an
> approved valuation method is supplied.

### Engineering controls, not source defects

- PO identifiers appear as `PO-11` in Enterprise Entry row 2 and `11` in
  Enterprise Purchase Order row 69. The standardization layer creates a
  canonical join key while preserving both raw values.
- Ingredient `7900` appears as `GRAM` in Item Recipe row 3 and `PKT (500 GM)`
  in Closing Stock row 151. Quantity comparison requires an approved
  conversion.

Do not present every negative number, repeated row, GST component, or rounding
residual as a confirmed source error. The corrected deterministic audit found
zero formula-exception rows.

## Data Journey And Layered Model

1. **Raw**: preserve the report export as supplied and add only provenance.
2. **Standardized**: normalize dates, identifiers, text, numeric types, signs,
   and UOM labels without changing business meaning.
3. **Dimensions**: create governed item, menu item, vendor, outlet, date, and
   UOM references.
4. **Facts**: establish declared grains for sales, inventory movements,
   consumption, purchase orders, receipts, risk, and menu impact.
5. **Summaries**: aggregate only after the fact grain is stable.
6. **Zoho outputs**: build governed analytical reports and dashboard views.
7. **Custom delivery**: use Zoho as the analytical source while the secured
   portal applies executive interaction and ABNAH visual hierarchy.

This prevents the dashboard from joining report totals, repeated headers, and
mixed-grain rows directly.

## Synthetic Demonstrator Boundary

The validation dataset represents three Delhi outlets over three months. It
retains the modeled POSIST-compatible columns and creates a coherent operating
story so cross-table calculations can be tested.

The following are modelled, not directly observed production facts:

- outlet coordinates where a production outlet master is unavailable;
- expiry/batch estimates where ABNAH has not enabled a source expiry report;
- recommended action wording and ownership;
- synthetic receipt and PO lineage needed to test a complete lifecycle.

Production options for recommendations are:

1. deterministic, approved business rules;
2. an analyst-maintained action/ownership table;
3. an AI recommendation service with review, confidence, and audit history.

The production system must label estimates and recommendations separately from
observed POSIST facts.

## Authentication, Hosting And Data Boundary

1. GitHub Pages hosts only static frontend code, schemas, documentation, and
   non-sensitive validation data.
2. The browser redirects to Zoho OAuth.
3. Supabase validates the account and access to the approved ABNAH workspace.
4. Refresh tokens are encrypted in Supabase; the browser receives only an
   opaque portal session.
5. The gateway reads selected Query Tables from Zoho and returns rows to the
   signed-in browser.
6. Operational rows are not written to GitHub or persisted by the gateway.
7. Exact report and Query Table links are generated on demand and remain
   governed by Zoho access.

## Why Refreshes Sometimes Failed Or Showed Zero

Two separate conditions were present:

1. Zoho allows at most five concurrent asynchronous export jobs per
   organization. Repeated P1/P2 refreshes could compete for that queue.
2. Zoho returned dates such as `31 Mar, 2026 00:00:00`, while the portal
   compared ISO values such as `2026-03-31`. Valid rows could therefore be
   filtered out after a successful export.

The gateway now serializes jobs, reuses a two-minute in-memory response cache,
and normalizes known Zoho date fields to `YYYY-MM-DD`.

Reference:
[Zoho asynchronous export limits](https://www.zoho.com/analytics/api/v2/bulk-api/export-data-async.html).

## Map Strategy

The portal always has a real pan/zoom OpenStreetMap base with governed outlet
markers. The current three-outlet coordinates are demonstrator geography and
are labelled accordingly.

The gateway can also request a short-lived native Zoho embed URL with the
selected criteria. Zoho documents that this endpoint requires
`ZohoAnalytics.embed.read` and Embedded Analytics eligibility. If the current
plan does not provide it, the real OpenStreetMap implementation remains the
supported visual and the exact Zoho report still opens through drill-through.

References:
[Zoho Get View URL](https://www.zoho.com/analytics/api/v2/embed-api/view-url.html),
[Zoho Get Embed URL](https://www.zoho.com/analytics/api/v2/embed-api/embed-url.html).

## Restroworks API Coverage

The current documentation packet contains:

- 34 documented entries;
- 30 callable HTTP operations;
- 4 documentation/checklist entries;
- 6 high-value Control Tower candidates: Bills, All Invoices, Menu Sync,
  Out-of-Stock Items, Fetch Inventory Data, and Indent.

No candidate is yet ABNAH-UAT validated. The public packet does not prove full
coverage for recipe BOM, batch/expiry, outlet geography, full PO-to-GRN
lineage, or a complete vendor master. Do not claim that APIs replace every
report today.

The production ingestion decision remains:

- scheduled, contract-validated CSV ingestion for uncovered reports; plus
- authenticated APIs for endpoints that pass UAT field, grain, pagination,
  freshness, and reconciliation tests.

## Code Studio Feasibility

Do not promise that the current portal can simply be moved into Zoho Code
Studio.

Zoho describes Code Studio as a Python environment for data transformation and
ML models, and currently documents it as an Enterprise-plan feature. It is not
a general React web-hosting replacement for this custom portal. On the current
Pro setup, GitHub Pages plus the Supabase OAuth/data gateway is the feasible
demonstrator architecture. A later enterprise decision can move transformation
jobs into Code Studio while retaining a separate presentation layer.

Reference:
[Zoho Code Studio](https://www.zoho.com/analytics/help/code-environment/code-studio.html).

## Local Viewer On The Work PC

`127.0.0.1` always means the computer on which the browser is running. A viewer
started on the personal laptop cannot be opened from the work laptop by using
the same localhost URL.

Use the hosted `Data quality` surface for presentation-safe aggregate evidence.
The full row reviewer remains private and must be started on the same work PC
after the local audit packet and reviewer are copied there:

```powershell
py -3 tools/local-auditor/local_report_viewer.py `
  --audit-run "D:\ABNAH_LOCAL\output\run_YYYYMMDD_HHMMSS"
```

Then open `http://127.0.0.1:8765/` on that same computer. Do not put the private
row packet in GitHub Pages.

## Exact Remaining Zoho Actions

1. Sign out of the custom portal and sign in once again only if you want the
   portal to attempt a native Zoho map embed. This grants the newly added
   `ZohoAnalytics.embed.read` scope. The OpenStreetMap view and exact
   login-governed Zoho report/Query Table links work without Embedded Analytics.
2. Keep all 38 Query Tables as currently saved; no Query Table rebuild is
   required for the custom P1/P2 portal.
3. If the Zoho dashboards themselves will be shown with changing dates, repair
   their dashboard timeline/user-filter column mappings. The custom portal does
   not depend on the Zoho dashboard timeline because it requests each Query
   Table using its own date field.
4. Do not create a replacement vendor-mitigation table before the meeting.
5. Use March 2026 for the validated demonstration baseline.
6. After UAT access, provide the enabled API credentials/samples and confirm
   production outlet geography, batch/expiry source, PO/GRN keys, and cost
   treatment.

## Questions And Answers

**Are the displayed P1/P2 values manually entered?**

No. In authenticated mode they are calculated from Zoho Query Table rows
returned through the API gateway. The validation baseline is used only when an
explicitly identified March source export fails.

**Why not just present the Zoho dashboard?**

Zoho remains the governed analytical layer. The custom portal adds ABNAH's
executive hierarchy, cross-view interaction, evidence drawers, precise
drill-through, and a consistent action-oriented presentation.

**Does the custom date filter require the Zoho dashboard timeline?**

No. The custom portal sends the date range to the exact Query Tables and filters
the returned rows. The Zoho dashboard timeline matters only when presenting
the original Zoho dashboard itself.

**Why is expiry labelled estimated?**

ABNAH has not enabled a production batch/expiry source. Query 38 is a
demonstrator based on receipt lineage, closing stock, theoretical demand, and
documented shelf-life assumptions. It must not be presented as observed expiry.

**Why is the risky-PO table empty while open PO exposure is not zero?**

Open exposure is all qualifying open PO value in Query 22. Risky PO mitigation
requires a stricter outlet-item-period match to an active non-green risk in
Query 36. No such intersection exists in the March baseline.

**Can another developer continue this work?**

Yes. The repository includes source schemas, evidence boundaries, 38 ordered
Query Tables, click-by-click Zoho instructions, KPI lineage, test data,
automated validations, portal source, Supabase functions, and handoff files.

**Can actual data replace synthetic data later?**

Yes, when actual multi-outlet aligned-period inputs pass the same contracts and
production gates. The layered model and KPI tests are intended to make that
replacement controlled rather than a dashboard rewrite.

## Presentation Guardrails

- Say "Restroworks/POSIST" unless ABNAH confirms a preferred product name.
- Say "estimated expiry exposure," not "actual expiry loss."
- Say "modelled recommendation," not "POSIST recommendation."
- Say "fit-for-use limitation," not "POSIST data is wrong."
- Say "API candidate," not "API integration complete."
- Do not expose raw local CSV rows, screenshots, secrets, or Supabase tokens.
- Keep the validated demonstration range on March 2026.
