# Visual Preview Coverage Contract

Required component matrix preview helper artifacts and readiness gates. Preview coverage artifacts help reviewers inspect whether design-source components, states, variants, resources, content samples, and viewports were enumerated before downstream implementation, but they are not the target visual requirements/spec asset package.

Preview coverage does not generate requirements, implementation HTML, product semantics, downstream-owned selectors, tasks, code component names, or design tokens. It preserves source-backed coverage evidence that points back to design-source refs and forward to `visual-spec-package/` records.

## Artifact Family

Default directory:

```text
specs/<feature>/intake/visual-design/previews/
```

Required files:

- `component-matrix-preview.html`
- `component-coverage.yaml`
- `viewport-coverage.yaml`
- `known-gaps.md`
- `screenshots/`

## Source Boundary

Preview coverage is downstream of visual-design intake and adjacent to the visual spec package:

1. Visual-design intake records source-backed facts, limitations, Figma metadata, node inventory, and visual requirements.
2. Visual Spec Package records the target structured visual requirements/spec facts.
3. Preview coverage records reviewer-oriented matrix surfaces and machine-readable coverage evidence.

If Figma or design-source evidence is missing, truncated, contradictory, or blocked, preview coverage must record a `VISUAL_PREVIEW_*` blocker and keep the affected coverage cell missing. Do not silently complete a missing state, variant, resource, or viewport in preview HTML.

## `component-matrix-preview.html`

The file is a human-review panel only. Each preview cell should expose stable anchors such as `id` or `data-preview-id` so `component-coverage.yaml` can reference the cell.

The preview panel may display:

- component sets and component instances
- variant props
- states
- size, density, and theme dimensions
- content samples, including long copy, empty, overflow, and error-like visual states when source-backed
- viewport-specific snapshots or links
- missing, blocked, and out-of-scope labels

The preview panel must not define product semantics, downstream component names, implementation selectors, design tokens, or source-backed facts that are absent from the design source.

## `component-coverage.yaml`

The file is the machine-readable component coverage evidence.

Top-level fields:

- ready_gate: PASS|BLOCKED
- blockers: array of `VISUAL_PREVIEW_*` or allowed upstream `VISUAL_SPEC_*` blocker codes
- components: array

Each component must include:

- id
- source_ref
- name
- required_dimensions
- covered
- missing

Each covered record must include:

- visual_spec_ref
- preview_ref
- optional source_ref
- optional screenshot_refs
- dimension values matching the component's required dimensions when applicable

Each missing record must include:

- missing_type: state|variant|viewport|resource|asset|token|screenshot|visual_diff|source_evidence|visual_spec_ref|preview_ref
- reason
- blocker

## `viewport-coverage.yaml`

The file is the machine-readable viewport coverage evidence.

Each viewport record must include:

- id
- width
- height
- covered
- source_refs
- visual_spec_refs
- page_refs
- screenshot_refs
- visual_diff_status: pass|blocked|not_applicable

Missing viewport evidence must stay explicit in `missing` records or top-level blockers.

## Readiness

Preview coverage is ready only when:

- upstream visual-design intake readiness is PASS
- required preview artifacts exist
- `component-coverage.yaml` validates against `component-coverage.schema.json`
- `viewport-coverage.yaml` validates against `viewport-coverage.schema.json`
- every covered component record has a `visual_spec_ref`
- every covered component record has a `preview_ref` that resolves inside `component-matrix-preview.html`
- no missing record remains for required component states, variants, resources, assets, tokens, screenshots, visual diffs, source evidence, visual spec refs, or preview refs
- every viewport record is covered and has existing screenshot refs
- at least one viewport has page refs
- `known-gaps.md` has no unresolved `BLOCKED`, `UNRESOLVED`, or `TODO` marker

## Blocker Codes

- `VISUAL_PREVIEW_SOURCE_INTAKE_BLOCKED`
- `VISUAL_PREVIEW_REQUIRED_ARTIFACT_MISSING`
- `VISUAL_PREVIEW_SCHEMA_INVALID`
- `VISUAL_PREVIEW_FIGMA_NODE_COVERAGE_INCOMPLETE`
- `VISUAL_PREVIEW_COMPONENT_STATE_COVERAGE_INCOMPLETE`
- `VISUAL_PREVIEW_PAGE_COVERAGE_INCOMPLETE`
- `VISUAL_PREVIEW_ASSET_TRACEABILITY_INCOMPLETE`
- `VISUAL_PREVIEW_VIEWPORT_CAPTURE_INCOMPLETE`
- `VISUAL_PREVIEW_VISUAL_DIFF_BLOCKED`
- `VISUAL_PREVIEW_KNOWN_GAP_UNRESOLVED`
