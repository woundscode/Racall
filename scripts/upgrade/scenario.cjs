const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { BASELINE, readCandidate, assertHostedWindows, prepareInputs } = require('./inputs.cjs');
const { writeEvidence, portableSnapshot, assertPreserved } = require('./files.cjs');
const { InstalledDesktop } = require('./desktop.cjs');
const {
  createProvider,
  seedBaseline,
  assertLegacyData,
  exerciseUpgradedUI,
} = require('./fixture.cjs');

function installerCommand(file, args, run, label) {
  const result = spawnSync(file, args, {
    encoding: 'utf8',
    windowsHide: true,
    windowsVerbatimArguments: true,
    timeout: 240000,
  });
  fs.appendFileSync(
    path.join(run, 'process.log'),
    `${label}: status=${result.status}\n${result.stdout || ''}${result.stderr || ''}${result.error || ''}\n`,
  );
  assert.equal(result.error, undefined, `${label} could not run.`);
  assert.equal(result.status, 0, `${label} failed.`);
}

async function runUpgrade() {
  const root = path.resolve(__dirname, '../..');
  const { profile, candidate } = assertHostedWindows(root);
  const expected = readCandidate();
  // Exercise the real default APPDATA profile and registered install location.
  // This is intentionally forbidden outside a fresh hosted Windows VM.
  assert.equal(fs.existsSync(profile), false, 'Refusing to touch a pre-existing Racall profile.');
  const run = path.join(root, 'test-results', 'upgrade-' + Date.now());
  const destination = path.join(run, 'installed');
  const data = path.join(profile, 'knowledge');
  fs.mkdirSync(run, { recursive: true });
  const errors = [];
  const checks = [];
  const provider = createProvider();
  const desktop = new InstalledDesktop(path.join(destination, 'Racall.exe'), profile, run, errors);
  let providerStarted = false;
  try {
    const inputs = await prepareInputs(run, candidate, expected);
    checks.push(
      `Exact public ${BASELINE.version} and verified ${expected.version} installer hashes`,
    );
    writeEvidence(run, 'inputs.json', {
      baseline: BASELINE,
      candidate: expected,
      manifest: inputs.manifest,
    });
    installerCommand(
      inputs.old,
      ['/S', '/LANGUAGE=1049', '/D=' + destination],
      run,
      `Install published ${BASELINE.version}`,
    );
    const endpoint = await provider.start();
    providerStarted = true;
    const oldRuntime = await desktop.launch(BASELINE.version);
    const fixture = await seedBaseline(desktop, endpoint);
    assert.equal(provider.errors.length, 0, provider.errors.join('\n'));
    assert.ok(
      provider.calls.length >= 7,
      'Fixture chat, Research and Studio must use the real baseline backend.',
    );
    await desktop.close();
    const before = portableSnapshot(data);
    writeEvidence(run, 'before-upgrade.json', before);
    checks.push(
      'Published 0.3 creates real notes, chat, versioned sources, saved Research, Studio and trash',
    );
    // No /D: the new installer must discover the existing registered install location.
    installerCommand(
      inputs.next,
      ['/S', '/LANGUAGE=1033'],
      run,
      `Upgrade in place to candidate ${expected.version}`,
    );
    assertPreserved(before, data);
    assert.equal(
      JSON.parse(
        fs.readFileSync(path.join(destination, 'resources', 'installer-language.json'), 'utf8'),
      ).locale,
      'en',
    );
    checks.push('In-place installer reuses previous directory and preserves authoritative bytes');
    const callsBeforeLaunch = provider.calls.length;
    const nextRuntime = await desktop.launch(expected.version);
    await assertLegacyData(desktop, fixture);
    assert.equal(
      provider.calls.length,
      callsBeforeLaunch,
      'Opening upgraded data must not replay inference.',
    );
    const material = await exerciseUpgradedUI(desktop, fixture);
    const callsBeforeRestart = provider.calls.length;
    assert.ok(
      callsBeforeRestart > callsBeforeLaunch,
      'Explicit new Studio generation must reach the fixture.',
    );
    checks.push('Old chat/report citations retain exact historical source and both original files');
    checks.push('Baseline 0.3 Studio material, completed job and Markdown export remain unchanged');
    checks.push(
      'Earlier report opens and exports in the new library; EN/RU, light/dark and note-only Studio work',
    );
    await desktop.close();
    assertPreserved(before, data);
    const completed = portableSnapshot(data);
    await desktop.launch(expected.version);
    await assertLegacyData(desktop, fixture);
    const restored = await desktop.api(`/notebooks/${fixture.notebook.id}/materials/${material}`);
    assert.equal(restored.answer.validated, true);
    await desktop.page.waitForTimeout(1000);
    assert.equal(
      provider.calls.length,
      callsBeforeRestart,
      'Restart must not replay completed requests.',
    );
    assert.equal(provider.errors.length, 0, provider.errors.join('\n'));
    assert.equal(errors.length, 0, errors.join('\n'));
    await desktop.capture('04-upgraded-restart.png');
    await desktop.close();
    assertPreserved(completed, data);
    checks.push(
      'Full upgraded restart preserves old/new materials, settings and native theme without inference replay',
    );
    const uninstaller = fs
      .readdirSync(destination)
      .find((name) => /^Uninstall.*\.exe$/i.test(name));
    assert.ok(uninstaller, 'Upgraded uninstaller is missing.');
    installerCommand(
      path.join(destination, uninstaller),
      ['/S', '_?=' + destination],
      run,
      `Uninstall upgraded ${expected.version}`,
    );
    assert.equal(fs.existsSync(desktop.executable), false, 'Upgraded application was not removed.');
    const after = assertPreserved(completed, data);
    writeEvidence(run, 'after-uninstall.json', after);
    checks.push('Uninstall removes the upgraded application and preserves all fixture knowledge');
    const result = {
      passed: true,
      platform: 'win',
      arch: 'x64',
      baseline: BASELINE,
      candidate: expected,
      harnessSource: process.env.GITHUB_SHA,
      profile,
      oldRuntime,
      nextRuntime,
      checks,
      preservedFiles: Object.keys(before).length,
      syntheticProviderCalls: provider.calls.length,
      errors,
      publication: expected.publication,
    };
    writeEvidence(run, 'result.json', result);
    console.log(JSON.stringify(result));
  } catch (error) {
    await desktop.capture('failure.png').catch(() => {});
    writeEvidence(run, 'result.json', {
      passed: false,
      checks,
      error: error.stack || String(error),
      baseline: BASELINE,
      candidate: expected,
    });
    throw error;
  } finally {
    await desktop.close().catch(() => {});
    if (providerStarted) await provider.close();
    if (fs.existsSync(path.join(data, 'backend.log')))
      fs.copyFileSync(path.join(data, 'backend.log'), path.join(run, 'backend.log'));
  }
}

module.exports = { runUpgrade };
