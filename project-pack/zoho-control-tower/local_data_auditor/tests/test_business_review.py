import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from business_review import magnitude_severity, unit_basis  # noqa: E402
from issue_taxonomy import classify_deterministic_issue, classify_numeric_delta  # noqa: E402


class BusinessReviewTests(unittest.TestCase):
    def test_bounded_numeric_drift_is_minor(self):
        result = classify_numeric_delta("520.84", "520")
        self.assertEqual(result["severity"], "minor")

    def test_display_precision_residual_is_informational(self):
        result = classify_numeric_delta("288173.43", "288173.37")
        self.assertEqual(result["severity"], "info")

    def test_structure_and_type_failures_are_critical(self):
        result = classify_deterministic_issue(
            {"phase": "type", "severity": "error", "expected": "", "observed": ""}
        )
        self.assertEqual(result["severity"], "critical")
        self.assertEqual(result["state"], "confirmed_issue")

    def test_business_formula_mismatch_needs_definition(self):
        result = classify_deterministic_issue(
            {
                "phase": "business",
                "severity": "review",
                "expected": "520.84",
                "observed": "520",
            }
        )
        self.assertEqual(result["severity"], "minor")
        self.assertEqual(result["issue_class"], "reconciliation")
        self.assertEqual(result["state"], "needs_business_definition")

    def test_pack_units_resolve_to_base_unit_and_factor(self):
        self.assertEqual(unit_basis("PKT (500 GM)"), ("GM", Decimal("500")))
        self.assertEqual(unit_basis("Case (12000 ML)"), ("ML", Decimal("12000")))
        self.assertEqual(unit_basis("GRAM"), ("GM", Decimal("1")))

    def test_operational_magnitude_tiers(self):
        self.assertEqual(magnitude_severity(Decimal("20"), Decimal("0.1")), "minor")
        self.assertEqual(magnitude_severity(Decimal("900"), Decimal("2")), "major")
        self.assertEqual(magnitude_severity(Decimal("6000"), Decimal("2")), "critical")


if __name__ == "__main__":
    unittest.main()
