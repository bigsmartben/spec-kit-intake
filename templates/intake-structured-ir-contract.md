# Structured IR Intake Contract

Required structured UI acceptance IR artifacts and readiness gates. Runtime agents or external intake tools derive CI-friendly UI acceptance facts from traceable visual/design evidence before downstream workflows choose their own test runner, selectors, requirement IDs, or implementation ownership.

Structured IR does not generate requirements, tasks, code component names, implementation-owned selectors, or product semantics. It preserves source-backed DOM, ARIA, token, state, relation, locator-strategy, and assertion facts that can be consumed by low-cost CI checks.

## Artifact Family

Default directory:

```text
specs/<feature>/intake/visual-design/structured-ir/
```

Required files:

- `structured-ir.yaml`
- `ir-assertions.yaml`
- `ir-evidence-packet.md`

Optional enhancement refs may point to `figma2htmlssot/visual-spec.html`, `figma-map.json`, screenshots, or visual diff reports, but HTML SSOT and screenshots are not the primary acceptance substrate.

## Source Boundary

Structured IR is downstream of source evidence and upstream of implementation tests:

1. Visual/design intake records source-backed facts, limitations, Figma metadata, and visual requirements.
2. HTML SSOT records runnable visual preview and screenshot comparison surfaces when available.
3. Structured IR records deterministic acceptance facts suitable for CI.

If source evidence is missing, truncated, contradictory, or blocked, structured IR must record `IR_PROVIDER_EVIDENCE_MISSING`. If the source is clear but product behavior is ambiguous, it must record `IR_PRODUCT_AMBIGUITY_UNRESOLVED`. Do not collapse these into one generic gap.

## `structured-ir.yaml`

The file must normalize UI acceptance facts into provider-neutral records.

Top-level fields:

- ir_complete: true|false
- ir_item_count: integer
- source_refs_complete: true|false
- provider_evidence_complete: true|false
- product_ambiguities_recorded: true|false
- downstream_ownership_free: true|false
- product_ambiguities: array
- blocker_lint_errors: array
- items: array

Each item must include:

- id: stable `IR-*` identifier owned by intake
- source_refs: preserved source evidence refs
- des_refs: optional design evidence source refs
- visual_requirement_refs: optional refs to `visual-requirements.yaml`
- html_ssot_refs: optional enhancement refs only
- page, region, role, state, viewport
- locator: provider-neutral strategy, value, and `implementation_owned: false`
- expectations: DOM, ARIA, design token, state, content, or relation facts
- acceptance_intent: what low-cost check this fact supports
- evidence_type: observed|inferred|candidate|unsupported|missing|out_of_scope
- confidence: low|medium|high
- status: ready|blocked|reference_only|out_of_scope
- blockers: array

Locator strategies must not be implementation-owned CSS selectors, XPath, generated class names, or downstream test IDs. Candidate test IDs may be recorded only as `test-id-candidate` and must remain intake-owned guidance, not implementation ownership.

## `ir-assertions.yaml`

The file must describe low-cost assertions over IR items.

Top-level fields:

- assertions_complete: true|false
- assertion_count: integer
- ci_assertions_complete: true|false
- blocker_lint_errors: array
- assertions: array

Each assertion must include:

- id: stable `IRA-*` identifier owned by intake
- ir_refs: one or more `IR-*` refs
- assertion_type: visible|hidden|enabled|disabled|contains_text|role|aria|token|relation|state|viewport
- acceptance_intent
- expected
- evidence_refs
- ci_suitability: ci_low_cost|manual_review|blocked
- status: ready|blocked|reference_only|out_of_scope
- blockers

Ready assertions should use `ci_suitability: ci_low_cost`. Manual review and blocked assertions are allowed as explicit evidence, but they cannot satisfy CI readiness.

## Readiness

Structured IR intake is ready only when:

- upstream visual-design intake readiness is PASS
- required IR artifacts exist
- both schemas validate
- item and assertion counts match their arrays
- every ready assertion references an existing IR item
- source refs and provider evidence are complete
- product ambiguities are explicitly recorded and unresolved ambiguity does not masquerade as missing provider evidence
- locators are provider-neutral and not implementation-owned
- no downstream requirement IDs, tasks, code component names, implementation-owned selectors, or product semantics leak into the IR
- at least one ready `ci_low_cost` assertion exists
- `ir-evidence-packet.md` front matter reports `ready_gate: PASS` with no blockers

## Blocker Codes

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
