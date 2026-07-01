#!/usr/bin/env python3
"""Validate Spec Kit visual requirements/spec structured asset package intake artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from intake_validator_common import (
    emit,
    is_truthy,
    load_yaml,
    non_empty,
    parse_evidence_packet_status,
    validate_json_schema,
)


BLOCKERS = {
    "SOURCE_INTAKE_BLOCKED": "VISUAL_SPEC_SOURCE_INTAKE_BLOCKED",
    "REQUIRED_ARTIFACT_MISSING": "VISUAL_SPEC_REQUIRED_ARTIFACT_MISSING",
    "SCHEMA_INVALID": "VISUAL_SPEC_SCHEMA_INVALID",
    "INTAKE_INCOMPLETE": "VISUAL_SPEC_INTAKE_INCOMPLETE",
    "PROVIDER_EVIDENCE_MISSING": "VISUAL_SPEC_PROVIDER_EVIDENCE_MISSING",
    "PRODUCT_AMBIGUITY_UNRESOLVED": "VISUAL_SPEC_PRODUCT_AMBIGUITY_UNRESOLVED",
    "ASSERTION_COVERAGE_INCOMPLETE": "VISUAL_SPEC_ASSERTION_COVERAGE_INCOMPLETE",
    "LOCATOR_STRATEGY_INVALID": "VISUAL_SPEC_LOCATOR_STRATEGY_INVALID",
    "DOWNSTREAM_OWNERSHIP_LEAK": "VISUAL_SPEC_DOWNSTREAM_OWNERSHIP_LEAK",
    "READY_WITHOUT_EVIDENCE": "VISUAL_SPEC_READY_WITHOUT_EVIDENCE",
}

FORBIDDEN_FIELD_NAMES = {
    "requirement_id",
    "requirement_ids",
    "task_id",
    "task_ids",
    "implementation_task",
    "implementation_tasks",
    "code_component",
    "code_components",
    "component_name",
    "component_names",
    "css_selector",
    "xpath",
    "selector",
}
FORBIDDEN_LOCATOR_PATTERNS = [
    re.compile(r"^\s*[.#][A-Za-z0-9_-]+"),
    re.compile(r"^\s*//"),
    re.compile(r"^\s*/html\b"),
    re.compile(r"\b(css|xpath|querySelector)\b", re.IGNORECASE),
]
PRODUCT_AMBIGUITY_MARKERS = {
    "PRODUCT_AMBIGUITY",
    "PRODUCT_AMBIGUITY_UNRESOLVED",
    "VISUAL_SPEC_PRODUCT_AMBIGUITY_UNRESOLVED",
}
PROVIDER_EVIDENCE_MARKERS = {
    "MISSING_PROVIDER_EVIDENCE",
    "PROVIDER_EVIDENCE_MISSING",
    "VISUAL_SPEC_PROVIDER_EVIDENCE_MISSING",
}
LOCATOR_MARKERS = {"LOCATOR_STRATEGY_INVALID", "VISUAL_SPEC_LOCATOR_STRATEGY_INVALID"}
OWNERSHIP_MARKERS = {"DOWNSTREAM_OWNERSHIP_LEAK", "VISUAL_SPEC_DOWNSTREAM_OWNERSHIP_LEAK"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", help="Directory containing visual spec package artifacts")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    package_dir = Path(args.package_dir)
    blocker_codes: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {"package_dir": str(package_dir)}

    if not package_dir.exists() or not package_dir.is_dir():
        blocker_codes.extend(
            [
                BLOCKERS["SOURCE_INTAKE_BLOCKED"],
                BLOCKERS["REQUIRED_ARTIFACT_MISSING"],
                BLOCKERS["READY_WITHOUT_EVIDENCE"],
            ]
        )
        return emit(
            label="Visual Spec Package",
            json_mode=args.json,
            details=details,
            blockers=blocker_codes,
            warnings=warnings,
        )

    validate_source_intake(package_dir, details, blocker_codes)
    package_doc = validate_visual_spec_package(package_dir, details, blocker_codes)
    assertions_doc = validate_visual_spec_assertions(package_dir, details, blocker_codes)
    validate_cross_references(package_doc, assertions_doc, details, blocker_codes)
    validate_visual_spec_evidence_packet(package_dir, details, blocker_codes, warnings)

    return emit(
        label="Visual Spec Package",
        json_mode=args.json,
        details=details,
        blockers=blocker_codes,
        warnings=warnings,
    )


def validate_source_intake(
    package_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    upstream = package_dir.parent
    packet = upstream / "visual-evidence-packet.md"
    if not packet.exists():
        details["source_intake"] = {"missing": True}
        blocker_codes.append(BLOCKERS["SOURCE_INTAKE_BLOCKED"])
        return

    packet_status = parse_evidence_packet_status(packet.read_text(encoding="utf-8", errors="replace"))
    metadata = packet_status["metadata"]
    details["source_intake"] = {
        "path": str(packet),
        "ready_gate": packet_status["ready_gate"],
        "blockers": metadata.get("blockers"),
        "errors": packet_status["errors"],
    }
    source_blockers = metadata.get("blockers")
    if (
        packet_status["ready_gate"] != "PASS"
        or packet_status["errors"]
        or (isinstance(source_blockers, list) and source_blockers)
    ):
        blocker_codes.append(BLOCKERS["SOURCE_INTAKE_BLOCKED"])


def validate_visual_spec_package(
    package_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> dict[str, Any]:
    package_path = package_dir / "visual-spec.yaml"
    if not package_path.exists():
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])
        details["visual_spec_package"] = {"missing": True}
        return {}

    validate_json_schema(
        instance_path=package_path,
        schema_name="visual-spec-package.schema.json",
        details_key="visual_spec_package",
        details=details,
        blocker_codes=blocker_codes,
        schema_error_code=BLOCKERS["SCHEMA_INVALID"],
    )

    package_doc = load_yaml(package_path)
    items = package_doc.get("items")
    if not isinstance(items, list):
        items = []

    declared_count = parse_count(package_doc.get("visual_spec_item_count"), len(items))
    item_errors: list[dict[str, Any]] = []
    invalid_locators: list[str] = []
    ownership_leaks: list[str] = []
    provider_evidence_gaps: list[str] = []
    product_ambiguity_gaps: list[str] = []
    blocker_lint_items: list[str] = []
    has_ready_item = False

    details["visual_spec_package"] = {
        "visual_spec_package_complete": package_doc.get("visual_spec_package_complete"),
        "source_refs_complete": package_doc.get("source_refs_complete"),
        "provider_evidence_complete": package_doc.get("provider_evidence_complete"),
        "product_ambiguities_recorded": package_doc.get("product_ambiguities_recorded"),
        "resources_traceable_to_design_source": package_doc.get("resources_traceable_to_design_source"),
        "downstream_ownership_free": package_doc.get("downstream_ownership_free"),
        "visual_spec_item_count": declared_count,
        "actual_item_count": len(items),
        "blocker_lint_errors": package_doc.get("blocker_lint_errors"),
    }

    if not is_truthy(package_doc.get("visual_spec_package_complete")) or declared_count <= 0:
        blocker_codes.append(BLOCKERS["INTAKE_INCOMPLETE"])
    if declared_count != len(items):
        blocker_codes.append(BLOCKERS["INTAKE_INCOMPLETE"])
    if not is_truthy(package_doc.get("source_refs_complete")):
        blocker_codes.append(BLOCKERS["PROVIDER_EVIDENCE_MISSING"])
    if not is_truthy(package_doc.get("provider_evidence_complete")):
        blocker_codes.append(BLOCKERS["PROVIDER_EVIDENCE_MISSING"])
    if not is_truthy(package_doc.get("resources_traceable_to_design_source")):
        blocker_codes.append(BLOCKERS["PROVIDER_EVIDENCE_MISSING"])
    if not is_truthy(package_doc.get("product_ambiguities_recorded")):
        blocker_codes.append(BLOCKERS["PRODUCT_AMBIGUITY_UNRESOLVED"])
    if not is_truthy(package_doc.get("downstream_ownership_free")):
        blocker_codes.append(BLOCKERS["DOWNSTREAM_OWNERSHIP_LEAK"])
    if non_empty(package_doc.get("product_ambiguities")):
        blocker_codes.append(BLOCKERS["PRODUCT_AMBIGUITY_UNRESOLVED"])
    if non_empty(package_doc.get("blocker_lint_errors")):
        blocker_codes.append(BLOCKERS["INTAKE_INCOMPLETE"])

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            item_errors.append({"index": index, "error": "item must be a mapping"})
            continue

        item_id = str(item.get("id") or f"item-{index}")
        if item.get("status") == "ready":
            has_ready_item = True

        required_non_empty = [
            "id",
            "source_refs",
            "page",
            "region",
            "role",
            "state",
            "viewport",
            "locator",
            "expectations",
            "acceptance_intent",
            "evidence_type",
            "confidence",
            "status",
        ]
        missing = [
            field
            for field in required_non_empty
            if not non_empty(item.get(field))
        ]
        if "blockers" not in item:
            missing.append("blockers")
        if missing:
            item_errors.append({"id": item_id, "missing_fields": missing})

        if not valid_source_refs(item.get("source_refs")):
            provider_evidence_gaps.append(item_id)

        evidence_type = str(item.get("evidence_type") or "")
        if evidence_type in {"missing", "unsupported"} or non_empty(item.get("missing_evidence")):
            provider_evidence_gaps.append(item_id)

        blockers = as_string_set(item.get("blockers"))
        if blockers:
            blocker_lint_items.append(item_id)
        if blockers & PROVIDER_EVIDENCE_MARKERS:
            provider_evidence_gaps.append(item_id)
        if blockers & PRODUCT_AMBIGUITY_MARKERS or non_empty(item.get("ambiguity_refs")):
            product_ambiguity_gaps.append(item_id)
        if blockers & LOCATOR_MARKERS:
            invalid_locators.append(item_id)
        if blockers & OWNERSHIP_MARKERS:
            ownership_leaks.append(item_id)

        locator = item.get("locator")
        if not locator_is_valid(locator):
            invalid_locators.append(item_id)
        if has_downstream_ownership_leak(item):
            ownership_leaks.append(item_id)

    details["visual_spec_package"]["item_errors"] = item_errors
    details["visual_spec_package"]["provider_evidence_gaps"] = sorted(set(provider_evidence_gaps))
    details["visual_spec_package"]["product_ambiguity_gaps"] = sorted(set(product_ambiguity_gaps))
    details["visual_spec_package"]["invalid_locators"] = sorted(set(invalid_locators))
    details["visual_spec_package"]["ownership_leaks"] = sorted(set(ownership_leaks))
    details["visual_spec_package"]["blocker_lint_items"] = sorted(set(blocker_lint_items))

    if item_errors or blocker_lint_items or not has_ready_item:
        blocker_codes.append(BLOCKERS["INTAKE_INCOMPLETE"])
    if provider_evidence_gaps:
        blocker_codes.append(BLOCKERS["PROVIDER_EVIDENCE_MISSING"])
    if product_ambiguity_gaps:
        blocker_codes.append(BLOCKERS["PRODUCT_AMBIGUITY_UNRESOLVED"])
    if invalid_locators:
        blocker_codes.append(BLOCKERS["LOCATOR_STRATEGY_INVALID"])
    if ownership_leaks:
        blocker_codes.append(BLOCKERS["DOWNSTREAM_OWNERSHIP_LEAK"])

    return package_doc


def validate_visual_spec_assertions(
    package_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> dict[str, Any]:
    assertions_path = package_dir / "visual-spec-assertions.yaml"
    if not assertions_path.exists():
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])
        details["visual_spec_assertions"] = {"missing": True}
        return {}

    validate_json_schema(
        instance_path=assertions_path,
        schema_name="visual-spec-assertions.schema.json",
        details_key="visual_spec_assertions",
        details=details,
        blocker_codes=blocker_codes,
        schema_error_code=BLOCKERS["SCHEMA_INVALID"],
    )

    assertions_doc = load_yaml(assertions_path)
    assertions = assertions_doc.get("assertions")
    if not isinstance(assertions, list):
        assertions = []

    declared_count = parse_count(assertions_doc.get("assertion_count"), len(assertions))
    assertion_errors: list[dict[str, Any]] = []
    non_ci_assertions: list[str] = []
    product_ambiguity_gaps: list[str] = []
    provider_evidence_gaps: list[str] = []
    blocker_lint_assertions: list[str] = []
    ready_ci_count = 0

    details["visual_spec_assertions"] = {
        "assertions_complete": assertions_doc.get("assertions_complete"),
        "ci_assertions_complete": assertions_doc.get("ci_assertions_complete"),
        "assertion_count": declared_count,
        "actual_assertion_count": len(assertions),
        "blocker_lint_errors": assertions_doc.get("blocker_lint_errors"),
    }

    if not is_truthy(assertions_doc.get("assertions_complete")) or declared_count <= 0:
        blocker_codes.append(BLOCKERS["ASSERTION_COVERAGE_INCOMPLETE"])
    if not is_truthy(assertions_doc.get("ci_assertions_complete")):
        blocker_codes.append(BLOCKERS["ASSERTION_COVERAGE_INCOMPLETE"])
    if declared_count != len(assertions):
        blocker_codes.append(BLOCKERS["ASSERTION_COVERAGE_INCOMPLETE"])
    if non_empty(assertions_doc.get("blocker_lint_errors")):
        blocker_codes.append(BLOCKERS["ASSERTION_COVERAGE_INCOMPLETE"])

    for index, assertion in enumerate(assertions):
        if not isinstance(assertion, dict):
            assertion_errors.append({"index": index, "error": "assertion must be a mapping"})
            continue

        assertion_id = str(assertion.get("id") or f"assertion-{index}")
        required_non_empty = [
            "id",
            "visual_spec_refs",
            "assertion_type",
            "acceptance_intent",
            "expected",
            "evidence_refs",
            "ci_suitability",
            "status",
        ]
        missing = [
            field
            for field in required_non_empty
            if not non_empty(assertion.get(field))
        ]
        if "blockers" not in assertion:
            missing.append("blockers")
        if missing:
            assertion_errors.append({"id": assertion_id, "missing_fields": missing})

        status = str(assertion.get("status") or "")
        ci_suitability = str(assertion.get("ci_suitability") or "")
        if status == "ready" and ci_suitability == "ci_low_cost":
            ready_ci_count += 1
        elif status == "ready":
            non_ci_assertions.append(assertion_id)

        if not valid_source_refs(assertion.get("evidence_refs")):
            provider_evidence_gaps.append(assertion_id)

        blockers = as_string_set(assertion.get("blockers"))
        if blockers:
            blocker_lint_assertions.append(assertion_id)
        if blockers & PRODUCT_AMBIGUITY_MARKERS:
            product_ambiguity_gaps.append(assertion_id)
        if blockers & PROVIDER_EVIDENCE_MARKERS:
            provider_evidence_gaps.append(assertion_id)
        if blockers & LOCATOR_MARKERS:
            blocker_codes.append(BLOCKERS["LOCATOR_STRATEGY_INVALID"])
        if blockers & OWNERSHIP_MARKERS:
            blocker_codes.append(BLOCKERS["DOWNSTREAM_OWNERSHIP_LEAK"])
        if has_downstream_ownership_leak(assertion):
            blocker_codes.append(BLOCKERS["DOWNSTREAM_OWNERSHIP_LEAK"])

    details["visual_spec_assertions"]["assertion_errors"] = assertion_errors
    details["visual_spec_assertions"]["ready_ci_assertion_count"] = ready_ci_count
    details["visual_spec_assertions"]["non_ci_ready_assertions"] = non_ci_assertions
    details["visual_spec_assertions"]["provider_evidence_gaps"] = sorted(set(provider_evidence_gaps))
    details["visual_spec_assertions"]["product_ambiguity_gaps"] = sorted(set(product_ambiguity_gaps))
    details["visual_spec_assertions"]["blocker_lint_assertions"] = sorted(set(blocker_lint_assertions))

    if assertion_errors or blocker_lint_assertions or non_ci_assertions or ready_ci_count == 0:
        blocker_codes.append(BLOCKERS["ASSERTION_COVERAGE_INCOMPLETE"])
    if provider_evidence_gaps:
        blocker_codes.append(BLOCKERS["PROVIDER_EVIDENCE_MISSING"])
    if product_ambiguity_gaps:
        blocker_codes.append(BLOCKERS["PRODUCT_AMBIGUITY_UNRESOLVED"])

    return assertions_doc


def validate_cross_references(
    package_doc: dict[str, Any],
    assertions_doc: dict[str, Any],
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    items = package_doc.get("items")
    assertions = assertions_doc.get("assertions")
    if not isinstance(items, list) or not isinstance(assertions, list):
        return

    visual_spec_ids = {item.get("id") for item in items if isinstance(item, dict)}
    missing_refs: list[str] = []
    for assertion in assertions:
        if not isinstance(assertion, dict):
            continue
        for visual_spec_ref in assertion.get("visual_spec_refs") or []:
            if visual_spec_ref not in visual_spec_ids:
                missing_refs.append(str(visual_spec_ref))

    details["visual_spec_cross_refs"] = {
        "visual_spec_item_ids": sorted(str(item_id) for item_id in visual_spec_ids if item_id),
        "missing_visual_spec_refs": sorted(set(missing_refs)),
    }
    if missing_refs:
        blocker_codes.append(BLOCKERS["ASSERTION_COVERAGE_INCOMPLETE"])


def validate_visual_spec_evidence_packet(
    package_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
    warnings: list[str],
) -> None:
    evidence_path = package_dir / "visual-spec-evidence-packet.md"
    if not evidence_path.exists():
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])
        return

    details["visual_spec_evidence_packet"] = evidence_path.name
    packet_status = parse_evidence_packet_status(
        evidence_path.read_text(encoding="utf-8", errors="replace")
    )
    details["visual_spec_evidence_packet_metadata"] = packet_status["metadata"]
    if packet_status["warnings"]:
        warnings.extend(packet_status["warnings"])
    if packet_status["errors"]:
        blocker_codes.append(BLOCKERS["READY_WITHOUT_EVIDENCE"])
        return

    packet_blockers = packet_status["metadata"].get("blockers")
    has_packet_blockers = isinstance(packet_blockers, list) and bool(packet_blockers)
    if packet_status["ready_gate"] != "PASS" or has_packet_blockers:
        blocker_codes.append(BLOCKERS["READY_WITHOUT_EVIDENCE"])
        return

    current_blockers = [code for code in blocker_codes if code != BLOCKERS["READY_WITHOUT_EVIDENCE"]]
    if current_blockers:
        blocker_codes.append(BLOCKERS["READY_WITHOUT_EVIDENCE"])


def parse_count(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def valid_source_refs(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(str(ref).strip() for ref in value)


def as_string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {str(item).strip() for item in value if str(item).strip()}


def locator_is_valid(locator: Any) -> bool:
    if not isinstance(locator, dict):
        return False
    if locator.get("implementation_owned") is not False:
        return False
    strategy = str(locator.get("strategy") or "")
    if strategy in {"css", "xpath", "query-selector", "implementation-selector"}:
        return False
    value = str(locator.get("value") or "")
    if not value:
        return False
    return not any(pattern.search(value) for pattern in FORBIDDEN_LOCATOR_PATTERNS)


def has_downstream_ownership_leak(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in FORBIDDEN_FIELD_NAMES:
                return True
            if normalized == "id" and isinstance(nested, str) and looks_like_downstream_id(nested):
                return True
            if has_downstream_ownership_leak(nested):
                return True
    elif isinstance(value, list):
        return any(has_downstream_ownership_leak(item) for item in value)
    elif isinstance(value, str):
        return bool(re.search(r"\b(implementation task|code component|css selector|xpath)\b", value, re.IGNORECASE))
    return False


def looks_like_downstream_id(value: str) -> bool:
    return bool(re.match(r"^(REQ|FR|NFR|TASK|US|AC)-\d+", value.strip(), re.IGNORECASE))


if __name__ == "__main__":
    sys.exit(main())
