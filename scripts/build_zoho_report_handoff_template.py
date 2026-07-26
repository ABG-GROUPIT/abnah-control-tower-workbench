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
    views: dict[str, dict[str, str]] = {}
    for page in portal["pages"]:
        for slot_kind, items in (
            ("kpi", page["metrics"]),
            ("report", page["panels"]),
        ):
            for item in items:
                views[item["id"]] = {
                    "pageId": page["id"],
                    "slotKind": slot_kind,
                    "zohoViewName": item["zohoViewName"],
                    "securedEmbedUrl": "",
                }

    payload = {
        "schema": "abnah-zoho-report-embed-handoff/v2",
        "authMode": "zoho_secured_login",
        "integrationMode": "individual_report_views",
        "note": (
            "Paste only each individual saved view's secured-with-login iframe "
            "src URL. Never add passwords, OAuth tokens, client secrets, or "
            "report rows."
        ),
        "views": views,
    }
    serialized = f"{json.dumps(payload, indent=2)}\n"
    for target in TARGETS:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(serialized, encoding="utf-8")
        print(f"Wrote {target.relative_to(ROOT)} with {len(views)} view slots.")


if __name__ == "__main__":
    main()
