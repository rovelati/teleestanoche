#!/usr/bin/env python3
"""
TeleEstaNoche.es — Google Indexing API Automation
Submits canonical Spanish TDT channels and prime-time hub URLs to Google Indexing API (URL_UPDATED).
Requires Service Account email to be added as Owner in Google Search Console for https://www.teleestanoche.es/.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = "https://www.teleestanoche.es"
CHANNELS = [
    "la-1", "la-2", "antena-3", "cuatro", "telecinco", "lasexta",
    "fdf", "neox", "nova", "mega", "atreseries", "energy",
    "divinity", "be-mad", "trece", "dmax", "dkiss", "ten",
    "teledeporte", "gol-play", "24h", "real-madrid-tv", "clan", "boing"
]
ROOTS = ["/", "/ahora", "/peliculas-hoy", "/series-hoy", "/deportes-hoy", "/manana"]

ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

CANDIDATES = [
    os.getenv("GOOGLE_INDEXING_SERVICE_ACCOUNT_FILE"),
    Path("/var/www/programmecesoir.fr/programmecesoir-c491fade6de8.json"),
    Path("/Users/romolovelati/Desktop/programmecesoir.fr/programmecesoir-c491fade6de8.json"),
    Path("/var/www/codebase/SPIDER/google-service-account.json"),
    Path(__file__).resolve().parent.parent / "google-service-account.json",
    Path(__file__).resolve().parent / "google-service-account.json",
]

def get_service_account_path() -> Path | None:
    for c in CANDIDATES:
        if c:
            p = Path(c)
            if p.exists():
                return p
    return None

def get_priority_urls() -> list[str]:
    urls = [f"{ROOT}{p}/" if p != "/" else f"{ROOT}/" for p in ROOTS]
    for ch in CHANNELS:
        urls.append(f"{ROOT}/{ch}/")
    return urls

def main() -> int:
    parser = argparse.ArgumentParser(description="Submit URLs to Google Indexing API (TeleEstaNoche)")
    parser.add_argument("--sa", default=None, help="Path to Google Service Account JSON")
    parser.add_argument("--url", default=None, help="Submit only this specific URL (test)")
    args = parser.parse_args()

    sa_path = Path(args.sa) if args.sa else get_service_account_path()
    if not sa_path or not sa_path.exists():
        print(f"[Google Indexing] ERROR: Service Account JSON not found in candidate paths!", file=sys.stderr)
        return 1

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        print("[Google Indexing] Installing google-auth library...", file=sys.stderr)
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "google-auth", "requests"], check=True)
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession

    creds = service_account.Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
    session = AuthorizedSession(creds)

    import json
    with open(sa_path, "r", encoding="utf-8") as f:
        sa_data = json.load(f)
    client_email = sa_data.get("client_email", "unknown")

    urls_to_submit = [args.url] if args.url else get_priority_urls()

    print(f"=== Google Indexing API — {ROOT} ===")
    print(f"Service Account: {client_email}")
    print(f"URLs to notify : {len(urls_to_submit)}")
    print(f"Endpoint       : {ENDPOINT}")
    print("-" * 50)

    ok_count = 0
    fail_count = 0

    for idx, u in enumerate(urls_to_submit, 1):
        payload = {"url": u, "type": "URL_UPDATED"}
        try:
            resp = session.post(ENDPOINT, json=payload, timeout=15)
            if resp.status_code == 200:
                ok_count += 1
                print(f"[{idx}/{len(urls_to_submit)}] OK 200 -> {u}")
            else:
                fail_count += 1
                print(f"[{idx}/{len(urls_to_submit)}] FAIL {resp.status_code} -> {u}")
                data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                err_msg = data.get("error", {}).get("message", resp.text[:200])
                print(f"    Reason: {err_msg}")
                if "Failed to verify the URL ownership" in err_msg:
                    print(f"\n⚠️  CRITICAL: Add '{client_email}' as Owner in Google Search Console for {ROOT}/ to enable Google Indexing API!\n")
                    break
        except Exception as e:
            fail_count += 1
            print(f"[{idx}/{len(urls_to_submit)}] ERROR -> {u}: {e}")

        time.sleep(0.3)

    print("-" * 50)
    print(f"Google Indexing Complete: {ok_count} OK, {fail_count} Failed out of {len(urls_to_submit)} URLs.")
    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
