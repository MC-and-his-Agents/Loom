.PHONY: loom-check check skills-check loom-demo-new-project loom-self-plugin-check

loom-check: loom-self-plugin-check loom-demo-new-project
	python3 tools/loom_check.py

skills-check:
	python3 tools/skills_surface.py check

check: skills-check loom-check

loom-demo-new-project:
	python3 tools/loom_init.py bootstrap --target examples/new-project --write --force --verify --install-pr-template

loom-self-plugin-check:
	test -f plugins/loom/.codex-plugin/plugin.json
	test -f src/skills/registry.json
	test -f skills/registry.json
	test -f skills/loom-init/SKILL.md
	test -f skills/loom-init/loom-package.json
	test ! -f .agents/plugins/marketplace.json
