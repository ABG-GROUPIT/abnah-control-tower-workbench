-- Query Table: STD_Manual_Events
-- Purpose: Standardize manual/admin event rows used for spike explanation and annotations.
-- Source: RAW_Manual_Calendar_Events
-- Caveat: affected_outlets, affected_category, and affected_items are semicolon-delimited text scopes.

SELECT DISTINCT
    e."row_id" AS "event_row_id",
    e."event_id" AS "event_id",
    e."event_name" AS "event_name",
    e."event_type" AS "event_type",
    CAST(e."start_date" AS DATE) AS "start_date",
    COALESCE(CAST(e."end_date" AS DATE), CAST(e."start_date" AS DATE)) AS "end_date",
    e."outlet_scope" AS "outlet_scope",
    e."affected_outlets" AS "affected_outlets",
    e."affected_category" AS "affected_category",
    e."affected_items" AS "affected_items",
    CAST(e."expected_impact_pct" AS DECIMAL(8,2)) AS "expected_impact_pct",
    e."impact_direction" AS "impact_direction",
    e."confidence_level" AS "confidence_level",
    e."event_source" AS "event_source",
    e."admin_status" AS "admin_status",
    e."notes" AS "notes"
FROM "RAW_Manual_Calendar_Events" e;
