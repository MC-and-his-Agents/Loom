import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const root = new URL('..', import.meta.url);
const checks = [
  ['README.md', ['This package is retired.', 'npm install -g @mc-and-his-agents/loom', 'loom host install --host codex --scope user --apply --json', 'fails closed']],
  ['README.zh-CN.md', ['这个包已退役。', 'npm install -g @mc-and-his-agents/loom', 'loom host install --host codex --scope user --apply --json', 'fail closed']],
];

for (const [file, needles] of checks) {
  const content = readFileSync(join(root.pathname, file), 'utf8');
  for (const needle of needles) {
    if (!content.includes(needle)) {
      console.error(`doc sync check failed: ${file} missing ${JSON.stringify(needle)}`);
      process.exit(1);
    }
  }
}

console.log('doc sync check: OK');
