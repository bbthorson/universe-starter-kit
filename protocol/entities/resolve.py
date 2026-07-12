#!/usr/bin/env python3
"""
Entity resolution sanity check.

Proves that EVERY distinct name used across chapter frontmatter in this repo
(`pov`, `characters_present`, `characters_referenced`, `registers` keys, and
`location`) either:
  (a) resolves to an entities.yaml `id` via an alias, or
  (b) is on the documented intentional non-entity list (non_entities.yaml).

Any name that does neither is a MISS and fails the check. Resolution is
type-aware: `location` values resolve against places; the character fields
resolve against characters. This keeps a character ("Sofia") distinct from a
place named after them ("Sofia's Cheese Shop").

Scans every story under stories/ except the `_story_template` scaffold;
within a story's chapters/ folder, files prefixed `00_` (outlines, guides)
are skipped.

No external dependencies — a minimal frontmatter/registry parser is used so
this runs on a stock Python 3 (no PyYAML required). No network.

Usage:  python3 protocol/entities/resolve.py
Exit 0 if the corpus resolves cleanly; exit 1 if there are misses.
"""
import os
import re
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
STORIES = os.path.join(ROOT, "stories")

CHAR_FIELDS = ("pov", "characters_present", "characters_referenced")  # + registers keys
PLACE_FIELDS = ("location",)


# --------------------------------------------------------------------------
# Minimal parsers (no PyYAML)
# --------------------------------------------------------------------------
def read_frontmatter_lines(path):
    """Return the lines between the first two '---' fences."""
    lines = open(path, encoding="utf-8").read().splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    out = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        out.append(line)
    return out


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
        s = s[1:-1]
    return s.strip()


def parse_registry(path):
    """
    Parse entities.yaml just enough to build: alias(lower) -> (id, type).
    Understands the grouped-list shape this file uses: top-level group keys
    (characters:/places:/items:), list entries starting with '- id:', scalar
    fields, and both inline (["a","b"]) and block aliases.
    """
    alias_map = {}          # lower(alias) -> (id, type)
    entries = []            # list of dicts
    cur = None
    in_aliases_block = False

    for raw in open(path, encoding="utf-8").read().splitlines():
        line = raw.split("#", 1)[0] if not _in_string_hash(raw) else raw
        if not line.strip():
            continue

        m_item = re.match(r"^\s*-\s+id:\s*(.+)$", line)
        if m_item:
            if cur:
                entries.append(cur)
            cur = {"id": unquote(m_item.group(1)), "aliases": []}
            in_aliases_block = False
            continue

        if cur is None:
            continue

        m_alias_inline = re.match(r"^\s*aliases:\s*\[(.*)\]\s*$", line)
        if m_alias_inline:
            cur["aliases"] = [unquote(x) for x in _split_inline_list(m_alias_inline.group(1))]
            in_aliases_block = False
            continue

        if re.match(r"^\s*aliases:\s*$", line):
            in_aliases_block = True
            continue

        m_block_item = re.match(r"^\s*-\s+(.*)$", line)
        if in_aliases_block and m_block_item:
            cur["aliases"].append(unquote(m_block_item.group(1)))
            continue

        m_field = re.match(r"^\s{2,}(\w+):\s*(.*)$", line)
        if m_field:
            in_aliases_block = False
            key, val = m_field.group(1), m_field.group(2)
            if key in ("type", "displayName", "status"):
                cur[key] = unquote(val)
            continue

    if cur:
        entries.append(cur)

    for e in entries:
        for a in e.get("aliases", []):
            alias_map[a.lower()] = (e["id"], e.get("type", ""))
    return alias_map, entries


def _in_string_hash(line):
    # Keep '#' inside quoted aliases (e.g. hashtags) — a coarse guard so the
    # comment-stripper doesn't chop a legitimate value. We only strip comments
    # on lines that clearly aren't quoted values.
    return '"' in line and line.count('"') >= 2 and "#" in line and line.index('"') < line.index("#")


def _split_inline_list(s):
    # split on commas that are not inside quotes
    parts, buf, q = [], "", None
    for ch in s:
        if q:
            buf += ch
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
            buf += ch
        elif ch == ",":
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    if buf.strip():
        parts.append(buf)
    return [p for p in parts if p.strip()]


def parse_non_entities(path):
    """Return (exact_lower:set, prefix_lower:list)."""
    exact, prefixes = set(), []
    pending_pattern = None
    for raw in open(path, encoding="utf-8").read().splitlines():
        line = raw.split("#", 1)[0]
        if not line.strip():
            continue
        if re.match(r"^(\w+):\s*$", line):
            continue
        m_pat = re.match(r"^\s*-\s+pattern:\s*(.+)$", line)
        if m_pat:
            pending_pattern = unquote(m_pat.group(1))
            continue
        m_prefix = re.match(r"^\s*prefix:\s*(true|false)\s*$", line)
        if m_prefix and pending_pattern is not None:
            if m_prefix.group(1) == "true":
                prefixes.append(pending_pattern.lower())
            else:
                exact.add(pending_pattern.lower())
            pending_pattern = None
            continue
        m_item = re.match(r"^\s*-\s+(.+)$", line)
        if m_item:
            exact.add(unquote(m_item.group(1)).lower())
    if pending_pattern is not None:
        exact.add(pending_pattern.lower())
    return exact, prefixes


# --------------------------------------------------------------------------
# Corpus extraction
# --------------------------------------------------------------------------
def chapter_corpus():
    """Every chapter file in every real story (template + 00_* files skipped)."""
    out = []
    for path in sorted(glob.glob(os.path.join(STORIES, "*", "chapters", "*.md"))):
        story_dir = os.path.basename(os.path.dirname(os.path.dirname(path)))
        base = os.path.basename(path)
        if story_dir.startswith("_") or base.startswith("00_"):
            continue
        out.append(path)
    return out


def extract_names(fm_lines):
    """Return dict field -> list of raw values for the fields we resolve."""
    found = {"pov": [], "characters_present": [], "characters_referenced": [],
             "location": [], "registers": []}
    cur = None
    in_registers = False
    for line in fm_lines:
        m_top = re.match(r"^(\w+):\s*(.*)$", line)
        if m_top and not line.startswith(" "):
            key, val = m_top.group(1), m_top.group(2).strip()
            cur = key
            in_registers = (key == "registers")
            if key == "pov" and val:
                found["pov"].append(unquote(val))
            continue
        m_list = re.match(r"^\s+-\s+(.*)$", line)
        if m_list and cur in ("characters_present", "characters_referenced", "location"):
            found[cur].append(unquote(m_list.group(1)))
            continue
        m_reg = re.match(r"^\s+([A-Za-z][\w '\-&]*?):\s+(.*)$", line)
        if m_reg and in_registers:
            found["registers"].append(unquote(m_reg.group(1).strip()))
            continue
    return found


def normalize(raw):
    """Strip surrounding quotes and a trailing '(...)' annotation."""
    s = unquote(raw)
    s = re.sub(r"\s*\([^()]*\)\s*$", "", s).strip()
    return s


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    alias_map, entries = parse_registry(os.path.join(HERE, "entities.yaml"))
    ne_exact, ne_prefixes = parse_non_entities(os.path.join(HERE, "non_entities.yaml"))

    def is_non_entity(name):
        low = name.lower()
        if low in ne_exact:
            return True
        return any(low.startswith(p) for p in ne_prefixes)

    def resolve(name, want_type):
        low = name.lower()
        hit = alias_map.get(low)
        if hit and (want_type is None or hit[1] == want_type):
            return hit[0]
        return None

    resolved = {}       # normalized name -> id
    non_entities = set()
    misses = []         # (name, want_type, chapter, field)

    chapter_files = chapter_corpus()
    for path in chapter_files:
        fm = read_frontmatter_lines(path)
        names = extract_names(fm)
        ch = os.path.relpath(path, STORIES)
        buckets = [
            ("pov", "character", names["pov"]),
            ("characters_present", "character", names["characters_present"]),
            ("characters_referenced", "character", names["characters_referenced"]),
            ("registers", "character", names["registers"]),
            ("location", "place", names["location"]),
        ]
        for field, want_type, values in buckets:
            for raw in values:
                nm = normalize(raw)
                if not nm:
                    continue
                rid = resolve(nm, want_type)
                if rid:
                    resolved[nm] = rid
                elif is_non_entity(nm):
                    non_entities.add(nm)
                else:
                    misses.append((nm, want_type, ch, field))

    # ---- Report ----
    print("=" * 70)
    print("ENTITY RESOLUTION SANITY CHECK — chapter frontmatter corpus")
    print("=" * 70)
    print(f"Chapters scanned:        {len(chapter_files)}")
    print(f"Registry entities:       {len(entries)}")
    print(f"Distinct names resolved: {len(resolved)}")
    print(f"Distinct non-entities:   {len(non_entities)}")
    print(f"Misses:                  {len(misses)}")
    print()

    print("--- Resolved (name -> id) ---")
    for nm in sorted(resolved):
        print(f"  {nm:<40} -> {resolved[nm]}")
    print()
    print("--- Intentional non-entities (expected non-matches) ---")
    for nm in sorted(non_entities):
        print(f"  {nm}")
    print()

    if misses:
        print("!!! MISSES — names that neither resolve nor are documented one-offs:")
        seen = set()
        for nm, wt, ch, field in misses:
            key = (nm, wt)
            if key in seen:
                continue
            seen.add(key)
            print(f"  [{wt or 'any'}] {nm!r}  (first seen {ch} / {field})")
        print()
        print("FAIL — resolve these (add alias to entities.yaml or list in "
              "non_entities.yaml).")
        return 1

    print("OK — every distinct frontmatter name resolves to a registry id or "
          "is a documented one-off. No silent misses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
