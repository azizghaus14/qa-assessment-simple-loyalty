import textwrap
W,H=1150,1500
S={  # id:(x,y,label)
 'S0':(200,60,'S0\nIdle\n(page open)'),
 'E1':(760,60,'E1\nBrand list\nerror'),
 'S1':(200,250,'S1\nOutlets\nloaded'),
 'E2':(760,250,'E2\nNo outlets\nunder brand'),
 'S2':(200,440,'S2\nValid input\nentered'),
 'E3':(760,440,'E3\nValidation\nerror'),
 'S3':(200,650,'S3\nSubmitting\n(quotation)'),
 'E4':(760,620,'E4\nBilling email\nmissing'),
 'E5':(760,760,'E5\nQuotation\nfailed'),
 'S4':(200,880,'S4\nQuotation\ncreated'),
 'E6':(760,950,'E6\nCredit write\nfailed'),
 'S5':(200,1090,'S5\nCredits\ncommitted'),
 'E7':(760,1160,'E7\nEmail\nfailed'),
 'S6':(200,1300,'S6\nComplete'),
}
R=62
T=[ # (id, from, to, label, curve)
 ('T01','S0','S1','select brand (has outlets) /\nshow outlets + balances',0),
 ('T02','S0','E1','open page, brand list fails /\nERR-01 + Retry',0),
 ('T03','E1','S0','retry, service restored /\nbrand list shown',1),
 ('T04','S0','E2','select brand with 0 outlets /\nERR-02',0),
 ('T05','E2','S0','back to brand selection /\nclear selection',1),
 ('T06','S1','S2','enter valid amounts /\nenable NEXT',0),
 ('T07','S1','E3','enter invalid amount /\nERR-03 inline, keep values',0),
 ('T08','E3','S2','correct the input /\nclear error, enable NEXT',1),
 ('T09','S2','E4','click NEXT, billing email missing /\nERR-04, no quotation, no credits',0),
 ('T10','S2','S3','click NEXT, all valid /\nlock button, create idempotency key',0),
 ('T11','S3','E5','QuickBooks error or timeout /\nERR-05, no credits added',0),
 ('T12','E5','S4','retry with same idempotency key /\nexactly one quotation',1),
 ('T13','S3','S4','quotation generated /\nquotation number issued',0),
 ('T14','S4','E6','credit transaction fails /\nERR-06, roll back, void quotation',0),
 ('T15','S4','S5','credits committed atomically /\nbalance = balance + top-up per company',0),
 ('T16','S5','E7','email send fails /\nWARN-01, credits remain valid',0),
 ('T17','E7','S6','manual or queued resend /\nemail delivered, no re-credit',1),
 ('T18','S5','S6','email sent /\nwrite audit log, success screen',0),
]
SELF=[('T19','S3','double submit / blocked by idempotency key'),
      ('T20','S3','session expires / re-auth, resume once')]
BACK=[('T21','S2','S0','cancel or navigate away / discard, no writes')]
def esc(s): return s.replace('&','&amp;').replace('<','&lt;')
o=[f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial,sans-serif">',
   '<defs><marker id="a" markerWidth="9" markerHeight="9" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#333"/></marker></defs>']
import math
def edge(f,t,label,curve):
    x1,y1,_=S[f]; x2,y2,_=S[t]
    dx,dy=x2-x1,y2-y1; d=math.hypot(dx,dy) or 1
    sx,sy=x1+dx/d*R, y1+dy/d*R; ex,ey=x2-dx/d*(R+7), y2-dy/d*(R+7)
    if curve:
        mx,my=(sx+ex)/2-110,(sy+ey)/2
        o.append(f'<path d="M{sx},{sy} Q{mx},{my} {ex},{ey}" stroke="#555" fill="none" stroke-dasharray="4,3" marker-end="url(#a)"/>')
        lx,ly=mx-10,my
        anchor='end'
    else:
        o.append(f'<path d="M{sx},{sy} L{ex},{ey}" stroke="#333" fill="none" marker-end="url(#a)"/>')
        lx,ly=(sx+ex)/2+8,(sy+ey)/2-6
        anchor='start'
    tid=label.split(':')[0]
    o.append(f'<text x="{lx}" y="{ly}" font-size="12" font-weight="bold" text-anchor="{anchor}" fill="#0958d9">{esc(tid)}</text>')
for tid,f,t,lab,c in T: edge(f,t,tid+': '+lab,c)
for tid,f,t,lab in BACK:
    x1,y1,_=S[f]; x2,y2,_=S[t]
    o.append(f'<path d="M{x1-R},{y1} C{x1-150},{y1} {x2-150},{y2} {x2-R},{y2}" stroke="#555" fill="none" stroke-dasharray="4,3" marker-end="url(#a)"/>')
    o.append(f'<text x="{x1-128}" y="{(y1+y2)/2}" font-size="12" font-weight="bold" text-anchor="end" fill="#0958d9">{esc(tid)}</text>')
for tid,s,lab in SELF:
    x,y,_=S[s]
    off=0 if tid=='T19' else 30
    o.append(f'<path d="M{x+20},{y-R+10} C{x+120+off},{y-40-off} {x+120+off},{y+40+off} {x+20},{y+R-10}" stroke="#555" fill="none" stroke-dasharray="4,3" marker-end="url(#a)"/>')
    o.append(f'<text x="{x+112+off}" y="{y+4}" font-size="12" font-weight="bold" text-anchor="start" fill="#0958d9">{esc(tid)}</text>')
for sid,(x,y,lab) in S.items():
    err=sid.startswith('E')
    o.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="{"#fff1f0" if err else "#e6f4ff"}" stroke="{"#cf1322" if err else "#0958d9"}" stroke-width="{1.6 if not err else 1.2}"/>')
    ls=lab.split('\n'); ty=y-(len(ls)-1)*7+4
    for i,l in enumerate(ls):
        w='bold' if i==0 else 'normal'
        o.append(f'<text x="{x}" y="{ty+i*14}" font-size="{12 if i==0 else 10.5}" font-weight="{w}" text-anchor="middle" fill="#111">{esc(l)}</text>')
o.append('</svg>')
open('state.svg','w').write('\n'.join(o))
print('state.svg ok')
