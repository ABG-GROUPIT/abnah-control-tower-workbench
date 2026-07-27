from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


PLACEHOLDER_MARKERS = ("YOUR_", "PASTE_", "CHANGE_ME")
VALID_PAGES = ("p1", "p2", "p3", "p4")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an ABNAH portal handoff without printing secrets."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--required-pages",
        default="p1,p2",
        help="Comma-separated page IDs whose secured URLs must be complete.",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Validate the committed template structure without requiring values.",
    )
    parser.add_argument(
        "--write-visual-handoff",
        type=Path,
        help=(
            "Write a secret-free abnah-zoho-view-handoff/v4 payload after "
            "validation passes."
        ),
    )
    return parser.parse_args()


def nested(data: dict[str, object], *keys: str) -> object:
    current: object = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def is_missing(value: object) -> bool:
    if value is None or value == "" or value == []:
        return True
    if isinstance(value, str):
        return any(marker in value for marker in PLACEHOLDER_MARKERS)
    return False


def valid_https(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def visual_handoff(data: dict[str, object]) -> dict[str, object]:
    visuals = data["securedVisualUrls"]
    assert isinstance(visuals, dict)
    pages: dict[str, object] = {}
    for page_id, page_config in visuals.items():
        assert isinstance(page_config, dict)
        reports = page_config.get("reports", {})
        assert isinstance(reports, dict)
        pages[page_id] = {
            "dashboardViewName": page_config.get("dashboardViewName", ""),
            "securedDashboardFallbackUrl": page_config.get(
                "securedDashboardFallbackUrl",
                "",
            ),
            "reports": {
                report_id: {
                    "viewName": report.get("viewName", ""),
                    "securedViewUrl": report.get("securedViewUrl", ""),
                }
                for report_id, report in reports.items()
                if isinstance(report, dict)
            },
        }
    return {
        "schema": "abnah-zoho-view-handoff/v4",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "authMode": "zoho_secured_login",
        "integrationMode": (
            "individual_report_views_with_dashboard_fallbacks"
        ),
        "note": (
            "Generated from the local ABNAH portal handoff. Contains only "
            "secured Zoho view URLs; no secrets or operational rows."
        ),
        "pages": pages,
    }


def main() -> None:
    args = parse_args()
    data = json.loads(args.path.read_text(encoding="utf-8-sig"))
    errors: list[str] = []

    if data.get("schema") != "abnah-portal-handoff/v1":
        errors.append("schema")

    required_pages = [page.strip() for page in args.required_pages.split(",")]
    unknown = [page for page in required_pages if page not in VALID_PAGES]
    if unknown:
        raise SystemExit(f"Unknown required page IDs: {', '.join(unknown)}")

    required_paths = [
        ("publicConfiguration", "githubPagesPortalUrl"),
        ("publicConfiguration", "supabaseProjectRef"),
        ("publicConfiguration", "supabaseProjectUrl"),
        ("publicConfiguration", "supabaseFunctionBaseUrl"),
        ("publicConfiguration", "portalReturnUrl"),
        ("publicConfiguration", "portalAuthStartUrl"),
        ("publicConfiguration", "portalAuthCallbackUrl"),
        ("publicConfiguration", "portalStatusUrl"),
        ("publicConfiguration", "portalConfigUrl"),
        ("publicConfiguration", "zohoWorkspaceId"),
        ("publicConfiguration", "zohoOAuthClientId"),
        ("publicConfiguration", "zohoPortalAdminEmails"),
        ("privateConfiguration", "zohoOAuthClientSecret"),
        ("privateConfiguration", "zohoTokenEncryptionKey"),
    ]

    if not args.allow_placeholders:
        for path in required_paths:
            if is_missing(nested(data, *path)):
                errors.append(".".join(path))

    url_paths = [
        ("publicConfiguration", "githubPagesPortalUrl"),
        ("publicConfiguration", "supabaseProjectUrl"),
        ("publicConfiguration", "supabaseFunctionBaseUrl"),
        ("publicConfiguration", "portalReturnUrl"),
        ("publicConfiguration", "portalAuthStartUrl"),
        ("publicConfiguration", "portalAuthCallbackUrl"),
        ("publicConfiguration", "portalStatusUrl"),
        ("publicConfiguration", "portalConfigUrl"),
    ]
    for path in url_paths:
        value = nested(data, *path)
        if args.allow_placeholders and is_missing(value):
            continue
        if not valid_https(value):
            errors.append(".".join(path))

    visuals = data.get("securedVisualUrls")
    if not isinstance(visuals, dict):
        errors.append("securedVisualUrls")
        visuals = {}

    for page in required_pages:
        page_config = visuals.get(page)
        if not isinstance(page_config, dict):
            errors.append(f"securedVisualUrls.{page}")
            continue
        dashboard_url = page_config.get("securedDashboardFallbackUrl")
        if not args.allow_placeholders and not valid_https(dashboard_url):
            errors.append(
                f"securedVisualUrls.{page}.securedDashboardFallbackUrl"
            )
        reports = page_config.get("reports")
        if not isinstance(reports, dict) or not reports:
            errors.append(f"securedVisualUrls.{page}.reports")
            continue
        for report_id, report in reports.items():
            if not isinstance(report, dict):
                errors.append(f"securedVisualUrls.{page}.reports.{report_id}")
                continue
            for field in ("viewName", "queryTable"):
                if is_missing(report.get(field)):
                    errors.append(
                        f"securedVisualUrls.{page}.reports.{report_id}.{field}"
                    )
            secured_url = report.get("securedViewUrl")
            if not args.allow_placeholders and not valid_https(secured_url):
                errors.append(
                    f"securedVisualUrls.{page}.reports."
                    f"{report_id}.securedViewUrl"
                )

    if errors:
        print("Handoff validation failed. Missing or invalid fields:")
        for field in sorted(set(errors)):
            print(f"- {field}")
        raise SystemExit(1)

    if args.write_visual_handoff:
        output = visual_handoff(data)
        args.write_visual_handoff.write_text(
            json.dumps(output, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            "Wrote secret-free Zoho visual handoff: "
            f"{args.write_visual_handoff}"
        )

    report_count = sum(
        len(page.get("reports", {}))
        for page in visuals.values()
        if isinstance(page, dict)
    )
    print(
        "Handoff validation passed: "
        f"{len(visuals)} pages and {report_count} report URL slots. "
        "Secret values were not printed."
    )


if __name__ == "__main__":
    main()
