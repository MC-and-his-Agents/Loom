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

- Work Item: <owner>/<repo>/work_item/<GitHub issue number>
- Issue:
- Spec / plan:

## PR Metadata Machine Carrier

If this repository declares repo-specific PR metadata in `.loom/companion/repo-interface.json`, preserve the declared machine block exactly. Render the body to a file, update it with `gh pr edit --body-file <file>`, and read the live PR body back before review. After current-head review, run public `loom pr gate ... --attestation-artifact-input <artifact> --full-output --json`, save the complete readback to a repo-relative ignored file, then pass the same artifact and that file to `loom merge-ready --attestation-artifact-input <artifact> --pr-gate-result-file <file>`.

<!-- loom:repo-pr-metadata
{
  "schema_version": "loom-repo-pr-metadata/v1",
  "metadata_contract_id": "loom-governance-intensity",
  "surface": "merge_ready",
  "fields": {
    "work_item_locator": "<owner>/<repo>/work_item/<GitHub issue number>",
    "governance_intensity": "standard",
    "change_class": "contract",
    "suite_path": "minimal",
    "suite_not_applicable": null,
    "review_requirement": "current_head_review_required",
    "fact_chain_required": true,
    "pr_gate_required": true,
    "release_judgment": "no_release",
    "closeout_required": true,
    "upgrade_triggers": []
  },
  "source": {"rendered_hash": "sha256:replace-with-rendered-body-hash-or-renderer-id"},
  "parser_version": "loom-pr-metadata-parser/v2"
}
-->
