# Spec Kit Intake Extension

Extract, normalize, and validate SDD-ready intake artifacts from PRDs, visual designs, visual requirements/spec structured asset packages, optional preview evidence, test cases, and other software sources before downstream Spec Kit workflows project them into requirements.

The first goal of intake is not to generate requirements. It is to preserve as much input information as possible and turn it into structured material that SDD `specify` can consume accurately.

The intake goal is high-information source restoration: extracted facts must be usable as provider-neutral engineering input, and every downstream projection should remain traceable to the original artifact.

Intake artifacts are validated in two layers: JSON Schema checks enforce the required structure, field types, and enums; readiness validators then check source integrity, traceability, hashes, gaps, and cross-file parity.

## Supported Intake Sources

- PRDs, product briefs, Markdown documents, PDFs, and exported docs
- Low-fidelity, medium-fidelity, and high-fidelity design drafts
- Static images such as PNG, JPG, WebP, and exported screens
- PDF design packs and annotated review documents
- Figma files, pages, frames, nodes, components, variables, and exported screenshots
- Optional Figma-derived component matrix preview and coverage review helpers with traceable component, state, variant, viewport, and screenshot coverage
- Visual requirements/spec structured asset packages with CI-friendly DOM, ARIA, token, state, locator, relation, and assertion facts
- Existing test cases, Gherkin files, QA exports, and test management spreadsheets

## Intake Scenario Coverage

Intake commands are organized by vertical source domain. Each domain uses the same evidence pattern: preserve the original source, normalize source-backed facts, keep uncertainty explicit, and report readiness before downstream Spec Kit workflows project the evidence.

| Domain | Vertical scenarios | Normalized artifact | Primary readiness focus |
| --- | --- | --- | --- |
| PRD | product briefs, Markdown PRDs, exported docs, PDFs, issue or epic links, mixed stakeholder notes | `prd-intake.yaml` | source identity, product intent traceability, scope boundaries, acceptance evidence, clarification gaps |
| Visual design | static images, wireframes, PDF design packs, Markdown design briefs, Figma files or selected nodes | `visual-requirements.yaml` and `visual-spec-package/` | source integrity, Figma-backed resource traceability, fidelity rules, visual requirement traceability, structured visual spec readiness, CI-low-cost assertion readiness |
| Figma preview helper | Figma files or selected nodes projected into component matrix review surfaces | `previews/component-matrix-preview.html` plus coverage YAML | Figma component coverage, component-state coverage, variant coverage, viewport screenshots, known gaps |
| Test cases | automated tests, Gherkin files, manual QA cases, spreadsheets, test management exports, bug or issue repro steps | `test-case-intake.yaml` | scenario traceability, assertion extraction, fixture evidence, coverage gaps, flaky or skipped case reporting |

Vertical instructions should never convert source evidence directly into downstream-owned requirement IDs, implementation tasks, or code component names. They produce provider-neutral intake facts that downstream workflows can consume with source refs intact.

## Commands

- `/speckit.intake.visual-design` captures or validates visual design evidence, Figma-backed resources, visual requirements, preview coverage evidence, and the visual spec package for the active feature.
- `/speckit.intake.prd` captures or validates PRD evidence and normalizes product intent, scope, business rules, acceptance criteria, and clarification items.
- `/speckit.intake.test-cases` captures or validates test case evidence and normalizes scenarios, assertions, fixtures, and coverage gaps.

## Artifact Layout

```text
specs/<feature>/intake/
├── prd/
│   ├── source-manifest.yaml
│   ├── source-files/
│   ├── prd-intake.yaml
│   └── evidence-packet.md
├── visual-design/
│   ├── design-source-manifest.yaml
│   ├── source-files/
│   ├── visual-requirements.yaml
│   ├── figma-metadata.part-001.xml
│   ├── figma-metadata.index.yaml
│   ├── figma-node-inventory.yaml
│   ├── visual-evidence-packet.md
│   ├── previews/
│   │   ├── component-matrix-preview.html
│   │   ├── component-coverage.yaml
│   │   ├── viewport-coverage.yaml
│   │   ├── known-gaps.md
│   │   └── screenshots/
│   └── visual-spec-package/
│       ├── visual-spec.yaml
│       ├── visual-spec-assertions.yaml
│       └── visual-spec-evidence-packet.md
└── test-cases/
    ├── source-manifest.yaml
    ├── source-files/
    ├── test-case-intake.yaml
    └── evidence-packet.md
```

Figma metadata artifacts are required for Figma visual-design sources. Image, PDF, and Markdown visual-design sources use `design-source-manifest.yaml`, source-file checksums, extracted visual requirements, and visual parity evidence instead. PRD and test-case domains use their own source manifests and normalized intake files.

Machine-readable JSON Schemas live under `templates/schemas/` and are used by the validators before readiness rules run. Preview helpers are defined by `templates/intake-visual-previews-contract.md` and use `component-coverage.schema.json` and `viewport-coverage.schema.json`. Visual spec packages use `visual-spec-package.schema.json` and `visual-spec-assertions.schema.json`.

All intake commands provide capture instructions, evidence contracts, and readiness validation. Visual design validation additionally checks visual fidelity and Figma metadata parity.
Component matrix preview validation is owned by `scripts/python/validate_visual_previews.py`, including cross-file checks for preview refs, visual spec refs, screenshots, component coverage, viewport coverage, and known gaps.
Visual spec package validation is owned by `scripts/python/validate_visual_spec_package.py`, including source readiness, schema, cross-reference, locator, downstream-ownership, provider-evidence, product-ambiguity, design-source resource traceability, and CI assertion checks.

## Requirements

- Spec Kit `>=0.8.10.dev0`
- Python validator dependencies: `PyYAML` and `jsonschema`
- Optional: `figma-mcp` for Figma metadata capture

## Install for Local Development

From a Spec Kit project:

```bash
specify extension add --dev C:/Users/24598/Documents/github/spec-kit-intake
```

## Install from Release

From a Spec Kit project:

```bash
specify extension add intake --from https://github.com/bigsmartben/spec-kit-intake/archive/refs/tags/v0.1.4.zip
```

Release artifacts must include source-backed provenance for the `bigsmartben/spec-kit` integration fork. The release workflow uploads `release-provenance.json` with:

- `repository_url`
- `release_version`
- `source_commit_sha`
- `download_url`
- `validation_evidence`

Then run:

```text
/speckit.intake.visual-design capture <image|pdf|markdown|figma source and scope>
/speckit.intake.visual-design validate
/speckit.intake.visual-design build-spec-package <visual-design intake scope>
/speckit.intake.visual-design validate-spec-package
/speckit.intake.visual-design build-previews <figma source or visual-design intake scope>
/speckit.intake.visual-design validate-previews
/speckit.intake.prd capture <prd source and scope>
/speckit.intake.prd validate
/speckit.intake.test-cases capture <test source and scope>
/speckit.intake.test-cases validate
```

## Visual Design Readiness Gate

Visual design intake passes only when:

- source identity, fidelity level, and source-file integrity are proven
- low, medium, or high-fidelity extraction rules are applied consistently
- extracted requirements preserve layout hierarchy, spacing, typography, color, assets, states, responsive behavior, and accessibility evidence at the fidelity level supplied
- non-observed visual claims use bounded inference fields and stay auditable
- candidate completions remain reference-only and unsupported claims emit blocker codes
- parity evidence explains how implementation output will be compared with the original design artifact
- Figma sources also pass raw metadata completeness and node-inventory parity
- no blocker lint errors exist

Visual design claims use these evidence types:

- `observed`: source-backed fact from preserved files, rendered evidence, Figma metadata, screenshots, or prototype metadata.
- `inferred`: high-confidence derived claim that includes an inference rule, confidence method, score breakdown, and blocking conditions.
- `candidate`: low- or medium-confidence completion with `downstream_use: reference_only`.
- `unsupported`: rejected or blocked claim with a stable blocker code.
- `missing` or `out_of_scope`: explicit absence or excluded surface.

For irregular Figma sources, intake may generate bounded candidate completions, but it must not infer business rules, permissions, form validation, error copy, loading or disabled states, data sources, analytics, security, or compliance behavior from visual appearance alone.

## Figma Preview Helper Readiness Gate

Figma-derived component matrix preview evidence passes only when:

- upstream Figma visual-design intake is ready
- every required component set, component instance, variant prop, state, size, density, theme, content sample, resource, and viewport is covered or recorded as a blocking missing record
- the minimum acceptance grain is covered: component instance, state, content sample, container constraint, and viewport
- required preview cells link back to Figma refs, `visual-spec.yaml` items, `component-coverage.yaml` records, and screenshot or diff evidence when available
- component coverage is expressed in `previews/component-coverage.yaml`
- viewport coverage is expressed in `previews/viewport-coverage.yaml`
- screenshot coverage and visual-diff status are recorded
- known gaps are explicit and no blocking gap remains unresolved

The preview validator emits blocker codes such as `VISUAL_PREVIEW_SOURCE_INTAKE_BLOCKED`, `VISUAL_PREVIEW_REQUIRED_ARTIFACT_MISSING`, `VISUAL_PREVIEW_SCHEMA_INVALID`, `VISUAL_PREVIEW_FIGMA_NODE_COVERAGE_INCOMPLETE`, `VISUAL_PREVIEW_COMPONENT_STATE_COVERAGE_INCOMPLETE`, `VISUAL_PREVIEW_PAGE_COVERAGE_INCOMPLETE`, `VISUAL_PREVIEW_ASSET_TRACEABILITY_INCOMPLETE`, `VISUAL_PREVIEW_VIEWPORT_CAPTURE_INCOMPLETE`, `VISUAL_PREVIEW_VISUAL_DIFF_BLOCKED`, and `VISUAL_PREVIEW_KNOWN_GAP_UNRESOLVED`.

## Visual Spec Package Readiness Gate

The visual requirements/spec structured asset package passes only when:

- upstream visual-design intake is ready
- `visual-spec.yaml`, `visual-spec-assertions.yaml`, and `visual-spec-evidence-packet.md` exist
- visual spec items preserve source refs, page, region, role, state, viewport, provider-neutral locator strategy, expectations, acceptance intent, confidence, status, and blockers
- implementation resources, images, and token refs are traceable to the design source; for Figma sources, they must trace back to Figma refs
- assertions reference existing visual spec items and include ready `ci_low_cost` checks
- missing provider evidence and product ambiguity are represented with distinct blocker paths
- locator strategies avoid implementation-owned CSS selectors, XPath, generated class names, downstream test IDs, code component names, tasks, or requirement IDs
- component matrix previews, screenshots, and visual diffs remain helper evidence rather than the target deliverable

The visual spec package validator emits blocker codes such as `VISUAL_SPEC_SOURCE_INTAKE_BLOCKED`, `VISUAL_SPEC_REQUIRED_ARTIFACT_MISSING`, `VISUAL_SPEC_SCHEMA_INVALID`, `VISUAL_SPEC_INTAKE_INCOMPLETE`, `VISUAL_SPEC_PROVIDER_EVIDENCE_MISSING`, `VISUAL_SPEC_PRODUCT_AMBIGUITY_UNRESOLVED`, `VISUAL_SPEC_ASSERTION_COVERAGE_INCOMPLETE`, `VISUAL_SPEC_LOCATOR_STRATEGY_INVALID`, `VISUAL_SPEC_DOWNSTREAM_OWNERSHIP_LEAK`, and `VISUAL_SPEC_READY_WITHOUT_EVIDENCE`.

## Development

Validate the manifest from the local `spec-kit` checkout:

```bash
python -c "from pathlib import Path; from specify_cli.extensions import ExtensionManifest; ExtensionManifest(Path('extension.yml')); print('manifest ok')"
```

Validate visual-design artifacts:

```bash
python scripts/python/validate_visual_design_intake.py specs/<feature>/intake/visual-design
```

Validate component matrix preview helpers:

```bash
python scripts/python/validate_visual_previews.py specs/<feature>/intake/visual-design/previews
```

Validate visual spec package artifacts:

```bash
python scripts/python/validate_visual_spec_package.py specs/<feature>/intake/visual-design/visual-spec-package
```

Validate PRD artifacts:

```bash
python scripts/python/validate_prd_intake.py specs/<feature>/intake/prd
```

Validate test-case artifacts:

```bash
python scripts/python/validate_test_cases_intake.py specs/<feature>/intake/test-cases
```
