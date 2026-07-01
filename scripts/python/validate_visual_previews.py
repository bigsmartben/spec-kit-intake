#!/usr/bin/env python3
"""Validate Spec Kit Figma-derived component matrix preview bundles."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised in user environments
    yaml = None

from intake_validator_common import validate_json_schema


BLOCKERS = {
    "SOURCE_INTAKE_BLOCKED": "VISUAL_PREVIEW_SOURCE_INTAKE_BLOCKED",
    "REQUIRED_ARTIFACT_MISSING": "VISUAL_PREVIEW_REQUIRED_ARTIFACT_MISSING",
    "FIGMA_NODE_COVERAGE_INCOMPLETE": "VISUAL_PREVIEW_FIGMA_NODE_COVERAGE_INCOMPLETE",
    "COMPONENT_STATE_COVERAGE_INCOMPLETE": "VISUAL_PREVIEW_COMPONENT_STATE_COVERAGE_INCOMPLETE",
    "PAGE_COVERAGE_INCOMPLETE": "VISUAL_PREVIEW_PAGE_COVERAGE_INCOMPLETE",
    "ASSET_TRACEABILITY_INCOMPLETE": "VISUAL_PREVIEW_ASSET_TRACEABILITY_INCOMPLETE",
    "VIEWPORT_CAPTURE_INCOMPLETE": "VISUAL_PREVIEW_VIEWPORT_CAPTURE_INCOMPLETE",
    "VISUAL_DIFF_BLOCKED": "VISUAL_PREVIEW_VISUAL_DIFF_BLOCKED",
    "KNOWN_GAP_UNRESOLVED": "VISUAL_PREVIEW_KNOWN_GAP_UNRESOLVED",
    "SCHEMA_INVALID": "VISUAL_PREVIEW_SCHEMA_INVALID",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preview_dir", help="Directory containing visual-design preview artifacts")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    html_dir = Path(args.preview_dir)
    blocker_codes: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {"preview_dir": str(html_dir)}

    if not html_dir.exists() or not html_dir.is_dir():
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])
        return emit(args.json, details, sorted(set(blocker_codes)), warnings)

    validate_source_intake(html_dir, details, blocker_codes)

    required_files = {
        "component_matrix_preview": html_dir / "component-matrix-preview.html",
        "component_coverage": html_dir / "component-coverage.yaml",
        "viewport_coverage": html_dir / "viewport-coverage.yaml",
        "known_gaps": html_dir / "known-gaps.md",
    }
    missing = [name for name, path in required_files.items() if not path.exists()]
    screenshots_dir = html_dir / "screenshots"
    if not screenshots_dir.exists() or not screenshots_dir.is_dir():
        missing.append("screenshots")
    if missing:
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])
    details["required_artifacts"] = {"missing": missing}

    component_coverage = load_yaml_artifact(
        required_files["component_coverage"],
        "component-coverage.schema.json",
        "component_coverage",
        details,
        blocker_codes,
    )
    viewport_coverage = load_yaml_artifact(
        required_files["viewport_coverage"],
        "viewport-coverage.schema.json",
        "viewport_coverage",
        details,
        blocker_codes,
    )

    html_text = ""
    if required_files["component_matrix_preview"].exists():
        html_text = required_files["component_matrix_preview"].read_text(encoding="utf-8", errors="replace")

    validate_component_coverage(component_coverage, html_text, details, blocker_codes)
    validate_viewport_coverage(html_dir, viewport_coverage, details, blocker_codes)
    validate_known_gaps(required_files["known_gaps"], details, blocker_codes)

    return emit(args.json, details, sorted(set(blocker_codes)), warnings)


def validate_source_intake(
    html_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    upstream = html_dir.parent
    packet = upstream / "visual-evidence-packet.md"
    if not packet.exists():
        details["source_intake"] = {"missing": True}
        blocker_codes.append(BLOCKERS["SOURCE_INTAKE_BLOCKED"])
        return

    text = packet.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
    match = re.match(r"\A---\s*\r?\n(.*?)\r?\n---", text, re.DOTALL)
    metadata: dict[str, Any] = {}
    if match and yaml is not None:
        loaded = yaml.safe_load(match.group(1)) or {}
        metadata = loaded if isinstance(loaded, dict) else {}
    ready_gate = str(metadata.get("ready_gate") or "").strip().upper()
    blockers = metadata.get("blockers")
    details["source_intake"] = {
        "path": str(packet),
        "ready_gate": ready_gate,
        "blockers": blockers,
    }
    if ready_gate != "PASS" or (isinstance(blockers, list) and blockers):
        blocker_codes.append(BLOCKERS["SOURCE_INTAKE_BLOCKED"])


def load_yaml_artifact(
    path: Path,
    schema_name: str,
    details_key: str,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> dict[str, Any]:
    if not path.exists():
        return {}
    validate_json_schema(
        instance_path=path,
        schema_name=schema_name,
        details_key=details_key,
        details=details,
        blocker_codes=blocker_codes,
        schema_error_code=BLOCKERS["SCHEMA_INVALID"],
    )
    if yaml is None:
        blocker_codes.append(BLOCKERS["SCHEMA_INVALID"])
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        blocker_codes.append(BLOCKERS["SCHEMA_INVALID"])
        return {}
    return data if isinstance(data, dict) else {}


def preview_ref_in_html(preview_ref: str, html_text: str) -> bool:
    fragment = preview_ref.rsplit("#", 1)[-1] if "#" in preview_ref else preview_ref
    fragment = fragment.strip()
    if not fragment:
        return False
    if fragment.startswith("[") and fragment.endswith("]"):
        return fragment in html_text or fragment[1:-1] in html_text
    return (
        f'id="{fragment}"' in html_text
        or f"id='{fragment}'" in html_text
        or f'data-preview-id="{fragment}"' in html_text
        or f"data-preview-id='{fragment}'" in html_text
    )


def validate_component_coverage(
    component_coverage: dict[str, Any],
    html_text: str,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    components = component_coverage.get("components", [])
    missing_preview_refs: list[str] = []
    missing_visual_spec_refs: list[str] = []
    missing_records: list[str] = []
    asset_or_resource_gaps: list[str] = []
    covered_count = 0
    missing_count = 0

    for component in components if isinstance(components, list) else []:
        if not isinstance(component, dict):
            continue
        component_id = str(component.get("id") or "<unknown>")
        covered = component.get("covered", [])
        missing = component.get("missing", [])
        if isinstance(covered, list):
            covered_count += len(covered)
            for record in covered:
                if not isinstance(record, dict):
                    continue
                preview_ref = str(record.get("preview_ref") or "")
                visual_spec_ref = str(record.get("visual_spec_ref") or "")
                if not visual_spec_ref:
                    missing_visual_spec_refs.append(component_id)
                if not preview_ref or not preview_ref_in_html(preview_ref, html_text):
                    missing_preview_refs.append(preview_ref or component_id)
        if isinstance(missing, list):
            missing_count += len(missing)
            for record in missing:
                if not isinstance(record, dict):
                    continue
                missing_records.append(component_id)
                missing_type = str(record.get("missing_type") or "")
                if missing_type in {"asset", "resource", "token"}:
                    asset_or_resource_gaps.append(component_id)

    blockers = component_coverage.get("blockers")
    details["component_coverage"] = {
        "component_count": len(components) if isinstance(components, list) else 0,
        "covered_count": covered_count,
        "missing_count": missing_count,
        "missing_preview_refs": missing_preview_refs,
        "missing_visual_spec_refs": missing_visual_spec_refs,
        "missing_records": missing_records,
        "asset_or_resource_gaps": asset_or_resource_gaps,
        "ready_gate": component_coverage.get("ready_gate"),
        "blockers": blockers,
    }
    if not components or missing_preview_refs:
        blocker_codes.append(BLOCKERS["FIGMA_NODE_COVERAGE_INCOMPLETE"])
    if missing_records or missing_visual_spec_refs:
        blocker_codes.append(BLOCKERS["COMPONENT_STATE_COVERAGE_INCOMPLETE"])
    if asset_or_resource_gaps:
        blocker_codes.append(BLOCKERS["ASSET_TRACEABILITY_INCOMPLETE"])
    if component_coverage.get("ready_gate") != "PASS" or (isinstance(blockers, list) and blockers):
        blocker_codes.append(BLOCKERS["KNOWN_GAP_UNRESOLVED"])


def validate_viewport_coverage(
    html_dir: Path,
    viewport_coverage: dict[str, Any],
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    viewports = viewport_coverage.get("viewports", [])
    missing_screenshots: list[str] = []
    uncovered_viewports: list[str] = []
    visual_diff_blocked: list[str] = []
    page_refs = 0

    for viewport in viewports if isinstance(viewports, list) else []:
        if not isinstance(viewport, dict):
            continue
        viewport_id = str(viewport.get("id") or "<unknown>")
        if viewport.get("covered") is not True:
            uncovered_viewports.append(viewport_id)
        refs = viewport.get("screenshot_refs", [])
        if not refs:
            missing_screenshots.append(viewport_id)
        for ref in refs if isinstance(refs, list) else []:
            ref_path = str(ref)
            if ref_path and not (html_dir / ref_path).exists():
                missing_screenshots.append(ref_path)
        page_refs += len(viewport.get("page_refs", []) or [])
        if viewport.get("visual_diff_status") == "blocked":
            visual_diff_blocked.append(viewport_id)

    blockers = viewport_coverage.get("blockers")
    details["viewport_coverage"] = {
        "viewport_count": len(viewports) if isinstance(viewports, list) else 0,
        "missing_screenshots": missing_screenshots,
        "uncovered_viewports": uncovered_viewports,
        "visual_diff_blocked": visual_diff_blocked,
        "page_ref_count": page_refs,
        "ready_gate": viewport_coverage.get("ready_gate"),
        "blockers": blockers,
    }
    if not viewports or uncovered_viewports or missing_screenshots:
        blocker_codes.append(BLOCKERS["VIEWPORT_CAPTURE_INCOMPLETE"])
    if page_refs == 0:
        blocker_codes.append(BLOCKERS["PAGE_COVERAGE_INCOMPLETE"])
    if visual_diff_blocked:
        blocker_codes.append(BLOCKERS["VISUAL_DIFF_BLOCKED"])
    if viewport_coverage.get("ready_gate") != "PASS" or (isinstance(blockers, list) and blockers):
        blocker_codes.append(BLOCKERS["KNOWN_GAP_UNRESOLVED"])


def validate_known_gaps(
    known_gaps_path: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    if not known_gaps_path.exists():
        return
    text = known_gaps_path.read_text(encoding="utf-8", errors="replace")
    unresolved = bool(re.search(r"\b(UNRESOLVED|BLOCKED|TODO)\b", text, re.IGNORECASE))
    details["known_gaps"] = {"unresolved": unresolved}
    if unresolved:
        blocker_codes.append(BLOCKERS["KNOWN_GAP_UNRESOLVED"])


def emit(json_mode: bool, details: dict[str, Any], blockers: list[str], warnings: list[str]) -> int:
    result = {
        "status": "BLOCKED" if blockers else "PASS",
        "blockers": blockers,
        "warnings": warnings,
        "details": details,
    }
    if json_mode:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Visual preview readiness: {result['status']}")
        if blockers:
            print("Blockers:")
            for blocker in blockers:
                print(f"- {blocker}")
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"- {warning}")
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
