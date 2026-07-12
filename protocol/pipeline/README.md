# Extraction Pipeline

Re-runnable, read-only pipeline that turns chapter frontmatter + canon files into validated record instances. This is the "repo → records" step from [`../ARCHITECTURE.md`](../ARCHITECTURE.md) §10.

```sh
python3 protocol/pipeline/extract.py
```

Exit 0 = clean build (all records extracted, **every reference resolved through the registry**). Exit 1 = a reference didn't resolve, a date is malformed, or a record failed its lexicon schema (records are still written so you can inspect them). Runs on stock Python 3 — no dependencies, no network.

## What it emits

Output goes to `../records/` — **disposable build output**; the pipeline + `entities/` + `lexicons/` are the source of truth. Regenerate any time.

| File | Record type | Source |
|------|-------------|--------|
| `records/<book>/scenes.json` | `scene` | chapter frontmatter (date/place/participants/pov/beat_purpose) |
| `records/<book>/character_state_events.json` | `character.stateEvent` | per-chapter `registers` frontmatter |
| `records/series/places.json` | `place` | `canon library/locations/*.md` frontmatter |
| `records/series/character_profiles.json` | `character.profile` | registry + character files (reader-safe facts only) |

`item` + `custodyEvent` lexicons are provided but have no generic extractor — the custody chain is authored in your `subplot_threads.md` object-custody table. When an object matters enough to trace, add a small extractor for it following the same pattern (resolve every holder through the registry; `createdAt = storyDate`).

## How it stays honest

1. **Deterministic resolution.** Every character/place reference (scene participants + pov, stateEvent subjects, place refs) is normalized and looked up in `../entities/entities.yaml` by the same parser the resolver uses. An unresolved reference is a **build error, not a guess**. Deliberate one-offs come from `../entities/non_entities.yaml` and are handled explicitly — one-off scene settings are kept verbatim as `placeText`.
2. **Schema validation.** Every record is checked against its schema in `../lexicons/` (required fields, types, patterns, enums, no unexpected fields).
3. **`createdAt = storyDate`** on every event record, so record sets sort chronologically on any surface that honors `createdAt` (ARCHITECTURE.md §8).

## Adapting to your universe

- The NSID root is one constant (`NS` in `extract.py`) plus the lexicons' `$id`/`$type` — swap `example.universe` for a domain you own before publishing.
- The register vocabulary is one regex (`VALID_REGISTER`) plus the enum in `lexicons/character/stateEvent.json` — change together with your matrix/voice guide.
- `place.region` and `place.schedule` are emitted as `null` — enrich them from your locations index's operating rules when a reader surface needs open/closed logic.
- `character.profile.personaPublic` / `keyContradiction` are interpretive; fill them in a curated pass deciding which facts are reader-safe.
