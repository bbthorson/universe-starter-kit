# Derived Records Layer — Architecture

How a universe built on this kit projects to reader-facing surfaces — a public site, interactive timelines, or (optionally) the AT Protocol — without changing how it is written.

**Companion:** `KNOWLEDGE_FORMAT.md` covers the *inward* knowledge format (an agent-readable canon graph for authoring); this doc covers the *outward* published layer (records for readers). Two formats, opposite directions, shared identity.

These principles ran through a production universe (a complete, fully-audited book extracted to 140+ validated records) and were independently adopted by a second product (an interactive RPG-podcast engine). They generalize.

---

## 1. Purpose: one source, many surfaces

The repo is the single source of truth. It is **projected onto reader-facing surfaces**; no surface is the backbone.

- **A public site is the primary reading experience.** Chapters — plus interactive lenses like a scrubbable timeline and location/character feeds — are rendered from the derived record set, with full design control and no dependency on any niche client.
- **The AT Protocol is an optional, experimental projection**, used only for what it is uniquely good at: characters as portable identities (DIDs) and the novelty of a story you can read *inside* a social feed — follow a character, watch their state change across the timeline, trace an object's custody. A lens, not the distribution channel.

Both surfaces read from the same derived layer, so the choice of surface never re-derives the truth.

## 2. Core Principles

These are load-bearing. Every design choice below follows from them.

1. **The record layer is derived, never authored.** Records are generated from the prose and tracking files. No one writes a record by hand. If the story changes, records regenerate.
2. **The Golden Rule still holds.** Stories drive the canon. The pipeline reads finalized prose and emits records to match. Records never constrain or overwrite the writing. This inverts the common "AI pipeline" framing where structured state cages the prose: here, prose is the source; records are the projection.
3. **The repo stays private; publishing is outward-only.** All planning, drafts, canon, and the interiority docs live here, in private. Publishing is a one-way compile step that pushes a curated subset outward.
4. **Privacy is a gradient already present in the folders.** Interiority never leaves. Chapters are public. Anything gated is served through your own surface with your own access control — never published to a public protocol repo expecting it to stay private.
5. **The writing workflow is unaffected.** Author Mode / Scene Mode govern writing; the record layer is downstream of both.

## 3. Layer Model

```
world building/     Rules and patterns        (never published)
canon library/      Facts and state           (source for records)
stories/            The narratives            (source for records)
protocol/           Derived projection layer  (generated)
```

`protocol/` is a build output plus the schemas and scripts that produce it. It reads from the creative layers and never writes back to them.

## 4. Directory Layout

```
protocol/
  ARCHITECTURE.md          This document
  KNOWLEDGE_FORMAT.md      The inward (authoring) conventions
  lexicons/                Schema definitions per record type (JSON)
  entities/                Canonical ID registry + resolver
  pipeline/                Extraction scripts (repo -> records)
  records/                 Generated record instances (build output, disposable)
```

`records/` can be regenerated at any time and should be treated as disposable. `lexicons/` and `entities/` are committed source of truth.

## 5. Record Namespace (NSID)

Record types carry reverse-DNS names (NSIDs), e.g. `example.universe.character.stateEvent`. **The placeholder root `example.universe` lives in exactly one constant** (`pipeline/extract.py` and the `$id`/`$type` fields of `lexicons/*`), so swapping in a real owned domain is a mechanical change. Do not publish records anywhere public until you own the domain that roots the namespace.

Where a community lexicon already exists, reuse it rather than minting your own — e.g. if you mirror long-form chapters onto atproto, use the shared standard.site lexicon (`site.standard.document`) rather than inventing a chapter record type.

## 6. Record Types

The key insight: most of this data is **already structured** in the kit's tracking files and chapter frontmatter, so the work is extraction, not re-authoring.

| Repo source | Record type | Notes |
|---|---|---|
| `canon library/characters/*.md` | `character.profile` | Static identity. Only reader-safe structured facts — never the prose body wholesale |
| chapter frontmatter `registers` | `character.stateEvent` | The backdated time-series — one record per character per chapter beat. **This is the feature that lets a reader watch a character change** |
| `canon library/locations/*.md` | `place` | Includes operating constraints as structured fields, so a surface can flag "open/closed" on a story date |
| chapter frontmatter (dates, places, cast, pov) | `scene` | One record per chapter. The spine of any timeline view |
| object-custody table in `subplot_threads.md` | `item` + `custodyEvent` | The "trace an object" mechanic: reading custody events ordered by date reconstructs its literal path |
| `stories/*/chapters/*.md` | site content (+ optional standard.site mirror) | The prose itself is rendered by the site build, not re-encoded as records |
| `tracking/interiority/*.md` | **none, ever** | Author-only. Never published |

## 7. Identity Model

Stable IDs come first (see `entities/entities.yaml` and `KNOWLEDGE_FORMAT.md`): every character, place, and item has a permanent local key (`char.emma`) that never changes even when names do.

**The graduation ladder (default for single-writer prose universes):**

1. **Local stable IDs** — all any tooling needs. Start here.
2. **One protocol repo, multiple record collections** — if/when you publish to atproto, one identity holds all record types.
3. **Per-character DIDs** — promote an individual character to their own portable identity only when a concrete portability use-case appears (a character crossing into another product or world without forking the truth).

**Interactive/multiplayer universes are the exception:** when characters are owned by different people (players), key them on DIDs from day one — cross-campaign portability is the point, not a later upgrade.

## 8. Timestamps and Backdating

This determines whether timeline mechanics work.

- **`createdAt` is self-asserted** in atproto records; backdating a record to the story's in-world date is legitimate and sorts correctly (Bluesky computes `sortAt` as the earlier of `createdAt` and `indexedAt`).
- **Future-dating is clamped by Bluesky's app** (falls back to `indexedAt`), but the record still holds the real `createdAt`; your own surface can sort by it literally.
- **Contemporary settings:** set `createdAt = storyDate`. The pipeline enforces this.
- **Fantasy calendars / far-past / far-future:** the `datetime` format targets the contemporary era. Store the in-world date as a **plain string field** and let `createdAt` carry a real ISO timestamp whose only job is ordering. Never put a fantasy year in `createdAt`.

**Continuity bonus:** because every event record carries a `storyDate`, the generated record set doubles as a continuity check — contradictory in-world timing surfaces as inconsistent dates. (This caught a real prop-in-two-places error in production.)

## 9. The Finalization Gate

**No records are published from a story until its prose is locked.** Records are derived from prose and stories drive canon, so publishing an unfinished story's records would bake in continuity the prose may still change. The pipeline is re-runnable by design — extract against drafts freely for testing; only the publish step is gated.

## 10. The Pipeline

A one-way compile, repo → records:

1. **Read** the creative layers: entity registry, chapter frontmatter, canon files.
2. **Resolve** every name reference to a canonical ID via `entities.yaml`. An unresolved reference is a **build error**, not a guess.
3. **Emit** records into `protocol/records/`, setting `createdAt` from `storyDate`.
4. **Validate** records against the lexicon schemas.
5. **Publish** (separate, gated step) once a story is finalized.

Steps 1–4 run locally against drafts. Step 5 is the only step that touches a network. When prose and an old record disagree, the record is wrong and is regenerated — the prose is never edited to match a record.

See `pipeline/README.md` for the reference implementation.

## 11. Reader Surfaces (downstream, out of scope for the first build)

- **Book Mode:** clean sequential reading, rendered from the chapter files.
- **Timeline Explorer:** an interactive view over `scene`, `character.stateEvent`, `place`, and `custodyEvent` records — scrub a calendar, watch a character's state change, trace an object.
- **Location / character feeds:** the same records filtered by place or person. On a site this is a filtered view; on atproto it's a feed generator.

## 12. Decisions Every Adopting Universe Must Make

Resolve each before building the corresponding piece; until then, the defaults hold.

1. **NSID namespace domain** — defer until you actually publish; keep the placeholder-in-one-constant discipline.
2. **Identity model** — default: the graduation ladder (§7). Multiplayer → DIDs from day one.
3. **Public reading surface** — any static-site stack works; the records don't care.
4. **Gated content** — gate in your own surface layer; never publish private records to a public protocol repo.
5. **Records layout** — default: per-story (`records/book1/`); a series-wide merge is trivial later.
