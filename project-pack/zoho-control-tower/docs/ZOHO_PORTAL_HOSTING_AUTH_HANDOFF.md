# Portal Hosting, Authentication and Handoff

## Repository Boundary

| Deliverable | Repository owner |
| --- | --- |
| Zoho manuals, model handoff and URL templates | `arnavkadhe` |
| Custom portal application and server code | `ABG-GROUPIT` |

Do not commit application code changes to the documentation repository.
Do not commit client rows or credentials to either repository.

## Hosting Boundary

GitHub Pages can host:

- the static Atlas;
- documentation;
- screenshots-free presentation material;
- a blueprint of the custom portal;
- individual secured Zoho embeds that require no server secret.

GitHub Pages cannot:

- store a Zoho client secret;
- refresh an OAuth token;
- query Zoho APIs securely;
- enforce company authentication for the outer shell;
- calculate live custom KPI cards from private data.

The operational custom portal therefore runs from the ABG application
deployment, which supports server routes and environment variables.

## Sign-In for Individual Zoho Embeds

1. Share each saved report with the intended Zoho viewer account.
2. Generate a secured **Access with Login** URL.
3. The viewer opens Zoho Analytics and signs in.
4. The custom portal embeds the individual report URL.
5. Zoho applies report permissions inside the embed.

The custom portal cannot read or bypass the Zoho login cookie.

## Authentication for the Outer Portal

Zoho report authentication and custom-portal authentication are separate.

For the POC:

1. protect every embedded report with Zoho secured login;
2. use the approved ABG application URL;
3. do not place secrets in the browser.

For production:

1. use company-approved authentication for the ABG portal;
2. keep Zoho OAuth credentials server-side;
3. use a company allowlist or SSO policy approved by IT;
4. keep Zoho report permissions as an additional access boundary.

## Secure KPI Backend

If the Zoho API entitlement test succeeds:

1. an administrator creates the approved Zoho OAuth application;
2. credentials are entered only as deployment environment variables;
3. the server requests approved KPI aggregates;
4. the server returns only the fields required by the selected page;
5. the portal renders ABNAH-styled KPI cards;
6. the server caches short-lived aggregate responses;
7. no arbitrary SQL is accepted from the browser.

Do not send OAuth secrets in chat or store them in the handoff JSON.

## URL Handoff

Use:

```text
03_ZOHO_INSTRUCTIONS/zoho-secured-embed-handoff.example.json
```

Fill only the `securedUrl` values.

Handoff procedure:

1. finish and validate one saved report;
2. generate its secured URL;
3. paste it beside its exact view name;
4. repeat for the remaining saved reports;
5. generate the four dashboard URLs;
6. validate the JSON syntax;
7. provide the completed JSON to the ABG portal repository maintainer;
8. keep the file free of credentials and client rows.

## Company-Laptop Acceptance Test

- The ABG application URL opens.
- `https://analytics.zoho.in/` opens.
- The company viewer account signs in.
- The first individual report embed loads.
- A custom filter changes the embedded report.
- The native page-dashboard fallback opens.
- Page refresh does not expose a credential.
- Browser developer tools show no OAuth secret.

## Local Report Reviewer

The local report reviewer remains separate because it contains operational
rows.

`127.0.0.1` means the viewer must be running on the same laptop as the browser.

1. Start the local reviewer on that laptop.
2. Leave its terminal process running.
3. Open the exact port printed by the command.
4. If the browser shows `Connection refused`, restart the process on that
   laptop.

The local reviewer is not deployed to GitHub Pages or the custom portal.
