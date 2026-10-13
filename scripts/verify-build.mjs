import fs from 'node:fs';
import path from 'node:path';

const distDir = path.resolve('dist');

console.log('[verify-build] Checking built artifacts in dist/ ...');

if (!fs.existsSync(distDir)) {
  console.error('[verify-build] ERROR: dist/ directory does not exist.');
  process.exit(1);
}

const requiredFiles = [
  'index.html',
  'ahora/index.html',
  'peliculas-hoy/index.html',
  'deportes-hoy/index.html',
  'series-hoy/index.html',
  'manana/index.html',
  'la-1/index.html',
  'antena-3/index.html',
  'telecinco/index.html',
  'cuatro/index.html',
  'lasexta/index.html',
  '404.html',
  'robots.txt',
  '_headers',
  'llms.txt',
  'sitemap.xml'
];

let missing = 0;
for (const file of requiredFiles) {
  const fullPath = path.join(distDir, file);
  if (!fs.existsSync(fullPath)) {
    console.error(`[verify-build] MISSING: ${file}`);
    missing++;
  }
}

if (missing > 0) {
  console.error(`[verify-build] FAILED: ${missing} required files are missing.`);
  process.exit(1);
}

console.log('[verify-build] SUCCESS: All Spanish critical routes and channels verified!');
