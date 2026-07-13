#!/usr/bin/env python3
"""Focused checks for field authority and host-native lifecycle admission."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "src" / "skills" / "shared" / "scripts"
AUTHORITY = SCRIPTS / "authority_contract.py"
FLOW = SCRIPTS / "loom_flow.py"
ADMISSION = SCRIPTS / "github_admission.py"
GITHUB_HOST = SCRIPTS / "github_host.py"
CLI = ROOT / "tools" / "loom.py"
DOCUMENT = ROOT / "docs" / "methodology" / "governance" / "field-authority-verdict-contract.md"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def blocked_admission() -> dict[str, Any]:
    return {
        "result": "block",
        "admission_state": "needs_breakdown",
        "subject": {"type": "fr", "locator": "fr:100"},
        "next_action": "loom route --target <repo> --issue 100 --task 'Narrow child' --intent build --apply --json",
        "missing_inputs": ["native Work Item breakdown"],
    }


def check_authority_contract() -> None:
    authority = load_module("authority_contract", AUTHORITY)
    expected = {"work_item_scope", "delivery_state", "product_acceptance", "reconciliation_state", "pr_head_checks_merge", "workstation_session", "historical_audit"}
    if set(authority.FIELD_AUTHORITIES) != expected:
        raise AssertionError("field authority map drifted")
    independent = authority.authority_verdict(
        delivery_state="merged",
        product_acceptance="pending",
        reconciliation_state="drifted",
    )
    if independent["result"] != "pass" or independent["verdict"] != {"delivery_state": "merged", "product_acceptance": "pending", "reconciliation_state": "drifted"}:
        raise AssertionError("verdict fields must remain independently consumable")
    invalid = authority.authority_verdict(delivery_state="green")
    if invalid["result"] != "block" or invalid["primary_remediation"] != "supply valid independent authority verdict values":
        raise AssertionError("invalid verdict values must have one remediation")
    locator = authority.typed_locator("owner", "repo", "work_item", 42)
    parsed = authority.parse_typed_locator(locator, allow_legacy=False)
    if not parsed or (parsed["owner"], parsed["repo"], parsed["type"], parsed["id"], parsed["legacy"]) != ("owner", "repo", "work_item", 42, False):
        raise AssertionError("canonical Work Item locator did not parse")
    legacy = authority.parse_typed_locator("work_item:42")
    if not legacy or legacy["legacy"] is not True or legacy["compatibility"]["removed_in"] != "v0.31.0":
        raise AssertionError("legacy typed locator compatibility is not explicit")
    if authority.parse_typed_locator("work_item:42", allow_legacy=False) is not None:
        raise AssertionError("authoritative consumers must be able to reject legacy locators")
    if any(authority.parse_typed_locator(value) is not None for value in ("42", "fr:0", "acceptance:42", "unknown:42", "FR:42", "owner/repo/fr/0")):
        raise AssertionError("ambiguous or invalid typed locator was accepted")
    planning = authority.lifecycle_admission_verdict({"result": "pass", "admission_state": "planning", "subject": {"type": "fr", "locator": "fr:100"}})
    work_item = authority.lifecycle_admission_verdict({"result": "pass", "admission_state": "admitted", "subject": {"type": "work_item", "locator": "work_item:101"}})
    blocked = authority.lifecycle_admission_verdict(blocked_admission())
    deferred = authority.lifecycle_admission_verdict({"result": "pass", "intent": "build", "admission_state": "not_planned", "subject": {"type": "fr", "locator": "fr:100"}})
    unrelated = authority.lifecycle_admission_verdict({"result": "block", "admission_state": "unsupported_subject", "subject": {"type": "unknown", "locator": None}})
    if planning["result"] != "pass" or work_item["lifecycle_state"] != "not_applicable":
        raise AssertionError("planning FR and existing Work Item lifecycle results drifted")
    if blocked["result"] != "block" or blocked["primary_remediation"] != blocked_admission()["next_action"] or blocked["carrier_mutations"] is not False:
        raise AssertionError("blocked lifecycle verdict must retain one host-native remediation")
    if deferred["result"] != "block" or unrelated["result"] != "block":
        raise AssertionError("deferred execution and unrelated issue lifecycle handling drifted")


def check_host_subject_readback() -> None:
    host = load_module("authority_contract_github_host", GITHUB_HOST)
    original_rest_list = host.gh_rest_authenticated_list
    original_graphql = host.gh_graphql_authenticated_json
    try:
        explicit = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", issue_number="owner/repo/work_item/41")
        if explicit.get("issue_locator") != "owner/repo/issue/41" or explicit.get("source") != "explicit_issue":
            raise AssertionError("explicit lifecycle subject did not use the canonical locator")
        foreign = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", issue_number="other/repo/work_item/41")
        if foreign.get("result") != "block" or "foreign canonical locator" not in " ".join(foreign.get("errors", [])):
            raise AssertionError("foreign canonical lifecycle subject did not fail closed")
        target_mismatch = host.github_lifecycle_subject_readback(Path("."), "other", "repo", issue_number=41, target_owner="owner", target_repo="repo")
        if target_mismatch.get("result") != "block" or "does not match target origin" not in " ".join(target_mismatch.get("errors", [])):
            raise AssertionError("foreign explicit repository did not fail closed")
        explicit_conflict = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", issue_number=41, fr_number=42)
        if explicit_conflict.get("result") != "block" or "disagree" not in " ".join(explicit_conflict.get("errors", [])):
            raise AssertionError("conflicting --issue and --fr did not fail closed")

        pr_state = "OPEN"
        pr_head = "work/42"
        closing_numbers = [42]
        closing_has_next = False

        def graphql(_root: Path, _query: str, variables: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
            return ({"repository": {"pullRequest": {"number": variables["pr"], "state": pr_state, "headRefName": pr_head, "closingIssuesReferences": {"pageInfo": {"hasNextPage": closing_has_next}, "nodes": [{"number": number} for number in closing_numbers]}}}}, [])

        host.gh_graphql_authenticated_json = graphql
        pr = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", pr_number=7)
        if pr.get("issue_locator") != "owner/repo/issue/42" or pr.get("pr_locator") != "owner/repo/pr/7":
            raise AssertionError("PR context did not resolve its native closing issue")
        issue_pr_conflict = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", issue_number=41, pr_number=7)
        if issue_pr_conflict.get("result") != "block" or "closing issue #42 disagree" not in " ".join(issue_pr_conflict.get("errors", [])):
            raise AssertionError("explicit issue and PR closing issue conflict did not fail closed")

        host.gh_rest_authenticated_list = lambda _root, _path: ([{"number": 7, "state": "open"}], [])
        branch = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", branch_name="work/42")
        if branch.get("issue_number") != 42 or "branch_pr" not in branch.get("source", ""):
            raise AssertionError("branch context did not resolve through its unique PR")
        pr_head = "work/other"
        branch_pr_conflict = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", pr_number=8, branch_name="work/42")
        if branch_pr_conflict.get("result") != "block" or "head does not match branch" not in " ".join(branch_pr_conflict.get("errors", [])):
            raise AssertionError("explicit PR and branch identity conflict did not fail closed")
        pr_head = "work/42"

        host.gh_rest_authenticated_list = lambda _root, _path: ([{"number": 7, "state": "open"}, {"number": 8, "state": "open"}], [])
        ambiguous = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", branch_name="work/42")
        if ambiguous.get("result") != "block" or "2 eligible" not in " ".join(ambiguous.get("errors", [])):
            raise AssertionError("ambiguous branch PR context did not fail closed")

        host.gh_rest_authenticated_list = lambda _root, _path: ([], ["authenticated pagination incomplete"])
        unreadable = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", branch_name="work/42")
        if unreadable.get("result") != "block" or unreadable.get("errors") != ["authenticated pagination incomplete"]:
            raise AssertionError("unreadable or incomplete branch pagination did not fail closed")

        closing_numbers = [42, 43]
        multiple_closing = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", pr_number=7)
        if multiple_closing.get("result") != "block" or "exactly one primary Work Item" not in " ".join(multiple_closing.get("errors", [])):
            raise AssertionError("multiple native closing issues did not fail closed")
        closing_numbers = [42]
        closing_has_next = True
        truncated = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", pr_number=7)
        if truncated.get("result") != "block" or "pagination is unreadable or incomplete" not in " ".join(truncated.get("errors", [])):
            raise AssertionError("truncated closing issue readback did not fail closed")
        closing_has_next = False
        pr_state = "CLOSED"
        closed_execution = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", pr_number=7, intent="ship")
        if closed_execution.get("result") != "block" or "requires an open PR" not in " ".join(closed_execution.get("errors", [])):
            raise AssertionError("execution reused a closed PR")
        closed_closeout = host.github_lifecycle_subject_readback(Path("."), "owner", "repo", pr_number=7, intent="closeout")
        if closed_closeout.get("result") != "pass":
            raise AssertionError("closeout could not consume a closed PR")
    finally:
        host.gh_rest_authenticated_list = original_rest_list
        host.gh_graphql_authenticated_json = original_graphql


def check_authenticated_branch_pagination() -> None:
    host = load_module("authority_contract_github_host_pagination", GITHUB_HOST)
    calls: list[list[str]] = []
    host.host_api_env_token_present = lambda: True

    def run_process(command: list[str], _root: Path, *, timeout_seconds: int) -> SimpleNamespace:
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout='[[{"number": 7}], [{"number": 8}]]', stderr="")

    host.run_process = run_process
    rows, errors = host.gh_rest_authenticated_list(Path("."), "repos/owner/repo/pulls?state=all")
    if errors or [row.get("number") for row in rows] != [7, 8]:
        raise AssertionError("authenticated branch discovery did not flatten every REST page")
    if calls != [["gh", "api", "--paginate", "--slurp", "repos/owner/repo/pulls?state=all"]]:
        raise AssertionError(f"authenticated branch discovery omitted pagination: {calls}")
    host.run_process = lambda *_args, **_kwargs: SimpleNamespace(returncode=0, stdout='[{"number": 7}]', stderr="")
    rows, errors = host.gh_rest_authenticated_list(Path("."), "repos/owner/repo/pulls?state=all")
    if rows or not errors or "paginated JSON list" not in errors[0]:
        raise AssertionError("incomplete authenticated pagination did not fail closed")


def check_shared_admission_verdict() -> None:
    admission = load_module("authority_contract_admission", ADMISSION)
    issue_type = "fr"
    issue_state = "OPEN"
    children: list[dict[str, Any]] = []

    def github_issue(_root: Path, _owner: str, _repo: str, number: int) -> tuple[dict[str, Any], list[str]]:
        return {"number": number, "state": issue_state, "title": "Narrow child", "labels": [issue_type]}, []

    host = SimpleNamespace(
        detect_github_repo=lambda _root: ("owner", "repo"),
        github_issue_payload=github_issue,
        build_governance_surface=lambda _root: {"repo_interface": None},
        github_intake_object_type=lambda issue, repo_interface: ("work_item" if "work_item" in {str(label).lower() for label in issue.get("labels", [])} else issue_type, "fixture"),
        normalize_taxonomy_match_text=lambda value: str(value or "").lower(),
        normalized_issue_labels=lambda issue: {str(label).lower() for label in issue.get("labels", [])},
        github_intake_taxonomy_mapping=lambda _interface: ([], "missing", "fixture"),
        issue_tree_payload=lambda _root, _owner, _repo, _number: ({"subIssues": {"pageInfo": {"hasNextPage": False}, "nodes": children}}, []),
        gh_graphql_json=lambda _root, _query, _variables: ({"search": {"pageInfo": {"hasNextPage": False}, "nodes": []}}, []),
    )
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory)
        planning = admission.github_fr_wi_admission_payload(
            host=host,
            target_root=target,
            owner="owner",
            repo_name="repo",
            issue_number=100,
            intent="planning",
            task="Narrow child",
            blocked_by=[],
            work_item_number=None,
            apply=False,
        )
        executing = admission.github_fr_wi_admission_payload(
            host=host,
            target_root=target,
            owner="owner",
            repo_name="repo",
            issue_number=100,
            intent="build",
            task="Narrow child",
            blocked_by=[],
            work_item_number=None,
            apply=False,
        )
        children.append({"number": 102, "labels": ["work_item"]})
        lifecycle = admission.github_fr_wi_admission_payload(
            host=host,
            target_root=target,
            owner="owner",
            repo_name="repo",
            issue_number=100,
            intent="build",
            task=None,
            blocked_by=[],
            work_item_number=None,
            apply=False,
            lifecycle_only=True,
        )
        children.clear()
        issue_type = "work_item"
        work_item = admission.github_fr_wi_admission_payload(
            host=host,
            target_root=target,
            owner="owner",
            repo_name="repo",
            issue_number=101,
            intent="ship",
            task=None,
            blocked_by=[],
            work_item_number=None,
            apply=False,
        )
        issue_type = "phase"
        phase = admission.github_fr_wi_admission_payload(
            host=host,
            target_root=target,
            owner="owner",
            repo_name="repo",
            issue_number=99,
            intent="build",
            task=None,
            blocked_by=[],
            work_item_number=None,
            apply=False,
            lifecycle_only=True,
        )
        issue_type = "fr"
        fr_without_breakdown = admission.github_fr_wi_admission_payload(
            host=host, target_root=target, owner="owner", repo_name="repo", issue_number=100,
            intent="closeout", task=None, blocked_by=[], work_item_number=None, apply=False, lifecycle_only=True,
        )
        children.append({"number": 102, "labels": ["work_item"]})
        fr_closeout = admission.github_fr_wi_admission_payload(
            host=host, target_root=target, owner="owner", repo_name="repo", issue_number=100,
            intent="closeout", task=None, blocked_by=[], work_item_number=None, apply=False, lifecycle_only=True,
        )
        children.clear()
        issue_type = "phase"
        phase_without_breakdown = admission.github_fr_wi_admission_payload(
            host=host, target_root=target, owner="owner", repo_name="repo", issue_number=99,
            intent="closeout", task=None, blocked_by=[], work_item_number=None, apply=False, lifecycle_only=True,
        )
        children.append({"number": 98, "labels": ["problem"]})
        phase_closeout = admission.github_fr_wi_admission_payload(
            host=host, target_root=target, owner="owner", repo_name="repo", issue_number=99,
            intent="closeout", task=None, blocked_by=[], work_item_number=None, apply=False, lifecycle_only=True,
        )
        issue_type = "work_item"
        issue_state = "CLOSED"
        closed_work_item = admission.github_fr_wi_admission_payload(
            host=host, target_root=target, owner="owner", repo_name="repo", issue_number=101,
            intent="ship", task=None, blocked_by=[], work_item_number=None, apply=False, lifecycle_only=True,
        )
        if planning.get("lifecycle_verdict", {}).get("lifecycle_state") != "planning":
            raise AssertionError("route planning verdict was not attached to native admission")
        if executing.get("lifecycle_verdict", {}).get("lifecycle_state") != "needs_breakdown":
            raise AssertionError("executing FR did not use the shared native admission verdict")
        if lifecycle.get("admission_state") != "work_item_required" or lifecycle.get("evidence", {}).get("native_work_item_locators") != ["owner/repo/work_item/102"]:
            raise AssertionError("lifecycle admission did not require binding the existing native Work Item child")
        if work_item.get("lifecycle_verdict", {}).get("lifecycle_state") != "not_applicable":
            raise AssertionError("existing Work Item did not avoid an additional lifecycle gate")
        if phase.get("lifecycle_verdict", {}).get("lifecycle_state") != "needs_breakdown" or phase.get("subject", {}).get("locator") != "owner/repo/phase/99":
            raise AssertionError("Phase execution did not fail closed with a canonical subject")
        for label, closeout in (("FR", fr_closeout), ("Phase", phase_closeout)):
            if closeout.get("lifecycle_verdict", {}).get("lifecycle_state") != "closure_evaluation_required" or closeout.get("lifecycle_verdict", {}).get("result") != "pass":
                raise AssertionError(f"{label} closeout did not pass through to the closure evaluator")
        for label, closeout in (("FR", fr_without_breakdown), ("Phase", phase_without_breakdown)):
            if closeout.get("lifecycle_verdict", {}).get("lifecycle_state") != "needs_breakdown" or closeout.get("lifecycle_verdict", {}).get("result") != "block":
                raise AssertionError(f"unbroken {label} closeout did not fail closed before the closure evaluator")
        if closed_work_item.get("lifecycle_verdict", {}).get("lifecycle_state") != "host_state_invalid":
            raise AssertionError("execution accepted a closed Work Item")
        if any(target.iterdir()):
            raise AssertionError("native admission contract fixture must not write repository carriers")


def check_entrypoints() -> None:
    sys.path.insert(0, str(SCRIPTS))
    flow = load_module("authority_contract_flow", FLOW)
    execution_flow = sys.modules[flow.handle_flow.__module__]
    closeout_flow = sys.modules[flow.handle_closeout.__module__]
    cli = load_module("authority_contract_cli", CLI)
    original_execution_admission = execution_flow.lifecycle_admission_payload
    original_execution_emit = execution_flow.emit
    original_closeout_admission = closeout_flow.lifecycle_admission_payload
    original_closeout_emit = closeout_flow.emit
    original_cli_admission = cli.host_lifecycle_admission_payload
    original_cli_emit = cli.emit
    original_cli_safe = cli.agent_safe_payload
    captured: list[dict[str, Any]] = []
    flow_subjects: list[int | None] = []
    cli_subjects: list[int | None] = []
    try:
        def capture_flow_admission(**kwargs: Any) -> dict[str, Any]:
            flow_subjects.append(kwargs.get("issue_number"))
            return {
                **blocked_admission(),
                "lifecycle_state": "needs_breakdown",
                "primary_remediation": blocked_admission()["next_action"],
            }

        execution_flow.lifecycle_admission_payload = capture_flow_admission
        execution_flow.emit = lambda payload: captured.append(payload) or 0
        closeout_flow.lifecycle_admission_payload = capture_flow_admission
        closeout_flow.emit = lambda payload: captured.append(payload) or 0
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for operation in ("build", "pre-review"):
                status = flow.handle_flow(
                    SimpleNamespace(
                        target=str(target), operation=operation, owner=None, repo_name=None, issue=100, fr=None, pr=None, branch=None
                    )
                )
                if status != 0 or captured[-1].get("lifecycle_admission", {}).get("lifecycle_state") != "needs_breakdown":
                    raise AssertionError(f"flow {operation} did not stop at host-native lifecycle admission")
            status = flow.handle_closeout(
                SimpleNamespace(target=str(target), operation="check", owner=None, repo_name=None, fr=None, issue=100, pr=None, branch=None)
            )
            if status != 0 or captured[-1].get("command") != "closeout":
                raise AssertionError("closeout did not stop at host-native lifecycle admission")

            def capture_cli_admission(**kwargs: Any) -> dict[str, Any]:
                cli_subjects.append(kwargs.get("issue"))
                return {
                    **blocked_admission(),
                    "lifecycle_state": "needs_breakdown",
                    "primary_remediation": blocked_admission()["next_action"],
                }

            cli.host_lifecycle_admission_payload = capture_cli_admission
            cli.emit = lambda payload: captured.append(payload) or 0
            cli.agent_safe_payload = lambda payload, **_kwargs: payload
            status = cli.handle_ship(["--target", str(target), "--item", "owner/repo/work_item/100", "--issue", "100", "--pr", "101"])
            if status != 0 or captured[-1].get("command") != "ship":
                raise AssertionError("ship did not stop at host-native lifecycle admission")
            if hasattr(cli, "handle_ship_status"):
                raise AssertionError("removed ship status/preflight compatibility handler must not be restored")
            if any(target.iterdir()):
                raise AssertionError("lifecycle admission fixture must not write repository carriers")
            if flow_subjects != [100, 100, 100]:
                raise AssertionError(f"flow entrypoints did not infer lifecycle subject from --issue: {flow_subjects}")
            if cli_subjects != [100]:
                raise AssertionError(f"ship entrypoints did not infer lifecycle subject from --issue: {cli_subjects}")

    finally:
        execution_flow.lifecycle_admission_payload = original_execution_admission
        execution_flow.emit = original_execution_emit
        closeout_flow.lifecycle_admission_payload = original_closeout_admission
        closeout_flow.emit = original_closeout_emit
        cli.host_lifecycle_admission_payload = original_cli_admission
        cli.emit = original_cli_emit
        cli.agent_safe_payload = original_cli_safe


def check_entrypoint_authority_forwarding() -> None:
    sys.path.insert(0, str(SCRIPTS))
    flow = load_module("authority_contract_flow_forwarding", FLOW)
    execution_flow = sys.modules[flow.lifecycle_admission_payload.__module__]
    cli = load_module("authority_contract_cli_forwarding", CLI)
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory)
        flow_calls: list[dict[str, Any]] = []
        execution_flow.detect_github_repo = lambda _target: ("owner", "repo")
        execution_flow.github_lifecycle_subject_readback = lambda _target, _owner, _repo, **kwargs: flow_calls.append(kwargs) or {
            "result": "pass", "issue_number": 41, "errors": [],
        }
        execution_flow.github_fr_wi_admission_payload = lambda **_kwargs: {
            "lifecycle_verdict": {"result": "pass", "lifecycle_state": "not_applicable", "carrier_mutations": False},
        }
        flow_result = execution_flow.lifecycle_admission_payload(
            target_root=target,
            owner="owner",
            repo_name="repo",
            issue_number=41,
            fr_number=41,
            pr_number=7,
            branch_name="work/41",
            intent="build",
        )
        if flow_result.get("result") != "pass" or flow_calls != [{
            "issue_number": 41,
            "fr_number": 41,
            "pr_number": 7,
            "branch_name": "work/41",
            "intent": "build",
            "target_owner": "owner",
            "target_repo": "repo",
        }]:
            raise AssertionError(f"flow entrypoint did not reconcile every supplied authority: {flow_calls}")
        execution_flow.detect_github_repo = lambda _target: (None, None)
        unbound_flow = execution_flow.lifecycle_admission_payload(
            target_root=target, owner="owner", repo_name="repo", issue_number=41, intent="build",
        )
        if unbound_flow.get("result") != "block" or "target origin GitHub owner/repo" not in unbound_flow.get("missing_inputs", []):
            raise AssertionError("flow accepted an explicit repository without a target origin binding")

        cli_calls: list[dict[str, Any]] = []
        cli.infer_github_repo = lambda _target: "owner/repo"
        cli.github_lifecycle_subject_readback = lambda _target, _owner, _repo, **kwargs: cli_calls.append(kwargs) or {
            "result": "pass", "issue_number": 41, "errors": [],
        }
        cli.github_fr_wi_admission_payload = lambda **_kwargs: {
            "lifecycle_verdict": {"result": "pass", "lifecycle_state": "not_applicable", "carrier_mutations": False},
        }
        cli_result = cli.host_lifecycle_admission_payload(
            target=target,
            issue=41,
            fr=41,
            owner="owner",
            repo_name="repo",
            intent="ship",
            pr=7,
            branch="work/41",
        )
        if cli_result.get("result") != "pass" or cli_calls != [{
            "issue_number": 41,
            "fr_number": 41,
            "pr_number": 7,
            "branch_name": "work/41",
            "intent": "ship",
            "target_owner": "owner",
            "target_repo": "repo",
        }]:
            raise AssertionError(f"outer CLI did not reconcile every supplied authority: {cli_calls}")
        cli.infer_github_repo = lambda _target: None
        unbound_cli = cli.host_lifecycle_admission_payload(
            target=target, issue=41, owner="owner", repo_name="repo", intent="ship",
        )
        if unbound_cli.get("result") != "block" or "target origin GitHub owner/repo" not in unbound_cli.get("missing_inputs", []):
            raise AssertionError("outer CLI accepted an explicit repository without a target origin binding")


def check_document() -> None:
    text = DOCUMENT.read_text(encoding="utf-8")
    for needle in (
        "delivery_state",
        "product_acceptance",
        "reconciliation_state",
        "Typed locators",
        "owner/repo/type/id",
        "v0.31.0",
        "never changes `product_acceptance`",
        "loom route --issue <FR>",
        "--fr <FR>",
        "--issue <work-item-or-fr>",
        "missing_subject",
    ):
        if needle not in text:
            raise AssertionError(f"authority contract document missing {needle}")


def main() -> int:
    check_authority_contract()
    check_host_subject_readback()
    check_authenticated_branch_pagination()
    check_shared_admission_verdict()
    check_entrypoints()
    check_entrypoint_authority_forwarding()
    check_document()
    print("authority contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
