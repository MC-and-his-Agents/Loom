.PHONY: loom-check check py-compile skills-check skills-doc-reference-sync-check skills-generated-tree-drift-check skills-package-metadata-check skills-cache-artifacts-check skills-launcher-smoke-check host-adapter-check pr-binding-workflow-check fr-phase-close-guard-check host-attestation-check distinct-app-gate-workflow-check authority-contract-check fr-wi-admission-check product-acceptance-adapter-check failure-envelope-check light-profile-check delivery-gate-check composite-action-contract-check workflow-contract-check version-surface-check release-surface-check release-surface-doc-contract-check release-surface-workflow-contract-check release-surface-installer-sunset-guard-check release-surface-forbidden-patterns-check release-surface-installed-global-cli-smoke-check cli-contract-check npm-package-check npm-package-manifest-check npm-pack-payload-check loom-check-runtime-regression loom-check-runtime-locking loom-check-runtime-single-flight-locking loom-check-runtime-worktree-local-lock-paths loom-check-runtime-subprocess-env-purity loom-check-runtime-demo-fixture-cleanliness loom-check-runtime-temp-dir-cleanup loom-demo-new-project loom-demo-new-project-check loom-demo-new-project-generation-check loom-demo-new-project-canonicalization-check loom-demo-new-project-fixture-drift-check loom-demo-new-project-cleanliness-check loom-demo-new-project-sync loom-self-plugin-check daily-execution-cli-fast daily-execution-cli-full
loom-check: pr-binding-workflow-check fr-phase-close-guard-check authority-contract-check host-attestation-check distinct-app-gate-workflow-check product-acceptance-adapter-check failure-envelope-check light-profile-check delivery-gate-check composite-action-contract-check
loom-check: export PYTHONDONTWRITEBYTECODE=1

py-compile:
	python3 tools/py_compile_clean.py tools/loom.py tools/runtime_wrapper.py tools/loom_init.py tools/light_profile.py tools/loom_flow.py tools/loom_check.py tools/loom_status.py tools/build_distribution.py tools/py_compile_clean.py tools/check_cli_contract.py tools/check_authority_contract.py tools/check_product_acceptance_adapter.py tools/check_release_admission.py tools/release_admission.py tools/check_light_profile.py tools/check_npm_package.py tools/check_release_surface.py tools/check_pr_binding_workflow.py tools/check_fr_phase_close_guard.py tools/check_fr_phase_close_guard_workflow.py tools/check_distinct_app_gate_workflow.py tools/check_demo_bootstrap_fixture.py tools/check_loom_check_runtime_regressions.py tools/check_composite_actions.py tools/run_trusted_candidate_validation.py tools/read_delivery_gate_required_identity.py src/skills/shared/scripts/*.py src/skills/loom-init/scripts/*.py src/skills/loom-adopt/scripts/*.py src/skills/loom-resume/scripts/*.py src/skills/loom-pre-review/scripts/*.py src/skills/loom-review/scripts/*.py src/skills/loom-spec-review/scripts/*.py src/skills/loom-handoff/scripts/*.py src/skills/loom-build/scripts/*.py src/skills/loom-story/scripts/*.py

skills-check:
	python3 tools/skills_surface.py check

skills-doc-reference-sync-check:
	python3 tools/skills_surface.py check --surface docs-reference-sync

skills-generated-tree-drift-check:
	python3 tools/skills_surface.py check --surface generated-tree-drift

skills-package-metadata-check:
	python3 tools/skills_surface.py check --surface plugin-payload-metadata

skills-cache-artifacts-check:
	python3 tools/skills_surface.py check --surface cache-artifacts

skills-launcher-smoke-check:
	python3 tools/skills_surface.py check --surface launcher-smoke $(if $(SKILL),--skill $(SKILL),)

host-adapter-check:
	python3 tools/host_adapter_check.py

pr-binding-workflow-check:
	python3 tools/check_pr_binding_workflow.py

fr-phase-close-guard-check:
	python3 tools/check_fr_phase_close_guard.py
	python3 tools/check_fr_phase_close_guard_workflow.py

host-attestation-check:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/check_host_attestation.py

distinct-app-gate-workflow-check:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/check_distinct_app_gate_workflow.py

fr-wi-admission-check:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface fr-wi-admission

failure-envelope-check:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/check_cli_contract.py --surface failure-envelope

delivery-gate-check:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/check_delivery_gate.py

composite-action-contract-check:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/check_composite_actions.py

workflow-contract-check: pr-binding-workflow-check fr-phase-close-guard-check host-attestation-check release-surface-workflow-contract-check delivery-gate-check composite-action-contract-check

authority-contract-check:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/check_authority_contract.py

product-acceptance-adapter-check:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/check_product_acceptance_adapter.py

light-profile-check:
	PYTHONDONTWRITEBYTECODE=1 python3 tools/check_light_profile.py

version-surface-check:
	python3 tools/version_surface_check.py

release-surface-check:
	python3 tools/check_release_surface.py

release-surface-doc-contract-check:
	python3 tools/check_release_surface.py --surface release-doc-contract

release-surface-workflow-contract-check:
	python3 tools/check_release_surface.py --surface release-workflow-contract

release-surface-installer-sunset-guard-check:
	python3 tools/check_release_surface.py --surface installer-sunset-guard

release-surface-forbidden-patterns-check:
	python3 tools/check_release_surface.py --surface forbidden-release-surface-patterns

release-surface-installed-global-cli-smoke-check:
	python3 tools/check_release_surface.py --surface installed-global-cli-smoke

cli-contract-check:
	python3 tools/check_cli_contract.py

npm-package-check:
	python3 tools/check_npm_package.py
	npm run test:package

npm-package-manifest-check:
	python3 tools/check_npm_package.py --surface npm-package-manifest

npm-pack-payload-check:
	python3 tools/check_npm_package.py --surface npm-pack-payload

loom-check-runtime-regression:
	python3 tools/check_loom_check_runtime_regressions.py

loom-check-runtime-locking:
	python3 tools/check_loom_check_runtime_regressions.py --fixture-group locking

loom-check-runtime-single-flight-locking:
	python3 tools/check_loom_check_runtime_regressions.py --surface single-flight-locking

loom-check-runtime-worktree-local-lock-paths:
	python3 tools/check_loom_check_runtime_regressions.py --surface worktree-local-lock-paths

loom-check-runtime-subprocess-env-purity:
	python3 tools/check_loom_check_runtime_regressions.py --surface subprocess-env-purity

loom-check-runtime-demo-fixture-cleanliness:
	python3 tools/check_loom_check_runtime_regressions.py --surface demo-fixture-cleanliness

loom-check-runtime-temp-dir-cleanup:
	python3 tools/check_loom_check_runtime_regressions.py --surface temp-dir-cleanup

daily-execution-cli-fast:
	python3 tools/check_cli_contract.py --surface public-default-path

daily-execution-cli-full:
	python3 tools/check_cli_contract.py --surface aggregate

check: py-compile skills-check host-adapter-check version-surface-check release-surface-check cli-contract-check authority-contract-check product-acceptance-adapter-check light-profile-check npm-package-check loom-check

loom-demo-new-project:
	python3 tools/check_demo_bootstrap_fixture.py

loom-demo-new-project-check:
	python3 tools/check_demo_bootstrap_fixture.py

loom-demo-new-project-generation-check:
	python3 tools/check_demo_bootstrap_fixture.py --surface generation

loom-demo-new-project-canonicalization-check:
	python3 tools/check_demo_bootstrap_fixture.py --surface canonicalization

loom-demo-new-project-fixture-drift-check:
	python3 tools/check_demo_bootstrap_fixture.py --surface fixture-drift

loom-demo-new-project-cleanliness-check:
	python3 tools/check_demo_bootstrap_fixture.py --surface cleanliness

loom-demo-new-project-sync:
	python3 tools/loom_init.py bootstrap --target examples/new-project --scenario new --intent execution-control --intake examples/new-project/.loom/bootstrap/intake.snapshot.json --write --force --verify --install-pr-template --portable-output

loom-self-plugin-check:
	test -f plugins/loom/.codex-plugin/plugin.json
	test -f plugins/loom/skills/registry.json
	test -f plugins/loom/skills/loom-init/SKILL.md
	test -f src/skills/registry.json
	test -f skills/registry.json
	test -f skills/loom-init/SKILL.md
	test -f .agents/plugins/marketplace.json
	python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
