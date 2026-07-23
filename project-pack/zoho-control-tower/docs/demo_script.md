# Demo Script

## Goal

Show that ABNAH-style operational reports can be generated synthetically, loaded into a POSIST-like Neon backend, exposed through FastAPI CSV feeds, and modeled in Zoho Analytics.

Do not claim this is production forecasting or production stockout prediction.

Do not claim Zoho is already connected unless the main-data runbook has been completed manually:

- `docs/ngrok_fastapi_zoho_main_data_test_runbook.md`

## Dashboard Story Structure

Dashboard 1 is cross-outlet:

- Executive / Outlet Comparison / Outlet Health
- Compares Connaught Place, Hauz Khas, and Saket against each other.
- Shows outlet ranking, outlet health, outlet sales trend, inventory pressure, event exposure, and overall performance.

Dashboards 2 through 5 are outlet-specific modules:

- Sales and Menu Intelligence
- Vendor and Procurement Analytics
- Inventory and Consumption Intelligence
- Calendar, Event, and Competitor Intelligence

Use one outlet at a time for dashboards 2 through 5. The preferred Zoho pattern is one shared outlet-aware model with locked outlet dashboard filters or duplicated outlet pages such as:

- `Sales_Menu_OUT001`
- `Sales_Menu_OUT002`
- `Sales_Menu_OUT003`

## Pre-Demo Setup

1. Ensure `.env` contains `DATABASE_URL`.
2. Set `FEED_TOKEN` if using token-protected feed URLs.
3. Run:
   ```powershell
   python manage_demo.py reset-to-month 1
   ```
4. Start FastAPI:
   ```powershell
   .\scripts\run_api.bat
   ```
5. Expose FastAPI publicly if Zoho cloud needs to import it.
6. Use `docs/ngrok_fastapi_zoho_main_data_test_runbook.md` to prove `RAW_Sales_Report_OUT001` refresh behavior before full modeling.
7. Open Zoho Analytics workspace with imported feed tables and outlet-aware query tables, if those have been manually built.

## Flow

### 1. Explain Architecture

Use this phrasing:

```text
Synthetic ABNAH-style reports are loaded into Neon PostgreSQL as raw report tables.
FastAPI exposes those raw reports as CSV feeds.
Zoho imports the feeds and does the modeling/dashboard work.
The model is outlet-aware: one executive dashboard compares outlets, and the remaining modules are filtered to one outlet at a time.
```

### 2. Month 1 Baseline

Show:

- FastAPI outlet sales row counts for Month 1: OUT001 `1,529`, OUT002 `1,595`, OUT003 `1,731`; `STD_Sales_Report` union total `4,855`.
- Executive outlet comparison across Connaught Place, Hauz Khas, and Saket.
- Selected-outlet Sales/Menu module for Connaught Place.
- Optional switch to Hauz Khas or Saket using the same dashboard template/filter.

Suggested narrative:

- Connaught Place: weekday coffee/lunch pattern.
- Hauz Khas: youth/social demand.
- Saket Premium: weekend dessert/premium beverage behavior.

### 3. Month 2 Refresh

Run:

```powershell
python manage_demo.py load-month 2
```

Show:

- FastAPI outlet sales row counts increased to OUT001 `3,003`, OUT002 `3,088`, OUT003 `3,325`; `STD_Sales_Report` union total `9,416`.
- Zoho manual refresh/re-fetch of the same Web URL source.
- Executive dashboard updated across all outlets.
- Outlet-specific module for Connaught Place showing corporate event lift.
- Outlet-specific module for Hauz Khas showing student/social event lift.
- Outlet-specific procurement module showing vendor spend, PO status, and pending/partial POs for the selected outlet.

### 4. Month 3 Refresh

Run:

```powershell
python manage_demo.py load-month 3
```

Show:

- FastAPI outlet sales row counts increased to OUT001 `4,623`, OUT002 `4,747`, OUT003 `5,206`; `STD_Sales_Report` union total `14,576`.
- Zoho manual refresh/re-fetch.
- Executive dashboard updated across outlets.
- Saket outlet-specific module showing weekend/leisure dessert strength.
- Connaught Place outlet-specific module showing holiday softness but corporate spikes.
- Hauz Khas outlet-specific module showing cold beverage/wrap overperformance.
- Calendar/competitor module filtered to the selected outlet or market area.
- Inventory module showing selected-outlet inventory pressure after high-demand dates.

### 5. Reset Demo State

For repeat testing:

```powershell
python manage_demo.py reset-to-month 1
```

or:

```powershell
python manage_demo.py reset-to-month 2
```

After backend reset, Zoho does not change automatically. Refresh/re-fetch the Zoho RAW feed tables and confirm row counts return to the expected backend state.

## Caveats To State

- Data is synthetic.
- Neon simulates a POSIST-like backend; it is not claimed as the confirmed production POSIST architecture.
- FastAPI/ngrok/Zoho connection must be manually tested; ngrok is not built into the repo.
- Zoho direct PostgreSQL connector is only a fallback/test path.
- Competitor pricing is context, not causation.
- Stock risk is approximate and needs reorder levels, lead times, opening stock, transfers, and wastage for production prediction.
- Calendar/event intelligence is a foundation for forecasting, not full forecasting by itself.
- Dashboards 2 through 5 must not combine all outlets unless grouped or filtered by outlet.
