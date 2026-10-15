#!/usr/bin/env python3
"""Rebuild D2 figures/PDF and the consolidated PDF.
Requires reportlab, pypdf, pypdfium2, and svglib.
Run from any directory: python build_d2.py
"""
from pathlib import Path
from html import escape
import re, math
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon, Group
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable, Preformatted
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
import pypdfium2 as pdfium
from svglib.svglib import svg2rlg

ROOT=Path(__file__).resolve().parent
REPO_ROOT=ROOT.parents[2] if (ROOT.parents[2]/'.git').exists() else None
OUT=ROOT if REPO_ROOT else ROOT.parent
STORY_ROOT=REPO_ROOT or OUT
WIDTH=516
INK=HexColor('#1d2936'); RED=HexColor('#a0262a'); GREY=HexColor('#eef1f4')


def text(d,x,y,s,size=13,bold=False,color=INK):
    d.add(String(x,y,s,fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,fillColor=color))


def base(title,h=730):
    d=Drawing(720,h)
    text(d,24,h-25,'Pulse | '+title,18,True)
    text(d,24,h-47,'Goal: move every farm reading to a trusted Hub and keep it until stored.',12)
    text(d,24,h-66,'Legend: boxes = actions/states; solid arrows = normal; red dashed = failure.',11)
    return d


def box(d,x,y,w,h,lines,grey=False):
    d.add(Rect(x,y,w,h,rx=5,ry=5,fillColor=GREY if grey else white,strokeColor=INK,strokeWidth=1.2))
    for i,s in enumerate(lines):
        text(d,x+12,y+h-21-i*18,s,13.5,i==0)


def arrow(d,pts,label='',at=None,error=False):
    color=RED if error else INK
    for a,b in zip(pts,pts[1:]):
        d.add(Line(*a,*b,strokeColor=color,strokeWidth=1.3,strokeDashArray=[5,4] if error else None))
    a,b=pts[-2:]; ang=math.atan2(b[1]-a[1],b[0]-a[0]); r=7
    d.add(Polygon([b[0],b[1],b[0]-r*math.cos(ang-.45),b[1]-r*math.sin(ang-.45),b[0]-r*math.cos(ang+.45),b[1]-r*math.sin(ang+.45)],fillColor=color,strokeColor=color))
    if label:
        text(d,*(at or ((pts[0][0]+pts[-1][0])/2+5,(pts[0][1]+pts[-1][1])/2+5)),label,11,False,color)


def save(d,name):
    renderSVG.drawToFile(d,str(ROOT/(name+'.svg')))
    tmp=OUT/(name+'.figure.pdf'); renderPDF.drawToFile(d,str(tmp))
    p=pdfium.PdfDocument(str(tmp)); p[0].render(scale=2).to_pil().save(ROOT/(name+'.png')); p.close(); tmp.unlink()


def figures():
    d=base('Figure 2. Sampling to confirmed storage',860)
    ys=[690,580,470,360,250,140]
    labels=[['C1/C2 - Sample and hold','One Hub, stable ID and bytes','Report sensor state to HEALTH'],['C3 - Validate and persist','Rate-sized capacity; durable write','Then return Response.ok'],['C3/C4 - Serialized airtime gate','One active send; gap and budget','No catch-up burst'],['C3 hub - Authenticate sender','Verify signature, origin and policy','Untrusted input never reaches Hub'],['C5 - Validate and commit (A2)','Atomic storage or typed error','Duplicate gets STORED again'],['C3 - Verify receipt and clean up','STORED = success; FAILED = failure','Sync deletion, then notify Edge']]
    for y,ls in zip(ys,labels):box(d,28,y,330,75,ls)
    for y,n in zip(ys,ys[1:]):arrow(d,[(193,y),(193,n+75)],'continue',(206,n+87))
    box(d,450,580,245,75,['C2 - Retain and pause','Retry identical request','EC-07/08; expose backpressure'],True)
    arrow(d,[(358,617),(450,617)],'admit fails',(367,636),True)
    box(d,450,470,245,75,['C4 - Defer, never burst','Keep record in scheduler','EC-58; expiry still wins'],True)
    arrow(d,[(358,507),(450,507)],'gate closed',(363,526),True)
    box(d,450,360,245,75,['C3 - Drop untrusted packet','Local UNAUTHORIZED only','EC-19/38; no remote reply'],True)
    arrow(d,[(358,397),(450,397)],'invalid trust',(363,416),True)
    box(d,450,245,245,85,['C5 - Distinguish errors','Permanent: signed FAILED','Transient: no receipt, retry','EC-57 / EC-28'],True)
    arrow(d,[(358,287),(450,287)],'A2 error',(367,306),True)
    text(d,28,91,'All LoRa data and receipts share the radio gate; complete radio payload <=255 bytes.',12)
    text(d,28,69,'Missing receipts retry safely. A trusted permanent rejection terminates as failure.',12)
    text(d,28,47,'Expiry means storage is unconfirmed; it does not prove the Hub has no row (EC-13).',12)
    save(d,'D2_Telemetry_Flow')

    d=base('Figure 3. Durable Delivery and paced sending',900)
    box(d,30,715,330,65,['VALIDATING - rate-sized capacity','Check route, profile size, policy v2'],True)
    box(d,30,605,330,70,['PERSISTING - not accepted yet','Write, sync, rename, directory sync','Then return Response.ok'])
    box(d,30,470,330,85,['PENDING - durable and eligible','Earliest deadline, tie round-robin','After send: retry no sooner than 30 s','Recovery retains original deadline'])
    box(d,30,330,330,85,['AIRTIME GATE - per physical radio','One transmission at a time','Gap >=1 s after end + profile rules','Recheck expiry immediately first'])
    box(d,30,195,330,75,['CLEANUP - final receipt or expiry','STORED success / FAILED rejection','Sync deletion; EXPIRED on deadline'])
    box(d,30,70,330,65,['TERMINAL - release capacity','Log outcome and notify subscribers'],True)
    arrow(d,[(195,715),(195,675)],'valid',(205,690))
    arrow(d,[(195,605),(195,555)],'durable',(205,578))
    arrow(d,[(195,470),(195,415)],'eligible',(205,438))
    arrow(d,[(195,330),(195,270)],'final receipt / expiry',(47,295))
    arrow(d,[(195,195),(195,135)],'cleanup succeeds',(205,158))
    box(d,440,715,255,65,['REJECTED - no acceptance','Bad request / capacity / size'],True)
    arrow(d,[(360,747),(440,747)],'EC-12/20',(366,765),True)
    box(d,440,605,255,70,['CLOCK / STORAGE UNAVAILABLE','RTC or persistence fault','EC-54 / EC-53'],True)
    arrow(d,[(360,640),(440,640)],'cannot admit',(366,658),True)
    box(d,440,470,255,85,['RECOVERY - after restart','Lock, validate, quarantine','RTC determines remaining life','Enqueue valid unexpired records'])
    arrow(d,[(440,510),(360,510)],'resume',(377,527))
    box(d,440,330,255,85,['WAIT - serialized scheduler','Gate closed: keep waiting','Sent: await matching receipt','No receipt: re-enter PENDING'])
    arrow(d,[(360,372),(440,372)],'EC-58',(380,390),True)
    arrow(d,[(565,415),(565,450),(385,450),(385,489),(360,489)],'deferred / retry',(442,436))
    arrow(d,[(360,220),(405,220),(405,245),(360,245)],'retry cleanup EC-53',(432,231),True)
    text(d,30,35,'A terminal FAILED is signed by the expected peer; it never proves storage (EC-57/61).',12)
    save(d,'D2_Delivery_States')

    d=base('Figure 4. Validate and publish configuration',760)
    labels=[['C6 - Read and parse source','TOML schema version 1'],['C6 - Check complete profile','Sensor rate, queue, RTC, packet fit','Peer versions, loopback, drivers'],['C6 - Report validation result','validate: exit 0, source unchanged','split: continue only when valid'],['C6 - Lock and stage output','Write all three component files','Refuse existing output target'],['C6 - Publish complete directory','Rename staging, print paths','Deploy one consistent version']]
    ys=[585,465,345,225,105]
    for y,ls in zip(ys,labels):box(d,28,y,365,78,ls)
    for y,n in zip(ys,ys[1:]):arrow(d,[(210,y),(210,n+78)],'pass',(220,n+94))
    box(d,450,565,245,90,['ERROR - report and exit 1','Syntax: stop parsing','Semantic: collect all errors','Include available driver names'],True)
    arrow(d,[(393,625),(450,625)],'EC-33',(398,643),True)
    arrow(d,[(393,505),(420,505),(420,590),(450,590)],'EC-30/59/61',(443,525),True)
    box(d,450,225,245,78,['ERROR - retain old output','Lock or filesystem failure','Discard incomplete staging'],True)
    arrow(d,[(393,264),(450,264)],'EC-32/35',(398,285),True)
    text(d,28,55,'Approve a deployment only when encoded packet, memory and arrival-rate budgets fit.',12)
    save(d,'D2_Builder_Flow')

    src=svg2rlg(str(ROOT/'D1_Data_Model.svg'));scale=672/src.width;h=src.height*scale+120;d=Drawing(720,h)
    text(d,24,h-25,'Pulse | Figure 1. Hub data model',17,True)
    text(d,24,h-47,'Goal: move every farm reading to a trusted Hub and keep it until stored.',12)
    text(d,24,h-66,'Legend: boxes = tables; lines = foreign keys; 1 / 0..* / 1..* = cardinalities.',11)
    src.scale(scale,scale);g=Group(src);g.translate(24,24);d.add(g);save(d,'D2_Hub_Data_Model');save(d,'D1_Hub_Data_Model')


def inline(s):
    tokens=[]
    def token(v): tokens.append(v); return f'ZZTOKEN{len(tokens)-1}ZZ'
    s=re.sub(r'`([^`]+)`',lambda m:token('<font name="Courier" size="8">'+escape(m[1])+'</font>'),s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',lambda m:token('<link href="'+escape(m[2],quote=True)+'" color="#224b6e">'+escape(m[1])+'</link>'),s)
    s=escape(s); s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    for i,v in enumerate(tokens): s=s.replace(f'ZZTOKEN{i}ZZ',v)
    return s

BODY=ParagraphStyle('body',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=8,textColor=INK)
SMALL=ParagraphStyle('small',parent=BODY,fontSize=8.6,leading=11.8,spaceAfter=0)
HEAD=ParagraphStyle('head',parent=SMALL,fontName='Helvetica-Bold',textColor=white)
TITLE=ParagraphStyle('title',parent=BODY,fontName='Helvetica-Bold',fontSize=19,leading=24,spaceAfter=12,keepWithNext=True)
H2=ParagraphStyle('h2',parent=BODY,fontName='Helvetica-Bold',fontSize=14,leading=19,spaceBefore=12,spaceAfter=9,keepWithNext=True)
H3=ParagraphStyle('h3',parent=BODY,fontName='Helvetica-Bold',fontSize=11.5,leading=16,spaceBefore=10,spaceAfter=8,keepWithNext=True)

class Fig(Flowable):
    def __init__(self,path):
        super().__init__(); self.d=svg2rlg(str(path)); self.scale=min(WIDTH/self.d.width,(500 if path.stem=='D2_Builder_Flow' else 600)/self.d.height); self.width=self.d.width*self.scale; self.height=self.d.height*self.scale
    def draw(self):
        self.canv.saveState(); self.canv.scale(self.scale,self.scale); renderPDF.draw(self.d,self.canv,0,0); self.canv.restoreState()


def table(rows):
    n=len(rows[0])
    if n==2: widths=[43,473] if rows[0][0] in ['ID','Story'] else [150,366] if rows[0][0] in ['Type or field','Table','Index'] else [170,346]
    elif n==3: widths=[112,145,259] if rows[0][0]=='Piece' else [90,195,231] if rows[0][0]=='Method' else [132,178,206]
    elif n==4: widths=[85,120,150,161]
    elif n==5: widths=[39,65,34,145,233]
    elif n==7: widths=[43,72,101,132,62,50,56]
    else: widths=[WIDTH/n]*n
    cells=[[Paragraph(inline(c),HEAD if i==0 else SMALL) for c in row] for i,row in enumerate(rows)]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT',splitByRow=1)
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),INK),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor('#f5f7f9')]),('LINEBELOW',(0,0),(-1,0),.6,INK),('LINEBELOW',(0,1),(-1,-1),.3,HexColor('#ccd3da')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    return t


def split_row(line):
    cells=[]; part=[]; code=False
    for char in line.strip().strip('|'):
        if char=='`':code=not code
        if char=='|' and not code:
            cells.append(''.join(part).strip());part=[]
        else:part.append(char)
    cells.append(''.join(part).strip())
    return cells


def parse(source_path=None):
    source_path=source_path or ROOT/'D2_Detailed_Design.md'
    source=source_path.read_text().replace('<!-- include: Peer_Review_Notes.md -->', (ROOT/'Peer_Review_Notes.md').read_text().replace('# Pulse - Peer Design Review Notes', ''))
    lines=source.splitlines();story=[];i=0
    def control(line):
        return bool(re.match(r'^(#{1,4} |\| |!\[|```|<!--|- |\d+\. )',line))
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line=='<!-- pagebreak -->':story.append(PageBreak());i+=1;continue
        if line.startswith('```'):
            block=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):block.append(lines[i]);i+=1
            story.append(Preformatted('\n'.join(block),ParagraphStyle('code',fontName='Courier',fontSize=8,leading=10,spaceAfter=10)));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                parts=split_row(lines[i])
                if not all(re.fullmatch(r':?-+:?',cell.strip()) for cell in parts):rows.append(parts)
                i+=1
            assert all(len(row)==len(rows[0]) for row in rows),rows
            story.extend([table(rows),Spacer(1,10)]);continue
        if line.startswith('!['):
            name=re.search(r'\]\(([^)]+)\)',line)[1]
            story.extend([Fig(ROOT/Path(name).with_suffix('.svg')),Spacer(1,10)]);i+=1;continue
        heading=re.match(r'^(#{1,4}) (.*)',line)
        if heading:
            style=TITLE if len(heading[1])==1 else H2 if len(heading[1])==2 else H3
            story.append(Paragraph(inline(heading[2]),style));i+=1;continue
        if line.startswith('- '):story.append(Paragraph(inline(line[2:]),BODY,bulletText='-'));i+=1;continue
        para=[line];i+=1
        if not re.match(r'^\d+\. ',line):
            while i<len(lines) and lines[i].strip() and not control(lines[i].strip()):para.append(lines[i].strip());i+=1
        story.append(Paragraph(inline(' '.join(para)),BODY))
    return story


def footer(label):
    def draw(c,doc):
        c.saveState();c.setStrokeColor(HexColor('#ccd3da'));c.line(48,42,564,42)
        c.setFont('Helvetica',8);c.setFillColor(INK);c.drawString(48,29,label)
        c.drawRightString(564,29,str(doc.page));c.restoreState()
    return draw


def build_pdf(source_path,out_path,title,label):
    doc=SimpleDocTemplate(str(out_path),pagesize=(612,792),leftMargin=48,rightMargin=48,topMargin=42,bottomMargin=55,title=title,author='Jacob Cohen; Sujal Choukse; Yatharth Bajaj')
    draw=footer(label);doc.build(parse(source_path),onFirstPage=draw,onLaterPages=draw)


def main():
    figures()
    story_source=next((p for p in [STORY_ROOT/'User_Stories.md',ROOT.parents[2]/'User_Stories.md'] if p.is_file()),None)
    if story_source is None:raise FileNotFoundError('User_Stories.md')
    build_pdf(story_source,STORY_ROOT/'User_Stories.pdf','Pulse - User Stories','Pulse | User Stories')
    # Retain the earlier document's smaller serif typography.
    compact={BODY:dict(fontName='Times-Roman',fontSize=10,leading=12.5,spaceAfter=7),SMALL:dict(fontName='Times-Roman',fontSize=9,leading=11),HEAD:dict(fontName='Times-Bold',fontSize=9,leading=11),TITLE:dict(fontName='Times-Bold',fontSize=14,leading=18),H2:dict(fontName='Times-Bold',fontSize=12,leading=15),H3:dict(fontName='Times-Bold',fontSize=11,leading=14)}
    saved=[(style,{k:getattr(style,k) for k in attrs}) for style,attrs in compact.items()]
    try:
        for style,attrs in compact.items():
            for k,v in attrs.items():setattr(style,k,v)
        build_pdf(ROOT/'D1_Detailed_Design.md',OUT/'D1_Detailed_Design.pdf','Pulse - Assignment 6 - D1','Pulse | Assignment 6 | D1')
    finally:
        for style,attrs in saved:
            for k,v in attrs.items():setattr(style,k,v)
    build_pdf(ROOT/'D2_Detailed_Design.md',OUT/'D2_Detailed_Design.pdf','Pulse - Assignment 7 - D2','Pulse | Assignment 7 | D2')
    writer=PdfWriter()
    writer.append(str(STORY_ROOT/'User_Stories.pdf'),outline_item='User Stories')
    d0=next((p for p in [OUT/'Reference_PDFs/D0_High_Level_Design.pdf',ROOT/'D0_High_Level_Design.pdf',OUT.parent/'D0_High_Level_Design.pdf'] if p.is_file()),None)
    if d0 is None:raise FileNotFoundError('D0_High_Level_Design.pdf')
    writer.append(str(d0),outline_item='D0 - Original Design')
    writer.append(str(OUT/'D1_Detailed_Design.pdf'),outline_item='D1 - Assignment 6')
    writer.append(str(OUT/'D2_Detailed_Design.pdf'),outline_item='D2 - Assignment 7 and Peer Review Notes')
    writer.add_metadata({'/Title':'Pulse - Assignment 4 Design Collection - Assignment 7 Submission','/Author':'Jacob Cohen; Sujal Choukse; Yatharth Bajaj'})
    writer.write(str(OUT/'Assignment_4_Consolidated.pdf'))
    for path in [STORY_ROOT/'User_Stories.pdf',OUT/'D1_Detailed_Design.pdf',OUT/'D2_Detailed_Design.pdf',OUT/'Assignment_4_Consolidated.pdf']:print(path.name,len(PdfReader(path).pages),'pages')


if __name__=='__main__': main()
