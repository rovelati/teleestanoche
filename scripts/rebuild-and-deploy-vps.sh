#!/bin/bash
set -euo pipefail

LOG="/var/log/teleestanoche-rebuild.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting TeleEstaNoche.es Rebuild & Ingestion..." | tee -a "$LOG"

cd /var/www/teleestanoche.es

# 1. Fetch XMLTV and refresh cache
python3 scripts/fetch-epg-spain.py 2>&1 | tee -a "$LOG"

# 2. Build Astro SSG
npm run build 2>&1 | tee -a "$LOG"

# 3. Deploy to Cloudflare Pages using Global Key
export CLOUDFLARE_API_KEY="9578b8b72ddb8947067606c42533c784203b6"
export CLOUDFLARE_EMAIL="romolo.velati@gmail.com"
export CLOUDFLARE_ACCOUNT_ID="383050c9ba92a1ab1144bc18d44f586c"
npx --yes wrangler@4 pages deploy dist --project-name=teleestanoche --branch=main --commit-dirty=true 2>&1 | tee -a "$LOG"

# 4. Ping IndexNow
node scripts/ping-indexnow.mjs 2>&1 | tee -a "$LOG" || true

# 5. Ping Google Indexing API
python3 scripts/push-google-indexing.py 2>&1 | tee -a "$LOG" || true

echo "[$(date '+%Y-%m-%d %H:%M:%S')] TeleEstaNoche.es Rebuild & Deploy SUCCESS!" | tee -a "$LOG"
