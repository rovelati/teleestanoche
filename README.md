# Tele Esta Noche (teleestanoche.es) 🇪🇸📺

[![Sitio Web Oficial](https://img.shields.io/badge/Web-teleestanoche.es-red?style=for-the-badge&logo=googlechrome&logoColor=white)](https://www.teleestanoche.es/)
[![Desplegado en Cloudflare Pages](https://img.shields.io/badge/Despliegue-Cloudflare%20Pages-F38020?style=for-the-badge&logo=cloudflare&logoColor=white)](https://www.teleestanoche.es/)
[![Astro](https://img.shields.io/badge/Construido%20con-Astro%20v6-BC52EE?style=for-the-badge&logo=astro&logoColor=white)](https://astro.build/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **[Tele Esta Noche](https://www.teleestanoche.es/)** es la guía de televisión de la TDT en España más rápida, moderna y limpia. Diseñada para responder al instante a la pregunta: *¿Qué echan hoy en la tele?*

Generada estáticamente con **Astro SSG** y servida globalmente desde el Edge de **Cloudflare Pages** con tiempos de carga de 0ms, dark mode nativo de alto contraste y sin anuncios invasivos.

---

## 🌐 Portales Oficiales y Secciones Principales

Accede a la programación completa de la televisión en España en directo y en prime time:

- 🌙 **[Qué ver esta noche en TV (Prime Time 22:00)](https://www.teleestanoche.es/)** — Toda la programación estelar de la noche en los canales en abierto tras *El Hormiguero* y *La Revuelta*.
- 🔴 **[Qué echan ahora en la tele (En Directo)](https://www.teleestanoche.es/ahora/)** — Parrilla en directo con barras de progreso en tiempo real y emisión actual de la TDT.
- 🍿 **[Películas hoy en TV](https://www.teleestanoche.es/peliculas-hoy/)** — Todos los largometrajes, estrenos de cine y clásicos emitidos hoy en la televisión española.
- 🏆 **[Fútbol y Deportes hoy en TV](https://www.teleestanoche.es/deportes-hoy/)** — Retransmisiones deportivas en directo: LaLiga, Champions, baloncesto, tenis y motor en abierto.
- 📺 **[Series hoy en TV](https://www.teleestanoche.es/series-hoy/)** — Guía de series nacionales e internacionales emitidas hoy en la TDT.
- 📅 **[Programación TV Mañana](https://www.teleestanoche.es/manana/)** — Consulta anticipada de la parrilla televisiva del día de mañana.

---

## 📡 Canales de la TDT de España

Páginas dedicadas con la programación completa canal por canal:

| Canales Generalistas Nacionales | Cine, Series y Entretenimiento | Temáticos, Deportes e Infantil |
| :--- | :--- | :--- |
| • [La 1](https://www.teleestanoche.es/la-1/) (RTVE)<br>• [La 2](https://www.teleestanoche.es/la-2/) (RTVE)<br>• [Antena 3](https://www.teleestanoche.es/antena-3/) (Atresmedia)<br>• [Cuatro](https://www.teleestanoche.es/cuatro/) (Mediaset)<br>• [Telecinco](https://www.teleestanoche.es/telecinco/) (Mediaset)<br>• [laSexta](https://www.teleestanoche.es/lasexta/) (Atresmedia) | • [FDF](https://www.teleestanoche.es/fdf/) (Factoría de Ficción)<br>• [Neox](https://www.teleestanoche.es/neox/)<br>• [Nova](https://www.teleestanoche.es/nova/)<br>• [Mega](https://www.teleestanoche.es/mega/)<br>• [Atreseries](https://www.teleestanoche.es/atreseries/)<br>• [Energy](https://www.teleestanoche.es/energy/)<br>• [Divinity](https://www.teleestanoche.es/divinity/)<br>• [Be Mad](https://www.teleestanoche.es/be-mad/)<br>• [TRECE](https://www.teleestanoche.es/trece/)<br>• [DMAX](https://www.teleestanoche.es/dmax/)<br>• [DKISS](https://www.teleestanoche.es/dkiss/)<br>• [TEN](https://www.teleestanoche.es/ten/) | • [Teledeporte](https://www.teleestanoche.es/teledeporte/) (TDP)<br>• [GOL PLAY](https://www.teleestanoche.es/gol-play/)<br>• [Canal 24 Horas](https://www.teleestanoche.es/24h/)<br>• [Real Madrid TV](https://www.teleestanoche.es/real-madrid-tv/)<br>• [Clan](https://www.teleestanoche.es/clan/)<br>• [Boing](https://www.teleestanoche.es/boing/) |

---

## ⚡ Características Principales

- **Prime Time Español Real (22:00)**: Adaptado a las costumbres horarias de España, donde el verdadero prime time comienza a las 22:00 / 22:30.
- **Doble Fuso Horario Península / Canarias**: Selector instantáneo para hora peninsular (CET/CEST) o Islas Canarias (WET/WEST, *"una hora menos en Canarias"*).
- **Indexación Inmediata con IndexNow & Google Indexing API**:
  - Pings automáticos a Bing, Yandex y buscadores compatibles mediante clave IndexNow verificada (`4f25c5dc3491468f8459b92c21bb3ac1`).
  - Notificaciones en tiempo real `URL_UPDATED` a la API de Indexación de Google para posicionamiento prioritario en resultados móviles y Discover.
- **Datos Estructurados Schema.org**: Marcado enriquecido `TVGuide`, `ItemList`, `BroadcastService` y `WebPage` para obtención de Rich Snippets en Google.
- **Optimización Web Vitals**: Puntuación 100/100 en Core Web Vitals, HTML semántico y cero JavaScript innecesario.

---

## 🚀 Comandos de Automatización

```bash
# Ingesta diaria de EPG y construcción estática
npm run prebuild   # Descarga y parsea la EPG XMLTV de España
npm run build      # Genera el sitio estático en dist/

# Envío automático a motores de búsqueda
npm run ping:indexnow  # Notifica las 30 URLs canónicas a IndexNow (Bing/Yandex)
npm run ping:google    # Envía URL_UPDATED a Google Indexing API
npm run ping           # Ejecuta ambos pings secuencialmente

# Pipeline completo (EPG + Build + Test + Deploy + IndexNow + Google)
./scripts/rebuild-and-deploy.sh
```

---

## 📄 Licencia

Proyecto de código abierto publicado bajo licencia [MIT](LICENSE).
Sitio web oficial: **[https://www.teleestanoche.es/](https://www.teleestanoche.es/)**
