import type { Channel, Program, EPGCache } from '../types/epg';
import cacheRaw from '../data/epg-cache.json';

const cache = cacheRaw as unknown as EPGCache;

export function getAllChannels(): Channel[] {
  return cache.channels || [];
}

export function getChannel(id: string): Channel | undefined {
  return (cache.channels || []).find(c => c.id === id);
}

export function getAllPrograms(): Program[] {
  return cache.programs || [];
}

export function getProgramsForChannel(channelId: string): Program[] {
  return (cache.programs || []).filter(p => p.channelId === channelId);
}

export interface PrimeItem {
  channel: Channel;
  program?: Program;
  nextProgram?: Program;
  currentProgram?: Program;
  progressPercent: number;
}

/**
 * Returns programs for prime time tonight in Spain (centered on 22:00 / 22:30),
 * along with currently live broadcast and next upcoming program.
 */
export function getTonightPrimePrograms(referenceDate = new Date()): PrimeItem[] {
  const channels = getAllChannels();
  const allProgs = getAllPrograms();
  const nowMs = referenceDate.getTime();

  return channels.map(channel => {
    const chProgs = allProgs.filter(p => p.channelId === channel.id);
    
    // 1. Prime Time program: flagged as isTonightPrime or best match around 22:00
    let primeProg = chProgs.find(p => p.isTonightPrime);

    if (!primeProg) {
      primeProg = chProgs.find(p => {
        const h = parseInt(p.startMadrid.split(':')[0], 10);
        return h >= 21 && h <= 23;
      });
    }

    let nextProg: Program | undefined = undefined;
    if (primeProg) {
      const idx = chProgs.findIndex(p => p.id === primeProg!.id);
      if (idx !== -1 && idx + 1 < chProgs.length) {
        nextProg = chProgs[idx + 1];
      }
    }

    // 2. Currently on air program & progress
    let currentProg: Program | undefined = undefined;
    let progressPercent = 0;

    for (let i = 0; i < chProgs.length; i++) {
      const startMs = new Date(chProgs[i].startTime).getTime();
      const stopMs = new Date(chProgs[i].stopTime).getTime();

      if (nowMs >= startMs && nowMs < stopMs) {
        currentProg = chProgs[i];
        const total = stopMs - startMs;
        const elapsed = nowMs - startMs;
        progressPercent = Math.min(100, Math.max(0, Math.round((elapsed / total) * 100)));
        break;
      }
    }

    if (!currentProg && chProgs.length > 0) {
      currentProg = primeProg || chProgs[0];
      progressPercent = 45;
    }

    return {
      channel,
      program: primeProg || chProgs[0],
      nextProgram: nextProg,
      currentProgram: currentProg,
      progressPercent
    };
  });
}

/**
 * Returns the program currently on air for each channel.
 */
export function getOnNowPrograms(referenceDate = new Date()): { channel: Channel; current: Program | undefined; next: Program | undefined; progressPercent: number }[] {
  const channels = getAllChannels();
  const allProgs = getAllPrograms();
  const nowMs = referenceDate.getTime();

  return channels.map(channel => {
    const chProgs = allProgs.filter(p => p.channelId === channel.id);
    let current: Program | undefined;
    let next: Program | undefined;
    let progressPercent = 0;

    for (let i = 0; i < chProgs.length; i++) {
      const startMs = new Date(chProgs[i].startTime).getTime();
      const stopMs = new Date(chProgs[i].stopTime).getTime();

      if (nowMs >= startMs && nowMs < stopMs) {
        current = chProgs[i];
        if (i + 1 < chProgs.length) {
          next = chProgs[i + 1];
        }
        const total = stopMs - startMs;
        const elapsed = nowMs - startMs;
        progressPercent = Math.min(100, Math.max(0, Math.round((elapsed / total) * 100)));
        break;
      }
    }

    // Fallback if now is slightly out of bounds
    if (!current && chProgs.length > 0) {
      current = chProgs[0];
      next = chProgs[1];
      progressPercent = 30;
    }

    return { channel, current, next, progressPercent };
  });
}

/**
 * Filter all programs categorized as Movies (deduplicated by channel & title)
 */
export function getMoviesToday(): { channel: Channel; program: Program }[] {
  const allProgs = getAllPrograms();
  const channelsMap = new Map(getAllChannels().map(c => [c.id, c]));
  const seen = new Set<string>();

  return allProgs
    .filter(p => p.category === 'movies')
    .filter(p => {
      const key = `${p.channelId}-${p.title.trim().toLowerCase()}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .map(program => ({
      channel: channelsMap.get(program.channelId)!,
      program
    }))
    .filter(item => item.channel !== undefined)
    .slice(0, 150);
}

/**
 * Filter all programs categorized as Sports (deduplicated repeat broadcasts)
 */
export function getSportsToday(): { channel: Channel; program: Program }[] {
  const allProgs = getAllPrograms();
  const channelsMap = new Map(getAllChannels().map(c => [c.id, c]));
  const seen = new Set<string>();

  return allProgs
    .filter(p => p.category === 'sports')
    .filter(p => {
      const baseTitle = p.title.split('·')[0].split('-')[0].trim().toLowerCase();
      const key = `${p.channelId}-${baseTitle}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .map(program => ({
      channel: channelsMap.get(program.channelId)!,
      program
    }))
    .filter(item => item.channel !== undefined)
    .slice(0, 120);
}

/**
 * Filter all programs categorized as Series (deduplicated repeat episodes per channel)
 */
export function getSeriesToday(): { channel: Channel; program: Program }[] {
  const allProgs = getAllPrograms();
  const channelsMap = new Map(getAllChannels().map(c => [c.id, c]));
  const seen = new Set<string>();

  return allProgs
    .filter(p => p.category === 'series')
    .filter(p => {
      const baseTitle = p.title.split(' T')[0].split('·')[0].split('-')[0].trim().toLowerCase();
      const key = `${p.channelId}-${baseTitle}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .map(program => ({
      channel: channelsMap.get(program.channelId)!,
      program
    }))
    .filter(item => item.channel !== undefined)
    .slice(0, 120);
}

/**
 * Programs for tomorrow (Prime Time estelar por canal)
 */
export function getTomorrowPrograms(): { channel: Channel; program: Program }[] {
  const allProgs = getAllPrograms();
  const channelsMap = new Map(getAllChannels().map(c => [c.id, c]));
  
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const tomorrowDateStr = tomorrow.toISOString().split('T')[0];

  const seen = new Set<string>();
  const tomorrowProgs = allProgs.filter(p => {
    if (!p.startTime.startsWith(tomorrowDateStr) || !p.isTonightPrime) return false;
    if (seen.has(p.channelId)) return false;
    seen.add(p.channelId);
    return true;
  });

  return tomorrowProgs.map(program => ({
    channel: channelsMap.get(program.channelId)!,
    program
  })).filter(item => item.channel !== undefined);
}
