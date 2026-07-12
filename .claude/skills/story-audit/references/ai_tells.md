# AI-Tells Taxonomy

A checklist for the **prose-craft pass** (see `SKILL.md`). AI-generated prose has recurring
stylistic tells — phrasing patterns, buzzwords, and fiction tics that make writing feel
formulaic. This file is the catalogue the pass scans against.

## The one rule that keeps this honest

**Flag repetition and formula, not presence.** Almost every item below is also a legitimate
craft tool. Em-dashes, the rule of three, sensory grounding, a character's physical reaction
to fear — these are how good prose works. The tell is not that they appear; it's that they
appear *on a schedule*: the same device, the same rhythm, the same somatic beat, recurring
until the prose reads as generated rather than written.

Three consequences:

1. **This is a whole-book judgment.** A single em-dash or one metallic tang is invisible at
   the chapter level and only resolves into a tell across the book. That's why this is an
   audit pass, not a `canon-check` line — per-chapter reads structurally cannot see the
   pattern.
2. **Frequency beats instinct.** For the greppable tells, get a count before you judge.
   "Feels em-dash-heavy" is worthless; "41 em-dashes across 12 chapters, 9 of them in Ch. 7"
   is a finding. The mechanical pre-pass (below) exists for exactly this.
3. **Honor the style guide's carve-outs.** If `ai_instructions.md` *mandates* a device, its
   presence is not a tell. A sensory-first universe is *supposed* to smell of things; the
   tell there is the same three smells recycled, not scent itself. A **catalogued voice tic**
   (a dialect, a verbal habit recorded in the voice guide) is a designed feature — never flag
   it as an AI physical-tell. An *uncatalogued* beat repeated across chapters is fair game.

## Severity mapping

AI tells are a **craft** concern. They feed **Tier 3 — Craft** of the report and follow a
different severity ladder than continuity findings:

- A tell appearing **once or twice** → 🔵 nit (note it, don't tier it).
- A tell forming a **pattern** (same device recurring across many chapters, or clustered
  heavily in one) → 🟡 slip.
- **Never 🔴, never Tier 1.** An AI tell does not break canon; it's a polish call the author
  owns. Frame every finding as a *suggestion with a location*, not a mandate.

## The mechanical pre-pass (feeds the judgment pass)

Some tells are countable. Run these before the judgment read and hand the model the counts,
so it spends its attention deciding *whether the frequency is a problem in this genre* rather
than hunting blind. Report per chapter and book-total.

Each entry is `signal — what to count`. Regexes are given as clean code spans (a bulleted
list, not a table, so the pipes are real alternation you can copy verbatim — a markdown table
would force `\|` escapes that break the regex):

- **Em-dash density** — count `—` per 1000 words, per chapter.
- **Negative parallelism** — `not (just |merely |only )?[^.]{1,40}[—,] (it'?s|but) `, plus "It wasn't X. It was Y."
- **"Here's the kicker"** — `here'?s (the|where) (the )?(thing|kicker|catch|interesting|deal)` and `but here'?s`.
- **Corporate/AI filler** — `\b(delve|leverage|unlock|elevate|testament|tapestry|landscape|ecosystem|symphony|realm|navigate the)\b`.
- **Magic adverbs** — `\b(deeply|quietly|fundamentally|remarkably|profoundly|utterly|palpably)\b` frequency.
- **Recycled physical tells** — somatic-beat frequency per chapter: `\b(jaw|breath|throat|chest|pulse|swallow\w*|exhal\w*)\b`; then flag the *same* beat (e.g. a clenched jaw) recurring across chapters or clustered in one.
- **Chapter-ending symmetry** — for each chapter, flag when its **last sentence stands alone as its own paragraph and runs under ~12 words** — a cheap proxy for the "epiphany button" close. A pattern across many chapters is the tell.

Counts are inputs, not verdicts. The judgment pass decides which counts are genre-legitimate
(a technical universe may earn "leverage"; a lyrical one may earn "symphony") and which are
the model's fingerprints.

The last two entries are **proxies**, not detectors — a somatic word isn't automatically a tell,
and a short final paragraph is sometimes the right ending. They exist because these two tells
have no clean single-token signal and are the easiest to skip on a judgment-only read (the
chapter-ending one especially: it requires deliberately reading all N closing paragraphs
together, which is exactly what gets dropped under time pressure). The proxy surfaces the
candidates; the judgment pass confirms the pattern. A **repeated-construction / n-gram scan**
(the same distinctive phrase reused at two big beats — e.g. "the version of himself who…") is
a worthwhile optional extension here: it's a symmetry tell that no fixed regex predicts.

## The taxonomy

### A. Phrasing & structure

- **Negative parallelism ("Not X — it's Y").** The reflexive "It's not a bug; it's a design
  flaw" cadence. One is rhetoric; a habit of it is a tell. Flag when it recurs as a
  paragraph- or scene-closing move.
- **Rule of three / tricolon abuse.** Concepts, adjectives, or clauses grouped in threes,
  especially semicolon-separated lists. Flag *repetition of the pattern*, not any single triad.
- **Em-dash addiction.** Em-dashes forcing dramatic pauses or explanatory asides at high
  density. Use the count; flag clusters and book-wide density spikes.
- **"Here's the kicker" reveals.** Manufactured revelation: "But here's the thing," "Here's
  where it gets interesting," "The kicker?" A narrator nudging the reader toward its own
  cleverness.

### B. Buzzwords & vocabulary

- **Magic adverbs.** "Deeply," "quietly," "fundamentally," "remarkably" propping up a flat
  sentence to feel profound. Flag frequency and the *deeply/quietly + verb* construction.
- **Grandiose metaphors.** Over-reliance on "tapestry," "landscape," "ecosystem," "symphony,"
  "realm," "dance of." Flag when abstraction substitutes for a concrete image.
- **Corporate/AI filler.** "Delve," "leverage," "innovative," "transform," "unlock,"
  "testament to," "navigate." Genre-check each — some are legitimate in-world; the tell is the
  cluster.
- **Vague attribution.** "Experts argue," "studies show," "it's said that," "many believe" —
  unspecified authorities. Rare in fiction prose but common in a character's exposition or an
  essayistic narrator; flag when it stands in for a real source or a specific voice.

### C. Fiction & storytelling tics

- **Physical tells as emotion.** The recycled somatic vocabulary: hitched/caught breath,
  tight or clenched jaw, dilating pupils, swallowing hard, a "breath he didn't know he was
  holding," exhaling through the nose. Flag when the *same* beat recurs across chapters as the
  default emotion-carrier. **Carve-out:** a somatic beat catalogued as a character's voice tic
  is designed, not a tell.
- **Sensory clichés.** The stock sensory kit: metallic tang (of blood, of fear), the smell of
  ozone, jasmine, sandalwood, petrichor; "the air was thick with." Flag *recycling of the same
  few sensations*, not sensory writing itself. **Carve-out:** a sensory-first style guide
  mandates rich sensation — the tell is the narrow, repeated palette, not the presence.
- **Meaningless action filler.** Characters performing business they don't want and that
  carries no meaning — the cigarette they didn't want, the coffee they don't drink, crossing
  and uncrossing arms to fill a beat. Flag gestures that neither characterize nor advance.
- **Perfect symmetry.** Paragraphs of near-identical length; every scene or chapter closing on
  a tidy, inspirational bow; each beat resolving too neatly. Flag mechanical evenness — real
  prose has ragged, load-bearing asymmetry.

## What a finding looks like

> 🟡 **Recycled physical tell — "breath he didn't know he was holding."** Appears Ch. 3, 6, 7,
> 11 (4×), each time as the release beat after tension. `ch07.md:212`, `ch11.md:88`, … Not a
> catalogued voice tic. Suggest varying the release or cutting two instances. *(Tier 3 —
> author's call; not a continuity issue.)*

Cite locations, give the count, name the carve-out you checked, and mark it a suggestion.
Never present an AI-tell finding as something the book is *wrong* for having.
