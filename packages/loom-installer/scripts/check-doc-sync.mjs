import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(scriptDir, '..');
const repoRoot = join(packageRoot, '..', '..');

const requiredNeedles = [
  {
    path: 'README.md',
    needles: [
      'Loom 是一个以 skills 为先的方法论仓库',
      'Fetch and follow instructions from https://raw.githubusercontent.com/MC-and-his-Agents/Loom/refs/heads/main/.codex/INSTALL.md',
      'npx @mc-and-his-agents/loom-installer add plugin --host codex',
      '高级 / 兼容',
    ],
  },
  {
    path: '.codex/INSTALL.md',
    needles: [
      'git clone https://github.com/MC-and-his-Agents/Loom.git ~/.codex/loom',
      'ln -s ~/.codex/loom/skills ~/.agents/skills/loom',
      'Restart Codex',
    ],
  },
  {
    path: 'skills/README.md',
    needles: [
      'canonical skills library',
      '默认从 `loom-init` 开始',
      'Advanced / Compatibility',
      'npx @mc-and-his-agents/loom-installer add skill <skill-id>',
    ],
  },
  {
    path: 'skills/distribution-and-adapter-contract.md',
    needles: [
      '@mc-and-his-agents/loom-installer',
      'repo-local `.codex-plugin/` + `skills/`',
      'main 分支是真相源',
      'publish 成功后再创建 `loom-installer-v<version>` git tag 与同名前缀的 GitHub Release',
    ],
  },
  {
    path: 'packages/loom-installer/README.md',
    needles: [
      'npm install -D @mc-and-his-agents/loom-installer',
      'Node `>=20`',
      'Python `>=3.10`，推荐 `3.11+`',
      'add plugin',
      'add skill <skill-id>',
      'payload is generated from the canonical root `.codex-plugin/` and `skills/` sources',
    ],
  },
];

function readRepoFile(relativePath) {
  return readFileSync(join(repoRoot, relativePath), 'utf8');
}

for (const entry of requiredNeedles) {
  const content = readRepoFile(entry.path);
  for (const needle of entry.needles) {
    if (!content.includes(needle)) {
      console.error(`doc sync check failed: ${entry.path} is missing ${JSON.stringify(needle)}`);
      process.exit(1);
    }
  }
}

console.log('doc sync check: OK');
