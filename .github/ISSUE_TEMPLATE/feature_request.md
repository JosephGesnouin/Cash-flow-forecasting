---
name: 🟢 Feature request (treasury PO)
about: Propose a new KPI, page, slider, alert, export — anything that adds capability.
title: "[Feature] "
labels: ["enhancement", "needs-triage"]
---

> Read the [README §9](../../blob/main/README.md#9-propose-an-update--file-a-github-issue)
> before filing — it includes a worked example of a great feature request.

### What treasury question are you trying to answer?
<!-- One or two sentences in treasurer's terms. What real-world pain or
question motivates this? What is the cost of NOT doing it? -->

### Acceptance criteria
<!-- Use the GIVEN / WHEN / THEN format. This is the most important part
of the issue. If you can't write it, you don't have a feature yet —
you have a wish. See README §8.6 for a worked example. -->

```
GIVEN  <starting state of the app — which page, which data, which assumption>
WHEN   <the user action — opens, clicks, configures>
THEN   <observable result — a value shown, a chart updated, an alert>
AND    <a measurable, falsifiable secondary check>
```

### Where in the app?
<!-- Tick all that apply. -->
- [ ] Dashboard
- [ ] Forecast
- [ ] Scenarios
- [ ] Receivables / Payables
- [ ] Bank Accounts
- [ ] Variance
- [ ] New page

### Data needed
<!-- Which existing files / columns are needed? Reference functions in
src/ where possible — saves the developer 20 minutes. Example:
"Use src.metrics.dso(ar, today). Inputs: data/ar_invoices.csv, columns
[issue_date, payment_date, status, amount_eur]." -->

### Effort estimate (your guess)
- [ ] **S** — under an hour for someone who knows the codebase
- [ ] **M** — half a day
- [ ] **L** — full sprint or more

### Why now? (priority)
<!-- One sentence quantifying the cost of not doing it. Examples:
- "We missed a €450k working-capital drift last quarter."
- "Audit is asking for this in the Q3 review."
- "Stress scenario currently breaches our buffer; we need to model
   the corrective action." -->

### References
<!-- Links to relevant docs/, screenshots, mockups, related issues. -->
- `docs/METHODOLOGY.md` §
- `docs/USER_GUIDE.md` §

### Optional: a draft prompt
<!-- If you want to ship this feature yourself with Claude Code, paste
the prompt you would give the AI. The maintainer can use it as the
starting point. -->
