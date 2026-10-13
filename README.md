# Blueprint & Guida di Implementazione: teleestanoche.es
> **Progetto:** Guida TV in chiaro ultra-veloce per la Spagna (TDT)  
> **Dominio:** `https://www.teleestanoche.es` (e `https://teleestanoche.es`)  
> **Stack:** Astro (SSG) + Tailwind CSS v4 + Cloudflare Pages + EPG XMLTV Spain

---

## 1. Obiettivo & Visione del Prodotto

Replicare l'architettura tecnica e SEO di successo di `aussietvtonight.com` sul mercato spagnolo, posizionandosi per le ricerche:
- *"Qué echan hoy en la tele"* / *"Qué echan hoy en TV"*
- *"Qué ver esta noche en TV"* / *"Parrilla TV hoy"*
- *"Programación TV hoy"* / *"Guía TV hoy"*
- *"Películas hoy en TV"* / *"Fútbol y deportes hoy en TV"*

A differenza dei portali spagnoli tradizionali (*FormulaTV*, *SincroGuía*, *El País*), il sito deve essere:
- **Ultra-veloce e leggero** (zero banner invasivi, bundle statico edge-cached).
- **Dark mode moderna** ad alto contrasto.
- **Centrato sul Prime Time spagnolo (ore 22:00)** e sul consumo live (*"Ahora en TV"*).

---

## 2. Errori da Evitare (Lezioni Apprese dai Progetti Precedenti)

| Errore commesso in passato | Soluzione obbligatoria per teleestanoche.es |
| :--- | :--- |
| **Copia acritica di repository esistenti** con file zombie (es. `llms.txt` tedesco, script TMDb/Postgres non usati, vecchi report GSC). | **Inizializzazione pulita:** Solo i file necessari. Nessun file ereditato da altri paesi. |
| **Geolocalizzazione incompleta o tardiva** (es. `lang="en"`, metadati non allineati). | **Geolocalizzazione nativa dal giorno 1:** `lang="es-ES"`, meta tag geo España, header `Content-Language: es-ES`, schema.org `spatialCoverage: Spain`. |
| **Orario Prime Time errato** (19:30 o 21:15). | In Spagna il Prime Time reale inizia alle **22:00 / 22:30** (dopo *El Hormiguero* e *La Revuelta*). Il filtro serale predefinito deve puntare alle 22:00. |
| **Mancata gestione del doppio fuso orario spagnolo**. | Spagna peninsulare (CET/CEST) vs Isole Canarie (WET/WEST, *"una hora menos en Canarias"*). Prevedere selettore città/fuso. |
| **Funzioni Cloudflare superflue** (es. vecchi redirect `410 Gone` in `functions/`). | Nessuna directory `functions/` a meno di reale necessità dinamica; gestione 404 nativa tramite `src/pages/404.astro`. |
| **IndexNow e Bing Webmaster aggiunti a posteriori**. | Configurare subito il file chiave UTF-8 di IndexNow alla root e i tag Bing `msvalidate.01`. |

---

## 3. Fonti Dati EPG & Flusso di Ingestione

### A. Fonte Principale XMLTV (100% canali nazionali e tematici)
- **URL EPG:** `https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml.gz`
- **Caratteristiche:** Aggiornato quotidianamente alle ~08:48 (ora di Madrid), compresso in `.gz` (~7.3 MB), contiene i "Big 6" (*La 1, La 2, Antena 3, Cuatro, Telecinco, laSexta*), tutte le tematiche TDT, le reti autonome e i loghi canali dedicati.
- **Repository icone picons:** `https://raw.githubusercontent.com/davidmuma/picons_dobleM/master/icon/[NomeCanale].png`

### B. Fonte Secondaria / Streaming Ufficiale (TDTChannels)
- **URL EPG compresso:** `https://www.tdtchannels.com/epg/TV.xml.gz` (533 KB, Cloudflare CDN).
- **Player Streaming Ufficiali (Link esterni conformi):**
  - RTVE (La 1, La 2, TDP, 24h): `https://www.rtve.es/play/videos/directo/`
  - Atresmedia (Antena 3, laSexta, Neox, Nova, Mega, Atreseries): `https://www.atresplayer.com/directos/`
  - Mediaset España (Telecinco, Cuatro, FDF, Divinity, Energy, Be Mad): `https://www.mitele.es/directo/`

---

## 4. Canali Target della TDT Spagnola (Mappatura)

Lo script di parsing estrarrà esclusivamente questo cluster ad alta domanda (24 canali):

### 1. Generalistas Nacionales ("Los 6 Grandes")
1. `la-1` — **La 1** (RTVE)
2. `la-2` — **La 2** (RTVE)
3. `antena-3` — **Antena 3** (Atresmedia)
4. `cuatro` — **Cuatro** (Mediaset)
5. `telecinco` — **Telecinco** (Mediaset)
6. `lasexta` — **laSexta** (Atresmedia)

### 2. Cine, Series & Entretenimiento
7. `fdf` — **Factoría de Ficción (FDF)**
8. `neox` — **Neox**
9. `nova` — **Nova**
10. `mega` — **Mega**
11. `atreseries` — **Atreseries**
12. `energy` — **Energy**
13. `divinity` — **Divinity**
14. `be-mad` — **Be Mad** (100% Cinema HD)
15. `trece` — **TRECE**
16. `dmax` — **DMAX**
17. `dkiss` — **DKISS**
18. `ten` — **TEN**

### 3. Deportes, Noticias & Infantil
19. `teledeporte` — **Teledeporte (TDP)**
20. `gol-play` — **GOL PLAY**
21. `24h` — **Canal 24 Horas**
22. `real-madrid-tv` — **Real Madrid TV**
23. `clan` — **Clan**
24. `boing` — **Boing**

*(Opzionali regionali FORTA attivabili in una seconda fase: TV3, Telemadrid, Canal Sur, TVG, ETB2).*

---

## 5. Architettura Pagine & Routing SEO

```text
src/pages/
├── index.astro                -> "Esta Noche en TV" (Prime Time ore 22:00)
├── ahora.astro                -> "Ahora en TV" / "En Directo" (con barra di avanzamento e orario corrente)
├── peliculas-hoy.astro        -> Filtro dedicato: Tutti i film di oggi su tutti i canali
├── deportes-hoy.astro         -> Filtro dedicato: Calcio, basket, tennis e sport oggi in TV
├── series-hoy.astro           -> Filtro dedicato: Serie TV e fiction
├── manana.astro               -> Programmazione di domani
├── [canal].astro              -> Pagine dinamiche per singolo canale (es. /la-1/, /antena-3/, /telecinco/)
├── politica-de-privacidad.astro -> Privacy & Cookie Policy GDPR / AEPD
├── aviso-legal.astro          -> Termini legali obbligatori in Spagna (LSSI-CE)
└── 404.astro                  -> Pagina non trovato con link rapidi a stasera / canali
```

### Struttura Metadati HTML & Headers
```html
<html lang="es-ES">
<head>
  <!-- Geolocalizzazione Spagna -->
  <meta name="geo.region" content="ES" />
  <meta name="geo.country" content="España" />
  <meta name="geo.placename" content="España (Madrid, Barcelona, Valencia, Sevilla, Canarias)" />
  <meta name="geo.position" content="40.4168;-3.7038" />
  <meta name="ICBM" content="40.4168, -3.7038" />
  <meta name="coverage" content="España" />
  <meta name="distribution" content="Spain" />
  <meta http-equiv="content-language" content="es-ES" />
  <link rel="alternate" hreflang="es-ES" href="https://www.teleestanoche.es/" />
  <link rel="alternate" hreflang="x-default" href="https://www.teleestanoche.es/" />
```

### Header HTTP Cloudflare (`public/_headers`)
```text
/*
  Content-Language: es-ES
  X-Robots-Tag: all
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
```

---

## 6. Pipeline di Ingestione EPG (`scripts/fetch-epg-spain.py`)

Lo script Python eseguito in `prebuild` deve:
1. Effettuare il download in memoria di `https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml.gz`.
2. Decomprimere lo stream XMLTV.
3. Filtrare esclusivamente la lista dei canali consentiti (`ALLOWED_CHANNELS`).
4. Convertire i timestamp UTC nel fuso locale di Madrid (`Europe/Madrid`), calcolando anche l'offset per le Isole Canarie (-1h).
5. Estrarre solo la finestra utile: da 4 ore prima di adesso fino alle 06:00 di domani (+ giorno successivo per `/manana/`).
6. Salvare il file `src/data/epg-cache.json` ottimizzato e compresso (< 2 MB).

---

## 7. Configurazione Motori di Ricerca & IndexNow

1. **Bing Webmaster Tools / Yandex:**
   - Generare la chiave IndexNow (es. `14ccfafe37144708a4d3c8e34b5e4a08`).
   - Salvare in `public/[chiave].txt`.
   - Inserire il meta tag Bing: `<meta name="msvalidate.01" content="[BING_KEY]" />`.
2. **File per motori AI (`public/llms.txt`):**
   - Redigere il file completamente in spagnolo descrivendo `teleestanoche.es` come la guida TV di riferimento in chiaro per la TDT spagnola.
3. **Sitemap:**
   - Generazione automatica tramite `@astrojs/sitemap`.

---

## 8. Piano di Azione Operativo Passo-Passo

Quando sei pronto a lanciare il codice nella cartella `teleestanoche.es`:

### Passo 1: Inizializzazione Ambiente Pulito
```bash
cd /Users/romolovelati/Desktop/teleestanoche.es
npm init -y
npm install astro @astrojs/sitemap tailwindcss @tailwindcss/vite
```

### Passo 2: Copia e Sanitizzazione dei Componenti da aussietvtonight
Copiare da `aussietvtonight` **solo** i componenti core, applicando la traduzione e l'adattamento:
- `Header.astro` -> Titolo "Tele Esta Noche", bandiera 🇪🇸, menu in spagnolo (*Esta Noche, Ahora, Películas, Deportes, Series, Mañana*).
- `BaseLayout.astro` -> Metadati `es-ES`, coordinate geografiche Spagna, IndexNow.
- `ChannelCard.astro` / `ProgramOverlay.astro` -> Visualizzazione programma con orari di Madrid e Canarie.
- `city-selector` -> Selettore tra:
  - `Península y Baleares (CET / Hora peninsular)`
  - `Islas Canarias (-1h / WET)`

### Passo 3: Script EPG Spagnolo
Creare `scripts/fetch-epg-spain.py` e configurare in `package.json`:
```json
{
  "scripts": {
    "prebuild": "python3 scripts/fetch-epg-spain.py || true",
    "build": "astro build",
    "deploy": "npx wrangler pages deploy dist --project-name=teleestanoche --branch=main"
  }
}
```

### Passo 4: Cloudflare Pages & Dominio
- Creare il progetto Cloudflare Pages `teleestanoche`.
- Collegare il dominio personalizzato `www.teleestanoche.es` e `teleestanoche.es`.
- Inserire il tag GA4 (o attendere ID per la Spagna).
