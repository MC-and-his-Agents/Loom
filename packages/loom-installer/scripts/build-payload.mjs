import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync, renameSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join, relative } from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(scriptDir, '..');
const repoRoot = join(packageRoot, '..', '..');
const payloadRoot = join(packageRoot, 'payload');
const pluginManifestSource = join(repoRoot, 'plugins', 'loom', '.codex-plugin');
const skillsSourceRoot = join(repoRoot, 'skills');
const pluginManifestPath = join(pluginManifestSource, 'plugin.json');
const installLayoutPath = join(skillsSourceRoot, 'install-layout.json');
const payloadLockDir = join(packageRoot, '.payload-lock');
const repoVersionPath = join(repoRoot, 'VERSION');
const packageJsonPath = join(packageRoot, 'package.json');

function sleep(milliseconds) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, milliseconds);
}

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

function writeJson(path, value) {
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

function sha256(path) {
  const hash = createHash('sha256');
  hash.update(readFileSync(path));
  return hash.digest('hex');
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

function collectFiles(baseDir, relativeBase = '') {
  const files = [];
  for (const entry of readdirSync(baseDir, { withFileTypes: true })) {
    if (shouldIgnore(entry.name)) {
      continue;
    }
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

function gitValue(args, fallback) {
  try {
    return execFileSync('git', args, { cwd: repoRoot, encoding: 'utf8' }).trim() || fallback;
  } catch {
    return fallback;
  }
}

function publicSkillEntries() {
  const registry = readJson(join(skillsSourceRoot, 'registry.json'));
  if (!Array.isArray(registry.entries) || registry.entries.length === 0) {
    throw new Error('skills/registry.json must declare entries');
  }
  return registry.entries.map((entry) => {
    if (!entry?.id) {
      throw new Error('skills/registry.json contains an entry without id');
    }
    return entry;
  });
}

function requiredInstallLayoutPaths() {
  const layout = readJson(installLayoutPath);
  if (!Array.isArray(layout.required_paths) || layout.required_paths.length === 0) {
    throw new Error('skills/install-layout.json must declare required_paths');
  }
  return layout.required_paths;
}

function verifyRequiredPaths(rootDir, requiredPaths, label) {
  const missing = [];
  for (const requiredPath of requiredPaths) {
    if (!existsSync(join(rootDir, requiredPath))) {
      missing.push(requiredPath);
    }
  }
  if (missing.length > 0) {
    throw new Error(`${label} is missing required paths: ${missing.join(', ')}`);
  }
}

function buildPluginPayload(currentPayloadRoot) {
  const pluginTarget = join(currentPayloadRoot, 'plugin', 'loom');
  mkdirSync(pluginTarget, { recursive: true });
  copyDirectoryFiltered(pluginManifestSource, join(pluginTarget, '.codex-plugin'));
  copyDirectoryFiltered(skillsSourceRoot, join(pluginTarget, 'skills'));
  return pluginTarget;
}

function buildSingleSkillPayloads(currentPayloadRoot, entries, requiredPaths) {
  const skillsPayloadRoot = join(currentPayloadRoot, 'skills');
  mkdirSync(skillsPayloadRoot, { recursive: true });
  const skills = [];
  for (const entry of entries) {
    const skillId = entry.id;
    const sourceDir = join(skillsSourceRoot, skillId);
    if (!existsSync(sourceDir)) {
      throw new Error(`missing skill source: ${sourceDir}`);
    }
    const contract = readJson(join(sourceDir, 'contract.json'));
    const packageMetadata = readJson(join(sourceDir, 'loom-package.json'));
    const packageDir = join(skillsPayloadRoot, skillId);
    mkdirSync(packageDir, { recursive: true });
    copyDirectoryFiltered(sourceDir, packageDir);
    const runtimeRoot = join(packageDir, packageMetadata.runtime_root ?? '.loom-runtime');
    verifyRequiredPaths(runtimeRoot, requiredPaths, `single-skill runtime for ${skillId}`);
    if (!existsSync(join(packageDir, 'SKILL.md')) || !existsSync(join(packageDir, 'loom-package.json'))) {
      throw new Error(`single-skill package for ${skillId} is incomplete`);
    }
    skills.push({
      id: contract.id,
      display_name: contract.display_name,
      contract_version: contract.contract_version,
      skill_package_version: packageMetadata.skill_package_version,
      runtime_core_version: packageMetadata.runtime_core_version,
      package_metadata: 'loom-package.json',
      runtime_root: packageMetadata.runtime_root,
      launcher: packageMetadata.launcher,
      relative_path: `skills/${skillId}`,
    });
  }
  return skills;
}

if (!existsSync(pluginManifestPath)) {
  throw new Error(`missing plugin manifest: ${pluginManifestPath}`);
}
if (!existsSync(skillsSourceRoot)) {
  throw new Error(`missing skills source root: ${skillsSourceRoot}`);
}
if (!existsSync(installLayoutPath)) {
  throw new Error(`missing install layout: ${installLayoutPath}`);
}

function acquirePayloadLock() {
  let attempts = 0;
  for (;;) {
    try {
      mkdirSync(payloadLockDir);
      return;
    } catch (error) {
      if (error?.code !== 'EEXIST') {
        throw error;
      }
      attempts += 1;
      if (attempts >= 200) {
        throw new Error(`timed out waiting for payload build lock: ${payloadLockDir}`);
      }
      sleep(100);
    }
  }
}

function releasePayloadLock() {
  rmSync(payloadLockDir, { recursive: true, force: true });
}

function publishPayload(stagingRoot) {
  rmSync(payloadRoot, { recursive: true, force: true });
  renameSync(stagingRoot, payloadRoot);
}

function buildPayload() {
  const stagingRoot = mkdtempSync(join(packageRoot, '.payload-build-'));
  try {
    mkdirSync(stagingRoot, { recursive: true });

    const requiredPaths = requiredInstallLayoutPaths();
    const pluginTarget = buildPluginPayload(stagingRoot);
    verifyRequiredPaths(join(pluginTarget, 'skills'), requiredPaths, 'plugin payload');
    const skillRecords = buildSingleSkillPayloads(stagingRoot, publicSkillEntries(), requiredPaths);
    const pluginManifest = readJson(pluginManifestPath);
    const packageJson = readJson(packageJsonPath);
    const repoVersion = readFileSync(repoVersionPath, 'utf8').trim();
    const registry = readJson(join(skillsSourceRoot, 'registry.json'));
    const files = collectFiles(stagingRoot).filter((entry) => entry.path !== 'manifest.json');
    const hostAdapterVersion = pluginManifest['x-loom']?.host_adapter_version ?? '1.0.0';

    const manifest = {
      schema_version: 'loom-installer-payload/v1',
      loom_version: repoVersion,
      source_repository: 'https://github.com/MC-and-his-Agents/Loom',
      source_commit: gitValue(['rev-parse', 'HEAD'], 'unknown'),
      source_ref: gitValue(['rev-parse', '--abbrev-ref', 'HEAD'], 'unknown'),
      built_at: process.env.LOOM_INSTALLER_BUILD_TIMESTAMP ?? new Date().toISOString(),
      version_context: {
        repo_version: repoVersion,
        installer_package_version: packageJson.version,
        plugin_surface_version: pluginManifest.version,
        host_adapter_version: hostAdapterVersion,
        skills_registry_version: registry.registry_version,
        runtime_core_version: skillRecords[0]?.runtime_core_version ?? '1.0.0',
      },
      runtime: {
        python_minimum: '3.10',
        python_recommended: '3.11+',
      },
      plugin: {
        name: pluginManifest.name,
        version: pluginManifest.version,
        host_adapter_version: hostAdapterVersion,
        relative_path: 'plugin/loom',
      },
      skills: skillRecords,
      files,
    };

    writeJson(join(stagingRoot, 'manifest.json'), manifest);
    publishPayload(stagingRoot);

    console.log(`payload ready: ${relative(repoRoot, payloadRoot)}`);
    console.log(`skills bundled: ${skillRecords.map((skill) => skill.id).join(', ')}`);
  } finally {
    rmSync(stagingRoot, { recursive: true, force: true });
  }
}

acquirePayloadLock();
try {
  buildPayload();
} finally {
  releasePayloadLock();
}
