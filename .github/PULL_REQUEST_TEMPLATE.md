## Summary

- Problem:
- Scope:

## Validation

- [ ] Verified locally
- [ ] Verified by automation
- [ ] Not applicable

Validation details:
- Python compile checks should use `make py-compile` or `python3 tools/py_compile_clean.py ...`; do not use bare `python3 -m py_compile ...` in the repository checkout.

## Risks And Follow-ups

- Risks:
- Follow-ups:

## Related Work

- Issue:
- Loom Work Item:
- Spec / plan:

## PR Metadata Machine Carrier

If this repository declares repo-specific PR metadata in `.loom/companion/repo-interface.json`, preserve the declared machine block exactly. Render the body to a file, update with `gh pr edit --body-file <file>`, read the PR body back, and run `loom pr metadata-preflight --body-file <rendered> --compare-body-file <readback>` before review or merge-ready.
