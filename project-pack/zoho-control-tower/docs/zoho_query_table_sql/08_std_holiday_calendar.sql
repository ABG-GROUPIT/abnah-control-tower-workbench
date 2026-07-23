-- Query Table: STD_Holiday_Calendar
-- Purpose: Standardize configured Indian holiday/calendar rows.
-- Source: RAW_Indian_Calendar_Holidays
-- Caveat: Synthetic calendar rows should be verified before production use.

SELECT DISTINCT
    h."row_id" AS "holiday_row_id",
    CAST(h."calendar_date" AS DATE) AS "calendar_date",
    h."holiday_name" AS "holiday_name",
    h."holiday_type" AS "holiday_type",
    h."region" AS "region",
    h."is_public_holiday" AS "is_public_holiday",
    h."is_bank_holiday" AS "is_bank_holiday",
    h."expected_business_impact" AS "expected_business_impact",
    h."impact_direction" AS "impact_direction",
    h."notes" AS "notes"
FROM "RAW_Indian_Calendar_Holidays" h;
