---
name: 🟡 Data question
about: A number is technically computed but doesn't match what you would have computed from the underlying data.
title: "[Data] "
labels: ["question", "data"]
---

> Often the answer is in [`docs/METHODOLOGY.md`](../../blob/main/docs/METHODOLOGY.md)
> or [`docs/DATA_MODEL.md`](../../blob/main/docs/DATA_MODEL.md). Skim them
> first — but if the answer isn't there, file the question.

### The number you saw
<!-- KPI / chart / table, the value, the page where it appears. -->

### The number you expected
<!-- Your reference computation. Show the math if possible. Examples:
- "DSO 55d, but I expected ~50d because Open AR €38.3M ÷ trailing 90d
   sales ~€21M × 90 = 50d."
- "Cash on hand €18.28M, but I expected €19M because Op EUR is €8.5M +
   Op DE €2.4M + ... = €19.32M." -->

### Underlying data you checked
<!-- Files / columns from data/ that you examined to derive the
expected number. -->

### Hypothesis
<!-- Your best guess on why they might not match — FX rounding,
calendar convention, RCF inclusion/exclusion, weekend FX gap, etc. -->

### Outcome you'd like
- [ ] Correct the number (this is actually a bug)
- [ ] Document the convention more explicitly in `docs/METHODOLOGY.md`
- [ ] Add a tooltip in the app explaining the formula
- [ ] Just confirm the number is right and close
