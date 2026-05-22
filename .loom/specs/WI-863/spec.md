# WI-863 Spec

## Outcome

Codex App main-thread review runs can discover or report Codex App host proof consistently, even when the environment carries `CODEX_CI=1`.

When app-server endpoint, thread id, thread cwd, target root, and reviewed head are bound, `review run` selects `loom/codex-app-review` by default. When proof is incomplete, the fallback remains `loom/default-codex-exec` and the output names the missing proof.

## Acceptance

- `CODEX_CI=1` does not force headless fallback when valid Codex App host proof is present.
- Missing or partial host proof produces a structured diagnostic naming absent locators.
- App adapter metadata records selected adapter, selection source, fallback reason, proof sources, discovery evidence, thread/target binding, and reviewed head.
- Existing headless and unavailable app-server fallback behavior remains intact.
- A focused fixture proves `CODEX_CI=1` plus valid thread proof still selects `loom/codex-app-review`.
- A focused fixture proves missing proof still falls back and exposes missing-proof diagnostics.
- A live Codex App host-context review proof reaches `review run -> normalized evidence -> review record -> merge-ready or review gate consumption`.
- Raw Codex App review output remains runtime evidence only and does not become authored review truth.

## Non Goals

- Do not reopen the #746 adapter migration scope.
- Do not remove `loom/default-codex-exec`.
- Do not make App raw review output a second authored truth source.
- Do not expand Loom into a multi-engine marketplace.
