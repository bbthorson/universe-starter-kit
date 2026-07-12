# Report Template

Write the synthesized report to `stories/<book>/tracking/audit_<YYYY-MM-DD>.md`. Keep the
verdict-first ordering, the action tiers, the author-calls section, and the "genuinely
strong" section — the report is what the author *acts on*, so it's organized by what to do,
not by which pass found what. "Part" below means whatever your project calls its structural
divisions (meals, acts, arcs).

````markdown
# Book <N> Full Audit — *<Title>*

**Date:** <YYYY-MM-DD>
**Scope:** All <K> chapters + tracking files + canon library + derived records
**Method:** Parallel read-only passes (per-part continuity, story-structure,
tracking-fidelity, records-layer), synthesized. Golden Rule — prose is truth; records get
flagged, prose only where it breaks a hard constraint.
**Confidence:** <which model tier ran which pass — e.g. "continuity + structure + synthesis
on a strong model; tracking + records on a cheap model." State it so a cheap pass isn't
mistaken for a deep one.>

---

## Verdict

<One paragraph. Lead with the honest headline — "solid and sound," or not. Say what's
strong structurally, then name how many things need fixing before locking and what kind
(repairs vs. refinements).>

**Finding counts:** <X> contradictions (🔴), <Y> slips (🟡), <Z> nits (🔵).

| Pass | 🔴 | 🟡 | 🔵 | State of the prose |
|------|----|----|----|--------------------|
| Part 1 (Ch…) | | | | |
| … | | | | |
| Story structure | — | — | — | |
| Records layer | | | | |

---

## Tier 1 — Critical (fix before locking)

<Reader-catchable prose contradictions and canon files asserting superseded facts. For each:
severity, where (file:line + quote both sides), the problem in plain terms, and the fix —
labeled (prose) or (record) so the author knows what changes.>

### 1.1 🔴 <one-line title>
- **Where:** `file:line` (quote) vs. `file:line` (quote)
- **Problem:** <why these can't both be true>
- **Fix (prose|record):** <the specific change>

## Tier 2 — High priority (before sign-off)
<Dropped threads, doubled beats, timeline knots, systematic record staleness.>

## Tier 3 — Craft
<POV drift, register overuse, pacing, arc-agency — real but subjective.>

## Tier 4 — Hygiene
<Stale flags, citation cleanups, draft residue. A bulleted list is fine here.>

---

## Author calls (not bugs — decisions)

<Genuine forks the audit surfaced, not errors: which of two backstories is canon, whether an
early echo is intentional. List each with options, not a pre-chosen fix. Keeping these out
of the tiers keeps the fix sequence honestly mechanical.>

---

## What's genuinely strong (verified clean)

<A real section, not a courtesy. What the audit confirmed is working — beats, fair play,
villain-is-human, arcs, records spine. Tells the author what NOT to touch.>

---

## Recommended sequence

1. <Fixes have an order — resolve a prose contradiction before reconciling the record that
   describes it. Spell it out.>
2. …
N. <Point the high-volume mechanical record reconciliation at a cheap-model batch run with
   spot-checks — token-efficient and safe, because it's verifiable against frontmatter.>

<Close with which tiers are the "solid and sound" bar vs. the "excellent" bar.>
````
