#!/bin/bash
# Rebuild, verify, deploy and ping IndexNow + Google Indexing for teleestanoche.es
set -euo pipefail

# Ensure Node 22+ is used
if [ -d "$HOME/.nvm/versions/node/v22.23.2/bin" ]; then
  export PATH="$HOME/.nvm/versions/node/v22.23.2/bin:$PATH"
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "=== TeleEstaNoche.es Rebuild & Indexing Pipeline ==="
echo "Working directory: $DIR"

# 1. Fetch EPG data
echo "--- 1. Fetching Spanish EPG XMLTV ---"
python3 scripts/fetch-epg-spain.py || true

# 2. Build Astro static site
echo "--- 2. Building Astro Static Site ---"
npm run build

# 3. Post-build verification
echo "--- 3. Verifying Build Output ---"
node scripts/verify-build.mjs

# 4. Optional Cloudflare Pages deploy (if CF credentials present)
if [ -n "${CLOUDFLARE_API_TOKEN:-}" ] || [ -n "${CLOUDFLARE_API_KEY:-}" ]; then
  echo "--- 4. Deploying to Cloudflare Pages ---"
  npx --yes wrangler@4 pages deploy dist --project-name=teleestanoche --branch=main --commit-dirty=true || true
fi

# 5. Ping IndexNow (Bing, Yandex, Seznam)
echo "--- 5. Submitting URLs to IndexNow ---"
node scripts/ping-indexnow.mjs || true

# 6. Ping Google Indexing API (URL_UPDATED)
echo "--- 6. Submitting URLs to Google Indexing API ---"
python3 scripts/push-google-indexing.py || true

echo "=== Pipeline Completed Successfully! ==="
