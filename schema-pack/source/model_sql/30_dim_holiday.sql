-- Query Table: DIM_Holiday
-- Purpose: Reusable holiday dimension.
-- Source: STD_Holiday_Calendar
-- Supplemental file: requested layer list includes DIM_Holiday, but the requested numbered file list omitted it.

SELECT
    h."holiday_row_id" AS "holiday_key",
    h."calendar_date" AS "calendar_date",
    h."holiday_name" AS "holiday_name",
    h."holiday_type" AS "holiday_type",
    h."region" AS "region",
    h."is_public_holiday" AS "is_public_holiday",
    h."is_bank_holiday" AS "is_bank_holiday",
    h."expected_business_impact" AS "expected_business_impact",
    h."impact_direction" AS "impact_direction",
    h."notes" AS "notes"
FROM "STD_Holiday_Calendar" h;
