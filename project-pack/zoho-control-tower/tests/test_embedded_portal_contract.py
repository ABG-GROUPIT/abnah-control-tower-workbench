from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
CONFIG = REPOSITORY / "config" / "zoho-portal.json"
MIGRATION = ROOT / "docs" / "ZOHO_CURRENT_WORKSPACE_MIGRATION.md"
CAPABILITY = ROOT / "docs" / "ABNAH_REFERENCE_TO_ZOHO_CAPABILITY_MATRIX.md"
EMBED = ROOT / "docs" / "ZOHO_EMBEDDED_PORTAL_SETUP.md"
HOSTING = ROOT / "docs" / "ZOHO_PORTAL_HOSTING_AUTH_HANDOFF.md"
REPORT_SEQUENCE = (
    ROOT / "docs" / "ZOHO_REPORT_BUILD_EMBED_AND_FILTER_SEQUENCE.md"
)
FILTER_MAPPING = ROOT / "docs" / "ZOHO_DASHBOARD_FILTER_MAPPING_MATRIX.md"
HANDOFF = REPOSITORY / "config" / "zoho-secured-embed-handoff.example.json"
PORTAL_PAGE = REPOSITORY / "app" / "portal" / "page.tsx"
QUERY_TABLES = (
    ROOT
    / "FINAL_ZOHO_CONTROL_TOWER_IMPLEMENTATION"
    / "02_QUERY_TABLES"
)


class EmbeddedPortalContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))

    def test_four_reference_pages_have_five_primary_metrics(self) -> None:
        pages = self.config["pages"]
        self.assertEqual(4, len(pages))
        self.assertEqual(
            ["p1", "p2", "p3", "p4"],
            [page["id"] for page in pages],
        )
        self.assertTrue(all(len(page["metrics"]) == 5 for page in pages))
        self.assertEqual(20, sum(len(page["metrics"]) for page in pages))
        self.assertEqual(19, sum(len(page["panels"]) for page in pages))
        self.assertTrue(
            all(
                page["filterStrategy"] == "zoho_dashboard_user_filters"
                for page in pages
            )
        )

    def test_every_portal_object_has_a_packaged_query_source(self) -> None:
        source_queries = {
            item["sourceQuery"]
            for page in self.config["pages"]
            for item in [*page["metrics"], *page["panels"]]
        }
        self.assertTrue(source_queries)
        for source_query in source_queries:
            self.assertTrue((QUERY_TABLES / source_query).is_file(), source_query)

    def test_reference_corrected_kpis_are_present(self) -> None:
        metric_ids = {
            metric["zohoViewName"]
            for page in self.config["pages"]
            for metric in page["metrics"]
        }
        for expected in (
            "CT_P1_KPI_Open_Actions",
            "CT_P2_KPI_Delayed_PO_Value",
            "CT_P2_KPI_Price_Watch",
            "CT_P3_KPI_Menu_Items",
        ):
            self.assertIn(expected, metric_ids)

    def test_portal_selectors_use_modeled_values(self) -> None:
        filters = {
            (page["id"], item["id"]): item
            for page in self.config["pages"]
            for item in page["filters"]
        }
        self.assertEqual(
            [
                "ALL",
                "Pending",
                "Partially Received",
                "Closed",
                "Cancelled",
            ],
            [
                option["value"]
                for option in filters[("p2", "poStatus")]["options"]
            ],
        )
        self.assertEqual(
            ["ALL", "kg", "litre", "pcs"],
            [
                option["value"]
                for option in filters[("p3", "uom")]["options"]
            ],
        )

    def test_committed_portal_contains_no_embed_credentials(self) -> None:
        self.assertEqual(
            "zoho_secured_login",
            self.config["auth"]["mode"],
        )
        for page in self.config["pages"]:
            self.assertEqual("", page["dashboardEmbedUrl"])
            self.assertTrue(
                all(panel["embedUrl"] == "" for panel in page["panels"])
            )

    def test_one_file_handoff_is_blank_and_complete(self) -> None:
        handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
        self.assertEqual(
            "abnah-zoho-dashboard-embed-handoff/v3",
            handoff["schema"],
        )
        self.assertEqual("zoho_secured_login", handoff["authMode"])
        self.assertEqual(
            "page_dashboard_views",
            handoff["integrationMode"],
        )

        expected = {
            page["id"]: {
                "dashboardViewName": page["dashboardViewName"],
                "securedDashboardEmbedUrl": "",
            }
            for page in self.config["pages"]
        }
        self.assertEqual(4, len(handoff["pages"]))
        self.assertEqual(expected, handoff["pages"])

    def test_delivery_portal_has_a_separate_route(self) -> None:
        self.assertTrue(PORTAL_PAGE.is_file(), PORTAL_PAGE)
        self.assertIn(
            "EmbeddedControlTowerPortal standalone",
            PORTAL_PAGE.read_text(encoding="utf-8"),
        )

    def test_handoff_documents_cover_current_stage_and_security(self) -> None:
        for path in (
            MIGRATION,
            CAPABILITY,
            EMBED,
            HOSTING,
            REPORT_SEQUENCE,
            FILTER_MAPPING,
        ):
            self.assertTrue(path.is_file(), path)
        migration = MIGRATION.read_text(encoding="utf-8")
        self.assertIn("all 38 numbered Query Tables saved", migration)
        self.assertIn("20_fact_ct_actual_consumption.sql", migration)
        self.assertIn("Weighted Unit Price", migration)
        embed = EMBED.read_text(encoding="utf-8")
        self.assertIn("four complete secured Zoho dashboards", embed)
        self.assertIn("Do not use:", embed)
        self.assertIn("Dashboard User Filters", embed)
        hosting = HOSTING.read_text(encoding="utf-8")
        self.assertIn("GitHub Pages is not a backend", hosting)
        self.assertIn("20 KPI objects", hosting)
        self.assertIn("means **this same laptop**", hosting)
        sequence = REPORT_SEQUENCE.read_text(encoding="utf-8")
        self.assertIn("Build and secure these four dashboards", sequence)
        self.assertIn("Dashboard User Filters", sequence)
        self.assertIn("secured-with-login dashboard iframe URLs", sequence)
        mapping = FILTER_MAPPING.read_text(encoding="utf-8")
        self.assertIn("Query 34", mapping)
        self.assertIn("source_period_code", mapping)
        self.assertIn("outlet_code", mapping)


if __name__ == "__main__":
    unittest.main()
