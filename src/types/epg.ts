export interface Channel {
  id: string;          // slug e.g. "la-1"
  xmltvId: string;     // XMLTV id in guiatv.xml e.g. "La 1 HD"
  name: string;        // "La 1"
  number: number;      // LCN order (1, 2, 3...)
  group: 'general' | 'cine-series' | 'tematico' | 'deportes-noticias' | 'infantil';
  logo: string;        // URL or local asset
  streamUrl: string;   // Official live OTT stream URL
  description: string; // Spanish description of the channel
}

export interface Program {
  id: string;
  channelId: string;
  channelName: string;
  channelLogo: string;
  title: string;
  description: string;
  category: 'movies' | 'series' | 'sports' | 'news' | 'entertainment' | 'kids';
  categoryEs: string;  // "Cine", "Series", "Deportes", "Informativo", "Entretenimiento", "Infantil"
  startTime: string;   // ISO string UTC
  stopTime: string;    // ISO string UTC
  startMadrid: string; // HH:mm (Europe/Madrid)
  stopMadrid: string;  // HH:mm (Europe/Madrid)
  startCanarias: string; // HH:mm (Atlantic/Canary, -1h)
  stopCanarias: string;  // HH:mm (Atlantic/Canary, -1h)
  durationMinutes: number;
  icon?: string;
  rating?: string;
  isTonightPrime?: boolean;
}

export interface EPGCache {
  updatedAt: string;
  channels: Channel[];
  programs: Program[];
}
