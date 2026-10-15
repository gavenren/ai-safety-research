#!/usr/bin/env python3
"""Build paper.pdf from the full Markdown report, with a text coverage check.

Usage: python build_pdf.py --font-dir /path/to/dejavu-fonts
ReportLab, pypdf, and Pillow are needed. The PDF embeds DejaVu font subsets.
Standalone font files are not included. See FONT_LICENSE.txt for their notices.
The default font search checks common system locations and the bundled runtime.
The PDF has fixed metadata and uses ReportLab's invariant mode.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import reportlab
import PIL
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
    TableStyle, XPreformatted,
)
import pypdf


BASE = Path(__file__).resolve().parent
WEB_BASE = "https://github.com/gavenren/ai-safety-research/blob/main/research/2026-10-15-computer-use-retries/"
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 48
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN
NAVY = colors.HexColor("#173346")
TEAL = colors.HexColor("#246A75")
LIGHT = colors.HexColor("#EDF3F5")
INK = colors.HexColor("#20292E")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(name, value):
    (BASE / name).write_text(json.dumps(value, indent=2) + "\n")


def find_font_dir(supplied):
    candidates = [Path(supplied)] if supplied else []
    candidates += [Path("/usr/share/fonts/truetype/dejavu"), Path("/usr/share/fonts/dejavu")]
    for parent in Path(sys.executable).resolve().parents:
        candidates += [parent / "native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype"]
    for path in candidates:
        if (path / "DejaVuSerif.ttf").is_file():
            return path
    raise SystemExit("DejaVu fonts were not found. Set --font-dir to their directory.")


def register_fonts(font_dir):
    mapping = {
        "Paper": "DejaVuSerif.ttf",
        "PaperBold": "DejaVuSerif-Bold.ttf",
        "PaperItalic": "DejaVuSerif-Italic.ttf",
        "PaperBoldItalic": "DejaVuSerif-BoldItalic.ttf",
        "Sans": "DejaVuSans.ttf",
        "SansBold": "DejaVuSans-Bold.ttf",
        "Mono": "DejaVuSansMono.ttf",
    }
    for name, filename in mapping.items():
        pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
    pdfmetrics.registerFontFamily("Paper", normal="Paper", bold="PaperBold", italic="PaperItalic", boldItalic="PaperBoldItalic")
    pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="SansBold", italic="Sans", boldItalic="SansBold")
    pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono", italic="Mono", boldItalic="Mono")
    return {filename: sha256(font_dir / filename) for filename in mapping.values()}


def plain(text):
    text = re.sub(r"!?\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    return text.replace("**", "").replace("`", "").replace("*", "")


def inline(text):
    """Escape source text; then add only supported Markdown inline styles."""
    pattern = r"(!?\[[^\]]+\]\([^)]+\)|`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)"
    result = []
    for token in re.split(pattern, text):
        if not token:
            continue
        link = re.fullmatch(r"!?\[([^\]]+)\]\(([^)]+)\)", token)
        if link:
            label, target = link.groups()
            result.append('<link href="' + html.escape(urljoin(WEB_BASE, target), quote=True) + '" color="#246A75">' + html.escape(label) + "</link>")
        elif token.startswith("`") and token.endswith("`"):
            result.append('<font name="Mono" size="8.1">' + html.escape(token[1:-1]) + "</font>")
        elif token.startswith("**") and token.endswith("**"):
            result.append("<b>" + html.escape(token[2:-2]) + "</b>")
        elif token.startswith("*") and token.endswith("*"):
            result.append("<i>" + html.escape(token[1:-1]) + "</i>")
        else:
            result.append(html.escape(token))
    return "".join(result)


def style_set():
    styles = getSampleStyleSheet()
    specs = {
        "Body": dict(fontName="Paper", fontSize=9.3, leading=13.6, textColor=INK, spaceAfter=6, allowWidows=0, allowOrphans=0),
        "TitlePaper": dict(fontName="SansBold", fontSize=23, leading=28, textColor=NAVY, spaceAfter=13, keepWithNext=True),
        "H2": dict(fontName="SansBold", fontSize=12, leading=16, textColor=NAVY, spaceBefore=12, spaceAfter=6, keepWithNext=True),
        "H3": dict(fontName="SansBold", fontSize=10, leading=14, textColor=TEAL, spaceBefore=8, spaceAfter=4, keepWithNext=True),
        "H4": dict(fontName="SansBold", fontSize=9.4, leading=13, textColor=INK, spaceBefore=6, spaceAfter=4, keepWithNext=True),
        "BulletPaper": dict(fontName="Paper", fontSize=9.3, leading=13.6, leftIndent=13, firstLineIndent=-10, spaceAfter=4, textColor=INK),
        "Caption": dict(fontName="Sans", fontSize=8.1, leading=11.3, textColor=INK, spaceAfter=8),
        "Cell": dict(fontName="Sans", fontSize=7.6, leading=10.6, textColor=INK, spaceAfter=0),
        "CellHead": dict(fontName="SansBold", fontSize=7.6, leading=10.6, textColor=colors.white, spaceAfter=0),
        "CodePaper": dict(fontName="Mono", fontSize=7.2, leading=10.2, textColor=INK, backColor=LIGHT, borderPadding=7, spaceBefore=3, spaceAfter=8),
    }
    for name, spec in specs.items():
        styles.add(ParagraphStyle(name, alignment=TA_LEFT, **spec))
    return styles


class PaperDoc(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ("H2", "H3"):
            key = "section-" + str(self.seq.nextf("section"))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(), key, level=0 if flowable.style.name == "H2" else 1, closed=False)


def page_marks(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#C1CDD2"))
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 37, PAGE_WIDTH - MARGIN, 37)
    canvas.setFont("Sans", 7.2)
    canvas.setFillColor(colors.HexColor("#52636D"))
    canvas.drawString(MARGIN, 25, "COMPUTER-USE RETRY STUDY  |  15 OCTOBER 2026")
    canvas.drawRightString(PAGE_WIDTH - MARGIN, 25, str(doc.page))
    if doc.page > 1:
        canvas.setFont("Sans", 7)
        canvas.drawString(MARGIN, PAGE_HEIGHT - 29, "PENDING ACTIONS, DELAYED READS, AND SAFE RETRIES")
    canvas.restoreState()


def table_widths(rows):
    """Allocate space from both word length and total cell text length."""
    n = len(rows[0])
    weights = []
    for col in range(n):
        texts = [plain(row[col]) for row in rows]
        longest = max(len(word) for text in texts for word in text.split()) if any(texts) else 1
        weights.append(min(35, max(longest, max(len(t) for t in texts) ** 0.72, 9)))
    return [CONTENT_WIDTH * weight / sum(weights) for weight in weights]


def build_story(source, styles):
    lines = source.splitlines()
    story, checks, tables, figures = [], [], 0, 0
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            if i == len(lines):
                raise ValueError("Unclosed source code block")
            body = "\n".join(code)
            for row in code:
                if pdfmetrics.stringWidth(row, "Mono", 7.2) > CONTENT_WIDTH - 14:
                    raise ValueError("Code line exceeds the PDF width: " + row)
            story.append(XPreformatted(html.escape(body), styles["CodePaper"]))
            checks.extend(row.strip() for row in code if row.strip())
            i += 1
            continue
        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if image_match:
            alt, filename = image_match.groups()
            image_path = BASE / filename
            from PIL import Image as PILImage
            with PILImage.open(image_path) as img:
                width, height = img.size
            flow = Image(str(image_path), width=CONTENT_WIDTH, height=CONTENT_WIDTH * height / width)
            flow.hAlign = "CENTER"
            flow.keepWithNext = True
            story.append(flow)
            gap = Spacer(1, 5)
            gap.keepWithNext = True
            story.append(gap)
            figures += 1
            i += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            level, text = len(heading.group(1)), heading.group(2)
            story.append(Paragraph(inline(text), styles["TitlePaper" if level == 1 else "H" + str(level)]))
            checks.append(plain(text))
            i += 1
            continue
        if line.startswith("|"):
            raw_rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", cell.replace(" ", "")) for cell in row):
                    raw_rows.append(row)
                i += 1
            if any(len(row) != len(raw_rows[0]) for row in raw_rows):
                raise ValueError("The source table has unequal column counts")
            rows = [[Paragraph(inline(cell), styles["CellHead" if row_index == 0 else "Cell"]) for cell in row] for row_index, row in enumerate(raw_rows)]
            table = Table(rows, colWidths=table_widths(raw_rows), repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("LINEBELOW", (0, -1), (-1, -1), .4, colors.HexColor("#C1CDD2")),
            ]))
            # Keep these short source tables intact, with their headings.
            story.extend([KeepTogether([table]), Spacer(1, 8)])
            checks.extend(plain(cell) for row in raw_rows for cell in row if cell)
            tables += 1
            continue
        bullet = re.match(r"^([-*]|\d+\.)\s+(.+)$", line)
        if bullet:
            label, text = bullet.groups()
            prefix = "&#8226;" if label in ("-", "*") else html.escape(label)
            story.append(Paragraph(prefix + " " + inline(text), styles["BulletPaper"]))
            checks.append(plain(text))
            i += 1
            continue
        if line == "---":
            story.append(Spacer(1, 6)); i += 1; continue
        para = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||```|!\[|[-*] |\d+\. )", lines[i].strip()):
            para.append(lines[i].strip()); i += 1
        text = " ".join(para)
        style = "Caption" if text.startswith("Figure ") else "Body"
        story.append(Paragraph(inline(text), styles[style]))
        checks.append(plain(text))
    return story, checks, tables, figures


def compact(text):
    return re.sub(r"\s+", "", text).replace("\u00ad", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--font-dir")
    args = parser.parse_args()
    font_dir = find_font_dir(args.font_dir)
    fonts = register_fonts(font_dir)
    source_path = BASE / "report.md"
    source = source_path.read_text()
    source_title = next(line[2:] for line in source.splitlines() if line.startswith("# "))
    for char in set(source):
        if ord(char) >= 32 and ord(char) not in pdfmetrics.getFont("Paper").face.charToGlyph and char not in "\n\r\t":
            raise ValueError("The report font has no glyph for " + repr(char))
    rl_config.invariant = 1
    doc = PaperDoc(str(BASE / "paper.pdf"), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                   topMargin=47, bottomMargin=49, title=source_title, author="Codex (AI-generated study)",
                   subject="A reproducible event-model study. No human review. No AI model test.",
                   creator="build_pdf.py with ReportLab", pageCompression=1)
    story, checks, table_count, figure_count = build_story(source, style_set())
    doc.build(story, onFirstPage=page_marks, onLaterPages=page_marks)
    reader = pypdf.PdfReader(BASE / "paper.pdf")
    extracted = []
    for number, page in enumerate(reader.pages, 1):
        page_text = page.extract_text() or ""
        page_text = page_text.replace("COMPUTER-USE RETRY STUDY  |  15 OCTOBER 2026\n" + str(number) + "\n", "", 1)
        page_text = page_text.replace("PENDING ACTIONS, DELAYED READS, AND SAFE RETRIES\n", "", 1)
        extracted.append(page_text)
    text = "\n".join(extracted)
    compact_text = compact(text)
    missing = [chunk for chunk in checks if compact(chunk) not in compact_text]
    links = []
    for page in reader.pages:
        for ref in page.get("/Annots", []):
            obj = ref.get_object()
            uri = obj.get("/A", {}).get("/URI")
            if uri:
                links.append(str(uri))
    result = {
        "status": "PASS" if not missing else "FAIL",
        "source_sha256": sha256(source_path), "pdf_sha256": sha256(BASE / "paper.pdf"),
        "pages": len(reader.pages), "source_text_chunks_checked": len(checks),
        "missing_text_chunks": missing, "table_count": table_count, "figure_count": figure_count,
        "external_link_annotations": len(links), "link_targets": sorted(set(links)),
        "visual_review": "PENDING: render and inspect every page before release",
        "deterministic_rebuild": "PENDING: compare two builds before release",
        "privacy": "Public build records omit local absolute paths.",
    }
    dump("pdf_check.json", result)
    dump("pdf_environment.json", {"python": sys.version.split()[0], "reportlab": reportlab.Version,
         "pypdf": pypdf.__version__, "pillow": PIL.__version__, "fonts_sha256": fonts, "pdf_page_format": "A4",
         "reportlab_invariant": True, "source": "report.md", "output": "paper.pdf",
         "command": "python build_pdf.py --font-dir /path/to/dejavu-fonts"})
    print(json.dumps({key: value for key, value in result.items() if key not in ("link_targets",)}, indent=2))
    if missing:
        raise SystemExit("PDF text coverage check failed")


if __name__ == "__main__":
    main()
