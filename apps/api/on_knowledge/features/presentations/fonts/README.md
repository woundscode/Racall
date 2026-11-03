# Presentation fonts

DejaVu Sans regular and bold, version 2.37, are redistributed unchanged from the
[official DejaVu release](https://github.com/dejavu-fonts/dejavu-fonts/releases/tag/version_2_37).
The accompanying `LICENSE` contains the original copyright and permission notices;
`provenance.json` records the download URL and SHA-256 of the archive and files.

PDF exports embed the used TrueType glyphs. SVG previews embed a small font subset
for each page, and do not make font requests to the network. Their measurement and
line breaks use these exact font files, including Cyrillic glyphs.

PPTX exports contain editable text and shapes, with the DejaVu Sans font family
specified. The font is not embedded into PPTX: the presentation application may
substitute another font if DejaVu Sans is unavailable on that computer. Text stays
editable, but exact typography should be checked in the recipient's application.
Use the PDF export for fixed appearance. PowerPoint/LibreOffice rendering and
native packaging are separate acceptance checks, not implied by an XML readback.
