import { createHash } from 'node:crypto';
import { readdirSync, readFileSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(scriptDir, '..');
const payloadRoot = join(packageRoot, 'payload');
const fixedTimestamp = process.env.LOOM_INSTALLER_BUILD_TIMESTAMP ?? '2026-01-01T00:00:00.000Z';

function runBuild() {
  const result = spawnSync('node', ['./scripts/build-payload.mjs'], {
    cwd: packageRoot,
    env: {
      ...process.env,
      LOOM_INSTALLER_BUILD_TIMESTAMP: fixedTimestamp,
    },
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  if (result.status !== 0) {
    throw new Error((result.stderr || result.stdout || 'build-payload failed').trim());
  }
}

function walk(dir, base = dir) {
  const files = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const entryPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...walk(entryPath, base));
      continue;
    }
    if (!entry.isFile()) {
      continue;
    }
    const rel = relative(base, entryPath).replaceAll('\\', '/');
    const fileBytes = readFileSync(entryPath).byteLength;
    const sha = createHash('sha256').update(readFileSync(entryPath)).digest('hex');
    files.push(`${rel}:${fileBytes}:${sha}`);
  }
  return files.sort();
}

function fingerprint() {
  const files = walk(payloadRoot);
  return createHash('sha256').update(files.join('\n')).digest('hex');
}

function main() {
  runBuild();
  const firstManifest = JSON.parse(readFileSync(join(payloadRoot, 'manifest.json'), 'utf8'));
  if (firstManifest.built_at !== fixedTimestamp) {
    throw new Error(`payload manifest built_at must equal ${fixedTimestamp}`);
  }
  const first = fingerprint();
  runBuild();
  const secondManifest = JSON.parse(readFileSync(join(payloadRoot, 'manifest.json'), 'utf8'));
  if (secondManifest.built_at !== fixedTimestamp) {
    throw new Error(`second payload manifest built_at must equal ${fixedTimestamp}`);
  }
  const second = fingerprint();
  if (first !== second) {
    throw new Error('payload rebuild drift detected');
  }
  console.log(`payload drift check: OK (${first})`);
}

try {
  main();
} catch (error) {
  console.error(`payload drift check failed: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
}
