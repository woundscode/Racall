# 0.4 Beta acceptance checklist

Publication: **hold**. Development authorized 2026-11-03; public 0.3 assets remain
unchanged. [Plan](PLAN_04.md) · [Presentation guide](PRESENTATIONS.md)

## Implemented and checked locally

The [final local follow-up](VERIFICATION_04_FOLLOWUP_2026-11-03.md) covers the
revised deterministic assembly: 585 Python tests and the rebuilt Windows x64
presentation, Studio and persistence scenarios passed. The earlier record
retains its original scope.

- [x] Python-owned typed deck, bounded output and canonical source references.
- [x] Saved outline review releases the worker before a separate explicit job.
- [x] Pinned source context and outline revision; idempotency and restart without replay.
- [x] Revision conflicts, preserved original, portable drafts and stale-save rejection.
- [x] Slide title/bullet/notes editing, reorder/delete and light/dark templates.
- [x] English/Russian interface strings and TypeScript validation.
- [x] Real PPTX/PDF export tests, embedded PDF/SVG Cyrillic fonts and editable PPTX text.
- [x] English/Russian sample PDFs rendered and visually inspected.
- [x] All original Python tests pass alongside new presentation tests.
- [x] Windows x64 packaged presentations, Studio and persistence scenarios.
- [x] Frozen Windows backend includes rendering resources, fonts and dependency licenses.

Measured results and limitations: [initial verification](VERIFICATION_04_2026-11-03.md)
and [final local follow-up](VERIFICATION_04_FOLLOWUP_2026-11-03.md).

## Release gates

- [x] Final deterministic-assembly checks: exact approved text, slide IDs and
      citations, preserved edited review states, no provider/embedding calls, and
      offline **Create slides / Оформить слайды** followed by export.
- [x] Automated desktop acceptance across the 0.4 release platforms.
- [x] Six native builds: Windows/macOS/Linux, x64 and ARM64, with export smoke checks
      ([native candidate verification](VERIFICATION_04_NATIVE_2026-11-03.md)).
- [x] Installed Windows x64 0.3 → 0.4 upgrade preserves original
      notebooks/materials/revisions and knowledge after uninstall
      ([hosted-runner result](VERIFICATION_04_NATIVE_2026-11-03.md)).
- [ ] Actual PowerPoint/LibreOffice rendering checked; font substitution limits recorded.
- [ ] Bounded real-provider EN/RU presentation evaluation with independent factual review.
- [ ] Resolve remaining dependency findings for release; the targeted Electron CA
      fix does not close the [other advisories](DEPENDENCY_REVIEW_04_2026-11-03.md).
- [ ] Final release notes/screenshots, checksums and owner publication approval.

Automated fixtures establish request, storage and file-format behavior. They do
not certify model factual reliability. The [November 3 live Ollama check](MODEL_EVALUATION_04_2026-11-03.md)
completed the English workflow and exports, but independent review found an
unsupported speaker-note claim accepted by the critic in the earlier
two-generation workflow. The run stopped on low
available RAM before Russian. The [follow-up](MODEL_EVALUATION_04_FOLLOWUP_2026-11-03.md)
ran both languages without a resource stop, with at least 4.57 GB sampled free RAM.
English passed independent review; Russian failed an unsupported statement in
the initial outline. A separate corrected copy passed offline export and restart,
which does not erase the live failure. The EN/RU factual gate remains incomplete;
prior 0.3 false positives remain relevant. No WSL/Docker load or model download was used.

Python now assembles the approved saved outline without a second writer or
critic. This removes that rewrite step; it does not establish factual reliability
of initial outlines or turn user-edited content into model-validated content.
