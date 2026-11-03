# 0.4 Beta dependency review — 2026-11-03

The original review below is retained as historical evidence. See the
[compatible-update follow-up](#compatible-update-follow-up) for the current
dependency versions and remaining release assessment.

The targeted Electron update to **44.9.1** in `d38bbf9` addresses the compromised
CA advisory described below. **This is not a clean dependency audit.** npm reported
20 vulnerable packages after the patch: 16 moderate, 3 high and 1 critical,
down from 21 before it. These counts describe packages, not distinct advisories.
Other resolved packages were unchanged.

This review covers the critical/high npm findings and their observed reachability.
It does not certify Python dependencies, all Chromium/native components, every
moderate finding or the application's overall security. The subsequent six-platform
rebuild passed its [native checks](VERIFICATION_04_NATIVE_2026-11-03.md). The isolated
official Windows x64 runtime probe below supplies separate version evidence;
application test success does not close the remaining advisories.

## Packaging and network boundary

[`next.config.ts`](../apps/web/next.config.ts) uses `output: 'export'` and
`images.unoptimized: true`. The Python backend serves the generated files through
[`StaticFiles`](../apps/api/on_knowledge/app.py); a Next.js server is not packaged.
The inspected pre-patch Windows `app.asar` contained 19 entries and no
`node_modules` entries. Compiled frontend assets and the Electron runtime are
still distributed; a `devDependencies` label is not a security exemption.

[`backend.cjs`](../apps/desktop/backend.cjs) starts the Python service on
`127.0.0.1`. Its only main-process `fetch` found during this review requests the
service's HTTP `/api/settings` endpoint. Provider requests are handled by Python.
[`security.cjs`](../apps/desktop/security.cjs) restricts production connections to
the UI origin, denies permission requests and opens external links in the system
browser. [`window.cjs`](../apps/desktop/window.cjs) enables sandboxing and context
isolation and disables Node integration. These controls limit the observed
paths; they do not prove an affected dependency harmless. Development uses a live
Next server and a different CSP path, so the production assessment does not cover it.

## Electron: targeted CA fix

Electron 44.4.5 was affected by
[GHSA-jr5w-w6x2-84p9](https://github.com/electron/electron/security/advisories/GHSA-jr5w-w6x2-84p9).
An attacker with a certificate from compromised intermediates and an opportunity
to intercept TLS traffic could impersonate a server. The advisory identifies
**44.9.1** as the first fixed release in the 44 branch;
[its release notes](https://github.com/electron/electron/releases/tag/v44.9.1)
confirm the mitigation for Chromium and Node networking.

All six Windows/macOS/Linux x64/ARM64 ZIPs were present in the official release.
The GitHub asset digests matched the published
[SHA-256 manifest](https://github.com/electron/electron/releases/download/v44.9.1/SHASUMS256.txt).
The Windows x64 archive was also downloaded into an isolated ignored directory.
Its 158,389,896 bytes independently hashed to
`41bd7900bd42d0f49110a81617876137041fbbf473466920248ddb076349ef91`, matching the
manifest before extraction or execution. The other five assets received metadata
checks only. The dependency patch closes this advisory at the selected-version
level; rebuilt application packages still require verification. It does not
establish that every embedded component is patched.

## Remaining critical/high findings

| Package and dependency path | Observed exposure and remaining risk |
| --- | --- |
| `next@16.3.6` | The two critical advisories concern the live [Image Optimization API with SVG](https://github.com/vercel/next.js/security/advisories/GHSA-2464-fhr4-w9xw) and [`use cache` functions returning typed arrays](https://github.com/vercel/next.js/security/advisories/GHSA-673q-mjm6-r5xr). These server paths are absent from the packaged static application. No `use cache`, Server Actions or `images.remotePatterns` configuration was found. This also limits the reported [Server Actions DoS](https://github.com/vercel/next.js/security/advisories/GHSA-p3m5-59mp-jv5r) and [image SSRF](https://github.com/vercel/next.js/security/advisories/GHSA-cjq9-62q9-8jv4) paths. Development/build dependencies remain unpatched. Both critical advisories identify 16.4.1 as fixed. |
| `next > sharp@0.35.4` | [GHSA-wq5f-xc86-pv6w](https://github.com/lovell/sharp/security/advisories/GHSA-wq5f-xc86-pv6w) concerns SVG decoding through librsvg on glibc Linux. No sharp runtime module is packaged; document imports use Python. Malicious SVG inputs processed during a build could still expose CI. The advisory fixes this in sharp 0.35.5. |
| `next > postcss > source-map-js@1.2.1`; `@tailwindcss/postcss > postcss` or `@tailwindcss/node > source-map-js@1.2.1` | Malformed indexed source maps can block the build process's event loop. No application source-map parser was found, and the module is not packaged. Untrusted build maps remain relevant. See the upstream [fix](https://github.com/7rulnik/source-map-js/commit/cf76580) and [1.2.2 release](https://github.com/7rulnik/source-map-js/releases/tag/v1.2.2). |
| `electron > @electron/get > undici@7.29.1`; `electron-builder > app-builder-lib > @electron/rebuild > node-gyp > undici@6.28.1` | These npm copies serve build/download tooling, which contacts external servers. **Embedded Undici is also 7.29.1 in both the old 44.4.5 runtime and the verified official 44.9.1 Windows x64 runtime.** Updating an npm copy does not replace the embedded implementation. This remains unresolved. |

The verified archive was run only with `ELECTRON_RUN_AS_NODE=1` and
`-p JSON.stringify(process.versions)`, without launching Racall, an installer or a
browser profile. It reported Electron **44.9.1**, Node **24.22.0**, Chromium
**152.0.7977.167** and Undici **7.29.1**. That Undici version remains inside the
advisories' affected ranges; no backported fix was verified. The CA patch must not
be described as an Undici fix.

Undici's high findings include
[lost custom TLS callbacks](https://github.com/nodejs/undici/security/advisories/GHSA-2m5v-pch6-74hx),
[redirect/cache poisoning](https://github.com/nodejs/undici/security/advisories/GHSA-4w7w-5xrc-9h26),
[TLS renegotiation DoS](https://github.com/nodejs/undici/security/advisories/GHSA-qrxm-fqhp-jwvm)
and [malformed response encoding DoS](https://github.com/nodejs/undici/security/advisories/GHSA-xjj6-f33q-929c).
No custom TLS callbacks or cache interceptors were found in desktop code. Its
observed HTTP fetch targets its own backend, limiting malicious remote-peer
scenarios in the normal application flow. This does not remove the external
download tooling's exposure or establish that an affected embedded version is safe.
Relevant fixes are Undici 6.29.1 / 7.30.1 for these installed major versions.

## Outstanding verification

- Confirm runtime versions in the rebuilt application packages. Keep embedded
  Undici open: the official Windows x64 runtime probe confirms 7.29.1, and there
  is no verified fix for it in this update.
- Keep the audit findings visible in release readiness records even though all
  six rebuilt packages passed their native application checks.
- Address the remaining dependencies through separate, scoped updates and fresh
  audits. No automatic broad dependency update was made by this review.

Local evidence is retained in ignored `test-results/native04-dependency-audit.json`,
`native04-dependency-paths.json`, `native04-dependency-triage.json`,
`electron-v44.9.1-release.json` and `electron-v44.9.1-SHASUMS256.txt`. The original
audit and baseline runtime probe describe the pre-patch state. The separate
`test-results/electron-runtime-44.9.1/verification.json` and `versions.json`
record the verified archive and post-patch runtime probe.

## Compatible-update follow-up

A fresh audit reproduced the 20-package baseline. Targeted compatible updates
and a clean `npm ci` now leave **15 moderate, 0 high and 0 critical** npm findings.
The full audit still exits with code 1; no advisory, dependency category or audit
level was suppressed. The remaining findings are the propagation of
**GHSA-g3hv-75wg-m249**, discussed below. This is not a zero-finding audit.

| Dependency | Previous | Updated |
| --- | --- | --- |
| Electron | 44.9.1 | 44.10.1 |
| Next.js, its environment package and native SWC packages | 16.3.6 | 16.4.4 |
| sharp and its platform packages | 0.35.4 | 0.35.5 |
| sharp's libvips packages | 1.3.3 | 1.3.4 |
| source-map-js | 1.2.1 | 1.2.2 |
| fast-uri | 3.1.8 | 3.1.9 |
| npm Undici through `@electron/get` | 7.29.1 | 7.30.1 |
| npm Undici through `node-gyp` | 6.28.1 | 6.29.1 |

These versions address the earlier Next, sharp, source-map-js and Undici
advisories. fast-uri 3.1.9 addresses the upstream
[scheme-decoding](https://github.com/fastify/fast-uri/security/advisories/GHSA-w74x-v6f9-j3xg)
and [host-canonicalization](https://github.com/fastify/fast-uri/security/advisories/GHSA-wjr9-j795-jxcr)
advisories. electron-builder remains 26.15.6: changing it to the available 26.18.1
would still retain the incompatible old minimatch chains. No forced downgrade,
major upgrade, broad override or application version change was made.

### Embedded runtime verified independently

The [official Electron 44.10.1 release](https://github.com/electron/electron/releases/tag/v44.10.1)
lists all six required Windows/macOS/Linux x64/ARM64 ZIPs, and each has an entry
in its [official SHA-256 manifest](https://github.com/electron/electron/releases/download/v44.10.1/SHASUMS256.txt).
The Windows x64 ZIP was downloaded into an isolated directory and independently
verified before extraction: 157,982,210 bytes, SHA-256
`5099bdc11c6a78edff35851491c1f8228a1c2e844e1b376eee219402c42c6011`.
The other five assets received availability/checksum-entry checks, not execution.

Both that isolated binary and the installed npm runtime were probed using
`ELECTRON_RUN_AS_NODE=1`, without starting Racall or a browser profile. They report
Electron **44.10.1**, Node **24.22.1**, Chromium **152.0.7977.169** and embedded
Undici **7.30.1**. The embedded Undici therefore reaches the
[upstream security-fix release](https://github.com/nodejs/undici/releases/tag/v7.30.1);
this conclusion does not rely on the separate npm copy. Rebuilt application
checks are still required for the updated dependency set.

### Remaining minimatch assessment

The [primary advisory](https://github.com/isaacs/minimatch/security/advisories/GHSA-g3hv-75wg-m249)
describes attacker-controlled pattern amplification at `optimizationLevel >= 2`,
and names 11.0.1 as fixed. npm marks `<11.0.1` as affected. The installed tree
contains 10.2.6 at the root, 9.0.9 under `@electron/universal`, 5.1.9 under
`filelist`, and 3.1.5 under `@electron/asar`, `dir-compare` and `glob`. All remain
visible in the audit. Replacing every old callable API with minimatch 11's named
exports would risk breaking packaging; npm's suggested electron-builder downgrade
to 20.23.1 was not applied.

The scoped reachability review found:

- `app-builder-lib/out/fileMatcher.js` constructs matchers with `{ dot: true }`;
  minimatch 10 defaults to optimization level 1. Universal's matcher calls pass
  `{ matchBase: true }`, and its minimatch 9 also defaults to level 1. No enabling
  of level 2 was found in these builder chains. The inspected 3/5 implementations
  do not contain the advisory's `firstPhasePreProcess` implementation.
- Patterns come from repository-owned packaging configuration and builder
  defaults. Racall does not pass notebook text, imported documents or user search
  strings into these matchers. No minimatch imports were found in application
  source, and the previously generated static client contained no minimatch
  markers. The earlier packaged archive also contained no npm module tree.
- The current targets use separate architectures, not Universal macOS builds,
  and NSIS rather than Squirrel. Some reported dependent paths are consequently
  installed tooling that these release targets do not execute.

**Proposed release disposition:** retain this named moderate build-tool finding
as a bounded, documented exception, rather than claiming it fixed. Keep packaging
patterns in reviewed repository configuration; do not accept user-supplied glob
patterns or enable level 2 without reassessing this advisory. The existing native
build jobs have a 60-minute timeout. Recheck the final package contents and revisit
the exception when builder dependencies or glob options change. This assessment
does not cover arbitrary untrusted build configurations or future advisories.

### Validation and evidence

`npm ci` completed, `npm ls --all` passed, and actual installed package manifests
were checked against the lockfile. The selected runtime passed the headless probe.
The lockfile retains every platform-specific SWC entry and all six supported
sharp targets. A preliminary incremental install left older physical package
files despite a current npm tree report; the clean install corrected that, and
the final filesystem check confirms the versions above.

Evidence is retained in ignored `test-results/dependency04-closure-audit-before.json`,
`dependency04-closure-audit-after.json`, `dependency04-installed-tree.json`,
`dependency04-installed-runtime.json`, `electron-v44.10.1-six-assets.json`,
`electron-v44.10.1-SHASUMS256.txt` and
`electron-runtime-44.10.1/{verification,versions}.json`.
Before publication, rerun the audit and check current upstream releases: the
[Next 16.4.4 notes](https://github.com/vercel/next.js/releases/tag/v16.4.4) explicitly
announce a separate November security release. The selected versions resolve the
published findings reviewed here, not undisclosed or subsequently released ones.
