-- Query Table: DIM_Event
-- Purpose: Reusable manual event dimension.
-- Source: STD_Manual_Events
-- Join keys: event_id, start_date/end_date, affected scope text.

SELECT
    e."event_id" AS "event_key",
    e."event_id" AS "event_id",
    e."event_name" AS "event_name",
    e."event_type" AS "event_type",
    e."start_date" AS "start_date",
    e."end_date" AS "end_date",
    e."outlet_scope" AS "outlet_scope",
    e."affected_outlets" AS "affected_outlets",
    e."affected_category" AS "affected_category",
    e."affected_items" AS "affected_items",
    e."expected_impact_pct" AS "expected_impact_pct",
    e."impact_direction" AS "impact_direction",
    e."confidence_level" AS "confidence_level",
    e."event_source" AS "event_source",
    e."admin_status" AS "admin_status",
    e."notes" AS "notes"
FROM "STD_Manual_Events" e;
