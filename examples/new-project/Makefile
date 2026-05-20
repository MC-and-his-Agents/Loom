.PHONY: loom-check loom-story-carriers-check loom-verify

loom-check: loom-verify loom-story-carriers-check

loom-verify:
	python3 .loom/bin/loom_init.py verify --target .

loom-story-carriers-check:
	python3 .loom/bin/loom_story_carriers.py .
