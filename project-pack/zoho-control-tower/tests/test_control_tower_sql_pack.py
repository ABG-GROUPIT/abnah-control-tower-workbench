from __future__ import annotations

import csv
import importlib.util
import sqlite3
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts" / "build_control_tower_v2_sql.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("control_tower_sql_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ControlTowerSqlPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = _load_builder()
        cls.builder.build()

    def test_query_pack_respects_zoho_dependency_limit(self) -> None:
        levels = self.builder.dependency_levels(self.builder.QUERIES)
        self.assertEqual(38, len(self.builder.QUERIES))
        self.assertLessEqual(max(levels.values()), 3)
        self.assertEqual({1, 2, 3}, set(levels.values()))

    def test_presentation_only_views_are_not_query_tables(self) -> None:
        query_names = {query.name for query in self.builder.QUERIES}
        self.assertTrue(query_names.isdisjoint(self.builder.REPORT_LAYER_VIEWS))
        self.assertTrue(query_names.isdisjoint(self.builder.GATED_QUERY_TABLES))

    def test_no_signal_source_fields_are_not_projected(self) -> None:
        query_sql = "\n".join(query.sql for query in self.builder.QUERIES)
        for source_field in ('p."pr_number"', 'f."receiver_store_kitchen_name"'):
            self.assertNotIn(source_field, query_sql)
        self.assertNotIn("RAWN_CT_enterprise_stock_return", query_sql)

        purchase_receipt = next(
            query
            for query in self.builder.QUERIES
            if query.name == "STD_CT_Purchase_Receipt"
        )
        self.assertNotIn(
            'e."batch_number"',
            purchase_receipt.sql,
            "The blank POSIST Entry batch field must not be treated as evidence",
        )

    def test_active_queries_do_not_use_unavailable_scenario_masters(self) -> None:
        blocked_sources = {
            "AUX_Item_Master",
            "AUX_Vendor_Master",
            "STD_CT_Expiry_Estimate",
        }
        query_names = {query.name for query in self.builder.QUERIES}
        self.assertTrue(query_names.isdisjoint(blocked_sources))
        for query in self.builder.QUERIES:
            self.assertTrue(
                blocked_sources.isdisjoint(query.sources),
                f"{query.name} still depends on an unavailable scenario source",
            )

    def test_demo_reference_extensions_are_non_disruptive(self) -> None:
        by_name = {query.name: query for query in self.builder.QUERIES}
        self.assertEqual(
            37,
            by_name["DIM_CT_Outlet_Enriched"].order,
        )
        self.assertEqual(
            ("DIM_CT_Outlet",),
            by_name["DIM_CT_Outlet_Enriched"].sources,
        )
        self.assertNotIn(
            "CAST(",
            by_name["DIM_CT_Outlet_Enriched"].sql,
        )
        self.assertEqual(
            38,
            by_name["FACT_CT_Expiry_Risk"].order,
        )
        self.assertEqual(
            ("AUX_Expiry_Estimate-Copy",),
            by_name["FACT_CT_Expiry_Risk"].sources,
        )
        inventory_risk = by_name["FACT_CT_Inventory_Risk"]
        self.assertNotIn("AUX_Expiry_Estimate-Copy", inventory_risk.sources)
        self.assertIn('"risk_type"', inventory_risk.sql)
        self.assertIn('"stockout_risk_severity"', inventory_risk.sql)
        self.assertNotIn('"expiry_risk_severity"', inventory_risk.sql)

        expiry_risk = by_name["FACT_CT_Expiry_Risk"]
        for projected_field in (
            '"batch_allocation_id"',
            '"receipt_date"',
            '"grn_number"',
            '"receipt_source_status"',
        ):
            self.assertIn(projected_field, expiry_risk.sql)
        self.assertIn(
            'WHEN e."risk_status" IN (\'EXPIRED\', \'EXPIRES_TODAY\')',
            expiry_risk.sql,
        )
        self.assertNotIn("CAST(", expiry_risk.sql)
        self.assertNotIn("CONCAT(", expiry_risk.sql)

    def test_enriched_outlet_sql_executes_from_existing_dimension(self) -> None:
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.row_factory = sqlite3.Row
        connection.execute(
            'CREATE TABLE "13_dim_ct_outlet.sql" '
            '("outlet_code", "outlet_name")'
        )
        connection.executemany(
            'INSERT INTO "13_dim_ct_outlet.sql" VALUES (?, ?)',
            (
                ("OUT001", "ABNAH Cafe Connaught Place"),
                ("OUT002", "ABNAH Cafe Hauz Khas"),
                ("OUT003", "ABNAH Cafe Saket Premium"),
            ),
        )
        query_path = (
            self.builder.OUTPUT / "37_dim_ct_outlet_enriched.sql"
        )
        sql = "\n".join(
            line
            for line in query_path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("--")
        )
        rows = connection.execute(sql).fetchall()
        self.assertEqual(3, len(rows))
        self.assertEqual("Connaught Place", rows[0]["market_area"])
        self.assertAlmostEqual(28.6315, rows[0]["latitude"])
        self.assertEqual("New", rows[2]["new_matured_flag"])
        self.assertEqual(1, rows[2]["is_synthetic"])

    def test_expiry_risk_sql_executes_over_packaged_scenario(self) -> None:
        source_path = (
            ROOT
            / "exports"
            / "control_tower_zoho"
            / "AUX_Expiry_Estimate.csv"
        )
        with source_path.open(encoding="utf-8-sig", newline="") as handle:
            source_rows = list(csv.DictReader(handle))
        self.assertEqual(206, len(source_rows))
        columns = list(source_rows[0])

        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.row_factory = sqlite3.Row
        definition = ", ".join(f'"{column}"' for column in columns)
        connection.execute(
            f'CREATE TABLE "AUX_Expiry_Estimate-Copy" ({definition})'
        )
        placeholders = ", ".join("?" for _ in columns)
        connection.executemany(
            f'INSERT INTO "AUX_Expiry_Estimate-Copy" '
            f"VALUES ({placeholders})",
            (
                tuple(row[column] for column in columns)
                for row in source_rows
            ),
        )

        query_path = self.builder.OUTPUT / "38_fact_ct_expiry_risk.sql"
        sql = "\n".join(
            line
            for line in query_path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("--")
        )
        rows = connection.execute(sql).fetchall()
        self.assertEqual(206, len(rows))
        severity_counts: dict[str, int] = {}
        for row in rows:
            severity = row["risk_severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        self.assertEqual(
            {"PURPLE": 35, "RED": 92, "AMBER": 79},
            severity_counts,
        )
        self.assertEqual(
            206,
            len({row["action_id"] for row in rows}),
        )
        self.assertEqual(
            {
                "demo_only_no_posist_batch_or_expiry_source",
            },
            {row["production_use_status"] for row in rows},
        )

    def test_vendor_report_is_quality_gated_and_used_as_the_master(self) -> None:
        std_vendor = next(
            query
            for query in self.builder.QUERIES
            if query.name == "STD_CT_Vendor_Report"
        )
        dim_vendor = next(
            query
            for query in self.builder.QUERIES
            if query.name == "DIM_CT_Vendor"
        )
        self.assertEqual(("RAWN_CT_vendor_report-Copy",), std_vendor.sources)
        self.assertIn("STD_CT_Vendor_Report", dim_vendor.sources)
        self.assertIn("'vendor_report' AS \"source_evidence\"", dim_vendor.sql)
        self.assertIn(
            "'observed_in_po_or_entry_only' AS \"source_evidence\"",
            dim_vendor.sql,
        )

    def test_every_import_reference_uses_existing_copy_table_name(self) -> None:
        query_sql = "\n".join(query.sql for query in self.builder.QUERIES)
        query_sources = {
            source for query in self.builder.QUERIES for source in query.sources
        }
        reference_only_imports = {"AUX_Outlet_Master"}
        for logical_name, zoho_name in self.builder.ZOHO_IMPORT_TABLE_NAMES.items():
            self.assertNotIn(f'"{logical_name}"', query_sql)
            if logical_name in reference_only_imports:
                self.assertNotIn(f'"{zoho_name}"', query_sql)
                self.assertNotIn(zoho_name, query_sources)
                continue
            self.assertIn(f'"{zoho_name}"', query_sql)
            self.assertIn(zoho_name, query_sources)

    def test_menu_profitability_uses_recipe_cogs(self) -> None:
        query = next(
            query
            for query in self.builder.QUERIES
            if query.name == "FACT_CT_Menu_Profitability"
        )
        self.assertIn("theoretical_cost_per_menu_unit", query.sql)
        self.assertNotIn(
            'SUM(s."source_purchase_value") AS "theoretical_cogs"',
            query.sql,
        )

    def test_generated_sql_file_count(self) -> None:
        files = list(self.builder.OUTPUT.glob("*.sql"))
        self.assertEqual(len(self.builder.QUERIES), len(files))

    def test_generated_sql_uses_exact_filename_query_table_names(self) -> None:
        for query in self.builder.QUERIES:
            rendered = (self.builder.OUTPUT / query.filename).read_text(
                encoding="utf-8"
            )
            self.assertIn(f"-- Query Table: {query.filename}", rendered)
            for source in query.sources:
                if source not in self.builder.QUERY_TABLE_NAME_BY_LOGICAL:
                    continue
                physical_name = self.builder.QUERY_TABLE_NAME_BY_LOGICAL[source]
                self.assertIn(f'"{physical_name}"', rendered)
                self.assertNotIn(f'"{source}"', rendered)

        with (
            self.builder.OUTPUT / "QUERY_TABLE_MANIFEST.csv"
        ).open(encoding="utf-8-sig", newline="") as handle:
            manifest = list(csv.DictReader(handle))
        self.assertEqual(
            [query.filename for query in self.builder.QUERIES],
            [row["query_table_name"] for row in manifest],
        )
        self.assertEqual(
            [query.name for query in self.builder.QUERIES],
            [row["logical_model_name"] for row in manifest],
        )

    def test_standardized_key_columns_have_explicit_output_aliases(self) -> None:
        expected_aliases = {
            "STD_CT_Sales_Item": (
                's."item_code" AS "item_code"',
                's."item_name" AS "item_name"',
            ),
            "STD_CT_Inventory_Period": (
                'v."item_code" AS "item_code"',
                'v."source_period_code" AS "source_period_code"',
            ),
            "STD_CT_Purchase_Order": (
                'p."po_number" AS "po_number"',
                'p."vendor_name" AS "vendor_name"',
            ),
            "STD_CT_Vendor_Report": (
                'v."vendor_code" AS "vendor_code"',
                'v."vendor_name" AS "vendor_name"',
            ),
        }
        by_name = {query.name: query.sql for query in self.builder.QUERIES}
        for query_name, aliases in expected_aliases.items():
            for alias in aliases:
                self.assertIn(alias, by_name[query_name])

    def test_simple_projection_aliasing_is_idempotent(self) -> None:
        for query in self.builder.QUERIES:
            self.assertEqual(
                query.sql.rstrip(),
                self.builder.alias_simple_projection_columns(query.sql.rstrip()),
                query.name,
            )

    def test_po_receipt_derived_table_publishes_join_keys(self) -> None:
        query = next(
            query
            for query in self.builder.QUERIES
            if query.name == "FACT_CT_PO_Receipt_Line"
        )
        for alias in (
            'e."source_period_code" AS "source_period_code"',
            'e."outlet_code" AS "outlet_code"',
            'e."po_number" AS "po_number"',
            'e."item_code" AS "item_code"',
        ):
            self.assertIn(alias, query.sql)

    def test_cte_queries_follow_zoho_constraints(self) -> None:
        cte_queries = [
            query
            for query in self.builder.QUERIES
            if query.sql.lstrip().upper().startswith("WITH ")
        ]
        self.assertEqual(
            {
                "FACT_CT_Menu_Impact",
                "FACT_CT_Risky_PO",
            },
            {query.name for query in cte_queries},
        )
        for query in cte_queries:
            self.assertLessEqual(
                len(self.builder.CTE_DEFINITION_RE.findall(query.sql)),
                3,
                query.name,
            )
            self.assertIsNone(
                self.builder.DERIVED_SUBQUERY_RE.search(query.sql),
                query.name,
            )

        inventory_risk = next(
            query
            for query in self.builder.QUERIES
            if query.name == "FACT_CT_Inventory_Risk"
        )
        self.assertFalse(inventory_risk.sql.lstrip().upper().startswith("WITH "))
        self.assertEqual(
            1,
            self.builder.max_derived_subquery_depth(inventory_risk.sql),
        )
        self.assertIn(
            'FROM "STD_CT_Inventory_Snapshot" s',
            inventory_risk.sql,
        )

    def test_from_subqueries_do_not_exceed_zoho_depth_limit(self) -> None:
        for query in self.builder.QUERIES:
            self.assertLessEqual(
                self.builder.max_derived_subquery_depth(query.sql),
                1,
                query.name,
            )

    def test_every_query_dependency_is_built_earlier(self) -> None:
        order = {query.name: query.order for query in self.builder.QUERIES}
        for query in self.builder.QUERIES:
            for source in query.sources:
                if source in order:
                    self.assertLess(
                        order[source],
                        query.order,
                        f"{query.name} depends on {source} before it is available",
                    )

    def test_po_receipt_and_risk_paths_remain_within_three_levels(self) -> None:
        levels = self.builder.dependency_levels(self.builder.QUERIES)
        self.assertEqual(2, levels["FACT_CT_PO_Receipt_Line"])
        self.assertEqual(3, levels["SUM_CT_Vendor_Scorecard"])
        self.assertEqual(3, levels["FACT_CT_Risky_PO"])
        self.assertEqual(3, levels["FACT_CT_Menu_Impact"])

    def test_inventory_risk_sql_executes_without_cte(self) -> None:
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.row_factory = sqlite3.Row
        connection.create_function(
            "CONCAT",
            -1,
            lambda *values: "".join(
                "" if value is None else str(value) for value in values
            ),
        )
        tables = {
            "26_fact_ct_forecast_ingredient_demand.sql": (
                "source_period_code",
                "outlet_code",
                "item_code",
                "forecast_ingredient_qty",
            ),
            "22_fact_ct_purchase_order.sql": (
                "source_period_code",
                "outlet_code",
                "item_code",
                "remaining_qty",
                "open_po_value",
                "po_number",
                "is_open_po",
            ),
            "05_std_ct_inventory_snapshot.sql": (
                "source_period_code",
                "snapshot_date",
                "outlet_code",
                "outlet_name",
                "item_code",
                "item_name",
                "category_name",
                "super_category_name",
                "canonical_uom",
                "average_unit_cost",
                "closing_qty",
                "closing_value",
            ),
        }
        for table_name, columns in tables.items():
            definition = ", ".join(f'"{column}"' for column in columns)
            connection.execute(
                f'CREATE TABLE "{table_name}" ({definition})'
            )

        connection.execute(
            'INSERT INTO "05_std_ct_inventory_snapshot.sql" VALUES '
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "month_01",
                "2026-01-31",
                "OUT001",
                "Test Outlet",
                "ING001",
                "Test Ingredient",
                "Dairy",
                "Raw Material",
                "litre",
                10,
                0,
                0,
            ),
        )
        connection.execute(
            'INSERT INTO "26_fact_ct_forecast_ingredient_demand.sql" '
            "VALUES (?, ?, ?, ?)",
            ("month_01", "OUT001", "ING001", 5),
        )
        connection.execute(
            'INSERT INTO "22_fact_ct_purchase_order.sql" '
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("month_01", "OUT001", "ING001", 2, 20, "PO-001", 1),
        )
        query_path = (
            self.builder.OUTPUT / "27_fact_ct_inventory_risk.sql"
        )
        sql = "\n".join(
            line
            for line in query_path.read_text(encoding="utf-8").splitlines()
            if not line.startswith("--")
        )
        row = connection.execute(sql).fetchone()
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual("STOCKOUT", row["risk_type"])
        self.assertEqual("PURPLE", row["risk_severity"])
        self.assertAlmostEqual(3.75, row["shortage_qty"])
        self.assertAlmostEqual(37.5, row["total_risk_value"])
        self.assertEqual("Expedite existing PO", row["recommended_action"])
        self.assertEqual("Procurement", row["action_owner"])
        self.assertEqual("Due today", row["due_band"])

    def test_otif_uses_exact_line_linkage_and_eligible_closed_denominator(self) -> None:
        line = next(
            query
            for query in self.builder.QUERIES
            if query.name == "FACT_CT_PO_Receipt_Line"
        )
        for join_key in (
            'p."outlet_code" = r."outlet_code"',
            'p."po_number" = r."po_number"',
            'p."item_code" = r."item_code"',
            'p."source_period_code" = r."source_period_code"',
        ):
            self.assertIn(join_key, line.sql)
        self.assertIn('"eligible_closed_line_flag"', line.sql)
        self.assertIn('"otif_success_flag"', line.sql)

        summary = next(
            query
            for query in self.builder.QUERIES
            if query.name == "SUM_CT_Vendor_Scorecard"
        )
        self.assertIn('SUM(v."otif_success_flag")', summary.sql)
        self.assertIn('SUM(v."eligible_closed_line_flag")', summary.sql)


if __name__ == "__main__":
    unittest.main()
