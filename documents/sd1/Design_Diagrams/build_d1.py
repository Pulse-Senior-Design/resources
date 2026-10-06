#!/usr/bin/env python3
"""Export the D1 SVG and Markdown sources. Requires reportlab and pypdfium2."""
from pathlib import Path
from html import escape
import re
import xml.etree.ElementTree as ET
import tempfile
import pypdfium2 as pdfium

from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Preformatted, Flowable,
)
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parent
WIDTH = 516


def read_svg():
    root = ET.parse(ROOT / 'D1_Data_Model.svg').getroot()
    height = float(root.attrib['height'])
    drawing = Drawing(float(root.attrib['width']), height)
    for el in root:
        a = el.attrib
        tag = el.tag.split('}')[-1]
        color = HexColor(a.get('fill', '#000000'))
        stroke = HexColor(a['stroke']) if 'stroke' in a else None
        if tag == 'rect':
            drawing.add(Rect(float(a['x']), height-float(a['y'])-float(a['height']),
                             float(a['width']), float(a['height']),
                             rx=float(a.get('rx', 0)), ry=float(a.get('rx', 0)),
                             fillColor=color, strokeColor=stroke,
                             strokeWidth=float(a.get('stroke-width', 0))))
        elif tag == 'line':
            drawing.add(Line(float(a['x1']), height-float(a['y1']),
                             float(a['x2']), height-float(a['y2']),
                             strokeColor=stroke, strokeWidth=float(a.get('stroke-width', 1))))
        elif tag == 'text':
            font = 'Helvetica-Bold' if a.get('font-weight') == 'bold' else 'Helvetica'
            drawing.add(String(float(a['x']), height-float(a['y']), el.text or '',
                             fontName=font, fontSize=float(a['font-size']), fillColor=color))
    return drawing


class Figure(Flowable):
    def __init__(self, drawing):
        super().__init__()
        self.drawing = drawing
        self.scale = (WIDTH * 0.96) / drawing.width
        self.width = WIDTH * 0.96
        self.height = drawing.height * self.scale

    def draw(self):
        self.canv.saveState()
        self.canv.scale(self.scale, self.scale)
        renderPDF.draw(self.drawing, self.canv, 0, 0)
        self.canv.restoreState()


def inline(s):
    # Protect code and links before applying the simple Markdown rules.
    tokens = []
    def put(value):
        tokens.append(value)
        return f'@@TOKEN{len(tokens)-1}@@'
    s = re.sub(r'`([^`]+)`', lambda m: put('<font name="Courier" size="8.2">'
               + escape(m[1]) + '</font>'), s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',
               lambda m: put(f'<link href="{escape(m[2], quote=True)}" color="#000000">'
                             + escape(m[1]) + '</link>'), s)
    s = escape(s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    for i, value in enumerate(tokens):
        s = s.replace(f'@@TOKEN{i}@@', value)
    return s


BODY = ParagraphStyle('body', fontName='Times-Roman', fontSize=10, leading=12.5,
                      textColor=HexColor('#000000'), spaceAfter=7)
SMALL = ParagraphStyle('cell', parent=BODY, fontSize=9, leading=11, spaceAfter=0)
HEAD = ParagraphStyle('headcell', parent=SMALL, fontName='Times-Bold')
TITLE = ParagraphStyle('title', parent=BODY, fontName='Times-Bold', fontSize=14,
                       leading=18, spaceAfter=10)
H2 = ParagraphStyle('section', parent=BODY, fontName='Times-Bold', fontSize=12,
                    leading=15, spaceAfter=9, keepWithNext=True)
H3 = ParagraphStyle('subsection', parent=BODY, fontName='Times-Bold', fontSize=11,
                    leading=14, spaceBefore=7,
                    spaceAfter=6, keepWithNext=True)
CODE = ParagraphStyle('code', fontName='Courier', fontSize=8.4, leading=10.2,
                      spaceAfter=12)


def table(rows):
    n = len(rows[0])
    if n == 2:
        widths = [150, WIDTH-150]
    else:
        widths = [125, 185, WIDTH-310]
    if rows[0][0] == 'Piece':
        widths = [112, 145, WIDTH-257]
    if rows[0][0] == 'Method':
        widths = [90, 195, WIDTH-285]
    if rows[0][0] == 'Requirement or interface':
        widths = [140, 115, WIDTH-255]
    if rows[0][0] == 'ID':
        widths = [38, WIDTH-38]
    cells = [[Paragraph(inline(c), HEAD if i == 0 else SMALL) for c in row]
             for i, row in enumerate(rows)]
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('GRID', (0, 0), (-1, -1), 0.4, HexColor('#000000')),
    ]))
    return t


def parse(drawing):
    lines = (ROOT / 'D1_Detailed_Design.md').read_text().splitlines()
    story, i = [], 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == '<!-- pagebreak -->':
            story.append(PageBreak())
            i += 1
        elif line.startswith('```'):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                block.append(lines[i])
                i += 1
            story.append(Preformatted('\n'.join(block), CODE))
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [s.strip() for s in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', s.replace(' ', '')) for s in row):
                    rows.append(row)
                i += 1
            story.extend([table(rows), Spacer(1, 9)])
        elif line.startswith('!['):
            story.extend([Figure(drawing), Spacer(1, 5)])
            i += 1
        elif line.startswith('# '):
            story.append(Paragraph(inline(line[2:]), TITLE))
            i += 1
        elif line.startswith('## '):
            story.append(Paragraph(inline(line[3:]), H2))
            i += 1
        elif line.startswith('### '):
            story.append(Paragraph(inline(line[4:]), H3))
            i += 1
        elif line.startswith('- '):
            story.append(Paragraph(inline(line[2:]), BODY, bulletText='-'))
            i += 1
        else:
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '|', '```', '![', '<!--', '- ')):
                para.append(lines[i].strip())
                i += 1
            story.append(Paragraph(inline(' '.join(para)), BODY))
    return story


class NumberedCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saved = []

    def showPage(self):
        self.saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        count = len(self.saved)
        for state in self.saved:
            self.__dict__.update(state)
            self.setFont('Times-Roman', 9)
            self.setFillColor(HexColor('#000000'))
            self.drawCentredString(306, 24, str(self._pageNumber))
            super().showPage()
        super().save()


def main():
    drawing = read_svg()
    with tempfile.TemporaryDirectory(prefix='pulse-d1-') as temp:
        figure_pdf = Path(temp) / 'figure.pdf'
        renderPDF.drawToFile(drawing, str(figure_pdf))
        pdf = pdfium.PdfDocument(str(figure_pdf))
        page = pdf[0]
        bitmap = page.render(scale=200/72)
        bitmap.to_pil().save(ROOT / 'D1_Data_Model.png')
        bitmap.close()
        page.close()
        pdf.close()
    doc = SimpleDocTemplate(str(ROOT / 'D1_Detailed_Design.pdf'), pagesize=(612, 792),
                            rightMargin=48, leftMargin=48, topMargin=52, bottomMargin=48,
                            title='Pulse - D1 Detailed Design',
                            author='Jacob Cohen, Sujal Choukse, Yatharth Bajaj',
                            subject='Assignment 6: Node C3 and Hub C5')
    doc.build(parse(drawing), canvasmaker=NumberedCanvas)
    print('Exported D1_Data_Model.png and D1_Detailed_Design.pdf')


if __name__ == '__main__':
    main()
