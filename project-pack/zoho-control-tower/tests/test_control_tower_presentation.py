import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_control_tower_presentation.py"
SPEC = importlib.util.spec_from_file_location("control_tower_presentation", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ControlTowerPresentationTests(unittest.TestCase):
    def test_story_register_is_complete_and_unique(self):
        contract = MODULE.build_presentation_contract()
        stories = contract["stories"]

        self.assertEqual(len(stories), 76)
        self.assertEqual(len({story["id"] for story in stories}), 76)
        self.assertEqual(
            {"kpi": 33, "chart": 22, "table": 21},
            {
                kind: sum(story["kind"] == kind for story in stories)
                for kind in ("kpi", "chart", "table")
            },
        )
        self.assertTrue(
            all(story["sourceTable"] in contract["sourceProfiles"] for story in stories)
        )

    def test_model_catalog_contains_exact_query_sequence(self):
        model = MODULE.build_model_catalog()

        self.assertEqual(len(model["tables"]), 38)
        self.assertEqual(
            [table["buildOrder"] for table in model["tables"]],
            list(range(1, 39)),
        )
        self.assertTrue(all("-- Query Table:" in table["sql"] for table in model["tables"]))

    def test_hosted_contract_excludes_local_and_sensitive_evidence(self):
        contract = MODULE.build_presentation_contract()
        text = str(contract).lower()

        for token in ("c:\\users", "downloads\\", ".png", ".jpeg", "customer name"):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
