# WI-689 Spec

## Acceptance

- Installed Loom status is documented as evidence, not a second governance truth source.
- Status distinguishes host-adapter plugin installs from generated single-skill installs and reports host adapter, installed layer, version context, runtime state, upgrade eligibility, failed layer, and fail-closed reason.
- Missing or inconsistent installed version metadata fails closed.
- `upgrade-plan` is read-only and reports installed version context, available payload context, changed paths, drift, rollback path, failed layer, and fail-closed reason.
- `verify-upgrade` is read-only and reports whether the installed layer is current, drifted, upgrade-available, or incompatible after rehearsal/install.
- Installer fixtures cover current/no-op, upgrade-available, drift, and missing/incompatible metadata with rollback visibility for failed rehearsal.

## Non-Goals

- Do not publish the root `v0.8.0` release.
- Do not replace repo-owned governance carriers with installer status.
- Do not make external runtime installation the default path.
