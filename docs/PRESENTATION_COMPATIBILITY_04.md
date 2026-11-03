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
- Actual LibreOffice conversion and visual acceptance remain pending until the workflow and review have completed for the candidate commit.
