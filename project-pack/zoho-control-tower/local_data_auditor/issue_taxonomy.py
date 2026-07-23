"""Shared severity and interpretation taxonomy for ABNAH audit evidence."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any


SEVERITY_ORDER = {
    "info": 0,
    "minor": 1,
    "major": 2,
    "critical": 3,
}


def decimal_or_none(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return None


def numeric_delta(expected: Any, observed: Any) -> dict[str, Any] | None:
    expected_value = decimal_or_none(expected)
    observed_value = decimal_or_none(observed)
    if expected_value is None or observed_value is None:
        return None
    absolute = abs(expected_value - observed_value)
    denominator = max(abs(expected_value), Decimal("0.01"))
    percent = absolute / denominator * Decimal("100")
    return {
        "expected": expected_value,
        "observed": observed_value,
        "absolute": absolute,
        "percent": percent,
    }


def classify_numeric_delta(expected: Any, observed: Any) -> dict[str, Any]:
    """Classify a genuine numeric mismatch by materiality.

    The first envelope absorbs normal display precision. A 520.84 versus 520
    mismatch is retained as minor, while a sub-paise residual is informational.
    """

    delta = numeric_delta(expected, observed)
    if delta is None:
        return {
            "severity": "major",
            "impact_abs": "",
            "impact_pct": "",
        }

    absolute = delta["absolute"]
    percent = delta["percent"]
    if absolute <= Decimal("0.05") or percent <= Decimal("0.01"):
        severity = "info"
    elif absolute <= Decimal("1") or percent <= Decimal("0.25"):
        severity = "minor"
    elif absolute <= Decimal("100") or percent <= Decimal("2"):
        severity = "major"
    else:
        severity = "critical"
    return {
        "severity": severity,
        "impact_abs": f"{absolute:f}",
        "impact_pct": f"{percent:.4f}",
    }


def highest_severity(values: list[str] | tuple[str, ...]) -> str:
    return max(values or ["info"], key=lambda value: SEVERITY_ORDER.get(value, -1))


def classify_deterministic_issue(issue: dict[str, Any]) -> dict[str, Any]:
    phase = str(issue.get("phase", "")).casefold()
    rule_id = str(issue.get("rule_id", "")).casefold()
    original = str(issue.get("severity", "")).casefold()
    delta = numeric_delta(issue.get("expected"), issue.get("observed"))

    if phase in {"schema", "structure", "type"} or original == "error":
        severity = "critical"
        issue_class = "structure" if phase != "type" else "type"
        state = "confirmed_issue"
        impact = {"impact_abs": "", "impact_pct": ""}
    elif phase == "coverage" or rule_id == "header_only_export":
        severity = "critical"
        issue_class = "coverage"
        state = "confirmed_issue"
        impact = {"impact_abs": "", "impact_pct": ""}
    elif delta is not None:
        impact = classify_numeric_delta(issue.get("expected"), issue.get("observed"))
        severity = impact["severity"]
        issue_class = "reconciliation"
        state = "needs_business_definition"
    else:
        severity = "major" if original in {"warning", "review"} else "info"
        issue_class = "business_logic" if phase == "business" else "completeness"
        state = "needs_business_definition"
        impact = {"impact_abs": "", "impact_pct": ""}

    return {
        "severity": severity,
        "issue_class": issue_class,
        "state": state,
        "confidence": "high" if state == "confirmed_issue" else "medium",
        **impact,
    }
