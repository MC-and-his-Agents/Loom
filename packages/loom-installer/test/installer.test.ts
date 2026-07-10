import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';

test('loom-installer CLI is a fail-closed tombstone', () => {
  const result = spawnSync(process.execPath, ['dist/src/cli.js', 'add', 'plugin', '--json'], { encoding: 'utf8' });
  assert.equal(result.status, 1);
  const payload = JSON.parse(result.stdout);
  assert.equal(payload.status, 'blocked');
  assert.equal(payload.distribution_layer, 'tombstone-package');
  assert.match(payload.fail_closed_reason, /loom-installer is retired/);
  assert.equal(payload.migration.install_cli, 'npm install -g @mc-and-his-agents/loom');
});
