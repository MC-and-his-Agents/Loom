import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import test from "node:test";

const packageJson = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8"));

function runLoom(args) {
  return spawnSync(process.execPath, ["bin/loom.mjs", ...args], {
    cwd: new URL("..", import.meta.url),
    encoding: "utf8"
  });
}

test("root npm package exposes the frozen loom bin contract", () => {
  assert.equal(packageJson.name, "@mc-and-his-agents/loom");
  assert.equal(packageJson.bin.loom, "bin/loom.mjs");
  assert.equal(packageJson.publishConfig.access, "public");
  assert.equal(JSON.stringify(packageJson).includes("@mc-and-his-agents/loom-installer"), false);
});

test("loom bin prints help", () => {
  const completed = runLoom(["--help"]);
  assert.equal(completed.status, 0, completed.stderr);
  assert.match(completed.stdout, /usage: loom <command>/);
});

test("loom bin reports the root VERSION", () => {
  const completed = runLoom(["version", "--json"]);
  assert.equal(completed.status, 0, completed.stderr);
  const payload = JSON.parse(completed.stdout);
  assert.equal(payload.result, "pass");
  assert.equal(payload.versions.repo_version, "v0.13.0");
});
