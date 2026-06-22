import { spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = join(scriptDir, '..');
const lockDir = join(packageRoot, '.installer-regression-lock');
const ownerPath = join(lockDir, 'owner.json');
const staleAfterMs = 6 * 60 * 60 * 1000;
const timeoutMs = Number(process.env.LOOM_INSTALLER_REGRESSION_LOCK_TIMEOUT_SECONDS ?? '300') * 1000;

function sleep(milliseconds) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, milliseconds);
}

function nowIso() {
  return new Date().toISOString();
}

function readOwner() {
  try {
    return JSON.parse(readFileSync(ownerPath, 'utf8'));
  } catch {
    return {};
  }
}

function processIsAlive(pid) {
  if (!Number.isInteger(pid) || pid <= 0) {
    return false;
  }
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    return error?.code === 'EPERM';
  }
}

function ownerIsStale(owner) {
  if (!processIsAlive(owner.pid)) {
    return true;
  }
  const startedAt = Date.parse(owner.started_at ?? '');
  if (Number.isNaN(startedAt)) {
    return false;
  }
  return Date.now() - startedAt > staleAfterMs;
}

function formatBusy(owner, fallback) {
  return [
    'installer regression lock is busy',
    `lock: ${lockDir}`,
    `owner: run_id=${owner.run_id ?? 'unknown'} pid=${owner.pid ?? 'unknown'} started_at=${owner.started_at ?? 'unknown'}`,
    `owner_command: ${owner.command ?? 'unknown'}`,
    `owner_cwd: ${owner.cwd ?? 'unknown'}`,
    `fallback: ${fallback}`,
  ].join('\n');
}

function acquireLock() {
  const runId = randomUUID().replaceAll('-', '');
  const owner = {
    schema_version: 'loom-installer-regression-lock/v1',
    run_id: runId,
    pid: process.pid,
    started_at: nowIso(),
    command: ['node', 'packages/loom-installer/scripts/run-regression.mjs'].join(' '),
    cwd: process.cwd(),
  };
  const started = Date.now();
  for (;;) {
    try {
      mkdirSync(lockDir);
      try {
        writeFileSync(ownerPath, `${JSON.stringify(owner, null, 2)}\n`, 'utf8');
      } catch (error) {
        rmSync(lockDir, { recursive: true, force: true });
        throw error;
      }
      return runId;
    } catch (error) {
      if (error?.code !== 'EEXIST') {
        throw error;
      }
      const currentOwner = readOwner();
      if (ownerIsStale(currentOwner)) {
        rmSync(lockDir, { recursive: true, force: true });
        continue;
      }
      if (Date.now() - started >= timeoutMs) {
        throw new Error(formatBusy(currentOwner, 'wait for the owner to finish, verify/remove a stale lock, or run in a different worktree'));
      }
      sleep(250);
    }
  }
}

function releaseLock(runId) {
  const owner = readOwner();
  if (owner.run_id !== runId) {
    return;
  }
  rmSync(lockDir, { recursive: true, force: true });
}

function runStep(label, command, args, env) {
  console.log(`installer tombstone regression: ${label}`);
  const result = spawnSync(command, args, {
    cwd: packageRoot,
    env,
    stdio: 'inherit',
  });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    throw new Error(`${label} failed with exit code ${result.status ?? 'unknown'}`);
  }
}

function main() {
  if (!existsSync(join(packageRoot, 'package.json'))) {
    throw new Error(`installer package root is missing package.json: ${packageRoot}`);
  }
  const cacheDir = mkdtempSync(join(tmpdir(), 'loom-installer-npm-cache-'));
  const env = {
    ...process.env,
    npm_config_cache: cacheDir,
    NPM_CONFIG_CACHE: cacheDir,
  };
  let runId = null;
  try {
    runId = acquireLock();
    console.log(`installer regression lock acquired: ${lockDir}`);
    console.log(`installer regression npm cache: ${cacheDir}`);
    runStep('npm ci', 'npm', ['ci'], env);
    runStep('npm test', 'npm', ['test'], env);
    runStep('npm pack --dry-run', 'npm', ['pack', '--dry-run'], env);
  } finally {
    if (runId) {
      releaseLock(runId);
    }
    rmSync(cacheDir, { recursive: true, force: true });
  }
}

try {
  main();
} catch (error) {
  console.error(`installer tombstone regression failed: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
}
