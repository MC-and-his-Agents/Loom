#!/usr/bin/env node
import { formatResult, parseCli, runInstaller } from './index.js';
import { InstallerError } from './utils.js';
import type { InstallResult } from './types.js';

function errorResult(message: string): InstallResult {
  return {
    schema_version: 'loom-installer-result/v1',
    operation: 'add',
    mode: 'plugin',
    host: 'codex',
    distribution_layer: 'host-adapter-plugin',
    status: 'blocked',
    installed_paths: [],
    verification: [],
    warnings: [],
    version_context: null,
    failed_layer: 'cli',
    fail_closed_reason: message,
  };
}

try {
  const parsed = parseCli(process.argv.slice(2));
  const result = runInstaller(parsed);
  if (parsed.options.json) {
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } else {
    process.stdout.write(`${formatResult(result)}\n`);
  }
} catch (error) {
  const message = error instanceof InstallerError ? error.failClosedReason : error instanceof Error ? error.message : String(error);
  const parsedJson = process.argv.includes('--json');
  if (parsedJson) {
    process.stdout.write(`${JSON.stringify(errorResult(message), null, 2)}\n`);
  } else {
    process.stderr.write(`loom-installer: ${message}\n`);
  }
  process.exit(1);
}
