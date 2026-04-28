# Installing Loom for Codex

Enable Loom skills in Codex via native skill discovery. Clone the repository and symlink each public Loom skill directory.

## Prerequisites

- Git
- Python `>=3.10`, recommended `3.11+`

## Installation

1. Clone Loom:

   ```bash
   git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom
   ```

2. Create skill symlinks:

   ```bash
   mkdir -p ~/.agents/skills
   for skill in ~/.codex/loom/skills/loom-*; do
     ln -sfn "$skill" "$HOME/.agents/skills/$(basename "$skill")"
   done
   ```

3. Restart Codex.

## Verify

```bash
ls -la ~/.agents/skills/loom-init
ls ~/.agents/skills/loom-init/SKILL.md
```

## Update

```bash
cd ~/.codex/loom && git pull
```

The skills update through the symlink.

## Uninstall

```bash
rm ~/.agents/skills/loom-*
```

Optionally delete the clone:

```bash
rm -rf ~/.codex/loom
```
