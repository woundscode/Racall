# Presentation compatibility checks for 0.4

This gate opens Racall's exported PPTX files in real LibreOffice Impress on a disposable GitHub Ubuntu 24.04 runner. It checks the resulting PDFs and the editable presentation after an office round trip. It does not install Office on the developer's computer or start an AI model.

The automated result and visual review are separate. A successful workflow proves the checks described below passed for the recorded LibreOffice version and fonts. It does **not** mean Microsoft PowerPoint was tested, or that every office version and font substitution behaves identically.

## Run and reproduce

Run **Check presentation compatibility in LibreOffice** from GitHub Actions on the candidate branch. Relevant pushes to `codex/0.4-presentations` also run the gate; it neither publishes nor changes a release.

The workflow installs `libreoffice-impress`, `poppler-utils` and `fonts-dejavu-core` only on its temporary runner. Python dependencies come from `uv.lock`. Each conversion uses its own LibreOffice user profile to prevent interference from another office process. The command-line switches and filter names follow the official [LibreOffice startup documentation](https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html) and [conversion filter table](https://help.libreoffice.org/latest/en-US/text/shared/guide/convertfilters.html).

On an existing Linux environment with those tools already available:

```sh
uv sync --frozen
uv run python scripts/test.py tests/test_presentation_compatibility.py -q
uv run python scripts/check_presentation_compatibility.py --output test-results/compatibility-review-01
```

Use a fresh output directory for every attempt. The runner records exact LibreOffice, Poppler and Python versions, installed package versions, selected font paths and SHA-256 hashes, commit SHA and workflow run ID. The report also shows whether the system's regular/bold DejaVu Sans files match the fonts bundled with Racall. An unexpected font family fails the run. The Ubuntu package repository can receive updates, so the recorded package manifest, rather than the runner label alone, identifies a result's environment.

## Coverage and assertions

Six deterministic, synthetic cases cover English and Russian in both light and dark templates, plus two schema-boundary cases (160-character title, 220-character bullet and 1,200-character speaker notes). Boundary cases deliberately use narrow unbroken tokens to exercise wrapping at the maximum permitted length while still fitting the supported layout. They do not imply every maximum-length combination fits: production layout rejects overflowing content.

The normal cases use the same synthetic source facts and meeting note as the live 0.4 evaluation fixtures. They include source IDs, version hashes, page locations, exact source excerpts, an edited slide, speaker notes and printable notes/source appendices. These are export fixtures, not a new assessment of AI factual accuracy.

For each case the script:

1. Exports the actual production PPTX and PDF; derives expected pages from the shared production layout.
2. Converts PPTX to PDF with LibreOffice's `impress_pdf_Export` filter.
3. Converts PPTX to editable ODP and back to PPTX, checking slide dimensions, editable text shapes and speaker-note text against the original. Rasterized replacement pictures fail this text-only fixture gate.
4. Opens that returned PPTX in LibreOffice and renders it to PDF again.
5. Extracts text bounding boxes from all three PDFs with Poppler, checks every expected word, slide dimensions, page count, out-of-page text and overlapping word rectangles. Unicode compatibility normalization permits equivalent ligatures; whitespace and extraction order do not cause a false failure.
6. Renders every PDF page to a 96-DPI PNG and records font information for visual review.

This catches missing text and many clipping/overlap defects. Text geometry alone cannot prove correct colors, glyph appearance, layering or overall visual quality. The unit tests deliberately damage content, dimensions, geometry and notes to confirm the checker rejects them; they do not substitute for running LibreOffice.

## Review the evidence

Download the `presentation-compatibility` workflow artifact. `result.json` must say `passed: true`; `environment.json` and `runner-packages.txt` identify the rendering environment. `commands.log` records the exact commands and converter output. Each case includes the source PPTX, returned PPTX/ODP, expected content, PDFs, bounding-box XML, font lists and page PNGs.

Before calling the compatibility gate complete, visually inspect **every page** in `reference`, `office` and `roundtrip-render` for each case. Compare the office-rendered pages with Racall's reference: titles and bullets must remain readable, Russian glyphs intact, themes correct, and notes/source appendices complete. Check the maximum-length cases particularly carefully. Record the workflow run, commit, reviewer, pages reviewed and any differences in the release acceptance record.

The machine report deliberately leaves `visual_review: pending` and `microsoft_powerpoint: not tested`. A human or agent review must supply the separate visual evidence. A missing Office installation on the user's computer is not silently counted as a successful PowerPoint test.

## Implementation log

- Separated synthetic fixture generation, pure content/geometry checks and external tool execution so a contributor can inspect each boundary independently.
- Added rejection tests before the gate implementation, then checked all six fixtures through the production exporter locally.
- Added a narrowly scoped workflow that preserves artifacts even when a conversion or check fails. No existing application layout, logo or theme was changed for this gate.
- On 2026-11-03, [workflow run 41662366119](https://github.com/woundscode/Racall/actions/runs/41662366119) passed all six cases at commit `4abe9c1063cd313c8dc22125501b3fea5a458b0a`: 22 pages in each of the reference, direct office and round-trip PDF paths, with editable text and speaker notes preserved. The recorded environment was LibreOffice 24.2.7.2, Poppler 24.02.0 and Python 3.12.3. Ubuntu's DejaVu Sans files differed from the bundled font hashes; this result therefore covers those recorded system font versions, not identical embedded PPTX fonts.
- Artifact `13241229044` has ZIP SHA-256 `ab8ad8ad247ad7c075dfaecc33e3568009471f5c2bc0b4bc7ad1a0853fd635a0`.

## Candidate acceptance, 2026-11-03

[Workflow run 41662832717](https://github.com/woundscode/Racall/actions/runs/41662832717) passed again at candidate commit `3c22f580ad09078917c86075adc70bf17628faa0`. Artifact `13241708950` has ZIP SHA-256 `4518ed342abbfe94edd593d71d6f70cf074d032df9ec7d9355afd3c2ac2df8e4`. All 66 rendered PNG files are byte-identical to the first run, and the exporter, layout, fonts, schemas, fixtures and compatibility runner were unchanged between those commits.

The root coding agent separately inspected all six contact sheets covering all 66 page images (three columns: reference, LibreOffice, returned PPTX). The review accepted readable text, correct Cyrillic glyphs and light/dark themes, complete notes/source appendices, and no visible clipping or overlapping content. The deliberate truncated sentence at the 1,200-character boundary fixture appears equally in all three paths and is fixture content, not lost export text. This was an agent visual review, not a claim that the user manually opened the files in Office.

The LibreOffice compatibility gate is accepted for this candidate and recorded environment. The immutable machine reports still say `visual_review: pending`; the review above and the separate local `visual-review.json` record provide the complementary visual evidence. Microsoft PowerPoint remains **not tested**.
