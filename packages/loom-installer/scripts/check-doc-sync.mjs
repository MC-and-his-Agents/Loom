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
      'npx @mc-and-his-agents/loom-installer add skill loom-init --host codex',
      'npm install -D @mc-and-his-agents/loom-installer',
      'Node `>=20`',
      'Python `>=3.10`，推荐 `3.11+`',
      'Loom 当前真实执行面仍然是仓库里的 Python runtime。',
      '你希望 Agent 自己判断当前环境更适合 plugin 还是 single-skill 接入',
    ],
  },
  {
    path: 'skills/README.md',
    needles: [
      'npx @mc-and-his-agents/loom-installer add plugin',
      'npx @mc-and-his-agents/loom-installer add skill <skill-id>',
      'add plugin` 承诺完整 Loom 入口面',
      'add skill <skill-id>` 只承诺对应标准 skill',
      '安装成功不等于已经执行 Loom runtime',
      '单 skill package 不自动补齐 `loom-init`、其余 scenario skills 或完整 plugin 安装体验',
    ],
  },
  {
    path: 'skills/distribution-and-adapter-contract.md',
    needles: [
      '@mc-and-his-agents/loom-installer',
      '不伪装成 repo-local `loom` plugin 的完整安装成功',
      '若 shared runtime / resources 缺失、合同漂移或运行态冲突，宿主必须 fail-closed，而不是继续报告“可运行”',
      '当前入口属于 plugin install、scenario skill 还是单 skill package',
      'main 分支是真相源',
      'publish 成功后再创建同版本 git tag',
    ],
  },
  {
    path: 'skills/route-matrix.md',
    needles: [
      '显式 skill 名称调用优先',
      '若无显式 skill，则按任务信号做隐式路由',
      '若无法稳定判断，回退到 `loom-init`，输出最小补充信号',
      '`selected_skill: "loom-init"`',
      '`fallback_to: "loom-init"`',
    ],
  },
  {
    path: 'packages/loom-installer/README.md',
    needles: [
      'npm install -D @mc-and-his-agents/loom-installer',
      'Node `>=20`',
      'Python `>=3.10`，推荐 `3.11+`',
      '把某个单独 Loom skill 接到对应宿主',
      '它不替代 Loom 当前的 Python runtime；真正的执行面仍然是仓库里的 Python 脚本与已发布的 skill / plugin 产物。',
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
