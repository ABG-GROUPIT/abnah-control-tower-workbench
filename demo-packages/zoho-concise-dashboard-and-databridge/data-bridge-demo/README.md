# DataBridge Weekly Refresh Demonstration

This demonstration uses three synthetic report families:

1. Enterprise Entry
2. Closing Stock
3. Daily Sales

It shows a safe cumulative refresh without altering the production raw tables.

## Important Import Choice

Use **Delete existing records and add** for this demonstration.

Each cumulative workbook contains the complete history available at that step.
Replacing the file and re-fetching therefore produces:

| Step | Included dates | Expected rows by sheet |
|---|---|---|
| 1 | Week 1 | Entry 6, Closing 5, Daily Sales 7 |
| 2 | Weeks 1-2 | Entry 12, Closing 10, Daily Sales 14 |
| 3 | Weeks 1-3 | Entry 18, Closing 15, Daily Sales 21 |

Do not use **Add records at end** with the cumulative workbook. Re-fetching a
cumulative file in append mode would duplicate the older weeks.

## Files

### Weekly delta workbooks

Each file contains only one new week:

- `weekly-deltas/week_01/ABNAH_DataBridge_Weekly_Delta.xlsx`
- `weekly-deltas/week_02/ABNAH_DataBridge_Weekly_Delta.xlsx`
- `weekly-deltas/week_03/ABNAH_DataBridge_Weekly_Delta.xlsx`

### Cumulative refresh workbooks

Each folder contains the same stable filename:

- `cumulative-refresh/step_01_week_01/ABNAH_DataBridge_Current.xlsx`
- `cumulative-refresh/step_02_weeks_01_02/ABNAH_DataBridge_Current.xlsx`
- `cumulative-refresh/step_03_weeks_01_03/ABNAH_DataBridge_Current.xlsx`

### Live drop

`live-drop/ABNAH_DataBridge_Current.xlsx` is the file DataBridge should watch.
It starts as Step 1.

## Sheet Contract

Every workbook has exactly three sheets:

| Sheet | Grain | Schema status |
|---|---|---|
| `Enterprise Entry` | One received item line | Matches the captured 35-column POSIST-style entry schema |
| `Closing Stock` | One item at a weekly closing checkpoint | Matches the captured 15-column POSIST-style closing schema |
| `Daily Sales` | One daily session summary | Bridge-normalized from the captured report fields |

`Daily Sales` includes three ingestion provenance fields that are not claimed as
untouched POSIST export columns:

- `Source Row ID`
- `Deployment`
- `Business Date`

They make weekly refresh, deduplication, and date filtering demonstrable.

## One-Time Zoho Setup

Use a separate demonstration workspace or three new demonstration tables.

1. Install and start Zoho DataBridge on the machine containing `live-drop`.
2. In Zoho Analytics, click **Create** > **New Table / Import Data**.
3. Click **Files & Feeds** > **Local File**.
4. Set **File Type** to **Excel**.
5. Choose the DataBridge installation that can access the file.
6. Paste the full path to `live-drop/ABNAH_DataBridge_Current.xlsx`.
7. Select all three sheets.
8. Confirm **First row contains column names** is **Yes**.
9. Confirm date columns are Date and numeric columns are Number/Currency.
10. Import into three tables:

| Sheet | Zoho table name |
|---|---|
| Enterprise Entry | `DEMO_DB_RAW_Enterprise_Entry` |
| Closing Stock | `DEMO_DB_RAW_Closing_Stock` |
| Daily Sales | `DEMO_DB_RAW_Daily_Sales` |

11. In the data-source import settings, choose **Delete existing records and
   add**.
12. Keep the file path and filename unchanged.

No lookup is needed for this refresh demonstration.

## Live Demonstration

### Step 1: Week 1

The `live-drop` file initially contains Week 1.

1. Run **Sync Now** or **Re-fetch Data**.
2. Open each table.
3. Confirm row counts are `6`, `5`, and `7`.

### Step 2: Weeks 1-2

1. Close the live workbook if it is open in Excel.
2. Replace the contents of `live-drop` with the file from
   `cumulative-refresh/step_02_weeks_01_02`.
3. Keep the filename `ABNAH_DataBridge_Current.xlsx`.
4. Run **Sync Now**.
5. Confirm row counts become `12`, `10`, and `14`.
6. Filter Business/stock dates to show both weeks.

### Step 3: Weeks 1-3

Repeat using
`cumulative-refresh/step_03_weeks_01_03/ABNAH_DataBridge_Current.xlsx`.
Expected counts are `18`, `15`, and `21`.

## What the Demonstration Proves

- A stable local file path can feed a repeatable DataBridge import.
- The same three Zoho tables can be refreshed without deleting/recreating them.
- Existing reports built on those tables remain attached.
- The cumulative replacement method avoids duplicates and missing historical
  rows.
- A production process can later replace synthetic workbook generation with
  validated POSIST exports.

## What It Does Not Prove

- It does not validate a scheduled POSIST API feed.
- It does not make the synthetic values production truth.
- It does not prove expiry, outlet-master, or vendor-master availability.
- It does not change the current 38-table model.

## Regenerate the Workbooks

Run from the repository root:

```powershell
& "demo-packages\zoho-concise-dashboard-and-databridge\data-bridge-demo\scripts\run_build.ps1"
```

Zoho references:

- DataBridge:
  <https://www.zoho.com/analytics/help/import-data/databridge.html>
- File import and refresh settings:
  <https://www.zoho.com/analytics/help/import-data/files-feeds.html>
