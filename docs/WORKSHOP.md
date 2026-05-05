# Workshop — 45 minutes, 2 facilitators, 30 treasurers in the room

> Goal: every treasurer leaves saying *"I can do this on my phone on
> Monday morning."* The constraint: only **one** Claude Code access, on a
> phone. No team laptops. The asset: **two** facilitators in the room
> sharing the load — one runs the audience, one drives the phone.

This document is the operating manual for both facilitators. Read it once
each, then rehearse together (§4).

---

## 1. The setup, in one sentence

A **Host** holds the microphone and owns the room. An **Operator** holds
the phone and owns the code. Between them, the audience steers a single
Claude Code session live — no spectator passivity, no team-laptop chaos.

---

## 2. The two roles, sharply defined

The single most important thing in this workshop is that the Host and the
Operator **do not step on each other**. The split below is non-negotiable
during the live session — discussions happen during rehearsal, not on
stage.

### 2.1 The HOST

Owns: the **room**, the **clock**, the **polls**, the **narrative**.

Responsibilities:

- Holds the wireless microphone for the entire 45 minutes.
- Delivers the opening pitch (§9) and the closing 60 seconds (§16).
- Pushes each live poll on the projected screen (Slido / Mentimeter) and
  reads results aloud.
- Calls predict-then-watch shows of hands ("who thinks this prompt
  succeeds first try?").
- Recruits and brings up Round 2 volunteers.
- **Owns the countdown timer**. Calls "30 seconds left" on every block.
  Cuts the Operator if they overrun.
- Narrates what the Operator is doing for the audience: *"You can see
  Claude is opening `metrics.py` first — it found the existing aging
  function and is going to extend it."*
- Picks the Round 3 stump-the-AI prompt from audience submissions.
- Distributes the take-home memo at minute 40.

The Host **never** touches the phone. **Never** types a prompt. **Never**
debugs.

### 2.2 The OPERATOR

Owns: the **phone**, the **Streamlit app**, the **prompts**, the **diffs**.

Responsibilities:

- Holds the phone with Claude Code authenticated, working dir in the repo.
- Types every prompt verbatim (in Round 2, dictation from volunteers).
- **Reads the diff aloud** before accepting any change. *"It's editing
  `app.py`, line 47, adding a new metric call. Looks right. Accepting."*
- Hits accept / reject visibly. The audience sees the gesture.
- Refreshes the Streamlit app on the right screen after each accept and
  describes what changed.
- Catches errors and decides in 30 seconds: re-prompt or move on.
- Maintains the **prompt menu** (printed) and reads from it for Round 1
  pre-written prompts.
- During the Host's narration breaks, **silently pre-stages the next
  prompt** in the input box (does not press Enter).

The Operator **never** speaks while the Host is talking, except to read
diffs aloud or announce a result. Two voices simultaneously kills
audibility.

### 2.3 Cheat sheet (printed, one per facilitator)

```
HOST                                  OPERATOR
─────────────────────────────         ─────────────────────────────
Mic, clock, polls, narrative.         Phone, code, diffs, app.

YOU SAY:                              YOU SAY:
- The opening / closing pitches.      - "Reading the diff: <what>."
- "30 seconds left."                  - "Accepting." / "Rejecting."
- "Show of hands — predict?"          - "App is reloading."
- "We have a winner: option B."       - "Done — feature is live."
- Volunteer call-ups.                 - "Need 60 more seconds."

YOU DO NOT:                           YOU DO NOT:
- Touch the phone.                    - Touch the microphone.
- Type prompts.                       - Run polls.
- Debug code.                         - Manage the clock.
- Fix bugs on stage.                  - Speak during Host narration
                                        (except diffs / results).
```

---

## 3. Coordination signals (silent, on stage)

The Host and Operator agree on six gestures during rehearsal so they can
coordinate without breaking the room's attention.

| Signal | From | To | Meaning |
|--------|------|------|---------|
| 👍 thumb up | Operator | Host | "Ready to run / accepted, move on." |
| ✋ palm up | Operator | Host | "Buy me 30 seconds — I'm reading the diff." |
| ✋ palm down | Operator | Host | "I'm bailing on this prompt, please redirect." |
| 👇 finger to clock | Host | Operator | "You're at 90 seconds left." |
| ✊ fist tap | Host | Operator | "Skip ahead — we cut the rest." |
| 🤙 phone gesture | Either | Either | "Mic / phone glitch — give me a moment." |

These are practiced in rehearsal until they're reflexive.

---

## 4. The 45-minute joint rehearsal (the day before)

Block 45 minutes the day before the workshop. Both facilitators in a quiet
room, the actual phone, the actual screen-mirror dongle.

| Min | Activity |
|-----|----------|
| 00–05 | Read this document together. Agree on signals (§3). |
| 05–10 | Test screen mirroring. Test microphone. Test the Streamlit URL. |
| 10–25 | Operator runs the **anchor demo prompt** (§10). Host narrates as if 30 people were watching. Time it. Tighten. |
| 25–35 | Operator runs **two of the four Round-1 prompts** end-to-end. Host runs a fake poll on their phone, narrates, calls the predict-then-watch. Notice every place where you talked over each other. |
| 35–40 | Practise the volunteer call-up: Host pretends to call "Marie", brings them up, hands them the mic. Operator types a dictated prompt. Find the awkwardness. |
| 40–45 | Debrief. Agree on the cuts: which Round-1 option is too risky to leave on the menu? Which prompt needs to be pre-cached on the phone? |

If the rehearsal is skipped, the workshop will be 70% as good. The two of
you have to look like a band, not two soloists.

---

## 5. T-30 minute checklist (split by role)

Both arrive in the room 30 minutes before kick-off.

**HOST setup**

- [ ] Microphone tested at the back of the room
- [ ] Slido / Mentimeter event open, QR code on the opening slide
- [ ] Countdown timer on the slide deck (5 / 13 / 10 / 8 / 5 minute blocks)
- [ ] Take-home memos counted (×30) and stacked at the door
- [ ] Round 1 menu slide loaded (4 options, one per quadrant)
- [ ] Round 3 audience-input form open, QR ready on a separate slide

**OPERATOR setup**

- [ ] Phone connected to room screen, **mirroring tested with audience seats**
- [ ] Claude Code open, working dir in the repo, last test prompt clean
- [ ] Streamlit URL bookmarked on the second screen, app reachable
- [ ] Pre-written prompt menu printed and on the lectern
- [ ] Phone on charger that reaches the operator's seat
- [ ] Wifi + 5G hotspot both active, hotspot tested as fallback
- [ ] Notifications muted on the phone (do not skip — incoming WhatsApps on
      a mirrored screen are a session-ender)

**JOINT verification (10 min before doors open)**

- [ ] Host runs one fake poll, Operator votes — the poll updates on screen
- [ ] Host calls a fake volunteer ("come up here"), Operator hands them
      the mic from the other side of the stage — confirm the choreography
      works
- [ ] Operator runs the anchor demo prompt one more time. Host narrates.
      If anything feels rough, fix it now.

---

## 6. Room layout

```
┌──────────────────────────────┬──────────────────────────────┐
│                              │                              │
│   PHONE MIRROR               │   STREAMLIT APP              │
│   (Claude Code,              │   (live Helios dashboard,    │
│    prompt + diff)            │    auto-refresh)             │
│                              │                              │
└──────────────────────────────┴──────────────────────────────┘
       ┌────────────────────────────────────────────┐
       │   POLL SLIDE / QR CODE / TIMER             │
       │   (driven by the Host's laptop)            │
       └────────────────────────────────────────────┘

          [ HOST ]         [ AUDIENCE 30 ]         [ OPERATOR ]
            mic                                       phone
```

The Host stands stage-left near the laptop. The Operator sits stage-right
with the phone, screen mirroring already running. The two should be visible
simultaneously but not within typing distance — the audience needs to see
two people, not one person with a sidekick.

---

## 7. The 45-minute matrix (who does what, every minute)

| Min | Block | HOST does | OPERATOR does |
|-----|-------|-----------|----------------|
| 00–04 | Frame & rules | Delivers opening pitch (§9). Shows QR. Confirms poll registrations on screen. | Sits visibly with phone on mirror. Stays silent. Pre-stages the anchor prompt in the input box (does not press Enter). |
| 04–09 | Anchor demo | At minute 4, says: *"Operator, run the anchor."* Calls predict-then-watch ("succeeds first try?"). Narrates as Claude works. | Reads anchor prompt aloud. Hits Enter. Reads diff aloud. Accepts. Refreshes Streamlit. Says: *"Done — new KPI is live."* |
| 09–10 | Round 1 setup | Shows the 4-option menu slide. Reads each option in 15 seconds. Launches the 60-second poll. | Pulls the matching pre-written prompt for each option to top of stack. Stays silent. |
| 10–11 | Round 1 vote | Reads countdown ("30 seconds left to vote"). Announces the winner. | Locates the winner's prompt on the printed menu. Loads it into the input box. |
| 11–18 | Round 1 build | Predict-then-watch. Narrates Claude's actions ("opening `metrics.py`…"). Calls clock at 60 sec & 30 sec marks. | Hits Enter. Reads diff aloud at every step. Accepts / rejects visibly. Refreshes app. |
| 18–22 | Round 1 review | Asks one open question to the room: *"What would you change about this feature?"* Takes 2 verbal answers. | Stays at the phone, ready. If the audience's feedback is small, runs an instant tweak prompt. |
| 22–24 | Round 2 setup | Calls 3 pre-recruited volunteers up to the front. Hands first volunteer the mic. Explains the task. | Resets the prompt input. Says *"Ready when you are."* |
| 24–32 | Round 2 hot-seat | After each volunteer dictates: launches the 30-sec scoring poll (clarity / specificity / did-it-work). Calls the next volunteer. | Types each prompt verbatim. Reads diff aloud. Accepts / rejects. Reports outcome briefly. |
| 32–34 | Round 3 setup | Pushes the audience-input form QR. Reads the top 5 submissions aloud. Picks one. | Stays at the phone, scans the form on a side screen too — flags any that's clearly impossible. |
| 34–40 | Round 3 build | Narrates. Manages clock tightly — says *"three minutes left"*, then *"one minute"*. | Runs the prompt. If it fails, re-prompts once. Then narrates the failure honestly. |
| 40–43 | Debrief | Distributes the memo. Pushes the final retro poll (Monday-confidence 1–10 + free text). Reads a few free-text answers aloud. | Closes Claude Code. Brings the Streamlit app full-screen on the main screen. Stands next to the Host. |
| 43–45 | Closing | Delivers the closing 60 seconds (§16). | Silent, beside the Host, dashboard glowing on the screen behind them. |

This matrix is the source of truth. Print it. Stick it under the Host's
laptop and on the Operator's lectern.

---

## 8. The four engagement mechanisms (recap)

These are the Host's tools to keep 30 spectators active. The Operator
supports each but does not run any of them.

1. **Live poll** every 6–7 minutes. QR code visible from minute 0. The
   Host pushes each poll on the laptop screen.
2. **Predict-then-watch** before every prompt that runs. The Host says:
   *"Show of hands — succeeds first try? … now let's see."* The Operator
   waits for the Host's "go" before pressing Enter.
3. **AI-watch scorecard** (printed A6, one per chair). The Host mentions
   it twice — once at minute 4, once at minute 25. Spectators tick boxes
   silently as the session unfolds.
4. **Hot-seat performance** (Round 2). Three volunteers, three prompts,
   three different outcomes. The single most memorable moment of the day.

---

## 9. Opening pitch (HOST script — 4 minutes)

> *"Welcome. In front of you: a treasury app for a fictional industrial
> group — Helios Industries. Eight bank accounts in three currencies. €38
> million of open AR, €13 million of open AP. A 13-week direct cash
> forecast. Three stress scenarios. The whole thing was built in two
> hours by an AI controlled by a human typing what they wanted."*
>
> *"Today is not a demo. We are two facilitators. My colleague has the
> phone — that's our entire development team. I have the microphone —
> that's the management. **You** are the product owners. For the next 40
> minutes, you decide what gets built next, you score the prompts, and
> in Round 3 you'll throw the AI off a cliff."*
>
> *"Three rules:*
> *— **Specific beats clever.** 'Add a chart' is a bad prompt. 'On the
>    Receivables page, add a horizontal bar chart of the top-five customers
>    by open EUR balance' is a good one.*
> *— **We watch the diff.** Every change is read out loud before accepting.
>    The AI is wrong about one time in five.*
> *— **You scan this QR code now.**"* (point at the QR slide)

The Host then pauses for 30 seconds while the audience scans. The Operator
uses this pause to confirm the prompt is loaded. At minute 4, the Host
says: *"Operator, anchor."*

---

## 10. The prompt sequence (printed menu for the OPERATOR)

### Anchor demo prompt — minute 4 to 9

> *"In `app.py`, add a 9th KPI card called 'AR overdue %'. It shows the
> share of open AR (in EUR) where `due_date` is before today, divided by
> total open AR. Display as a percentage with one decimal. Colour the
> value red if > 15%, otherwise default. Reuse `src.metrics.aging_buckets`
> if it helps."*

### Round 1 menu — pick by audience vote (one of four)

| Code | Prompt menu item the Host reads aloud | Pre-written prompt the Operator runs |
|------|----------------------------------------|----------------------------------------|
| **A** | *"Heatmap of expected receipts by week × day"* | *"In `pages/1_Forecast.py`, add a heatmap above the line chart, showing the sum of expected AR receipts in EUR per (week, weekday) cell, for the next 4 weeks. Use plotly's `imshow`. Title: 'Expected receipts heatmap (next 4 weeks)'. Use `dl.load_ar()`, filter status == 'Open'."* |
| **B** | *"M&A simulator slider"* | *"In `pages/1_Forecast.py`, add to the sidebar a number_input 'Acquisition (€M)' default 0, range 0–50, step 1, and a date_input 'Acquisition date' between today and end of horizon. If amount > 0, append a single forecast line with category 'M&A (simulated)' and amount = -value*1e6 on the chosen date. Trajectory and min-balance must reflect it."* |
| **C** | *"Bank-fee anomaly detector"* | *"Create a new page `pages/7_Anomalies.py`. Detect transactions where category == 'Bank Fees' and abs(amount_eur) > 1.5 × the trailing 12-month rolling mean of Bank Fees. Show: a count KPI of anomalies, a sortable dataframe, and a timeline scatter where anomalies are red, normal points are blue. Use `dl.load_transactions()` and follow the style of `pages/3_Receivables_Payables.py`."* |
| **D** | *"Customer concentration risk score"* | *"In `src/metrics.py`, add `customer_concentration(ar)` returning a dict {'herfindahl': float, 'top3_share': float} computed on Open AR. In `pages/3_Receivables_Payables.py` Receivables tab, show two new KPIs above the aging chart: 'Concentration HHI' and 'Top-3 share' — colour the top-3 KPI red if > 0.40."* |

### Round 2 hot-seat task

The Host announces:

> *"Task: add a button on the Forecast page that exports the current
> 13-week forecast lines as CSV. Three volunteers, each will dictate
> their own prompt for this exact same task. We will see three different
> outcomes."*

The Operator types verbatim. After each, the Host runs a 30-second poll.

### Round 3 stump the AI

The Host opens an audience submission form and reads the top 5 upvoted
prompts. Picks the one with the best mix of *meaningful + tractable in 6
minutes*. Examples that have worked well:

- *"Add a Slack notification when DSO drifts more than 5 days."*
- *"Project the cash position 24 months out and tell us when we run out
  of RCF."*
- *"Make all the charts colour-blind safe."*

If a prompt is clearly impossible (e.g. *"connect to our real ERP"*), the
Host says so out loud and picks the next one — *"that one's a great
question for our follow-up workshop on real data integration"*.

---

## 11. Take-home memo (printed × 30, distributed at minute 40)

Single A5 card. Same on both sides if you want a chair-back card.

```
VIBE CODING FOR TREASURERS — THE 5 REFLEXES

1. SCOPE       One feature per prompt. One file. One test.
2. ANCHOR      Always name the exact file to modify.
3. DATA-FIRST  State the columns, the units, the period.
4. TEST        Define the acceptance criterion BEFORE prompting.
5. ITERATE     The AI is wrong 1 time in 5. Read the diff.
               Re-prompt; never accept blind.

THE PROMPT TEMPLATE
───────────────────
In <file>, add <feature>.
Acceptance: <a measurable, observable result>.
Data: <files / columns to use>.
Style: follow <reference file>.

WHAT TO TRY ON MONDAY
─────────────────────
Pick one repetitive task you do every week.
Open Claude on your phone tomorrow morning.
Apply the five reflexes.
Show us what you built next month.
```

---

## 12. Risks and plan B (split by role)

| Risk | Likelihood | HOST's recovery move | OPERATOR's recovery move |
|------|------------|----------------------|----------------------------|
| Phone mirroring breaks | Medium-high | Bridge with a story for ~60 sec ("while we sort this out, who's already used Claude on their phone?") | Reset the cable / restart mirroring; if it doesn't recover in 90 sec, switch to laptop SSH backup |
| Wifi drops mid-prompt | Medium | Run the predict-then-watch poll on a slower cadence to fill time | Switch to 5G hotspot |
| One prompt eats 6 minutes | High | Call out the timer hard at 3 min: *"Operator, status?"* | Say "I'm bailing" out loud and explain why — turn it into a teaching moment |
| Volunteer freezes at the mic | Medium | Take the mic back, model it: *"if I were them I'd say…"*, then hand back | Be ready to type a Host-suggested prompt instead |
| Audience disengages in Round 2 | Medium | Make the scoring poll mandatory, push the QR even harder | Read every diff slowly, theatrically — slow down, don't speed up |
| AI produces something insecure / weird | Low | Pause: *"Operator, what did you see?"* Let the Operator narrate. Use the moment to drive home reflex #5. | Reject visibly. Say *"that's wrong because <X> — re-prompting"*. Next prompt addresses what was wrong. |
| Both facilitators sick / phone dies | Low | Plan B: facilitator narrates a pre-recorded screencast of the same flow, polls still run. The session still delivers the memo. | — |

---

## 13. Success criteria

Measured in the final 5 minutes. The two facilitators evaluate jointly
right after the room empties.

1. **At least 4 prompts have been executed and accepted**, with visible
   results in the Streamlit app.
2. **At least 1 prompt has failed on stage**, been re-prompted, and
   eventually succeeded.
3. **The "Monday confidence" poll averages ≥ 7 / 10**.
4. **At least 5 take-home memos** come back with the "what I'll try on
   Monday" line filled in (collected at the door).
5. **At least 3 questions** in the debrief are about extending to real
   data — signal that the audience is past the demo and into
   operationalisation.

If you hit 4/5 of these, the workshop worked. Pitch the follow-up
session before they leave the room.

---

## 14. The closing 60 seconds (HOST script — minute 44)

> *"You did not watch a demo. You ran a development team. The phone
> typed, but you specified, you scored, you steered, you rejected. The
> only thing that changes on Monday morning is that the phone in your
> pocket is yours, but the brain doing the steering is the same."*
>
> *"Pick one repetitive treasury task you do every week. Open Claude on
> your phone tomorrow morning. Apply the five reflexes on your memo.
> Show us what you built next month — we'll come back and ship the best
> ones together."*

The Operator stands beside the Host, dashboard glowing on the main screen
behind both of them. The session ends on the working app, not on a slide.

---

## 15. After the workshop (the two of you, in private, within 24h)

A 20-minute joint debrief, while it's fresh:

- Which prompt landed best? Which failed worst?
- Where did the choreography break? (Talked over each other? Missed a
  signal? Volunteer flow awkward?)
- Which 3 audience questions deserve a follow-up workshop?
- Pick the **one** feature from the day that's worth merging into the
  main repo. Open a PR before the end of the week — the audience will
  remember.

Leave a `RETRO.md` in `docs/` with the answers. The next time you run
this session — and you will — your future selves will thank you.
