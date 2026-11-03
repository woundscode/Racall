const assert = require('node:assert/strict');
const { createRequire } = require('node:module');
const path = require('node:path');
const { test } = require('node:test');
const { FileMatcher } = require('app-builder-lib/out/fileMatcher');

const consumers = ['app-builder-lib', '@electron/universal'];

for (const consumer of consumers) {
  const localRequire = createRequire(require.resolve(consumer));
  const { Minimatch } = localRequire('minimatch');

  test(`${consumer} bounds globstar preprocessing at the configured expansion limit`, () => {
    // Six segments make only 64 rows in the vulnerable versions: a bounded
    // regression for GHSA-g3hv-75wg-m249, not a CPU/memory exhaustion test.
    const pattern =
      Array.from({ length: 6 }, (_, i) => `**/../p${i}/q${i}`).join('/') + '/file.txt';
    const matcher = new Minimatch(pattern, { optimizationLevel: 2, braceExpandMax: 4 });
    assert.ok(matcher.globParts.length <= 4, 'Preprocessing exceeded braceExpandMax');
  });
}

// Model the entries and traversal order of a small package source tree. The
// filter is the real builder filter, including directory/partial matches.
const tree = [
  'apps/desktop/main.cjs',
  'apps/desktop/.config.json',
  'apps/desktop/cache/ignored.tmp',
  'apps/shared/release.json',
  'apps/shared/i18n/en.json',
  'apps/shared/i18n/ru.json',
  'apps/web/out/index.html',
  'apps/web/out/_next/static/app.js',
  'apps/web/out/_next/static/app.js.map',
  'apps/web/.env',
  'notes/private.md',
  'assets/logo.png',
  'assets/logo.jpg',
  'assets/logo.svg',
  'assets/.hidden.png',
  'package.json',
];

function selectFiles(patterns) {
  const source = path.resolve('packaging-fixture');
  const matcher = new FileMatcher(
    source,
    path.resolve('package-output'),
    (value) => value,
    patterns,
  );
  const filter = matcher.createFilter();
  return tree.filter((relative) => {
    const parts = relative.split('/');
    return parts.every((_, index) =>
      filter(path.join(source, ...parts.slice(0, index + 1)), {
        isDirectory: () => index < parts.length - 1,
      }),
    );
  });
}

test('builder includes declared application files and traverses their parent directories', () => {
  assert.deepEqual(selectFiles(['apps/desktop/**', 'package.json', 'apps/shared/**']), [
    'apps/desktop/main.cjs',
    'apps/desktop/.config.json',
    'apps/desktop/cache/ignored.tmp',
    'apps/shared/release.json',
    'apps/shared/i18n/en.json',
    'apps/shared/i18n/ru.json',
    'package.json',
  ]);
});

test('builder excludes nested caches while retaining dotfiles and selected JSON resources', () => {
  assert.deepEqual(
    selectFiles(['apps/desktop/**', '!apps/desktop/cache/**', 'apps/shared/**/*.json']),
    [
      'apps/desktop/main.cjs',
      'apps/desktop/.config.json',
      'apps/shared/release.json',
      'apps/shared/i18n/en.json',
      'apps/shared/i18n/ru.json',
    ],
  );
});

test('builder handles brace extensions and negated source maps', () => {
  assert.deepEqual(selectFiles(['apps/web/out/**', '!**/*.map', 'assets/*.{png,jpg}']), [
    'apps/web/out/index.html',
    'apps/web/out/_next/static/app.js',
    'assets/logo.png',
    'assets/logo.jpg',
    'assets/.hidden.png',
  ]);
});

test('builder expands literal directory mappings and normalizes Windows pattern separators', () => {
  assert.deepEqual(selectFiles(['apps\\shared', 'package.json']), [
    'apps/shared/release.json',
    'apps/shared/i18n/en.json',
    'apps/shared/i18n/ru.json',
    'package.json',
  ]);
});

test('universal allowlist matching retains basename, braces, dotfile and path semantics', () => {
  const { minimatch } = createRequire(require.resolve('@electron/universal'))('minimatch');
  const cases = [
    ['native/addon.node', '*.node', true],
    ['native/addon.dll', '*.node', false],
    ['Resources/app.asar', '**/*.{asar,node}', true],
    ['Resources/app.asar.unpacked/addon.node', '**/*.{asar,node}', true],
    ['Resources/.hidden.node', '*.node', false],
    ['Contents/Info.plist', '**/Info.plist', true],
    ['Contents/Other.plist', '**/Info.plist', false],
  ];
  for (const [file, pattern, expected] of cases) {
    assert.equal(minimatch(file, pattern, { matchBase: true }), expected, `${file}: ${pattern}`);
  }
});

test('legacy asar and directory filters retain their callable minimatch API', () => {
  for (const consumer of ['@electron/asar', 'dir-compare']) {
    const minimatch = createRequire(require.resolve(consumer))('minimatch');
    assert.equal(typeof minimatch, 'function', `${consumer} requires the callable export`);
    assert.equal(minimatch('native/addon.node', '*.node', { matchBase: true }), true);
    assert.equal(minimatch('native/addon.dll', '*.node', { matchBase: true }), false);
  }
});

test('legacy glob still expands and reads files used by packaging tools', () => {
  const glob = createRequire(require.resolve('@electron/asar'))('glob');
  assert.deepEqual(
    glob.sync('{package.json,LICENSE}', { cwd: path.resolve(__dirname, '..'), nodir: true }).sort(),
    ['LICENSE', 'package.json'],
  );
});
