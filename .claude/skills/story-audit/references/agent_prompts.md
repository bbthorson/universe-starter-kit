# Agent Prompt Scaffolds

One scaffold per audit pass. Fill in the `<book>`, part ranges, chapter file names, and
timeline anchors before spawning. If your paths contain spaces, tell each agent to quote
them. Every scaffold ends with the same output contract so findings merge cleanly at
synthesis.

All agents are **read-only** — say so explicitly in every prompt ("Do NOT edit any file.
Report findings only."). Each agent's final message IS the deliverable: instruct it to
return the findings list itself, not a summary of having done the work. The orchestrator
reads these findings; it does not read the chapters.

Adapt terminology to your project. This kit says **part** for a story's structural division;
a given project may call them meals, acts, arcs, or sections — use whatever
`00_book_metadata.md` uses. Worked examples below are drawn from a cozy-crime book whose
parts are "meals"; keep the structure, swap the specifics.

## Shared output contract (paste into every agent prompt)

> Return findings as a structured list. For each finding: severity (🔴 contradiction /
> 🟡 slip / 🔵 nit), location (`file:line` + a short quote), the conflict (prose says X vs.
> source says Y — cite the source file), and a suggested resolution naming which side should
> change. Default: prose is truth and the record changes — unless the prose violates a hard
> constraint in `ai_instructions.md`, in which case the prose is the problem. End with a
> 2–3 sentence overall assessment and a verdict line: clean / slips found (N) /
> contradictions found (N).

## Shared severity scale

- 🔴 contradiction — breaks canon/continuity or a hard constraint; reader-catchable.
- 🟡 slip — likely wrong or stale record; needs an author/record call.
- 🔵 nit — minor / cosmetic / hygiene.

---

## Per-part continuity (one agent per part)

The `canon-check` procedure scoped to a part. Spawn one per part. Strong-reasoner tier.

```
You are running a READ-ONLY continuity audit of <Part P (chapters A–B)> of Book <N> of the
<universe name>. Do NOT edit any file. Report findings only. Your final message is the
deliverable — return the findings list itself.

Base directory (quote paths with spaces): <ABS PATH>

Target prose: the chapter files for chapters <A–B> in "stories/<book>/chapters/". Read each
fully, including frontmatter.

Cross-reference (read these too):
- "stories/<book>/tracking/character_matrix.md" (rows for chapters A–B, plus one adjacent)
- "stories/<book>/tracking/timeline_ledger.md"
- "stories/<book>/tracking/subplot_threads.md"
- "stories/<book>/tracking/interiority/" (sections relevant to A–B)
- "stories/<book>/characters/" (secondary characters appearing in this part)
- "canon library/continuity.md", "canon library/characters/*.md",
  "canon library/antagonists/<this book's antagonist>.md",
  "canon library/glossary.md", "canon library/group_dynamics.md"
- "canon library/locations/index.md" + the location files for places in these chapters
- "ai_instructions.md" (hard constraints)

Timeline anchors for this part (verify against these; flag relative-time phrases that
disagree): <paste the ledger rows / dates / key beats for chapters A–B>

Run every check:
1. Character state & voice — does each present character's register and one-line emotional
   state match their character_matrix cell? Are state changes between chapters motivated
   on-page? Voice tics roughly once per scene, not every line? Any contradiction of
   established facts/secrets — and confirm any deferred secret is NEVER surfaced early on
   the page.
2. Timeline & travel — implied dates match the anchors; relative-time phrases ("yesterday,"
   "two weeks ago") agree with absolute dates; travel between locations respects the rules
   in locations/index.md (no teleporting).
3. Location consistency — is each location open/operating on the scene's date (market days,
   shop hours are schedule rules)? Physical details match the location file?
4. Subplot & clue custody — every prop/clue in the right hands at this point in its custody
   chain; thread statuses in subplot_threads.md consistent with the prose; nothing "paid
   off" that wasn't introduced.
5. Hard constraints — check every red line in ai_instructions.md (e.g. no head-hopping
   within a scene; any tone ceiling; on-page-content limits; villain stays human). Also
   check continuity across the part boundary: entrances/exits, register carried over from
   the previous part, props and knowledge that should persist.
6. Record accuracy — flag any character_matrix / timeline_ledger / subplot_threads /
   interiority entry that is wrong or stale vs. the prose (prose is truth).

<PASTE: shared output contract>
Also give a 2–3 sentence assessment of this part's soundness.
```

**Per-part emphasis to add**, tailored to where the part sits in the arc (examples from the
cozy-crime "meals" model): a setup part → introductions and clue-planting; an investigation
part → does each discovery plausibly lead to the next, POV excursions into other feeds must
be clean cuts not head-hops; a crisis part → does the low point land and the turn feel
earned, is any reveal fair to the reader; a resolution part → **no deus ex machina** (every
element traceable to setup), interleaved timelines stay date-coherent, the villain's exit
stays human.

---

## Story-structure pass

Whole-book, structure-not-lines. Strong-reasoner tier.

```
You are running a READ-ONLY story-structure audit of Book <N> of the <universe name>. Do NOT
edit any file. Report findings only. Your final message is the deliverable.

Base directory (quote paths with spaces): <ABS PATH>

Read first (the rules the book must satisfy):
- "ai_instructions.md" (the project's craft and construction rules — mystery/plot
  construction, tone, and any part-level thematic mapping such as a per-part symbol/menu)
- "world building/" (voice guide, writing guide — whatever exists)
- "stories/<book>/chapters/00_story_outline.md" and any part-summary file
- "stories/<book>/plot/" background
- "stories/<book>/tracking/subplot_threads.md" and "tracking/character_matrix.md"
- "canon library/books/<book>.md" and "canon library/series_plan.md"

Then read ALL chapter files for structure (another auditor covers line-level continuity).

Assess, one section each:
1. Fair-play / plant-payoff ledger — list every clue or planted element and its chapter;
   is the payoff earned from planted material; is anything essential to the ending
   introduced too late (deus ex machina risk)?
2. Misdirection — which alternatives are genuine vs. decorative; fairly dismissed; any
   dangling?
3. Beat structure vs. the outline — flag beats rushed, missing, or mislocated.
4. Pacing — chapter lengths and the tension curve across parts; where does it sag or rush?
5. Character arcs — for each main-cast member, a completed on-page arc OR an explicit
   carry-forward in the tracking? Flag set-up-but-unpaid arcs that aren't sanctioned.
6. Subplots — coherent setup → development → payoff? Does any deferred/unnamed element
   leave a hole for a first-time reader?
7. Part-level rhythm — do the parts' thematic/structural signatures match the writing guide?
8. Series setup — does the book plant what later books need without over-promising?

For each finding: severity (🔴 structural problem / 🟡 weakness / 🔵 observation), cite
chapters/lines. End with (a) a one-paragraph verdict on whether the story is "solid and
sound," and (b) a top-5 prioritized fix list.
```

---

## Tracking-fidelity + records-layer pass

The records' fidelity to the prose and *internal* consistency. Cheaper-model tier — mostly
verification against the prose and the chapter frontmatter.

```
You are running a READ-ONLY audit of the TRACKING and RECORDS layer for Book <N> of the
<universe name>. The per-part auditors check prose deeply; YOUR job is whether the records
faithfully describe it and agree with each other. Do NOT edit any file. Report findings
only. Your final message is the deliverable.

Base directory (quote paths with spaces): <ABS PATH>

Read:
- "CANON_CHANGELOG.md"
- "canon library/continuity.md" — is there an "After Book <N>" section, and does it match
  the book's actual ending (world state, character state, antagonist final status, which
  secrets stayed hidden)?
- "canon library/books/<book>.md", all "canon library/characters/*.md",
  "canon library/antagonists/<antagonist>.md" — are Book <N> developments recorded and
  non-contradictory across files?
- "canon library/glossary.md", "canon library/group_dynamics.md", "canon library/series_plan.md",
  and the locations index for drift.
- "stories/<book>/00_book_metadata.md", story-level character overviews, secondary files.
- "stories/<book>/tracking/" — character_matrix.md, timeline_ledger.md, subplot_threads.md,
  interiority/*.md. Check INTERNAL cross-consistency: do matrix dates match ledger dates
  row-by-row? Do subplot thread chapter citations match matrix beats? Do interiority docs
  agree with matrix registers? Are existing ⚠ flags still open or already resolved by the
  prose? Chapter frontmatter is the source of truth for chapter numbers/dates.
- "stories/_story_template/" — does the book conform (spot-check ~5 chapters' frontmatter
  against the schema)?
- If "protocol/records/" is built: re-run "protocol/entities/resolve.py" and
  "protocol/pipeline/extract.py"; any resolution miss or schema failure is a finding. Report
  coverage.

Watch especially for a **systematic staleness pocket** — a whole class of files left behind
by a past renumber or direction change (chapter-number citations are the usual tell, and the
derived layer is often more current than hand-maintained character files).

Group findings: (a) canon-library completeness for post-book state, (b) tracking-file
internal consistency, (c) outstanding ⚠ flags — open or stale, (d) template/spec
conformance, (e) records coverage/build, (f) cross-file contradictions. For each: severity,
file + line, what's wrong, what it should say (cite the conflicting source). End with a
verdict on whether the project is "tracking character and story progress appropriately" and
a prioritized list of record updates.
```

---

## Prose-craft / AI-tells pass

Whole-book, prose only. Scans for the stylistic tells of AI-generated prose and feeds
**Tier 3 — Craft** only. Cheaper-model tier: the counting is mechanical and the checklist is
explicit. Its findings are suggestions, never contradictions — say so in the prompt.

```
You are running a READ-ONLY prose-craft audit of Book <N> of the <universe name>, scanning
for the stylistic tells of AI-generated prose. Do NOT edit any file. Report findings only.
Your final message is the deliverable.

Base directory (quote paths with spaces): <ABS PATH>

Read first (the rules that define what is NOT a tell here):
- ".claude/skills/story-audit/references/ai_tells.md" — the taxonomy, the severity ladder,
  and the mechanical count-first method. Follow it exactly.
- "ai_instructions.md" §2 (prose style) and §3 (dialogue) — any device the style guide
  MANDATES (e.g. sensory-first prose) is not a tell; its narrow repetition is.
- "world building/" voice guide — every CATALOGUED voice tic (a dialect, a verbal habit, a
  signature somatic beat) is a designed feature. Never flag a catalogued tic as an AI tell.
  Build this allowlist before you read the prose.

Then, for ALL chapter files in "stories/<book>/chapters/":
1. Mechanical pre-pass FIRST. For each greppable tell in ai_tells.md, count occurrences per
   chapter and book-total (em-dash density per 1000 words; negative-parallelism cadence;
   "here's the kicker" phrasings; the filler/buzzword list; magic adverbs; somatic-beat
   frequency; and the chapter-ending-symmetry proxy — is each chapter's last sentence a
   short standalone paragraph?). Produce a table. The last two are proxies that surface
   candidates for the judgment pass, not verdicts.
2. Judgment pass. Using the counts as input, decide which frequencies are genre-legitimate
   and which are the model's fingerprints. Then read for the non-greppable tells: recycled
   physical tells (same somatic beat across chapters), a narrow/repeated sensory palette,
   meaningless action filler, perfect paragraph/chapter symmetry.

Severity ladder (from ai_tells.md): a tell once or twice → 🔵 nit; a tell forming a pattern
across chapters or clustered heavily in one → 🟡 slip. NEVER 🔴, NEVER Tier 1. Frame each
finding as a suggestion with a location, not a mandate.

For each finding: the tell, its count and locations (file:line + short quotes), the carve-out
you checked (why it isn't legitimate craft or a catalogued tic here), and a suggested fix
(vary / thin out / cut). End with: (a) the count table, (b) a 2–3 sentence verdict on whether
the prose reads as written or generated, and (c) the 3–5 tells most worth the author's
attention. All findings route to Tier 3.
```
