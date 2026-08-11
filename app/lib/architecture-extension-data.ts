export interface ZiaHelperTable {
  order: number;
  name: string;
  viewId: string;
  deploymentStatus: string;
  grain: string;
  purpose: string;
  sqlPurpose?: string;
  whyItExists: string;
  dependencies: string[];
  workflows: string[];
  keyFields: string[];
  acceptanceControl: string;
  guardrails: string[];
  steps: string[];
}

export const ziaHelperTables: ZiaHelperTable[] = [
  {
    order: 1,
    name: "ZIA_QT_03_Recipe_Canonical",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_CREATED",
    grain: "menu_item_code x ingredient_code x canonical_uom",
    purpose: "Expose governed recipe quantities and conversion authority without opening the broad recipe master to Ask Zia.",
    whyItExists: "Recipe questions were refused while REF_Item_Recipe remained correctly excluded from the seven-object semantic scope.",
    dependencies: ["REF_Item_Recipe", "CTL_UOM_Conversions"],
    workflows: ["WF03 Recipe decomposition", "WF04 Menu-to-vendor dependency", "WF10 Dessert ranking follow-up"],
    keyFields: ["menu_item_code", "menu_item_name", "ingredient_code", "ingredient_name", "recipe_source_qty", "recipe_source_unit", "canonical_qty_per_menu_unit", "canonical_uom", "conversion_status", "conversion_authority"],
    acceptanceControl: "Cream Cheese Bagel returns five canonical rows; Classic Cold Coffee - Regular returns eight.",
    guardrails: ["Ask one exact menu variant at a time.", "Never infer recipe quantities from sales or risk rows.", "Keep REF_Item_Recipe excluded when this helper is exposed."],
    steps: [
      "Open Data and verify the existing table name and live view ID shown here; do not recreate or rename it.",
      "In Ask Zia Include/Exclude Columns, include this helper and keep the broad REF_Item_Recipe table excluded.",
      "Set Item Name and Ingredient Name as high-priority dimensions; keep canonical quantity and UOM together.",
      "Run the two acceptance recipes and compare every returned row, quantity and unit to the source control.",
      "Only mark a recipe workflow PASS after Report Information shows this helper and the exact item variant.",
    ],
  },
  {
    order: 2,
    name: "ZIA_QT_01_Procurement_Snapshot",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_CREATED",
    grain: "snapshot_date x po_number x item_code",
    purpose: "Present one-date open procurement state with vendor, PO, material, liability and timing fields on the same row.",
    whyItExists: "Broad procurement state was difficult to query conversationally without losing the selected snapshot or multiplying repeated state rows.",
    dependencies: ["QT_05_Procurement_Control"],
    workflows: ["WF01 Open-versus-overdue boundary", "WF04 Menu-to-vendor dependency", "WF11 Open vendors on 14 Jan"],
    keyFields: ["snapshot_date", "vendor_code", "vendor_name", "po_number", "item_code", "item_name", "open_quantity_canonical", "all_open_po_liability_pre_tax", "overdue_open_po_liability_pre_tax", "overdue_days", "delivery_status_scope", "latest_valid_flag"],
    acceptanceControl: "31 Jan FreshDairy all-open state is INR 79,267.88 and 13 POs; 14 Jan has eight open vendors.",
    guardrails: ["Fix exactly one snapshot_date before totaling state measures.", "Expected-delivery flow still comes from RAW_Enterprise_Purchase_Order.", "Never present all-open liability as overdue-only liability."],
    steps: [
      "Verify the existing helper and view ID, then include it in Ask Zia.",
      "Prioritize snapshot_date, vendor_name, po_number and item_name; retain delivery_status_scope as an explanatory field.",
      "Ask one fully scoped state question with the exact snapshot date and positive open quantity.",
      "Inspect Report Information for one equality date and reconcile distinct POs plus liability before accepting.",
      "Use RAW_Enterprise_Purchase_Order instead when the question asks what is expected to arrive on a physical delivery date.",
    ],
  },
  {
    order: 3,
    name: "ZIA_QT_02_Menu_Actual_Forecast",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_CREATED",
    grain: "record_scope x outlet_name x menu_item_code x business_or_forecast_date",
    purpose: "Separate actual menu economics from deterministic future menu demand while retaining each clock explicitly.",
    whyItExists: "Forecast follow-ups lost outlet/date context and exact-date sales follow-ups widened to a quarter.",
    dependencies: ["QT_04_Menu_Profitability", "QT_01A_Menu_Forecast"],
    workflows: ["WF02 Sales, margin and Latte forecast", "WF05 Exact-date Latte economics", "WF10 Continuous-range dessert ranking"],
    keyFields: ["record_scope", "business_date", "as_of_date", "forecast_date", "outlet_name", "menu_item_code", "menu_item_name", "category_name", "actual_net_sales_value", "actual_theoretical_gross_margin", "actual_theoretical_gross_margin_pct", "forecast_menu_qty", "forecast_net_sales_value", "date_semantic_rule"],
    acceptanceControl: "Connaught Coffee Classics January sales are INR 207,489.63 at 84.02% weighted theoretical GM; Latte forecast is 2.333333 units and INR 554.223333.",
    guardrails: ["Filter record_scope before choosing a date.", "Actual uses business_date; forecast uses as_of_date plus forecast_date.", "Use a continuous inclusive predicate for date ranges."],
    steps: [
      "Verify the live helper and include it in Ask Zia; keep record_scope and date_semantic_rule visible.",
      "For actuals, filter record_scope = ACTUAL and use business_date only.",
      "For forecasts, filter record_scope = FORECAST and state both the snapshot and target date.",
      "Use 100 x SUM(margin) / SUM(net sales) for a weighted margin percentage; never average row percentages.",
      "Inspect Report Information for the exact date predicate and log no-data honestly when the requested day is absent.",
    ],
  },
  {
    order: 4,
    name: "ZIA_QT_04_Menu_Vendor_Dependency",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_CREATED",
    grain: "snapshot_date x menu_item_code x ingredient_code x po_number",
    purpose: "Connect an exact menu recipe to the vendors and open procurement lines for its ingredients.",
    whyItExists: "A direct conversational join selected inventory exposure instead of procurement liability and silently guessed a missing menu variant.",
    dependencies: ["ZIA_QT_03_Recipe_Canonical", "ZIA_QT_01_Procurement_Snapshot"],
    workflows: ["WF04 Menu-to-vendor dependency"],
    keyFields: ["snapshot_date", "menu_item_code", "menu_item_name", "ingredient_code", "ingredient_name", "canonical_qty_per_menu_unit", "outlet_name", "vendor_name", "po_number", "expected_delivery_date", "vendor_open_quantity_canonical", "vendor_quantity_uom", "vendor_open_po_liability_pre_tax", "vendor_overdue_open_po_liability_pre_tax"],
    acceptanceControl: "Classic Cold Coffee - Regular: PackPro INR 11,621.85 / 8 POs; FreshDairy INR 8,754.33 / 4; SweetBase INR 1,878.81 / 1.",
    guardrails: ["Clarify menu variant and snapshot before querying.", "Use vendor liability fields, never monetary_exposure.", "For category scope de-duplicate snapshot + vendor + PO + ingredient before summing."],
    steps: [
      "Verify the existing helper and include only its curated dependency fields in Ask Zia.",
      "Ask for one exact menu variant and one snapshot date; show ingredients with no open PO as zero/no open PO.",
      "For category scope, get the menu_item_code set from ZIA_QT_02_Menu_Actual_Forecast first.",
      "Filter this helper by that code set, then de-duplicate at snapshot, vendor, PO and ingredient before totaling liability.",
      "Reconcile vendor liability and distinct PO counts to the acceptance control before presentation.",
    ],
  },
  {
    order: 5,
    name: "ZIA_QT_05_Inventory_Expiry_Action",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_CREATED",
    grain: "snapshot_date x evaluation_id",
    purpose: "Keep current stock, expiry batches, next-day demand, seven-day demand, shortage and exposure in one curated action row.",
    whyItExists: "Earlier answers omitted the date/unit, mixed total stock with batch expiry, and summed incompatible UOMs.",
    dependencies: ["QT_02_Numerical_Risk_Center", "SYN_Provisional_Expiry_Report"],
    workflows: ["WF06 Provisional expiry today", "WF07 Inclusive expiry window", "WF09 Latest Red inventory action"],
    keyFields: ["snapshot_date", "risk_domain", "outlet_name", "item_name", "batch_number", "expiry_date", "canonical_uom", "total_item_stock_qty", "expired_batch_qty", "usable_nonexpired_qty", "current_stock_qty", "next_day_required_qty", "forecast_required_qty", "shortage_qty", "monetary_exposure", "expiry_window_qty_at_risk", "latest_valid_flag", "core_complete_flag", "metric_semantic_rule"],
    acceptanceControl: "Expiry, inclusive-window and six-row Red inventory controls reconcile; the complete 31 Jan Red exposure is INR 15,115.85.",
    guardrails: ["Every expiry answer says PROVISIONAL SYNTHETIC EXPIRY DEMONSTRATION - NOT POSIST ACTUALS.", "MAX repeated total-stock measures; SUM physical batch measures.", "Never total kg, litre and pcs together."],
    steps: [
      "Verify the helper and expose its date, UOM, action measures, completeness flags and disclosure fields together.",
      "For expiry, fix one snapshot, outlet, material and UOM; MAX total stock and SUM physical batch quantities.",
      "For an expiry window, keep snapshot_date fixed and apply a continuous inclusive expiry_date range.",
      "For inventory action, require LATEST_VALID, core_complete_flag = 1, INVENTORY and Red on the same visible result.",
      "Compare narrative and visible rows one-for-one; fail the workflow if they name different items or omit units.",
    ],
  },
  {
    order: 6,
    name: "ZIA_01_Strict_Overdue_PO",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_CREATED_REQUIRED_BY_REPRODUCED_FAILURE",
    grain: "as_of_date x po_number x item_code",
    purpose: "Physically restrict semantic rows to overdue_days > 0 so Ask Zia cannot widen overdue-only wording to all-open procurement.",
    whyItExists: "The reproduced live prompt translated 'more than zero days' incorrectly and returned the all-open INR 79,267.88 set.",
    dependencies: ["QT_05_Procurement_Control"],
    workflows: ["WF01 FreshDairy strict overdue liability"],
    keyFields: ["as_of_date", "vendor_name", "po_number", "item_name", "canonical_uom", "remaining_qty_canonical", "overdue_liability_pre_tax", "expected_delivery_date", "overdue_days", "risk_color", "core_complete_flag", "latest_valid_flag", "snapshot_selector", "overdue_scope_code", "semantic_row_key"],
    acceptanceControl: "31 Jan FreshDairy: INR 56,175.06, 10 distinct overdue POs and maximum 29 overdue days.",
    guardrails: ["Every row is physically overdue_days > 0.", "Do not expose an all-open measure with an overdue synonym.", "Fallback is RPT_V2_P08_Delivery_Breach_Action_Top10 when Report Information drifts."],
    steps: [
      "Verify the existing strict helper and live view ID; do not replace it with a natural-language threshold on the broad table.",
      "Expose overdue_liability_pre_tax, distinct PO and maximum overdue days with explicit overdue-only synonyms.",
      "Ask WF01 at 31 Jan, then inspect Report Information for this helper and one equality date.",
      "Reconcile INR 56,175.06, 10 distinct POs and 29 maximum days; reject the all-open control.",
      "Log the UI result in the conversational ledger and present only after the primary plus follow-up are marked PASS.",
    ],
  },
  {
    order: 7,
    name: "ZIA_01A_Strict_Overdue_Vendor_Summary",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_REMEDIATION_HELPER_CONVERSATIONALLY_BLOCKED",
    grain: "Snapshot Date x Vendor Name",
    purpose: "Expose one business-readable vendor summary row per strict-overdue snapshot so liability, PO count and maximum delay require no conversational regrouping.",
    sqlPurpose: "Group ZIA_01_Strict_Overdue_PO by as_of_date and vendor_name; rename them Snapshot Date and Vendor Name; calculate SUM(overdue_liability_pre_tax), COUNT(DISTINCT po_number) and MAX(overdue_days) as three business-readable measures.",
    whyItExists: "The line-level strict helper reconciled numerically, but Ask Zia still refused the original exact prompt. This second helper removes underscore-heavy names and aggregation ambiguity; an explicit prompt naming it also refused, proving that source calculation is not the remaining blocker.",
    dependencies: ["ZIA_01_Strict_Overdue_PO"],
    workflows: ["WF01 strict-overdue semantic remediation"],
    keyFields: ["Snapshot Date", "Vendor Name", "Strict Overdue Liability", "Distinct Overdue PO Count", "Maximum Overdue Days"],
    acceptanceControl: "31 Jan 2026 / FreshDairy Foods NCR: INR 56,175.0572 strict-overdue liability, 10 distinct overdue POs and maximum 29 overdue days.",
    guardrails: ["The parent helper already restricts every row to overdue_days > 0.", "One row represents one snapshot and one vendor; do not sum it across dates.", "The original prompt and the explicit-helper prompt both refused, so this helper is not conversational acceptance evidence.", "Use RPT_V2_P08_Delivery_Breach_Action_Top10 until a clean live prompt and follow-up both pass."],
    steps: [
      "Resolve the live Query Table through the private client binding and verify the five business-readable columns shown here.",
      "Read the SQL as a vendor/date summary of the physically strict ZIA_01 helper; do not join it back to line rows before totaling.",
      "Reconcile FreshDairy on 31 Jan to INR 56,175.0572, 10 distinct overdue POs and 29 maximum overdue days.",
      "Run the original exact WF01 prompt in a clean conversation, then run a separate prompt explicitly naming this helper.",
      "Keep WF01 BLOCKED because both prompt routes refused; record the governed P08 report as the presentation fallback.",
    ],
  },
  {
    order: 8,
    name: "ZIA_QT_06_Provisional_Expiry_Only",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_CREATED_UI_READ_BACK_WAT06_AND_WAT07_TARGETED_SMOKES_PARTIAL",
    grain: "snapshot_date x evaluation_id (EXPIRY only)",
    purpose: "Physically isolate provisional expiry rows and expose every quantity as a UOM-bound display field with an exact source disclosure.",
    whyItExists: "WF06 omitted the mandatory disclosure and WF07 selected a batch count instead of the governed expiry-window quantity on the overloaded inventory/expiry surface.",
    dependencies: ["ZIA_QT_05_Inventory_Expiry_Action"],
    workflows: ["WF06 Provisional expiry today", "WF07 Inclusive provisional expiry window"],
    keyFields: ["snapshot_date", "outlet_name", "item_name", "batch_number", "expiry_date", "canonical_uom", "expired_quantity_with_uom", "expiry_window_quantity_with_uom", "data_status_disclosure"],
    acceptanceControl: "Exact-day and inclusive-window source controls reconcile; both targeted conversational smokes remain partial.",
    guardrails: ["This is a Zia helper, not an eleventh governed core Query Table.", "Every quantity carries its UOM in the same field.", "The provisional-synthetic disclosure is a physical column and must remain visible."],
    steps: ["Resolve the private view ID from the client binding; never hard-code it in a public artifact.", "Verify the SQL hash and EXPIRY-only predicate before inclusion.", "Set table priority High, dates to Full Date, and UOM-bound display fields to Actual.", "Save, reopen and read back the synonyms and functions.", "Keep WAT06 PARTIAL because disclosure/material/outlet were omitted, and keep WAT07 PARTIAL because it selected batch count rather than the governed quantity."],
  },
  {
    order: 9,
    name: "ZIA_QT_07_Current_Red_Inventory",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_CREATED_UI_READ_BACK_FUNCTIONAL_SMOKE_PASS_NO_SCHEMA_V1_RECEIPT",
    grain: "latest valid complete Red INVENTORY evaluation",
    purpose: "Expose six current Red inventory subjects with explicit one-day and seven-day horizon fields while preventing cross-UOM quantity totals.",
    whyItExists: "WF09 selected a value-shaped seven-day field and used MAX exposure on the mixed inventory/expiry helper.",
    dependencies: ["ZIA_QT_05_Inventory_Expiry_Action"],
    workflows: ["WF09 Latest Red inventory action"],
    keyFields: ["snapshot_date", "outlet_name", "item_name", "canonical_uom", "current_stock_with_uom", "next_day_date", "next_day_requirement_with_uom", "forecast_horizon_end_date", "forecast_horizon_days", "seven_day_requirement_with_uom", "shortage_with_uom", "monetary_exposure"],
    acceptanceControl: "Six latest-valid complete Red rows reconcile; monetary exposure is the only additive numeric measure.",
    guardrails: ["Do not reintroduce raw numeric quantity fields.", "Keep monetary_exposure on Sum.", "Retain the seven-day horizon days and end date beside the display quantity."],
    steps: ["Verify the physical latest-valid, complete, Red INVENTORY predicates.", "Set quantity display fields to Actual and exposure to Sum.", "Read back date roles, UOM synonyms and the seven-day field.", "Retain the functional-smoke receipt showing helper routing, all six governed rows and UOM-safe output.", "Do not promote the canonical WAT ledger without a schema-v1 receipt; keep the full ladder held."],
  },
  {
    order: 10,
    name: "ZIA_QT_08_Positive_Open_Vendor_Material",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_EDITED_IN_PLACE_V3_FUNCTIONAL_SMOKE_PASS_NO_SCHEMA_V1_RECEIPT",
    grain: "snapshot_date x vendor x material x canonical_uom",
    purpose: "Enforce strictly positive, source-complete open procurement while separating display-only repeated vendor controls from anchor-row-safe additive measures.",
    whyItExists: "WF11 used a non-strict generated predicate, while the prior helper repeated vendor count and liability on every material row. Version 3 makes those repeated controls display text and emits additive safe measures only on one deterministic vendor anchor row.",
    dependencies: ["ZIA_QT_01_Procurement_Snapshot"],
    workflows: ["WF11 Open vendors on 14 Jan"],
    keyFields: ["snapshot_date", "vendor_code", "vendor_name", "item_name", "canonical_uom", "item_open_quantity_with_uom", "item_distinct_po_count", "item_open_liability_pre_tax", "vendor_distinct_po_count", "vendor_open_liability_pre_tax", "vendor_distinct_po_count_safe", "vendor_open_liability_pre_tax_safe", "open_state_scope_code"],
    acceptanceControl: "The targeted smoke routed to QT08, returned all 19 vendor-material rows across eight vendors, and reconciled both anchor-row-safe totals.",
    guardrails: ["Positive-open and completeness predicates exist in both detail and vendor scopes.", "vendor_distinct_po_count and vendor_open_liability_pre_tax are display text, never additive measures.", "The two *_safe measures occur only on each vendor's deterministic minimum-item anchor row and use High / Sum.", "Count vendors using distinct vendor_code only when explicitly requested."],
    steps: ["Verify the outer and inner positive-open predicates and completeness checks.", "Confirm the repeated vendor count and liability fields are display text.", "Confirm vendor_distinct_po_count_safe and vendor_open_liability_pre_tax_safe exist only on the deterministic minimum-item anchor row for each vendor and are High / Sum.", "Retain the WAT11 functional-smoke receipt for 19 rows, eight vendors and reconciled safe totals.", "Keep canonical WAT11 PARTIAL and the governed report fallback until a schema-v1 receipt and required follow-up exist."],
  },
  {
    order: 11,
    name: "ZIA_QT_09_PO_Delivery_UOM_Safe",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_RECREATED_TARGETED_3_FIELD_UI_READBACK_PASS_WAT_RETRY_NO_GATE_IMPROVEMENT",
    grain: "physical PO line",
    purpose: "Keep expected-delivery line detail while exposing non-additive ordered quantity beside source UOM and retaining combined PO-line display fields.",
    whyItExists: "WF08 routed correctly but generated a cross-UOM Key Highlight that attached the lowest numeric quantity to the wrong item.",
    dependencies: ["RAW_Enterprise_Purchase_Order"],
    workflows: ["WF08 Expected delivery line detail"],
    keyFields: ["expected_delivery_date", "po_number", "item_name", "ordered_quantity", "source_uom", "ordered_quantity_with_uom", "po_line_display", "ordered_value_pre_tax"],
    acceptanceControl: "The 27-Jan line count, PO count and pre-tax detail total reconcile to the physical source.",
    guardrails: ["ordered_quantity is non-additive text and source_uom is a separate Actual field; retain ordered_quantity_with_uom for safe display.", "Line subtotal may Sum because it has one currency grain.", "Do not join this physical flow to daily state snapshots."],
    steps: ["Verify the physical raw-PO dependency and exact expected-delivery date field.", "Set ordered_quantity and source_uom to Actual with the governed synonyms.", "Set ordered_value_pre_tax to Sum and read back all three fields after saving.", "Run WAT_08_01 in a fresh conversation only after a new causal routing change.", "Fail the smoke if the helper is bypassed or any cross-UOM Key Highlight or grand total appears."],
  },
  {
    order: 12,
    name: "ZIA_QT_10_PO_Delivery_Value_By_PO",
    viewId: "PRIVATE_CLIENT_BINDING",
    deploymentStatus: "LIVE_CREATED_AND_UI_READ_BACK_TARGETED_WAT_PENDING",
    grain: "expected_delivery_date x po_number",
    purpose: "Provide exactly one ordered-value row per delivery date and PO for durable grouped PO-value answers.",
    whyItExists: "The WF08 grouped follow-up reconciled numerically but did not display all exact PO totals durably.",
    dependencies: ["RAW_Enterprise_Purchase_Order"],
    workflows: ["WF08 Value by PO follow-up"],
    keyFields: ["expected_delivery_date", "po_number", "physical_line_count", "po_ordered_value_pre_tax", "po_value_display", "po_value_scope_code"],
    acceptanceControl: "The 27-Jan scope has exactly three rows for three POs and reconciles to the detail total.",
    guardrails: ["One row per date and PO; no repeated PO summary value.", "PO ordered value uses Sum.", "This helper does not replace the physical line-detail surface."],
    steps: ["Verify the one-row-per-date-and-PO grain.", "Set expected_delivery_date to Full Date and PO value to Sum.", "Read back PO-value synonyms and scope code.", "Run WAT_08_02 immediately after a passing WAT_08_01 in the same conversation.", "Keep WF08 PARTIAL until both schema-v1 receipts pass."],
  },
];

export interface ZiaWorkflow {
  id: string;
  name: string;
  prompt: string;
  primaryObject: string;
  dateContract: string;
  filterContract: string;
  aggregationContract: string;
  expectedControl: string;
  negativeControl: string;
  presentationStatus: string;
  sourceStatus: "PASS";
  conversationStatus: "NOT_RUN" | "PARTIAL" | "PASS" | "FAIL";
  followUpStatus: "NOT_RUN" | "PARTIAL" | "PASS" | "FAIL";
  liveFinding: string;
}

export const ziaWorkflowAcceptanceLedger = {
  artifact: "19_LIVE_CONVERSATIONAL_ZIA_RESULTS.csv",
  status: "BLOCKED",
  testCount: 22,
  passCount: 7,
  partialCount: 9,
  failCount: 6,
  presentationReadyWorkflowCount: 0,
  currentLedger: "7 PASS / 9 PARTIAL / 6 FAIL",
} as const;

export const ziaWorkflows: ZiaWorkflow[] = [
  { id: "WF01", name: "FreshDairy strict overdue liability", prompt: "As of 31 Jan 2026, show FreshDairy open POs overdue by more than zero days, total overdue liability, distinct POs and maximum overdue days.", primaryObject: "ZIA_01_Strict_Overdue_PO + ZIA_01A_Strict_Overdue_Vendor_Summary", dateContract: "as_of_date = 31 Jan 2026; follow-up = 21 Jan 2026", filterContract: "vendor_name = FreshDairy Foods NCR; overdue_days > 0", aggregationContract: "SUM overdue liability; DISTINCTCOUNT PO; MAX overdue days", expectedControl: "31 Jan: INR 56,175.0572 / 10 POs / 29 days. 21 Jan: INR 25,686.13 / 7 / 19.", negativeControl: "INR 79,267.88 / 13 POs is all-open, not overdue-only.", presentationStatus: "BLOCKED - use RPT_V2_P08_Delivery_Breach_Action_Top10 only.", sourceStatus: "PASS", conversationStatus: "FAIL", followUpStatus: "FAIL", liveFinding: "WAT_01_01 refused despite the active strict helper and semantic settings. The immediate 21-Jan follow-up then errored, so context could not be evaluated. Earlier helper reconciliation is diagnostic source evidence, not conversational acceptance." },
  { id: "WF02", name: "Coffee Classics economics and Latte demand", prompt: "Ask actual January Coffee Classics economics for Connaught, then separately ask the 21-Jan snapshot forecast for Latte - Medium on 22 Jan.", primaryObject: "ZIA_QT_02_Menu_Actual_Forecast", dateContract: "Actual: 1-31 Jan inclusive. Forecast: as_of 21 Jan, target 22 Jan.", filterContract: "Connaught; Coffee Classics; then Latte - Medium; record_scope first", aggregationContract: "SUM sales; weighted GM ratio of sums; MAX one forecast row", expectedControl: "INR 207,489.63 / 84.02%; forecast 2.333333 units / INR 554.223333.", negativeControl: "A blank forecast or a response missing outlet, snapshot, target date or method fails.", presentationStatus: "BLOCKED - the actual-economics WAT fails and the full ladder is unsafe.", sourceStatus: "PASS", conversationStatus: "FAIL", followUpStatus: "PASS", liveFinding: "The actual-economics WAT selected only the date-range endpoints and returned INR 14,941.52 / 84.16%, so it failed. The separate forecast WAT passed with FORECAST scope, 21-Jan snapshot, 22-Jan target, exact outlet/item and 2.333333 units / INR 554.223333." },
  { id: "WF03", name: "Governed recipe decomposition", prompt: "List exact recipe ingredients, quantities and units for Cream Cheese Bagel; repeat separately for Classic Cold Coffee - Regular.", primaryObject: "ZIA_QT_03_Recipe_Canonical", dateContract: "No date; current reference master", filterContract: "Exact menu variant", aggregationContract: "Actual rows; no cross-variant summation", expectedControl: "Cream Cheese Bagel has 5 rows; Classic Cold Coffee - Regular has 8.", negativeControl: "A refusal, missing units or another size's recipe fails.", presentationStatus: "BLOCKED - both WAT rows pass, but the six-tier natural-language workflow does not.", sourceStatus: "PASS", conversationStatus: "PASS", followUpStatus: "PASS", liveFinding: "Both atomic WAT rows passed: five Cream Cheese Bagel rows and eight Classic Cold Coffee - Regular rows routed to the canonical helper. Display rounding is disclosed and exact source quantities remain controlled; the broader ladder still records unsafe refusals, hallucination and mixed-UOM behavior." },
  { id: "WF04", name: "Menu-to-vendor dependency", prompt: "For Classic Cold Coffee - Regular at 31 Jan, identify recipe ingredients and vendors with open liability and PO count; then run category scope.", primaryObject: "ZIA_QT_04_Menu_Vendor_Dependency", dateContract: "One procurement snapshot; recipe itself is undated", filterContract: "Exact menu variant; positive open quantity; recipe ingredient set", aggregationContract: "Item: sum vendor liability. Category: de-duplicate snapshot + vendor + PO + ingredient first.", expectedControl: "PackPro INR 11,621.85 / 8; FreshDairy INR 8,754.33 / 4; SweetBase INR 1,878.81 / 1.", negativeControl: "monetary_exposure, a missing snapshot or a guessed menu variant fails.", presentationStatus: "BLOCKED - clarification and complete ingredient-bridge controls are not reliable.", sourceStatus: "PASS", conversationStatus: "FAIL", followUpStatus: "PARTIAL", liveFinding: "The ambiguous WAT silently widened the menu variant and omitted a snapshot, producing fanout liability, so it failed. The exact-variant WAT reconciled the three vendor amounts and distinct PO counts, but omitted supported ingredients with zero open PO and remains PARTIAL." },
  { id: "WF05", name: "Exact-date Latte economics", prompt: "For Latte - Medium on exactly 22 Jan show net sales and theoretical margin; then repeat for exactly 1 Feb.", primaryObject: "ZIA_QT_02_Menu_Actual_Forecast", dateContract: "business_date equality, one day per question", filterContract: "record_scope = ACTUAL; Latte - Medium; complete recipe cost", aggregationContract: "SUM net sales; SUM theoretical margin", expectedControl: "22 Jan: INR 1,738.61 / INR 1,449.94. 1 Feb: no Month-1 row.", negativeControl: "A broadened Q1 result of INR 41,267.78 / INR 34,341.36 fails.", presentationStatus: "BLOCKED - the no-data follow-up widens the requested date.", sourceStatus: "PASS", conversationStatus: "PASS", followUpStatus: "FAIL", liveFinding: "The 22-Jan WAT passed with exact business_date equality and INR 1,738.61 / INR 1,449.94. The immediate 1-Feb follow-up retained the item but widened the absent day to Q1 2026 and returned INR 41,267.78 / INR 34,341.36, so it failed." },
  { id: "WF06", name: "Provisional expiry today", prompt: "At 22 Jan, show provisional batches expiring that day with total stock, expired batch quantity, usable quantity and UOM.", primaryObject: "ZIA_QT_06_Provisional_Expiry_Only", dateContract: "snapshot_date = expiry_date = 22 Jan", filterContract: "physical EXPIRY-only scope; group by outlet, material and UOM", aggregationContract: "UOM-bound Actual display fields; no cross-UOM numeric total", expectedControl: "Three exact-day batch rows plus the mandatory provisional-synthetic disclosure.", negativeControl: "Calling it actual POSIST expiry or omitting the disclosure fails.", presentationStatus: "BLOCKED - the targeted smoke routed to the helper and returned exactly three UOM-bound rows, but omitted strict disclosure, material and outlet; canonical PARTIAL is unchanged.", sourceStatus: "PASS", conversationStatus: "PARTIAL", followUpStatus: "PASS", liveFinding: "WAT06 routed to ZIA_QT_06 and returned the exact three UOM-bound rows. It still omitted the strict provisional disclosure plus material and outlet context, so it remains PARTIAL and is not presentation-safe." },
  { id: "WF07", name: "Inclusive provisional expiry window", prompt: "From the 25-Jan snapshot, list provisional batches expiring continuously from 25 through 30 Jan inclusive.", primaryObject: "ZIA_QT_06_Provisional_Expiry_Only", dateContract: "snapshot = 25 Jan; expiry_date between 25 and 30 Jan inclusive", filterContract: "Physical EXPIRY-only rows; preserve zero-row dates as explicit no evidence", aggregationContract: "UOM-bound expiry-window display by expiry date, material and unit", expectedControl: "46 rows / 20 materials; the no-row date remains explicit.", negativeControl: "Endpoint-only dates, missing expiry_date or a batch count without quantity fails.", presentationStatus: "BLOCKED - the targeted smoke routed to the helper and honored the inclusive interval, but selected batch count instead of the governed quantity; canonical PARTIAL is unchanged.", sourceStatus: "PASS", conversationStatus: "PARTIAL", followUpStatus: "PASS", liveFinding: "WAT07 routed to ZIA_QT_06 and preserved the continuous inclusive interval. It used batch count rather than the governed UOM-bound expiry-window quantity, so it remains PARTIAL." },
  { id: "WF08", name: "Expected deliveries on 27 January", prompt: "Which physical PO lines are expected on 27 Jan with items, quantities, units and pre-tax ordered value?", primaryObject: "ZIA_QT_09_PO_Delivery_UOM_Safe + ZIA_QT_10_PO_Delivery_Value_By_PO", dateContract: "expected_delivery_date = 27 Jan; no state snapshot", filterContract: "Physical PO line helper for detail; one-row-per-date-and-PO helper for value follow-up", aggregationContract: "Line quantity is non-additive text beside source_uom; line and PO pre-tax values Sum", expectedControl: "10 physical lines / 3 POs, then exactly 3 PO-value rows; the totals reconcile.", negativeControl: "Any state-snapshot join, cross-UOM quantity highlight or missing PO value fails.", presentationStatus: "BLOCKED - the corrected detail helper passed targeted readback, but the indexed retry still bypassed it and generated unsafe cross-UOM aggregates.", sourceStatus: "PASS", conversationStatus: "PARTIAL", followUpStatus: "PARTIAL", liveFinding: "The replacement detail helper exposes ordered_quantity as non-additive text beside source_uom, and its targeted three-field readback passed. The indexed WAT_08_01 retry still routed to RAW_Enterprise_Purchase_Order and generated a cross-UOM grand total and Key Highlights, so the primary remains PARTIAL; the grouped follow-up was not promoted." },
  { id: "WF09", name: "Latest Red inventory action", prompt: "At the latest valid complete snapshot, list every Red inventory material with stock, next-day and seven-day requirement, shortage, exposure and UOM.", primaryObject: "ZIA_QT_07_Current_Red_Inventory", dateContract: "Physically latest-valid complete Red INVENTORY scope", filterContract: "No conversational domain/color/completeness widening is possible", aggregationContract: "UOM-bound quantity displays; SUM monetary_exposure", expectedControl: "Six current rows across three outlets and three UOMs; exposure reconciles.", negativeControl: "A one-item answer, wrong horizon, narrative/table mismatch or cross-UOM total fails.", presentationStatus: "BLOCKED - the targeted smoke functionally passed, but no schema-v1 receipt was captured and the canonical PARTIAL ledger is unchanged.", sourceStatus: "PASS", conversationStatus: "PARTIAL", followUpStatus: "PASS", liveFinding: "WAT09 routed to ZIA_QT_07, returned all six governed rows with UOM-safe quantities, and kept exposure as the only additive measure. This is a functional smoke pass without a schema-v1 receipt, not a canonical pass; full reruns remain held." },
  { id: "WF10", name: "Top Desserts by continuous-range margin", prompt: "From 15 through 25 Jan inclusive, rank the top five Desserts by source net margin, then ask each recipe separately.", primaryObject: "ZIA_QT_02_Menu_Actual_Forecast + ZIA_QT_03_Recipe_Canonical", dateContract: "business_date >= 15 Jan AND <= 25 Jan; recipe has no date", filterContract: "record_scope = ACTUAL; category = Desserts; exact returned item per recipe question", aggregationContract: "SUM source net margin across every day; top 5 descending", expectedControl: "6,356.87 / 5,910.59 / 5,342.88 / 3,165.55 / 3,156.98.", negativeControl: "The endpoint-only 1,119.28 / 907.93 / 848.55 / 772.28 / 697.21 ranking fails.", presentationStatus: "BLOCKED - range/ranking semantics fail and recipe output adds a mixed-UOM total.", sourceStatus: "PASS", conversationStatus: "FAIL", followUpStatus: "PARTIAL", liveFinding: "The ranking WAT reproduced both endpoint-only date selection and daily-row ranking, so it failed. The recipe WAT selected the exact item and canonical helper, but display rounding and an invalid mixed-UOM grand total leave it PARTIAL." },
  { id: "WF11", name: "Open vendors on 14 January", prompt: "As of 14 Jan count vendors with open POs and list each vendor, materials, distinct PO count and liability.", primaryObject: "ZIA_QT_08_Positive_Open_Vendor_Material", dateContract: "snapshot_date = 14 Jan", filterContract: "Strictly positive and source-complete procurement is enforced physically", aggregationContract: "DISTINCTCOUNT vendor_code; item liability Sum; repeated vendor controls display-only; SUM anchor-row *_safe measures", expectedControl: "All 19 vendor-material rows, eight vendors and both anchor-row-safe totals reconcile.", negativeControl: "A count without names/materials, a non-strict scope, additive display fields or a safe value repeated beyond one anchor row per vendor fails.", presentationStatus: "BLOCKED - FUNCTIONAL_SMOKE_PASS_NO_SCHEMA_V1_RECEIPT; the canonical primary/follow-up ledger and presentation gate are unchanged.", sourceStatus: "PASS", conversationStatus: "PARTIAL", followUpStatus: "PARTIAL", liveFinding: "FUNCTIONAL_SMOKE_PASS_NO_SCHEMA_V1_RECEIPT: WAT11 routed to QT08 v3, returned all 19 vendor-material rows across eight vendors, and reconciled both safe totals. Repeated vendor count/liability remained display text, while the two additive safe measures occurred only on each vendor's deterministic minimum-item anchor row. This is not a canonical PASS." },
];

export const ziaSemanticDeployment = {
  artifact: "25_MINIMAL_LIVE_SEMANTIC_DEPLOYMENT.csv",
  status: "BASE_67_READ_BACK_FIVE_CAUSAL_HELPERS_TARGETED_SMOKES_COMPLETE_FUNCTIONAL_ONLY_GATE_UNCHANGED_FULL_RERUNS_HELD",
  actionCount: 67,
  baseSemanticRowCount: 67,
  actionBreakdown: [
    { label: "Apply base semantic contract", count: 1, detail: "The ordered semantic contract is the comparison baseline; standard descriptions remain uncertified." },
    { label: "Include curated objects", count: 8, detail: "Seven helper Query Tables plus the physical purchase-order flow were read back in scope." },
    { label: "Exclude competing objects", count: 9, detail: "Broad, duplicate and staging objects remain outside the meeting-demo Ask Zia scope; exclusion readback matched." },
    { label: "Set missing field metadata", count: 42, detail: "Synonyms, priorities and supported Default Functions were checked; descriptions are not certified by the available readback." },
    { label: "Hide unsafe fields", count: 6, detail: "Remove competing dates, amounts and row-ratio shortcuts from conversational routing." },
    { label: "Create governed formula", count: 1, detail: "The ratio-of-sums weighted theoretical gross-margin formula exists, is included and is semantically verified." },
  ],
  deploymentSteps: [
    "Keep ZLD009 and the corrected ZLD037 ACTUAL / Full Date setting unchanged unless a new governed contract is approved.",
    "Treat the aggregate formula as verified; do not recreate or rewrite it without a causal failure.",
    "Keep standard descriptions uncertified until a supported description readback proves them directly.",
    "Do not repeat the WF08 or WF04 smoke without a new causal semantic or presentation change.",
    "After any approved causal change, save, close, reopen and read back the exact setting before testing.",
    "Run the affected WAT rows first; rerun the six-tier ladder only when the WAT gate materially improves.",
  ],
  postPlanAdditions: {
    helperCount: 5,
    status: "TARGETED_SMOKES_COMPLETE_QT08_V3_AND_QT09_REPLACEMENT_READ_BACK_FUNCTIONAL_ONLY",
    scope: "Expiry-only, current Red inventory, positive-open vendor/material v3, UOM-safe PO detail and one-row-per-PO delivery value",
    gate: "WAT09 and WAT11 functionally passed without schema-v1 receipts; WAT06 and WAT07 remain partial; WAT08 produced no improvement. Canonical ledgers are unchanged and full reruns remain held.",
  },
  liveEvidence: "The original 67-action semantic baseline, ZLD009 and corrected ZLD037 remain read back; the aggregate formula is verified and standard descriptions remain uncertified. Five additive purpose-separated helpers were created or edited in place. Targeted smokes are complete: WAT06 routed correctly but omitted required disclosure/context; WAT07 routed correctly but chose batch count; WAT08 still selected the raw PO source and produced unsafe cross-UOM output; WAT09 functionally passed without a schema-v1 receipt; and QT08 v3 made repeated vendor controls display text plus anchor-row-safe measures before WAT11 functionally passed without a schema-v1 receipt. Canonical WAT 22 remains 7 PASS / 9 PARTIAL / 6 FAIL, the ladder remains 7 PASS / 9 PARTIAL / 50 FAIL, and full reruns remain held.",
} as const;

export const ziaNaturalLanguageLadder = {
  artifact: "26_NATURAL_LANGUAGE_ACCEPTANCE_LADDER.csv",
  status: "7_PASS_9_PARTIAL_50_FAIL_PRESENTATION_BLOCKED",
  workflowCount: 11,
  testCount: 66,
  passCount: 7,
  partialCount: 9,
  failCount: 50,
  presentationReadyWorkflowCount: 0,
  tiers: [
    { id: "A", label: "Plain business gate", count: 11, rule: "Ordinary business wording or the required clarification; no technical-object hint." },
    { id: "B", label: "Atomic companion", count: 11, rule: "One safe detail, forecast, recipe, no-data or measure-clarity question in a fresh conversation." },
    { id: "C", label: "Diagnostic only", count: 11, rule: "Explicit routing diagnosis. A pass here never proves natural-language readiness." },
    { id: "D", label: "Colloquial paraphrase", count: 11, rule: "Everyday phrasing such as 'what goes into' or 'supposed to land'." },
    { id: "E", label: "Context follow-up", count: 11, rule: "Run immediately after its parent; date, vendor, item, domain and measure context must persist." },
    { id: "F", label: "Governed negative control", count: 11, rule: "Unsafe wording must be rejected, clarified or answered with the governed no-data behavior." },
  ],
  acceptanceRule: "A workflow is presentation-ready only when A, B, D and E pass, F fails safely as designed, and the visible answer, narrative, Report Information and numerical control all agree. Tier C is diagnostic only.",
  currentLedger: "7 PASS / 9 PARTIAL / 50 FAIL",
} as const;

export const ziaPresentationFlows = [
  { title: "Procurement truth", route: "ZIA_01 strict overdue + ZIA_QT_08 positive-open vendor/material v3 + ZIA_QT_09/10 delivery helpers", steps: ["Keep the strict-overdue workflow on its governed report fallback.", "Treat QT08 v3 WAT11 as FUNCTIONAL_SMOKE_PASS_NO_SCHEMA_V1_RECEIPT, not a canonical pass.", "Do not present the UOM-safe PO-line helper conversationally: WAT08 bypassed it and produced unsafe cross-UOM output."], control: "QT08 returned 19 vendor-material rows across eight vendors with safe totals; delivery controls remain source-only", fallback: "RPT_V2_P08_Delivery_Breach_Action_Top10 plus governed procurement reports" },
  { title: "Sales to demand", route: "ZIA_QT_02_Menu_Actual_Forecast", steps: ["Ask January Coffee Classics actual economics.", "Start a separate forecast question.", "Repeat Connaught, Latte - Medium, 21-Jan snapshot and 22-Jan target."], control: "INR 207,489.63 / 84.02%; then 2.333333 units", fallback: "Governed QT04/QT01A report evidence" },
  { title: "Recipe to vendor", route: "ZIA_QT_03_Recipe_Canonical -> ZIA_QT_04_Menu_Vendor_Dependency", steps: ["Ask one exact recipe variant.", "Use its ingredient set with one 31-Jan snapshot.", "Show no-open-PO ingredients rather than dropping them."], control: "8 recipe rows plus three vendor groups", fallback: "Two governed atomic tables" },
  { title: "Expiry evidence", route: "ZIA_QT_06_Provisional_Expiry_Only", steps: ["Require the physical provisional-synthetic disclosure field.", "Keep WAT06 PARTIAL because disclosure/material/outlet were omitted.", "Keep WAT07 PARTIAL because the inclusive answer selected batch count instead of governed quantity."], control: "Exact-day and inclusive-window source controls reconcile; conversational controls do not", fallback: "RPT_V2_R08A provisional expiry table" },
  { title: "Latest inventory action", route: "ZIA_QT_07_Current_Red_Inventory", steps: ["Use the physically current complete Red inventory helper.", "Keep all quantities UOM-bound and sum only monetary exposure.", "Treat the six-row WAT09 result as a functional smoke without a schema-v1 receipt, not a canonical pass."], control: "Six current Red rows and governed exposure", fallback: "RPT_V2_R08B inventory shortage action table" },
  { title: "Menu ranking to recipe", route: "ZIA_QT_02_Menu_Actual_Forecast -> ZIA_QT_03_Recipe_Canonical", steps: ["Prove the 15-25 Jan inclusive range.", "Rank five Desserts by source net margin.", "Ask one atomic recipe question per returned item."], control: "Five exact margin values; then governed recipe rows", fallback: "RPT_V2_S07B plus recipe map" },
] as const;

export interface WeatherObject {
  name: string;
  viewId: string;
  status: string;
  rows: string;
  grain: string;
  purpose: string;
  dependencies: string[];
  keyFields: string[];
  steps: string[];
}

export const weatherLandingTables: WeatherObject[] = [
  { name: "RAW_Weather_Realized_Daily", viewId: "PRIVATE_CLIENT_BINDING", status: "EVALUATION_ONLY", rows: "270 rows | 1 Jan-31 Mar 2026", grain: "weather_date x outlet_code", purpose: "Historical Forecast API model-grid past-weather proxy for descriptive joins.", dependencies: ["Open-Meteo Historical Forecast API", "Local normalizer"], keyFields: ["weather_date", "outlet_code", "outlet_name", "temperature_mean_c", "relative_humidity_mean_pct", "precipitation_sum_mm", "coordinate_status", "license_scope", "attribution_text"], steps: ["Fetch in Asia/Kolkata through the local normalizer.", "Validate one row per date and outlet code.", "Import Update/Add into the existing table; never recreate it.", "Retain EVALUATION_ONLY, DEMO_APPROXIMATE and attribution fields on every row."] },
  { name: "RAW_Weather_Forecast_Daily", viewId: "PRIVATE_CLIENT_BINDING", status: "EVALUATION_ONLY", rows: "24 rows | issued 6 Aug; targets 6-13 Aug 2026", grain: "forecast_as_of_date x weather_date x outlet_code", purpose: "Retain the current issued forecast vintage, including D+0, before the reporting query selects D+1-D+7.", dependencies: ["Open-Meteo Forecast API", "Local normalizer"], keyFields: ["forecast_as_of_date", "weather_date", "lead_days", "outlet_code", "outlet_name", "temperature_mean_c", "precipitation_sum_mm", "fetched_at_utc", "weather_data_status"], steps: ["Fetch the current Forecast API response and stamp fetched_at_utc.", "Retain every forecast vintage in the raw table.", "Validate the composite key before Update/Add.", "Use QT_09, not the raw table, for the latest D+1-D+7 report surface."] },
  { name: "CTL_Weather_Parameters", viewId: "PRIVATE_CLIENT_BINDING", status: "PROVISIONAL_DEMO_REQUIRES_ABNAH_APPROVAL", rows: "1 effective-dated row", grain: "parameter_set_id x effective date range", purpose: "Govern provisional cool/hot and rain/heavy-rain bands without hard-coding report formulas.", dependencies: ["ABNAH business approval pending"], keyFields: ["parameter_set_id", "effective_from", "effective_to", "cool_upper_c", "hot_lower_c", "rain_threshold_mm", "heavy_rain_threshold_mm", "parameter_status"], steps: ["Open the exact control row; do not edit report-local thresholds.", "Change a band only after business approval.", "Refresh QT_07, QT_08 and QT_09 in order.", "Reconcile band members before publishing any updated weather report."] },
];

export const weatherQueryTables: WeatherObject[] = [
  { name: "QT_07_Weather_Sales_Daily", viewId: "PRIVATE_CLIENT_BINDING", status: "LIVE_DEMO_EXTENSION", rows: "4,855 rows | 31 dates | 3 outlets | 110 items", grain: "weather_date x outlet_name x menu_item_code", purpose: "Join one daily menu-economics row to one provider weather row for descriptive association.", dependencies: ["QT_04_Menu_Profitability", "RAW_Weather_Realized_Daily", "CTL_Weather_Parameters"], keyFields: ["weather_date", "outlet_name", "menu_item_code", "menu_item_name", "sold_menu_qty", "net_sales_value", "temperature_mean_c", "relative_humidity_mean_pct", "precipitation_sum_mm", "temperature_band", "precipitation_band", "weather_analysis_scope"], steps: ["Create or verify QT_07_Weather_Sales_Daily with the exact name.", "Join weather_date to sales_date and exact outlet_name for this demo only.", "Confirm all 4,855 Month-1 rows match and retain provisional disclosures.", "Use this physical-date table when a weather report must respond to a Reporting Period filter."] },
  { name: "QT_08_Weather_Menu_Sensitivity", viewId: "PRIVATE_CLIENT_BINDING", status: "LIVE_DEMO_EXTENSION", rows: "855 rows | 3 outlets | 110 items | 3 precipitation bands", grain: "outlet_name x menu_item_code x temperature_band x precipitation_band", purpose: "Summarize active-selling-day menu demand and economics by governed weather band.", dependencies: ["QT_07_Weather_Sales_Daily"], keyFields: ["outlet_name", "menu_item_code", "menu_item_name", "category_name", "temperature_band", "precipitation_band", "active_days", "average_active_selling_day_qty", "average_active_selling_day_net_sales_value", "weighted_menu_gross_margin_pct", "weather_analysis_scope"], steps: ["Create or verify QT_08_Weather_Menu_Sensitivity.", "Group only at outlet, item, temperature band and precipitation band.", "Use active-selling-day averages; zero-sale item-days are absent from QT04.", "Keep these aggregated live views unmapped from the core Reporting Period unless a physical-date QT07 companion is built."] },
  { name: "QT_09_Latest_Weather_Outlook", viewId: "PRIVATE_CLIENT_BINDING", status: "LIVE_DEMO_EXTENSION", rows: "21 rows | 3 outlets | D+1-D+7", grain: "latest forecast_as_of_date x weather_date x outlet_code", purpose: "Select the latest retained forecast vintage and expose only the next seven target days.", dependencies: ["RAW_Weather_Forecast_Daily", "CTL_Weather_Parameters"], keyFields: ["forecast_as_of_date", "weather_date", "lead_days", "outlet_code", "outlet_name", "temperature_min_c", "temperature_max_c", "relative_humidity_mean_pct", "precipitation_sum_mm", "temperature_band", "precipitation_band", "weather_outlook_scope"], steps: ["Create or verify QT_09_Latest_Weather_Outlook.", "Select the latest forecast_as_of_date per outlet and target date.", "Restrict lead_days to 1 through 7; keep weather_date as the future target date.", "Use a dedicated Weather Forecast Run filter; never map the January core Snapshot As Of control to this August evaluation outlook."] },
];

export interface WeatherReportGuide {
  name: string;
  viewId: string;
  base: string;
  visual: string;
  question: string;
  shelves: string[];
  fixed: string[];
  mappings: Record<string, string>;
  intentionallyUnmapped: string[];
  acceptance: string;
  disclosure: string;
  steps: string[];
}

export const weatherReports: WeatherReportGuide[] = [
  { name: "RPT_WX01_Daily_Sales_Weather_Context_DEMO", viewId: "PRIVATE_CLIENT_BINDING", base: "QT_08_Weather_Menu_Sensitivity", visual: "Vertical bar", question: "How did average active-selling-day net sales differ across the provisional precipitation bands?", shelves: ["X: precipitation_band - Actual", "Y: average_active_selling_day_net_sales_value - Average", "Color: none"], fixed: [], mappings: { Outlet: "QT_08_Weather_Menu_Sensitivity.outlet_name", "Menu Item": "QT_08_Weather_Menu_Sensitivity.menu_item_name", "Menu Category": "QT_08_Weather_Menu_Sensitivity.category_name" }, intentionallyUnmapped: ["Reporting Period", "Snapshot As Of", "Raw Material", "Material Category", "Canonical UOM", "Risk Domain", "Vendor"], acceptance: "Three concise bars (DRY, HEAVY_RAIN and RAIN) in the verified export.", disclosure: "Evaluation-only provider model-grid association; not causal and not outlet-station observation.", steps: ["Open the existing report by its exact name and verify the base table.", "Set the shelves exactly as listed and keep one series.", "Map only Outlet, Menu Item and Menu Category to the exact QT08 columns.", "Leave Reporting Period unmapped because this live QT08 object is already aggregated across its loaded window.", "Export once and verify three readable bars plus the visible evaluation disclosure before dashboard use."] },
  { name: "RPT_WX02_Top_Menu_Demand_Weather_Sensitivity_DEMO", viewId: "PRIVATE_CLIENT_BINDING", base: "QT_08_Weather_Menu_Sensitivity", visual: "Vertical bar", question: "Which menu items had the highest average quantity on represented active selling days?", shelves: ["X: menu_item_name - Actual", "Y: average_active_selling_day_qty - Average", "Top/Bottom: Top 10 descending by the displayed measure"], fixed: [], mappings: { Outlet: "QT_08_Weather_Menu_Sensitivity.outlet_name", "Menu Item": "QT_08_Weather_Menu_Sensitivity.menu_item_name", "Menu Category": "QT_08_Weather_Menu_Sensitivity.category_name" }, intentionallyUnmapped: ["Reporting Period", "Snapshot As Of", "Raw Material", "Material Category", "Canonical UOM", "Risk Domain", "Vendor"], acceptance: "Ten readable ranked bars in the verified export.", disclosure: "Active-selling-day association only; zero-sales item/dates are absent.", steps: ["Open the exact saved report and verify QT_08_Weather_Menu_Sensitivity as the base.", "Use menu_item_name and the average active-selling-day quantity exactly as shown.", "Apply Top 10 descending and keep the chart single-series.", "Map only the three compatible menu/outlet controls; do not force a core date filter onto the aggregated rows.", "Verify labels remain readable at dashboard width and retain the active-selling-day disclosure."] },
  { name: "RPT_WX03_D7_Rainfall_Outlook_DEMO", viewId: "PRIVATE_CLIENT_BINDING", base: "QT_09_Latest_Weather_Outlook", visual: "Line chart", question: "What total provider-forecast rainfall is currently shown across D+1-D+7?", shelves: ["X: weather_date - Date", "Y: precipitation_sum_mm - Sum", "Sort: weather_date ascending"], fixed: ["lead_days between 1 and 7 in QT09"], mappings: { Outlet: "QT_09_Latest_Weather_Outlook.outlet_name", "Weather Forecast Run": "QT_09_Latest_Weather_Outlook.forecast_as_of_date" }, intentionallyUnmapped: ["Reporting Period", "Snapshot As Of", "Menu Item", "Menu Category", "Raw Material", "Material Category", "Canonical UOM", "Risk Domain", "Vendor"], acceptance: "Seven ordered points labelled 7-13 Aug 2026 in the verified export.", disclosure: "Current provider forecast, not realised weather and not a demand forecast.", steps: ["Open the exact saved report and verify QT_09_Latest_Weather_Outlook as the base.", "Use weather_date on the X-axis and SUM precipitation on the Y-axis.", "Map Outlet to outlet_name; add a separate Weather Forecast Run control only if forecast-vintage selection is needed.", "Never map the core January Snapshot As Of filter to this August evaluation outlook.", "Confirm seven chronological points and retain provider attribution before dashboard use."] },
  { name: "RPT_WX04_Menu_Demand_Weather_Matrix_DEMO", viewId: "PRIVATE_CLIENT_BINDING", base: "QT_08_Weather_Menu_Sensitivity", visual: "Pivot", question: "How does average active-selling-day menu quantity compare across precipitation bands?", shelves: ["Rows: menu_item_name", "Columns: precipitation_band", "Data: average_active_selling_day_qty - Average", "Rank: top items; ties may extend the visible row count"], fixed: [], mappings: { Outlet: "QT_08_Weather_Menu_Sensitivity.outlet_name", "Menu Item": "QT_08_Weather_Menu_Sensitivity.menu_item_name", "Menu Category": "QT_08_Weather_Menu_Sensitivity.category_name" }, intentionallyUnmapped: ["Reporting Period", "Snapshot As Of", "Raw Material", "Material Category", "Canonical UOM", "Risk Domain", "Vendor"], acceptance: "One-page readable pivot with HEAVY_RAIN and RAIN columns; no horizontal scroll in export.", disclosure: "Descriptive association; provisional bands, approximate coordinates and active-selling-day denominator.", steps: ["Open the exact saved pivot and verify the base table.", "Place menu_item_name on Rows, precipitation_band on Columns and Average quantity in Data.", "Keep only the ranked item set needed for a one-page export; allow ties rather than forcing a misleading cut.", "Map only Outlet, Menu Item and Menu Category; leave core date/state controls unmapped.", "Export to PDF and confirm one readable page plus the mandatory evaluation disclosure."] },
];

export const weatherGovernanceGates = [
  { label: "Client coordinates", status: "BLOCKED", detail: "Current Connaught Place, Hauz Khas and Saket coordinates are DEMO_APPROXIMATE neighbourhood centroids." },
  { label: "Commercial route", status: "BLOCKED", detail: "Production requires an approved Open-Meteo customer endpoint or separately approved self-hosting." },
  { label: "Historical association", status: "LIVE DEMO", detail: "14,576 local daily menu/weather joins matched with zero unmatched rows; live Month-1 QT07 has 4,855 rows." },
  { label: "Weather-aware AutoML", status: "DESIGNED", detail: "Requires retained as-issued weather vintages, longer actual history, chronological validation and business acceptance." },
] as const;
