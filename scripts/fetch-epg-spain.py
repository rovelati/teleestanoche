#!/usr/bin/env python3
"""
fetch-epg-spain.py
Downloads Spanish EPG XMLTV (EPG_dobleM with TDTChannels fallback),
filters target channels for teleestanoche.es, converts timezones,
categorizes genres, and writes src/data/epg-cache.json.
"""

import gzip
import io
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

PRIMARY_EPG_URL = "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml.gz"
FALLBACK_EPG_URL = "https://www.tdtchannels.com/epg/TV.xml.gz"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
CHANNELS_FILE = os.path.join(PROJECT_DIR, "src", "data", "channels.json")
OUTPUT_FILE = os.path.join(PROJECT_DIR, "src", "data", "epg-cache.json")

MADRID_TZ = ZoneInfo("Europe/Madrid")
CANARIAS_TZ = ZoneInfo("Atlantic/Canary")

def load_channels():
    if not os.path.exists(CHANNELS_FILE):
        print(f"Error: {CHANNELS_FILE} not found.")
        sys.exit(1)
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def download_xmltv():
    urls = [PRIMARY_EPG_URL, FALLBACK_EPG_URL]
    data = None
    for url in urls:
        try:
            print(f"[fetch-epg-spain] Downloading XMLTV from {url}...")
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "TeleEstaNoche-Bot/1.0 (+https://www.teleestanoche.es)"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                # Decompress if gzipped
                if url.endswith(".gz") or raw[:2] == b'\x1f\x8b':
                    data = gzip.decompress(raw)
                else:
                    data = raw
                print(f"[fetch-epg-spain] Downloaded and decompressed {len(data)} bytes")
                return data
        except Exception as e:
            print(f"[fetch-epg-spain] Failed downloading {url}: {e}")
            continue
    raise RuntimeError("Could not download any Spanish XMLTV feed.")

def parse_xmltv_date(date_str):
    # Formats: "20261013075000 +0200" or "20261013075000"
    clean = date_str.strip()
    match = re.match(r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(?:\s*([+-]\d{4}))?", clean)
    if not match:
        return None
    y, m, d, H, M, S, tz_str = match.groups()
    base_dt = datetime(int(y), int(m), int(d), int(H), int(M), int(S))
    
    if tz_str:
        sign = -1 if tz_str[0] == '-' else 1
        tz_hours = int(tz_str[1:3])
        tz_mins = int(tz_str[3:5])
        offset = timezone(sign * timedelta(hours=tz_hours, minutes=tz_mins))
        return base_dt.replace(tzinfo=offset)
    else:
        # Default UTC
        return base_dt.replace(tzinfo=timezone.utc)

def categorize(title, desc, cat_raw, channel_id):
    combined = f"{title} {desc} {cat_raw}".lower()

    if any(k in combined for k in ["película", "pelicula", "cine", "film", "largometraje"]) or channel_id == "be-mad":
        return ("movies", "Cine")

    if any(k in combined for k in ["fútbol", "futbol", "baloncesto", "tenis", "ciclismo", "deporte", "sports", "liga", "champions", "copa"]) or channel_id in ["teledeporte", "gol-play", "real-madrid-tv"]:
        return ("sports", "Deportes")

    if any(k in combined for k in ["serie", "telenovela", "temporada", "capítulo", "capitulo", "episodio"]) or channel_id in ["atreseries", "fdf", "energy", "nova"]:
        return ("series", "Series")

    if any(k in combined for k in ["telediario", "noticias", "informativo", "el tiempo", "actualidad", "al rojo vivo", "debate"]) or channel_id == "24h":
        return ("news", "Informativo")

    if any(k in combined for k in ["dibujos", "animación", "animacion", "infantil", "peppa pig", "bob esponja", "pocoyó"]) or channel_id in ["clan", "boing"]:
        return ("kids", "Infantil")

    return ("entertainment", "Entretenimiento")

def main():
    channels = load_channels()
    xmltv_to_channel = {}
    for ch in channels:
        xmltv_to_channel[ch["xmltvId"].lower()] = ch
        xmltv_to_channel[ch["name"].lower()] = ch
        xmltv_to_channel[ch["id"].lower()] = ch

    xml_bytes = download_xmltv()
    print("[fetch-epg-spain] Parsing XML...")
    
    now_utc = datetime.now(timezone.utc)
    # Window: from 6 hours ago to 36 hours ahead
    min_time = now_utc - timedelta(hours=6)
    max_time = now_utc + timedelta(hours=36)
    
    programs = []
    
    # Fast iterparse to keep memory light
    context = ET.iterparse(io.BytesIO(xml_bytes), events=("end",))
    
    count = 0
    for event, elem in context:
        if elem.tag == "programme":
            ch_attr = elem.get("channel", "")
            ch_lower = ch_attr.lower()
            
            target_ch = xmltv_to_channel.get(ch_lower)
            if target_ch:
                start_raw = elem.get("start", "")
                stop_raw = elem.get("stop", "")
                
                dt_start = parse_xmltv_date(start_raw)
                dt_stop = parse_xmltv_date(stop_raw) if stop_raw else (dt_start + timedelta(hours=1) if dt_start else None)
                
                if dt_start and dt_stop and dt_stop > min_time and dt_start < max_time:
                    title_elem = elem.find("title")
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Sin título"
                    
                    desc_elem = elem.find("desc")
                    desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                    
                    cat_elem = elem.find("category")
                    cat_raw = cat_elem.text.strip() if cat_elem is not None and cat_elem.text else ""
                    
                    icon_elem = elem.find("icon")
                    icon_url = icon_elem.get("src", "") if icon_elem is not None else ""
                    
                    # Convert time to Madrid and Canarias
                    dt_madrid_start = dt_start.astimezone(MADRID_TZ)
                    dt_madrid_stop = dt_stop.astimezone(MADRID_TZ)
                    dt_canarias_start = dt_start.astimezone(CANARIAS_TZ)
                    dt_canarias_stop = dt_stop.astimezone(CANARIAS_TZ)
                    
                    start_madrid = dt_madrid_start.strftime("%H:%M")
                    stop_madrid = dt_madrid_stop.strftime("%H:%M")
                    start_canarias = dt_canarias_start.strftime("%H:%M")
                    stop_canarias = dt_canarias_stop.strftime("%H:%M")
                    
                    duration = max(1, int((dt_stop - dt_start).total_seconds() / 60))
                    cat_slug, cat_es = categorize(title, desc, cat_raw, target_ch["id"])
                    
                    # Prime time in Spain: starts between 21:15 and 23:15, or is active at 22:15
                    madrid_hour = dt_madrid_start.hour + dt_madrid_start.minute / 60.0
                    madrid_stop_hour = dt_madrid_stop.hour + dt_madrid_stop.minute / 60.0
                    
                    # If stops next day morning
                    if dt_madrid_stop.date() > dt_madrid_start.date():
                        madrid_stop_hour += 24.0
                    
                    is_tonight_prime = (21.25 <= madrid_hour <= 23.25) or (madrid_hour <= 22.0 and madrid_stop_hour >= 22.5)
                    
                    prog_id = f"{target_ch['id']}-{int(dt_start.timestamp())}"
                    
                    programs.append({
                        "id": prog_id,
                        "channelId": target_ch["id"],
                        "channelName": target_ch["name"],
                        "channelLogo": target_ch["logo"],
                        "title": title,
                        "description": desc,
                        "category": cat_slug,
                        "categoryEs": cat_es,
                        "startTime": dt_start.isoformat(),
                        "stopTime": dt_stop.isoformat(),
                        "startMadrid": start_madrid,
                        "stopMadrid": stop_madrid,
                        "startCanarias": start_canarias,
                        "stopCanarias": stop_canarias,
                        "durationMinutes": duration,
                        "icon": icon_url or target_ch["logo"],
                        "isTonightPrime": is_tonight_prime
                    })
                    count += 1
                    
            elem.clear()

    # Sort programs by channel order, then start time
    ch_order = {ch["id"]: i for i, ch in enumerate(channels)}
    programs.sort(key=lambda p: (ch_order.get(p["channelId"], 99), p["startTime"]))
    
    print(f"[fetch-epg-spain] Extracted {len(programs)} programs across {len(channels)} target channels")
    
    cache_data = {
        "updatedAt": now_utc.isoformat(),
        "channels": channels,
        "programs": programs
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
    print(f"[fetch-epg-spain] Saved cache to {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE) // 1024} KB)")

if __name__ == "__main__":
    main()
