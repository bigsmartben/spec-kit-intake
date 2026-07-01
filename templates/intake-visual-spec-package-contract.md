# Visual Spec Package Contract

Required visual requirements/spec structured asset package artifacts and readiness gates. Runtime agents or external intake tools derive high-fidelity UI delivery facts from traceable visual/design evidence before downstream workflows choose their own test runner, selectors, requirement IDs, or implementation ownership.

Visual Spec Package does not generate requirements, tasks, code component names, implementation-owned selectors, or product semantics. It preserves source-backed DOM, ARIA, token, state, relation, locator-strategy, and assertion facts that can be consumed by low-cost CI checks.

## Artifact Family

Default directory:

```text
specs/<feature>/intake/visual-design/visual-spec-package/
```

Required files:

- `visual-spec.yaml`
- `visual-spec-assertions.yaml`
- `visual-spec-evidence-packet.md`

Optional helper refs may point to `previews/component-matrix-preview.html`, `previews/component-coverage.yaml`, `previews/viewport-coverage.yaml`, screenshots, or visual diff reports, but preview panels and screenshots are not the target deliverable.

## Source Boundary

Visual Spec Package is downstream of source evidence and upstream of implementation tests:

1. Visual/design intake records source-backed facts, limitations, Figma metadata, and visual requirements.
2. Preview helpers record component matrix review, component coverage, viewport coverage, and screenshot comparison evidence when useful.
3. Visual Spec Package records deterministic visual requirements/spec facts suitable for downstream implementation and CI.

If source evidence is missing, truncated, contradictory, or blocked, visual spec package must record `VISUAL_SPEC_PROVIDER_EVIDENCE_MISSING`. If the source is clear but product behavior is ambiguous, it must record `VISUAL_SPEC_PRODUCT_AMBIGUITY_UNRESOLVED`. Do not collapse these into one generic gap.

## `visual-spec.yaml`

The file must normalize UI acceptance facts into provider-neutral records.

Top-level fields:

- visual_spec_package_complete: true|false
- visual_spec_item_count: integer
- source_refs_complete: true|false
- provider_evidence_complete: true|false
- resources_traceable_to_design_source: true|false
- product_ambiguities_recorded: true|false
- downstream_ownership_free: true|false
- product_ambiguities: array
- blocker_lint_errors: array
- items: array

Each item must include:

- id: stable `VS-*` identifier owned by intake
- source_refs: preserved source evidence refs
- des_refs: optional design evidence source refs
- visual_requirement_refs: optional refs to `visual-requirements.yaml`
- preview_refs: optional refs to `previews/component-matrix-preview.html`, `previews/component-coverage.yaml`, `previews/viewport-coverage.yaml`, screenshots, or diff evidence
- page, region, role, state, viewport
- locator: provider-neutral strategy, value, and `implementation_owned: false`
- expectations: DOM, ARIA, design token, state, content, or relation facts
- acceptance_intent: what low-cost check this fact supports
- evidence_type: observed|inferred|candidate|unsupported|missing|out_of_scope
- confidence: low|medium|high
- status: ready|blocked|reference_only|out_of_scope
- blockers: array

Locator strategies must not be implementation-owned CSS selectors, XPath, generated class names, or downstream test IDs. Candidate test IDs may be recorded only as `test-id-candidate` and must remain intake-owned guidance, not implementation ownership.

## `visual-spec-assertions.yaml`

The file must describe low-cost assertions over visual spec items.

Top-level fields:

- assertions_complete: true|false
- assertion_count: integer
- ci_assertions_complete: true|false
- blocker_lint_errors: array
- assertions: array

Each assertion must include:

- id: stable `VSA-*` identifier owned by intake
- visual_spec_refs: one or more `VS-*` refs
- assertion_type: visible|hidden|enabled|disabled|contains_text|role|aria|token|relation|state|viewport
- acceptance_intent
- expected
- evidence_refs
- ci_suitability: ci_low_cost|manual_review|blocked
- status: ready|blocked|reference_only|out_of_scope
- blockers

Ready assertions should use `ci_suitability: ci_low_cost`. Manual review and blocked assertions are allowed as explicit evidence, but they cannot satisfy CI readiness.

## Readiness

Visual Spec Package intake is ready only when:

- upstream visual-design intake readiness is PASS
- required visual spec package artifacts exist
- both schemas validate
- item and assertion counts match their arrays
- every ready assertion references an existing visual spec item
- source refs and provider evidence are complete
- implementation resources, images, and token refs are traceable to the design source; for Figma sources, they must trace back to Figma refs
- product ambiguities are explicitly recorded and unresolved ambiguity does not masquerade as missing provider evidence
- locators are provider-neutral and not implementation-owned
- no downstream requirement IDs, tasks, code component names, implementation-owned selectors, or product semantics leak into the visual spec package
- at least one ready `ci_low_cost` assertion exists
- `visual-spec-evidence-packet.md` front matter reports `ready_gate: PASS` with no blockers

## Blocker Codes

- `VISUAL_SPEC_SOURCE_INTAKE_BLOCKED`
- `VISUAL_SPEC_REQUIRED_ARTIFACT_MISSING`
- `VISUAL_SPEC_SCHEMA_INVALID`
- `VISUAL_SPEC_INTAKE_INCOMPLETE`
- `VISUAL_SPEC_PROVIDER_EVIDENCE_MISSING`
- `VISUAL_SPEC_PRODUCT_AMBIGUITY_UNRESOLVED`
- `VISUAL_SPEC_ASSERTION_COVERAGE_INCOMPLETE`
- `VISUAL_SPEC_LOCATOR_STRATEGY_INVALID`
- `VISUAL_SPEC_DOWNSTREAM_OWNERSHIP_LEAK`
- `VISUAL_SPEC_READY_WITHOUT_EVIDENCE`
