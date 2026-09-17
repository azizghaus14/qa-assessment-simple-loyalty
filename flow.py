import textwrap
W=1120
nodes=[]; edges=[]
def node(id,kind,x,y,text,w=300,h=None):
    nodes.append(dict(id=id,kind=kind,x=x,y=y,text=text,w=w,h=h)); return id
def edge(a,b,label="",side=None):
    edges.append((a,b,label,side))
MX=330   # main column centre
EX=830   # error column centre
def P(id,y,t,w=330): return node(id,'proc',MX,y,t,w)
def D(id,y,t,w=330): return node(id,'dec',MX,y,t,w)
def E(id,y,t,w=430): return node(id,'err',EX,y,t,w)

P('start',40,'START: Finance executive opens SMS Credit Top-Up',300)
P('p1',140,'Load brand list from MikeTango database')
D('d1',240,'Brand list loaded?')
E('e1',240,'ERR-01 "Unable to load brands. Please try again."\nAction: show Retry; no data changed')
P('p2',350,'Finance executive selects a brand')
D('d2',450,'Brand has at least one outlet?')
E('e2',450,'ERR-02 "No outlets found under this brand.\nPlease contact support."\nAction: return to brand selection')
P('p3',560,'Display outlets: outlet name, company (billing entity),\ncurrent SMS balance')
P('p4',670,'Finance executive enters top-up quantity per outlet')
D('d3',770,'Input valid? (integer, > 0, within max,\nat least one outlet filled)')
E('e3',770,'ERR-03 inline per field:\n"Enter a whole number greater than 0"\n"Maximum 100,000 credits per outlet"\n"Enter a top-up for at least one outlet"\nAction: block Next; keep entered values')
D('d4',890,'Billing email present and valid\nfor every selected company?')
E('e4',890,'ERR-04 "Billing email missing or invalid for\n{company}. Update the client record first."\nAction: block Next; no quotation, no credits')
P('p5',1000,'Click NEXT: disable button, create idempotency key')
P('p6',1090,'Call QuickBooks API: generate quotation\n(line item per company)')
D('d5',1190,'Quotation generated?')
E('e5',1190,'ERR-05 "Quotation could not be generated.\nNo credits have been added."\nAction: Retry with SAME idempotency key;\nno duplicate quotation, no partial credit')
P('p7',1300,'Credit SMS to EACH company account\n(single atomic transaction, balance = balance + top-up)')
D('d6',1400,'All credits committed?')
E('e6',1400,'ERR-06 "Top-up failed. No credits were added."\nAction: roll back transaction, void/flag quotation,\nalert finance for reconciliation')
P('p8',1510,'Send quotation email to client billing address')
D('d7',1610,'Email sent?')
E('e7',1610,'WARN-01 "Quotation created and credits added,\nbut the email could not be sent."\nAction: queue retry + manual Resend;\ncredits REMAIN valid')
P('p9',1720,'Write audit log: user, brand, companies,\namounts, quotation no., timestamp')
P('end',1810,'END: Success screen with quotation no.\nand updated balance per company',320)

edge('start','p1'); edge('p1','d1'); edge('d1','p2','Yes'); edge('d1','e1','No','r')
edge('p2','d2'); edge('d2','p3','Yes'); edge('d2','e2','No','r')
edge('p3','p4'); edge('p4','d3'); edge('d3','d4','Yes'); edge('d3','e3','No','r')
edge('d4','p5','Yes'); edge('d4','e4','No','r')
edge('p5','p6'); edge('p6','d5'); edge('d5','p7','Yes'); edge('d5','e5','No','r')
edge('p7','d6'); edge('d6','p8','Yes'); edge('d6','e6','No','r')
edge('p8','d7'); edge('d7','p9','Yes'); edge('d7','e7','No','r')
edge('p9','end')

LH=15
def lines(t,w,fs=12):
    out=[]
    for para in t.split('\n'):
        out+= textwrap.wrap(para, max(10,int(w/(fs*0.55)))) or ['']
    return out
def size(n):
    fs=12 if n['kind']!='err' else 11
    ls=lines(n['text'],n['w'],fs)
    h=n['h'] or max(46, len(ls)*LH+22)
    return ls,h,fs
svg=[f'<svg viewBox="0 0 {W} 1880" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial,sans-serif">']
svg.append('<defs><marker id="a" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#333"/></marker></defs>')
pos={}
for n in nodes:
    ls,h,fs=size(n); pos[n['id']]=(n['x'],n['y'],n['w'],h)
for a,b,label,side in edges:
    ax,ay,aw,ah=pos[a]; bx,by,bw,bh=pos[b]
    if side=='r':
        y=ay+ah/2
        svg.append(f'<path d="M{ax+aw/2},{y} L{bx-bw/2},{by+bh/2}" stroke="#333" fill="none" marker-end="url(#a)"/>')
        svg.append(f'<text x="{ax+aw/2+10}" y="{y-6}" font-size="11" fill="#b00">{label}</text>')
    else:
        svg.append(f'<path d="M{ax},{ay+ah} L{bx},{by}" stroke="#333" fill="none" marker-end="url(#a)"/>')
        if label: svg.append(f'<text x="{ax+8}" y="{ay+ah+14}" font-size="11" fill="#060">{label}</text>')
for n in nodes:
    ls,h,fs=size(n); x,y,w=n['x'],n['y'],n['w']
    if n['kind']=='dec':
        svg.append(f'<polygon points="{x},{y} {x+w/2},{y+h/2} {x},{y+h} {x-w/2},{y+h/2}" fill="#fff7e6" stroke="#d48806"/>')
    elif n['kind']=='err':
        svg.append(f'<rect x="{x-w/2}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fff1f0" stroke="#cf1322"/>')
    else:
        fill='#e6f4ff' if n['id'] in('start','end') else '#f6ffed'
        stroke='#0958d9' if n['id'] in('start','end') else '#389e0d'
        svg.append(f'<rect x="{x-w/2}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}"/>')
    ty=y+h/2-(len(ls)-1)*LH/2+4
    for i,l in enumerate(ls):
        svg.append(f'<text x="{x}" y="{ty+i*LH}" font-size="{fs}" text-anchor="middle" fill="#111">{l.replace("&","&amp;").replace("<","&lt;")}</text>')
svg.append('</svg>')
open('/Users/azizghaus/Documents/CV/Applications/SimpleLoyalty/flow.svg','w').write('\n'.join(svg))
print('svg written', len('\n'.join(svg)))
