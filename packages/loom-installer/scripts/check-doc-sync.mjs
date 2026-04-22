import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(scriptDir, '..');
const repoRoot = join(packageRoot, '..', '..');

const mirroredPairs = [
  ['skills/README.md', 'plugins/loom/skills/README.md'],
  ['skills/distribution-and-adapter-contract.md', 'plugins/loom/skills/distribution-and-adapter-contract.md'],
  ['skills/shared/scripts/loom_check.py', 'plugins/loom/skills/shared/scripts/loom_check.py'],
];

const requiredNeedles = [
  {
    path: 'README.md',
    needles: [
      'npx @mc-and-his-agents/loom-installer add plugin --host codex',
      'npm install -D @mc-and-his-agents/loom-installer',
      'Node `>=20`',
      'Python `>=3.10`，推荐 `3.11+`',
      'Loom 当前真实执行面仍然是仓库里的 Python runtime。',
    ],
  },
  {
    path: 'skills/README.md',
    needles: [
      'npx @mc-and-his-agents/loom-installer add plugin',
      '安装成功不等于已经执行 Loom runtime',
    ],
  },
  {
    path: 'skills/distribution-and-adapter-contract.md',
    needles: [
      '@mc-and-his-agents/loom-installer',
      'main 分支是真相源',
      'publish 成功后再创建同版本 git tag',
    ],
  },
  {
    path: 'packages/loom-installer/README.md',
    needles: [
      'npm install -D @mc-and-his-agents/loom-installer',
      'Node `>=20`',
      'Python `>=3.10`，推荐 `3.11+`',
      '发布只在 `main` 上进行',
    ],
  },
];

function readRepoFile(relativePath) {
  return readFileSync(join(repoRoot, relativePath), 'utf8');
}

for (const [sourcePath, mirrorPath] of mirroredPairs) {
  const source = readRepoFile(sourcePath);
  const mirror = readRepoFile(mirrorPath);
  if (source !== mirror) {
    console.error(`doc sync check failed: ${mirrorPath} drifted from ${sourcePath}`);
    process.exit(1);
  }
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
