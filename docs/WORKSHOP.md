# Workshop — 45 minutes, 1 operator on a phone, 30 treasurers in the room

> Goal: have 30 junior treasurers leave the room saying *"I can do this on
> my phone on Monday morning."* The hard constraint: only **one** Claude
> Code access, on the facilitator's phone. No teams, no parallel laptops.
> Engagement has to come from elsewhere.

This is the **solo-operator** format. A separate plan would apply if you had
6 laptops and could split into teams; that earlier version is in git
history.

---

## 1. The constraint, reframed as a feature

**One operator, 30 spectators** is usually death by passivity. But it has
two things going for it:

1. **The audience is the prompt-writer, collectively.** They're not watching
   a pre-recorded demo — they decide what gets built next, in real time.
   That's the entire pedagogy: *the human in "human-in-the-loop" is them*.
2. **The phone constraint is the message.** If the lesson is "AI lets a
   non-developer ship treasury tools fast", then doing it on a phone in
   front of them proves the point harder than any laptop demo would. They
   recognise the tool — it's the same phone they use for emails.

So the format is built around **continuous audience involvement** through
four mechanisms (§4), and the phone is on stage, not hidden.

---

## 2. Setup — what has to be true 30 minutes before kick-off

Hard requirements:

- The operator's phone **mirrors to the room screen** (HDMI dongle, AirPlay,
  Chromecast — tested at least once before the day).
- The repo is **already cloned** on the phone (Claude Code on iOS / Android,
  authenticated, working directory set to the project root).
- `python data/generate_data.py` and `streamlit run app.py` have **already
  been validated** earlier the same day — running on a small cloud VM
  (Streamlit Cloud / Hugging Face Spaces / Render) that the phone hits via
  browser. The phone shouldn't try to run Streamlit locally.
- A **second screen** in the room shows the live Streamlit app. So the
  audience sees: code prompt on one screen, app refreshing on the other.
- A **live poll system** is set up — Slido, Mentimeter, or a Google Form
  with a QR code projected from the start. The QR code is on a slide and
  visible during the whole session.
- The operator has a **wired microphone** (a phone screen + a soft voice
  loses the back rows in 90 seconds).
- A **facilitator** (different person from the operator) runs the room:
  reads polls, calls volunteers, keeps time. The operator focuses on the
  phone.

**T-30 minute checklist** (printed on a card the operator carries):

```
[ ] Phone connected to room screen, mirroring works
[ ] Streamlit app reachable on second screen
[ ] Claude Code session live, last test prompt executed cleanly
[ ] QR code for live poll on opening slide
[ ] Microphone on, levels checked
[ ] Timer visible (35-min countdown when construction starts)
[ ] Take-home memo printed × 30
```

---

## 3. The 45-minute breakdown

| Min | Block | Lead | What happens |
|-----|-------|------|--------------|
| 00–04 | **Frame & ground rules** | Facilitator | Pitch (script in §6). QR code shown — everyone joins the live poll right now. |
| 04–09 | **Anchor demo** | Operator | One single, low-stakes prompt run live to show "the loop": prompt → diff → accept → app updates. Picks a deliberately clear win (§7, demo prompt). |
| 09–22 | **Round 1: audience as Product Owner** | Both | 13 min. Audience picks the next feature from a 4-option menu via live poll. Operator builds the winner. Continuous narration. |
| 22–32 | **Round 2: hot-seat prompt-craft** | Both | 10 min. 3 volunteers come to the front, **dictate** their prompts for the same small task. Operator types each. Audience scores via poll. |
| 32–40 | **Round 3: stump the AI** | Both | 8 min. Audience submits free-text feature ideas via the form. Facilitator picks the gnarliest. Operator runs it. Show the failure modes too. |
| 40–45 | **Debrief & memo** | Facilitator | 5 min. Live poll: what did you learn? Distribute take-home memo. Last word from operator. |

**Time discipline**: the facilitator owns the clock, not the operator.
Operator is allowed to say *"I want 90 more seconds"*, but only if the
facilitator agrees. If we're behind, we cut Round 3, never Round 1 (it's
the most engagement per minute).

---

## 4. The four engagement mechanisms

These run **continuously** in the background of the three rounds. They turn
"30 people watching one phone" into "30 people steering one phone".

### 4.1 Live poll (always on)

A QR code on the screen leads to a single Slido / Mentimeter event.
Throughout the session, the facilitator pushes 5–6 polls:

- **Round 1 menu** (4 options, multiple choice, 60-second window).
- **Hot-seat scoring** (3 prompts × 3 axes: clarity / specificity / did-it-work).
- **Stump-the-AI submissions** (open text, audience upvotes).
- **Final retro** (1-question slider: *"how confident am I to try this on
  Monday?"* on a 1–10 scale).

A poll every ~7 minutes is the rhythm. Less than that and the back rows
disengage; more and it becomes mechanical.

### 4.2 Predict-then-watch

Before the operator hits Enter on each prompt, the facilitator asks the
room out loud:

> *"Show of hands — who thinks this prompt will succeed first try?"*

Then the prompt runs. The audience either celebrates the prediction or
laughs at the failure. **It costs 8 seconds and turns every prompt into a
shared bet.** The whole room watches the diff because they have skin in the
game.

### 4.3 The AI-watch scorecard

A printed A6 card on each chair, ticked silently:

```
AI-WATCH SCORECARD                Name: ____________

   [ ] One prompt succeeded first try
   [ ] One prompt needed re-prompting
   [ ] One prompt produced a real bug we caught
   [ ] One feature changed my mind about what's possible
   [ ] One thing the AI did better than I expected
   [ ] One thing the AI did worse than I expected

What I'll prompt myself on Monday:
   _________________________________________________
```

The card gives shy participants a way to be active without speaking. The
last line is the **only** deliverable that matters: it's their commitment.

### 4.4 The hot-seat (Round 2)

The single piece of "performance" in the session. Three volunteers come to
the mic and dictate their prompts for the same task. Operator types
verbatim. The room sees prompt quality drive output quality, side by side.
This is the moment that shifts treasurers from *"AI is magic"* to *"AI is
a tool I write specifications for"*.

---

## 5. Choosing the room screen layout

The dual-screen layout is non-negotiable. Suggestion:

```
┌──────────────────────────────┬──────────────────────────────┐
│                              │                              │
│   PHONE MIRROR               │   STREAMLIT APP              │
│   (Claude Code,              │   (live Helios dashboard)    │
│    prompt + diff)            │                              │
│                              │                              │
│                              │                              │
└──────────────────────────────┴──────────────────────────────┘
       ┌────────────────────────────────────────────┐
       │   POLL SLIDE / QR CODE / TIMER             │
       └────────────────────────────────────────────┘
```

If only one big screen is available, split it 60/40 — phone mirror left,
Streamlit app right. Polls go on the facilitator's laptop screen at the
front of the room.

---

## 6. Opening pitch (4 minutes — script)

> *"Welcome. In front of you: a treasury app for a fictional industrial
> group. €38M of open AR, €13M of open AP, eight bank accounts in three
> currencies, a 13-week forecast, three stress scenarios. It was built in
> two hours by an AI that I controlled by typing what I wanted."*
>
> *"Here's what's different about today: I will not show you a polished
> demo. I will let you decide what to build next, on my phone, in real
> time. Three rounds. You will pick the features. You will score the
> prompts. You will throw the AI off a cliff in round three. I am the
> typist. You are the product owner."*
>
> *"Three ground rules:*
> *— Specific beats clever. 'Add a chart' is a bad prompt. 'Add a
>    horizontal bar chart on the AR page showing top-five customers by
>    open balance, in EUR' is a good one.*
> *— Watch the diff. The AI is wrong about 1 time in 5. We accept nothing
>    blind.*
> *— You scan this QR code now."* (point to it)

The pitch is precisely 4 minutes. Time it once before the day. Trim ruthlessly.

---

## 7. The prompt sequence (with backups)

The operator carries a printed prompt menu. Here's the canonical sequence;
the facilitator can swap any item if the audience steers somewhere else.

### Anchor demo prompt — 4 minutes (always run this one)

> *"In `app.py`, add a 9th KPI card called 'AR overdue %'. It shows the
> share of open AR (in EUR) where `due_date` is before today, divided by
> total open AR. Display as a percentage with one decimal. Colour the
> value red if > 15%, otherwise default. Use `src.metrics.aging_buckets`
> if helpful."*

Why this prompt: small surface, visible result, uses an existing function,
has a clear pass/fail. The audience sees the dashboard reload with a new
red number. Confidence anchored.

### Round 1 menu (4 options for live vote — pick one to build)

| Option | Headline | Why it's a good choice |
|--------|----------|-------------------------|
| **A** | Heatmap of expected receipts | Visual, on the Forecast page, 8 minutes of work |
| **B** | M&A simulator slider | Interactive, shows direct impact on closing balance |
| **C** | Bank-fee anomaly detector | New page, shows AI handling a "find outliers" prompt |
| **D** | Customer concentration score (Herfindahl + top-3 share) | Treasury-relevant, fits in 8 minutes, opinionated risk threshold |

The facilitator reads each option in 30 seconds. Poll runs 60 seconds. The
winner gets built in 8 minutes. The operator carries a pre-written prompt
for **all four** so there's no on-the-fly authoring stress.

Example pre-written prompt for option **D**:

> *"In `src/metrics.py`, add a function `customer_concentration(ar)` that
> returns a dict with `herfindahl` (sum of squared customer shares of open
> AR) and `top3_share` (share of the three largest open-AR customers).
> Then in the Receivables tab of `pages/3_Receivables_Payables.py`, show
> two new KPIs above the aging chart: 'Concentration HHI' and 'Top-3
> share'. Colour the top-3 share red if > 0.40."*

### Round 2 hot-seat task (3 volunteers each prompt this)

The same task is set, three different prompts.

> Task announced to the room: *"Add a button on the Forecast page that
> exports the current 13-week forecast lines as CSV."*

Volunteers come up one at a time, dictate their prompt, the operator types
it verbatim, hits Enter, audience watches the result, scores via poll, next
volunteer.

This deliberately tests: did they specify the file? did they specify the
column ordering? did they specify the file name? Three different prompts
will produce three different outcomes — the comparison is the lesson.

### Round 3 — "stump the AI"

Audience submits free-text feature ideas via the form. Facilitator surfaces
the 5 most-upvoted, picks the gnarliest one that fits in ~8 minutes.
Examples of the kind of prompts that have shown up in similar workshops:

- *"Project the cash position 2 years out and show when we run out of
  RCF."* (Hard: requires extrapolating revenue trend, calibrating decay,
  hitting the RCF limit logic.)
- *"Add a Slack notification when DSO drifts more than 5 days."* (Hard:
  needs an external service, the AI will likely stub it — good teaching
  moment about dependencies.)
- *"Replace all charts with prettier ones."* (Hard for the right reasons:
  vague. Operator should reject the prompt and ask the audience to
  rewrite it. Pedagogically valuable.)

The win condition for Round 3 is **not** that the feature works perfectly —
it's that the audience sees the AI struggle, iterate, and eventually
deliver something. Failure-on-stage is the most under-used teaching
moment in AI demos.

---

## 8. The take-home memo (printed × 30)

A single A5 card, given out at minute 40:

```
VIBE CODING FOR TREASURERS — THE 5 REFLEXES

1. SCOPE       One feature per prompt. One file. One acceptance test.
2. ANCHOR      Always name the exact file to modify.
3. DATA-FIRST  State the columns, the units, the period.
4. TEST        Define the acceptance criterion BEFORE prompting.
5. ITERATE     The AI is wrong 1 time in 5. Read the diff.
               Re-prompt; don't accept blind.

THE PROMPT TEMPLATE
───────────────────
In <file>, add <feature>.
Acceptance: <a measurable, observable result>.
Data: <files / columns to use>.
Style: follow <reference file>.

WHAT TO TRY ON MONDAY
─────────────────────
On your own dataset (even an Excel export):
1. Generate 24 months of synthetic data with one prompt.
2. Build a Streamlit dashboard with a second prompt.
3. Stop. That's the demo. Iterate from there.
```

This card is the artefact that survives the session. Everything else is
ephemera.

---

## 9. Risks and plan B

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Phone screen mirroring fails | Medium-high | Pre-tested twice. Fallback: facilitator's laptop SSHes into a hosted Claude Code session on a tablet, audience watches that screen instead. |
| Wifi drops mid-prompt | Medium | Pre-cache the most likely 6 prompts on the phone. Use a 5G hotspot as backup. |
| One prompt eats 6 minutes | High | Operator must say *"I'm cutting this"* aloud at 3 min and explain why. Showing how to abort is part of the lesson. |
| Audience disengages in Round 2 | Medium | Hot-seat scoring poll is mandatory; facilitator moves the room to vote actively. |
| Volunteers don't come up | Medium | Facilitator pre-recruits 5 candidates during the coffee break. Never ask the room cold. |
| AI produces something unsafe / weird | Low | Operator always reads the diff aloud before accepting. If it's weird, REJECT on stage — this is the best teaching moment of the day. |
| The whole thing falls flat | Low | Plan B: facilitator narrates a pre-recorded screencast of the same flow, polls still run. The session still delivers the memo. |

---

## 10. Success criteria

Measured in the final 5-minute debrief:

1. **At least 4 prompts have been executed and accepted**, with visible
   results in the Streamlit app.
2. **At least 1 prompt has failed on stage**, been re-prompted, and
   eventually succeeded — making the failure mode tangible.
3. **The "Monday confidence" poll averages ≥ 7 / 10**.
4. **At least 5 take-home memos** come back with the "what I'll try on
   Monday" line filled in (collected at the door).
5. **At least 3 questions in the debrief** are about extending to real
   data (MT940, ERP, etc.) — signal that they're already past the demo
   and into operationalisation.

---

## 11. What you say in the last 60 seconds

> *"You did not watch a demo today. You ran a development team. The phone
> typed, but you specified, you scored, you steered, you rejected. The
> only thing that changes on Monday morning is that the phone in your
> pocket is mine, but the brain doing the steering is yours. Pick one
> repetitive treasury task you do every week. Open Claude on your phone
> tomorrow morning. Apply the five reflexes. Show me what you built next
> month."*

Then the operator hands the room screen back to the dashboard, and the
session ends on the working app — not on a slide.
