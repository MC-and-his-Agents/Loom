"""Validated Make-target contract for untrusted candidate checks."""

from __future__ import annotations

import re


ALLOWED_MAKE_TARGETS = (
    "py-compile",
    "skills-doc-reference-sync-check",
    "skills-check",
    "host-adapter-check",
    "pr-binding-workflow-check",
    "fr-phase-close-guard-check",
    "host-attestation-check",
    "authority-contract-check",
    "fr-wi-admission-check",
    "pr-metadata-check",
    "product-acceptance-adapter-check",
    "failure-envelope-check",
    "light-profile-check",
    "loom-check-runtime-regression",
    "loom-demo-new-project-check",
    "cli-contract-check",
    "release-surface-check",
    "npm-package-check",
    "delivery-gate-check",
    "composite-action-contract-check",
    "workflow-contract-check",
    "check",
    "test",
    "lint",
    "typecheck",
)
TARGETS_RE = re.compile(r"[a-z0-9][a-z0-9-]*(?: [a-z0-9][a-z0-9-]*)*")


def parse_make_targets(value: object) -> tuple[list[str], list[str]]:
    """Accept only a space-delimited allowlist; never a shell command."""

    if not isinstance(value, str) or not value or value.strip() != value or not TARGETS_RE.fullmatch(value):
        return [], ["validation_command must be a single-line space-delimited Make target list"]
    targets = list(dict.fromkeys(value.split(" ")))
    unsupported = [target for target in targets if target not in ALLOWED_MAKE_TARGETS]
    if unsupported:
        return [], ["validation_command contains unsupported Make targets: " + ", ".join(unsupported)]
    if targets == ["delivery-gate-check"]:
        return [], ["validation_command cannot contain only the delivery-gate evaluator self-test"]
    return targets, []
