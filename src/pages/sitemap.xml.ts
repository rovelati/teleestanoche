import type { APIRoute } from 'astro';
import { getAllChannels } from '../utils/epg';

export const GET: APIRoute = async () => {
  const channels = getAllChannels();
  const today = new Date().toISOString().split('T')[0];

  const staticRoutes = [
    { url: 'https://www.teleestanoche.es/', changefreq: 'hourly', priority: '1.0' },
    { url: 'https://www.teleestanoche.es/ahora/', changefreq: 'always', priority: '0.9' },
    { url: 'https://www.teleestanoche.es/peliculas-hoy/', changefreq: 'hourly', priority: '0.8' },
    { url: 'https://www.teleestanoche.es/series-hoy/', changefreq: 'hourly', priority: '0.8' },
    { url: 'https://www.teleestanoche.es/deportes-hoy/', changefreq: 'hourly', priority: '0.8' },
    { url: 'https://www.teleestanoche.es/manana/', changefreq: 'daily', priority: '0.8' },
    { url: 'https://www.teleestanoche.es/aviso-legal/', changefreq: 'monthly', priority: '0.3' },
    { url: 'https://www.teleestanoche.es/politica-de-privacidad/', changefreq: 'monthly', priority: '0.3' },
  ];

  const channelRoutes = channels.map(c => ({
    url: `https://www.teleestanoche.es/${c.id}/`,
    changefreq: 'hourly',
    priority: '0.7'
  }));

  const allUrls = [...staticRoutes, ...channelRoutes];

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allUrls.map(u => `  <url>
    <loc>${u.url}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>
  </url>`).join('\n')}
</urlset>`;

  return new Response(xml.trim(), {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8'
    }
  });
};
