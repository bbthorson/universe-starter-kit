import fs from 'fs';
import path from 'path';
import { Config } from '../config.js';
import { Registry } from '../registry/entities.js';
import { ChapterData, LinterEngine } from '../linter/engine.js';

function getBookKey(storyDir: string): string {
  const base = path.basename(storyDir);
  const m = base.match(/^0*(\d+)/);
  if (m) {
    return `book${parseInt(m[1], 10)}`;
  }
  return base.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function getOverviewOneline(filePath: string): string | null {
  if (!fs.existsSync(filePath)) return null;
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim().toLowerCase() === '## overview') {
      for (let j = i + 1; j < Math.min(i + 6, lines.length); j++) {
        let text = lines[j].trim();
        text = text.replace(/^\*|\*$/g, '').trim();
        text = text.replace(/^-/, '').trim();
        if (text) return text;
      }
    }
  }
  return null;
}

function splitRegister(value: string): { register: string; expr: string } {
  const val = value.trim();
  const m = val.match(/^([^(]+?)\s*(\(.*)?$/);
  const expr = (m ? m[1] : val).trim().replace(/;$/, '').trim();
  const register = expr.split(/\s*(?:->|→)\s*/)[0].trim();
  return { register, expr };
}

export interface CompilationResult {
  file: string;
  count: number;
}

export function compileProject(
  projectRoot: string,
  config: Config,
  registry: Registry,
  engine: LinterEngine
): CompilationResult[] {
  const NS = config.project.nsid;
  const outputDir = path.resolve(projectRoot, config.paths.output);
  const results: CompilationResult[] = [];

  const stories = engine.getStories();
  const allPlaces: any[] = [];
  const allProfiles: any[] = [];

  // 1. Stories compile (scenes and state events)
  for (const storyDir of stories) {
    const book = getBookKey(storyDir);
    const chapters = engine.loadChapters(storyDir);
    if (chapters.length === 0) continue;

    const scenes: any[] = [];
    const events: any[] = [];

    for (const ch of chapters) {
      if (ch.dates.length === 0) continue;
      const storyDate = ch.dates[0];
      const storyDateEnd = ch.dates.length > 1 ? ch.dates[ch.dates.length - 1] : null;
      const chRef = `${book}#ch${ch.chapterNum}`;
      const sceneId = `scene.${book}.ch${ch.chapterNum}`;

      // Resolve locations
      const placeRefs: string[] = [];
      const placeText: string[] = [];
      for (const loc of ch.locationNames) {
        const resolved = registry.resolve(loc, 'place');
        if (resolved) {
          if (!placeRefs.includes(resolved.id)) {
            placeRefs.push(resolved.id);
          }
        } else if (registry.isNonEntity(loc)) {
          const norm = registry.normalize(loc);
          if (norm && !placeText.includes(norm)) {
            placeText.push(norm);
          }
        }
      }

      // Resolve people helper
      const resolvePeople = (names: string[]): string[] => {
        const ids: string[] = [];
        for (const name of names) {
          const resolved = registry.resolve(name, 'character');
          if (resolved && !ids.includes(resolved.id)) {
            ids.push(resolved.id);
          }
        }
        return ids;
      };

      const participants = resolvePeople(ch.charactersPresent);
      const referenced = resolvePeople(ch.charactersReferenced);
      const povId = ch.pov ? registry.resolve(ch.pov, 'character')?.id || null : null;

      const scene: any = {
        $type: `${NS}.scene`,
        id: sceneId,
        storyDate,
        chapterRefs: [chRef],
        title: ch.title,
        part: ch.frontmatter.part !== undefined ? ch.frontmatter.part : null,
        beat: ch.frontmatter.beat || null,
        placeRefs,
        placeText: placeText.length > 0 ? placeText : null,
        pov: povId,
        participants,
        referenced,
        primaryEvent: ch.beatPurpose,
        createdAt: storyDate,
        sourceFile: ch.relativeFilePath,
      };

      if (storyDateEnd) {
        scene.storyDateEnd = storyDateEnd;
      }

      scenes.push(scene);

      // Registers / state events
      for (const [name, val] of Object.entries(ch.registers)) {
        const resolved = registry.resolve(name, 'character');
        if (!resolved) continue;

        const { register, expr } = splitRegister(val);
        const eventId = `stateEvent.${resolved.id.split('.', 2)[1]}.${book}.ch${ch.chapterNum}`;

        const ev: any = {
          $type: `${NS}.character.stateEvent`,
          id: eventId,
          subject: resolved.id,
          storyDate,
          register,
          state: val,
          chapterRef: chRef,
          sceneRef: sceneId,
          createdAt: storyDate,
          sourceFile: ch.relativeFilePath,
        };

        if (expr !== register) {
          ev.registerExpr = expr;
        }
        if (storyDateEnd) {
          ev.storyDateEnd = storyDateEnd;
        }

        events.push(ev);
      }
    }

    // Sort events
    events.sort((a, b) => {
      if (a.subject !== b.subject) return a.subject.localeCompare(b.subject);
      if (a.storyDate !== b.storyDate) return a.storyDate.localeCompare(b.storyDate);
      return a.chapterRef.localeCompare(b.chapterRef);
    });

    // Write story files
    const bookDir = path.join(outputDir, book);
    fs.mkdirSync(bookDir, { recursive: true });

    const scenesPath = path.join(bookDir, 'scenes.json');
    fs.writeFileSync(scenesPath, JSON.stringify(scenes, null, 2) + '\n', 'utf-8');
    results.push({ file: path.relative(projectRoot, scenesPath), count: scenes.length });

    const eventsPath = path.join(bookDir, 'character_state_events.json');
    fs.writeFileSync(eventsPath, JSON.stringify(events, null, 2) + '\n', 'utf-8');
    results.push({ file: path.relative(projectRoot, eventsPath), count: events.length });
  }

  // 2. Locations / places compile
  const locationsDir = path.resolve(projectRoot, config.paths.locations);
  if (fs.existsSync(locationsDir)) {
    const locFiles = fs.readdirSync(locationsDir)
      .filter(f => f.endsWith('.md') && !f.startsWith('_') && f !== 'index.md')
      .sort();

    for (const file of locFiles) {
      const filePath = path.join(locationsDir, file);
      const content = fs.readFileSync(filePath, 'utf-8');
      const { data } = engine.parseFrontmatter(content);

      if (data && data.id && String(data.id).startsWith('place.')) {
        allPlaces.push({
          $type: `${NS}.place`,
          id: data.id,
          name: data.title || '',
          status: data.status || 'active',
          region: data.region || null,
          firstAppearance: data.first_appearance || null,
          schedule: data.schedule || null,
          sourceFile: path.relative(projectRoot, filePath),
        });
      }
    }
  }

  // 3. Characters profiles compile
  for (const ent of registry.allEntities) {
    if (ent.type === 'character' && ent.status === 'active') {
      const srcFile = ent.sourceFile ? path.resolve(projectRoot, ent.sourceFile) : '';
      const oneLine = srcFile ? getOverviewOneline(srcFile) : null;

      allProfiles.push({
        $type: `${NS}.character.profile`,
        id: `profile.${ent.id.split('.', 2)[1]}`,
        subject: ent.id,
        displayName: ent.displayName,
        oneLine,
        sourceFile: ent.sourceFile || '',
      });
    }
  }

  // Write series files
  const seriesDir = path.join(outputDir, 'series');
  fs.mkdirSync(seriesDir, { recursive: true });

  if (allPlaces.length > 0) {
    const placesPath = path.join(seriesDir, 'places.json');
    fs.writeFileSync(placesPath, JSON.stringify(allPlaces, null, 2) + '\n', 'utf-8');
    results.push({ file: path.relative(projectRoot, placesPath), count: allPlaces.length });
  }

  if (allProfiles.length > 0) {
    const profilesPath = path.join(seriesDir, 'character_profiles.json');
    fs.writeFileSync(profilesPath, JSON.stringify(allProfiles, null, 2) + '\n', 'utf-8');
    results.push({ file: path.relative(projectRoot, profilesPath), count: allProfiles.length });
  }

  return results;
}
