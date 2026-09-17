# Quality Assurance Engineering Intern — Assessment

Assessment submission for the Quality Assurance Engineering Intern role at Simple Loyalty
(SMS Credit Reload feature for the GoSMS product).

**Hosted version:** https://azizghaus14.github.io/qa-assessment-simple-loyalty/

## Contents

| File | Description |
|---|---|
| `index.html` | Full submission: assumptions, state transition model, transition table, flowchart with error handling, test cases |
| `Aziz-Ghaus-QA-Assessment.pdf` | Same document as a PDF |
| `State-transition-diagram.png`, `state.svg` | State transition diagram |
| `Flowchart.png`, `flow.svg` | Process flowchart with error handling |
| `diagrams.py` | Script that generates both diagrams |

## Summary

The feature lets a finance executive top up prepaid SMS credits for outlets under a brand,
generating a QuickBooks quotation and crediting the client's account.

Three decisions shape the design and the tests:

1. **Credits are held per company (billing entity), not per brand.** A brand can span several
   companies, so one submission may bill more than one entity. Tests TC-21 to TC-23 cover this.
2. **The quotation is the commit point.** Credits are applied only after QuickBooks confirms,
   and all credits are written in a single atomic transaction so a partial top-up cannot occur.
3. **A failed email does not reverse the credits.** It raises a warning and offers a resend,
   because reversing credits the client has already been quoted for is the worse outcome.

An idempotency key prevents a retry or a double click from creating a second quotation or
double credits (TC-10, TC-18, TC-19).

The feature is modelled as a state machine using the four elements of state transition testing:
**states**, **transitions**, **events** and **actions**. 21 transitions (T01-T21) are listed in a
State / Event / Action / Next-state table, and 27 test cases cover each transition exactly once
plus six business rules (R1-R6), with every case traceable to the transition or rule it verifies.

T07 (valid input -> validation error) is one transition reached by six different invalid inputs,
so it is written as a single data-driven case rather than six near-identical ones.

Syed Muhammad Aziz Ghaus · azizghaus14@gmail.com
