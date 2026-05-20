# WI-816 Spec

## Outcome

HotCP runtime hygiene findings are fixed in Loom without leaking Loom source-repo fixtures or Python runtime cache into adopted repositories.

## Acceptance

- Closeout runs repo-declared `make loom-check` before falling back to repo-local or shared `loom_check.py`.
- Closeout payload records the gate source as `repo_declared_make_target`, `repo_local_loom_check`, or `shared_loom_check`.
- Installed Python runtime execution does not leave `.pyc`, `.pyo`, `.pyd`, or `__pycache__` residue in the host workspace.
- Installer drift checks fail closed when installed runtime cache residue exists.
- `.loom/stories/_template.md` and `.loom/bin/loom_story_carriers.py` are scaffolded, registered, generated, and checked.
- Story carrier checks fail closed for missing work item, missing artifact registration, missing schema markers, or copied placeholders.

## Non Goals

- Do not require adopted repositories to carry Loom source fixtures such as `examples/new-project`.
- Do not turn story carriers into Work Item or review verdict replacements.
- Do not expand this batch into profile redesign or unrelated governance behavior.

