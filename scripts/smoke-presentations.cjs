/** Real Python editing/drafts/exports with a synthetic saved deck; no inference. */
const { _electron: electron, expect } = require('@playwright/test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { randomUUID } = require('node:crypto');
const { captureWindow } = require('./smoke/capture.cjs');
const root = path.resolve(__dirname, '..');
const run = path.join(root, 'test-results', 'presentations-desktop-' + Date.now());
const data = path.join(run, 'data');
fs.mkdirSync(data, { recursive: true });
const en = require('../apps/shared/locales/en.json');
const ru = require('../apps/shared/locales/ru.json');
const errors = [];
let app;
async function launch() {
  const env = {
    ...process.env,
    OPENNOTEBOOK_DATA_DIR: data,
    OPENNOTEBOOK_SMOKE_MODE: '1',
    PYTHON_KEYRING_BACKEND: 'keyring.backends.null.Keyring',
  };
  for (const key of [
    'ELECTRON_RUN_AS_NODE',
    'OPENNOTEBOOK_API_KEY',
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY',
    'OLLAMA_API_KEY',
  ])
    delete env[key];
  app = await electron.launch({
    ...(process.env.OPENNOTEBOOK_TEST_EXE
      ? { executablePath: process.env.OPENNOTEBOOK_TEST_EXE, args: ['--disable-gpu'] }
      : { args: [root, '--disable-gpu'] }),
    env,
    timeout: 60000,
  });
  const page = await app.firstWindow({ timeout: 60000 });
  page.setDefaultTimeout(15000);
  page.on('pageerror', (error) => errors.push(error.message));
  await app.evaluate(({ BrowserWindow }) => {
    const window = BrowserWindow.getAllWindows()[0];
    window.webContents.setBackgroundThrottling(false);
    window.setSize(1180, 820);
  });
  await page.locator('.navigation').waitFor();
  assert.equal(
    await app.evaluate(({ app }) => app.getPath('userData')),
    path.join(data, 'electron-profile'),
  );
  return page;
}
async function close() {
  const previous = app;
  app = undefined;
  if (!previous) return;
  await previous
    .evaluate(({ BrowserWindow }) =>
      BrowserWindow.getAllWindows().forEach((window) => window.destroy()),
    )
    .catch(() => {});
  await previous.close().catch(() => {});
}
async function api(page, endpoint, method = 'GET', body) {
  return page.evaluate(
    async ({ endpoint, method, body }) => {
      const response = await fetch('/api' + endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      return response.status === 204 ? null : response.json();
    },
    { endpoint, method, body },
  );
}
async function openMaterial(page, title, locale = en, editable = true) {
  await page.getByRole('tab', { name: locale['nav.artifacts'], exact: true }).click();
  await page
    .locator('.material-library .note-tabs')
    .getByRole('button', { name: title, exact: true })
    .click();
  await expect(page.locator('.presentation-editor')).toBeVisible();
  if (editable)
    await expect(page.getByLabel(locale['presentation.deckTitle'], { exact: true })).toBeEnabled();
}
function seed(notebook, note) {
  const quote = 'Marigold launches on October 18. The pilot has three stations.';
  const citation = {
    id: 'fixture-evidence',
    source_id: note.id,
    note_id: note.id,
    kind: 'note',
    version: note.revision,
    title: note.title,
    quote,
    number: 1,
    location: {
      element: 0,
      type: 'text',
      line_start: 1,
      line_end: 1,
      offset_start: 0,
      offset_end: quote.length,
    },
  };
  const presentation = {
    schema_version: 1,
    revision: 1,
    stage: 'slides',
    title: 'Marigold fixture',
    language: 'en',
    template: 'light',
    slides: [
      {
        id: 'slide-one',
        layout: 'title',
        title: 'Marigold',
        bullets: ['Launch: October 18'],
        notes: 'The pilot has three stations.',
        evidence_ids: [citation.id],
        review_state: 'generated',
      },
      {
        id: 'slide-two',
        layout: 'bullets',
        title: 'Pilot',
        bullets: ['Three stations'],
        notes: '',
        evidence_ids: [citation.id],
        review_state: 'generated',
      },
      {
        id: 'slide-three',
        layout: 'section',
        title: 'Next steps',
        bullets: [],
        notes: '',
        evidence_ids: [citation.id],
        review_state: 'generated',
      },
    ],
  };
  const directory = path.join(data, 'notebooks', notebook.id, 'materials');
  fs.mkdirSync(directory, { recursive: true });
  const id = randomUUID();
  const material = {
    id,
    job_id: id,
    kind: 'presentation',
    title: presentation.title,
    created_at: new Date().toISOString(),
    body: '# Marigold',
    answer: {
      claims: [],
      citations: [citation],
      validated: true,
      mode: 'presentation',
      message: '',
    },
    presentation,
  };
  fs.writeFileSync(path.join(directory, material.id + '.json'), JSON.stringify(material));
  const outline = structuredClone(material);
  outline.id = randomUUID();
  outline.job_id = outline.id;
  outline.kind = 'presentation_outline';
  outline.presentation.stage = 'outline';
  outline.title = outline.presentation.title = 'Outline fixture';
  fs.writeFileSync(path.join(directory, outline.id + '.json'), JSON.stringify(outline));
  return material;
}
async function download(page, format) {
  const file = path.join(run, `edited.${format}`);
  await app.evaluate(({ BrowserWindow }, file) => {
    globalThis.__presentationDownload = '';
    BrowserWindow.getAllWindows()[0].webContents.session.once('will-download', (_event, item) => {
      item.setSavePath(file);
      item.once('done', (_event, state) => {
        globalThis.__presentationDownload = state;
      });
    });
  }, file);
  await page
    .getByRole('button', {
      name: en['presentation.exportFormat'].replace('{format}', format.toUpperCase()),
      exact: true,
    })
    .click();
  await expect.poll(() => app.evaluate(() => globalThis.__presentationDownload)).toBe('completed');
  const bytes = fs.readFileSync(file);
  assert.ok(bytes.length > 1000);
  assert.equal(
    bytes.subarray(0, format === 'pdf' ? 4 : 2).toString(),
    format === 'pdf' ? '%PDF' : 'PK',
  );
}
(async () => {
  try {
    let page = await launch();
    const notebook = await api(page, '/notebooks', 'POST', { title: 'Presentations acceptance' });
    const base = `/notebooks/${notebook.id}`;
    const note = await api(page, base + '/notes', 'POST', {
      title: 'Pilot source',
      body: 'Marigold launches on October 18. The pilot has three stations.',
    });
    const material = seed(notebook, note);
    const endpoint = base + `/materials/${material.id}/presentation`;
    await page.reload();
    await openMaterial(page, material.title);
    await expect(page.locator('.presentation-preview img')).toBeVisible();
    await expect
      .poll(() =>
        page
          .locator('.presentation-preview img')
          .evaluate((img) => img.complete && img.naturalWidth > 0),
      )
      .toBe(true);
    await page.getByLabel(en['presentation.deckTitle'], { exact: true }).fill('Edited Marigold');
    await page
      .getByLabel(en['presentation.slideTitle'], { exact: true })
      .first()
      .fill('Launch overview');
    await expect
      .poll(async () => (await api(page, endpoint + '/draft'))?.presentation.title)
      .toBe('Edited Marigold');
    await expect(page.getByRole('button', { name: 'Export PPTX', exact: true })).toBeDisabled();
    await close();
    page = await launch();
    await openMaterial(page, material.title);
    await expect(page.getByText(en['presentation.recovered'], { exact: true })).toBeVisible();
    await expect(page.getByLabel(en['presentation.deckTitle'], { exact: true })).toHaveValue(
      'Edited Marigold',
    );
    await page.getByRole('button', { name: en['presentation.save'], exact: true }).click();
    await expect
      .poll(async () => (await api(page, base + `/materials/${material.id}`)).presentation.revision)
      .toBe(2);
    assert.equal(await api(page, endpoint + '/draft'), null);
    const saved = await api(page, base + `/materials/${material.id}`);
    assert.equal(saved.presentation.slides[0].review_state, 'edited');
    assert.equal(saved.answer.validated, false);
    // Leave Reports immediately, before the 500 ms draft debounce can run.
    await page
      .locator('[data-slide-id="slide-one"]')
      .getByLabel(en['presentation.notes'], { exact: true })
      .fill('Immediate navigation edit');
    await page.getByRole('tab', { name: en['nav.chat'], exact: true }).click();
    await expect(page.getByRole('tab', { name: en['nav.chat'], exact: true })).toHaveAttribute(
      'aria-selected',
      'true',
    );
    await expect(page.getByRole('tabpanel', { name: en['nav.chat'], exact: true })).toBeVisible();
    assert.equal(
      (await api(page, base + `/materials/${material.id}`)).presentation.slides[0].notes,
      'Immediate navigation edit',
    );
    await openMaterial(page, 'Edited Marigold');
    await page.getByRole('button', { name: en['presentation.moveUp'], exact: true }).nth(1).click();
    await expect(page.locator('.presentation-slide').first()).toHaveAttribute(
      'data-slide-id',
      'slide-two',
    );
    await page
      .getByRole('button', { name: en['presentation.removeSlide'], exact: true })
      .last()
      .click();
    await page.getByRole('button', { name: en['presentation.save'], exact: true }).click();
    await expect
      .poll(async () => (await api(page, base + `/materials/${material.id}`)).presentation.revision)
      .toBe(4);
    assert.equal(
      (await api(page, base + `/materials/${material.id}`)).presentation.slides.length,
      2,
    );
    await page
      .getByLabel(en['presentation.deckTitle'], { exact: true })
      .fill('Discard this change');
    page.once('dialog', (dialog) => dialog.accept());
    await page.getByRole('button', { name: en['presentation.discard'], exact: true }).click();
    await expect(page.getByLabel(en['presentation.deckTitle'], { exact: true })).toHaveValue(
      'Edited Marigold',
    );
    await download(page, 'pptx');
    await download(page, 'pdf');
    await page.locator('.presentation-editor .material-heading').scrollIntoViewIfNeeded();
    await captureWindow(app, path.join(run, 'presentation-editor-light-en.png'));
    await page.locator('.presentation-preview').scrollIntoViewIfNeeded();
    await captureWindow(app, path.join(run, 'presentation-light-en.png'));
    // UI submission semantics use synthetic responses; backend generation has its own integration tests.
    const submissions = [];
    const fixtureJobs = [];
    await page.route(`**/api${base}/jobs`, async (route) => {
      if (route.request().method() === 'POST') {
        const request = route.request().postDataJSON();
        submissions.push(request);
        const job = {
          id: randomUUID(),
          request_id: request.request_id,
          outline_id: request.outline_id,
          outline_revision: request.outline_revision,
          kind: 'presentation',
          status: 'running',
          stage: 'assembling',
          steps: [],
          question: '',
          title: 'Generated fixture',
          language: 'en',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          result: { material_id: material.id },
        };
        fixtureJobs.unshift(job);
        return route.fulfill({ json: job, status: 202 });
      }
      return route.fulfill({ json: fixtureJobs });
    });
    await openMaterial(page, 'Outline fixture');
    const generate = page.getByRole('button', {
      name: en['presentation.generateSlides'],
      exact: true,
    });
    await generate.click();
    await expect.poll(() => submissions.length).toBe(1);
    await expect(generate).toBeDisabled();
    await openMaterial(page, 'Edited Marigold');
    await openMaterial(page, 'Outline fixture', en, false);
    await expect(generate).toBeDisabled();
    await expect(
      page.locator(`.presentation-editor [data-job-id="${fixtureJobs[0].id}"]`),
    ).toHaveAttribute('data-status', 'running');
    assert.equal(submissions.length, 1, 'Reopening an outline must recover its existing job');
    fixtureJobs[0].status = fixtureJobs[0].stage = 'completed';
    await expect(
      page.locator(`.presentation-editor [data-job-id="${fixtureJobs[0].id}"]`),
    ).toHaveAttribute('data-status', 'completed');
    await page.getByLabel(en['presentation.deckTitle'], { exact: true }).fill('Revised outline');
    await page
      .locator(`.presentation-editor [data-job-id="${fixtureJobs[0].id}"]`)
      .getByRole('button', { name: en['jobs.openResult'], exact: true })
      .click();
    await expect(page.locator('.presentation-editor')).toHaveAttribute(
      'data-material-id',
      material.id,
    );
    await openMaterial(page, 'Revised outline');
    await expect(generate).toBeEnabled();
    await generate.click();
    await expect.poll(() => submissions.length).toBe(2);
    assert.equal(submissions[0].outline_revision, 1);
    assert.equal(submissions[1].outline_revision, 2);
    assert.notEqual(submissions[0].request_id, submissions[1].request_id);
    fixtureJobs[0].status = fixtureJobs[0].stage = 'completed';
    await expect(
      page.locator(`.presentation-editor [data-job-id="${fixtureJobs[0].id}"]`),
    ).toHaveAttribute('data-status', 'completed');
    await page.unroute(`**/api${base}/jobs`);
    await page.getByRole('button', { name: 'Settings', exact: true }).click();
    await page.getByLabel('Interface language').selectOption('ru');
    await page.getByRole('radio', { name: ru['settings.themeDark'], exact: true }).click();
    await page.getByRole('button', { name: ru['common.back'], exact: true }).click();
    await openMaterial(page, 'Edited Marigold', ru);
    await page
      .getByLabel(ru['presentation.deckTitle'], { exact: true })
      .fill('Презентация «Мэриголд»');
    await page.getByLabel(ru['presentation.template'], { exact: true }).selectOption('dark');
    const darkPreview = page.waitForResponse((response) =>
      response.url().endsWith(endpoint + '/preview?revision=5'),
    );
    await page.getByRole('button', { name: ru['presentation.save'], exact: true }).click();
    await expect
      .poll(async () => (await api(page, base + `/materials/${material.id}`)).presentation.revision)
      .toBe(5);
    assert.ok((await darkPreview).ok());
    await expect(page.locator('.presentation-preview img')).toBeVisible();
    await expect
      .poll(() =>
        page
          .locator('.presentation-preview img')
          .evaluate((img) => img.complete && img.naturalWidth > 0),
      )
      .toBe(true);
    await app.evaluate(({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].setSize(1000, 680));
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    await page.locator('.presentation-editor .material-heading').scrollIntoViewIfNeeded();
    await captureWindow(app, path.join(run, 'presentation-editor-dark-ru.png'));
    await page.locator('.presentation-preview').scrollIntoViewIfNeeded();
    await captureWindow(app, path.join(run, 'presentation-dark-ru.png'));
    assert.deepEqual(errors, []);
    assert.equal(
      (await api(page, base + '/jobs')).length,
      0,
      'Editing/export must make no model jobs',
    );
    fs.writeFileSync(
      path.join(run, 'result.json'),
      JSON.stringify(
        {
          passed: true,
          errors,
          modelCalls: 0,
          syntheticJobSubmissions: submissions.length,
          checks: [
            'real Python saved revisions',
            'draft survives restart',
            'edited claims invalidate verification',
            'reorder/delete',
            'discard restores saved revision',
            'PPTX/PDF binary download',
            'safe SVG preview',
            'immediate Reports tab exit persists changes',
            'immediate job-result exit persists changes',
            'existing generation job recovers on outline reopen',
            'reopening does not duplicate generation',
            'explicit revised outline submission (mock response)',
            'EN/light and RU/dark',
            'minimum window',
            'isolated profile',
          ],
        },
        null,
        2,
      ),
    );
    console.log(JSON.stringify({ passed: true, artifacts: run }));
  } catch (error) {
    if (app) await captureWindow(app, path.join(run, 'failure.png')).catch(() => {});
    throw error;
  } finally {
    await close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
