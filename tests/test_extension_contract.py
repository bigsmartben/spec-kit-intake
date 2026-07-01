import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "python" / "validate_visual_design_intake.py"
PRD_VALIDATOR = ROOT / "scripts" / "python" / "validate_prd_intake.py"
TEST_CASE_VALIDATOR = ROOT / "scripts" / "python" / "validate_test_cases_intake.py"
HTML_SSOT_VALIDATOR = ROOT / "scripts" / "python" / "validate_html_ssot.py"
STRUCTURED_IR_VALIDATOR = ROOT / "scripts" / "python" / "validate_structured_ir_intake.py"


def write_visual_intake_fixture(intake: Path, source_type: str, fidelity: str, file_name: str):
    intake.mkdir(parents=True, exist_ok=True)
    source_dir = intake / "source-files"
    source_dir.mkdir()
    source = source_dir / file_name
    source.write_bytes(f"{source_type}:{fidelity}:source".encode("utf-8"))

    import hashlib

    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    rel_source = f"source-files/{file_name}"
    if source_type == "image":
        source_details = [
            "source_details:",
            "  image_dimensions:",
            "    width_px: 100",
            "    height_px: 100",
            "  region_coverage: full",
            "  ocr_status: not_applicable",
        ]
    elif source_type == "pdf":
        source_details = [
            "source_details:",
            "  page_count: 1",
            "  processed_page_count: 1",
            "  rendered_page_refs:",
            f"    - {rel_source}#page=1",
            "  text_extraction_status: complete",
        ]
    elif source_type == "markdown":
        source_details = [
            "source_details:",
            "  heading_structure:",
            "    - Design brief",
            "  embedded_or_linked_asset_refs: []",
            "  design_note_parsing_status: complete",
        ]
    elif source_type == "figma":
        source_details = [
            "source_details:",
            "  file_url: https://www.figma.com/file/example",
            "  file_key: example",
            "  selected_node_ids:",
            "    - '1'",
        ]
    else:
        source_details = []

    (intake / "design-source-manifest.yaml").write_text(
        "\n".join(
            [
                f"source_type: {source_type}",
                f"required_fidelity: {fidelity}",
                "source_integrity_complete: true",
                "captured_at: '2026-06-23T00:00:00Z'",
                "capture_method: local_fixture",
                "page_or_frame_count: 1",
                "processed_count: 1",
                "extraction_scope: full",
                "source_files:",
                f"  - path: {rel_source}",
                "    mime_type: application/octet-stream",
                f"    byte_size: {source.stat().st_size}",
                f"    sha256: {digest}",
                "    role: original",
                *source_details,
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "visual-requirements.yaml").write_text(
        "\n".join(
            [
                "visual_requirements_complete: true",
                "visual_requirements_count: 1",
                "source_refs_complete: true",
                "fidelity_rules_applied: true",
                "visual_parity_plan_complete: true",
                "blocker_lint_errors: []",
                "parity_plan:",
                "  comparison_targets:",
                "    - primary_surface",
                f"  original_refs: ['{rel_source}#full']",
                "  comparison_method: manual_review",
                "  thresholds:",
                "    manual_review_checklist:",
                "      - compare primary hierarchy",
                "  accepted_exceptions: []",
                "  blocking_difference_categories:",
                "    - missing_required_visual_fact",
                "requirements:",
                "  - id: VR-001",
                "    category: layout",
                "    requirement: Preserve primary content hierarchy",
                f"    source_refs: ['{rel_source}#full']",
                "    evidence_type: observed",
                "    confidence: high",
                "    confidence_rationale: Source artifact directly shows the primary hierarchy.",
                "    engineering_action: Implement matching hierarchy",
                "    acceptance_check: Compare implementation screenshot with source",
                f"    fidelity_level: {fidelity}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "visual-evidence-packet.md").write_text(
        "---\n"
        "ready_gate: PASS\n"
        "blockers: []\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 1\n"
        "generated_at: '2026-06-23T00:00:00Z'\n"
        "---\n"
        "# Visual Design Evidence Packet\n",
        encoding="utf-8",
    )


def write_prd_intake_fixture(intake: Path):
    intake.mkdir(parents=True, exist_ok=True)
    source_dir = intake / "source-files"
    source_dir.mkdir()
    source = source_dir / "feature-prd.md"
    source.write_text("# Feature PRD\n\nUsers can save draft content.\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(source.read_bytes()).hexdigest()

    (intake / "source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: markdown",
                "source_integrity_complete: true",
                "captured_at: '2026-06-23T00:00:00Z'",
                "capture_method: local_fixture",
                "document_version: fixture-v1",
                "extraction_scope: full",
                "source_files:",
                "  - path: source-files/feature-prd.md",
                "    mime_type: text/markdown",
                f"    byte_size: {source.stat().st_size}",
                f"    sha256: {digest}",
                "    role: original",
                "source_details:",
                "  heading_coverage: full",
                "  parsed_section_coverage: full",
                "  linked_asset_refs: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "prd-intake.yaml").write_text(
        "\n".join(
            [
                "prd_intake_complete: true",
                "source_refs_complete: true",
                "extracted_fact_count: 1",
                "acceptance_evidence_complete: true",
                "unresolved_ambiguity_marked: true",
                "acceptance_gaps: []",
                "open_questions:",
                "  - '[NEEDS CLARIFICATION] Pricing rules are outside this fixture.'",
                "blocker_lint_errors: []",
                "facts:",
                "  - id: PI-001",
                "    category: acceptance",
                "    statement: Users can save draft content.",
                "    source_refs: ['source-files/feature-prd.md#L3']",
                "    evidence_type: observed",
                "    confidence: high",
                "    confidence_rationale: Source statement directly describes the accepted behavior.",
                "    downstream_hint: candidate_acceptance_input",
                "    acceptance_or_validation_signal: Draft save behavior is explicitly stated.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "evidence-packet.md").write_text(
        "---\n"
        "ready_gate: PASS\n"
        "blockers: []\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 1\n"
        "generated_at: '2026-06-23T00:00:00Z'\n"
        "---\n"
        "# PRD Evidence Packet\n",
        encoding="utf-8",
    )


def write_test_case_intake_fixture(intake: Path):
    intake.mkdir(parents=True, exist_ok=True)
    source_dir = intake / "source-files"
    source_dir.mkdir()
    source = source_dir / "test_feature.py"
    source.write_text("def test_save_draft():\n    assert True\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(source.read_bytes()).hexdigest()

    (intake / "source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: code",
                "source_integrity_complete: true",
                "captured_at: '2026-06-23T00:00:00Z'",
                "capture_method: local_fixture",
                "framework_or_format: pytest",
                "execution_scope: unit",
                "source_files:",
                "  - path: source-files/test_feature.py",
                "    mime_type: text/x-python",
                f"    byte_size: {source.stat().st_size}",
                f"    sha256: {digest}",
                "    role: original",
                "source_details:",
                "  test_names:",
                "    - test_save_draft",
                "  execution_status: passed",
                "  skipped_markers: []",
                "  fixture_refs:",
                "    - local pytest fixture",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "test-case-intake.yaml").write_text(
        "\n".join(
            [
                "test_case_intake_complete: true",
                "source_refs_complete: true",
                "scenario_count: 1",
                "assertions_complete: true",
                "fixture_evidence_complete: true",
                "coverage_gaps_recorded: true",
                "assertion_gaps: []",
                "fixture_or_test_data_gaps: []",
                "coverage_gaps:",
                "  - Error-state coverage is not present in the fixture.",
                "flaky_or_skipped_cases: []",
                "blocker_lint_errors: []",
                "scenarios:",
                "  - id: TC-001",
                "    category: unit",
                "    scenario: Saving draft content succeeds.",
                "    source_refs: ['source-files/test_feature.py#L1']",
                "    evidence_type: observed",
                "    confidence: high",
                "    confidence_rationale: Test source directly exercises the scenario.",
                "    actors: ['registered_user']",
                "    preconditions: ['draft content exists']",
                "    actions: ['save draft']",
                "    expected_outcomes: ['draft is persisted']",
                "    assertions: ['save path returns success']",
                "    fixtures_or_test_data: ['local pytest fixture']",
                "    coverage_signal: happy_path_present_error_path_missing",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "evidence-packet.md").write_text(
        "---\n"
        "ready_gate: PASS\n"
        "blockers: []\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 1\n"
        "generated_at: '2026-06-23T00:00:00Z'\n"
        "---\n"
        "# Test Case Evidence Packet\n",
        encoding="utf-8",
    )


def write_image_visual_intake_fixture(intake: Path):
    write_visual_intake_fixture(intake, "image", "low", "wireframe.png")


def write_html_ssot_fixture(html_dir: Path):
    visual_intake = html_dir.parent
    write_visual_intake_fixture(visual_intake, "figma", "high", "figma-source.txt")
    html_dir.mkdir(parents=True, exist_ok=True)
    screenshots = html_dir / "screenshots"
    screenshots.mkdir(exist_ok=True)
    (screenshots / "home-desktop.png").write_bytes(b"fake-png")
    asset = html_dir / "logo.svg"
    asset.write_text("<svg></svg>", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(asset.read_bytes()).hexdigest()
    (html_dir / "visual-spec.html").write_text(
        '<main data-figma-node-id="1" data-spec-role="home-page">'
        '<button data-figma-node-id="2" data-acceptance-unit="component-state">Save</button>'
        "</main>",
        encoding="utf-8",
    )
    (html_dir / "figma-map.json").write_text(
        json.dumps(
            {
                "source_intake_refs": ["../visual-requirements.yaml#VR-001"],
                "mappings": [
                    {
                        "figma_node_id": "1",
                        "selector": '[data-figma-node-id="1"]',
                        "acceptance_unit": "page",
                        "required": True,
                        "states": ["default"],
                        "viewports": ["desktop"],
                        "content_sample": "Home",
                        "container_constraint": "page",
                    },
                    {
                        "figma_node_id": "2",
                        "selector": '[data-figma-node-id="2"]',
                        "acceptance_unit": "component-state",
                        "required": True,
                        "states": ["default"],
                        "viewports": ["desktop"],
                        "content_sample": "Save",
                        "container_constraint": "header",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (html_dir / "assets-manifest.json").write_text(
        json.dumps(
            {
                "assets": [
                    {
                        "id": "asset-logo",
                        "path": "logo.svg",
                        "role": "brand",
                        "source_refs": ["figma://node/logo"],
                        "sha256": digest,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (html_dir / "coverage-report.md").write_text(
        "---\n"
        "ready_gate: PASS\n"
        "blockers: []\n"
        "required_nodes_total: 2\n"
        "required_nodes_covered: 2\n"
        "component_state_coverage_complete: true\n"
        "page_coverage_complete: true\n"
        "asset_traceability_complete: true\n"
        "viewport_capture_complete: true\n"
        "visual_diff_status: pass\n"
        "accepted_exceptions: []\n"
        "---\n"
        "# Coverage Report\n",
        encoding="utf-8",
    )
    (html_dir / "known-gaps.md").write_text("# Known Gaps\n\nNone.\n", encoding="utf-8")


def write_structured_ir_fixture(ir_dir: Path):
    visual_intake = ir_dir.parent
    write_visual_intake_fixture(visual_intake, "figma", "high", "figma-source.txt")
    ir_dir.mkdir(parents=True, exist_ok=True)

    (ir_dir / "structured-ir.yaml").write_text(
        "\n".join(
            [
                "ir_complete: true",
                "ir_item_count: 1",
                "source_refs_complete: true",
                "provider_evidence_complete: true",
                "product_ambiguities_recorded: true",
                "downstream_ownership_free: true",
                "product_ambiguities: []",
                "blocker_lint_errors: []",
                "items:",
                "  - id: IR-home-save-default",
                "    source_refs:",
                "      - figma://node/2",
                "    visual_requirement_refs:",
                "      - ../visual-requirements.yaml#VR-001",
                "    html_ssot_refs:",
                "      - ../figma2htmlssot/visual-spec.html#[data-figma-node-id='2']",
                "    page: home",
                "    region: header",
                "    role: button",
                "    state: default",
                "    viewport: desktop",
                "    locator:",
                "      strategy: role",
                "      value: button[name='Save']",
                "      implementation_owned: false",
                "    expectations:",
                "      dom:",
                "        - button element is present",
                "      aria:",
                "        - accessible name is Save",
                "      design_tokens:",
                "        - token: color.primary",
                "          source_ref: figma://variables/color-primary",
                "      relations:",
                "        - type: appears-before",
                "          target: main content",
                "    acceptance_intent: Save control is semantically discoverable at desktop viewport",
                "    evidence_type: observed",
                "    confidence: high",
                "    status: ready",
                "    blockers: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (ir_dir / "ir-assertions.yaml").write_text(
        "\n".join(
            [
                "assertions_complete: true",
                "assertion_count: 1",
                "ci_assertions_complete: true",
                "blocker_lint_errors: []",
                "assertions:",
                "  - id: IRA-home-save-visible",
                "    ir_refs:",
                "      - IR-home-save-default",
                "    assertion_type: visible",
                "    acceptance_intent: Save control is visible and discoverable",
                "    expected: true",
                "    evidence_refs:",
                "      - structured-ir.yaml#IR-home-save-default",
                "    ci_suitability: ci_low_cost",
                "    status: ready",
                "    blockers: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (ir_dir / "ir-evidence-packet.md").write_text(
        "---\n"
        "ready_gate: PASS\n"
        "blockers: []\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 1\n"
        "generated_at: '2026-07-01T00:00:00Z'\n"
        "---\n"
        "# Structured IR Evidence Packet\n",
        encoding="utf-8",
    )


def test_manifest_loads_with_spec_kit_checkout():
    spec_kit_src = ROOT.parent / "spec-kit" / "src"
    if not spec_kit_src.exists():
        pytest.skip("spec-kit checkout not available next to extension")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(spec_kit_src)

    code = (
        "from pathlib import Path; "
        "from specify_cli.extensions import ExtensionManifest; "
        "m=ExtensionManifest(Path('extension.yml')); "
        "assert m.id == 'intake'; "
        "assert len(m.commands) == 5; "
        "assert {c['name'] for c in m.commands} == {'speckit.intake.visual-design', 'speckit.intake.figma2htmlssot', 'speckit.intake.ir', 'speckit.intake.prd', 'speckit.intake.test-cases'}; "
        "assert m.hooks"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr


def test_config_template_matches_extension_defaults():
    extension = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8-sig"))
    config = yaml.safe_load((ROOT / "config-template.yml").read_text(encoding="utf-8"))

    defaults = extension["defaults"]
    assert defaults["artifacts"] == config["artifacts"]
    assert defaults["readiness"] == config["readiness"]
    assert defaults["capture"] == config["capture"]


def test_manifest_declared_files_exist():
    extension = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8-sig"))

    for command in extension["provides"]["commands"]:
        assert (ROOT / command["file"]).exists(), command["file"]
    for config in extension["provides"].get("config", []):
        assert (ROOT / config["template"]).exists(), config["template"]

    for value in extension["defaults"]["artifacts"].values():
        if not isinstance(value, str):
            continue
        if value.startswith(("commands/", "templates/", "scripts/python/")):
            assert (ROOT / value).exists(), value


def test_release_provenance_contract_is_documented_and_generated():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "extension-artifact.yml").read_text(encoding="utf-8")
    for field in [
        "repository_url",
        "release_version",
        "source_commit_sha",
        "download_url",
        "validation_evidence",
    ]:
        assert field in readme
        assert field in workflow
    assert "release-provenance.json" in workflow


def test_readme_release_url_matches_extension_version():
    extension = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8-sig"))
    version = extension["extension"]["version"]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"archive/refs/tags/v{version}.zip" in readme


def test_html_ssot_schema_and_validator_paths_are_declared():
    extension = ROOT / "extension.yml"
    config = ROOT / "config-template.yml"
    for document in (extension.read_text(encoding="utf-8-sig"), config.read_text(encoding="utf-8")):
        assert "scripts/python/validate_html_ssot.py" in document
        assert "templates/schemas/figma-map.schema.json" in document
        assert "templates/schemas/assets-manifest.schema.json" in document
        assert "templates/schemas/html-ssot-coverage.schema.json" in document

    assert HTML_SSOT_VALIDATOR.exists()
    assert (ROOT / "templates" / "schemas" / "figma-map.schema.json").exists()
    assert (ROOT / "templates" / "schemas" / "assets-manifest.schema.json").exists()
    assert (ROOT / "templates" / "schemas" / "html-ssot-coverage.schema.json").exists()


def test_structured_ir_schema_and_validator_paths_are_declared():
    extension = ROOT / "extension.yml"
    config = ROOT / "config-template.yml"
    assert "commands/speckit.intake.ir.md" in extension.read_text(encoding="utf-8-sig")
    for document in (extension.read_text(encoding="utf-8-sig"), config.read_text(encoding="utf-8")):
        assert "scripts/python/validate_structured_ir_intake.py" in document
        assert "templates/intake-structured-ir-contract.md" in document
        assert "templates/intake-structured-ir-evidence-packet-template.md" in document
        assert "templates/schemas/structured-ir.schema.json" in document
        assert "templates/schemas/ir-assertions.schema.json" in document

    assert STRUCTURED_IR_VALIDATOR.exists()
    assert (ROOT / "commands" / "speckit.intake.ir.md").exists()
    assert (ROOT / "templates" / "intake-structured-ir-contract.md").exists()
    assert (ROOT / "templates" / "intake-structured-ir-evidence-packet-template.md").exists()
    assert (ROOT / "templates" / "schemas" / "structured-ir.schema.json").exists()
    assert (ROOT / "templates" / "schemas" / "ir-assertions.schema.json").exists()


def test_validator_blocks_missing_directory():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "missing-dir"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "VISUAL_SOURCE_MANIFEST_MISSING" in result.stdout
    assert "VISUAL_REQUIREMENTS_MISSING" in result.stdout
    assert "VISUAL_EVIDENCE_PACKET_MISSING" in result.stdout


def test_prd_validator_blocks_missing_directory():
    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "missing-dir"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "PRD_SOURCE_MANIFEST_MISSING" in result.stdout
    assert "PRD_INTAKE_MISSING" in result.stdout
    assert "PRD_EVIDENCE_PACKET_MISSING" in result.stdout


def test_test_case_validator_blocks_missing_directory():
    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), "missing-dir"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "TEST_SOURCE_MANIFEST_MISSING" in result.stdout
    assert "TEST_CASE_INTAKE_MISSING" in result.stdout
    assert "TEST_EVIDENCE_PACKET_MISSING" in result.stdout


def test_structured_ir_validator_blocks_missing_directory():
    result = subprocess.run(
        [sys.executable, str(STRUCTURED_IR_VALIDATOR), "missing-dir"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "IR_SOURCE_INTAKE_BLOCKED" in result.stdout
    assert "IR_REQUIRED_ARTIFACT_MISSING" in result.stdout
    assert "IR_READY_WITHOUT_EVIDENCE" in result.stdout


@pytest.mark.parametrize(
    ("source_type", "fidelity", "file_name"),
    [
        ("image", "low", "wireframe.png"),
        ("pdf", "medium", "design-pack.pdf"),
        ("markdown", "high", "design-brief.md"),
    ],
)
def test_validator_passes_visual_source_matrix(source_type, fidelity, file_name):
    work_dir = ROOT / ".tmp" / f"test-validator-{source_type}-{fidelity}"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, source_type, fidelity, file_name)

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Visual design intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_visual_validator_allows_remote_source_gap_but_blocks_integrity():
    work_dir = ROOT / ".tmp" / "test-validator-remote-source-gap"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")

    (intake / "design-source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: figma",
                "required_fidelity: high",
                "source_integrity_complete: false",
                "captured_at: '2026-07-01T00:00:00Z'",
                "capture_method: figma_url",
                "page_or_frame_count: 1",
                "processed_count: 1",
                "extraction_scope: selected_node",
                "snapshot_status: not_available",
                "integrity_gap_reason: Figma source URL was provided without a local export snapshot.",
                "retrieval_metadata:",
                "  retrieved_at: '2026-07-01T00:00:00Z'",
                "  stable_url: https://www.figma.com/file/example",
                "  visible_title: Fixture design",
                "source_files:",
                "  - path: figma://file/example",
                "    mime_type: application/x-figma",
                "    checksum_status: unavailable",
                "    role: original",
                "source_details:",
                "  file_url: https://www.figma.com/file/example",
                "  file_key: example",
                "  selected_node_ids:",
                "    - '1'",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SOURCE_INTEGRITY_INCOMPLETE" in payload["blockers"]
    assert "VISUAL_SCHEMA_INVALID" not in payload["blockers"]
    assert "VISUAL_SOURCE_FILE_MISSING" not in payload["blockers"]
    assert payload["details"]["source_files"][0]["remote_ref"] is True

    shutil.rmtree(work_dir)


def test_prd_validator_passes_complete_minimal_intake():
    work_dir = ROOT / ".tmp" / "test-prd-validator-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PRD intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_prd_validator_allows_remote_source_gap_but_blocks_integrity():
    work_dir = ROOT / ".tmp" / "test-prd-validator-remote-source-gap"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    (intake / "source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: url",
                "source_integrity_complete: false",
                "captured_at: '2026-07-01T00:00:00Z'",
                "capture_method: remote_url",
                "document_version: remote-v1",
                "extraction_scope: full",
                "snapshot_status: not_available",
                "integrity_gap_reason: Source URL was accessible but no local snapshot was provided.",
                "retrieval_metadata:",
                "  retrieved_at: '2026-07-01T00:00:00Z'",
                "  stable_url: https://example.com/prd",
                "  visible_title: Remote PRD",
                "  author_or_owner: product",
                "source_files:",
                "  - path: https://example.com/prd",
                "    mime_type: text/html",
                "    checksum_status: unavailable",
                "    role: original",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "PRD_SOURCE_INTEGRITY_INCOMPLETE" in payload["blockers"]
    assert "PRD_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert "PRD_SCHEMA_INVALID" not in payload["blockers"]
    assert "PRD_SOURCE_FILE_MISSING" not in payload["blockers"]
    assert payload["details"]["source_files"][0]["remote_ref"] is True

    shutil.rmtree(work_dir)


def test_prd_validator_blocks_untraceable_facts():
    work_dir = ROOT / ".tmp" / "test-prd-validator-untraceable"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    text = (intake / "prd-intake.yaml").read_text(encoding="utf-8")
    text = text.replace("source_refs_complete: true", "source_refs_complete: false")
    text = text.replace("source_refs: ['source-files/feature-prd.md#L3']", "source_refs: []")
    (intake / "prd-intake.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "PRD_FACTS_UNTRACEABLE" in payload["blockers"]
    assert "PRD_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert "PRD_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["prd_intake"]["valid"] is False

    shutil.rmtree(work_dir)


def test_prd_validator_blocks_invalid_confidence_enum():
    work_dir = ROOT / ".tmp" / "test-prd-validator-confidence"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    text = (intake / "prd-intake.yaml").read_text(encoding="utf-8")
    text = text.replace("    confidence: high", "    confidence: certain")
    (intake / "prd-intake.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "PRD_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["prd_intake"]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    (
        "kind",
        "writer",
        "validator",
        "artifact",
        "source_refs_line",
        "schema_blocker",
        "detail_key",
    ),
    [
        (
            "prd",
            write_prd_intake_fixture,
            PRD_VALIDATOR,
            "prd-intake.yaml",
            "    source_refs: ['source-files/feature-prd.md#L3']",
            "PRD_SCHEMA_INVALID",
            "prd_intake",
        ),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "test-case-intake.yaml",
            "    source_refs: ['source-files/test_feature.py#L1']",
            "TEST_SCHEMA_INVALID",
            "test_case_intake",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-requirements.yaml",
            "    source_refs: ['source-files/wireframe.png#full']",
            "VISUAL_SCHEMA_INVALID",
            "visual_requirements",
        ),
    ],
)
def test_validators_require_string_source_refs(
    kind,
    writer,
    validator,
    artifact,
    source_refs_line,
    schema_blocker,
    detail_key,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-numeric-source-ref"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    path = intake / artifact
    text = path.read_text(encoding="utf-8")
    text = text.replace(source_refs_line, "    source_refs: [123]")
    path.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert schema_blocker in payload["blockers"]
    assert payload["details"]["schema_validation"][detail_key]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    (
        "kind",
        "writer",
        "validator",
        "artifact",
        "anchor_line",
        "schema_blocker",
        "detail_key",
    ),
    [
        (
            "prd",
            write_prd_intake_fixture,
            PRD_VALIDATOR,
            "prd-intake.yaml",
            "    acceptance_or_validation_signal: Draft save behavior is explicitly stated.",
            "PRD_SCHEMA_INVALID",
            "prd_intake",
        ),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "test-case-intake.yaml",
            "    coverage_signal: happy_path_present_error_path_missing",
            "TEST_SCHEMA_INVALID",
            "test_case_intake",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-requirements.yaml",
            "    fidelity_level: low",
            "VISUAL_SCHEMA_INVALID",
            "visual_requirements",
        ),
    ],
)
def test_validators_reject_unknown_blocker_codes(
    kind,
    writer,
    validator,
    artifact,
    anchor_line,
    schema_blocker,
    detail_key,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-unknown-blocker"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    path = intake / artifact
    text = path.read_text(encoding="utf-8")
    text = text.replace(anchor_line, f"{anchor_line}\n    blockers: [NOT_A_BLOCKER]")
    path.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert schema_blocker in payload["blockers"]
    assert payload["details"]["schema_validation"][detail_key]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    (
        "kind",
        "writer",
        "validator",
        "artifact",
        "rationale_line",
        "schema_blocker",
    ),
    [
        (
            "prd",
            write_prd_intake_fixture,
            PRD_VALIDATOR,
            "prd-intake.yaml",
            "    confidence_rationale: Source statement directly describes the accepted behavior.\n",
            "PRD_SCHEMA_INVALID",
        ),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "test-case-intake.yaml",
            "    confidence_rationale: Test source directly exercises the scenario.\n",
            "TEST_SCHEMA_INVALID",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-requirements.yaml",
            "    confidence_rationale: Source artifact directly shows the primary hierarchy.\n",
            "VISUAL_SCHEMA_INVALID",
        ),
    ],
)
def test_validators_require_confidence_rationale(
    kind,
    writer,
    validator,
    artifact,
    rationale_line,
    schema_blocker,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-missing-confidence-rationale"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    path = intake / artifact
    text = path.read_text(encoding="utf-8")
    text = text.replace(rationale_line, "")
    path.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert schema_blocker in payload["blockers"]

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    (
        "kind",
        "writer",
        "validator",
        "artifact",
        "count_line",
        "blocker",
        "detail_key",
        "match_key",
    ),
    [
        (
            "prd",
            write_prd_intake_fixture,
            PRD_VALIDATOR,
            "prd-intake.yaml",
            "extracted_fact_count: 1",
            "PRD_INTAKE_MISSING",
            "prd_intake",
            "count_matches_facts",
        ),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "test-case-intake.yaml",
            "scenario_count: 1",
            "TEST_CASE_INTAKE_MISSING",
            "test_case_intake",
            "count_matches_scenarios",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-requirements.yaml",
            "visual_requirements_count: 1",
            "VISUAL_REQUIREMENTS_MISSING",
            "visual_requirements",
            "count_matches_requirements",
        ),
    ],
)
def test_validators_block_declared_count_mismatch(
    kind,
    writer,
    validator,
    artifact,
    count_line,
    blocker,
    detail_key,
    match_key,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-count-mismatch"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    path = intake / artifact
    text = path.read_text(encoding="utf-8")
    text = text.replace(count_line, count_line.replace(": 1", ": 2"))
    path.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert blocker in payload["blockers"]
    assert payload["details"][detail_key][match_key] is False

    shutil.rmtree(work_dir)


def test_prd_validator_blocks_incomplete_evidence_front_matter():
    work_dir = ROOT / ".tmp" / "test-prd-validator-front-matter"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    (intake / "evidence-packet.md").write_text(
        "---\nready_gate: PASS\n---\n# PRD Evidence Packet\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "PRD_READY_WITHOUT_EVIDENCE" in payload["blockers"]

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    ("kind", "writer", "validator", "packet_name", "ready_blocker"),
    [
        ("prd", write_prd_intake_fixture, PRD_VALIDATOR, "evidence-packet.md", "PRD_READY_WITHOUT_EVIDENCE"),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "evidence-packet.md",
            "TEST_READY_WITHOUT_EVIDENCE",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-evidence-packet.md",
            "VISUAL_READY_WITHOUT_EVIDENCE",
        ),
    ],
)
def test_validators_block_blocked_evidence_packet(
    kind,
    writer,
    validator,
    packet_name,
    ready_blocker,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-blocked-packet"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    packet = intake / packet_name
    text = packet.read_text(encoding="utf-8")
    text = text.replace("ready_gate: PASS", "ready_gate: BLOCKED")
    packet.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert ready_blocker in payload["blockers"]

    shutil.rmtree(work_dir)


def test_test_case_validator_passes_complete_minimal_intake():
    work_dir = ROOT / ".tmp" / "test-case-validator-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "test-cases"
    write_test_case_intake_fixture(intake)

    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Test-case intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_test_case_validator_allows_remote_source_gap_but_blocks_integrity():
    work_dir = ROOT / ".tmp" / "test-case-validator-remote-source-gap"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "test-cases"
    write_test_case_intake_fixture(intake)

    (intake / "source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: issue",
                "source_integrity_complete: false",
                "captured_at: '2026-07-01T00:00:00Z'",
                "capture_method: remote_issue",
                "framework_or_format: issue",
                "execution_scope: regression",
                "snapshot_status: not_available",
                "integrity_gap_reason: Issue was referenced without a local exported snapshot.",
                "retrieval_metadata:",
                "  retrieved_at: '2026-07-01T00:00:00Z'",
                "  stable_url: https://example.com/issues/1",
                "  visible_title: Regression case",
                "source_files:",
                "  - path: https://example.com/issues/1",
                "    mime_type: text/html",
                "    checksum_status: unavailable",
                "    role: original",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "TEST_SOURCE_INTEGRITY_INCOMPLETE" in payload["blockers"]
    assert "TEST_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert "TEST_SCHEMA_INVALID" not in payload["blockers"]
    assert "TEST_SOURCE_FILE_MISSING" not in payload["blockers"]
    assert payload["details"]["source_files"][0]["remote_ref"] is True

    shutil.rmtree(work_dir)


def test_test_case_validator_blocks_missing_assertions_and_coverage():
    work_dir = ROOT / ".tmp" / "test-case-validator-missing-assertions"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "test-cases"
    write_test_case_intake_fixture(intake)

    text = (intake / "test-case-intake.yaml").read_text(encoding="utf-8")
    text = text.replace("assertions_complete: true", "assertions_complete: false")
    text = text.replace("coverage_gaps_recorded: true", "coverage_gaps_recorded: false")
    text = text.replace("    assertions: ['save path returns success']", "    assertions: []")
    text = text.replace("coverage_gaps:\n  - Error-state coverage is not present in the fixture.\n", "coverage_gaps: []\n")
    text = text.replace("    coverage_signal: happy_path_present_error_path_missing", "    coverage_signal: ''")
    (intake / "test-case-intake.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "TEST_ASSERTIONS_MISSING" in result.stdout
    assert "TEST_COVERAGE_GAPS_MISSING" in result.stdout
    assert "TEST_READY_WITHOUT_EVIDENCE" in result.stdout

    shutil.rmtree(work_dir)


def test_test_case_validator_reports_schema_errors_in_json():
    work_dir = ROOT / ".tmp" / "test-case-validator-schema-error"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "test-cases"
    write_test_case_intake_fixture(intake)

    text = (intake / "test-case-intake.yaml").read_text(encoding="utf-8")
    text = text.replace("    category: unit", "    category: smoke")
    (intake / "test-case-intake.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "TEST_SCHEMA_INVALID" in payload["blockers"]
    assert "TEST_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert payload["details"]["schema_validation"]["test_case_intake"]["valid"] is False

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_missing_source_type_details():
    work_dir = ROOT / ".tmp" / "test-validator-missing-source-details"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "image", "low", "wireframe.png")

    text = (intake / "design-source-manifest.yaml").read_text(encoding="utf-8")
    text = text.split("source_details:", 1)[0]
    (intake / "design-source-manifest.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["visual_source_manifest"]["valid"] is False

    shutil.rmtree(work_dir)


def test_validator_blocks_unsupported_visual_source_type():
    work_dir = ROOT / ".tmp" / "test-validator-unsupported-source"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "sketch", "high", "design.sketch")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "VISUAL_SOURCE_TYPE_UNSUPPORTED" in result.stdout
    assert "VISUAL_SCHEMA_INVALID" in result.stdout
    assert "VISUAL_READY_WITHOUT_EVIDENCE" in result.stdout

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_unbounded_inferred_claim():
    work_dir = ROOT / ".tmp" / "test-validator-unbounded-inference"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "image", "medium", "wireframe.png")

    text = (intake / "visual-requirements.yaml").read_text(encoding="utf-8")
    text = text.replace("    evidence_type: observed", "    evidence_type: inferred")
    (intake / "visual-requirements.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SCHEMA_INVALID" in payload["blockers"]
    assert "VISUAL_INFERENCE_CONTRACT_INVALID" in payload["blockers"]
    assert payload["details"]["visual_requirements"]["evidence_type_counts"]["inferred"] == 1

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_candidate_promoted_to_accepted_claim():
    work_dir = ROOT / ".tmp" / "test-validator-candidate-promoted"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "image", "medium", "wireframe.png")

    text = (intake / "visual-requirements.yaml").read_text(encoding="utf-8")
    text = text.replace("    evidence_type: observed", "    evidence_type: candidate")
    text = text.replace("    confidence: high", "    confidence: medium")
    text = text.replace(
        f"    fidelity_level: medium",
        "\n".join(
            [
                "    inference_rule: visual_button_shape + short_text_label",
                "    confidence_method: rule_score_v1",
                "    score_breakdown:",
                "      - signal: visual_button_shape",
                "        weight: 0.25",
                "      - signal: short_text_label",
                "        weight: 0.2",
                "    downstream_use: accepted_claim",
                "    missing_evidence:",
                "      - component_instance",
                "    blocking_conditions:",
                "      - promote only after component or prototype evidence exists",
                "    fidelity_level: medium",
            ]
        ),
    )
    (intake / "visual-requirements.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SCHEMA_INVALID" in payload["blockers"]
    assert "VISUAL_INFERENCE_CONTRACT_INVALID" in payload["blockers"]

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_unsupported_claim_even_when_packet_says_pass():
    work_dir = ROOT / ".tmp" / "test-validator-unsupported-claim"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")

    text = (intake / "visual-requirements.yaml").read_text(encoding="utf-8")
    text = text.replace("    evidence_type: observed", "    evidence_type: unsupported")
    text = text.replace(
        "    engineering_action: Implement matching hierarchy",
        "\n".join(
            [
                "    blocker_code: FIGMA_UNSUPPORTED_STATE_INFERENCE",
                "    reason: No variant, prototype state, naming convention, or source note defines loading behavior.",
                "    downstream_use: blocked",
                "    missing_evidence:",
                "      - variant_state",
                "      - prototype_state",
                "    blockers:",
                "      - FIGMA_UNSUPPORTED_STATE_INFERENCE",
                "    engineering_action: Keep the loading state unresolved",
            ]
        ),
    )
    (intake / "visual-requirements.yaml").write_text(text, encoding="utf-8")

    metadata = intake / "figma-metadata.part-001.xml"
    metadata.write_text("<figma><node id=\"1\" name=\"Root\" /></figma>\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(metadata.read_bytes()).hexdigest()
    (intake / "figma-metadata.index.yaml").write_text(
        "\n".join(
            [
                "file_url: https://www.figma.com/file/example",
                "file_key: example",
                "page_id: page-1",
                "selected_node_ids: ['1']",
                "captured_at: '2026-06-22T00:00:00Z'",
                "mcp_tool: get_metadata",
                "design_version_or_timestamp: '2026-06-22T00:00:00Z'",
                "selected_subtree_complete: true",
                "raw_metadata_complete: true",
                "expected_root_node_ids: ['1']",
                "captured_root_node_ids: ['1']",
                "missing_root_node_ids: []",
                "gap_count: 0",
                "gaps: []",
                "shards:",
                "  - path: figma-metadata.part-001.xml",
                f"    byte_size: {metadata.stat().st_size}",
                f"    sha256: {digest}",
                "    root_node_ids: ['1']",
                "    node_count: 1",
                "    truncated: false",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (intake / "figma-node-inventory.yaml").write_text(
        "\n".join(
            [
                "raw_node_count: 1",
                "inventory_node_count: 1",
                "excluded_node_count: 0",
                "missing_node_count: 0",
                "duplicate_node_count: 0",
                "truncated_raw_evidence: false",
                "node_inventory_coverage: 100%",
                "parity_passed: true",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_BLOCKER_LINT_ERRORS" in payload["blockers"]
    assert "VISUAL_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert payload["details"]["visual_requirements"]["evidence_type_counts"]["unsupported"] == 1

    shutil.rmtree(work_dir)


def test_validator_passes_complete_minimal_figma_intake():
    work_dir = ROOT / ".tmp" / "test-validator-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")

    metadata = intake / "figma-metadata.part-001.xml"
    metadata.write_text("<figma><node id=\"1\" name=\"Root\" /></figma>\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(metadata.read_bytes()).hexdigest()

    (intake / "figma-metadata.index.yaml").write_text(
        "\n".join(
            [
                "file_url: https://www.figma.com/file/example",
                "file_key: example",
                "page_id: page-1",
                "selected_node_ids:",
                "  - '1'",
                "captured_at: '2026-06-22T00:00:00Z'",
                "mcp_tool: get_metadata",
                "design_version_or_timestamp: '2026-06-22T00:00:00Z'",
                "selected_subtree_complete: true",
                "raw_metadata_complete: true",
                "expected_root_node_ids:",
                "  - '1'",
                "captured_root_node_ids:",
                "  - '1'",
                "missing_root_node_ids: []",
                "gap_count: 0",
                "gaps: []",
                "shards:",
                "  - path: figma-metadata.part-001.xml",
                f"    byte_size: {metadata.stat().st_size}",
                f"    sha256: {digest}",
                "    root_node_ids:",
                "      - '1'",
                "    node_count: 1",
                "    truncated: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "figma-node-inventory.yaml").write_text(
        "\n".join(
            [
                "raw_node_count: 1",
                "inventory_node_count: 1",
                "excluded_node_count: 0",
                "missing_node_count: 0",
                "duplicate_node_count: 0",
                "truncated_raw_evidence: false",
                "node_inventory_coverage: 100%",
                "parity_passed: true",
                "",
            ]
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Visual design intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_validator_blocks_legacy_figma_only_without_manifest():
    work_dir = ROOT / ".tmp" / "test-validator-legacy-figma"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    intake.mkdir(parents=True)

    metadata = intake / "figma-metadata.part-001.xml"
    metadata.write_text("<figma><node id=\"1\" name=\"Root\" /></figma>\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(metadata.read_bytes()).hexdigest()

    (intake / "figma-metadata.index.yaml").write_text(
        "\n".join(
            [
                "file_url: https://www.figma.com/file/example",
                "file_key: example",
                "page_id: page-1",
                "selected_node_ids:",
                "  - '1'",
                "captured_at: '2026-06-22T00:00:00Z'",
                "mcp_tool: get_metadata",
                "design_version_or_timestamp: '2026-06-22T00:00:00Z'",
                "selected_subtree_complete: true",
                "raw_metadata_complete: true",
                "expected_root_node_ids:",
                "  - '1'",
                "captured_root_node_ids:",
                "  - '1'",
                "missing_root_node_ids: []",
                "gap_count: 0",
                "gaps: []",
                "shards:",
                "  - path: figma-metadata.part-001.xml",
                f"    byte_size: {metadata.stat().st_size}",
                f"    sha256: {digest}",
                "    root_node_ids:",
                "      - '1'",
                "    node_count: 1",
                "    truncated: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "figma-node-inventory.yaml").write_text(
        "\n".join(
            [
                "raw_node_count: 1",
                "inventory_node_count: 1",
                "excluded_node_count: 0",
                "missing_node_count: 0",
                "duplicate_node_count: 0",
                "truncated_raw_evidence: false",
                "node_inventory_coverage: 100%",
                "parity_passed: true",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "figma-evidence-packet.md").write_text(
        "# Figma Evidence Packet\n\n- ready_gate: PASS\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "VISUAL_SOURCE_MANIFEST_MISSING" in result.stdout
    assert "FIGMA_READY_WITHOUT_COMPLETENESS_PROOF" in result.stdout

    shutil.rmtree(work_dir)


def test_html_ssot_validator_passes_complete_minimal_bundle():
    work_dir = ROOT / ".tmp" / "test-html-ssot-validator-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    html_dir = work_dir / "visual-design" / "figma2htmlssot"
    write_html_ssot_fixture(html_dir)

    result = subprocess.run(
        [sys.executable, str(HTML_SSOT_VALIDATOR), str(html_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "HTML SSOT readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_html_ssot_validator_blocks_missing_directory():
    result = subprocess.run(
        [sys.executable, str(HTML_SSOT_VALIDATOR), "missing-dir"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "HTML_SSOT_REQUIRED_ARTIFACT_MISSING" in result.stdout


def test_html_ssot_validator_blocks_source_intake_blocked():
    work_dir = ROOT / ".tmp" / "test-html-ssot-source-blocked"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    html_dir = work_dir / "visual-design" / "figma2htmlssot"
    write_html_ssot_fixture(html_dir)
    packet = html_dir.parent / "visual-evidence-packet.md"
    packet.write_text(
        "---\n"
        "ready_gate: BLOCKED\n"
        "blockers: [VISUAL_REQUIREMENTS_MISSING]\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 0\n"
        "generated_at: '2026-06-23T00:00:00Z'\n"
        "---\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(HTML_SSOT_VALIDATOR), "--json", str(html_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "HTML_SSOT_SOURCE_INTAKE_BLOCKED" in payload["blockers"]

    shutil.rmtree(work_dir)


def test_html_ssot_validator_reports_schema_errors_in_json():
    work_dir = ROOT / ".tmp" / "test-html-ssot-schema-error"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    html_dir = work_dir / "visual-design" / "figma2htmlssot"
    write_html_ssot_fixture(html_dir)
    figma_map = json.loads((html_dir / "figma-map.json").read_text(encoding="utf-8"))
    figma_map["mappings"][0].pop("selector")
    (html_dir / "figma-map.json").write_text(json.dumps(figma_map), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(HTML_SSOT_VALIDATOR), "--json", str(html_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "HTML_SSOT_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["figma_map"]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    ("edit_kind", "expected_blocker"),
    [
        ("missing_selector", "HTML_SSOT_FIGMA_NODE_COVERAGE_INCOMPLETE"),
        ("component_state", "HTML_SSOT_COMPONENT_STATE_COVERAGE_INCOMPLETE"),
        ("page", "HTML_SSOT_PAGE_COVERAGE_INCOMPLETE"),
        ("asset", "HTML_SSOT_ASSET_TRACEABILITY_INCOMPLETE"),
        ("viewport", "HTML_SSOT_VIEWPORT_CAPTURE_INCOMPLETE"),
        ("visual_diff", "HTML_SSOT_VISUAL_DIFF_BLOCKED"),
        ("known_gap", "HTML_SSOT_KNOWN_GAP_UNRESOLVED"),
    ],
)
def test_html_ssot_validator_blocks_incomplete_coverage(edit_kind, expected_blocker):
    work_dir = ROOT / ".tmp" / f"test-html-ssot-{edit_kind}"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    html_dir = work_dir / "visual-design" / "figma2htmlssot"
    write_html_ssot_fixture(html_dir)

    if edit_kind == "missing_selector":
        html = (html_dir / "visual-spec.html").read_text(encoding="utf-8")
        (html_dir / "visual-spec.html").write_text(html.replace('data-figma-node-id="2"', ""), encoding="utf-8")
    elif edit_kind == "component_state":
        coverage = (html_dir / "coverage-report.md").read_text(encoding="utf-8")
        (html_dir / "coverage-report.md").write_text(
            coverage.replace("component_state_coverage_complete: true", "component_state_coverage_complete: false"),
            encoding="utf-8",
        )
    elif edit_kind == "page":
        figma_map = json.loads((html_dir / "figma-map.json").read_text(encoding="utf-8"))
        figma_map["mappings"] = [item for item in figma_map["mappings"] if item["acceptance_unit"] != "page"]
        (html_dir / "figma-map.json").write_text(json.dumps(figma_map), encoding="utf-8")
    elif edit_kind == "asset":
        assets = json.loads((html_dir / "assets-manifest.json").read_text(encoding="utf-8"))
        assets["assets"][0]["source_refs"] = []
        (html_dir / "assets-manifest.json").write_text(json.dumps(assets), encoding="utf-8")
    elif edit_kind == "viewport":
        shutil.rmtree(html_dir / "screenshots")
        (html_dir / "screenshots").mkdir()
    elif edit_kind == "visual_diff":
        coverage = (html_dir / "coverage-report.md").read_text(encoding="utf-8")
        (html_dir / "coverage-report.md").write_text(
            coverage.replace("visual_diff_status: pass", "visual_diff_status: blocked"),
            encoding="utf-8",
        )
    elif edit_kind == "known_gap":
        (html_dir / "known-gaps.md").write_text("# Known Gaps\n\nBLOCKED: missing mobile state.\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(HTML_SSOT_VALIDATOR), "--json", str(html_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert expected_blocker in payload["blockers"]

    shutil.rmtree(work_dir)


def test_structured_ir_validator_passes_complete_minimal_bundle():
    work_dir = ROOT / ".tmp" / "test-structured-ir-validator-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    ir_dir = work_dir / "visual-design" / "structured-ir"
    write_structured_ir_fixture(ir_dir)

    result = subprocess.run(
        [sys.executable, str(STRUCTURED_IR_VALIDATOR), str(ir_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Structured IR intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_structured_ir_validator_blocks_source_intake_blocked():
    work_dir = ROOT / ".tmp" / "test-structured-ir-source-blocked"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    ir_dir = work_dir / "visual-design" / "structured-ir"
    write_structured_ir_fixture(ir_dir)
    packet = ir_dir.parent / "visual-evidence-packet.md"
    packet.write_text(
        "---\n"
        "ready_gate: BLOCKED\n"
        "blockers: [VISUAL_REQUIREMENTS_MISSING]\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 0\n"
        "generated_at: '2026-07-01T00:00:00Z'\n"
        "---\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(STRUCTURED_IR_VALIDATOR), "--json", str(ir_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "IR_SOURCE_INTAKE_BLOCKED" in payload["blockers"]
    assert "IR_READY_WITHOUT_EVIDENCE" in payload["blockers"]

    shutil.rmtree(work_dir)


def test_structured_ir_validator_reports_schema_errors_in_json():
    work_dir = ROOT / ".tmp" / "test-structured-ir-schema-error"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    ir_dir = work_dir / "visual-design" / "structured-ir"
    write_structured_ir_fixture(ir_dir)
    text = (ir_dir / "structured-ir.yaml").read_text(encoding="utf-8")
    (ir_dir / "structured-ir.yaml").write_text(
        text.replace("    role: button\n", ""),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(STRUCTURED_IR_VALIDATOR), "--json", str(ir_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "IR_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["structured_ir"]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    ("artifact", "detail_key"),
    [
        ("structured-ir.yaml", "structured_ir"),
        ("ir-assertions.yaml", "ir_assertions"),
    ],
)
def test_structured_ir_validator_rejects_unknown_blocker_codes(artifact, detail_key):
    work_dir = ROOT / ".tmp" / f"test-structured-ir-unknown-blocker-{detail_key}"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    ir_dir = work_dir / "visual-design" / "structured-ir"
    write_structured_ir_fixture(ir_dir)

    path = ir_dir / artifact
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("    blockers: []", "    blockers: [NOT_A_BLOCKER]", 1), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(STRUCTURED_IR_VALIDATOR), "--json", str(ir_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "IR_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"][detail_key]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    ("edit_kind", "expected_blocker"),
    [
        ("provider_evidence", "IR_PROVIDER_EVIDENCE_MISSING"),
        ("provider_evidence_blocker", "IR_PROVIDER_EVIDENCE_MISSING"),
        ("product_ambiguity", "IR_PRODUCT_AMBIGUITY_UNRESOLVED"),
        ("locator", "IR_LOCATOR_STRATEGY_INVALID"),
        ("ownership", "IR_DOWNSTREAM_OWNERSHIP_LEAK"),
        ("assertion_coverage", "IR_ASSERTION_COVERAGE_INCOMPLETE"),
        ("assertion_blocker", "IR_ASSERTION_COVERAGE_INCOMPLETE"),
        ("cross_ref", "IR_ASSERTION_COVERAGE_INCOMPLETE"),
        ("evidence_packet", "IR_READY_WITHOUT_EVIDENCE"),
    ],
)
def test_structured_ir_validator_blocks_readiness_failures(edit_kind, expected_blocker):
    work_dir = ROOT / ".tmp" / f"test-structured-ir-{edit_kind}"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    ir_dir = work_dir / "visual-design" / "structured-ir"
    write_structured_ir_fixture(ir_dir)

    if edit_kind == "provider_evidence":
        text = (ir_dir / "structured-ir.yaml").read_text(encoding="utf-8")
        (ir_dir / "structured-ir.yaml").write_text(
            text.replace("provider_evidence_complete: true", "provider_evidence_complete: false"),
            encoding="utf-8",
        )
    elif edit_kind == "provider_evidence_blocker":
        text = (ir_dir / "structured-ir.yaml").read_text(encoding="utf-8")
        (ir_dir / "structured-ir.yaml").write_text(
            text.replace("    blockers: []", "    blockers: [IR_PROVIDER_EVIDENCE_MISSING]", 1),
            encoding="utf-8",
        )
    elif edit_kind == "product_ambiguity":
        text = (ir_dir / "structured-ir.yaml").read_text(encoding="utf-8")
        (ir_dir / "structured-ir.yaml").write_text(
            text.replace("product_ambiguities: []", "product_ambiguities:\n  - Save disabled conditions are not specified."),
            encoding="utf-8",
        )
    elif edit_kind == "locator":
        text = (ir_dir / "structured-ir.yaml").read_text(encoding="utf-8")
        (ir_dir / "structured-ir.yaml").write_text(
            text.replace("      value: button[name='Save']", "      value: '#save-button'"),
            encoding="utf-8",
        )
    elif edit_kind == "ownership":
        text = (ir_dir / "structured-ir.yaml").read_text(encoding="utf-8")
        (ir_dir / "structured-ir.yaml").write_text(
            text.replace("    blockers: []", "    blockers: []\n    code_component: SaveButton", 1),
            encoding="utf-8",
        )
    elif edit_kind == "assertion_coverage":
        text = (ir_dir / "ir-assertions.yaml").read_text(encoding="utf-8")
        (ir_dir / "ir-assertions.yaml").write_text(
            text.replace("    ci_suitability: ci_low_cost", "    ci_suitability: manual_review"),
            encoding="utf-8",
        )
    elif edit_kind == "assertion_blocker":
        text = (ir_dir / "ir-assertions.yaml").read_text(encoding="utf-8")
        (ir_dir / "ir-assertions.yaml").write_text(
            text.replace("    blockers: []", "    blockers: [IR_PROVIDER_EVIDENCE_MISSING]", 1),
            encoding="utf-8",
        )
    elif edit_kind == "cross_ref":
        text = (ir_dir / "ir-assertions.yaml").read_text(encoding="utf-8")
        (ir_dir / "ir-assertions.yaml").write_text(
            text.replace("      - IR-home-save-default", "      - IR-missing"),
            encoding="utf-8",
        )
    elif edit_kind == "evidence_packet":
        (ir_dir / "ir-evidence-packet.md").write_text(
            "---\n"
            "ready_gate: BLOCKED\n"
            "blockers: [IR_PROVIDER_EVIDENCE_MISSING]\n"
            "source_ref_count: 1\n"
            "extracted_item_count: 1\n"
            "generated_at: '2026-07-01T00:00:00Z'\n"
            "---\n",
            encoding="utf-8",
        )

    result = subprocess.run(
        [sys.executable, str(STRUCTURED_IR_VALIDATOR), "--json", str(ir_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert expected_blocker in payload["blockers"]

    shutil.rmtree(work_dir)
