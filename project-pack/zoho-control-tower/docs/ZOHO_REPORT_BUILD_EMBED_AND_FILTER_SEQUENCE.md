# ABNAH Zoho Report Build, Embed And Filter Sequence

## Purpose

This is the resume guide for the current Zoho workspace. It starts at the
point where all 38 Query Tables have been created and the lookup and Aggregate
Formula work is being completed.

The final delivery architecture is:

```text
38 numbered Query Tables
        |
        v
39 saved Zoho views: 20 KPI views + 19 reports
        |
        | secured-with-login iframe URL per saved view
        v
ABNAH external portal shell
        |
        | page layout, filters, colors and navigation
        v
Executive control tower
```

Do not embed one complete Zoho dashboard inside each page. That would replace
the supplied ABNAH layout with the native Zoho dashboard layout. The custom
portal now embeds every saved Zoho KPI/report in its own assigned slot.

## Resume Point

Complete these gates in order. Do not start report construction until Gate 3
passes.

### Gate 1 - Five corrected Query Tables

If these physical fields are already visible in View Mode, do not resave the
queries again. If any field is missing, replace and save only these five Query
Tables in this order:

1. `20_fact_ct_actual_consumption.sql`
2. `21_fact_ct_consumption_variance.sql`
3. `24_fact_ct_po_receipt_line.sql`
4. `31_sum_ct_price_movement.sql`
5. `33_sum_ct_scm_monthly.sql`

Verify:

| Query | Required physical fields |
| --- | --- |
| 20 | `bridge_transfer_out_qty`, `bridge_return_qty`, `bridge_closing_qty` |
| 21 | `signed_consumption_variance_value`, `consumption_variance_direction` |
| 24 | `eligible_lead_time_deviation_days` |
| 31 | `price_comparison_key`, `unit_price_change_percent`, `absolute_unit_price_change_percent`, `price_movement_direction` |
| 33 | `working_capital_value` |

No portal or embedding change requires another Query Table revision.

### Gate 2 - Exactly four required Aggregate Formulas

Create or retain only these required formulas:

| Query Table | Formula |
| --- | --- |
| `23_fact_ct_purchase_receipt.sql` | `Weighted Unit Price` |
| `24_fact_ct_po_receipt_line.sql` | `PO Fill Rate %` |
| `24_fact_ct_po_receipt_line.sql` | `Vendor OTIF %` |
| `25_fact_ct_menu_profitability.sql` | `Menu Gross Margin %` |

Expressions:

```text
Weighted Unit Price
if(sum("received_qty") <> 0,
   sum("receipt_subtotal") / sum("received_qty"),
   null)
```

```text
PO Fill Rate %
if(sum("ordered_qty") <> 0,
   sum("received_qty") / sum("ordered_qty") * 100,
   null)
```

```text
Vendor OTIF %
if(sum("eligible_closed_line_flag") <> 0,
   sum("otif_success_flag") / sum("eligible_closed_line_flag") * 100,
   null)
```

```text
Menu Gross Margin %
if(sum("net_sales") <> 0,
   sum("gross_margin_value") / sum("net_sales") * 100,
   null)
```

If Percentage formatting multiplies the displayed value again, remove
`* 100`. The final displayed values, not the storage convention, must match
the acceptance guide.

Aggregate Formulas are used in saved Summary Views. They are not expected to
appear in the direct KPI Widget **Data Column** list.

### Gate 3 - Pre-dashboard validation

Complete the detailed matrices in:

```text
ZOHO_LOOKUPS_AGGREGATE_FORMULAS_AND_PRE_DASHBOARD_SETUP.md
```

Minimum checks:

- Query 37 has 3 unique outlet codes.
- Query 14 has 43 unique item codes.
- Query 15 has 110 unique menu-item codes.
- Query 16 has 70 unique vendor names.
- Query 12 has 90 unique sales dates.
- Every required lookup is many-to-one from the fact/summary child to the
  unique dimension parent.
- The child column is converted to Lookup; the selected parent column is the
  unique dimension key.
- Query 34 exception totals match the acceptance guide.
- `month_03` is the default current-state period.

## Authentication Flow

The portal starts with a Zoho access screen.

1. The viewer chooses **Sign in with Zoho**.
2. Zoho Analytics opens in a normal browser tab.
3. The viewer signs in with the account to which the saved views were shared.
4. The viewer returns to the portal.
5. The viewer chooses **Continue after sign-in**.
6. Every secured report iframe reuses the active Zoho browser session.
7. Zoho independently checks permission for every saved view.

The static portal cannot inspect the Zoho cookie or automatically prove the
login because Zoho is a different origin. The Continue button is a preflight
step, not an authentication bypass. If the account is not authorized, Zoho
will still refuse the embedded reports.

For true one-step company SSO before the shell opens, use Zoho Directory with
Microsoft Entra ID, or an approved Embedded Analytics/JWT deployment. That is
an administrator and licensing decision, not a Query Table change.

## Build One Saved View

Repeat this procedure for every KPI and report in the page registers below.

### A. Create the view

1. Open Zoho Analytics.
2. Choose **Create > New Report**.
3. Choose the object type stated in the dashboard build guide.
4. Select the exact numbered Query Table.
5. Add the exact shelves, value aggregation, grouping, sort and fixed filter.
6. Save using the exact `CT_...` name.

For a direct KPI:

1. Select the physical Data Column.
2. Select Sum, Average, Count or Count Distinct as documented.
3. Leave Group By blank.
4. Type the business label in the KPI settings.

For an Aggregate Formula KPI:

1. Create a Summary View.
2. Place the named Aggregate Formula in the value area.
3. Do not add a grouping field.
4. Format the single value.
5. Save it using the assigned KPI view name.

### B. Validate before styling

1. Set period to `month_03` when the report is current-state.
2. Set Outlet to All.
3. Compare the number or report control totals with
   `ZOHO_DASHBOARD_EXPECTED_RESULTS.md`.
4. Test OUT001, OUT002 and OUT003 individually.
5. Confirm a historical trend still contains all three months.
6. Fix calculation or filtering errors before changing colors.

### C. Apply Zoho-side formatting

The outer portal provides the page background, cards, spacing, headings,
navigation and filter bar. Zoho still draws the pixels inside each iframe.

Therefore configure the saved Zoho view itself:

- white or transparent report background where available;
- hidden duplicate title, border and unnecessary toolbar;
- compact padding for KPI views;
- legend position and number formatting;
- the exact state colors below;
- interactive embed mode for tooltips, drill and underlying data.

State colors:

| State | Color |
| --- | --- |
| Purple | `#6F2DBD` |
| Red | `#E24950` |
| Amber | `#D29A2D` |
| Green | `#168D61` |
| Grey / no data | `#9A9A9A` |

Page accents:

| Page | Accent |
| --- | --- |
| Risk Action Center | Purple `#5B2D82`, gold `#9A8559` |
| Procurement & Vendor | Blue `#4164D9` |
| Consumption & Menu | Gold `#9A8559`, navy `#0F1834` |
| Explorer & Quality | Red `#E44B51`, charcoal `#343B46` |

### D. Share and generate the individual secured embed

1. Open the saved KPI/report view itself, not the full dashboard.
2. Choose **Share**.
3. Share the view with the exact company Zoho account as Viewer.
4. Remove public access and old without-login links.
5. Choose **Share > Embed**.
6. Select **Access with Login** or the equivalent secured-login option.
7. Select interactive mode.
8. Hide the Zoho view title/toolbar when those options are available because
   the outer card already supplies the title.
9. Copy the generated iframe.
10. Copy only the value of its `src` attribute.

Do not provide a password, OAuth token, client secret, raw row or full iframe
HTML to the portal.

### E. Connect the portal slot

1. Open `/portal/`.
2. Complete the Zoho sign-in preflight.
3. Choose **Configure**.
4. Select the correct page number.
5. Locate the exact saved view name.
6. Paste its secured iframe `src` URL.
7. Choose **Save locally**.
8. Switch that page from **Blueprint** to **Live reports**.
9. Confirm that the Zoho view appears inside the existing ABNAH card/panel.
10. Change a portal filter and choose **Apply**.
11. Confirm only the intended report frames reload with the corresponding
    criteria.

Unconfigured slots remain in Blueprint form. This supports progressive
construction without breaking the page.

## Exact Build And Embed Order

Build Page 4 first because it provides descriptive and data-quality controls,
then Page 3, Page 2 and Page 1. This proves the detailed sources before the
executive action layer.

### Page 4 - SCM Descriptive Explorer & Data Quality

KPI slots:

1. `CT_P4_KPI_Closing_Stock`
2. `CT_P4_KPI_Open_PO`
3. `CT_P4_KPI_Net_Sales`
4. `CT_P4_KPI_Actual_Consumption`
5. `CT_P4_KPI_Consumption_Variance`

Report slots:

6. `CT_P4_SCM_Monthly_Trend`
7. `CT_P4_Data_Quality_Detail`
8. `CT_P4_Descriptive_Explorer`

Period must not filter the monthly trend or Query 34 quality detail. Outlet
must not filter Query 34.

### Page 3 - Consumption Variance & Menu Profitability

KPI slots:

1. `CT_P3_KPI_Net_Sales`
2. `CT_P3_KPI_Theoretical_COGS`
3. `CT_P3_KPI_Menu_Gross_Margin`
4. `CT_P3_KPI_Menu_Items`
5. `CT_P3_KPI_Consumption_Leakage`

Report slots:

6. `CT_P3_Consumption_Bridge`
7. `CT_P3_Consumption_Variance`
8. `CT_P3_Menu_BCG`
9. `CT_P3_Outlet_Item_Heatmap`

The bridge must retain all periods. Quantity reports require one Canonical UOM.
Menu filters apply only to menu sources. Raw-material filters apply only to
ingredient consumption sources.

### Page 2 - Procurement, Vendor & Capital Control

KPI slots:

1. `CT_P2_KPI_Monthly_Purchase`
2. `CT_P2_KPI_Open_PO_Liability`
3. `CT_P2_KPI_Delayed_PO_Value`
4. `CT_P2_KPI_OTIF`
5. `CT_P2_KPI_Price_Watch`

Report slots:

6. `CT_P2_Procurement_Funnel`
7. `CT_P2_Vendor_Scorecard`
8. `CT_P2_Ingredient_Price_Trend`
9. `CT_P2_Top_Price_Movement`
10. `CT_P2_Pending_By_Vendor`
11. `CT_P2_Expected_Delivery_Breach`

Period must not filter the historical ingredient price trend. Vendor and
ingredient filters apply only to reports whose source has those columns.

### Page 1 - Risk Action Center

KPI slots:

1. `CT_P1_KPI_Outlets_At_Stockout_Risk`
2. `CT_P1_KPI_Menu_Items_At_Risk`
3. `CT_P1_KPI_Stockout_Risk_Value`
4. `CT_P1_KPI_Expiry_Risk_Value_Demo`
5. `CT_P1_KPI_Open_Actions`

Report slots:

6. `CT_P1_Outlet_Risk_Map`
7. `CT_P1_Action_Center`
8. `CT_P1_Stockout_Risk_Detail`
9. `CT_P1_Menu_Impact_Detail`
10. `CT_P1_Expiry_Risk_Detail_Demo`
11. `CT_P1_Vendor_PO_Risk`

The Risk control changes the visible scope:

- Stockout shows Query 27, 28 and 36 views.
- Expiry shows Query 38 views.
- All shows both scopes.

The stockout reports retain their fixed `risk_type = STOCKOUT` report filter.

## External Filter Contract

The portal applies filters by rebuilding each individual secured embed URL
with a URL-encoded `ZOHO_CRITERIA` expression. This works without a backend.

Do not create another row of native Zoho dashboard filters for this delivery
portal. Create only the fixed report filters named in the report build guide.
The outer portal displays all controls required for the active page at once,
then sends each selected value only to compatible saved views.

The exact visible controls are:

| Page | Controls shown together |
| --- | --- |
| Page 1 | As-of period, Region, Outlet, Risk, Ingredient category, Owner |
| Page 2 | As-of period, Region, Outlet, Ingredient category, Vendor, PO status, Raw material |
| Page 3 | As-of period, Region, Outlet, Super category, Menu category, Menu item, Raw material, Canonical UOM |
| Page 4 | Period, Region, Outlet, Ingredient category, Exception type |

The exact select values come from the modeled fields:

- Page 2 PO status: `Pending`, `Partially Received`, `Closed`, `Cancelled`;
- Page 3 Canonical UOM: `kg`, `litre`, `pcs`;
- Page 1 Risk: `STOCKOUT` or `EXPIRY`; this switches visible view families
  rather than adding a source criterion;
- Page 4 Exception type: the six Query 34 exception codes listed in the
  portal selector.

Example:

```text
("27_fact_ct_inventory_risk.sql"."source_period_code" = 'month_03')
AND
("27_fact_ct_inventory_risk.sql"."outlet_code" = 'OUT001')
```

Search controls use `LIKE '%value%'`. Select controls use equality. The portal
has a per-report mapping and does not send a filter to a report whose source
does not support it.

| Filter | Mapping rule |
| --- | --- |
| As-of period | Current-state views only |
| Outlet | Views with a genuine `outlet_code` |
| Region | Outlet-linked views through Query 37 |
| Ingredient category | Ingredient facts through Query 14 |
| Menu category/super category | Menu facts through Query 15 |
| Vendor | PO, receipt, vendor and price views |
| PO status | PO/receipt-line views only |
| Raw material | Ingredient-grain views only |
| Menu item | Menu-grain views only |
| Canonical UOM | Quantity consumption views only |
| Exception type | Query 34 quality detail only |

`ZOHO_CRITERIA` is a view filter, not row-level security. Zoho sharing and the
secured login remain the security boundary.

### Filter exclusions that are intentional

- Page 2 period does not alter `CT_P2_Ingredient_Price_Trend`.
- Page 3 period does not alter `CT_P3_Consumption_Bridge`.
- Page 4 period does not alter `CT_P4_SCM_Monthly_Trend` or
  `CT_P4_Data_Quality_Detail`.
- Page 4 outlet and region do not alter model-wide Query 34 quality checks.
- Menu category, super category and menu item do not alter ingredient-grain
  views.
- Ingredient category and raw material do not alter menu-grain views.
- Canonical UOM applies only to quantity-consumption views.
- Vendor and PO status apply only to views whose physical source contains
  those attributes.

If a control does not apply to a saved view, that iframe stays unchanged when
the control is applied. This is deliberate, not a broken global filter.

## Native Dashboard Option

The saved views can also be assembled into the native four-tab dashboard after
the custom portal is working. This provides:

- a Zoho-only fallback;
- native reports-as-filters;
- one object for internal Zoho sharing;
- a comparison surface for acceptance testing.

The custom portal does not depend on that dashboard. Build it after the saved
views reconcile, not before.

## Known Exact-Fidelity Boundaries

The individual-report approach preserves the ABNAH outer layout. It does not
rewrite the pixels inside a Zoho iframe.

- `CT_P1_Action_Center` remains a conditional-format Zoho table for the MVP.
  Exact action cards require approved row retrieval through a backend/API.
- `CT_P3_Consumption_Bridge` remains a Zoho combination chart for the MVP.
  An exact waterfall requires either a supported Zoho waterfall or custom
  rendering over approved aggregate data.

Do not calculate these values independently in the browser.

## Acceptance Gate Per View

Do not mark a view complete until:

- its exact `CT_...` name is used;
- its source Query Table and aggregation match the guide;
- its default result reconciles;
- its page filters affect only the intended data;
- its secured embed works after a fresh Zoho sign-in;
- its title and toolbar do not duplicate the outer card;
- its colors match the state/page contract;
- no unapproved actual-source claim is made for expiry, OTIF or other gated
  measures.

## Official References

- Zoho secured individual-view embedding and `ZOHO_CRITERIA`:
  https://www.zoho.com/analytics/help/publishing/embed-reports.html
- Zoho JavaScript API for embedded-view control:
  https://www.zoho.com/analytics/js-api/
- Zoho `applyUserFilter` JavaScript method:
  https://www.zoho.com/analytics/js-api/apply-user-filter.html
- Zoho dashboard filter mapping:
  https://www.zoho.com/analytics/help/dashboard/filter.html
- Zoho Directory and Microsoft Entra SSO:
  https://www.zoho.com/analytics/help/zoho-directory.html
