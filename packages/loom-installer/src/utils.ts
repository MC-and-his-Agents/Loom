import { accessSync, cpSync, existsSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { constants } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

export class InstallerError extends Error {
  readonly failClosedReason: string;

  constructor(message: string, failClosedReason?: string) {
    super(message);
    this.name = 'InstallerError';
    this.failClosedReason = failClosedReason ?? message;
  }
}

export function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new InstallerError(message);
  }
}

export function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, 'utf8')) as T;
}

export function writeJson(path: string, value: unknown): void {
  ensureDirectory(dirname(path));
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

export function ensureDirectory(path: string): void {
  mkdirSync(path, { recursive: true });
}

export function ensureTargetWritable(path: string): void {
  if (!existsSync(path)) {
    throw new InstallerError(`target path does not exist: ${path}`);
  }
  try {
    accessSync(path, constants.W_OK);
  } catch {
    throw new InstallerError(`target path is not writable: ${path}`);
  }
}

export function ensureTargetExists(path: string): void {
  if (!existsSync(path)) {
    throw new InstallerError(`target path does not exist: ${path}`);
  }
}

export function copyTree(source: string, target: string, force: boolean): void {
  if (existsSync(target)) {
    if (!force) {
      throw new InstallerError(`target already exists: ${target}`, `existing Loom-managed install requires --force: ${target}`);
    }
    rmSync(target, { recursive: true, force: true });
  }
  ensureDirectory(dirname(target));
  cpSync(source, target, { recursive: true, force: true });
}

export function replaceTree(source: string, target: string): void {
  rmSync(target, { recursive: true, force: true });
  ensureDirectory(dirname(target));
  cpSync(source, target, { recursive: true, force: true });
}

export function sha256(path: string): string {
  const hash = createHash('sha256');
  hash.update(readFileSync(path));
  return hash.digest('hex');
}

export function fileExists(path: string): boolean {
  return existsSync(path) && statSync(path).isFile();
}

export function dirExists(path: string): boolean {
  return existsSync(path) && statSync(path).isDirectory();
}

export function runCommand(
  command: string,
  args: string[],
  env: NodeJS.ProcessEnv,
  cwd?: string,
): { status: number | null; stdout: string; stderr: string } {
  const result = spawnSync(command, args, {
    cwd,
    env,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  if (result.error) {
    throw new InstallerError(`failed to execute ${command}: ${result.error.message}`);
  }
  return {
    status: result.status,
    stdout: result.stdout ?? '',
    stderr: result.stderr ?? '',
  };
}

export function resolveAbsolute(path: string): string {
  return resolve(path);
}
