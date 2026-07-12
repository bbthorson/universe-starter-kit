#!/usr/bin/env python3
"""
Reference extraction pipeline: repo -> records.

Re-runnable, read-only. Turns chapter frontmatter + canon files into validated
record instances (ARCHITECTURE.md §10). Emits the four record types that are
fully derivable from the kit's standard file shapes:

  scene                  one per chapter        <- chapter frontmatter
  character.stateEvent   one per char per ch    <- frontmatter `registers`
  place                  one per location file  <- canon library/locations/*
  character.profile      one per character      <- registry + character files

item + custodyEvent are universe-specific (the custody chain is authored in
tracking/subplot_threads.md prose tables) — add an extractor for your object
following the same pattern; the lexicons for both are already in place.

How it stays honest:
  * Every character/place reference is resolved through
    entities/entities.yaml. An UNRESOLVED reference is a build error, not a
    guess; deliberate one-offs come from non_entities.yaml.
  * Every record is checked against its schema in lexicons/.
  * createdAt is set from storyDate (§8) so records sort chronologically.

Output: protocol/records/<book>/scenes.json + character_state_events.json,
and protocol/records/series/places.json + character_profiles.json.
`records/` is disposable build output — regenerate any time.

Stock Python 3, no dependencies, no network.

Usage:  python3 protocol/pipeline/extract.py
Exit 0 = clean build. Exit 1 = unresolved reference / malformed date /
schema failure (records are still written so you can inspect them).
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("UNIVERSE_ROOT") or os.path.abspath(os.path.join(HERE, "..", ".."))
ENTITIES = os.path.join(ROOT, "protocol", "entities")
LEXICONS = os.path.join(ROOT, "protocol", "lexicons")
STORIES = os.path.join(ROOT, "stories")
LOCATIONS = os.path.join(ROOT, "canon library", "locations")
OUT = os.path.join(ROOT, "protocol", "records")

# Placeholder NSID root — swap for a domain you own before publishing anywhere
# (ARCHITECTURE.md §5). This constant and the lexicons' $id/$type are the ONLY
# places the root appears.
NS = "example.universe"

# The kit's default register vocabulary (see character_matrix.md). If your
# voice guide defines a different one, change it here AND in
# lexicons/character/stateEvent.json.
VALID_REGISTER = re.compile(r"^(public|private|under-pressure)$")

sys.path.insert(0, ENTITIES)
from resolve import (  # noqa: E402
    parse_registry, parse_non_entities, read_frontmatter_lines, unquote, normalize,
)

ERRORS = []


def err(msg):
    ERRORS.append(msg)


# --------------------------------------------------------------------------
# Registry-backed resolution
# --------------------------------------------------------------------------
ALIAS_MAP, ENTRIES = parse_registry(os.path.join(ENTITIES, "entities.yaml"))
NE_EXACT, NE_PREFIXES = parse_non_entities(os.path.join(ENTITIES, "non_entities.yaml"))
DISPLAY = {e["id"]: e.get("displayName", e["id"]) for e in ENTRIES}


def is_non_entity(name):
    low = name.lower()
    return low in NE_EXACT or any(low.startswith(p) for p in NE_PREFIXES)


def resolve(name, want_type, ctx):
    """Resolve a raw frontmatter name to a registry id, or None.

    Returns (id | None, status) where status is 'resolved', 'non-entity',
    'empty', or 'MISS'. A MISS is recorded as a build error.
    """
    nm = normalize(name)
    if not nm:
        return None, "empty"
    hit = ALIAS_MAP.get(nm.lower())
    if hit and (want_type is None or hit[1] == want_type):
        return hit[0], "resolved"
    if is_non_entity(nm):
        return None, "non-entity"
    err(f"UNRESOLVED {want_type or 'any'} ref {nm!r} ({ctx})")
    return None, "MISS"


# --------------------------------------------------------------------------
# Corpus: stories and chapters
# --------------------------------------------------------------------------
def story_dirs():
    """Real story folders (the _story_template scaffold is skipped)."""
    out = []
    if not os.path.isdir(STORIES):
        return out
    for name in sorted(os.listdir(STORIES)):
        path = os.path.join(STORIES, name)
        if os.path.isdir(path) and not name.startswith(("_", ".")):
            out.append(path)
    return out


def book_key(story_dir):
    """'01. The Case of ...' or '01_example' -> 'book1'; else a slug."""
    base = os.path.basename(story_dir)
    m = re.match(r"^0*(\d+)", base)
    if m:
        return f"book{int(m.group(1))}"
    return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")


def chapter_files(story_dir):
    return [p for p in sorted(glob.glob(os.path.join(story_dir, "chapters", "*.md")))
            if not os.path.basename(p).startswith("00_")]


def parse_chapter_fm(path):
    fm = read_frontmatter_lines(path)
    data = {"location": [], "characters_present": [], "characters_referenced": [],
            "registers": {}, "pov": None, "chapter": None, "date": None,
            "title": None, "part": None, "beat": None, "beat_purpose": None}
    cur = None
    in_registers = False
    for line in fm:
        m_top = re.match(r"^(\w+):\s*(.*)$", line)
        if m_top and not line.startswith(" "):
            key, val = m_top.group(1), m_top.group(2).strip()
            cur = key
            in_registers = (key == "registers")
            if key == "meal":       # legacy alias for `part`
                key = "part"
            if key in ("pov", "chapter", "date", "title", "part", "beat",
                       "beat_purpose") and val:
                data[key] = unquote(val)
            continue
        m_list = re.match(r"^\s+-\s+(.*)$", line)
        if m_list and cur in ("location", "characters_present", "characters_referenced"):
            data[cur].append(unquote(m_list.group(1)))
            continue
        m_reg = re.match(r"^\s+([A-Za-z][\w '\-&]*?):\s+(.*)$", line)
        if m_reg and in_registers:
            data["registers"][unquote(m_reg.group(1).strip())] = unquote(m_reg.group(2))
    return data


def dates_of(date_str):
    return re.findall(r"\d{4}-\d{2}-\d{2}", date_str or "")


# --------------------------------------------------------------------------
# Extractors
# --------------------------------------------------------------------------
def extract_story(story_dir):
    """Return (scenes, state_events) for one story."""
    book = book_key(story_dir)
    scenes, events = [], []
    for path in chapter_files(story_dir):
        fm = parse_chapter_fm(path)
        if not fm["chapter"]:
            continue
        num = int(fm["chapter"])
        ds = dates_of(fm["date"])
        if not ds:
            err(f"{os.path.relpath(path, ROOT)}: no ISO date in frontmatter `date`")
        story_date = ds[0] if ds else None
        rel = os.path.relpath(path, ROOT)
        ch_ref = f"{book}#ch{num}"

        place_refs, place_text = [], []
        for loc in fm["location"]:
            rid, status = resolve(loc, "place", f"{rel} location")
            if rid and rid not in place_refs:
                place_refs.append(rid)
            elif status == "non-entity":
                pt = normalize(loc)
                if pt and pt not in place_text:
                    place_text.append(pt)

        def people(values, field):
            out = []
            for v in values:
                rid, _status = resolve(v, "character", f"{rel} {field}")
                if rid and rid not in out:
                    out.append(rid)
            return out

        participants = people(fm["characters_present"], "characters_present")
        referenced = people(fm["characters_referenced"], "characters_referenced")
        pov_id = None
        if fm["pov"]:
            pov_id, _ = resolve(fm["pov"], "character", f"{rel} pov")

        scene = {
            "$type": f"{NS}.scene",
            "id": f"scene.{book}.ch{num}",
            "storyDate": story_date,
            "chapterRefs": [ch_ref],
            "title": fm["title"],
            "part": int(fm["part"]) if fm["part"] and str(fm["part"]).isdigit() else fm["part"],
            "beat": fm["beat"],
            "placeRefs": place_refs,
            "placeText": place_text or None,
            "pov": pov_id,
            "participants": participants,
            "referenced": referenced,
            "primaryEvent": fm["beat_purpose"],
            "createdAt": story_date,
            "sourceFile": rel,
        }
        if len(ds) > 1:
            scene["storyDateEnd"] = ds[-1]
        if not place_refs and not place_text:
            err(f"{scene['id']}: no place (neither registered placeRef nor placeText)")
        scenes.append(scene)

        for name, value in fm["registers"].items():
            subject, status = resolve(name, "character", f"{rel} registers")
            if not subject:
                continue  # non-entity register keys are expected; misses already logged
            register, expr = split_register(value)
            if not VALID_REGISTER.match(register):
                err(f"BAD register {register!r} for {subject} ({rel})")
            ev = {
                "$type": f"{NS}.character.stateEvent",
                "id": f"stateEvent.{subject.split('.', 1)[1]}.{book}.ch{num}",
                "subject": subject,
                "storyDate": story_date,
                "register": register,
                "state": value,
                "chapterRef": ch_ref,
                "sceneRef": f"scene.{book}.ch{num}",
                "createdAt": story_date,
                "sourceFile": rel,
            }
            if expr != register:
                ev["registerExpr"] = expr
            if len(ds) > 1:
                ev["storyDateEnd"] = ds[-1]
            events.append(ev)

    events.sort(key=lambda r: (r["subject"], r["storyDate"] or "", r["chapterRef"]))
    return scenes, events


def split_register(value):
    """'private -> under-pressure (note)' -> ('private', 'private -> under-pressure')."""
    value = value.strip()
    m = re.match(r"^([^(]+?)\s*(\(.*)?$", value)
    expr = (m.group(1) if m else value).strip().rstrip(";").strip()
    register = re.split(r"\s*(?:->|→)\s*", expr)[0].strip()
    return register, expr


def parse_simple_fm(path, keys):
    fm = read_frontmatter_lines(path)
    data = {k: None for k in keys}
    for line in fm:
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m and m.group(1) in keys:
            data[m.group(1)] = unquote(m.group(2).strip())
    return data


def extract_places():
    places = []
    for path in sorted(glob.glob(os.path.join(LOCATIONS, "*.md"))):
        base = os.path.basename(path)
        if base.startswith("00_") or base == "index.md":
            continue
        fm = parse_simple_fm(path, ("id", "title", "status", "first_appearance"))
        pid = fm["id"]
        if not pid or not pid.startswith("place."):
            err(f"{os.path.relpath(path, ROOT)}: location file missing `id: place.*` frontmatter")
            continue
        places.append({
            "$type": f"{NS}.place",
            "id": pid,
            "name": fm["title"],
            "status": fm["status"],
            # region + schedule are universe-specific enrichments: derive them
            # from your locations index / per-file operating rules.
            "region": None,
            "firstAppearance": fm["first_appearance"],
            "schedule": None,
            "sourceFile": os.path.relpath(path, ROOT),
        })
    # sanity: every registered place has a file/record
    got = {p["id"] for p in places}
    for e in ENTRIES:
        if e.get("type") == "place" and e["id"] not in got:
            err(f"registry place {e['id']} has no location record")
    return places


def overview_oneline(path):
    """The text following an '## Overview' heading, as the one-line summary."""
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except OSError:
        return None
    for i, l in enumerate(lines):
        if l.strip().lower() == "## overview":
            for j in range(i + 1, min(i + 6, len(lines))):
                t = lines[j].strip().lstrip("*").strip()
                t = re.sub(r"^\*|\*$", "", t).strip()
                if t:
                    return t
    return None


def extract_profiles():
    """One profile per active registered character that has a source file.
    Only reader-safe structured facts (ARCHITECTURE.md §6): personaPublic /
    keyContradiction are interpretive and left for a curated pass."""
    profiles = []
    for e in ENTRIES:
        if e.get("type") != "character" or e.get("status") != "active":
            continue
        src = e.get("sourceFile")
        rec = {
            "$type": f"{NS}.character.profile",
            "id": f"profile.{e['id'].split('.', 1)[1]}",
            "subject": e["id"],
            "displayName": DISPLAY.get(e["id"], e["id"]),
            "oneLine": overview_oneline(os.path.join(ROOT, src)) if src else None,
            "sourceFile": src or "",
        }
        profiles.append(rec)
    return profiles


# --------------------------------------------------------------------------
# Validation + write
# --------------------------------------------------------------------------
def validate_common(rec):
    for k in ("storyDate", "createdAt"):
        if k in rec and rec[k] and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(rec[k])):
            err(f"{rec.get('id')}: bad {k} {rec[k]!r}")
    if rec.get("createdAt") and rec.get("storyDate") and rec["createdAt"] != rec["storyDate"]:
        err(f"{rec.get('id')}: createdAt != storyDate")


def _type_ok(val, types):
    if isinstance(types, str):
        types = [types]
    for t in types:
        if t == "null" and val is None:
            return True
        if t == "string" and isinstance(val, str):
            return True
        if t == "integer" and isinstance(val, int) and not isinstance(val, bool):
            return True
        if t == "array" and isinstance(val, list):
            return True
        if t == "object" and isinstance(val, dict):
            return True
    return False


def check_schema(rec, schema, label):
    """Recursive JSON-Schema check: required, const, enum, type, pattern,
    additionalProperties:false, nested objects and array items. Enough for
    the lexicons in this repo — no external dependency."""
    def validate(v, s, path):
        if "const" in s and v != s["const"]:
            err(f"[{label}] {path}: must be {s['const']!r}")
        if "enum" in s and v not in s["enum"]:
            err(f"[{label}] {path}: {v!r} not in {s['enum']}")
        if "type" in s and not _type_ok(v, s["type"]):
            err(f"[{label}] {path}: {v!r} wrong type (want {s['type']})")
        if "pattern" in s and isinstance(v, str) and not re.search(s["pattern"], v):
            err(f"[{label}] {path}: {v!r} fails pattern {s['pattern']}")
        if isinstance(v, dict) and "properties" in s:
            props = s["properties"]
            for req in s.get("required", []):
                if req not in v:
                    err(f"[{label}] {path}: missing required field {req!r}")
            if s.get("additionalProperties") is False:
                for k in v:
                    if k not in props:
                        err(f"[{label}] {path}: unexpected field {k!r}")
            for k, sub in v.items():
                if k in props:
                    validate(sub, props[k], f"{path}.{k}")
        if isinstance(v, list) and "items" in s:
            for idx, item in enumerate(v):
                validate(item, s["items"], f"{path}[{idx}]")

    validate(rec, schema, rec.get("id", "?"))


def load_schema(rel):
    with open(os.path.join(LEXICONS, rel), encoding="utf-8") as f:
        return json.load(f)


def write(dirname, name, data):
    outdir = os.path.join(OUT, dirname)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return os.path.relpath(path, ROOT)


def main():
    scene_schema = load_schema("scene.json")
    event_schema = load_schema("character/stateEvent.json")
    place_schema = load_schema("place.json")
    profile_schema = load_schema("character/profile.json")

    written = []
    total = 0
    for story in story_dirs():
        book = book_key(story)
        scenes, events = extract_story(story)
        if not scenes:
            continue
        for rec in scenes + events:
            validate_common(rec)
            check_schema(rec, scene_schema if rec["$type"].endswith(".scene") else event_schema,
                         f"{book}")
        written.append((write(book, "scenes.json", scenes), len(scenes)))
        written.append((write(book, "character_state_events.json", events), len(events)))
        total += len(scenes) + len(events)

    places = extract_places()
    profiles = extract_profiles()
    for rec in places:
        check_schema(rec, place_schema, "places")
    for rec in profiles:
        check_schema(rec, profile_schema, "profiles")
    if places:
        written.append((write("series", "places.json", places), len(places)))
    if profiles:
        written.append((write("series", "character_profiles.json", profiles), len(profiles)))
    total += len(places) + len(profiles)

    print("=" * 68)
    print("EXTRACTION — repo -> records")
    print("=" * 68)
    for rel, n in written:
        print(f"  {n:>4} records -> {rel}")
    if not written:
        print("  (no stories with chapter frontmatter found — nothing to extract)")

    if ERRORS:
        print(f"\n!!! {len(ERRORS)} VALIDATION ERROR(S):")
        for e in ERRORS[:50]:
            print(f"  - {e}")
        print("\nFAIL — records written but the build is not clean.")
        return 1

    print(f"\nOK — {total} records extracted; every reference resolved through "
          "the registry. Clean build.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
