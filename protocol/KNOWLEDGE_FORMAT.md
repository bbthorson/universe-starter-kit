# Knowledge Format Conventions — the inward layer

How the canon library and tracking files are structured so that any agent (or script) can consume the canon for drafting and continuity work with no bespoke parsing. This is the *inward* half of a two-format architecture: this file covers the knowledge graph you author against; `ARCHITECTURE.md` (the derived-records layer) covers the *outward* half you publish from. Two formats, opposite directions, shared identity.

The conventions follow Google's **Open Knowledge Format** (OKF, v0.1 — pin the version you conform to and expect churn; it's just markdown conventions, so churn is cheap). A canon library is already 90% OKF-shaped: markdown files, a concept graph (characters ↔ locations ↔ antagonists ↔ books), indexes, and a changelog. These conventions formalize the last 10%.

---

## The essentials

- **One concept = one markdown file.** The file path is the concept's identity.
- **Exactly one required frontmatter field:** `type`.
- Recommended queryable fields: `title`, `description`, `tags`, `timestamp`; `resource` where a canonical link exists.
- Body is freeform markdown.
- Concepts cross-link with normal markdown links → the directory becomes a graph. Replace prose references ("see the locations index") with real relative links so the graph is machine-traversable.
- Optional `index.md` per directory (progressive disclosure) and a chronological log — `CANON_CHANGELOG.md` is this repo's log of record.

## Type vocabulary (controlled list)

OKF leaves the type vocabulary to the producer. This kit's starting vocabulary — keep it small and documented here; expand deliberately:

| `type` | Applies to |
|---|---|
| `Character` | `canon library/characters/*` |
| `Antagonist` | `canon library/antagonists/*` |
| `Location` | `canon library/locations/*` |
| `Book` | `canon library/books/*` |
| `SeriesPlan` | `series_plan.md` (overview/index) |
| `Guide` | `world building/*` (craft rules) |
| `Reference` | `glossary.md`, `group_dynamics.md`, `locations/index.md` |
| `Continuity` | `continuity.md` |
| `StoryBible` | a story's metadata/background file |
| `Chapter` | `stories/*/chapters/*` (prose — light frontmatter only) |
| `Tracking` | `character_matrix.md`, `timeline_ledger.md`, `subplot_threads.md` |
| `Interiority` | `tracking/interiority/*` (private, never published) |
| `Template` | `00_*_template.md` files |

## Frontmatter standard

```yaml
---
type: Character            # required
title: "[Display Name]"    # recommended
description: One line — used by agents to decide relevance without opening the file.
tags: [main-cast, book1]
timestamp: 2026-01-01T00:00:00Z   # last meaningful update
# optional / project-specific:
id: char.example           # stable key — shared with protocol/entities/entities.yaml
status: active
---
```

Keep it minimal. `type` is the only hard requirement; add the rest where it earns its place.

## Identity: one key, three views

**The `id:` field is the bridge between layers.** The same stable key appears in:

1. the entity's markdown file frontmatter (human view),
2. `protocol/entities/entities.yaml` (the registry — maps id → aliases → file),
3. any derived record emitted by the outward layer (`ARCHITECTURE.md`).

Convention: **filename = id-slug** (`char.emma` → `characters/emma.md`). IDs are permanent; display names and even filenames may change, the id never does.

## Guardrails

- **Don't OKF-ify prose.** Chapters get the chapter-guide frontmatter only (which is richer than OKF's — dates, registers, threads); never fragment scenes into "concepts."
- **`Interiority` is part of the internal bundle** — included for authoring and agent use, kept private, never projected outward by any publishing layer.
- This serves authoring and the AI pipeline. If it starts feeling like bureaucracy, stop.
