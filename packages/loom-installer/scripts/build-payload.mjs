import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join, relative } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(scriptDir, '..');
const repoRoot = join(packageRoot, '..', '..');
const payloadRoot = join(packageRoot, 'payload');
const pluginSource = join(repoRoot, 'plugins', 'loom');
const skillsSourceRoot = join(repoRoot, 'packages', 'skills');
const pluginManifestPath = join(pluginSource, '.codex-plugin', 'plugin.json');

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

function sha256(path) {
  const hash = createHash('sha256');
  hash.update(readFileSync(path));
  return hash.digest('hex');
}

function collectFiles(baseDir, relativeBase = '') {
  const files = [];
  for (const entry of readdirSync(baseDir, { withFileTypes: true })) {
    const entryPath = join(baseDir, entry.name);
    const entryRelative = relativeBase ? join(relativeBase, entry.name) : entry.name;
    if (entry.isDirectory()) {
      files.push(...collectFiles(entryPath, entryRelative));
      continue;
    }
    if (!entry.isFile()) {
      continue;
    }
    files.push({
      path: entryRelative.replaceAll('\\', '/'),
      bytes: statSync(entryPath).size,
      sha256: sha256(entryPath),
    });
  }
  return files.sort((a, b) => a.path.localeCompare(b.path));
}

function shouldIgnore(name) {
  return name === '__pycache__' || name.endsWith('.pyc');
}

function copyDirectoryFiltered(sourceDir, targetDir) {
  mkdirSync(targetDir, { recursive: true });
  for (const entry of readdirSync(sourceDir, { withFileTypes: true })) {
    if (shouldIgnore(entry.name)) {
      continue;
    }
    const sourcePath = join(sourceDir, entry.name);
    const targetPath = join(targetDir, entry.name);
    if (entry.isDirectory()) {
      copyDirectoryFiltered(sourcePath, targetPath);
      continue;
    }
    if (entry.isFile()) {
      cpSync(sourcePath, targetPath, { force: true });
    }
  }
}

function gitValue(args, fallback) {
  try {
    return execFileSync('git', args, { cwd: repoRoot, encoding: 'utf8' }).trim() || fallback;
  } catch {
    return fallback;
  }
}

if (!existsSync(pluginSource)) {
  throw new Error(`missing plugin source: ${pluginSource}`);
}
if (!existsSync(skillsSourceRoot)) {
  throw new Error(`missing skills source root: ${skillsSourceRoot}`);
}

rmSync(payloadRoot, { recursive: true, force: true });
mkdirSync(payloadRoot, { recursive: true });
mkdirSync(join(payloadRoot, 'plugin'), { recursive: true });
mkdirSync(join(payloadRoot, 'skills'), { recursive: true });

copyDirectoryFiltered(pluginSource, join(payloadRoot, 'plugin', 'loom'));

const skillDirs = readdirSync(skillsSourceRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();

const skills = [];
for (const skillDir of skillDirs) {
  const sourceDir = join(skillsSourceRoot, skillDir);
  const contractPath = join(sourceDir, 'contract.json');
  const contract = readJson(contractPath);
  copyDirectoryFiltered(sourceDir, join(payloadRoot, 'skills', skillDir));
  skills.push({
    id: contract.id,
    display_name: contract.display_name,
    contract_version: contract.contract_version,
    relative_path: `skills/${skillDir}`,
  });
}

const pluginManifest = readJson(pluginManifestPath);
const files = collectFiles(payloadRoot)
  .filter((entry) => entry.path !== 'manifest.json');

const manifest = {
  schema_version: 'loom-installer-payload/v1',
  loom_version: pluginManifest.version,
  source_repository: 'https://github.com/MC-and-his-Agents/Loom',
  source_commit: gitValue(['rev-parse', 'HEAD'], 'unknown'),
  source_ref: gitValue(['rev-parse', '--abbrev-ref', 'HEAD'], 'unknown'),
  built_at: process.env.LOOM_INSTALLER_BUILD_TIMESTAMP ?? new Date().toISOString(),
  runtime: {
    python_minimum: '3.10',
    python_recommended: '3.11+'
  },
  plugin: {
    name: pluginManifest.name,
    version: pluginManifest.version,
    relative_path: 'plugin/loom'
  },
  skills,
  files
};

writeFileSync(join(payloadRoot, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');

console.log(`payload ready: ${relative(repoRoot, payloadRoot)}`);
console.log(`skills bundled: ${skills.map((skill) => skill.id).join(', ')}`);
