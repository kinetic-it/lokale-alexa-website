#!/usr/bin/env python3
"""Baut den Amazon-Geraete-Leitfaden als PDF aus content.<sprache>.json.

Aufruf (im Repo-Root):
    python3 tools/leitfaden/build_pdf.py            # baut de und en nach build/
    python3 tools/leitfaden/build_pdf.py en OUT.pdf  # baut eine Sprache an einen Pfad

Deutsch (content.de.json) ist der Master. Beide Dateien haben dieselben Block-IDs.
Benoetigt: reportlab, Schrift DejaVu Sans (Debian/Ubuntu: Paket fonts-dejavu-core).
"""
import io, json, os, sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, NextPageTemplate, Flowable, KeepTogether, CondPageBreak)

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIRS = [os.path.join(HERE, 'fonts'), '/usr/share/fonts/truetype/dejavu', '/usr/share/fonts/dejavu', '/usr/share/fonts/TTF']
def font_path(name):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p): return p
    sys.exit('Schrift %s nicht gefunden (Paket fonts-dejavu-core installieren)' % name)
pdfmetrics.registerFont(TTFont('DejaVuSans', font_path('DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path('DejaVuSans-Bold.ttf')))
pdfmetrics.registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans-Bold', italic='DejaVuSans', boldItalic='DejaVuSans-Bold')

C_NAVY = Color(0.090196, 0.211765, 0.290196)
C_TEAL_LINE = Color(0.031373, 0.498039, 0.54902)
C_TEAL_H2 = Color(0.027451, 0.556863, 0.619608)
C_GREY = Color(0.321569, 0.388235, 0.443137)
C_ZEBRA = Color(0.933333, 0.956863, 0.964706)
C_RULE = Color(0.811765, 0.862745, 0.882353)
W, H = A4
LM = 45.0
FW = 505.3
COLW = [123.8, 161.7, 219.5]
H1_TOP = 15.0
H1_MID = 15.0

def S(name, **kw):
    base = dict(fontName='DejaVuSans', textColor=C_NAVY, fontSize=9.4, leading=14, spaceAfter=8)
    base.update(kw)
    return ParagraphStyle(name, **base)

ST = dict(
    p=S('p'),
    h1=S('h1', fontName='DejaVuSans-Bold', fontSize=20, leading=26, spaceBefore=0, spaceAfter=16, keepWithNext=1),
    h2=S('h2', fontName='DejaVuSans-Bold', fontSize=12, leading=16, textColor=C_TEAL_H2, spaceBefore=12, spaceAfter=9, keepWithNext=1),
    bullet=S('bullet', fontSize=9.1, leading=13.8, leftIndent=10, firstLineIndent=-8, spaceAfter=6),
    th=S('th', fontName='DejaVuSans-Bold', fontSize=8.3, leading=11.8, textColor=Color(1, 1, 1), spaceAfter=0),
    td=S('td', fontSize=8.1, leading=11.8, spaceAfter=0),
    ctitle=S('ctitle', fontName='DejaVuSans-Bold', fontSize=29, leading=36, spaceAfter=0),
    csub=S('csub'),
    cstat=S('cstat', fontName='DejaVuSans-Bold'),
    tocT=S('tocT', fontName='DejaVuSans-Bold', fontSize=20, leading=23, spaceAfter=21.1),
)

class TocLine(Flowable):
    def __init__(self, level, text, key, page):
        super().__init__()
        self.level, self.text, self.key, self.page = level, text, key, page
        self.size = 10 if level == 1 else 8.4
        self.font = 'DejaVuSans-Bold' if level == 1 else 'DejaVuSans'
        self.color = C_NAVY if level == 1 else C_GREY
        self.indent = 0 if level == 1 else 13
        self.height_ = 23 if level == 1 else 14
    def wrap(self, aw, ah):
        self.width = aw
        return aw, self.height_
    def draw(self):
        c = self.canv
        base = 7.0 if self.level == 1 else 5.6
        y = base
        c.setFillColor(self.color); c.setFont(self.font, self.size)
        c.drawString(self.indent, y, self.text)
        num = str(self.page)
        nw = stringWidth(num, self.font, self.size)
        c.drawRightString(self.width, y, num)
        if self.level == 2:
            x0 = self.indent + stringWidth(self.text, self.font, self.size) + 5
            x1 = self.width - nw - 5
            c.setFont('DejaVuSans', self.size)
            x = x0
            dw = stringWidth('.', 'DejaVuSans', self.size) + 3.2
            while x + dw <= x1:
                c.drawString(x, y, '.'); x += dw
        c.linkRect('', self.key, (0, 0, self.width, self.height_), relative=1, thickness=0)

class Raised(Flowable):
    """Zeichnet ein Flowable um dy Punkte nach oben versetzt (Layout bleibt unveraendert)."""
    def __init__(self, inner, dy, trim=False):
        super().__init__(); self.inner, self.dy, self.trim = inner, dy, trim
        self.style = getattr(inner, 'style', None)
        self.keepWithNext = getattr(inner, 'keepWithNext', 0)
        self.spaceBefore = getattr(self.style, 'spaceBefore', 0)
        self.spaceAfter = getattr(self.style, 'spaceAfter', 0)
    def getPlainText(self):
        return self.inner.getPlainText()
    def wrap(self, aw, ah):
        self.w, self.h = self.inner.wrap(aw, ah)
        if self.trim: self.h -= self.dy
        return self.w, self.h
    def split(self, aw, ah):
        return []
    def draw(self):
        self.canv.translate(0, 0 if self.trim else self.dy); self.inner.drawOn(self.canv, 0, 0)

class Para(Paragraph):
    """Absatz, der nicht ueber eine Seitengrenze geteilt wird."""
    def split(self, aw, ah):
        return []

class CondBreak(CondPageBreak):
    _SPACETRANSFER = True
    _ZEROSIZE = True   # Abstaende des Nachbarn bleiben erhalten (kein doppelter Abstand)

class H1Gap(Flowable):
    """Abstand vor einer Kapitelueberschrift: oben auf der Seite kleiner als mitten auf der Seite."""
    keepWithNext = 1
    def wrap(self, aw, ah):
        top = abs(ah - (H - 49 - 50)) < 0.5
        return 0, (H1_TOP if top else H1_MID)
    def draw(self):
        pass

class Doc(BaseDocTemplate):
    def __init__(self, fn, meta, anchors, **kw):
        super().__init__(fn, pagesize=A4, leftMargin=LM, rightMargin=W - LM - FW, topMargin=49, bottomMargin=50,
                         title=meta['pdf_title'], subject=meta['pdf_subject'], author='', creator='', **kw)
        self.meta, self.anchors, self.seen = meta, anchors, {}
        self.n = 0
        self.logo = os.path.join(HERE, 'logo.jpg')
        frame = Frame(LM, 50, FW, H - 49 - 50, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='f')
        cover_frame = Frame(LM, 50, FW, H - 52 - 50, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='cf')
        self.addPageTemplates([PageTemplate('cover', [cover_frame], onPage=self.deco_cover),
                               PageTemplate('main', [frame], onPage=self.deco_main)])
    def footer(self, c):
        c.setFont('DejaVuSans', 7.7); c.setFillColor(C_GREY)
        c.drawString(LM, H - 811 - 5.9, self.meta['footer'])
        c.drawCentredString(W / 2, H - 811 - 5.9, str(c.getPageNumber()))
        c.drawImage(self.logo, 524, H - 832, 26, 26)
    def deco_cover(self, c, d):
        self.footer(c)
    def deco_main(self, c, d):
        c.setFont('DejaVuSans', 7.7); c.setFillColor(C_GREY)
        c.drawString(LM, H - 20 - 5.9, self.meta['header'])
        c.setStrokeColor(C_TEAL_LINE); c.setLineWidth(0.6)
        c.line(LM, H - 35, LM + FW, H - 35)
        self.footer(c)
    def afterFlowable(self, f):
        name = getattr(getattr(f, 'style', None), 'name', None)
        if name in ('h1', 'h2'):
            self.n += 1
            key = 'sec%d' % self.n
            txt = f.getPlainText()
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(txt, key, 0 if name == 'h1' else 1, 0)
            self.seen[key] = (name, txt, self.page)

def esc(t):
    return t.replace('&', '&amp;')

def table_flow(rows):
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(esc(c), ST['th'] if i == 0 else ST['td']) for c in r])
    t = Table(data, colWidths=COLW, repeatRows=1)
    cmds = [('BACKGROUND', (0, 0), (-1, 0), C_NAVY),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8.1), ('BOTTOMPADDING', (0, 0), (-1, 0), 8.1),
            ('TOPPADDING', (0, 1), (-1, -1), 8.0), ('BOTTOMPADDING', (0, 1), (-1, -1), 8.0)]
    for i in range(1, len(rows)):
        cmds.append(('BACKGROUND', (0, i), (-1, i), C_ZEBRA if i % 2 == 1 else Color(1, 1, 1)))
        cmds.append(('LINEBELOW', (0, i), (-1, i), 0.3, C_RULE))
    t.setStyle(TableStyle(cmds))
    return t

def story(content, anchors):
    m, blocks = content['meta'], content['blocks']
    s = []
    s.append(Spacer(1, 74 - 7))
    for ln in m['cover_title']:
        s.append(Paragraph(esc(ln), ST['ctitle']))
    s.append(Spacer(1, 25.0))
    s.append(Paragraph(esc(m['cover_subtitle']), ST['csub']))
    s.append(Paragraph(esc(m['cover_status']), ST['cstat']))
    for p in m['cover_paragraphs']:
        s.append(Paragraph(esc(p), ST['p']))
    if m['cover_note']:
        s.append(Spacer(1, 12))
        for p in m['cover_note']:
            s.append(Paragraph(esc(p), ST['p']))
    s.append(NextPageTemplate('main'))
    s.append(PageBreak())
    s.append(Paragraph(esc(m['toc_title']), ST['tocT']))
    n = 0
    for b in blocks:
        if b['t'] in ('h1', 'h2'):
            n += 1
            key = 'sec%d' % n
            pg = anchors.get(key, 0)
            s.append(TocLine(1 if b['t'] == 'h1' else 2, b['text'], key, pg))
    s.append(PageBreak())
    for i, b in enumerate(blocks):
        t = b['t']
        nxt = blocks[i + 1]['t'] if i + 1 < len(blocks) else ''
        if t in ('h1', 'h2') and nxt == 'table':
            s.append(CondBreak(120 if t == 'h2' else 140))
        if t == 'h1':
            s.append(H1Gap())
            s.append(Paragraph(esc(b['text']), ST[t]))
        elif t == 'h2':
            s.append(Paragraph(esc(b['text']), ST[t]))
        elif t == 'p':
            s.append(Para(esc(b['text']), ST[t]))
        elif t == 'bullets':
            for it in b['items']:
                s.append(Para('• ' + esc(it), ST['bullet']))
        elif t == 'table':
            s.append(table_flow(b['rows']))
            s.append(Spacer(1, 12))
    return s

def build(lang, out):
    content = json.load(open(os.path.join(HERE, 'content.%s.json' % lang), encoding='utf-8'))
    anchors = {}
    for _ in range(4):
        buf = io.BytesIO()
        doc = Doc(buf, content['meta'], anchors)
        doc.build(story(content, anchors))
        new = {k: v[2] for k, v in doc.seen.items()}
        if new == anchors: break
        anchors = new
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, 'wb').write(buf.getvalue())
    print(lang, out, doc.page, 'Seiten')

if __name__ == '__main__':
    if len(sys.argv) == 3:
        build(sys.argv[1], sys.argv[2])
    else:
        for l in ('de', 'en'):
            build(l, os.path.join(HERE, 'build', 'leitfaden-%s.pdf' % l))
