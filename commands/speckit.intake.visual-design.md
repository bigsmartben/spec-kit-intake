---
description: Capture or validate visual design intake for the active Spec Kit feature.
---

## User Input

```text
$ARGUMENTS
```

Classify the input before proceeding:

- `source`: image, PDF, Markdown design brief, Figma URL, file, page, frame, node, or exported design asset
- `intake_dir`: existing visual-design intake artifact directory
- `validation_request`: validate, check, gate, readiness, build-spec-package, validate-spec-package, build-previews, validate-previews, or CI-friendly assertion request
- `review_guidance`: target platform, required fidelity, capture scope, source precedence, Figma-backed resource requirements, or reviewer instructions

## Goal

Create, update, or validate provider-neutral visual design intake artifacts for the active Spec Kit feature. Intake preserves reachable design sources, raw provider evidence, stable source refs, checksums or retrieval metadata, schema-required visual facts, and the visual requirements/spec structured asset package so downstream SDD workflows can implement high-fidelity UI with traceability.

Default artifact directory:

```text
specs/<feature>/intake/visual-design/
```

Normative authority:

- `templates/schemas/*.json` defines machine-readable structure, required fields, types, and enums.
- `scripts/python/validate_visual_design_intake.py` defines readiness evaluation and blocker emission.
- `scripts/python/validate_visual_spec_package.py` defines structured visual spec package readiness.
- `scripts/python/validate_visual_previews.py` defines component matrix preview and coverage readiness.
- `templates/intake-visual-design-contract.md` defines semantic extraction policy, fidelity policy, and provider evidence policy.
- `templates/intake-visual-spec-package-contract.md` defines the visual requirements/spec structured asset package.
- `templates/intake-visual-previews-contract.md` defines preview coverage helper artifact structure, boundaries, and blocker semantics.
- This command only performs input routing, context loading, capture orchestration, validation invocation, and reporting.

## Operating Boundaries

- Preserve original design sources and record checksums before extraction.
- For Figma sources, implementation resources, images, exported assets, and token refs must trace back to Figma source refs.
- Extract visual requirements as traceable engineering input, not as unsupported prose summaries or downstream-specific schema projections.
- Treat `visual-spec-package/` as the target structured visual requirements/spec asset package for downstream delivery and CI-friendly checks.
- Treat `previews/component-matrix-preview.html`, screenshots, and visual diffs as optional human-review helper evidence only, not the target deliverable.
- Treat `previews/component-coverage.yaml` and `previews/viewport-coverage.yaml` as structured coverage evidence for reviewer completeness checks; they may support readiness but do not replace `visual-spec-package/`.
- Use bounded inference for dirty or incomplete design sources: observed claims are source-backed facts; inferred claims require explicit rules and high confidence; candidate claims are reference-only; unsupported claims must remain blocked.
- Mark low, medium, or high fidelity explicitly and apply the matching extraction rules.
- Use stable provider-neutral evidence IDs and source refs. Do not invent downstream-owned item IDs, requirement IDs, schema fields, code component names, or product semantics.
- Do not mark intake ready unless source integrity, requirement traceability, fidelity proof, and intake parity planning pass.
- Preserve raw Figma metadata exactly in `figma-metadata.part-*.xml` for Figma sources.
- Do not modify application source, tests, package manifests, feature implementation files, or existing Spec Kit core templates.
- If required tooling is unavailable, create a blocked evidence packet that records the missing tool and stop before claiming readiness.

## Context Loading

1. Verify the current directory is a Spec Kit project by checking for `.specify/`, unless `$ARGUMENTS` points to a standalone artifact directory for extension development.
2. Identify the active feature:
   - Prefer `SPECIFY_FEATURE` when set.
   - Otherwise use the current Git branch name when it matches a directory under `specs/`.
   - Otherwise inspect `specs/` and choose the most recent feature directory only if there is a single clear candidate.
   - If the feature cannot be identified and no standalone artifact directory was provided, stop and ask the user to set `SPECIFY_FEATURE` or run from the feature branch.
3. Read `.specify/extensions/intake/intake-config.yml` when present.
4. Read `templates/intake-visual-design-contract.md` and the referenced JSON Schemas from this extension before creating or validating artifacts.
5. Read any existing intake artifacts and preserve valid evidence unless the user explicitly asks to recapture it.

## Mode Routing

- Capture mode: use when `$ARGUMENTS` names an image, PDF, Markdown design brief, Figma URL, frame, node, platform, fidelity level, or asks to capture, ingest, update, or recapture visual evidence.
- Build spec package mode: use when `$ARGUMENTS` includes `build-spec-package`, `with spec package`, `structured visual spec`, `CI assertions`, or asks for downstream delivery/acceptance assets.
- Validate spec package mode: use when `$ARGUMENTS` includes `validate-spec-package`, `check spec package`, `visual spec readiness`, or only names an existing `visual-spec-package` directory.
- Build previews mode: use when `$ARGUMENTS` includes `build-previews`, `component matrix`, `preview coverage`, `coverage review`, `component-coverage`, or `viewport-coverage`.
- Validate previews mode: use when `$ARGUMENTS` includes `validate-previews`, `check previews`, `preview readiness`, or only names an existing `previews` directory.
- Validate mode: use when `$ARGUMENTS` includes `validate`, `check`, `gate`, `readiness`, or only names an existing visual-design intake directory.
- Capture then validate: use when both a source and validation intent are present, or after capture artifacts are updated.

## Capture Procedure

1. Resolve the source from `$ARGUMENTS` or existing artifact metadata:
   - source type: `image`, `pdf`, `markdown`, or `figma`
   - source path, URL, file key, page, frame, node, region, or Markdown section scope
   - required fidelity: `low`, `medium`, or `high`
   - design version or timestamp
2. Create `design-source-manifest.yaml` with contract-required source identity, integrity, coverage, capture method, and fidelity fields.
3. Preserve file-based originals under `source-files/`; for remote or Figma sources, record stable URLs and exported screenshots or assets, or record a structured gap/blocker when unavailable.
4. For Figma sources, preserve raw provider evidence before deriving normalized requirements:
   - write raw metadata shards as `figma-metadata.part-NNN.xml`
   - build `figma-metadata.index.yaml`
   - build `figma-node-inventory.yaml`
   - validate metadata and inventory parity before deriving visual requirements
5. Extract source-specific evidence:
   - image: dimensions, regions, OCR status, visual hierarchy, assets, and region coverage
   - pdf: original file hash, page count, rendered page refs, text extraction status, and page coverage
   - markdown: heading structure, design notes, embedded or linked assets, and visual requirement mappings
   - figma: complete descendant metadata, node inventory, variables/styles/components, screenshots, and assets
6. Classify source-domain scenario coverage using `templates/intake-visual-design-contract.md`; do not define additional scenario categories in this command.
7. Build `visual-requirements.yaml` according to `templates/schemas/visual-requirements.schema.json` and the semantic policies in `templates/intake-visual-design-contract.md`.
   - Record direct facts as `evidence_type: observed`.
   - Promote only rule-backed, high-confidence derived claims to `evidence_type: inferred` with `inference_rule`, `confidence_method`, `score_breakdown`, `downstream_use: accepted_claim`, and `blocking_conditions`.
   - Keep low- or medium-confidence completions as `evidence_type: candidate` with `downstream_use: reference_only` and `missing_evidence`.
   - Record unsupported or conflicting claims as `evidence_type: unsupported` with `blocker_code`, `reason`, `missing_evidence`, and `blockers`.
8. For unavailable required evidence, record a structured gap or blocker instead of omitting the field. Do not infer business rules, permissions, form validation, error copy, dynamic states, data sources, analytics, security, or compliance behavior from visual appearance alone.
9. Create or update `visual-evidence-packet.md` from `templates/intake-visual-design-evidence-packet-template.md` with readiness front matter and human-readable evidence notes; keep structured records in `visual-requirements.yaml`. Preserve an existing `figma-evidence-packet.md` only as a legacy compatibility alias when already configured by the host project.
10. Add an intake parity plan that records source-side comparison targets, methods, thresholds, accepted exceptions, and blocking difference categories without defining implementation capture artifacts or downstream delivery approval.
11. Run validation before reporting readiness.

## Visual Spec Package Procedure

1. Resolve the upstream visual-design intake directory and target `visual-spec-package/` directory.
2. Ensure visual-design intake passes readiness before building or validating the package:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_design_intake.py <visual-design-intake-dir>
```

3. Create or update:
   - `visual-spec.yaml`: structured visual requirements/spec facts for pages, regions, roles, states, viewports, locators, expectations, resources, tokens, and blockers.
   - `visual-spec-assertions.yaml`: low-cost assertions over visual spec items.
   - `visual-spec-evidence-packet.md`: readiness summary, blocker separation, resource traceability, and next corrective action.
4. For Figma sources, every implementation resource, image, exported asset, icon, font, color token, spacing token, radius token, typography token, and component-state ref must trace to Figma metadata, node, variable, style, component, or exported asset refs.
5. When preview artifacts exist, use them only as helper evidence:
   - `previews/component-matrix-preview.html` is a human review mirror for component sets, instances, variant props, states, sizes, density, theme, content samples, and viewports.
   - `previews/component-coverage.yaml` is the machine-readable component coverage record.
   - `previews/viewport-coverage.yaml` is the machine-readable viewport coverage record.
6. Do not use `component-matrix-preview.html` or preview rendering output as the source of truth for assets, tokens, product behavior, or requirements. Use Figma/source refs and visual-design intake evidence as authority.
7. Validate before reporting readiness:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_spec_package.py <visual-spec-package-dir>
```

## Preview Coverage Procedure

1. Resolve the upstream visual-design intake directory and target `previews/` directory.
2. Ensure visual-design intake passes readiness before building or validating preview coverage:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_design_intake.py <visual-design-intake-dir>
```

3. Create or update according to `templates/intake-visual-previews-contract.md`:
   - `component-matrix-preview.html`: human-review panel that exhaustively displays component sets, component instances, variant props, states, sizes, density, theme, content samples, and viewports.
   - `component-coverage.yaml`: machine-readable coverage records for each required component dimension, covered cell, missing cell, blocker, visual spec ref, preview ref, and Figma source ref.
   - `viewport-coverage.yaml`: machine-readable viewport coverage records with source refs, visual spec refs, page refs, screenshots, and visual diff status.
   - `known-gaps.md`: accepted exceptions, missing evidence, blocked captures, and owner or next action.
   - `screenshots/`: Figma source screenshots, preview screenshots, and diff outputs when tooling is available.
4. Link every preview cell back to its Figma node, component, variable, or style ref, its `visual-spec.yaml` item, its `component-coverage.yaml` record, and screenshot or diff evidence when available.
5. Do not use preview HTML as a requirements source, implementation HTML, product semantic source, token source, or replacement for `visual-spec.yaml`.
6. Do not silently complete missing Figma states, variants, viewports, resources, or images. Record them in `component-coverage.yaml`, `viewport-coverage.yaml`, or `known-gaps.md`.
7. Validate before reporting readiness:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_previews.py <previews-dir>
```

## Validation Procedure

1. Resolve the visual-design intake directory from `$ARGUMENTS` or the active feature.
2. Run:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_design_intake.py <intake-dir>
```

3. Prefer `--json` when a machine-readable result is needed. Report the validator result exactly:
   - `PASS` means the evidence passed JSON Schema structure checks and is ready for downstream projection as traceable visual engineering input.
   - `BLOCKED` means downstream workflows must keep design-derived requirements blocked, unresolved, or marked `[NEEDS CLARIFICATION]` instead of promoting unsupported design facts.

## Readiness Authority

Use this precedence when sources disagree:

1. JSON Schemas are canonical for structural validity in all modes.
2. `validate_visual_design_intake.py` is canonical for visual-design intake readiness status and blocker codes.
3. `validate_visual_spec_package.py` is canonical for visual spec package readiness status and blocker codes.
4. `validate_visual_previews.py` is canonical for preview coverage readiness status and blocker codes.
5. `templates/intake-visual-design-contract.md` is canonical for semantic extraction, fidelity, and provider evidence policy.
6. `templates/intake-visual-spec-package-contract.md` and `templates/intake-visual-previews-contract.md` are canonical for their artifact families.

Do not restate, reinterpret, or override blocker codes in this command.

## Report

Return:

- mode executed: capture, validate, capture_then_validate, build_spec_package, validate_spec_package, build_previews, or validate_previews
- output or validated directory
- source type and source refs captured, or the recorded gap/blocker
- required fidelity, or the recorded gap/blocker
- source file count and processed count, or the recorded gap/blocker
- visual requirement count
- visual spec package item count when built or validated
- visual spec package assertion count and CI-low-cost assertion count when built or validated
- preview component coverage count and viewport coverage count when built or validated
- Figma-backed resource traceability result when source is Figma
- readiness result
- blocker lint errors
- next corrective action when blocked
- open questions that must remain `[NEEDS CLARIFICATION]`
