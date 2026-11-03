const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { Readable, Transform } = require('node:stream');
const { pipeline } = require('node:stream/promises');
const REPOSITORY = Object.freeze(require('../../apps/shared/repository.json'));

// Published 0.3 hashes are recorded in docs/VERIFICATION_03_RELEASE_2026-10-25.md.
// The candidate is supplied explicitly after its native build; never guess or use latest.
const BASELINE = Object.freeze({
  version: '0.3.0-beta.1',
  source: '839d5219d9269071c07e61497061905cc3f707e9',
  name: 'Racall-0.3.0-beta.1-win-x64.exe',
  size: 153279432,
  sha256: 'b968cb0f91f0ddfba481853c2949e0978d7d603a9634b18be6d76fde91dc1eb9',
});

function positiveInteger(value, label) {
  assert.match(value || '', /^[1-9]\d*$/, `${label} must be an explicit positive integer.`);
  const number = Number(value);
  assert.ok(Number.isSafeInteger(number), `${label} exceeds the safe integer range.`);
  return number;
}

function readCandidate(env = process.env, policy = require('../../apps/shared/release.json')) {
  assert.match(policy.version, /^\d+\.\d+\.\d+(?:-[a-z0-9]+(?:\.[a-z0-9]+)*)?$/);
  assert.notEqual(policy.version, BASELINE.version, 'The candidate must differ from the baseline.');
  assert.ok(['hold', 'approved'].includes(policy.publication));
  assert.match(env.RACALL_UPGRADE_SOURCE || '', /^[a-f0-9]{40}$/, 'Pin the candidate source SHA.');
  assert.match(env.RACALL_UPGRADE_SHA256 || '', /^[a-f0-9]{64}$/, 'Pin the installer SHA-256.');
  const size = positiveInteger(env.RACALL_UPGRADE_SIZE, 'Installer size');
  assert.ok(size > 1000000, 'The candidate is too small to be a Racall installer.');
  return Object.freeze({
    version: policy.version,
    source: env.RACALL_UPGRADE_SOURCE,
    run: positiveInteger(env.RACALL_UPGRADE_RUN, 'Build run ID'),
    artifact: positiveInteger(env.RACALL_UPGRADE_ARTIFACT, 'Artifact ID'),
    publication: policy.publication,
    name: `Racall-${policy.version}-win-x64.exe`,
    size,
    sha256: env.RACALL_UPGRADE_SHA256,
  });
}

function verifyProvenance(run, artifact, candidate) {
  assert.equal(run.id, candidate.run);
  assert.equal(run.head_sha, candidate.source);
  assert.equal(run.path, '.github/workflows/build.yml');
  assert.ok(
    ['push', 'workflow_dispatch'].includes(run.event),
    'Use a source build, not a PR merge.',
  );
  assert.equal(run.status, 'completed');
  assert.equal(run.conclusion, 'success');
  assert.equal(run.repository?.id, REPOSITORY.id, 'Build belongs to another repository.');
  assert.equal(
    run.head_repository?.id,
    REPOSITORY.id,
    'Build source belongs to another repository.',
  );
  assert.equal(artifact.id, candidate.artifact);
  assert.equal(artifact.name, 'Racall-win-x64');
  assert.equal(artifact.expired, false);
  assert.equal(artifact.workflow_run?.id, candidate.run);
  assert.equal(artifact.workflow_run?.head_sha, candidate.source);
}

function assertHostedWindows(root, env = process.env, host = process) {
  assert.equal(env.CI, 'true', 'Upgrade checks require CI.');
  assert.equal(env.GITHUB_ACTIONS, 'true', 'Upgrade checks require GitHub Actions.');
  assert.equal(env.RUNNER_ENVIRONMENT, 'github-hosted', 'Self-hosted machines are not disposable.');
  assert.equal(env.GITHUB_REPOSITORY_ID, String(REPOSITORY.id));
  assert.match(env.GITHUB_REPOSITORY || '', /^[a-z\d-]+\/[a-z\d_.-]+$/i);
  assert.equal(env.RUNNER_OS, 'Windows');
  assert.equal(env.RUNNER_ARCH, 'X64');
  assert.equal(host.platform, 'win32');
  assert.equal(host.arch, 'x64');
  assert.ok(env.GITHUB_WORKSPACE && path.isAbsolute(env.GITHUB_WORKSPACE));
  assert.equal(path.resolve(env.GITHUB_WORKSPACE), root);
  assert.ok(env.APPDATA && path.isAbsolute(env.APPDATA));
  assert.ok(env.RUNNER_TEMP && path.isAbsolute(env.RUNNER_TEMP));
  assert.ok(env.RACALL_UPGRADE_CANDIDATE_DIR);
  const candidate = path.resolve(env.RACALL_UPGRADE_CANDIDATE_DIR);
  const relative = path.relative(path.resolve(env.RUNNER_TEMP), candidate);
  assert.ok(relative && !relative.startsWith('..') && !path.isAbsolute(relative));
  return { candidate, profile: path.join(env.APPDATA, 'OpenNotebook') };
}

function verifyManifest(manifest, candidate) {
  assert.equal(manifest.version, candidate.version);
  assert.equal(manifest.source, candidate.source);
  assert.equal(manifest.platform, 'win');
  assert.equal(manifest.arch, 'x64');
  assert.equal(manifest.publication, candidate.publication);
  assert.deepEqual(manifest.packages, [
    { name: candidate.name, size: candidate.size, sha256: candidate.sha256 },
  ]);
}

async function verifyFile(file, expected) {
  assert.equal(fs.statSync(file).size, expected.size, 'Unexpected installer size.');
  const digest = createHash('sha256');
  for await (const chunk of fs.createReadStream(file)) digest.update(chunk);
  assert.equal(digest.digest('hex'), expected.sha256, 'Unexpected installer SHA-256.');
}

async function verifyCandidateFiles(directory, candidate) {
  const manifest = JSON.parse(fs.readFileSync(path.join(directory, 'BUILD.json'), 'utf8'));
  verifyManifest(manifest, candidate);
  const next = path.join(directory, candidate.name);
  await verifyFile(next, candidate);
  const sums = fs.readFileSync(path.join(directory, 'SHA256SUMS.txt'), 'utf8');
  assert.equal(sums.trim(), `${candidate.sha256}  ${candidate.name}`);
  return { next, manifest };
}

async function prepareInputs(run, directory, candidate) {
  const { next, manifest } = await verifyCandidateFiles(directory, candidate);
  const old = path.join(run, BASELINE.name);
  const url = `https://github.com/${REPOSITORY.full_name}/releases/download/v${BASELINE.version}/${BASELINE.name}`;
  const response = await fetch(url, { signal: AbortSignal.timeout(120000) });
  assert.equal(response.status, 200, `Published ${BASELINE.version} installer is unavailable.`);
  let bytes = 0;
  const bound = new Transform({
    transform(chunk, _encoding, callback) {
      bytes += chunk.length;
      callback(
        bytes > BASELINE.size ? new Error('Published installer exceeded pinned size.') : null,
        chunk,
      );
    },
  });
  await pipeline(
    Readable.fromWeb(response.body),
    bound,
    fs.createWriteStream(old, { flags: 'wx' }),
  );
  await verifyFile(old, BASELINE);
  return { old, next, manifest };
}

module.exports = {
  BASELINE,
  readCandidate,
  verifyProvenance,
  assertHostedWindows,
  verifyManifest,
  verifyCandidateFiles,
  prepareInputs,
};
