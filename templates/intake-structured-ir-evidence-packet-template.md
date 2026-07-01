---
ready_gate: BLOCKED
blockers: []
source_ref_count: 0
extracted_item_count: 0
generated_at: ""
---

# Structured IR Evidence Packet

Purpose: summarize structured UI acceptance IR readiness while preserving enough traceability for downstream CI workflows to consume deterministic DOM, ARIA, token, state, relation, locator-strategy, and assertion facts.

This packet is a human-readable readiness summary. Machine-readable UI acceptance facts are recorded in `structured-ir.yaml` and `ir-assertions.yaml` and validated by `templates/schemas/structured-ir.schema.json` and `templates/schemas/ir-assertions.schema.json`. This packet does not define downstream requirement IDs, implementation tasks, code component names, implementation-owned selectors, or final product behavior.

## Source Boundary

- Visual/design intake directory:
- Visual/design readiness:
- HTML SSOT enhancement refs, if used:
- Screenshot or visual diff refs, if used:

## IR Summary

- structured-ir.yaml:
- ir-assertions.yaml:
- structured IR item count:
- assertion count:
- CI-low-cost assertion count:

## Evidence Separation

- Missing provider evidence:
- Product ambiguities:
- Accepted out-of-scope surfaces:
- Manual-review-only assertions:

## Readiness

- ready_gate:
- blockers:
- next corrective action:
