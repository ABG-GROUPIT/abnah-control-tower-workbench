# ABNAH Portal Handoff

Use this folder for the one controlled handoff between the Zoho dashboard
builder and the portal developer.

## Start

From this folder:

```powershell
Copy-Item .\ABNAH_PORTAL_HANDOFF_TEMPLATE.json .\ABNAH_PORTAL_HANDOFF.local.json
```

Fill only `ABNAH_PORTAL_HANDOFF.local.json`. That file is ignored by Git.
Do not edit the template with real values.

The local file contains:

- GitHub Pages and Supabase runtime URLs;
- Zoho workspace and OAuth configuration;
- the Zoho client secret and token-encryption key;
- Page 1 to Page 4 dashboard URLs;
- all 19 individual secured Zoho view URLs;
- the exact Query Table attached to every view.

## Validate

While Page 1 and Page 2 are the active scope:

```powershell
py -3 .\validate_handoff.py .\ABNAH_PORTAL_HANDOFF.local.json --required-pages p1,p2
```

To create the secret-free payload accepted by the portal's authenticated
Supabase configuration screen:

```powershell
py -3 .\validate_handoff.py .\ABNAH_PORTAL_HANDOFF.local.json --required-pages p1,p2 --write-visual-handoff .\ABNAH_ZOHO_VISUAL_HANDOFF.generated.json
```

The generated file contains only Zoho view names and URLs. It excludes OAuth
secrets, Supabase secrets, API keys and operational rows. It is ignored by Git.

For the final four-page handoff:

```powershell
py -3 .\validate_handoff.py .\ABNAH_PORTAL_HANDOFF.local.json --required-pages p1,p2,p3,p4
```

The validator prints missing field names only. It never prints secret values.

## URL Rule

For each saved Zoho report:

1. Open the report in Zoho Analytics.
2. Use **Share** and configure **Access with Login** for approved users.
3. Put that secured report URL in the matching `securedViewUrl`.
4. Put the complete dashboard URL only in `securedDashboardFallbackUrl`.

The custom portal uses Query Table API rows for KPIs, action queues and
underlying evidence. It uses selected individual Zoho views for visuals where
Zoho is stronger. A complete Zoho dashboard is only a fallback link.

## Secret Rule

These values must stay in the ignored local file and Supabase secrets:

- `zohoOAuthClientSecret`;
- `zohoTokenEncryptionKey`.

Do not request or copy a Supabase anon key or service-role key for this portal.
The browser does not use either key, and Supabase injects its reserved
service-role value into the deployed Edge Function.

Do not paste them into GitHub, documentation, screenshots, Teams messages or
public `open-view` URLs. The GitHub Pages frontend never receives them.

Official Zoho timeline-filter behavior is documented at:
https://www.zoho.com/analytics/help/dashboard/filter.html
