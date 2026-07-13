import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const packageJson = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8"));
const repoVersion = readFileSync(new URL("../VERSION", import.meta.url), "utf8").trim();
const repoRoot = fileURLToPath(new URL("..", import.meta.url));

function runLoom(args) {
  return spawnSync(process.execPath, ["bin/loom.mjs", ...args], {
    cwd: repoRoot,
    encoding: "utf8"
  });
}

test("root npm package exposes the frozen loom bin contract", () => {
  assert.equal(packageJson.name, "@mc-and-his-agents/loom");
  assert.equal(packageJson.bin.loom, "bin/loom.mjs");
  assert.equal(packageJson.publishConfig.access, "public");
  assert.equal(JSON.stringify(packageJson).includes("@mc-and-his-agents/loom-installer"), false);
});

test("root npm package includes suite contract source truth", () => {
  for (const requiredFile of [
    "docs/adoption/github-profile.md",
    "docs/adoption/legacy-install-migration.md",
    "docs/methodology/harness/full-spec-suite-cli-surface.md",
    "docs/methodology/harness/gate-chain.md",
    "docs/methodology/harness/task-carrier-contract.md",
    "docs/methodology/templates/evidence-map.md",
    "docs/methodology/templates/spec-suite.md"
  ]) {
    assert.equal(packageJson.files.includes(requiredFile), true, requiredFile);
  }
});

test("root npm package publishes only source skills and Codex plugin payload", () => {
  assert.equal(packageJson.files.includes("skills"), false);
  assert.equal(packageJson.files.includes("src/skills"), true);
  assert.equal(packageJson.files.includes("plugins/loom"), true);

  const pluginManifest = JSON.parse(
    readFileSync(new URL("../plugins/loom/.codex-plugin/plugin.json", import.meta.url), "utf8")
  );
  const pluginRegistry = JSON.parse(
    readFileSync(new URL("../plugins/loom/skills/registry.json", import.meta.url), "utf8")
  );
  assert.equal(pluginManifest.name, "loom");
  assert.equal(pluginRegistry.root_entry, "loom-init");
  assert.equal(pluginRegistry.entries.some((entry) => entry.id === "loom-init"), true);
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
  assert.equal(payload.versions.repo_version, repoVersion);
});

test("packed npm payload runs the public metadata-only adoption path", () => {
  const tmp = mkdtempSync(join(tmpdir(), "loom-npm-package-smoke-"));
  try {
    const packed = spawnSync("npm", ["pack", "--json", "--ignore-scripts", "--pack-destination", tmp], {
      cwd: repoRoot,
      encoding: "utf8"
    });
    assert.equal(packed.status, 0, packed.stderr || packed.stdout);
    const packInfo = JSON.parse(packed.stdout);
    const tarball = join(tmp, packInfo[0].filename);
    const extractRoot = join(tmp, "extract");
    mkdirSync(extractRoot);
    const extracted = spawnSync("tar", ["-xzf", tarball, "-C", extractRoot], { encoding: "utf8" });
    assert.equal(extracted.status, 0, extracted.stderr);

    const fixtureRepo = join(tmp, "fixture-repo");
    mkdirSync(fixtureRepo);
    const initialized = spawnSync("git", ["init", "--quiet"], { cwd: fixtureRepo, encoding: "utf8" });
    assert.equal(initialized.status, 0, initialized.stderr);

    const loomBin = join(extractRoot, "package", "bin", "loom.mjs");
    const installed = spawnSync(
      process.execPath,
      [loomBin, "install", "--target", fixtureRepo, "--apply", "--json"],
      { cwd: tmp, encoding: "utf8" }
    );
    assert.equal(installed.status, 0, installed.stderr || installed.stdout);
    const installPayload = JSON.parse(installed.stdout);
    assert.equal(installPayload.result, "pass");
    assert.deepEqual(new Set(installPayload.managed_writes), new Set([".loom/installed-state.json", "AGENTS.md"]));

    const validated = spawnSync(
      process.execPath,
      [loomBin, "installed-state", "validate", "--target", fixtureRepo, "--json"],
      { cwd: tmp, encoding: "utf8" }
    );
    assert.equal(validated.status, 0, validated.stderr || validated.stdout);
    assert.equal(JSON.parse(validated.stdout).result, "pass");

    const verified = spawnSync(
      process.execPath,
      [loomBin, "verify", "--target", fixtureRepo, "--json"],
      { cwd: tmp, encoding: "utf8" }
    );
    assert.equal(verified.status, 0, verified.stderr || verified.stdout);
    assert.equal(JSON.parse(verified.stdout).result, "pass");
    for (const removedCarrier of ["status", "progress", "reviews", "shadow", "work-items", "runtime"]) {
      assert.equal(existsSync(join(fixtureRepo, ".loom", removedCarrier)), false, removedCarrier);
    }
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
});
