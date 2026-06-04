# Execution Breakdown

| Unit | Scope | Owner | Status | Validation |
| --- | --- | --- | --- | --- |
| unit-wi-1302-1 | Extend suite-ready gate consumption. | main thread | done | `git diff --check`; focused contract check |
| unit-wi-1302-2 | Add regression coverage for legal and invalid formal-suite NA decisions. | main thread | done | focused docs-contract suite NA gate contract assertion |
| unit-wi-1302-3 | Regenerate managed skill runtime copies. | main thread | done | `tools/loom.py skills generate --apply --json`; `skills check` in full contract check |
