---
name: plot-suggest
description: Generate plot event suggestions grounded in canon — next-chapter beats, B-plot moves, or whole-story premises that are canon-legal by construction. Use when planning a chapter, unblocking a stalled outline, or brainstorming the next book. Suggestions cite their canon sources; nothing is invented that contradicts established facts.
---

# Plot Suggest

Generate plot event suggestions that are **grounded in what the universe has already
established**. The difference between this and freeform brainstorming: every suggestion
is built from open material the canon is already carrying (threads, secrets, states,
schedules) and cites it, so accepting a suggestion never creates a contradiction.

## When to use

- "What should happen next?" — planning the next chapter or scene
- A stalled outline: the part structure is set but a beat is empty
- Story-level: "what's Book N about?" grounded in the seeds prior books planted
- "Give me options for how X could pay off"

## Scope first

Ask (or infer from the request) which altitude the suggestion should live at:
1. **Beat** — the next scene/chapter inside a story in progress
2. **Thread move** — how to advance or pay off one specific subplot
3. **Premise** — a whole future story

## Gather the open material

Read, in this order (skip what doesn't exist yet):

1. **`canon library/continuity.md`** (latest entry) — world state, character open threads,
   recurring-character availability, **Seeds Planted for Future Books**.
2. **`stories/<current>/tracking/subplot_threads.md`** — every thread with status
   `introduced` / `developing` / `complicated` / `carry forward` is an open promise;
   the "Threads at risk" table is a to-do list of latent material. The object-custody
   table tells you where every tracked object *is* right now.
3. **`stories/<current>/tracking/character_matrix.md`** — each character's current
   register and state. A suggestion should move someone's state, not just the plot.
4. **`stories/<current>/tracking/interiority/*.md`** — the **withhold columns**: what each
   character is not saying is the highest-energy material available. (Private authoring
   input — never quote interiority content into reader-facing text.)
5. **`canon library/series_plan.md`** — the secret-progression table (what is *allowed*
   to crack open now vs. reserved for a later book) and locked decisions.
6. **`canon library/locations/index.md`** — schedules and travel rules; these generate
   plot (a place being closed, a market day forcing a date) as often as they constrain it.
7. **`ai_instructions.md`** — §6 story construction, §7 tone ceiling, §8 red lines.
   Suggestions must fit inside all three.
8. **The story's outline and part structure** — which structural beat the story is at;
   suggest beats that belong at this point in the shape.

## Generate

Produce **3–5 suggestions**, deliberately varied (don't give five versions of the same
move). Good generators, in rough order of strength:

- **An open thread + a character's withheld thing.** Force a `developing` thread through
  the character whose interiority says they can't handle it.
- **A seed that's due.** A planted seed whose payoff book is this one (or whose "at risk"
  entry says it's going stale).
- **A schedule collision.** Two facts in the locations index / timeline that can be made
  to collide (the place is closed the day they need it; travel time forces an overnight).
- **A custody move.** The tracked object changes hands — every hand-off is a scene.
- **A secret's knowledge boundary shifting by one person.** Not the full reveal (check
  the progression table for what's reserved) — one character learning one layer.
- **A recurring character's return** consistent with their availability in continuity.

## Output format

For each suggestion:

- **The event** (2–3 sentences, concrete: who does what, where, when)
- **Grounded in:** cited sources (`file` + the thread/cell/seed it builds on)
- **What it moves:** which thread(s) advance, whose state changes and to what
- **Cost / constraint check:** date works (schedules, travel), tone stays within the
  ceiling, no red line crossed, no reserved reveal spent early
- **Where it could go next:** one sentence on the follow-on it opens

Close with a recommendation: which suggestion you'd take and why (fit to the current
structural beat and to the focal character's arc).

## Rules

- **Never contradict canon.** If a suggestion needs a fact bent, say so explicitly and
  flag it as a canon-change proposal, not a plot suggestion.
- **Never spend a reserved reveal.** The secret-progression table is a schedule, not a menu.
- **Respect the tone ceiling.** No suggestion should require the story to exceed
  `ai_instructions.md` §7.
- **Suggestions are options, not edits.** This skill writes no prose and updates no
  tracking files.
