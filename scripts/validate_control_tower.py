#!/usr/bin/env python3
"""Validate the control-tower requirements, source queue, and draft KPI contract."""

from __future__ import annotations

import json
from pathlib import Path


def duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return repeated


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    generated = root / "schema-pack" / "generated"
    requirements = json.loads(
        (generated / "control-tower-requirements.json").read_text(encoding="utf-8")
    )
    lineage = json.loads((generated / "kpi-lineage.json").read_text(encoding="utf-8"))
    architecture = json.loads(
        (generated / "control-tower-architecture.json").read_text(encoding="utf-8")
    )
    atlas = json.loads((generated / "atlas.json").read_text(encoding="utf-8"))
    errors: list[str] = []

    if requirements.get("contractVersion") != "1.0.0":
        errors.append("Unexpected control-tower contract version.")
    if requirements.get("status") != "requirements_received_pending_source_validation":
        errors.append("Unexpected control-tower status.")
    if "No screenshots" not in requirements.get("sourcePolicy", ""):
        errors.append("Control-tower source policy must explicitly exclude screenshots.")
    if requirements.get("terminology", {}).get("preferredTerm") != "consumption":
        errors.append("Page 3 preferred terminology must be consumption.")

    pages = requirements.get("pages", [])
    kpis = requirements.get("kpis", [])
    if [page.get("number") for page in pages] != [1, 2, 3, 4]:
        errors.append("Control tower must contain pages 1 through 4 in order.")

    page_ids = [page.get("id", "") for page in pages]
    kpi_ids = [kpi.get("id", "") for kpi in kpis]
    if "" in page_ids or duplicates(page_ids):
        errors.append(f"Control-tower page ids are empty or duplicated: {duplicates(page_ids)}")
    if "" in kpi_ids or duplicates(kpi_ids):
        errors.append(f"Control-tower KPI ids are empty or duplicated: {duplicates(kpi_ids)}")

    page_id_set = set(page_ids)
    kpi_id_set = set(kpi_ids)
    for page in pages:
        missing = set(page.get("kpiIds", [])) - kpi_id_set
        if missing:
            errors.append(f"Page {page.get('id')} references missing KPIs: {sorted(missing)}")
        if "yield" in json.dumps(page).lower():
            errors.append(f"Page {page.get('id')} still uses yield terminology.")
    for kpi in kpis:
        if kpi.get("pageId") not in page_id_set:
            errors.append(f"KPI {kpi.get('id')} references an unknown page.")
        if kpi.get("approvalStatus") not in {"draft", "approved", "retired"}:
            errors.append(f"KPI {kpi.get('id')} has an invalid approval status.")
        if not all(kpi.get(field) for field in ("name", "businessDefinition", "formula", "grain", "owner", "validationStatus")):
            errors.append(f"KPI {kpi.get('id')} is missing a required definition field.")
        if "yield" in json.dumps(kpi).lower():
            errors.append(f"KPI {kpi.get('id')} still uses yield terminology.")

    report_ids = {report["id"] for report in atlas.get("reports", [])}
    endpoint_ids = {endpoint["id"] for endpoint in atlas.get("api_endpoints", [])}
    checkpoint_id = requirements.get("discoveryProgress", {}).get("reportId", "")
    if checkpoint_id not in report_ids:
        errors.append("Discovery checkpoint references an unknown report.")

    captured_candidate_ids: list[str] = []
    for group in requirements.get("capturePlan", {}).get("groups", []):
        if group.get("priority") not in {"P0", "P1", "P2"}:
            errors.append(f"Capture group {group.get('id')} has an invalid priority.")
        for report in group.get("reports", []):
            report_id = report.get("reportId", "")
            captured_candidate_ids.append(report_id)
            if report_id not in report_ids:
                errors.append(f"Capture plan references unknown report: {report_id}")
    repeated_candidates = duplicates(captured_candidate_ids)
    if repeated_candidates:
        errors.append(f"Capture candidates appear in multiple groups: {sorted(repeated_candidates)}")

    for endpoint in requirements.get("apiAssessment", {}).get("endpoints", []):
        endpoint_id = endpoint.get("endpointId", "")
        if endpoint_id not in endpoint_ids:
            errors.append(f"API assessment references unknown endpoint: {endpoint_id}")
        if endpoint.get("status") != "candidate":
            errors.append(f"Endpoint {endpoint_id} must remain candidate until UAT evidence exists.")

    lineage_kpis = {item.get("id"): item for item in lineage.get("kpis", [])}
    if set(lineage_kpis) != kpi_id_set:
        errors.append("Generated KPI lineage definitions do not match the control-tower KPI register.")
    for kpi in kpis:
        lineage_kpi = lineage_kpis.get(kpi["id"], {})
        for field in ("name", "businessDefinition", "formula", "grain", "owner", "approvalStatus", "validationStatus"):
            if lineage_kpi.get(field) != kpi.get(field):
                errors.append(f"Lineage KPI {kpi['id']} differs from control-tower field {field}.")
    if lineage.get("status") != "requirements_received":
        errors.append("KPI lineage must record that business requirements were received.")
    if any(lineage.get(collection) for collection in ("nodes", "edges", "publications")):
        errors.append("Lineage nodes, edges, and publications must remain empty until source mapping is selected.")

    if architecture.get("contractVersion") != "1.0.0":
        errors.append("Unexpected planned architecture contract version.")
    if architecture.get("status") != "planned_architecture_under_feasibility_validation":
        errors.append("Unexpected planned architecture status.")
    architecture_text = json.dumps(architecture)
    if "No screenshots" not in architecture.get("sourcePolicy", ""):
        errors.append("Planned architecture source policy must explicitly exclude screenshots.")
    if any(token in architecture_text for token in (".png", ".jpeg", ".jpg", "AppData\\\\Local", "Downloads\\\\")):
        errors.append("Planned architecture contains a screenshot or local-path reference.")

    expected_layers = ["source", "raw", "standardized", "dimension", "fact", "summary", "kpi", "experience"]
    layers = architecture.get("layers", [])
    layer_ids = [item.get("id", "") for item in layers]
    if layer_ids != expected_layers:
        errors.append(f"Planned architecture layers are missing or out of order: {layer_ids}")
    layer_order = {item.get("id"): item.get("order", 0) for item in layers}

    source_nodes = architecture.get("sourceNodes", [])
    model_nodes = architecture.get("modelNodes", [])
    architecture_nodes = source_nodes + model_nodes
    architecture_node_ids = [item.get("id", "") for item in architecture_nodes]
    architecture_node_set = set(architecture_node_ids)
    if "" in architecture_node_ids or duplicates(architecture_node_ids):
        errors.append(f"Architecture node ids are empty or duplicated: {duplicates(architecture_node_ids)}")
    if len([item for item in source_nodes if item.get("kind") == "report"]) != 21:
        errors.append("Planned architecture must contain exactly 21 selected/control report screens.")
    if len([item for item in source_nodes if item.get("kind") == "master"]) != 2:
        errors.append("Planned architecture must contain Outlet Master and Vendor Master.")
    if any(item.get("label") == "Enterprise Purchase Order" for item in source_nodes):
        errors.append("Empty Enterprise Purchase Order must not be a planned source node.")
    if not any(item.get("id") == "src_purchase_order" for item in source_nodes):
        errors.append("Purchase Order Report must be the planned PO source authority.")

    group_ids = {item.get("id") for item in architecture.get("groups", [])}
    for node in architecture_nodes:
        node_id = node.get("id", "")
        if node.get("layerId") not in layer_order:
            errors.append(f"Architecture node {node_id} references an unknown layer.")
        if node.get("groupId") not in group_ids:
            errors.append(f"Architecture node {node_id} references an unknown group.")
        if not node.get("pages") or set(node.get("pages", [])) - page_id_set:
            errors.append(f"Architecture node {node_id} has invalid page coverage.")
        if not all(node.get(field) for field in ("label", "description", "status", "role", "logic")):
            errors.append(f"Architecture node {node_id} is missing presentation metadata.")
        missing_inputs = set(node.get("inputs", [])) - architecture_node_set
        if missing_inputs:
            errors.append(f"Architecture node {node_id} references missing inputs: {sorted(missing_inputs)}")
        for input_id in node.get("inputs", []):
            upstream = next((item for item in architecture_nodes if item.get("id") == input_id), None)
            if upstream and layer_order.get(upstream.get("layerId"), 0) > layer_order.get(node.get("layerId"), 0):
                errors.append(f"Architecture edge {input_id} -> {node_id} runs backwards across layers.")
        report_id = node.get("reportId")
        if report_id and report_id not in report_ids:
            errors.append(f"Architecture source {node_id} references unknown report: {report_id}")
        if node.get("kind") == "report" and not report_id and node.get("catalogState") != "external_reference":
            errors.append(f"Architecture report {node_id} needs a catalog id or external-reference state.")

    routed_kpis: list[str] = []
    for route in architecture.get("kpiRoutes", []):
        summary_id = route.get("summaryNodeId", "")
        if summary_id not in architecture_node_set:
            errors.append(f"KPI route references missing summary node: {summary_id}")
        elif next(item for item in architecture_nodes if item.get("id") == summary_id).get("layerId") != "summary":
            errors.append(f"KPI route source is not a summary node: {summary_id}")
        routed_kpis.extend(route.get("kpiIds", []))
    if set(routed_kpis) != kpi_id_set or duplicates(routed_kpis):
        errors.append("Planned architecture must route every control-tower KPI exactly once.")

    decision_ids = [item.get("id", "") for item in architecture.get("decisions", [])]
    if "" in decision_ids or duplicates(decision_ids):
        errors.append("Planned architecture decisions need unique non-empty ids.")

    if errors:
        print("Control-tower validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    capture_count = len(captured_candidate_ids)
    print(
        "Control-tower validation passed: "
        f"{len(pages)} pages, {len(kpis)} draft KPIs, {capture_count} report candidates, "
        f"{len(requirements['apiAssessment']['endpoints'])} API candidates, "
        f"{len(source_nodes)} architecture sources and {len(model_nodes)} planned model nodes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
