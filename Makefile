.PHONY: loom-check check loom-demo-new-project

loom-check:
	python3 tools/loom_check.py

check: loom-check

loom-demo-new-project:
	python3 tools/loom_init.py bootstrap --target examples/new-project --write --force --verify --install-pr-template
