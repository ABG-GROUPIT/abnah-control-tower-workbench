# External Data Signals Pre-UAT Plan - India/NCR Context

This document plans lean external data signals that can strengthen the ABNAH intelligence dashboards before the POSist UAT schema is known. ABNAH is operating in India, so source selection must fit Indian coverage, Indian compliance expectations, Delhi/NCR operational realities, and cafe/procurement decisions.

This is a planning layer, not a schema build. Do not add these tables to the core model until POSist UAT screenshots/API docs confirm the internal POSist fields for outlet, vendor, item, PO, GRN, inventory, and sales grain.

India/NCR assumptions:

1. Use free/open sources only for proof of concept, validation, and early dashboard mockups.
2. Always keep a commercially available production option beside every free/open source.
3. Prefer India-relevant official or enterprise sources where available: IMD/weather, CPCB/data.gov.in AQI, India holiday calendars, Google Maps, and Mappls/MapmyIndia.
4. Use ABNAH-owned calendars and manually governed local events before depending on public entertainment/event APIs.
5. Do not use US-focused event APIs, consumer-platform scraping, or unofficial event scrapers as planning defaults.
6. Keep every external source optional until POSist confirms internal join keys and ABNAH confirms source approval.

## 1. Planning Principle

Use the smallest external signal set that can improve a real operational decision:

```text
Can we reorder safely?
Which vendor is practical during stockout?
Will weather spoil or delay material movement?
Will demand move because of weather, holidays, or local events?
Can Zoho forecast or classify the risk once these features are joined to history?
```

Avoid broad data enrichment that sounds impressive but does not change inventory, procurement, or consumption decisions.

## 2. First External Signal Shortlist

Source tier rule:

```text
PoC source proves whether the signal helps ABNAH.
Commercial source is what ABNAH could actually procure for a governed production workflow.
Do not let a free PoC source become the assumed production source without approval.
```

| Priority | Signal | PoC/free option | Commercial option | ABNAH stance | Main use |
|---|---|---|---|---|---|
| P0 | Weather at outlet and vendor locations | Open-Meteo; IMD if access is easy | Google Weather API, Tomorrow.io, OpenWeather paid, Meteomatics, AccuWeather Enterprise, or governed IMD access | Start with Open-Meteo/IMD for PoC, compare commercial weather if this becomes production-critical. | Spoilage risk, demand uplift, delivery disruption. |
| P0 | Vendor-to-outlet travel time and distance | Google Maps trial/free monthly usage; Mappls free developer access where available | Google Maps Platform Routes/Places/Geocoding or Mappls enterprise | Keep Google and Mappls as the serious production candidates; Mappls gets extra weight for India-native coverage. | Emergency vendor choice during stockout. |
| P0 | Vendor and outlet geocodes | Manual verified lat/long in vendor/outlet master | Google Places/Geocoding or Mappls geocoding | Manual for demo; commercial geocoding only when vendor addresses are messy or scale increases. | Needed for weather, route, AQI, and local event joins. |
| P1 | Internal/manual events | Existing manual event calendar, ABNAH ops calendar, or Google Calendar | Google Workspace Calendar governance or ABNAH-approved calendar/workflow system | ABNAH-owned event data is the cleanest first source. | Planned promotions, launches, closures, vendor blackout days. |
| P1 | India/NCR local event context | Manual curated Delhi/NCR event calendar for outlet catchments | PredictHQ if India/NCR coverage is validated; licensed exports/partner feeds from malls, venues, BookMyShow, Paytm Insider, or local event partners | Use commercial event data only if licensed and coverage is strong for Connaught Place, Hauz Khas, and Saket. | Demand uplift near outlet catchments. |
| P1 | Air quality | CPCB/data.gov.in AQI; Open-Meteo Air Quality for PoC fallback | Google Air Quality API, Ambee, IQAir/AirVisual, or approved AQI provider | CPCB/data.gov.in for PoC; commercial AQI only if AQI proves useful in demand/channel analysis. | Footfall/delivery context in Delhi; possible demand/channel impact. |
| P1 | Public holidays and school/office calendar | Existing Indian holiday table, National Portal calendar, manual Delhi/NCR additions | Calendarific, API Ninjas, Timeanddate, or approved holiday calendar provider | Keep current table for demo; commercial holiday API only if automated yearly maintenance matters. | Demand context and staffing/procurement planning. |
| P2 | Commodity or market price indexes | data.gov.in/Agmarknet mandi prices; manual weekly commodity CSV | Tridge, CEIC India Premium, or approved food/commodity data vendor | Defer until POSist confirms vendor-rate history and procurement variance fields. | Vendor rate variance and expected procurement pressure. |
| P2 | Search/social trend signals | Avoid initially | Only if approved enterprise data source exists | Not phase 1. | Weak/noisy demand proxy. |
| P2 | Competitor/menu context | Existing synthetic table, manual checks | Approved competitive intelligence or foodservice data provider | Not phase 1 unless ABNAH explicitly asks for market benchmarking. | Price context, not causal proof. |

## 3. P0 Signal Details

### 3.1 Weather

Fields to consider:

| Field | Grain | Why it matters |
|---|---|---|
| `temperature_2m` | location + hour/day | Heat-sensitive materials, cold beverage demand. |
| `relative_humidity_2m` | location + hour/day | Bakery/dairy quality risk and perceived weather. |
| `dew_point_2m` or wet bulb | location + hour/day | Better spoilage/comfort proxy than temperature alone. |
| `precipitation` and `precipitation_probability` | location + hour/day | Delivery delays, footfall drops, hot beverage mix. |
| `weather_code` | location + hour/day | Simple categorical weather feature for Zoho filters. |
| `wind_speed` | location + hour/day | Delivery disruption only if signal is strong. |

MVP approach:

1. Use outlet geocodes first for Connaught Place, Hauz Khas, Saket, and any confirmed ABNAH locations.
2. Pull daily weather for each outlet.
3. Use Open-Meteo or IMD for proof of concept.
4. If weather becomes a production feature, compare commercial options such as Google Weather API, Tomorrow.io, OpenWeather paid plans, Meteomatics, AccuWeather Enterprise, or governed IMD access.
5. Add vendor geocodes only after POSist/vendor master confirms vendor address quality.
6. Create derived bands instead of exposing too many raw weather fields.

Useful derived features:

| Feature | Logic |
|---|---|
| `heat_risk_band` | Temperature + humidity threshold for perishables. |
| `rain_risk_band` | Precipitation probability/amount threshold. |
| `weather_demand_band` | Simple hot/cold/rain/normal demand context. |
| `spoilage_risk_band` | Material class + heat/humidity + route duration. |

### 3.2 Vendor Route Suitability

Fields to consider:

| Field | Grain | Why it matters |
|---|---|---|
| `vendor_latitude`, `vendor_longitude` | vendor | Required for route and weather lookup. |
| `outlet_latitude`, `outlet_longitude` | outlet | Required for route and weather lookup. |
| `route_distance_km` | vendor + outlet + refresh time | Cost and practical sourcing radius. |
| `route_duration_minutes` | vendor + outlet + refresh time | Emergency replenishment feasibility. |
| `route_duration_in_traffic_minutes` | vendor + outlet + refresh time | Better stockout decision during operating hours. |
| `route_status` | vendor + outlet + refresh time | Detect unreachable/error routes. |

MVP approach:

1. Start with fixed vendor/outlet coordinates and daily route snapshot.
2. Use Google Routes or Mappls for proof of concept, depending on which account/API key is easiest to activate.
3. For production, compare Google Maps Platform and Mappls enterprise on India coverage, route ETA quality, pricing, billing control, support, and procurement fit.
4. Do not calculate every vendor-to-every-outlet route every hour unless there is a decision that needs it.
5. For emergency replenishment, route only candidate vendors for the stocked-out material.
6. Cache route results with timestamp and source so Zoho is not dependent on live API latency.

Useful derived features:

| Feature | Logic |
|---|---|
| `emergency_vendor_rank` | Vendor availability + ETA + historical reliability + weather risk. |
| `stockout_delivery_feasible_flag` | ETA below threshold and vendor active. |
| `cold_chain_route_risk_band` | ETA + heat/humidity + material perishability. |
| `route_delay_band` | Current traffic duration compared with normal duration. |

### 3.3 Vendor And Outlet Geocodes

This is the smallest dependency that unlocks route, weather, AQI, and local event features.

Minimum fields:

```text
entity_type
entity_code
entity_name
address_text
latitude
longitude
geocode_source
geocode_confidence
last_verified_at
```

Recommended rule:

Use manual/verified coordinates for demo and early UAT. Use Google Places/Geocoding or Mappls later only if ABNAH wants automated address resolution, confidence scoring, or scale beyond a small vendor master.

## 4. P1 Signal Details

### 4.1 Internal And Google Calendar Events

Use for:

- promotions,
- store events,
- menu launches,
- local campaigns,
- planned closures,
- vendor blackout days,
- school/office event overlays if maintained internally.

Fields:

```text
event_id
event_name
event_type
start_datetime
end_datetime
outlet_scope
affected_outlets
affected_category
affected_items
expected_impact_direction
expected_impact_pct
source_calendar
confidence_level
```

This extends the current `manual_calendar_events` concept. Google Calendar can be an input source later, but the canonical event table should stay source-neutral.

### 4.2 India/NCR Local Event Context

Use for:

- event-day sales uplift,
- procurement pre-positioning,
- staff/inventory readiness near outlet catchments.

India-specific rule:

Do not assume a public event API is usable for India. For ABNAH, the lean path is a manually governed Delhi/NCR event table covering only events that can plausibly affect Connaught Place, Hauz Khas, Saket, or future outlet catchments. Sources can include ABNAH marketing calendars, mall/market association calendars, known local festivals, school/college calendars, corporate-area closures, and manually approved local event lists.

Only use BookMyShow, Paytm Insider, Zomato, Swiggy, or similar consumer-platform data if ABNAH has a licensed export, partner API, or written approval. Do not use scraped data.

Commercial option:

PredictHQ can be evaluated as a commercial event intelligence source if its India/NCR coverage is proven around ABNAH outlet catchments. It should not replace ABNAH-owned calendars for promotions, closures, and planned internal activities.

Possible features:

| Feature | Grain | Use |
|---|---|---|
| `nearby_event_count` | outlet + date | Demand context. |
| `nearby_large_event_flag` | outlet + date | Procurement readiness. |
| `event_distance_km` | outlet + event | Relevance filter. |
| `event_category` | outlet + event | Helps separate food/festival/concert/sports signals. |

Start with manual events. Add public/commercial events only if coverage and licensing are strong enough for Delhi/NCR.

### 4.3 Air Quality

Delhi AQI can affect:

- dine-in footfall,
- delivery mix,
- outdoor movement,
- staff/vendor movement,
- product mix on bad-air days.

MVP fields:

```text
outlet_code
date_or_hour
aqi
aqi_category
dominant_pollutant
pm25
pm10
source
```

Use CPCB/data.gov.in AQI where feasible for proof of concept. If AQI proves useful, compare commercial options such as Google Air Quality API, Ambee, IQAir/AirVisual, or another approved AQI provider. Keep AQI as a context feature first. Do not claim causation until model validation shows signal.

## 5. Signals To Avoid For Phase 1

| Signal | Reason to defer |
|---|---|
| Google/search trends | Official access is limited/noisy and not obviously actionable for procurement. |
| Social media sentiment | High effort, weak operational precision, approval risk. |
| US-focused event APIs | Weak relevance for India/NCR outlet catchments. |
| BookMyShow/Paytm Insider scraping | Governance risk; use only licensed export or partner/API access if ABNAH approves it. |
| Zomato/Swiggy marketplace scraping | Governance risk and not needed for phase 1 inventory/procurement. |
| Full traffic telemetry | Route ETA is enough for the first stockout/vendor decision. |
| Broad demographic data | Useful for expansion/location analysis, not immediate inventory/procurement. |
| Competitor scraping | Governance and reliability risk unless an approved provider exists. |
| Deep commodity feeds | Useful later for vendor rate variance, but not required before POSist procurement fields are known. |

## 6. Zoho Analytics Fit

### 6.1 Dashboard Use

| Dashboard | External features to test |
|---|---|
| Inventory and Consumption Intelligence | Weather risk bands, spoilage risk, route/cold-chain risk, reorder feasibility. |
| Vendor and Procurement Analytics | Emergency vendor rank, ETA band, route delay band, vendor weather risk, vendor reliability overlays. |
| Sales and Menu Intelligence | Weather demand band, India holiday/event flags, curated Delhi/NCR event count, AQI category. |
| Executive Outlet Health | Weather/event-adjusted outlet context, external risk count. |

### 6.2 Zoho Forecasting

Use Zoho chart forecasting for simple time-series views:

- daily sales by outlet,
- daily theoretical ingredient demand,
- inventory value trend,
- weather-adjusted visual comparisons where the chart source has date grain.

This is useful before heavier ML because it is fast and explainable.

### 6.3 Zoho AutoML

Candidate AutoML targets after enough history exists:

| Target | Model type | Feature examples |
|---|---|---|
| `next_day_item_qty` | Regression | lag sales, weekday, holiday, event count, temperature, rain, AQI. |
| `ingredient_demand_qty` | Regression | item sales history, BOM, weather bands, event flags. |
| `stockout_risk_flag` | Classification | current stock, theoretical demand, lead time, route ETA, open PO, weather. |
| `vendor_delay_risk_flag` | Classification | vendor history, route duration, rain band, delivery day, PO size. |
| `spoilage_risk_flag` | Classification | material class, heat/humidity, route duration, storage category. |

Do not run AutoML until the target is trustworthy. For example, `stockout_risk_flag` requires actual stock movement/reorder fields from POSist, not only synthetic low-stock thresholds.

### 6.4 Zoho Code Studio

Use Code Studio or an external ETL layer for feature engineering that is awkward in query tables:

- geocode validation,
- route matrix calls or cached route ingestion,
- weather API pull and normalization,
- event density calculations,
- AQI provider normalization,
- spoilage/weather risk scoring,
- vendor emergency rank calculation,
- lag/rolling-window feature creation.

Enterprise preference:

```text
External API calls -> controlled ETL/FastAPI/job -> stored CSV/API feed -> Zoho import/query tables
```

Do not make dashboards depend on live external API calls. Cache and timestamp every external signal.

## 7. Lean MVP Feature Pack

Build this first after UAT confirms internal keys:

| Pack | Required internal fields | External fields | Business output |
|---|---|---|---|
| Weather demand context | outlet/date sales or consumption | outlet weather daily | Weather-adjusted demand visuals. |
| Spoilage risk | material category, stock/PO/GRN, vendor/outlet location | temp, humidity, route duration | Perishable material risk band. |
| Emergency vendor choice | vendor master, item-vendor mapping, stockout item, outlet | route ETA, route distance, weather band | Candidate vendor ranking during stockout. |
| Event readiness | outlet/date sales, manual events | curated India/NCR event count/category near outlet | Event-day procurement/demand planning. |

## 8. Candidate Feature Tables Later

These are not final schema tables yet. They are planning names for discussion.

| Candidate table | Grain | Notes |
|---|---|---|
| `EXT_Location_Master` | entity | Outlet/vendor coordinates and geocode confidence. |
| `EXT_Weather_Daily` | location + date | Daily weather history/forecast summary. |
| `EXT_Weather_Hourly` | location + hour | Only if daypart/order timestamp exists. |
| `EXT_Route_Vendor_Outlet` | vendor + outlet + snapshot time | Cached route distance/duration. |
| `EXT_Event_Calendar` | event + date + outlet/market | Manual/internal/approved India-local events normalized. |
| `EXT_Air_Quality_Daily` | outlet + date | AQI context. |
| `FEATURE_Inventory_External_Risk` | outlet + material + date | Combined risk features for dashboard/AutoML. |
| `FEATURE_Vendor_Emergency_Rank` | outlet + material + vendor + date | Candidate vendor ranking during stockout. |

## 9. Commercial Source Evaluation Rules

Before ABNAH moves any external signal from PoC to production, evaluate the commercial option on:

1. India/NCR coverage for Connaught Place, Hauz Khas, Saket, vendor locations, and future outlets.
2. Right to store, cache, transform, and display derived features in Zoho Analytics.
3. API quota, rate limits, monthly billing controls, and contract/procurement fit.
4. Historical data availability, because AutoML and regression need backfill, not only live forecasts.
5. SLA/support expectations if the signal affects procurement decisions.
6. Data refresh frequency that matches the business decision. Daily weather may be enough for dashboards; route ETA may need operating-hour snapshots.
7. Exportability to the existing FastAPI/CSV/Zoho feed pattern without live dashboard API calls.

## 10. Validation Rules

Before trusting external signals:

1. Confirm timezone alignment for all date/hour fields.
2. Confirm outlet/vendor coordinates are correct.
3. Compare route ETA against real expected delivery experience when possible.
4. Test weather-demand relationship historically before claiming impact.
5. Compare event-day uplift to non-event baseline.
6. Keep every external field stamped with `source`, `retrieved_at`, and `source_location`.
7. Separate actual POSist facts from external context features in dashboard labels.
8. Confirm source licensing/approval before using consumer-platform or public event data.

## 11. Initial Decision

The recommended pre-UAT shortlist is:

1. Weather daily at outlet level using Open-Meteo/IMD for PoC, with Google Weather API, Tomorrow.io, OpenWeather paid, Meteomatics, or AccuWeather Enterprise as commercial candidates.
2. Vendor/outlet geocode master using manually verified India coordinates first.
3. Vendor-to-outlet route matrix for candidate vendors only, using Google Routes or Mappls for PoC and comparing Google Maps Platform versus Mappls enterprise for production.
4. Manual/internal event calendar extension for ABNAH promotions, Indian holidays, Delhi/NCR events, and local outlet catchment context.
5. AQI from CPCB/data.gov.in for PoC, with Google Air Quality API, Ambee, IQAir/AirVisual, or another approved AQI provider as commercial candidates.
6. Public/commercial event data only if India/NCR coverage is proven and ABNAH has licensed/approved access; otherwise do not use it.
7. Commodity/market prices only after POSist UAT confirms procurement rate history; use data.gov.in/Agmarknet for PoC and Tridge/CEIC or an approved data vendor for commercial evaluation.

This shortlist is lean enough to implement in Zoho/ETL later while directly supporting ABNAH's phase 1 focus: inventory and consumption intelligence plus vendor and procurement analytics.

## 12. India-Relevant Source Notes

Check these source families again before implementation because API access, billing, and terms can change:

| Source family | Type | Use | Reference | Planning note |
|---|---|---|---|---|
| IMD API Management | Official/governed | Weather observations, forecasts, warnings | `https://api.imd.gov.in/` | Prefer if ABNAH wants official Indian weather context and access is approved. |
| Open-Meteo | Free/paid PoC-friendly | Fast weather history/forecast PoC | `https://open-meteo.com/en/docs` | Good for quick testing; paid plans exist, but it should still be compared against commercial providers for production. |
| Google Weather API | Commercial | Weather observations/forecast through Google Maps Platform | `https://developers.google.com/maps/documentation/weather/usage-and-billing` | Strong if ABNAH already chooses Google Maps Platform for routes, geocoding, and AQI. |
| Tomorrow.io | Commercial | Weather and route/weather risk context | `https://docs.tomorrow.io/reference/welcome` | Good candidate if ABNAH wants richer weather layers and alerts. |
| OpenWeather | Free plus commercial | Weather, historical, forecast, air quality | `https://openweathermap.org/price` | Transparent self-service paid option; evaluate India accuracy. |
| Meteomatics | Commercial/enterprise | High-resolution weather, historical, forecast, climate data | `https://www.meteomatics.com/en/weather-api/` | Strong enterprise option if weather quality becomes business-critical. |
| AccuWeather Enterprise | Commercial/enterprise | Weather, alerts, MinuteCast-style local forecasts | `https://apidev.accuweather.com/developers/overview` | Enterprise weather candidate; evaluate India coverage and licensing. |
| Google Routes API | Commercial with trial/free monthly usage | Route matrix and travel duration | `https://developers.google.com/maps/documentation/routes/compute_route_matrix` | Practical for vendor-to-outlet ETA and stockout routing. |
| Mappls/MapmyIndia | Commercial with developer access | India-native routing, geocoding, maps | `https://developer.mappls.com/` | Strong India fit; compare with Google on coverage, pricing, and approval. |
| Google Places/Geocoding | Commercial | Address cleanup and coordinate validation | `https://mapsplatform.google.com/pricing/` | Useful if vendor addresses are incomplete or need confidence scoring. |
| CPCB/data.gov.in AQI | Official/open data | India AQI context | `https://www.data.gov.in/resource/real-time-air-quality-index-various-locations` | Relevant for Delhi/NCR footfall and delivery context. |
| Google Air Quality API | Commercial | AQI, pollutant details, forecast/history | `https://developers.google.com/maps/documentation/air-quality/usage-and-billing` | Strong if ABNAH already procures Google Maps Platform. |
| Ambee | Commercial | AQI, weather, pollen, environmental data | `https://www.getambee.com/pricing` | India-relevant environmental data vendor to evaluate for AQI/weather bundles. |
| IQAir/AirVisual | Commercial with API access | AQI and pollution data | `https://www.iqair.com/air-quality-monitors/api` | Evaluate if AQI becomes a meaningful demand/channel feature. |
| National Portal of India holiday calendar / current holiday table | Official/open | India holidays | `https://www.india.gov.in/calendar` | Keep official holidays plus ABNAH-specific commercial/local events. |
| Calendarific | Commercial/free tier | Holiday calendar automation | `https://calendarific.com/pricing` | Use only if automated holiday maintenance is worth it. |
| Google Calendar API | Commercial workspace/governed | Internal ABNAH event calendars | `https://developers.google.com/workspace/calendar/api/v3/reference/events/list` | Useful for owned promotions, closures, and planned events, not as a generic public-event solution. |
| PredictHQ | Commercial | Local event intelligence for forecasting | `https://docs.predicthq.com/api/events/search-events` | Evaluate only if India/NCR coverage around outlets is strong enough. |
| data.gov.in/Agmarknet | Official/open | India mandi/commodity prices | `https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi` | Good PoC source for commodity context after POSist vendor-rate data is understood. |
| Tridge | Commercial | Food commodity and agri-market intelligence | `https://www.tridge.com/data-analytics` | Commercial option if ABNAH wants procurement price benchmarking. |
| CEIC India Premium | Commercial | India macro/alternative/economic data | `https://info.ceicdata.com/en-products-india-premium-database` | Use only if macro/commodity context becomes a serious procurement requirement. |
