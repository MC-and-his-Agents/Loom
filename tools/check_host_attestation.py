#!/usr/bin/env python3
"""Focused host-only fixture checks for #2025; no network or carrier input."""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "src/skills/shared/scripts"
WORKFLOW = ROOT / ".github" / "workflows" / "host-attestation-evidence.yml"
sys.path.insert(0, str(SCRIPTS))

import github_host

spec = importlib.util.spec_from_file_location("host_attestation", SCRIPTS / "host_attestation.py")
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

cli_spec = importlib.util.spec_from_file_location("loom_cli", ROOT / "tools" / "loom.py")
cli = importlib.util.module_from_spec(cli_spec)
assert cli_spec and cli_spec.loader
cli_spec.loader.exec_module(cli)

HEAD, MERGE = "a" * 40, "b" * 40


def facts(*, merged: bool = False, issue_completed: bool = True, compare_status: str = "ahead", truncated: bool = False, run_head: str = HEAD):
    pr = {
        "head": {"sha": HEAD}, "base": {"ref": "main"},
        "state": "closed" if merged else "open", "draft": False,
        "merged_at": "2026-07-11T00:00:00Z" if merged else None,
        "merge_commit_sha": MERGE if merged else None,
    }
    trees = {
        f"repos/o/r/git/commits/{HEAD}": {"tree": {"sha": "tree-head"}},
        "repos/o/r/git/trees/tree-head?recursive=1": {"truncated": truncated, "tree": [{"path": "src/a.py", "sha": "c" * 40, "mode": "100644", "type": "blob"}]},
        "repos/o/r": {"default_branch": "main"},
        "repos/o/r/actions/artifacts/7": {"id": 7, "digest": "sha256:" + "d" * 64, "expired": False, "name": "review", "workflow_run": {"id": 9}},
        "repos/o/r/actions/runs/9": {"id": 9, "event": "pull_request_target", "status": "completed", "conclusion": "success", "head_sha": run_head, "workflow_id": 3, "path": ".github/workflows/host-attestation-evidence.yml", "pull_requests": [{"number": 1}]},
    }
    if merged:
        trees.update({
            f"repos/o/r/compare/{MERGE}...main": {"status": compare_status},
            f"repos/o/r/git/commits/{MERGE}": {"tree": {"sha": "tree-merge"}},
            "repos/o/r/git/trees/tree-merge?recursive=1": {"truncated": False, "tree": [{"path": "src/a.py", "sha": "c" * 40, "mode": "100644", "type": "blob"}]},
            "repos/o/r/issues/2025": {"state": "closed" if issue_completed else "open", "state_reason": "completed" if issue_completed else None, "labels": [{"name": "work-item"}]},
        })
    return pr, trees


def reader(pr, mapping):
    def read_json(_root, path):
        if path.endswith("/pulls/1"):
            return pr, []
        return (mapping[path], []) if path in mapping else (None, [f"unexpected host path: {path}"])
    return read_json


def reviews(_root, path):
    assert path.endswith("/pulls/1/reviews")
    return [{"id": 4, "state": "APPROVED", "commit_id": HEAD, "user": {"id": 1}}], []


def closing_relation(_root, _query, variables):
    return {"repository": {"issue": {"closedByPullRequestsReferences": {"pageInfo": {"hasNextPage": False}, "nodes": [{"number": 1, "merged": True}]}}}}, []


pr, mapping = facts()
read_json = reader(pr, mapping)
attestation, errors = github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, read_json=read_json, read_list=reviews)
assert not errors and attestation and attestation["artifact"]["digest"].startswith("sha256:")

assert github_host._current_approved_review(
    [
        {"id": 1, "state": "APPROVED", "commit_id": HEAD, "user": {"id": 1}},
        {"id": 2, "state": "CHANGES_REQUESTED", "commit_id": HEAD, "user": {"id": 1}},
    ],
    HEAD,
)[1]

pr, mapping = facts(truncated=True)
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, read_json=reader(pr, mapping), read_list=reviews)[1]
pr, mapping = facts(run_head="e" * 40)
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, read_json=reader(pr, mapping), read_list=reviews)[1]
pr, mapping = facts()
mapping["repos/o/r/actions/artifacts/7"]["digest"] = "sha256:forged"
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, read_json=reader(pr, mapping), read_list=reviews)[1]
pr, mapping = facts()
pr["draft"] = True
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, read_json=reader(pr, mapping), read_list=reviews)[1]

pr, mapping = facts(merged=True)
closeout, errors = github_host.github_pr_closeout_readback(ROOT, "o", "r", 1, 2025, 7, read_json=reader(pr, mapping), read_list=reviews, read_graphql=closing_relation)
assert not errors and closeout and closeout["closeout"]["base_contains_merge"] is True
assert closeout["closeout"]["work_item_locator"] == "o/r/work_item/2025"
pr, mapping = facts(merged=True, issue_completed=False)
assert github_host.github_pr_closeout_readback(ROOT, "o", "r", 1, 2025, 7, read_json=reader(pr, mapping), read_list=reviews, read_graphql=closing_relation)[1]

def wrong_closing_relation(_root, _query, _variables):
    return {"repository": {"issue": {"closedByPullRequestsReferences": {"pageInfo": {"hasNextPage": False}, "nodes": [{"number": 2, "merged": True}]}}}}, []

pr, mapping = facts(merged=True)
assert github_host.github_pr_closeout_readback(ROOT, "o", "r", 1, 2025, 7, read_json=reader(pr, mapping), read_list=reviews, read_graphql=wrong_closing_relation)[1]

original_env, original_login, original_run = github_host.host_api_env_token_present, github_host.host_api_gh_logged_in, github_host.run_process
github_host.host_api_env_token_present, github_host.host_api_gh_logged_in = lambda: False, lambda _root: False
github_host.run_process = lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("anonymous fallback must not execute"))
assert github_host.gh_rest_authenticated_json(ROOT, "repos/o/r")[1]
github_host.host_api_env_token_present, github_host.host_api_gh_logged_in, github_host.run_process = original_env, original_login, original_run
pr, mapping = facts(merged=True, compare_status="diverged")
assert github_host.github_pr_closeout_readback(ROOT, "o", "r", 1, 2025, 7, read_json=reader(pr, mapping), read_list=reviews, read_graphql=closing_relation)[1]

with tempfile.TemporaryDirectory() as directory:
    artifact = Path(directory) / "artifact.json"
    artifact.write_text(json.dumps({"artifact_id": 7}), encoding="utf-8")
    assert module._artifact_id(artifact) == 7
    artifact.write_text(json.dumps({"artifact_id": 7, "digest": "forged"}), encoding="utf-8")
    try:
        module._artifact_id(artifact)
    except ValueError:
        pass
    else:
        raise AssertionError("locally asserted digest must be rejected")

forwarded: list[str] = []
original_attestation_main = cli.host_attestation_main
cli.host_attestation_main = lambda argv: forwarded.extend(argv) or 17
try:
    status = cli.main(
        [
            "loom",
            "attestation",
            "closeout",
            "--repo",
            "o/r",
            "--pr",
            "1",
            "--work-item",
            "2025",
            "--artifact-input",
            "artifact.json",
            "--json",
        ]
    )
finally:
    cli.host_attestation_main = original_attestation_main
assert status == 17
assert forwarded == [
    "closeout",
    "--repo",
    "o/r",
    "--pr",
    "1",
    "--work-item",
    "2025",
    "--artifact-input",
    "artifact.json",
    "--json",
]

workflow = WORKFLOW.read_text(encoding="utf-8")
for required in ("pull_request_target:", "host-attestation-evidence", "actions/upload-artifact@v4", "contents: read", "retention-days: 14"):
    assert required in workflow, f"host-attestation workflow is missing {required}"
for forbidden in ("actions/checkout", "github.event.pull_request.title", "github.event.pull_request.body", "secrets."):
    assert forbidden not in workflow, f"host-attestation workflow must not consume {forbidden}"

print("host attestation checks passed")
