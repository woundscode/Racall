"""Bundled, redistributable fonts shared by presentation measurement and renderers."""

from base64 import b64encode
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from threading import Lock

from fontTools import subset
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIRECTORY = Path(__file__).with_name("fonts")
_registration_lock = Lock()


def font_path(bold: bool = False) -> Path:
    return FONT_DIRECTORY / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")


def font_name(bold: bool = False) -> str:
    name = "RacallSansBold" if bold else "RacallSans"
    with _registration_lock:
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(font_path(bold))))
    return name


def text_width(text: str, size: float, bold: bool = False) -> float:
    font = pdfmetrics.getFont(font_name(bold))
    for character in text:
        if ord(character) not in font.face.charToGlyph:
            raise ValueError(f"The presentation font cannot display U+{ord(character):04X}.")
    return pdfmetrics.stringWidth(text, font.fontName, size)


@lru_cache(maxsize=64)
def _subset_font(characters: str, bold: bool) -> str:
    options = subset.Options()
    options.drop_tables += ["FFTM"]
    options.recalc_timestamp = False
    options.hinting = False
    with subset.load_font(str(font_path(bold)), options) as font:
        subsetter = subset.Subsetter(options)
        subsetter.populate(text=characters)
        subsetter.subset(font)
        output = BytesIO()
        font.save(output)
    return b64encode(output.getvalue()).decode("ascii")


def svg_font(text: str, bold: bool) -> str:
    """Subset only the used characters; never request an external browser font."""
    return _subset_font("".join(sorted(set(text))), bold)
