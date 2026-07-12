---
name: story-audit
description: Full-book audit of a completed (or near-complete) story — every chapter, tracking file, canon file, and derived record, checked in parallel passes and reported as tiered findings. Use before locking a book, before manuscript sign-off, or when a story has accumulated enough edits that continuity confidence is low. Read-only; produces a findings report, not edits.
---

# Story Audit

A full-book audit. Where `canon-check` verifies one chapter or scene, this audits an
entire story — prose, tracking, canon, and (if built) the derived records — and produces
a tiered, actionable findings report. The method found 6 contradictions, 28 slips, and 19
nits in a book that had already been reviewed chapter-by-chapter: whole-book passes catch
what per-chapter checks structurally cannot (doubled beats, dropped characters, arcs that
hollow out when a twist was layered in late).

**Read-only.** The output is a report file; fixing is a separate, explicitly-requested
pass. Golden Rule throughout: prose is truth; tracking files get flagged for update;
prose is only flagged where it violates a hard constraint in `ai_instructions.md`.

## When to use

- Before locking a book (v1 or final)
- Before manuscript sign-off
- After a structural revision (a twist added, chapters reordered, a subplot re-threaded)
  — late-layered changes are the #1 source of contradictions

## Method: parallel passes

Divide the work into independent read-only passes and run them as parallel subagents
where available (each pass names the files it needs — they don't overlap in judgment,
only in reading):

1. **Per-part continuity passes** (one per story part — e.g., four passes for a four-part
   book). Each runs the full `canon-check` procedure over its span of chapters *plus*
   checks against adjacent parts: entrances/exits, register continuity across the part
   boundary, props and knowledge carried over.
2. **Story-structure pass** (whole book, prose only). Does every structural beat land
   where the outline says? Is the reveal fair-play (can a reader work it out from planted
   material — check the plant/payoff tracker)? Does every main-cast member get an arc or
   an explicit carry-forward? Do part-level rhythms (the anchor element, pacing) match
   the writing guide?
3. **Tracking-fidelity pass.** Do `character_matrix.md`, `timeline_ledger.md`, and
   `subplot_threads.md` actually match the prose, chapter by chapter? Stale tracking is a
   finding even when the prose is fine — the tracking layer is what every future book
   builds on.
4. **Records-layer pass** (only if `protocol/records/` is built). Re-run
   `protocol/entities/resolve.py` and `protocol/pipeline/extract.py`; any resolution miss
   or schema failure is a finding. Check that character files' lore sections are current
   with the finished prose.
5. **Prose-craft / AI-tells pass** (whole book, prose only). Scans for the stylistic tells
   of AI-generated prose — negative parallelism, em-dash addiction, magic adverbs, recycled
   physical tells, a narrow sensory palette, perfect paragraph symmetry. The full checklist,
   the genre carve-outs that stop it firing on legitimate craft, and the mechanical
   count-first method live in [`references/ai_tells.md`](references/ai_tells.md). This pass
   feeds **Tier 3 — Craft** only: its findings are 🔵/🟡 suggestions, never contradictions.
   Because a tell only resolves into a pattern *across* the book, this is a whole-book
   judgment that per-chapter checks structurally cannot make — count the greppable tells
   first (regexes in the reference), then judge which counts are genre-legitimate.

Then a **synthesis pass** merges every pass's findings into one tiered report (below).

The reason for the fan-out is capacity: a whole book plus its tracking and canon does not
fit usefully in one context — a single-pass read either overflows or degrades into
skimming. So each pass holds one slice and returns *findings*, and the orchestrator that
synthesizes **reads the findings, never the chapters**. If the orchestrator starts reading
prose itself, it runs out of room before it can synthesize — that defeats the whole method.

Ready-to-fill prompt scaffolds for each pass (with the cross-reference file lists and the
shared output contract already written out) live in
[`references/agent_prompts.md`](references/agent_prompts.md). Adapt them to the book's part
boundaries and file names.

### Which model runs which pass (advisory)

Split the passes by **judgment required**, not by length — this is the difference between a
report that looks clean and one that is clean:

| Pass | Model tier | Why |
|------|-----------|-----|
| Per-part continuity | **Strong reasoner** | The contradictions that hurt a book are subtle (a prop in two places after a late twist, a name revealed before the scene meant to discover it). A cheap model reading fast *misses* these — and a missed contradiction never gets escalated, so the report reads clean but isn't. |
| Story-structure | **Strong reasoner** | Fair-play, arc-completion, and pacing are judgment calls. |
| Tracking-fidelity | **Cheaper model OK** | Mostly "does this cell match the prose / the frontmatter?" — high-volume, verifiable, low-judgment. |
| Records-layer | **Cheaper model OK** | Running the pipeline and reading its errors is mechanical. |
| Prose-craft / AI-tells | **Cheaper model OK** | The counting is mechanical and the checklist is explicit; the one place a stronger model helps is the genre-legitimacy call, so escalate only if the counts are ambiguous. |
| Synthesis | **Strong reasoner** | It's the deliverable the author acts on. |

The instinct to "use a cheap model for the long, tedious passes" is right *for the tracking
and records passes* and wrong for continuity — that's where a false negative costs you a
real bug. If tokens are tight, economize on tracking/records, never on continuity.

Treat this as a default, not a law: if the orchestrator is already a strong model and the
book is short, one tier throughout is fine. **A skill can't set the model itself** — it's
instructions the orchestrator follows; the orchestrator picks each subagent's model via the
Agent tool's `model` parameter. State which tiers ran which passes at the top of the report
so a reader knows the confidence level.

## Severity and tiers

Every finding gets a severity:
- 🔴 **contradiction** — breaks canon; a reader can catch it
- 🟡 **slip** — likely error / needs an author call
- 🔵 **nit** — polish

The report groups findings into action tiers:
- **Tier 1 — Critical (fix before locking):** contradictions a reader can catch, and
  canon files asserting superseded facts.
- **Tier 2 — High priority (before sign-off):** dropped threads (a character who enables
  the plot and then vanishes; a payoff the tracker recommended that was never executed),
  doubled beats, timeline knots.
- **Tier 3 — Craft:** POV drift, register overuse, pacing flags — real but subjective.
- **Tier 4 — Hygiene:** stale tracking cells, draft residue (names/props from abandoned
  directions), outdated ⚠ flags.

## Report format

Write the report to `stories/<book>/tracking/audit_YYYY-MM-DD.md`:

1. **Verdict paragraph** — is the book structurally sound? What kind of problems dominate
   (repairs vs. refinements)?
2. **Finding counts table** — 🔴/🟡/🔵 per pass, with a one-line "state of the prose" per part.
3. **Tiered findings**, each with: severity · location (`file:line`) · the conflict
   (prose vs. source, source cited) · suggested resolution (which side is wrong).
4. **Author calls** — findings where the right fix is a creative decision, listed
   separately with options rather than a recommendation.
5. **What's genuinely strong (verified clean)** — a real section, not a courtesy. An audit
   that only lists problems misrepresents a healthy book and hides the signal about what
   *not* to touch.

A fill-in report skeleton lives in
[`references/report_template.md`](references/report_template.md).

## Fix pass (separate, on request)

When asked to fix: work tier by tier, Tier 1 first. Tracking/canon files are updated to
match prose; prose is edited only for hard-constraint violations or Tier 1 contradictions,
and each prose fix should be the **minimal** change that resolves the finding (prefer
changing an object/date reference over rewriting a scene). Annotate the audit report with
✅ fix notes as items land, so the report remains the record of what was found and what
was done. Re-run the records pipeline (if built) after fixes and confirm a clean build.
