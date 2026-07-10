# WI-1741 Implementation Contract

## Implementation Scope

- Add deterministic changed-path validation profile selection to `loom ship`.
- Report the selected profile, source surface, changed paths source, reasons, and suggested validation commands in the short ship diagnostic payload.
- Preserve explicit `--validation-profile` overrides, including full validation override for otherwise light changes.
- Keep release/package/version surfaces on the release validation profile.
- Add focused ship wrapper contract coverage and align README / CLI matrix docs.

## Non-Goals

- Do not implement the #1739 metadata repair, carrier refresh, or shadow parity preflight repair chain.
- Do not implement #1742 inline or host-only closeout e2e behavior.
- Do not publish, tag, or otherwise perform #1743 release closeout.
- Do not replace hosted PR checks, review gates, or `loom_check` with the profile selector.
