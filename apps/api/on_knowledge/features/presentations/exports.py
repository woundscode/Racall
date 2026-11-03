"""Local exports from a saved presentation; these functions never call a provider."""

from html import escape
from io import BytesIO

from pptx import Presentation as PowerPoint
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.util import Pt
from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .font_support import font_name, svg_font
from .layout import HEIGHT, WIDTH, Page, layout_presentation
from .schemas import Presentation


def _pdf(document: Presentation, pages: list[Page]) -> bytes:
    output = BytesIO()
    canvas = Canvas(output, pagesize=(WIDTH, HEIGHT), invariant=True, pageCompression=1)
    canvas.setTitle(document.title)
    canvas.setAuthor("Racall")
    for page in pages:
        canvas.setFillColor(HexColor(page.background))
        canvas.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        canvas.setFillColor(HexColor("#F97316"))
        canvas.rect(0, HEIGHT - 6, WIDTH, 6, fill=1, stroke=0)
        for line in page.lines:
            canvas.setFillColor(HexColor(line.color))
            canvas.setFont(font_name(line.bold), line.size)
            canvas.drawString(line.x, HEIGHT - line.baseline, line.text)
        canvas.showPage()
    canvas.save()
    return output.getvalue()


def _rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value.removeprefix("#"))


def _pptx(document: Presentation, pages: list[Page]) -> bytes:
    output = BytesIO()
    deck = PowerPoint()
    deck.slide_width, deck.slide_height = Pt(WIDTH), Pt(HEIGHT)
    deck.core_properties.title = document.title
    deck.core_properties.author = "Racall"
    for page in pages:
        slide = deck.slides.add_slide(deck.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = _rgb(page.background)
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Pt(WIDTH), Pt(6))
        accent.fill.solid()
        accent.fill.fore_color.rgb = _rgb("#F97316")
        accent.line.fill.background()
        for line in page.lines:
            box = slide.shapes.add_textbox(
                Pt(line.x), Pt(line.baseline - line.size), Pt(WIDTH - line.x - 20), Pt(line.size * 1.5)
            )
            frame = box.text_frame
            frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
            frame.word_wrap = False
            frame.auto_size = MSO_AUTO_SIZE.NONE
            frame.vertical_anchor = MSO_ANCHOR.TOP
            paragraph = frame.paragraphs[0]
            paragraph.text = line.text
            paragraph.font.name = "DejaVu Sans"
            paragraph.font.size = Pt(line.size)
            paragraph.font.bold = line.bold
            paragraph.font.color.rgb = _rgb(line.color)
            paragraph.space_before = paragraph.space_after = Pt(0)
            paragraph.line_spacing = 1.0
        slide.notes_slide.notes_text_frame.text = page.notes
    deck.save(output)
    return output.getvalue()


def export_presentation(document: Presentation, citations: list[dict], format: str) -> bytes:
    if format not in {"pdf", "pptx"}:
        raise ValueError("Unsupported presentation export format.")
    if document.stage != "slides":
        raise ValueError("Generate slides from the outline before exporting.")
    pages = layout_presentation(document, citations)
    return _pdf(document, pages) if format == "pdf" else _pptx(document, pages)


def _svg(page: Page) -> str:
    styles = []
    for bold in (False, True):
        text = "".join(line.text for line in page.lines if line.bold == bold)
        if text:
            data = svg_font(text, bold)
            styles.append(
                f"@font-face{{font-family:Racall; font-weight:{700 if bold else 400}; src:url(data:font/ttf;base64,{data}) format('truetype');}}"
            )
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">',
        "<style>" + "".join(styles) + "</style>",
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{page.background}"/>',
        f'<rect width="{WIDTH}" height="6" fill="#F97316"/>',
    ]
    for line in page.lines:
        elements.append(
            f'<text x="{line.x}" y="{line.baseline}" font-family="Racall" font-size="{line.size}" font-weight="{700 if line.bold else 400}" fill="{line.color}" style="font-kerning:none;font-variant-ligatures:none" xml:space="preserve">{escape(line.text)}</text>'
        )
    return "".join(elements) + "</svg>"


def presentation_preview(document: Presentation, citations: list[dict]) -> list[str]:
    return [_svg(page) for page in layout_presentation(document, citations)]
