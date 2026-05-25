# WI-1006 Plan

1. Demote root README installer sections from adapter installer guidance to deprecated legacy artifact evidence.
2. Update adoption release/version/install docs so `loom` CLI is the only active release line and installer `latest` / `loom-installer-v*` are legacy evidence only.
3. Update installer package README files so command examples are clearly legacy and release notes reflect the #1005 sunset state.
4. Align doc-sync and release/version surface checker needles with the deprecated legacy wording.
5. Validate release surface, version surface, CLI contract, installer checks, `make check`, and Loom carrier checks.
6. Open the issue-scoped PR for #1006 and consume PR/merge evidence before closing the issue.
