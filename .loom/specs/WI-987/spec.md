# WI-987 Spec

## Goal

Align closeout retained review backlink checks with the carrier-only head-binding semantics already used by merge and PR gates.

## Acceptance

- `closeout check` validates the retained review record against the PR head with head-binding semantics instead of strict `reviewed_head == head_sha` equality.
- Carrier-only post-review changes remain accepted when they are limited to Loom governance carriers, review records, recovery/status surfaces, or their shadow evidence.
- Implementation drift after review remains fail-closed.
- `loom_check.py` includes a synthetic fixture proving closeout review backlink carrier-only behavior.
- Source, generated skills surface, and demo runtime copies stay synchronized.
- FR `#835` closeout check for PR `#984` passes with the retained review backlink marked `carrier-only`.

## Non-Goals

- Do not change the authoritative review decision model.
- Do not relax implementation drift detection.
- Do not implement model/profile work tracked outside WI-987.
