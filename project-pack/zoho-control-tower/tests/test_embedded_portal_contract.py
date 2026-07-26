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

    def test_handoff_documents_cover_current_stage_and_security(self) -> None:
        for path in (MIGRATION, CAPABILITY, EMBED):
            self.assertTrue(path.is_file(), path)
        migration = MIGRATION.read_text(encoding="utf-8")
        self.assertIn("all 38 numbered Query Tables saved", migration)
        self.assertIn("20_fact_ct_actual_consumption.sql", migration)
        self.assertIn("Weighted Unit Price", migration)
        embed = EMBED.read_text(encoding="utf-8")
        self.assertIn("Zoho secured-login dashboard embeds", embed)
        self.assertIn("Do not use:", embed)
        self.assertIn("GitHub Pages is static", embed)


if __name__ == "__main__":
    unittest.main()
