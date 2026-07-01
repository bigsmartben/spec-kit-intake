---
description: Create or validate structured UI acceptance IR for CI-friendly checks.
---

## User Input

```text
$ARGUMENTS
```

Classify the input before proceeding:

- `source`: existing visual-design intake directory, visual requirement refs, Figma metadata refs, or HTML SSOT enhancement refs
- `output_dir`: existing or target structured IR artifact directory
- `validation_request`: validate, check, gate, assertions, CI, or readiness request
- `review_guidance`: target platform, viewport set, required states, semantic regions, ARIA expectations, token coverage, or assertion scope

## Goal

Create, update, or validate an Intake-owned structured UI acceptance IR layer for the active Spec Kit feature. The IR is the CI-friendly validation substrate: it carries deterministic DOM, ARIA, design-token, state, locator-strategy, relation, and assertion facts without forcing downstream commands to parse provider-native files or run full-page screenshot diffs as the primary gate.

Default output directory:

```text
specs/<feature>/intake/visual-design/structured-ir/
```

Normative authority:

- `templates/intake-visual-design-contract.md` defines visual source evidence semantics.
- `templates/intake-structured-ir-contract.md` defines structured IR semantics, boundary, readiness, and blocker codes.
- `templates/schemas/structured-ir.schema.json` defines the machine-readable IR records.
- `templates/schemas/ir-assertions.schema.json` defines CI-friendly assertion records.
- `scripts/python/validate_structured_ir_intake.py` defines readiness validation.
- This command owns structured IR routing, capture orchestration, validation invocation, and report shape.

## Operating Boundaries

- Treat structured IR as the primary low-cost UI acceptance substrate.
- Treat HTML SSOT, screenshots, and visual diffs as enhancement evidence only; do not make them the primary acceptance contract.
- Preserve original source refs, visual requirement refs, DES refs, optional HTML SSOT refs, and explicit blocker refs.
- Do not generate downstream-owned requirement IDs, tasks, code component names, implementation-owned selectors, final test framework files, or product semantics.
- Do not infer business rules, permissions, validation behavior, analytics, data sources, security, or compliance behavior from visual appearance alone.
- Distinguish missing provider evidence from product ambiguity with separate blocker codes and evidence records.
- If required source evidence is unavailable, create a blocked `ir-evidence-packet.md` and stop before claiming readiness.

## Completeness Units

The minimum structured acceptance unit is:

```text
IR item + source ref + semantic locator strategy + expectation + assertion + viewport/state
```

Use this hierarchy:

- IR item: provider-neutral DOM, ARIA, token, state, content, relation, and locator-strategy fact.
- Assertion: low-cost check over one or more IR items.
- CI substrate: the set of ready assertions with `ci_suitability: ci_low_cost`.

## Context Loading

1. Verify the current directory is a Spec Kit project by checking for `.specify/`, unless `$ARGUMENTS` points to a standalone artifact directory for extension development.
2. Identify the active feature:
   - Prefer `SPECIFY_FEATURE` when set.
   - Otherwise use the current Git branch name when it matches a directory under `specs/`.
   - Otherwise inspect `specs/` and choose the most recent feature directory only if there is a single clear candidate.
   - If the feature cannot be identified and no standalone artifact directory was provided, stop and ask the user to set `SPECIFY_FEATURE` or run from the feature branch.
3. Read `.specify/extensions/intake/intake-config.yml` when present.
4. Read `templates/intake-visual-design-contract.md`, `templates/intake-structured-ir-contract.md`, and existing visual-design intake artifacts before creating or validating IR artifacts.
5. Read optional `figma2htmlssot/` artifacts only as enhancement evidence.
6. Read any existing structured IR artifacts and preserve stable valid IR IDs unless the source ref or normalized fact changes.

## Mode Routing

- Build mode: use when `$ARGUMENTS` names source refs, visual requirement refs, target viewports, required states, semantic regions, DOM/ARIA/token expectations, or asks to build, generate, derive, update, or recapture IR.
- Validate mode: use when `$ARGUMENTS` includes `validate`, `check`, `gate`, `assertions`, `CI`, `readiness`, or only names an existing structured IR output directory.
- Build then validate: use when both source and validation intent are present, or after build artifacts are updated.

## Build Procedure

1. Resolve the upstream visual-design intake directory and target structured IR output directory.
2. Ensure upstream visual-design intake passes readiness:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_design_intake.py <visual-design-intake-dir>
```

3. Create or update:
   - `structured-ir.yaml`: source-backed UI acceptance facts.
   - `ir-assertions.yaml`: low-cost assertions over IR items.
   - `ir-evidence-packet.md`: readiness summary, blocker separation, and next corrective action.
4. For each IR item, record stable `IR-*` ID, source refs, optional visual requirement refs, page, region, role, state, viewport, provider-neutral locator strategy, expectations, acceptance intent, confidence, status, and blockers.
5. For each assertion, record stable `IRA-*` ID, `IR-*` refs, assertion type, expected value, evidence refs, CI suitability, status, and blockers.
6. Record missing provider evidence as `IR_PROVIDER_EVIDENCE_MISSING`.
7. Record unresolved product ambiguity as `IR_PRODUCT_AMBIGUITY_UNRESOLVED`.
8. Record locator or ownership violations as `IR_LOCATOR_STRATEGY_INVALID` or `IR_DOWNSTREAM_OWNERSHIP_LEAK`.
9. Validate before reporting readiness:

```bash
python .specify/extensions/intake/scripts/python/validate_structured_ir_intake.py <structured-ir-dir>
```

## Validation Procedure

1. Resolve the structured IR output directory from `$ARGUMENTS` or the active feature.
2. Run:

```bash
python .specify/extensions/intake/scripts/python/validate_structured_ir_intake.py <structured-ir-dir>
```

3. The validator confirms:
   - upstream visual-design intake is ready
   - required artifacts exist
   - schemas validate
   - item and assertion counts match actual arrays
   - assertions reference existing IR items
   - source refs and provider evidence are complete
   - product ambiguities are explicit and not collapsed into missing provider evidence
   - locator strategies are provider-neutral
   - no downstream-owned requirement IDs, tasks, code component names, implementation-owned selectors, or product semantics leak into the IR
   - at least one ready `ci_low_cost` assertion exists
   - `ir-evidence-packet.md` readiness is PASS only when no blocking issue remains

4. Apply these blocker codes when validation fails:
   - `IR_SOURCE_INTAKE_BLOCKED`
   - `IR_REQUIRED_ARTIFACT_MISSING`
   - `IR_SCHEMA_INVALID`
   - `IR_INTAKE_INCOMPLETE`
   - `IR_PROVIDER_EVIDENCE_MISSING`
   - `IR_PRODUCT_AMBIGUITY_UNRESOLVED`
   - `IR_ASSERTION_COVERAGE_INCOMPLETE`
   - `IR_LOCATOR_STRATEGY_INVALID`
   - `IR_DOWNSTREAM_OWNERSHIP_LEAK`
   - `IR_READY_WITHOUT_EVIDENCE`

## Readiness Authority

Use this precedence when sources disagree:

1. Upstream visual-design intake is canonical for source evidence and limitations.
2. `structured-ir.yaml` is canonical for provider-neutral UI acceptance facts.
3. `ir-assertions.yaml` is canonical for low-cost CI assertion records.
4. HTML SSOT, screenshots, and visual diffs are enhancement evidence only.
5. `ir-evidence-packet.md` explains readiness, accepted exceptions, and blockers for human review.

Do not promote structured IR as ready when provider evidence is missing, product ambiguity is unresolved, assertions are not CI-suitable, or downstream implementation ownership has leaked into the intake layer.

## Report

Return:

- mode executed: build, validate, or build_then_validate
- output or validated directory
- upstream visual-design intake readiness
- IR item count
- assertion count
- ready CI-low-cost assertion count
- provider evidence gaps
- product ambiguity gaps
- locator or ownership violations
- readiness result
- blocker codes
- next corrective action when blocked
