# Universe Starter Kit

A template for building and maintaining a fictional universe — the folder structure, tracking conventions, and LLM instructions that keep a long-running story world consistent as it grows.

Start by copying this repo, then replace the bracketed placeholders as your universe takes shape. The conventions here were extracted from a universe that ran them through a complete, fully-audited book; they earn their keep once the story gets longer than one person's memory.

---

## Directory Structure

This universe is organized into layers, each with a distinct role:

### 📚 world building/
**Role: Rules and patterns.** High-level creative rules that govern how the universe works — tone, voice, structure, pacing. These files change rarely. They tell you *how to write* in this universe.

Contents:
- `01_series_overview.md` — Target audience, core concept, format, series guidelines

As your universe matures, add files here for a character voice guide (voice profiles and registers per character) and a writing guide (craft rules: chapter length, beat structure, pacing).

### 📇 canon library/
**Role: Facts and state.** The encyclopedia of specific people, places, and things in the universe. These files update after every story. They tell you *what is true* in this universe right now.

Contents:
- `characters/` — One file per character: background, relationships, secrets, and per-story lore tracking
- `antagonists/` — One antagonist profile per planned story (antagonists are characters too — this folder just keeps their spoiler-heavy plans separate)
- `locations/` — One file per location, plus `index.md` holding the cross-cutting geography facts and the **hard scheduling/travel rules**
- `books/` — One concept/summary file per planned story
- `series_plan.md` — Story order, timeline progression, secrets reveal schedule (the index for `books/`)
- `continuity.md` — "Previously on…" world-state summary, updated after each story
- `glossary.md` — Canon terms, quick-reference tables, consistency rules
- `group_dynamics.md` — Tensions, alliances, and pairing dynamics among the main cast

**Key distinction:** how a character *talks* (voice, registers) lives in `world building/`. What has *happened* to a character (backstory, events, relationships) lives in `canon library/`.

### 📜 stories/
**Role: The actual narratives.** Each story has its own subdirectory with chapters, outlines, character notes, plot documents, and tracking files. Stories are the primary drivers of the universe — they are always right.

---

## The Golden Rule: The Story Drives the Canon

Your highest priority is maintaining consistency with the **most recently written material** in the `stories/` folder. If you find a conflict between a story and the canon library, **the story is correct** and the canon file needs to be updated.

The one exception: prose that violates a hard constraint in `ai_instructions.md` (your universe's red lines) is flagged as a prose problem, not a canon problem.

## Workflow: The "Living Canon"

When new information is revealed in a story, the canon library must be updated to reflect it. This can happen:
- **During editing** — when changes affect canon (e.g., changing a location name)
- **After completing a story** — using the Canon Updates checklist in the story template
- **On request** — when you say "propose an update" to a file based on new material

All significant canon changes should be logged in [CANON_CHANGELOG.md](CANON_CHANGELOG.md). The changelog is the canon's chronological history — when a fact changed, and why.

## Modes of Operation

The AI assistant operates in one of two modes, which you specify:

- **✍️ Author Mode (Omniscient):** A co-creator with a bird's-eye view. Can access all information to help with planning, outlining, and consistency checks. In Author Mode, the assistant should be familiar with the contents of `canon library/` and `world building/`.

- **🎭 Scene Mode (Limited Context):** A focused writing assistant that must ONLY use the specific files you provide for that request. This maintains authentic character perspective — characters don't know everything.

## Creative Direction

For tone, style, voice, and craft guidelines, see [ai_instructions.md](ai_instructions.md). Fill in its bracketed sections early — the hard constraints you set there (POV rules, tone ceiling, red lines) are what continuity checks enforce.

---

## A note on naming

Directory names deliberately avoid emoji and other special characters (the emoji live up here in the README headers instead). Plain paths keep the repo friendly to shells, scripts, and any extraction tooling you add later.
