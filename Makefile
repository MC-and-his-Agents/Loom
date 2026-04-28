.PHONY: loom-check check loom-demo-new-project loom-self-plugin-install

loom-check: loom-self-plugin-install loom-demo-new-project
	python3 tools/loom_check.py

check: loom-check

loom-demo-new-project:
	python3 tools/loom_init.py bootstrap --target examples/new-project --write --force --verify --install-pr-template

loom-self-plugin-install:
	test -x packages/loom-installer/node_modules/.bin/tsc || npm ci --prefix packages/loom-installer
	npm --prefix packages/loom-installer run build
	node packages/loom-installer/dist/src/cli.js add plugin --host codex --target . --force --json
