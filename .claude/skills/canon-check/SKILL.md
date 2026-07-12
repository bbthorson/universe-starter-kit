---
name: canon-check
description: Verify a chapter, scene, or revision against series canon and continuity. Use when asked to check continuity, canon, or consistency; before locking a chapter; or after drafting/revising a scene. Reports contradictions only — never edits the prose.
---

# Canon Check

Verify that a piece of prose is consistent with established canon, continuity, and the
project's hard constraints. This is a **read-only audit**. It reports problems; it never
rewrites the story. The Golden Rule holds: stories drive canon, so when prose and a
tracking file disagree, the *tracking file* is what gets flagged for update — the prose is
never edited to match a record. The one exception: prose that violates a hard constraint
in `ai_instructions.md` (§7 tone ceiling, §8 red lines, the POV rules in §5) is flagged as
a prose problem.

## When to use

- "Check continuity / canon / consistency" on a chapter or scene
- After drafting or revising a scene, before sign-off
- Before a chapter or story part is locked / finalized

## Inputs

Identify the target prose (a chapter file under `stories/<book>/chapters/`, a scene, or a
diff) and which book it belongs to. The canonical sources live in two places:

- **Series-wide:** `canon library/` — `continuity.md`, `characters/*.md`,
  `antagonists/*.md`, `locations/*.md` (+ `locations/index.md`), `group_dynamics.md`,
  `glossary.md`, `series_plan.md`
- **Per-story:** `stories/<book>/tracking/` — `character_matrix.md`,
  `timeline_ledger.md`, `subplot_threads.md`

Also read `ai_instructions.md` §5, §7, and §8 first — they define this universe's hard
constraints, which this skill enforces verbatim rather than assuming.

## Procedure

Run every check. Read the target prose first, then cross-reference each source. Note that
story folders may contain spaces.

### 1. Character state & voice
For each character in the scene, open their row in `tracking/character_matrix.md` for this
chapter (and adjacent chapters):
- **Register** — does the prose match the cell (including transitions)? A character in
  their public register should not drop into raw vulnerability without a transition beat.
- **State arc** — is the one-line emotional state a believable step from the previous
  chapter's cell? Flag jumps with no on-page cause.
- **Voice** — cross-check the character's canon file and the voice guide in
  `world building/`. Distinctive tics should appear *roughly once per scene, not every
  line*. Flag overuse, and flag dialogue that could belong to any character.
- **Established facts** — no contradiction of background, relationships, or secrets in the
  character file or `continuity.md`. Pay special attention to **who knows what at this
  point in the timeline** — a secret's knowledge boundary (who's been told, on-page) is
  canon.

### 2. Timeline & travel
Cross-check `tracking/timeline_ledger.md`:
- Does the scene's implied date match the ledger row for this chapter, and the chapter's
  own frontmatter `date`?
- **Relative-time slips** — a prop/event referred to as "this morning," "yesterday," "two
  days ago" must agree with the absolute dates. This class of bug is real and readers
  catch it.
- **Travel time** — movements between locations must respect the scheduling/travel rules
  in `canon library/locations/index.md`. No character in two places within an impossible
  window.

### 3. Location consistency
Cross-check `canon library/locations/index.md` and the per-location files:
- Is the location **open/operating** on the scene's story date? (Operating rules are
  encoded per location file.)
- Physical details (layout, who works there, geography) match the location file.

### 4. Subplot & object custody
Cross-check `tracking/subplot_threads.md`:
- Every tracked object is in the **right hands** at this point in its custody chain.
- Thread status is consistent — nothing "paid off" that was never introduced; nothing
  contradicting an earlier `complicated`/`developing` beat.
- Flag any thread that ends in silence: a thread may only end `paid off`, explicitly
  `dropped` (with its why note), or `carry forward` — and a `carry forward` thread
  still needs its on-page carry-forward beat (a nod that keeps it alive), not
  disappearance.

### 5. Hard constraints (`ai_instructions.md`)
These are red lines — flag any violation:
- **POV** (§5): no head-hopping within a scene; no mind-reading of other characters;
  whatever POV model §5 defines, enforce it as written.
- **Tone** (§7): the scene must sit within the universe's calibration scale; flag anything
  above the stated ceiling.
- **Red lines** (§8): flag each one individually.

### 6. Cross-book continuity (series-wide scenes)
If the target is the opening of a new book or references prior events, check the relevant
`## After Book N` entry in `canon library/continuity.md` for world state, character state,
and recurring-character availability.

### 7. AI-tells (light craft glance, optional)
A single scene can't reveal the *patterns* that mark AI-generated prose — that's a whole-book
judgment the `story-audit` prose-craft pass makes (see
`.claude/skills/story-audit/references/ai_tells.md`). But at draft time it's cheap to catch
the obvious ones in the scene in front of you: negative parallelism ("not X — it's Y") used
as a reflex, a "here's the kicker" reveal, magic adverbs propping up flat sentences, an
uncatalogued physical tell (hitched breath, tight jaw) carrying the emotion, or the same two
or three stock smells. Flag these as 🔵 craft suggestions — or 🟡 if a single scene clusters
the *same* tell several times — never a contradiction, never a mandate; and honor the same
carve-outs: a device the style guide mandates or a catalogued
voice tic is not a tell. If the scene feels tell-heavy, say so and recommend a full
`story-audit` prose-craft pass rather than judging the pattern from one scene.

## Output

Report findings as a list, grouped by check. For each:

- **Severity:** 🔴 contradiction (breaks canon) · 🟡 likely slip / needs author call · 🔵 nit
- **Location:** chapter + the prose phrase at issue (`file:line` where possible)
- **Conflict:** what the prose says vs. what the source says, with the source cited
- **Suggested resolution:** which side is likely wrong. Default assumption: the prose is
  the truth and the tracking file needs updating — *unless* the prose violates a hard
  constraint (§5 POV rules, §7 tone ceiling, §8 red lines), in which case the prose is
  the problem.

End with a one-line verdict: **clean**, **slips found (N)**, or **canon contradictions
found (N)**. Do not modify any prose file. If asked to *fix* findings, update the
**tracking files** to match the prose (Golden Rule), and only touch prose for
hard-constraint violations after confirming with the author.
