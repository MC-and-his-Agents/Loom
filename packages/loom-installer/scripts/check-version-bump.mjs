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
];

const behaviorPaths = [];

const packageBehaviorFields = [
  'version',
  'bin',
  'files',
  'engines',
  'publishConfig',
  'dependencies',
  'optionalDependencies',
  'peerDependencies',
  'bundledDependencies',
  'bundleDependencies',
];

const packageBehaviorScripts = [
  'build',
  'prepack',
  'prepublishOnly',
  'test',
];

const ignoredCompatibilityPaths = [
  'plugins/loom/.codex-plugin/',
  'src/skills/',
  'skills/',
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

function readCurrentPackage() {
  return JSON.parse(readFileSync(packageJsonPath, 'utf8'));
}

function readBasePackage() {
  try {
    return JSON.parse(git(['show', `${baseRef}:packages/loom-installer/package.json`]));
  } catch {
    return null;
  }
}

function readBaseVersion() {
  return readBasePackage()?.version ?? null;
}

function changedFiles() {
  const output = git(['diff', '--name-only', `${baseRef}...HEAD`]);
  return output ? output.split('\n').filter(Boolean) : [];
}

function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}

function changedPackageField(basePackage, currentPackage, field) {
  return stableStringify(basePackage?.[field]) !== stableStringify(currentPackage?.[field]);
}

function packageJsonBehaviorChanged() {
  if (!changed.includes('packages/loom-installer/package.json')) {
    return false;
  }

  const basePackage = readBasePackage();
  if (basePackage === null) {
    return true;
  }
  const currentPackage = readCurrentPackage();

  if (packageBehaviorFields.some((field) => changedPackageField(basePackage, currentPackage, field))) {
    return true;
  }

  return packageBehaviorScripts.some(
    (script) => (basePackage.scripts?.[script] ?? null) !== (currentPackage.scripts?.[script] ?? null),
  );
}

const changed = changedFiles();
const relevantChanged = changed.filter((path) => !ignoredCompatibilityPaths.some((ignored) => path === ignored || path.startsWith(ignored)));
const behaviorChanged = changed.some(
  (path) =>
    relevantChanged.includes(path) &&
    (behaviorPaths.includes(path) || behaviorPrefixes.some((prefix) => path === prefix || path.startsWith(prefix))),
)
  || packageJsonBehaviorChanged();
const currentVersion = readCurrentVersion();
const baseVersion = readBaseVersion();

if (!behaviorChanged) {
  console.log(`version bump check: OK (no installer shim changes against ${baseRef})`);
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
