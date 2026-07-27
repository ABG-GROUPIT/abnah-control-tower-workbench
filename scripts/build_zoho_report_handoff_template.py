from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTAL_CONFIG = ROOT / "config" / "zoho-portal.json"
TARGETS = (
    ROOT / "config" / "zoho-secured-embed-handoff.example.json",
    ROOT
    / "project-pack"
    / "zoho-control-tower"
    / "config"
    / "zoho-secured-embed-handoff.example.json",
)


def main() -> None:
    portal = json.loads(PORTAL_CONFIG.read_text(encoding="utf-8"))
    pages: dict[str, dict[str, object]] = {}
    for page in portal["pages"]:
        pages[page["id"]] = {
            "dashboardViewName": page["dashboardViewName"],
            "securedDashboardFallbackUrl": "",
            "reports": {
                panel["id"]: {
                    "viewName": panel["zohoViewName"],
                    "securedViewUrl": "",
                }
                for panel in page["panels"]
            },
        }

    payload = {
        "schema": "abnah-zoho-view-handoff/v4",
        "authMode": "zoho_secured_login",
        "integrationMode": "individual_report_views_with_dashboard_fallbacks",
        "note": (
            "Backward-compatible QA artifact only. The production custom "
            "portal uses authenticated Query Table API exports and does not "
            "require these URLs. Never add passwords, OAuth tokens, client "
            "secrets, or report rows."
        ),
        "pages": pages,
    }
    serialized = f"{json.dumps(payload, indent=2)}\n"
    for target in TARGETS:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(serialized, encoding="utf-8")
        report_count = sum(len(page["reports"]) for page in pages.values())
        print(
            f"Wrote {target.relative_to(ROOT)} with {report_count} report "
            f"slots and {len(pages)} dashboard fallbacks."
        )


if __name__ == "__main__":
    main()
