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
        "user": {"id": 1, "login": "maintainer"},
        "state": "closed" if merged else "open", "draft": False,
        "merged_at": "2026-07-11T00:00:00Z" if merged else None,
        "merge_commit_sha": MERGE if merged else None,
    }
    trees = {
        f"repos/o/r/git/commits/{HEAD}": {"tree": {"sha": "tree-head"}},
        "repos/o/r/git/trees/tree-head?recursive=1": {"truncated": truncated, "tree": [{"path": "src/a.py", "sha": "c" * 40, "mode": "100644", "type": "blob"}]},
        "repos/o/r": {"default_branch": "main"},
        "repos/o/r/issues/2025": {"number": 2025, "labels": [{"name": "work-item"}]},
        "repos/o/r/actions/artifacts/7": {"id": 7, "digest": "sha256:" + "d" * 64, "expired": False, "name": "loom-host-attestation-1", "workflow_run": {"id": 9}, "created_at": "2026-07-11T00:01:00Z"},
        "repos/o/r/actions/runs/9": {"id": 9, "event": "pull_request_target", "status": "completed", "conclusion": "success", "head_sha": run_head, "workflow_id": 3, "path": ".github/workflows/host-attestation-evidence.yml", "pull_requests": [{"number": 1}], "triggering_actor": {"id": 1, "login": "maintainer"}, "run_started_at": "2026-07-11T00:00:00Z", "updated_at": "2026-07-11T00:02:00Z"},
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


def single_maintainer_reads(_root, path):
    if path.endswith("/reviews"):
        return [], []
    if "/collaborators?" in path:
        return [{"id": 1, "login": "maintainer", "permissions": {"push": True}}], []
    if path.endswith("/issues/2025/comments?per_page=100"):
        return [{"id": 11, "body": f"<!-- loom:host-attestation-artifact pr:1 head:{HEAD} id:7 -->", "created_at": "2026-07-11T00:03:00Z", "author_association": "OWNER", "user": {"id": 1, "login": "maintainer"}}], []
    return [], [f"unexpected host list path: {path}"]


def closing_relation(_root, _query, variables):
    return {"repository": {"issue": {"closedByPullRequestsReferences": {"pageInfo": {"hasNextPage": False}, "nodes": [{"number": 1, "merged": True}]}}}}, []


pr, mapping = facts()
read_json = reader(pr, mapping)
attestation, errors = github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, read_json=read_json, read_list=reviews)
assert not errors and attestation and attestation["artifact"]["digest"].startswith("sha256:")

single, errors = github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, work_item=2025, read_json=read_json, read_list=single_maintainer_reads, review_policy="single_maintainer")
assert not errors and single and single["review_policy"]["mode"] == "single_maintainer" and single["semantic_tree"]["semantic_digest"].startswith("sha256:")
assert single["review_policy"]["assertion_verified"] is True
def missing_assertion_reads(_root, path):
    if path.endswith("/reviews"):
        return [], []
    if "/collaborators?" in path:
        return [{"id": 1, "login": "maintainer", "permissions": {"push": True}}], []
    if path.endswith("/issues/2025/comments?per_page=100"):
        return [], []
    return [], [f"unexpected host list path: {path}"]
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, work_item=2025, read_json=read_json, read_list=missing_assertion_reads, review_policy="single_maintainer")[1]
def two_maintainers(_root, path):
    if path.endswith("/reviews"):
        return [], []
    return [
        {"id": 1, "login": "maintainer", "permissions": {"push": True}},
        {"id": 2, "login": "other", "permissions": {"push": True}},
    ], []
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, work_item=2025, read_json=read_json, read_list=two_maintainers, review_policy="single_maintainer")[1]
def single_changes_requested(_root, path):
    if path.endswith("/reviews"):
        return [{"id": 5, "state": "CHANGES_REQUESTED", "commit_id": HEAD, "user": {"id": 2}}], []
    return [{"id": 1, "login": "maintainer", "permissions": {"push": True}}], []
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, work_item=2025, read_json=read_json, read_list=single_changes_requested, review_policy="single_maintainer")[1]
pr_mismatch, mapping_mismatch = facts()
mapping_mismatch["repos/o/r/actions/runs/9"]["triggering_actor"] = {"id": 2, "login": "other"}
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, work_item=2025, read_json=reader(pr_mismatch, mapping_mismatch), read_list=single_maintainer_reads, review_policy="single_maintainer")[1]
pr_stale, mapping_stale = facts()
mapping_stale["repos/o/r/actions/artifacts/7"]["created_at"] = "2026-07-11T00:10:00Z"
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, work_item=2025, read_json=reader(pr_stale, mapping_stale), read_list=single_maintainer_reads, review_policy="single_maintainer")[1]

pr_recover, mapping_recover = facts(merged=True)
mapping_recover["repos/o/r/actions/artifacts/7"]["expired"] = True
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 7, work_item=2025, allow_merged=True, read_json=reader(pr_recover, mapping_recover), read_list=single_maintainer_reads, review_policy="single_maintainer")[1]
mapping_recover["repos/o/r/actions/artifacts/8"] = {"id": 8, "digest": "sha256:" + "e" * 64, "expired": False, "name": "loom-host-attestation-1", "workflow_run": {"id": 10}, "created_at": "2026-07-20T00:01:00Z"}
mapping_recover["repos/o/r/actions/runs/10"] = {"id": 10, "event": "workflow_dispatch", "status": "completed", "conclusion": "success", "head_sha": "f" * 40, "head_branch": "main", "workflow_id": 3, "path": ".github/workflows/host-attestation-evidence.yml", "pull_requests": [], "triggering_actor": {"id": 1, "login": "maintainer"}, "run_started_at": "2026-07-20T00:00:00Z", "updated_at": "2026-07-20T00:02:00Z"}
def recovery_reads(_root, path):
    if path.endswith("/reviews"):
        return [], []
    if "/collaborators?" in path:
        return [{"id": 1, "login": "maintainer", "permissions": {"push": True}}], []
    if path.endswith("/issues/2025/comments?per_page=100"):
        return [{"id": 12, "body": f"<!-- loom:host-attestation-artifact pr:1 head:{HEAD} id:8 -->", "created_at": "2026-07-20T00:03:00Z", "author_association": "OWNER", "user": {"id": 1, "login": "maintainer"}}], []
    return [], [f"unexpected host list path: {path}"]
recovered, errors = github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 8, work_item=2025, allow_merged=True, read_json=reader(pr_recover, mapping_recover), read_list=recovery_reads, review_policy="single_maintainer")
assert not errors and recovered and recovered["workflow_run"]["binding"] == "workflow_dispatch_reattest"
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 8, allow_merged=True, read_json=reader(pr_recover, mapping_recover), read_list=reviews, review_policy="approved")[1]
mapping_recover["repos/o/r/actions/runs/10"]["head_branch"] = "work/old-ref"
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 8, work_item=2025, allow_merged=True, read_json=reader(pr_recover, mapping_recover), read_list=recovery_reads, review_policy="single_maintainer")[1]
mapping_recover["repos/o/r/actions/runs/10"]["head_branch"] = "main"
mapping_recover["repos/o/r/issues/2025"]["labels"] = [{"name": "fr"}]
assert github_host.github_pr_attestation_readback(ROOT, "o", "r", 1, 8, work_item=2025, allow_merged=True, read_json=reader(pr_recover, mapping_recover), read_list=recovery_reads, review_policy="single_maintainer")[1]
mapping_recover["repos/o/r/issues/2025"]["labels"] = [{"name": "work-item"}]

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
    artifact.write_text(json.dumps({"artifact_id": True}), encoding="utf-8")
    try:
        module._artifact_id(artifact)
    except ValueError:
        pass
    else:
        raise AssertionError("boolean artifact ids must be rejected")

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
for required in ("pull_request_target:", "workflow_dispatch:", "Existing PR to re-attest", "github.rest.pulls.get", "host-attestation-evidence", "actions/upload-artifact@v4", "contents: read", "retention-days: 14"):
    assert required in workflow, f"host-attestation workflow is missing {required}"
for forbidden in ("actions/checkout", "github.event.pull_request.title", "github.event.pull_request.body", "secrets."):
    assert forbidden not in workflow, f"host-attestation workflow must not consume {forbidden}"

print("host attestation checks passed")
