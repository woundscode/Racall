"""Run real LibreOffice conversions in isolated profiles and retain review evidence."""

import hashlib
import json
import os
import platform
import shutil
import subprocess
import traceback
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from on_knowledge.features.presentations.exports import export_presentation
from on_knowledge.features.presentations.layout import layout_presentation
from pptx import Presentation as PowerPoint

from .checks import verify_bbox, verify_roundtrip
from .fixtures import Case, cases


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class Tools:
    def __init__(self, output: Path):
        self.output = output
        for command in ("soffice", "pdftotext", "pdftoppm", "pdffonts", "fc-match"):
            assert shutil.which(command), f"Required independent renderer tool is missing: {command}"

    def run(self, command: list[str], *, timeout=120) -> str:
        result = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        with (self.output / "commands.log").open("a", encoding="utf-8") as log:
            log.write(json.dumps(command, ensure_ascii=False) + "\n")
            log.write(f"exit={result.returncode}\n{result.stdout}{result.stderr}\n")
        assert result.returncode == 0, f"Command failed: {command[0]}: {result.stderr}"
        return result.stdout + result.stderr

    def convert(self, source: Path, destination: Path, format: str) -> Path:
        destination.mkdir()
        profile = destination / "profile"
        self.run(
            [
                "soffice",
                f"-env:UserInstallation={profile.resolve().as_uri()}",
                "--headless",
                "--nologo",
                "--nodefault",
                "--norestore",
                "--convert-to",
                format,
                "--outdir",
                str(destination),
                str(source),
            ]
        )
        output = destination / (source.stem + "." + format.split(":", 1)[0])
        assert output.is_file() and output.stat().st_size > 1000, f"No real office output: {output}"
        return output


def environment(tools: Tools, root: Path) -> dict:
    fonts = []
    for style, name in (("Book", "DejaVuSans.ttf"), ("Bold", "DejaVuSans-Bold.ttf")):
        lines = tools.run(
            ["fc-match", "-f", "%{family}\n%{file}\n", f"DejaVu Sans:style={style}"]
        ).splitlines()
        assert "DejaVu Sans" in lines[0].split(","), "Required DejaVu Sans font was substituted"
        file = Path(lines[1])
        bundled = root / "apps/api/on_knowledge/features/presentations/fonts" / name
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        fonts.append(
            {
                "style": style,
                "family": lines[0],
                "file": str(file),
                "sha256": digest,
                "matches_bundled": digest == hashlib.sha256(bundled.read_bytes()).hexdigest(),
            }
        )
    return {
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "libreoffice": tools.run(["soffice", "--version"]).strip(),
        "poppler": tools.run(["pdftotext", "-v"]).strip(),
        "fonts": fonts,
    }


def inspect_pdf(tools: Tools, pdf: Path, expected: list[list[str]]) -> dict:
    bbox = pdf.with_suffix(".bbox.xml")
    tools.run(["pdftotext", "-bbox-layout", "-enc", "UTF-8", str(pdf), str(bbox)])
    tools.run(["pdftoppm", "-r", "96", "-png", str(pdf), str(pdf.parent / (pdf.stem + "-page"))])
    font_output = tools.run(["pdffonts", str(pdf)])
    pdf.with_suffix(".fonts.txt").write_text(font_output, encoding="utf-8")
    return verify_bbox(ET.parse(bbox).getroot(), expected)


def run_case(tools: Tools, case: Case) -> dict:
    folder = tools.output / case.name
    folder.mkdir()
    expected = [
        [line.text for line in page.lines] for page in layout_presentation(case.document, case.citations)
    ]
    write_json(
        folder / "expected.json",
        {"presentation": case.document.model_dump(), "citations": case.citations, "pages": expected},
    )
    pptx = folder / "input.pptx"
    pptx.write_bytes(export_presentation(case.document, case.citations, "pptx"))
    reference = folder / "reference"
    reference.mkdir()
    original_pdf = reference / "racall.pdf"
    original_pdf.write_bytes(export_presentation(case.document, case.citations, "pdf"))
    reference_check = inspect_pdf(tools, original_pdf, expected)
    direct = tools.convert(pptx, folder / "office", "pdf:impress_pdf_Export")
    direct_check = inspect_pdf(tools, direct, expected)
    odp = tools.convert(pptx, folder / "odp", "odp:impress8")
    returned = tools.convert(odp, folder / "roundtrip", "pptx:Impress MS PowerPoint 2007 XML")
    editable_check = verify_roundtrip(PowerPoint(pptx), PowerPoint(returned))
    returned_pdf = tools.convert(returned, folder / "roundtrip-render", "pdf:impress_pdf_Export")
    returned_check = inspect_pdf(tools, returned_pdf, expected)
    result = {
        "name": case.name,
        "passed": True,
        "reference": reference_check,
        "libreoffice_pdf": direct_check,
        "office_roundtrip": editable_check,
        "roundtrip_pdf": returned_check,
    }
    write_json(folder / "case-result.json", result)
    return result


def run(output: Path, root: Path) -> dict:
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / "result.json").exists(), (
        "Choose a fresh evidence directory; do not reuse old results"
    )
    result = {
        "passed": False,
        "source": os.environ.get("GITHUB_SHA", "local-uncommitted"),
        "workflow_run": os.environ.get("GITHUB_RUN_ID"),
        "visual_review": "pending",
        "microsoft_powerpoint": "not tested",
        "cases": [],
    }
    try:
        tools = Tools(output)
        write_json(output / "environment.json", environment(tools, root))
        for case in cases():
            result["cases"].append(run_case(tools, case))
        result["passed"] = True
        return result
    except Exception:
        result["error"] = traceback.format_exc()
        raise
    finally:
        write_json(output / "result.json", result)
