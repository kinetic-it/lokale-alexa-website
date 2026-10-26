#!/usr/bin/env python3
"""Bilingual A4 guide: content JSON is translated; layout lives only here."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, PageBreak,
    Spacer, Table, TableStyle, NextPageTemplate,
)
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
WIDTH,HEIGHT=A4
LEFT=45
RIGHT=45
CONTENT=WIDTH-LEFT-RIGHT
NAVY=colors.HexColor('#17364a')
TEAL=colors.HexColor('#078e9e')
INK=colors.HexColor('#183c50')
MUTED=colors.HexColor('#526478')
STRIPE=colors.HexColor('#edf4f6')

pdfmetrics.registerFont(TTFont('DejaVuSans','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('DejaVuSans',normal='DejaVuSans',bold='DejaVuSans-Bold')

STYLES={
    'title':ParagraphStyle('cover-title',fontName='DejaVuSans-Bold',fontSize=27,leading=35,
                           textColor=NAVY,spaceAfter=18,splitLongWords=1),
    'subtitle':ParagraphStyle('cover-subtitle',fontName='DejaVuSans',fontSize=10,leading=15,
                              textColor=INK,spaceAfter=16),
    'h1':ParagraphStyle('chapter',fontName='DejaVuSans-Bold',fontSize=16,leading=21,
                        textColor=NAVY,spaceBefore=19,spaceAfter=10,keepWithNext=True),
    'h2':ParagraphStyle('section',fontName='DejaVuSans-Bold',fontSize=11.5,leading=16,
                        textColor=TEAL,spaceBefore=13,spaceAfter=7,keepWithNext=True),
    'lead':ParagraphStyle('lead',fontName='DejaVuSans-Bold',fontSize=9.1,leading=14,
                          textColor=INK,spaceAfter=6),
    'paragraph':ParagraphStyle('body',fontName='DejaVuSans',fontSize=9.1,leading=14,
                               textColor=INK,spaceAfter=9,allowWidows=0,allowOrphans=0),
    'table-head':ParagraphStyle('head-cell',fontName='DejaVuSans-Bold',fontSize=7.8,leading=10.5,
                                textColor=colors.white),
    'table-cell':ParagraphStyle('table-cell',fontName='DejaVuSans',fontSize=7.8,leading=11.1,
                                textColor=INK),
    'contents-title':ParagraphStyle('contents-title',fontName='DejaVuSans-Bold',
                                    fontSize=20,leading=26,textColor=NAVY,spaceAfter=15),
    'toc1':ParagraphStyle('toc-chapter',fontName='DejaVuSans-Bold',fontSize=9.4,leading=14.0,
                         leftIndent=0,firstLineIndent=0,spaceBefore=5),
    'toc2':ParagraphStyle('toc-section',fontName='DejaVuSans',fontSize=8.5,leading=12.0,
                         leftIndent=13,firstLineIndent=0),
}

def safe(text):
    """Escape source text, preserving written URLs as hyperlinks."""
    escaped=html.escape(text,quote=False)
    escaped=re.sub(r'(https?://[^\s<>&]+)',lambda m:
        f'<link href="{html.escape(m.group(0),quote=True)}" color="#078e9e">{m.group(0)}</link>',
        escaped)
    return escaped.replace('\n','<br/>')

def editable_ids(data):
    ids=[]
    for element in data['elements']:
        if element['type']=='table':
            ids.append(element['id'])
            ids.extend(cell['id'] for row in element['rows'] for cell in row)
        else:
            ids.append(element['id'])
    return ids

class GuideDoc(BaseDocTemplate):
    def __init__(self,path,lang,metadata):
        BaseDocTemplate.__init__(self,str(path),pagesize=A4,leftMargin=LEFT,rightMargin=RIGHT,
                                 topMargin=55,bottomMargin=58,title=metadata['title'],
                                 author='',subject='Voice and device compatibility guide',
                                 pageCompression=1)
        self.lang=lang
        frame=Frame(LEFT,58,CONTENT,HEIGHT-112,leftPadding=0,rightPadding=0,
                    topPadding=0,bottomPadding=0,id='body')
        self.addPageTemplates(PageTemplate(id='guide',frames=frame,onPage=self.background))
        self._heading_count=0

    def beforeDocument(self):
        self._heading_count=0

    def background(self,canv,doc):
        canv.saveState()
        if doc.page>1:
            canv.setFont('DejaVuSans',7.7)
            canv.setFillColor(MUTED)
            canv.drawString(LEFT,HEIGHT-26,
                'AMAZON DEVICES · SOFTWARE AND COMPATIBILITY' if self.lang=='en'
                else 'AMAZON-GERÄTE · SOFTWARE UND KOMPATIBILITÄT')
            canv.setStrokeColor(TEAL)
            canv.setLineWidth(.7)
            canv.line(LEFT,HEIGHT-38,WIDTH-RIGHT,HEIGHT-38)
        canv.setFont('DejaVuSans',7.7)
        canv.setFillColor(MUTED)
        label='As of: 22 October 2026' if self.lang=='en' else 'Stand: 22. Oktober 2026'
        canv.drawString(LEFT,25,label)
        canv.drawCentredString(WIDTH/2,25,str(doc.page))
        logo=ROOT/'footer-logo.png'
        if logo.exists():
            canv.drawImage(str(logo),WIDTH-RIGHT-26,10,width=26,height=26,mask='auto')
        canv.restoreState()

    def afterFlowable(self,flowable):
        if hasattr(flowable,'_guide_toc'):
            level,label=flowable._guide_toc
            self._heading_count+=1
            key=f'heading-{self._heading_count}'
            self.canv.bookmarkPage(key)
            self.notify('TOCEntry',(level,label,self.page,key))

def table_flow(element):
    num=element['columns']
    if num==2:
        widths=[CONTENT*.36,CONTENT*.64]
    elif num==3:
        widths=[CONTENT*.265,CONTENT*.34,CONTENT*.395]
    elif num==4:
        widths=[CONTENT*.23,CONTENT*.25,CONTENT*.25,CONTENT*.27]
    else:
        widths=[CONTENT/num]*num
    data=[]
    for i,row in enumerate(element['rows']):
        style=STYLES['table-head' if i==0 else 'table-cell']
        data.append([Paragraph(safe(cell['text'] or ' '),style) for cell in row])
    table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT',splitByRow=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),NAVY),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[STRIPE,colors.white]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),7),
        ('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#bacbd1')),
    ]))
    return table

def build(lang,outfile):
    data=json.loads((ROOT/f'content.{lang}.json').read_text(encoding='utf-8'))
    elements=data['elements']
    assert elements and data['meta']['language']==lang
    document=GuideDoc(outfile,lang,data['meta'])
    story=[]
    cover=[x for x in elements if x['id'].startswith('p01.')]
    body=[x for x in elements if not x['id'].startswith('p01.')]
    for item in cover:
        style=STYLES[item['type']]
        story.append(Paragraph(safe(item['text']),style))
        if item['id']=='p01.b004':
            story.append(Spacer(1,15))
    if lang=='en':
        story.append(Spacer(1,16))
        story.append(Paragraph('English edition, translated from the German original',
                                STYLES['lead']))
        story.append(Paragraph('Translation date: 26 October 2026. '
                                'Machine-assisted translation, not reviewed by a native speaker.',
                                STYLES['paragraph']))
    story.append(PageBreak())
    story.append(Paragraph('Contents' if lang=='en' else 'Inhaltsverzeichnis',
                           STYLES['contents-title']))
    toc=TableOfContents()
    toc.levelStyles=[STYLES['toc1'],STYLES['toc2']]
    story.extend([toc,PageBreak()])
    for item in body:
        kind=item['type']
        if kind=='table':
            story.extend([table_flow(item),Spacer(1,8)])
            continue
        content=safe(item['text'])
        if item.get('url'):
            content=f'<link href="{html.escape(item["url"],quote=True)}" color="#078e9e">{content}</link>'
        paragraph=Paragraph(content,STYLES[kind])
        if kind in ('h1','h2'):
            paragraph._guide_toc=(0 if kind=='h1' else 1,item['text'])
        story.append(paragraph)
    document.multiBuild(story,maxPasses=5)
    # ReportLab does not expose PDF catalog /Lang through Canvas.
    reader=PdfReader(str(outfile))
    writer=PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.root_object[NameObject('/Lang')]=TextStringObject('en-GB' if lang=='en' else 'de-DE')
    writer.add_metadata({'/Title':data['meta']['title'],
                         '/Subject':'Software and device compatibility guide' if lang=='en'
                                    else 'Software und Gerätekompatibilität'})
    temporary=Path(str(outfile)+'.metadata.tmp')
    with temporary.open('wb') as stream:
        writer.write(stream)
    temporary.replace(outfile)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--scratch-dir',type=Path,default=REPO/'scratchpad')
    args=parser.parse_args()
    args.scratch_dir.mkdir(parents=True,exist_ok=True)
    de=json.loads((ROOT/'content.de.json').read_text(encoding='utf-8'))
    en=json.loads((ROOT/'content.en.json').read_text(encoding='utf-8'))
    if editable_ids(de)!=editable_ids(en):
        raise ValueError('German and English content IDs differ')
    build('de',args.scratch_dir/'Amazon-Geraete-Leitfaden-de-rebuild.pdf')
    destination=REPO/'downloads'/'Amazon-Devices-Guide-2026-10-22-neutral-en.pdf'
    destination.parent.mkdir(parents=True,exist_ok=True)
    build('en',destination)
