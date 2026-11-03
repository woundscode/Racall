// Pure host/input/preservation checks. Never invoke an installer or Electron.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const { createHash } = require('node:crypto');
const {
  BASELINE,
  readCandidate,
  verifyProvenance,
  assertHostedWindows,
  verifyManifest,
  verifyCandidateFiles,
} = require('./inputs.cjs');
const { compareSnapshots } = require('./files.cjs');

// Deliberately synthetic IDs/hashes; these never identify a real build or installer.
const policy = { version: '0.4.0-beta.1', publication: 'hold' };
const candidateEnv = {
  RACALL_UPGRADE_SOURCE: 'a'.repeat(40),
  RACALL_UPGRADE_RUN: '101',
  RACALL_UPGRADE_ARTIFACT: '202',
  RACALL_UPGRADE_SIZE: '1000001',
  RACALL_UPGRADE_SHA256: 'b'.repeat(64),
};
const candidate = () => readCandidate(candidateEnv, policy);
const repository = { id: 1385819102, full_name: 'woundscode/Racall' };

test('candidate identities are required, strict and bound to checkout release policy', () => {
  const value = candidate();
  assert.equal(value.version, policy.version);
  assert.equal(value.publication, 'hold');
  assert.equal(value.name, 'Racall-0.4.0-beta.1-win-x64.exe');
  assert.equal(value.run, 101);
  assert.equal(value.artifact, 202);
  assert.equal(value.sha256, candidateEnv.RACALL_UPGRADE_SHA256);
  for (const key of Object.keys(candidateEnv)) {
    assert.throws(() => readCandidate({ ...candidateEnv, [key]: '' }, policy), key);
    assert.throws(() => readCandidate({ ...candidateEnv, [key]: '../other' }, policy), key);
  }
  for (const invalid of ['-1', '1.5', '0', '1e3', '9007199254740992'])
    assert.throws(() => readCandidate({ ...candidateEnv, RACALL_UPGRADE_RUN: invalid }, policy));
  assert.throws(() => readCandidate({ ...candidateEnv, RACALL_UPGRADE_SIZE: '1' }, policy));
  assert.throws(() => readCandidate(candidateEnv, { ...policy, version: '../escape' }));
  assert.throws(() => readCandidate(candidateEnv, { ...policy, version: BASELINE.version }));
  assert.throws(() => readCandidate(candidateEnv, { ...policy, publication: 'unknown' }));
});

test('candidate provenance requires the exact successful native build and unexpired artifact', () => {
  const expected = candidate();
  const run = {
    id: expected.run,
    head_sha: expected.source,
    path: '.github/workflows/build.yml',
    event: 'workflow_dispatch',
    status: 'completed',
    conclusion: 'success',
    repository,
    head_repository: repository,
  };
  const artifact = {
    id: expected.artifact,
    name: 'Racall-win-x64',
    expired: false,
    workflow_run: { id: expected.run, head_sha: expected.source },
  };
  verifyProvenance(run, artifact, expected);
  const renamed = { ...repository, full_name: 'renamed-owner/renamed-repository' };
  verifyProvenance({ ...run, repository: renamed, head_repository: renamed }, artifact, expected);
  for (const key of ['id', 'head_sha', 'path', 'event', 'status', 'conclusion'])
    assert.throws(() => verifyProvenance({ ...run, [key]: 'other' }, artifact, expected), key);
  for (const key of ['repository', 'head_repository'])
    assert.throws(() =>
      verifyProvenance({ ...run, [key]: { ...repository, id: 999 } }, artifact, expected),
    );
  for (const key of ['repository', 'head_repository'])
    assert.throws(() =>
      verifyProvenance({ ...run, [key]: { full_name: repository.full_name } }, artifact, expected),
    );
  for (const change of [
    { id: 999 },
    { name: 'Racall-win-arm64' },
    { expired: true },
    { workflow_run: { ...artifact.workflow_run, id: 999 } },
    { workflow_run: { ...artifact.workflow_run, head_sha: 'c'.repeat(40) } },
  ])
    assert.throws(() => verifyProvenance(run, { ...artifact, ...change }, expected));
});

const root = path.resolve('fixture-workspace');
const temp = path.resolve('fixture-runner-temp');
const env = {
  CI: 'true',
  GITHUB_ACTIONS: 'true',
  RUNNER_ENVIRONMENT: 'github-hosted',
  GITHUB_REPOSITORY: 'SleepyCodeMeow/Racall',
  GITHUB_REPOSITORY_ID: String(repository.id),
  RUNNER_OS: 'Windows',
  RUNNER_ARCH: 'X64',
  GITHUB_WORKSPACE: root,
  RUNNER_TEMP: temp,
  APPDATA: path.resolve('fixture-appdata'),
  RACALL_UPGRADE_CANDIDATE_DIR: path.join(temp, 'candidate'),
};
const host = { platform: 'win32', arch: 'x64' };

test('installation guards reject local, self-hosted, wrong-architecture and escaped paths', () => {
  assert.ok(assertHostedWindows(root, env, host).profile.endsWith('OpenNotebook'));
  assert.ok(assertHostedWindows(root, { ...env, GITHUB_REPOSITORY: repository.full_name }, host));
  assert.throws(() => assertHostedWindows(root, { ...env, GITHUB_REPOSITORY_ID: '999' }, host));
  assert.throws(() =>
    assertHostedWindows(root, { ...env, GITHUB_REPOSITORY: '../escaped/repository' }, host),
  );
  for (const key of [
    'CI',
    'GITHUB_ACTIONS',
    'RUNNER_ENVIRONMENT',
    'GITHUB_REPOSITORY',
    'GITHUB_REPOSITORY_ID',
    'RUNNER_OS',
    'RUNNER_ARCH',
    'GITHUB_WORKSPACE',
    'RUNNER_TEMP',
    'APPDATA',
    'RACALL_UPGRADE_CANDIDATE_DIR',
  ]) {
    assert.throws(() => assertHostedWindows(root, { ...env, [key]: '' }, host), key);
  }
  assert.throws(() =>
    assertHostedWindows(root, { ...env, RUNNER_ENVIRONMENT: 'self-hosted' }, host),
  );
  assert.throws(() => assertHostedWindows(root, env, { ...host, arch: 'arm64' }));
  assert.throws(() =>
    assertHostedWindows(root, { ...env, RACALL_UPGRADE_CANDIDATE_DIR: root }, host),
  );
});

test('the candidate manifest cannot substitute another source, package or released state', () => {
  const CANDIDATE = candidate();
  const manifest = {
    version: CANDIDATE.version,
    source: CANDIDATE.source,
    platform: 'win',
    arch: 'x64',
    publication: CANDIDATE.publication,
    packages: [{ name: CANDIDATE.name, size: CANDIDATE.size, sha256: CANDIDATE.sha256 }],
  };
  const verify = (value) => verifyManifest(value, CANDIDATE);
  verify(manifest);
  assert.throws(() =>
    verify({
      ...manifest,
      publication: CANDIDATE.publication === 'approved' ? 'hold' : 'approved',
    }),
  );
  for (const key of ['version', 'source', 'platform', 'arch', 'publication'])
    assert.throws(() => verify({ ...manifest, [key]: 'other' }));
  assert.throws(() =>
    verify({
      ...manifest,
      packages: [{ ...manifest.packages[0], sha256: BASELINE.sha256 }],
    }),
  );
  assert.throws(() =>
    verify({ ...manifest, packages: [...manifest.packages, manifest.packages[0]] }),
  );
  for (const change of [{ name: '../other.exe' }, { size: 2 }, { extra: true }])
    assert.throws(() =>
      verify({ ...manifest, packages: [{ ...manifest.packages[0], ...change }] }),
    );
});

test('artifact contents, manifest and checksum list must all match the explicit candidate', async (t) => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'racall-upgrade-contract-'));
  t.after(() => {
    assert.equal(path.dirname(directory), path.resolve(os.tmpdir()));
    assert.ok(path.basename(directory).startsWith('racall-upgrade-contract-'));
    fs.rmSync(directory, { recursive: true, force: true });
  });
  const bytes = Buffer.alloc(1000001, 'synthetic test data');
  const expected = readCandidate(
    { ...candidateEnv, RACALL_UPGRADE_SHA256: createHash('sha256').update(bytes).digest('hex') },
    policy,
  );
  const manifest = {
    version: expected.version,
    source: expected.source,
    platform: 'win',
    arch: 'x64',
    publication: expected.publication,
    packages: [{ name: expected.name, size: expected.size, sha256: expected.sha256 }],
  };
  const installer = path.join(directory, expected.name);
  fs.writeFileSync(installer, bytes);
  fs.writeFileSync(path.join(directory, 'BUILD.json'), JSON.stringify(manifest));
  fs.writeFileSync(
    path.join(directory, 'SHA256SUMS.txt'),
    `${expected.sha256}  ${expected.name}\n`,
  );
  const result = await verifyCandidateFiles(directory, expected);
  assert.equal(result.next, installer);
  assert.deepEqual(result.manifest, manifest);
  bytes[0] ^= 1;
  fs.writeFileSync(installer, bytes);
  await assert.rejects(() => verifyCandidateFiles(directory, expected), /SHA-256/);
  bytes[0] ^= 1;
  fs.writeFileSync(installer, bytes);
  fs.appendFileSync(path.join(directory, 'SHA256SUMS.txt'), '\nunexpected package');
  await assert.rejects(() => verifyCandidateFiles(directory, expected));
});

test('preservation permits new records but rejects lost or modified old files', () => {
  const before = { 'notes/old.md': { size: 4, sha256: 'old-hash' } };
  compareSnapshots(before, { ...before, 'materials/new.json': { size: 10, sha256: 'new-hash' } });
  assert.throws(() => compareSnapshots(before, {}));
  assert.throws(() => compareSnapshots(before, { 'notes/old.md': { size: 4, sha256: 'changed' } }));
  assert.throws(() => compareSnapshots({}, {}));
});
