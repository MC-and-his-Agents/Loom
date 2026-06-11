.PHONY: loom-check check py-compile skills-check skills-doc-reference-sync-check skills-generated-tree-drift-check skills-package-metadata-check skills-cache-artifacts-check skills-launcher-smoke-check host-adapter-check version-surface-check release-surface-check release-surface-doc-contract-check release-surface-workflow-contract-check release-surface-installer-sunset-guard-check release-surface-forbidden-patterns-check release-surface-installed-global-cli-smoke-check cli-contract-check npm-package-check npm-package-manifest-check npm-pack-payload-check loom-check-runtime-regression loom-check-runtime-locking loom-check-runtime-single-flight-locking loom-check-runtime-worktree-local-lock-paths loom-check-runtime-subprocess-env-purity loom-check-runtime-installer-regression-lock-output loom-demo-new-project loom-demo-new-project-check loom-demo-new-project-generation-check loom-demo-new-project-canonicalization-check loom-demo-new-project-fixture-drift-check loom-demo-new-project-cleanliness-check loom-demo-new-project-sync loom-self-plugin-check daily-execution-cli-fast daily-execution-cli-full
.PHONY: repo-local-cli-fast repo-local-cli-full repo-local-cli-setup-demo-bootstrap repo-local-cli-init-runtime repo-local-cli-fact-chain repo-local-cli-flow-gates repo-local-cli-workspace-locate repo-local-cli-purity-check repo-local-cli-runtime-state-scene-conflict-negative

REPO_LOCAL_CLI_GROUPS := setup-demo-bootstrap init-runtime fact-chain flow-gates workspace-locate purity-check runtime-state-scene-conflict-negative

loom-check: loom-self-plugin-check loom-demo-new-project-check loom-check-runtime-regression
	python3 tools/loom_check.py

py-compile:
	python3 tools/py_compile_clean.py tools/loom.py tools/loom_init.py tools/loom_flow.py tools/loom_check.py tools/loom_status.py tools/py_compile_clean.py tools/check_cli_contract.py tools/check_npm_package.py tools/check_release_surface.py tools/check_demo_bootstrap_fixture.py tools/check_loom_check_runtime_regressions.py skills/shared/scripts/*.py src/skills/shared/scripts/*.py skills/loom-init/scripts/*.py skills/loom-adopt/scripts/*.py skills/loom-resume/scripts/*.py skills/loom-pre-review/scripts/*.py skills/loom-review/scripts/*.py skills/loom-spec-review/scripts/*.py skills/loom-handoff/scripts/*.py skills/loom-retire/scripts/*.py skills/loom-merge-ready/scripts/*.py skills/loom-build/scripts/*.py skills/loom-story/scripts/*.py

skills-check:
	python3 tools/skills_surface.py check

skills-doc-reference-sync-check:
	python3 tools/skills_surface.py check --surface docs-reference-sync

skills-generated-tree-drift-check:
	python3 tools/skills_surface.py check --surface generated-tree-drift

skills-package-metadata-check:
	python3 tools/skills_surface.py check --surface package-metadata

skills-cache-artifacts-check:
	python3 tools/skills_surface.py check --surface cache-artifacts

skills-launcher-smoke-check:
	python3 tools/skills_surface.py check --surface launcher-smoke $(if $(SKILL),--skill $(SKILL),)

host-adapter-check:
	python3 tools/host_adapter_check.py

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

loom-check-runtime-installer-regression-lock-output:
	python3 tools/check_loom_check_runtime_regressions.py --surface installer-regression-lock-output

daily-execution-cli-fast:
	python3 tools/loom_check.py --profile source --source-surface daily-execution-cli-fast .

daily-execution-cli-full:
	python3 tools/loom_check.py --profile source --source-surface daily-execution-cli-full .

check: py-compile skills-check host-adapter-check version-surface-check release-surface-check cli-contract-check npm-package-check loom-check

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
	test -f src/skills/registry.json
	test -f skills/registry.json
	test -f skills/loom-init/SKILL.md
	test -f skills/loom-init/loom-package.json
	test ! -f .agents/plugins/marketplace.json

repo-local-cli-fast:
	@test -n "$(GROUP)" || { echo "usage: make repo-local-cli-fast GROUP=<group>"; echo "groups: $(REPO_LOCAL_CLI_GROUPS)"; exit 2; }
	@case " $(REPO_LOCAL_CLI_GROUPS) " in *" $(GROUP) "*) ;; *) echo "unknown repo-local-cli group: $(GROUP)"; echo "groups: $(REPO_LOCAL_CLI_GROUPS)"; exit 2;; esac
	$(MAKE) --no-print-directory repo-local-cli-$(GROUP)

repo-local-cli-full:
	$(MAKE) --no-print-directory repo-local-cli-setup-demo-bootstrap
	$(MAKE) --no-print-directory repo-local-cli-init-runtime
	$(MAKE) --no-print-directory repo-local-cli-fact-chain
	$(MAKE) --no-print-directory repo-local-cli-flow-gates
	$(MAKE) --no-print-directory repo-local-cli-workspace-locate
	$(MAKE) --no-print-directory repo-local-cli-purity-check
	$(MAKE) --no-print-directory repo-local-cli-runtime-state-scene-conflict-negative

repo-local-cli-setup-demo-bootstrap:
	$(MAKE) --no-print-directory loom-demo-new-project-check

repo-local-cli-init-runtime:
	cd examples/new-project && python3 .loom/bin/loom_init.py runtime-state --target .
	cd examples/new-project && python3 .loom/bin/loom_init.py verify --target .

repo-local-cli-fact-chain:
	cd examples/new-project && python3 .loom/bin/loom_init.py fact-chain --target .
	cd examples/new-project && python3 .loom/bin/loom_flow.py runtime-state --target . --item INIT-0001
	cd examples/new-project && python3 .loom/bin/loom_flow.py fact-chain --target . --item INIT-0001
	cd examples/new-project && python3 .loom/bin/loom_flow.py runtime-evidence --target . --item INIT-0001
	cd examples/new-project && python3 .loom/bin/loom_flow.py state-check --target . --item INIT-0001

repo-local-cli-flow-gates:
	cd examples/new-project && python3 .loom/bin/loom_flow.py flow pre-review --target . --item INIT-0001
	cd examples/new-project && python3 .loom/bin/loom_flow.py checkpoint admission --target . --item INIT-0001

repo-local-cli-workspace-locate:
	cd examples/new-project && python3 .loom/bin/loom_flow.py workspace locate --target . --item INIT-0001

repo-local-cli-purity-check:
	cd examples/new-project && python3 .loom/bin/loom_flow.py purity-check --target . --item INIT-0001

repo-local-cli-runtime-state-scene-conflict-negative:
	@if LOOM_SOURCE_REPO_ROOT="$$PWD" LOOM_INSTALLED_SKILLS_ROOT="$$PWD/skills" LOOM_RUNTIME_SCENE=upgrade-rehearsal python3 skills/shared/scripts/loom_flow.py runtime-state --target examples/new-project --item INIT-0001; then \
		echo "expected runtime-state conflict to fail closed"; \
		exit 1; \
	fi
