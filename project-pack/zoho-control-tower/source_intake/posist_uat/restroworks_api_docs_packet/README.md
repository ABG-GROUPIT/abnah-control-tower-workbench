# Restroworks API Docs Packet

Source reviewed: `https://api.restroworks.com/#intro`

Packet date: 2026-07-10

This packet summarizes the public Restroworks API reference exposed as a Postman documenter collection. It is a Codex working packet for ABNAH model planning, not a production connector and not a copy of the full API documentation.

## Extraction Summary

Parsed structure:

| Area | Count | Current relevance |
|---|---:|---|
| Data Integration | 2 | Sales, invoices, bill/KOT detail. |
| Online Order | 8 | Menu sync, out-of-stock status, online order workflow. |
| Delivery | 8 | Customer delivery workflow, low current priority. |
| Loyalty Integration | 7 | CRM/loyalty workflow, low current priority. |
| Cloud POS | 3 | Menu/order push workflow, secondary. |
| Stock | 2 | High-value phase-1 inventory/procurement source. |
| FAQ | 2 | Documentation only. |
| Checklist for Production | 2 | Implementation checklist only. |

Important caveat: the public docs use sample URLs and placeholders. ABNAH UAT must confirm the real base URL, enabled endpoints, authentication, pagination, rate limits, and response shape.

## Initial Usefulness Verdict

Useful for ABNAH, especially for phase 1, because the docs expose two stock/inventory endpoints:

1. `GET /api/v1/pos/fetch_Inventory_data`
2. `GET /api/v1/pos/get_indents`

These are directly relevant to Inventory and Consumption Intelligence plus Vendor and Procurement Analytics.

The data integration sales endpoints are useful for phase 2 and for consumption modelling:

1. `GET /api/v1/pos/bills`
2. `GET /api/v1/pos/get_all_invoices`

The online-order/menu endpoints are useful as master/availability context, but they should not drive phase-1 procurement unless ABNAH specifically wants aggregator availability intelligence.

Delivery and loyalty endpoints are low priority for the current ABNAH dashboard focus.

## Highest-Value Endpoints

| Priority | Endpoint | Why it matters |
|---|---|---|
| P0 | `GET /api/v1/pos/fetch_Inventory_data` | Exposes inventory transactions, PO/entity mode, vendors, items, quantities, unit conversions, taxes, invoice/PO references, stock entry, wastage, physical stock, vendor return, opening stock, and stock sale transaction types. |
| P0 | `GET /api/v1/pos/get_indents` | Exposes internal indent/requisition movement between supplier and receiver deployments/stores, item quantities, status, supply dates, taxes, and store codes. |
| P1 | `GET /api/v1/pos/bills` | Exposes bill/KOT item lines, quantities, categories, discounts, taxes, payments, close time, bill number, and customer/tab context. Useful for sales and theoretical consumption. |
| P1 | `GET /api/v1/online_order/menu` and standard menu response | Exposes menu item, category, taxes, variants, active status, in-stock/availability, nutrition/allergen/shelf-life fields in the newer menu structure. Useful for menu dimension enrichment. |
| P1 | `GET /api/v1/online_order/out_of_stock_items*` | Exposes item availability/out-of-stock state. Useful as a supplemental stockout signal, not a replacement for inventory facts. |

## Questions To Confirm With UAT/API Access

1. What is ABNAH's production base URL and authentication flow?
2. Are these public docs exactly the API version enabled for ABNAH?
3. Does `fetch_Inventory_data` return all inventory entities for ABNAH, or only selected integrations?
4. For `entity=po`, does the endpoint include full PO lifecycle status and vendor linkage?
5. Is there a GRN/receipt-specific transaction type beyond `stock_entry`, or does stock entry represent receipt/GRN?
6. Does `physical_stock` represent periodic counts, daily closing, or both?
7. Does `stock_sale` represent actual raw-material depletion/consumption or a different stock-out transaction?
8. Are `stock_transfer`, `finished_entry`, and `semi_entry` available now or still upcoming?
9. Are recipe/BOM APIs available outside this public collection?
10. Are vendor master, item master, unit master, store master, and recipe master available through separate APIs?

## Files In This Packet

| File | Purpose |
|---|---|
| `endpoint_inventory.csv` | Endpoint-level inventory with ABNAH usefulness notes. |
| `model_mapping_seed.csv` | First-pass mapping from API endpoints/transaction modes to current or candidate ABNAH model objects. |

## Working Rule

Treat this packet as evidence that Restroworks can likely support the phase-1 dashboard direction. Do not change SQL model objects until ABNAH UAT confirms endpoint access, sample responses, field consistency, pagination, date filtering, and outlet/vendor/item identifiers.
