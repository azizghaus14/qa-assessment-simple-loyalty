# Generates flow.svg (process flowchart) and state.svg (state machine), black & white.
CW=0.545  # Helvetica average char width factor
def wrap(text,maxw,fs):
    cpl=max(8,int(maxw/(fs*CW)))
    out=[]
    for para in text.split('\n'):
        words=para.split(); line=''
        if not words: out.append('')
        for w in words:
            t=(line+' '+w).strip()
            if len(t)<=cpl: line=t
            else:
                if line: out.append(line)
                line=w
        if line: out.append(line)
    return out
def tw(line,fs): return len(line)*fs*CW
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ---------------- process flowchart ----------------
LH=15
def flowchart(path):
    MX,EX=340,880
    rows=[
     ('start','term',MX,'START: Finance executive opens the SMS Credit Top-Up screen',300),
     ('p1','proc',MX,'Load brand list from the MikeTango database',300),
     ('d1','dec',MX,'Brand list loaded?',260),
     ('e1','err',EX,'ERR-01  "Unable to load brands. Please try again."\nAction: show Retry. No data changed.',400),
     ('p2','proc',MX,'Finance executive selects a brand',300),
     ('d2','dec',MX,'Brand has at least one outlet?',280),
     ('e2','err',EX,'ERR-02  "No outlets found under this brand. Please contact support."\nAction: return to brand selection.',400),
     ('p3','proc',MX,'Display outlets: outlet name, company (billing entity), current SMS balance',320),
     ('p4','proc',MX,'Finance executive enters a top-up quantity per outlet',300),
     ('d3','dec',MX,'Input valid? Whole number, greater than 0, within maximum, at least one outlet filled',320),
     ('e3','err',EX,'ERR-03  inline, per field: "Enter a whole number greater than 0" / "Maximum 100,000 credits per outlet" / "Enter a top-up for at least one outlet"\nAction: block NEXT. Entered values are kept.',400),
     ('d4','dec',MX,'Billing email present and valid for every selected company?',320),
     ('e4','err',EX,'ERR-04  "Billing email missing or invalid for {company}. Update the client record first."\nAction: block NEXT. No quotation, no credits.',400),
     ('p5','proc',MX,'Click NEXT: lock the button and create an idempotency key',300),
     ('p6','proc',MX,'Call the QuickBooks API to generate a quotation, one line item per company',320),
     ('d5','dec',MX,'Quotation generated?',260),
     ('e5','err',EX,'ERR-05  "Quotation could not be generated. No credits have been added."\nAction: retry with the SAME idempotency key, so no duplicate quotation and no partial credit.',400),
     ('p7','proc',MX,'Credit SMS to EACH company account in one atomic transaction (balance = balance + top-up)',330),
     ('d6','dec',MX,'All credits committed?',260),
     ('e6','err',EX,'ERR-06  "Top-up failed. No credits were added."\nAction: roll back the transaction, void or flag the quotation, alert finance for reconciliation.',400),
     ('p8','proc',MX,'Send the quotation email to the company billing address',300),
     ('d7','dec',MX,'Email sent?',240),
     ('e7','err',EX,'WARN-01  "Quotation created and credits added, but the email could not be sent."\nAction: queue a retry and offer Resend. Credits REMAIN valid.',400),
     ('p9','proc',MX,'Write the audit log: user, brand, companies, amounts, quotation number, timestamp',330),
     ('end','term',MX,'END: success screen with the quotation number and the updated balance per company',320),
    ]
    edges=[('start','p1',''),('p1','d1',''),('d1','p2','Yes'),('d1','e1','No'),('p2','d2',''),('d2','p3','Yes'),('d2','e2','No'),
     ('p3','p4',''),('p4','d3',''),('d3','d4','Yes'),('d3','e3','No'),('d4','p5','Yes'),('d4','e4','No'),('p5','p6',''),
     ('p6','d5',''),('d5','p7','Yes'),('d5','e5','No'),('p7','d6',''),('d6','p8','Yes'),('d6','e6','No'),('p8','d7',''),
     ('d7','p9','Yes'),('d7','e7','No'),('p9','end','')]
    N={}; y=30; main_gap=34
    for nid,kind,x,text,w in rows:
        fs=11.5
        ls=wrap(text,w-30,fs)
        need=max(w, max(tw(l,fs) for l in ls)+30)
        h=len(ls)*LH+(30 if kind=='dec' else 20)
        if kind=='dec': h=max(h,64)+10; need+=150
        N[nid]=dict(kind=kind,x=x,w=need,h=h,ls=ls,fs=fs,y=None)
    # lay out main column sequentially; error nodes align to their source decision
    ymain=30
    order=[r[0] for r in rows if r[2]==MX]
    for nid in order:
        N[nid]['y']=ymain; ymain+=N[nid]['h']+main_gap
    for a,b,lab in edges:
        if N[b]['x']==EX and N[b]['y'] is None:
            N[b]['y']=N[a]['y']+N[a]['h']/2-N[b]['h']/2
    H=ymain+10
    o=[f'<svg viewBox="0 0 1320 {int(H)}" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial,sans-serif">',
       '<defs><marker id="ar" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000"/></marker></defs>',
       f'<rect x="0" y="0" width="1320" height="{int(H)}" fill="#fff"/>']
    for a,b,lab in edges:
        A,B=N[a],N[b]
        if B['x']==EX:
            y=A['y']+A['h']/2
            o.append(f'<path d="M{A["x"]+A["w"]/2},{y} L{B["x"]-B["w"]/2},{B["y"]+B["h"]/2}" stroke="#000" fill="none" marker-end="url(#ar)"/>')
            o.append(f'<text x="{A["x"]+A["w"]/2+12}" y="{y-7}" font-size="11" fill="#000">{lab}</text>')
        else:
            o.append(f'<path d="M{A["x"]},{A["y"]+A["h"]} L{B["x"]},{B["y"]}" stroke="#000" fill="none" marker-end="url(#ar)"/>')
            if lab: o.append(f'<text x="{A["x"]+8}" y="{A["y"]+A["h"]+17}" font-size="11" fill="#000">{lab}</text>')
    for nid,n in N.items():
        x,y,w,h,ls,fs=n['x'],n['y'],n['w'],n['h'],n['ls'],n['fs']
        if n['kind']=='dec':
            o.append(f'<polygon points="{x},{y} {x+w/2},{y+h/2} {x},{y+h} {x-w/2},{y+h/2}" fill="#fff" stroke="#000"/>')
        elif n['kind']=='err':
            o.append(f'<rect x="{x-w/2}" y="{y}" width="{w}" height="{h}" rx="3" fill="#f2f2f2" stroke="#000" stroke-dasharray="5,3"/>')
        elif n['kind']=='term':
            o.append(f'<rect x="{x-w/2}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
        else:
            o.append(f'<rect x="{x-w/2}" y="{y}" width="{w}" height="{h}" rx="3" fill="#fff" stroke="#000"/>')
        ty=y+h/2-(len(ls)-1)*LH/2+4
        for i,l in enumerate(ls):
            o.append(f'<text x="{x}" y="{ty+i*LH}" font-size="{fs}" text-anchor="middle" fill="#000">{esc(l)}</text>')
    o.append('</svg>'); open(path,'w').write('\n'.join(o)); return H
h=flowchart('flow.svg'); print('flow.svg', int(h))

# ---------------- state machine ----------------
import math
def statechart(path):
    R=64
    S={'S0':(210,70,'S0|Idle|(page open)'),'E1':(830,70,'E1|Brand list|error'),
       'S1':(210,265,'S1|Outlets|loaded'),'E2':(830,265,'E2|No outlets|under brand'),
       'S2':(210,460,'S2|Valid input|entered'),'E3':(830,460,'E3|Validation|error'),
       'S3':(210,690,'S3|Submitting|(quotation)'),'E4':(830,640,'E4|Billing email|missing'),
       'E5':(830,800,'E5|Quotation|failed'),'S4':(210,920,'S4|Quotation|created'),
       'E6':(830,990,'E6|Credit write|failed'),'S5':(210,1140,'S5|Credits|committed'),
       'E7':(830,1200,'E7|Email|failed'),'S6':(210,1350,'S6|Complete')}
    T=[('T01','S0','S1',0),('T02','S0','E1',0),('T03','E1','S0',1),('T04','S0','E2',0),('T05','E2','S0',1),
       ('T06','S1','S2',0),('T07','S1','E3',0),('T08','E3','S2',1),('T09','S2','E4',0),('T10','S2','S3',0),
       ('T11','S3','E5',0),('T12','E5','S4',1),('T13','S3','S4',0),('T14','S4','E6',0),('T15','S4','S5',0),
       ('T16','S5','E7',0),('T17','E7','S6',1),('T18','S5','S6',0)]
    H=1450
    o=[f'<svg viewBox="0 0 1150 {H}" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial,sans-serif">',
       '<defs><marker id="ar2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#000"/></marker></defs>',
       f'<rect x="0" y="0" width="1150" height="{H}" fill="#fff"/>']
    for tid,f,t,curve in T:
        x1,y1,_=S[f]; x2,y2,_=S[t]; dx,dy=x2-x1,y2-y1; d=math.hypot(dx,dy) or 1
        sx,sy=x1+dx/d*R,y1+dy/d*R; ex,ey=x2-dx/d*(R+8),y2-dy/d*(R+8)
        if curve:
            mx,my=(sx+ex)/2-120,(sy+ey)/2
            o.append(f'<path d="M{sx},{sy} Q{mx},{my} {ex},{ey}" stroke="#000" fill="none" stroke-dasharray="5,3" marker-end="url(#ar2)"/>')
            lx,ly,anc=mx-6,my,'end'
        else:
            o.append(f'<path d="M{sx},{sy} L{ex},{ey}" stroke="#000" fill="none" marker-end="url(#ar2)"/>')
            lx,ly,anc=(sx+ex)/2+8,(sy+ey)/2-7,'start'
        o.append(f'<text x="{lx}" y="{ly}" font-size="12.5" font-weight="bold" text-anchor="{anc}" fill="#000">{tid}</text>')
    # T21 cancel: S2 -> S0 (left)
    x1,y1,_=S['S2']; x2,y2,_=S['S0']
    o.append(f'<path d="M{x1-R},{y1} C{x1-155},{y1} {x2-155},{y2} {x2-R},{y2}" stroke="#000" fill="none" stroke-dasharray="5,3" marker-end="url(#ar2)"/>')
    o.append(f'<text x="{x1-132}" y="{(y1+y2)/2}" font-size="12.5" font-weight="bold" text-anchor="end" fill="#000">T21</text>')
    # self loops on S3
    x,y,_=S['S3']
    for i,tid in enumerate(['T19','T20']):
        off=i*34
        o.append(f'<path d="M{x+22},{y-R+12} C{x+130+off},{y-46-off} {x+130+off},{y+46+off} {x+22},{y+R-12}" stroke="#000" fill="none" stroke-dasharray="5,3" marker-end="url(#ar2)"/>')
        o.append(f'<text x="{x+124+off}" y="{y+5}" font-size="12.5" font-weight="bold" text-anchor="start" fill="#000">{tid}</text>')
    for sid,(x,y,lab) in S.items():
        err=sid.startswith('E')
        o.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="#fff" stroke="#000" stroke-width="{1.2 if err else 1.8}" {"stroke-dasharray=\'5,3\'" if err else ""}/>')
        ls=lab.split('|'); ty=y-(len(ls)-1)*7+4
        for i,l in enumerate(ls):
            o.append(f'<text x="{x}" y="{ty+i*14}" font-size="{12.5 if i==0 else 10.5}" font-weight="{"bold" if i==0 else "normal"}" text-anchor="middle" fill="#000">{esc(l)}</text>')
    o.append('</svg>'); open(path,'w').write('\n'.join(o))
statechart('state.svg'); print('state.svg ok')
