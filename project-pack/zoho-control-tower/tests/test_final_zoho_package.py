from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts" / "build_final_zoho_package.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("final_zoho_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class FinalZohoPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = _load_builder()
        cls.package = cls.builder.build()

    def test_only_the_fourteen_active_imports_are_packaged(self) -> None:
        import_dir = self.package / "01_IMPORT_FILES"
        actual = {
            path.name
            for path in import_dir.glob("*.csv")
            if path.name != "IMPORT_CHECKLIST.csv"
        }
        expected = {
            "RAWN_CT_vendor_report.csv",
            "RAWN_CT_gross_net_margin.csv",
            "RAWN_CT_item_recipe_report.csv",
            "RAWN_CT_enterprise_variance_normal.csv",
            "RAWN_CT_closing_stock.csv",
            "RAWN_CT_enterprise_purchase_order.csv",
            "RAWN_CT_enterprise_entry.csv",
            "RAWN_CT_enterprise_transfer_from.csv",
            "RAWN_CT_enterprise_transfer_to.csv",
            "RAWN_CT_enterprise_wastage_normal.csv",
            "AUX_Menu_Demand_Forecast.csv",
            "AUX_Expiry_Estimate.csv",
            "AUX_Outlet_Master.csv",
            "AUX_Theoretical_Consumption.csv",
        }
        self.assertEqual(expected, actual)
        self.assertFalse(any(name.startswith("RAW_CT_") for name in actual))

    def test_query_folder_contains_the_current_manifest_only(self) -> None:
        query_dir = self.package / "02_QUERY_TABLES"
        sql_files = sorted(query_dir.glob("*.sql"))
        manifest = _read_rows(query_dir / "QUERY_TABLE_MANIFEST.csv")
        self.assertEqual(38, len(sql_files))
        self.assertEqual(38, len(manifest))
        self.assertLessEqual(
            max(int(row["dependency_level"]) for row in manifest),
            3,
        )
        self.assertTrue((query_dir / "10_std_ct_vendor_report.sql").exists())
        self.assertTrue((query_dir / "37_dim_ct_outlet_enriched.sql").exists())
        self.assertTrue((query_dir / "38_fact_ct_expiry_risk.sql").exists())
        self.assertFalse(any("zia_" in path.name.lower() for path in sql_files))

    def test_import_checklist_and_sql_target_copy_named_tables(self) -> None:
        checklist = _read_rows(
            self.package / "01_IMPORT_FILES" / "IMPORT_CHECKLIST.csv"
        )
        self.assertEqual(14, len(checklist))
        self.assertTrue(
            all(row["zoho_table_name"].endswith("-Copy") for row in checklist)
        )

        query_dir = self.package / "02_QUERY_TABLES"
        query_sql = "\n".join(
            path.read_text(encoding="utf-8") for path in query_dir.glob("*.sql")
        )
        reference_only_files = {"AUX_Outlet_Master.csv"}
        for row in checklist:
            logical_name = Path(row["file_name"]).stem
            self.assertNotIn(f'"{logical_name}"', query_sql)
            if row["file_name"] in reference_only_files:
                self.assertNotIn(f'"{row["zoho_table_name"]}"', query_sql)
                continue
            self.assertIn(f'"{row["zoho_table_name"]}"', query_sql)

    def test_handoff_contains_all_source_contracts(self) -> None:
        contracts = list(
            (self.package / "05_DEVELOPER_HANDOFF" / "SOURCE_CONTRACTS").glob(
                "*.json"
            )
        )
        self.assertEqual(21, len(contracts))

    def test_truth_and_reconciliation_gates_are_packaged_and_passing(self) -> None:
        validation = self.package / "04_VALIDATION_AND_LIMITATIONS"
        truth = list((validation / "TRUTH_PACK").glob("*.csv"))
        self.assertEqual(13, len(truth))
        reconciliation = _read_rows(validation / "_RECONCILIATION_RESULTS.csv")
        acceptance = _read_rows(
            validation / "TRUTH_PACK" / "CONTROL_TOWER_ACCEPTANCE_CHECKS.csv"
        )
        self.assertEqual({"PASS"}, {row["status"] for row in reconciliation})
        self.assertEqual({"PASS"}, {row["status"] for row in acceptance})

    def test_package_manifest_hashes_every_payload_file(self) -> None:
        manifest = _read_rows(self.package / "PACKAGE_MANIFEST.csv")
        expected_paths = {
            path.relative_to(self.package).as_posix()
            for path in self.package.rglob("*")
            if path.is_file() and path.name != "PACKAGE_MANIFEST.csv"
        }
        self.assertEqual(expected_paths, {row["path"] for row in manifest})
        for row in manifest:
            path = self.package / Path(row["path"])
            self.assertEqual(int(row["size_bytes"]), path.stat().st_size)
            self.assertEqual(row["sha256"], _sha256(path), row["path"])

    def test_start_here_rejects_legacy_and_actual_data_claims(self) -> None:
        start = (self.package / "START_HERE.md").read_text(encoding="utf-8")
        self.assertIn("14 active Zoho import files", start)
        self.assertIn("38 Query Tables", start)
        self.assertIn("no actual ABNAH operational rows", start)
        self.assertIn("older generic 37-query model", start)
        self.assertIn(
            "03A_LOOKUPS_FORMULAS_AND_PRE_DASHBOARD_SETUP.md",
            start,
        )

    def test_pre_dashboard_setup_runbook_is_packaged(self) -> None:
        path = (
            self.package
            / "03_ZOHO_INSTRUCTIONS"
            / "03A_LOOKUPS_FORMULAS_AND_PRE_DASHBOARD_SETUP.md"
        )
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("37_dim_ct_outlet_enriched.sql", text)
        self.assertIn("Open PO Count", text)
        self.assertIn("Menu Gross Margin %", text)
        self.assertIn("month_03", text)
        self.assertIn("Stockout Risk Item Count | 16", text)
        self.assertIn("Open Risky PO Count | 1", text)

    def test_dashboard_expected_results_are_packaged(self) -> None:
        instructions = self.package / "03_ZOHO_INSTRUCTIONS"
        expected_results = (
            instructions / "04A_DASHBOARD_EXPECTED_RESULTS.md"
        )
        acceptance = (
            self.package
            / "04_VALIDATION_AND_LIMITATIONS"
            / "TRUTH_PACK"
            / "DASHBOARD_CHART_ACCEPTANCE.csv"
        )
        self.assertTrue(expected_results.is_file())
        self.assertTrue(acceptance.is_file())
        text = expected_results.read_text(encoding="utf-8")
        self.assertIn("Query 27 stockout action rows: **6**", text)
        self.assertEqual(2557, len(_read_rows(acceptance)))

    def test_current_stage_and_embed_guides_are_packaged(self) -> None:
        instructions = self.package / "03_ZOHO_INSTRUCTIONS"
        for filename in (
            "03B_CURRENT_WORKSPACE_MIGRATION.md",
            "04B_REFERENCE_TO_ZOHO_CAPABILITY_MATRIX.md",
            "07_EMBEDDED_PORTAL_SETUP.md",
            "08_PORTAL_HOSTING_AUTH_HANDOFF.md",
            "zoho-secured-embed-handoff.example.json",
        ):
            self.assertTrue((instructions / filename).is_file(), filename)
        handoff = (
            instructions / "zoho-secured-embed-handoff.example.json"
        ).read_text(encoding="utf-8")
        self.assertIn("abnah-zoho-secured-embed-handoff/v1", handoff)


if __name__ == "__main__":
    unittest.main()
