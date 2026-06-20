# WI-1626-1631-1634-1635 Plan Boundary

- WI-1626-1631-1634-1635 is a bounded PR5 convergence Work Item for issues #1626/#1631/#1634/#1635, with implementation scope limited by the Work Item carrier and suite path decision.
- Implement `loom host verify --host codex` as a hard verification of both metadata-only repository adoption and Codex user-level plugin provider registration.
- Ensure npm package contents serve only global CLI, source skills truth, and Codex user plugin payload; root `skills/` must not ship as a package payload.
- Keep legacy repo-local surfaces as hard gate blockers for verification and document the explicit migration path without automatic deletion.
- Require a separate release Work Item if this PR expands into VERSION changes, release workflow dispatch, tag creation, npm publish, GitHub Release creation, or milestone parent closeout.
