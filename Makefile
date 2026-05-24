.PHONY: loom-check check py-compile skills-check host-adapter-check version-surface-check cli-contract-check loom-check-runtime-regression loom-demo-new-project loom-demo-new-project-check loom-demo-new-project-sync loom-self-plugin-check

loom-check: loom-self-plugin-check loom-demo-new-project-check loom-check-runtime-regression
	python3 tools/loom_check.py

py-compile:
	python3 tools/py_compile_clean.py tools/loom.py tools/loom_init.py tools/loom_flow.py tools/loom_check.py tools/loom_status.py tools/py_compile_clean.py tools/check_cli_contract.py tools/check_demo_bootstrap_fixture.py tools/check_loom_check_runtime_regressions.py skills/shared/scripts/*.py src/skills/shared/scripts/*.py skills/loom-init/scripts/*.py skills/loom-adopt/scripts/*.py skills/loom-resume/scripts/*.py skills/loom-pre-review/scripts/*.py skills/loom-review/scripts/*.py skills/loom-spec-review/scripts/*.py skills/loom-handoff/scripts/*.py skills/loom-retire/scripts/*.py skills/loom-merge-ready/scripts/*.py skills/loom-build/scripts/*.py skills/loom-story/scripts/*.py

skills-check:
	python3 tools/skills_surface.py check

host-adapter-check:
	python3 tools/host_adapter_check.py

version-surface-check:
	python3 tools/version_surface_check.py

cli-contract-check:
	python3 tools/check_cli_contract.py

loom-check-runtime-regression:
	python3 tools/check_loom_check_runtime_regressions.py

check: py-compile skills-check host-adapter-check version-surface-check cli-contract-check loom-check

loom-demo-new-project:
	python3 tools/check_demo_bootstrap_fixture.py

loom-demo-new-project-check:
	python3 tools/check_demo_bootstrap_fixture.py

loom-demo-new-project-sync:
	python3 tools/loom_init.py bootstrap --target examples/new-project --scenario new --intent execution-control --intake examples/new-project/.loom/bootstrap/intake.snapshot.json --write --force --verify --install-pr-template --portable-output

loom-self-plugin-check:
	test -f plugins/loom/.codex-plugin/plugin.json
	test -f src/skills/registry.json
	test -f skills/registry.json
	test -f skills/loom-init/SKILL.md
	test -f skills/loom-init/loom-package.json
	test ! -f .agents/plugins/marketplace.json
