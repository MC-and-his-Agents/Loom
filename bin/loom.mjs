#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const packageRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const cli = join(packageRoot, "tools", "loom.py");
const invocationCwd = process.cwd();
const args = process.argv.slice(2);
const candidates = process.platform === "win32" ? ["py", "python3", "python"] : ["python3", "python"];

let lastError = null;

for (const candidate of candidates) {
  const commandArgs = candidate === "py" ? ["-3", cli, ...args] : [cli, ...args];
  const completed = spawnSync(candidate, commandArgs, {
    cwd: packageRoot,
    stdio: "inherit",
    env: {
      ...process.env,
      LOOM_SOURCE_REPO_ROOT: process.env.LOOM_SOURCE_REPO_ROOT || packageRoot,
      LOOM_INVOCATION_CWD: process.env.LOOM_INVOCATION_CWD || invocationCwd,
      PYTHONDONTWRITEBYTECODE: process.env.PYTHONDONTWRITEBYTECODE || "1"
    }
  });

  if (completed.error && completed.error.code === "ENOENT") {
    lastError = completed.error;
    continue;
  }

  if (completed.error) {
    console.error(JSON.stringify({
      schema_version: "loom-npm-bin/v1",
      command: "loom",
      result: "block",
      failed_layer: "python-runtime",
      fail_closed_reason: completed.error.message,
      fallback_to: ["install Python 3.11 or newer", "python3 tools/loom.py help --json"]
    }, null, 2));
    process.exit(1);
  }

  process.exit(completed.status ?? 1);
}

console.error(JSON.stringify({
  schema_version: "loom-npm-bin/v1",
  command: "loom",
  result: "block",
  failed_layer: "python-runtime",
  fail_closed_reason: lastError ? lastError.message : "Python runtime was not found",
  fallback_to: ["install Python 3.11 or newer", "python3 tools/loom.py help --json"]
}, null, 2));
process.exit(1);
