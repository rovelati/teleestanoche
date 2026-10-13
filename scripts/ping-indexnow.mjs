#!/usr/bin/env node
/**
 * ping-indexnow.mjs — teleestanoche.es
 * Submits all canonical URLs to IndexNow (Bing, Yandex, Seznam, etc.)
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const HOST = 'www.teleestanoche.es';
const KEY = '4f25c5dc3491468f8459b92c21bb3ac1';
const KEY_LOCATION = `https://${HOST}/${KEY}.txt`;
const ENDPOINTS = [
  'https://api.indexnow.org/indexnow',
  'https://www.bing.com/indexnow',
];

const channelsData = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../src/data/channels.json'), 'utf-8')
);

const ALL_URLS = [
  `https://${HOST}/`,
  `https://${HOST}/ahora/`,
  `https://${HOST}/peliculas-hoy/`,
  `https://${HOST}/series-hoy/`,
  `https://${HOST}/deportes-hoy/`,
  `https://${HOST}/manana/`,
  ...channelsData.map((c) => `https://${HOST}/${c.id}/`),
];

async function pingIndexNow() {
  console.log(`[IndexNow] Preparing Bing/IndexNow notification for ${HOST}...`);
  console.log(`[IndexNow] Submitting ${ALL_URLS.length} canonical URLs:`);
  ALL_URLS.forEach((u, i) => console.log(`  ${i + 1}. ${u}`));

  const payload = {
    host: HOST,
    key: KEY,
    keyLocation: KEY_LOCATION,
    urlList: ALL_URLS,
  };

  for (const endpoint of ENDPOINTS) {
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'User-Agent': 'TeleEstaNoche-IndexNow/1.0 (+https://www.teleestanoche.es)',
        },
        body: JSON.stringify(payload),
      });

      if (response.status === 200 || response.status === 202) {
        console.log(`[IndexNow] SUCCESS! (${endpoint}) Status ${response.status}: Submitted ${ALL_URLS.length} URLs.`);
      } else {
        const txt = await response.text();
        console.warn(`[IndexNow] WARN (${endpoint}): Status ${response.status} - ${txt}`);
      }
    } catch (error) {
      console.error(`[IndexNow] ERROR connecting to ${endpoint}:`, error.message);
    }
  }
}

pingIndexNow();
