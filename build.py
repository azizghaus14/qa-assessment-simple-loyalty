import json
TITLE="Quality Assurance Engineering Intern - Assessment"
SUB="SMS Credit Reload feature (MikeTango / GoSMS) | Syed Muhammad Aziz Ghaus | azizghaus14@gmail.com | +60 17-414 7089"
INTRO=("Assessment 1 describes the SMS Credit Reload feature and how it is intended to work. "
 "This document is the response to Assessment 2: Part 1 is the flowchart for the feature including error handling, "
 "and Part 2 is the set of test cases, supported by a state transition model that shows the coverage is complete.")
ASSUMPTIONS=[
 "SMS credits belong to a company (billing entity), not to a brand. One brand can span several companies, so a single submission may bill more than one entity.",
 "The quotation is the commit point: credits are added only once QuickBooks confirms the quotation was generated.",
 "Sending the quotation email is a separate, non-blocking step. If it fails, the quotation and credits stay valid and the email is retried, because reversing credits the client has already been quoted for is the worse outcome.",
 "Crediting several companies happens in one atomic transaction, so a partial top-up cannot occur.",
 "Each submission carries an idempotency key, so a retry or double click cannot produce a second quotation or double credits."]
STATES=[("S0","Page open, no brand selected"),("S1","Brand selected, outlets loaded"),("S2","Valid top-up amounts entered"),
 ("S3","Submitting (quotation request in flight)"),("S4","Quotation generated"),("S5","Credits committed"),
 ("S6","Complete (emailed, audit logged, success screen)"),("E1-E7","Error states, one per failure point in the flowchart")]
TRANS=[
("T01","S0","Select a brand that has outlets","Show outlet list with company (billing entity) and current balance","S1"),
("T02","S0","Open page, brand list fails to load",'ERR-01 "Unable to load brands. Please try again." + Retry',"E1"),
("T03","E1","Retry after service restored","Brand list displayed","S0"),
("T04","S0","Select a brand with no outlets",'ERR-02 "No outlets found under this brand."',"E2"),
("T05","E2","Return to brand selection","Selection cleared","S0"),
("T06","S1","Enter valid top-up amounts","NEXT enabled","S2"),
("T07","S1","Enter invalid amount","ERR-03 inline message; entered values kept","E3"),
("T08","E3","Correct the input","Error cleared, NEXT enabled","S2"),
("T09","S2","Click NEXT with missing/invalid billing email","ERR-04 naming the company; no quotation, no credits","E4"),
("T10","S2","Click NEXT with all data valid","Button locked, idempotency key created","S3"),
("T11","S3","QuickBooks error or timeout",'ERR-05 "No credits have been added." + Retry',"E5"),
("T12","E5","Retry with the same idempotency key","Exactly one quotation created","S4"),
("T13","S3","Quotation generated","Quotation number issued, line item per company","S4"),
("T14","S4","Credit transaction fails","ERR-06, transaction rolled back, quotation voided/flagged, finance alerted","E6"),
("T15","S4","Credits committed atomically","balance = balance + top-up, per company","S5"),
("T16","S5","Quotation email fails to send","WARN-01; credits and quotation remain valid; Resend offered","E7"),
("T17","E7","Resend (manual or queued)","Email delivered; credits not applied again","S6"),
("T18","S5","Quotation email sent","Audit log written; success screen shown","S6"),
("T19","S3","Second submit (double click)","Blocked by idempotency key; no duplicate quotation or credits","S3"),
("T20","S3","Session expires mid-submission","Re-authentication prompt; flow resumes once, single credit","S3"),
("T21","S2","Cancel or navigate away","All input discarded; no quotation, no credits, no audit entry","S0")]
REQS=[("R1","SMS credits are charged and credited to the company (billing entity), never to the brand as a whole"),
("R2","A single submission may cover outlets belonging to different companies"),
("R3","Only outlets with a top-up entered are quoted and credited"),
("R4","Quotation line totals, tax and grand total match the system calculation to 2 decimal places"),
("R5","A top-up increments the existing balance rather than replacing it"),
("R6","Every successful top-up is recorded in the audit log")]
TC=[
("TC-01","T01","Select a brand that has outlets","Brand 'SilverTree' has 3 outlets across 2 companies","Select 'SilverTree'","Outlet list shows all 3 outlets with outlet name, company and current SMS balance","Positive"),
("TC-02","T02","Brand list fails to load","Brand list service unavailable","Open the Top-Up page","ERR-01 shown with Retry. No data written anywhere","Negative"),
("TC-03","T03","Recover from brand list failure","ERR-01 displayed; service restored","Click Retry","Brand list loads; back in S0","Recovery"),
("TC-04","T04","Brand with no outlets","Brand 'EmptyBrand' has 0 active outlets","Select 'EmptyBrand'","ERR-02 shown; NEXT unavailable","Negative"),
("TC-05","T05","Return from the no-outlet state","ERR-02 displayed","Choose another brand","Selection cleared and the new brand's outlets load","Recovery"),
("TC-06","T06","Enter valid top-up quantities","Outlets displayed","Enter 500 for outlet A, 1000 for outlet B, leave C blank","Values accepted; NEXT enabled","Positive"),
("TC-07","T07","Invalid input (data-driven, single transition)","Outlets displayed","Enter in turn: 0 / -50 / 1.5 / abc / all blank / 100001","Matching ERR-03 message each time; NEXT stays disabled; valid values preserved","Negative"),
("TC-08","T08","Correct an invalid input","ERR-03 displayed","Replace the invalid value with 500","Error clears; NEXT enabled","Recovery"),
("TC-09","T09","Missing billing email","Outlet B's company has no billing email","Enter valid amounts, click NEXT","ERR-04 naming the company; no quotation, no credits","Negative"),
("TC-10","T10","Submit a valid top-up","Valid amounts; all billing emails present","Click NEXT","Button locks; idempotency key created; quotation requested","Positive"),
("TC-11","T11","QuickBooks unavailable","QuickBooks returns error/timeout","Click NEXT","ERR-05 shown; no quotation; no credits on any company","Negative"),
("TC-12","T12","Retry after QuickBooks failure","ERR-05 displayed; QuickBooks restored","Click Retry","Exactly one quotation exists; credits applied once","Recovery"),
("TC-13","T13","Quotation generated","Valid submission; QuickBooks healthy","Click NEXT","Quotation created with one line item per company matching the entered amounts","Positive"),
("TC-14","T14","Credit write fails after quotation","Quotation created; credit transaction fails mid-way","Complete submission","ERR-06; no company partially credited; quotation voided/flagged; finance alerted","Negative"),
("TC-15","T15","Credits committed per company","Quotation created successfully","Complete submission","Each company's balance rises by its own amount; other companies unchanged","Positive"),
("TC-16","T16","Quotation email fails","Credits committed; mail service down","Complete submission","WARN-01; credits and quotation remain valid; Resend offered","Negative"),
("TC-17","T17","Resend the quotation email","WARN-01 displayed; mail service restored","Click Resend","Email delivered; credits not applied a second time","Recovery"),
("TC-18","T18","Full happy path","All services healthy","Complete the flow","Email sent, audit log written, success screen shows quotation number and updated balances","Positive"),
("TC-19","T19","Double submission","Valid amounts entered","Click NEXT twice rapidly","One quotation and one credit transaction only","Negative"),
("TC-20","T20","Session expires during submission","Submission in flight; token expires","Complete submission","Re-authentication prompt; afterwards exactly one quotation and one set of credits","Negative"),
("TC-21","T21","Cancel mid-flow","Amounts entered, NEXT not clicked","Navigate away, then return","No quotation, no credits, no audit entry; clean form","Negative"),
("TC-22","R1","Credits are company-scoped","Brand spans Company X and Company Y","Top up an outlet belonging to Company X only","Only Company X is credited and billed; Company Y untouched","Business rule"),
("TC-23","R2","Several companies in one submission","Brand spans Company X and Company Y","Top up 500 for X's outlet and 800 for Y's outlet","Charges separated per billing entity, each emailed to its own address; X +500, Y +800","Business rule"),
("TC-24","R3","Partial fill of the outlet list","Brand has 3 outlets","Fill outlet A only","Only A's company is quoted and credited; B and C excluded entirely","Business rule"),
("TC-25","R4","Quotation totals and rounding","Amounts producing a fractional tax value","Submit","Line totals, tax and grand total match to 2 decimal places with no rounding drift","Business rule"),
("TC-26","R5","Balance is incremented, not overwritten","Company X holds 2,000 credits","Top up 500","Balance becomes 2,500","Business rule"),
("TC-27","R6","Audit trail completeness","Successful top-up","Complete flow, open audit log","Entry records user, brand, companies, amounts, quotation number and timestamp","Business rule")]
COVER1=("Every transition listed above is covered by exactly one test case, and no transition is tested twice. "
 "T07 is a single transition reached by six different invalid inputs, so it is written as one data-driven test case (TC-07) "
 "rather than six near-identical ones.")
COVER2=("Transition to test case: "+", ".join(f"T{ i+1:02d} - TC-{i+1:02d}" for i in range(21))+
 ". Business rules R1 to R6 are covered by TC-22 to TC-27.")
RISKS=[("Money and credits out of step (TC-11, TC-12, TC-14, TC-19, TC-20).","The expensive failure is a client billed without credits, or credited twice. The idempotency key and the atomic transaction are what prevent it."),
("Crediting the wrong entity (TC-22, TC-23, TC-24).","The brand-to-company split is the subtlest rule in the feature, so it gets dedicated tests."),
("Silent partial success (TC-14, TC-16).","The user must always be told exactly which of quotation, credits and email succeeded.")]
json.dump(dict(title=TITLE,sub=SUB,intro=INTRO,assumptions=ASSUMPTIONS,states=STATES,trans=TRANS,reqs=REQS,tc=TC,cover1=COVER1,cover2=COVER2,risks=RISKS),open('data.json','w'),indent=1)

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
flow=open('flow.svg').read(); state=open('state.svg').read()
rows=lambda d: "\n".join("<tr>"+"".join(f"<td>{esc(c)}</td>" for c in r)+"</tr>" for r in d)
html=f"""<!doctype html><html><head><meta charset="utf-8">
<title>QA Engineering Intern Assessment - SMS Credit Reload - Syed Muhammad Aziz Ghaus</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
@page{{size:A4;margin:13mm}}
body{{font:14px/1.55 Helvetica,Arial,sans-serif;color:#111;background:#fafafa;margin:0}}
.wrap{{max-width:1040px;margin:0 auto;padding:28px 22px 60px;background:#fff}}
h1{{font-size:20px;margin:0 0 3px;font-weight:bold}}
h2{{font-size:14.5px;margin:24px 0 8px;font-weight:bold}}
h3{{font-size:13px;margin:18px 0 6px;font-weight:bold}}
.sub{{color:#444;margin-bottom:14px;font-size:12.5px}}
table{{border-collapse:collapse;width:100%;font-size:12px;table-layout:fixed}}
th,td{{border:1px solid #999;padding:5px 7px;vertical-align:top;text-align:left;word-wrap:break-word}}
th{{background:#f5f5f5;font-weight:bold}}
ul{{margin:4px 0 4px 17px;padding:0}} li{{margin-bottom:4px}}
svg{{width:100%;height:auto;display:block;margin:6px auto}}
.note{{margin:8px 0 0;font-size:12.5px}} .cov{{font-size:11.5px;color:#333;margin:4px 0 0}}
@media print{{body{{font-size:11px;background:#fff}}.wrap{{max-width:none;padding:0}}table{{font-size:9px}}
.page{{page-break-before:always}}h2,h3{{page-break-after:avoid}}svg{{max-height:212mm;width:auto;margin:4px auto}}}}
@media screen{{.page{{display:none}}}}
</style></head><body><div class="wrap">
<h1>{TITLE}</h1><div class="sub">{SUB}</div>
<p>{INTRO}</p>
<h2>1. Assumptions</h2><ul>{"".join(f"<li>{esc(a)}</li>" for a in ASSUMPTIONS)}</ul>
<div class="page"></div>
<h2>2. Assessment 2, Part 1 - Flowchart (including error handling and messages)</h2>
{flow}
<div class="page"></div>
<h2>3. Assessment 2, Part 2 - Test cases</h2>
<h3>3.1 State transition model</h3>
<p style="margin:2px 0 6px">The feature is modelled with the four elements of state transition testing: <b>states</b> (the circles), <b>transitions</b> (the arrows), <b>events</b> (what triggers a transition) and <b>actions</b> (what the system does in response, including the message shown). Arrows are numbered; the event and action for each are listed in the transition table.</p>
{state}
<table><tr><th style="width:80px">State</th><th>Meaning</th></tr>{rows(STATES)}</table>
<h3>3.2 Transition table</h3>
<table><tr><th style="width:42px">ID</th><th style="width:52px">From</th><th style="width:210px">Event</th><th>Action (system response / message)</th><th style="width:52px">To</th></tr>{rows(TRANS)}</table>
<p class="note">{COVER1}</p><p class="cov">{COVER2}</p>
<h3>3.3 Business rules (traceability)</h3>
<table><tr><th style="width:42px">ID</th><th>Rule</th></tr>{rows(REQS)}</table>
<h3>3.4 Test cases</h3>
<p style="margin:0 0 6px">Each case is traceable to a transition (T) or business rule (R), and states its own preconditions and data so it can be repeated by anyone.</p>
<table><tr><th style="width:38px">ID</th><th style="width:34px">Ref</th><th style="width:104px">Title</th><th style="width:116px">Precondition</th><th style="width:116px">Steps</th><th>Expected result</th><th style="width:52px">Type</th></tr>{rows(TC)}</table>
<h2>4. Highest-risk areas</h2><ul>{"".join(f"<li><b>{esc(a)}</b> {esc(b)}</li>" for a,b in RISKS)}</ul>
</div></body></html>"""
open('assessment.html','w').write(html)
print('built html + data.json')
