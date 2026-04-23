import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(scriptDir, '..');
const repoRoot = join(packageRoot, '..', '..');
const packageJsonPath = join(packageRoot, 'package.json');
const baseArgIndex = process.argv.indexOf('--base');
const baseRef = baseArgIndex >= 0 ? process.argv[baseArgIndex + 1] : 'origin/main';

const behaviorPrefixes = [
  'packages/loom-installer/src/',
  'plugins/loom/',
  'packages/skills/',
];

const behaviorPaths = [
  'packages/loom-installer/package.json',
  'packages/loom-installer/scripts/build-payload.mjs',
];

function git(args) {
  return execFileSync('git', args, {
    cwd: repoRoot,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  }).trim();
}

function readCurrentVersion() {
  return JSON.parse(readFileSync(packageJsonPath, 'utf8')).version;
}

function readBaseVersion() {
  try {
    return JSON.parse(git(['show', `${baseRef}:packages/loom-installer/package.json`])).version;
  } catch {
    return null;
  }
}

function changedFiles() {
  const output = git(['diff', '--name-only', `${baseRef}...HEAD`]);
  return output ? output.split('\n').filter(Boolean) : [];
}

const changed = changedFiles();
const behaviorChanged = changed.some(
  (path) => behaviorPaths.includes(path) || behaviorPrefixes.some((prefix) => path === prefix || path.startsWith(prefix)),
);
const currentVersion = readCurrentVersion();
const baseVersion = readBaseVersion();

if (!behaviorChanged) {
  console.log(`version bump check: OK (no installer behavior changes against ${baseRef})`);
  process.exit(0);
}

if (baseVersion === null) {
  console.log(`version bump check: OK (no base installer package at ${baseRef})`);
  process.exit(0);
}

if (baseVersion === currentVersion) {
  console.error(`version bump check failed: installer behavior changed but version stayed ${currentVersion}`);
  console.error(`changed files:\n${changed.join('\n')}`);
  process.exit(1);
}

console.log(`version bump check: OK (${baseVersion} -> ${currentVersion})`);
