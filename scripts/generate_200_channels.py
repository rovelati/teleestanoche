#!/usr/bin/env python3
"""
generate_200_channels.py
Curates and generates src/data/channels.json with exactly 200 top Spanish television channels.
"""

import json
import re
import urllib.parse

with open('/tmp/doblem_channels.json') as f:
    doble = json.load(f)
ch_map = doble['channels']
counts = doble['counts']

with open('src/data/channels.json') as f:
    current = json.load(f)

# The base 24 national DTT channels stay 1..24
channels_200 = []
used_slugs = set()
used_xmltv = set()

for c in current:
    channels_200.append(c)
    used_slugs.add(c['id'])
    used_xmltv.add(c['xmltvId'])

# Additional channels definitions (xmltvId, clean_name, group, stream_url, description)
additional_specs = [
    # --- CINE & SERIES (36 channels) ---
    ("Movistar Plus HD", "Movistar Plus+", "cine-series", "https://ver.movistarplus.es/", "Canal insignia de Movistar Plus+ con grandes estrenos de cine, series originales exclusivas y documentales."),
    ("M+ Estrenos HD", "M+ Estrenos", "cine-series", "https://ver.movistarplus.es/", "Los estrenos cinematográficos más recientes de la cartelera y taquilla mundial sin interrupciones."),
    ("M+ Hits HD", "M+ Hits", "cine-series", "https://ver.movistarplus.es/", "Grandes éxitos taquilleros del cine reciente y películas aclamadas por el público."),
    ("M+ Originales HD", "M+ Originales", "cine-series", "https://ver.movistarplus.es/", "Producción propia de ficción, series y documentales originales galardonados."),
    ("M+ Clásicos HD", "M+ Clásicos", "cine-series", "https://ver.movistarplus.es/", "Obras maestras de la historia del cine, directores legendarios y joyas en blanco y negro y color."),
    ("M+ Acción HD", "M+ Acción", "cine-series", "https://ver.movistarplus.es/", "Adrenalina pura: cine de acción, thrillers policiacos, artes marciales y persecuciones."),
    ("M+ Comedia HD", "M+ Comedia", "cine-series", "https://ver.movistarplus.es/", "Las mejores comedias españolas e internacionales, humor inteligente y grandes clásicos cómicos."),
    ("M+ Drama HD", "M+ Drama", "cine-series", "https://ver.movistarplus.es/", "Películas dramáticas conmovedoras, historias humanas intensas y cine de autor."),
    ("M+ Indie HD", "M+ Indie", "cine-series", "https://ver.movistarplus.es/", "Cine independiente, festivales internacionales de Cannes, Sundance, Berlín y Venecia."),
    ("M+ Cine Español", "M+ Cine Español", "cine-series", "https://ver.movistarplus.es/", "Homenaje integral al séptimo arte en España, desde los premios Goya hasta el cine clásico español."),
    ("TCM HD", "TCM", "cine-series", "https://www.canaltcm.com/", "Turner Classic Movies: el canal de los cinéfilos con las mejores películas de todos los tiempos en alta definición."),
    ("Canal Hollywood HD", "Canal Hollywood", "cine-series", "https://canalhollywood.es/", "El canal líder de cine con los mayores éxitos de las grandes productoras de Hollywood."),
    ("AMC HD", "AMC", "cine-series", "https://amcselekt.es/canales/amc/", "Cine contemporáneo galardonado y series exclusivas de aclamada crítica internacional."),
    ("Warner TV HD", "Warner TV", "cine-series", "https://warnertv.es/", "Series icónicas de Warner Bros, estrenos de ficción y superproducciones cinematográficas."),
    ("STAR Channel HD", "STAR Channel", "cine-series", "https://starchannel.es/", "El hogar de las grandes series de entretenimiento, acción y los mejores thrillers."),
    ("AXN HD", "AXN", "cine-series", "https://axn.es/", "Series policíacas de investigación, adrenalina, rescates y cine de máxima tensión."),
    ("AXN Movies HD", "AXN Movies", "cine-series", "https://axnmovies.es/", "Canal 100% dedicado al cine de acción, aventuras, thriller y ciencia ficción."),
    ("Calle 13 HD", "Calle 13", "cine-series", "https://calle13.es/", "El canal del crimen, la intriga, la investigación forense y los procedimentales policíacos."),
    ("Cosmo HD", "Cosmo", "cine-series", "https://cosmopolitantv.es/", "Series de éxito internacional, dramas británicos, comedia y lifestyle contemporáneo."),
    ("SciFi HD", "Sci-Fi", "cine-series", "https://ver.movistarplus.es/", "Ciencia ficción, mundos distópicos, fantasía épica y fenómenos sobrenaturales."),
    ("Comedy Central HD", "Comedy Central", "cine-series", "https://comedycentral.es/", "El templo del humor: stand-up comedy, monólogos, sitcoms míticas y parodias."),
    ("DARK", "DARK", "cine-series", "https://amcselekt.es/canales/dark/", "El único canal en España dedicado 100% al cine de terror, slasher, suspense y gore."),
    ("XTRM", "XTRM", "cine-series", "https://amcselekt.es/canales/xtrm/", "Acción sin límites, artes marciales extremas, westerns modernos y suspense criminal."),
    ("Sundance TV", "Sundance TV", "cine-series", "https://sundancetv.es/", "Historias únicas, cine independiente comprometido y series de autor de todo el mundo."),
    ("Somos", "Somos", "cine-series", "https://amcselekt.es/canales/somos/", "Canal dedicado íntegramente al cine español de todas las épocas."),
    ("Canal FlixOlé 1", "FlixOlé 1", "cine-series", "https://flixole.com/", "La mayor plataforma y canal lineal de cine español restaurado y clásicos en HD."),
    ("Canal FlixOlé 2", "FlixOlé 2", "cine-series", "https://flixole.com/", "Segundo canal de FlixOlé con joyas del cine europeo, spaghetti westerns y comedia."),
    ("BOM Cine", "BOM Cine", "cine-series", "https://bomcine.com/", "Canal de cine en abierto con ciclos temáticos, cine de aventuras y thrillers."),
    ("8madrid TV", "8madrid", "cine-series", "https://8madrid.tv/", "Canal de referencia de cine de calidad en la Comunidad de Madrid."),
    ("Cines Verdi TV", "Cines Verdi TV", "cine-series", "https://cinesverditv.com/", "La programación cinematográfica de las prestigiosas salas Verdi en televisión."),
    ("Cine Feel Good", "Cine Feel Good", "cine-series", "https://cinefeelgood.com/", "Películas inspiradoras, comedias familiares y cine emotivo."),
    ("BBC Series", "BBC Series", "cine-series", "https://bbc.com/", "Las aclamadas series de drama, misterio y época de la BBC británica."),
    ("SkyShowtime", "SkyShowtime 1", "cine-series", "https://skyshowtime.com/", "Canal lineal de SkyShowtime con grandes producciones de Universal, Paramount y Showtime."),
    ("HBO Max Avances", "Max Avances", "cine-series", "https://max.com/", "Canal de avances y novedades de las mejores series de HBO y Warner."),
    ("Veo7", "Veo TV", "cine-series", "https://veotv.es/", "Canal de entretenimiento, series y espacios divulgativos en abierto."),
    ("Squirrel TV", "Squirrel TV", "cine-series", "https://squirrelmedia.es/", "Canal temático de cine y entretenimiento para toda la familia."),

    # --- DEPORTES (35 channels) ---
    ("Eurosport 1 HD", "Eurosport 1", "deportes", "https://eurosport.es/", "La casa del deporte europeo: Roland Garros, Juegos Olímpicos, ciclismo y deportes de invierno."),
    ("Eurosport 2", "Eurosport 2", "deportes", "https://eurosport.es/", "Segundo canal de Eurosport con transmisiones polideportivas exclusivas en directo."),
    ("DAZN 1 HD", "DAZN 1", "deportes", "https://dazn.com/es-ES", "Retransmisiones estelares de DAZN: Premier League, MotoGP, boxeo y fútbol femenino."),
    ("DAZN 2 HD", "DAZN 2", "deportes", "https://dazn.com/es-ES", "Eventos en directo complementarios de competiciones polideportivas internacionales."),
    ("DAZN 3 HD", "DAZN 3", "deportes", "https://dazn.com/es-ES", "Fútbol internacional, baloncesto y copas europeas en directo."),
    ("DAZN 4 HD", "DAZN 4", "deportes", "https://dazn.com/es-ES", "Transmisiones simultáneas de grandes jornadas deportivas de DAZN."),
    ("DAZN F1 HD", "DAZN F1", "deportes", "https://dazn.com/es-ES", "El canal oficial de la Fórmula 1 en España: entrenamientos, clasificación y carreras en directo."),
    ("DAZN MotoGP", "DAZN MotoGP", "deportes", "https://dazn.com/es-ES", "Toda la emoción del Mundial de Motociclismo: Moto3, Moto2 y MotoGP."),
    ("DAZN LaLiga HD", "DAZN LaLiga", "deportes", "https://dazn.com/es-ES", "Cinco partidos por jornada de LaLiga EA Sports en directo con previa y análisis."),
    ("DAZN Baloncesto", "DAZN Baloncesto", "deportes", "https://dazn.com/es-ES", "Euroliga, EuroCup y las mejores competiciones continentales de baloncesto."),
    ("M+ Vamos HD", "M+ Vamos", "deportes", "https://ver.movistarplus.es/", "Canal polideportivo de Movistar Plus+ con análisis de actualidad, reportajes y directos."),
    ("M+ LaLiga HD", "M+ LaLiga", "deportes", "https://ver.movistarplus.es/", "Emisión oficial de LaLiga EA Sports con los mejores partidos y El Clásico."),
    ("M+ Liga de Campeones HD", "M+ Champions", "deportes", "https://ver.movistarplus.es/", "Toda la UEFA Champions League, Europa League y Conference League en directo."),
    ("M+ Deportes HD", "M+ Deportes", "deportes", "https://ver.movistarplus.es/", "NBA, rugby Six Nations, atletismo Diamond League y grandes citas mundiales."),
    ("M+ Deportes 2 HD", "M+ Deportes 2", "deportes", "https://ver.movistarplus.es/", "Eventos polideportivos en directo y retransmisiones multicanal de Movistar."),
    ("M+ Baloncesto", "M+ Baloncesto", "deportes", "https://ver.movistarplus.es/", "Liga Endesa ACB, Copa del Rey y baloncesto internacional."),
    ("M+ Golf HD", "M+ Golf", "deportes", "https://ver.movistarplus.es/", "Masters de Augusta, PGA Tour, Ryder Cup y circuito europeo de golf."),
    ("LaLiga TV Hypermotion HD", "LaLiga Hypermotion", "deportes", "https://laliga.com/", "Todos los partidos de la Segunda División del fútbol español en directo."),
    ("Tennis Channel", "Tennis Channel", "deportes", "https://tennischannel.com/", "El canal dedicado íntegramente al circuito ATP y WTA de tenis profesional."),
    ("Surf Channel", "Surf Channel", "deportes", "https://surfchannel.tv/", "Canal temático dedicado al mundo del surf, olas gigantes y deportes de playa."),
    ("Nautical Channel", "Nautical Channel", "deportes", "https://nauticalchannel.com/", "Navegación a vela, regatas internacionales, kitesurf y vida marina."),
    ("Motorvision", "Motorvision", "deportes", "https://motorvision.tv/", "Pruebas de superdeportivos, carreras automovilísticas, tuning y rallies."),
    ("Fast&FunBox", "Fast & FunBox", "deportes", "https://spain.spiintl.com/", "Deportes de riesgo y acción extrema: motocross, skate, snowboard y BMX."),
    ("FightSports", "Fight Sports", "deportes", "https://fightsports.tv/", "Deportes de combate: boxeo de campeonato, MMA, kickboxing y judo."),
    ("Caza y Pesca HD", "Caza y Pesca", "deportes", "https://ver.movistarplus.es/", "Espacios dedicados al respeto por el medio ambiente, la caza deportiva y la pesca fluvial y marítima."),
    ("Iberalia TV", "Iberalia TV", "deportes", "https://iberalia.tv/", "Canal de naturaleza, caza, pesca y gestión cinegética en la Península Ibérica."),
    ("Cazavisión", "Cazavisión", "deportes", "https://cazavision.com/", "Canal internacional especializado en documentales de caza y naturaleza salvaje."),
    ("Betis TV", "Betis TV", "deportes", "https://realbetisbalompie.es/rbb-tv/", "Canal oficial del Real Betis Balompié con partidos, cantera y tertulias verdiblancas."),
    ("LaLiga TV BAR", "LaLiga TV Bar", "deportes", "https://laligabar.es/", "Canal para establecimientos públicos con la emisión completa del fútbol profesional."),
    ("Primera Federación", "Primera Federación", "deportes", "https://rfef.es/", "Emisión de los partidos de la Primera Federación RFEF del fútbol español."),
    ("M+ Vamos 2", "M+ Vamos 2", "deportes", "https://ver.movistarplus.es/", "Señal complementaria para citas polideportivas simultáneas."),
    ("M+ Vamos 3", "M+ Vamos 3", "deportes", "https://ver.movistarplus.es/", "Tercera señal de apoyo deportivo de Movistar Plus+."),
    ("DAZN 1 BAR", "DAZN Bar 1", "deportes", "https://dazn.com/", "Canal hostelero con competiciones de fútbol inglés y motor de DAZN."),
    ("DAZN 2 BAR", "DAZN Bar 2", "deportes", "https://dazn.com/", "Segunda señal para establecimientos con eventos simultáneos de DAZN."),
    ("Replay", "Replay Deportes", "deportes", "https://ver.movistarplus.es/", "Resúmenes completos y repeticiones de los mejores momentos deportivos."),

    # --- AUTONÓMICAS & REGIONALES (40 channels) ---
    ("TV3", "TV3 Catalunya", "autonomica", "https://www.ccma.cat/3cat/directes/tv3/", "Televisió de Catalunya: canal generalista líder en Cataluña con informativos, series y entretenimiento en catalán."),
    ("3CatInfo", "3CatInfo", "autonomica", "https://www.ccma.cat/3cat/directes/3catinfo/", "Canal de noticias e información continua 24 horas de la CCMA en Cataluña."),
    ("SX3", "SX3", "autonomica", "https://www.ccma.cat/3cat/directes/sx3/", "El canal infantil y juvenil referente de Cataluña con animación y programas divulgativos."),
    ("Esport 3", "Esport 3", "autonomica", "https://www.ccma.cat/3cat/directes/esport3/", "Canal temático deportivo de Cataluña con cobertura de fútbol, baloncesto y polideportivo."),
    ("Betevé", "Betevé", "autonomica", "https://beteve.cat/en-directe/", "Canal público de la ciudad de Barcelona con información de proximidad y cultura local."),
    ("Telemadrid", "Telemadrid", "autonomica", "https://www.telemadrid.es/emision-en-directo/", "Canal autonómico público de la Comunidad de Madrid: Telenoticias, debate y tradiciones madrileñas."),
    ("La Otra", "La Otra", "autonomica", "https://www.telemadrid.es/emision-en-directo-laotra/", "Segundo canal de Telemadrid enfocado a la cultura, el deporte madrileño y las series."),
    ("Telemadrid Internacional", "Telemadrid Int", "autonomica", "https://www.telemadrid.es/emision-en-directo/", "Señal exterior de Telemadrid para el seguimiento de la actualidad madrileña en el mundo."),
    ("Canal Sur HD", "Canal Sur", "autonomica", "https://www.canalsur.es/en-directo-canal-sur-tv-4228.html", "Radio y Televisión de Andalucía (RTVA): actualidad andaluza, folclore, cultura y cercanía."),
    ("Andalucía TV", "Andalucía TV", "autonomica", "https://www.canalsur.es/en-directo-andalucia-tv-4230.html", "Segundo canal de la RTVA con espacios temáticos, culturales y divulgativos."),
    ("Canal Sur Andalucía", "Canal Sur SAT", "autonomica", "https://www.canalsur.es/en-directo-canal-sur-andalucia-4229.html", "Señal internacional de Andalucía para comunidades andaluzas en el exterior."),
    ("etb1", "ETB1", "autonomica", "https://www.eitb.eus/es/television/etb1/", "Canal autonómico generalista de Euskal Telebista íntegramente en euskera."),
    ("etb2", "ETB2", "autonomica", "https://www.eitb.eus/es/television/etb2/", "Segundo canal de Euskal Telebista en castellano con informativos de referencia y entretenimiento."),
    ("TVG", "TVG Galicia", "autonomica", "https://www.crtvg.es/en-directo", "Televisión de Galicia: la voz de la comunidad gallega con series, informativos y tradiciones en gallego."),
    ("TVG2", "TVG2", "autonomica", "https://www.crtvg.es/en-directo/canle/tvg2", "Segundo canal de la CRTVG enfocado a la cultura, los espacios infantiles y el deporte gallego."),
    ("TVG Europa HD", "TVG Europa", "autonomica", "https://www.crtvg.es/en-directo", "Emisión satélite de la TVG dirigida a los gallegos en España y Europa."),
    ("À Punt", "À Punt", "autonomica", "https://www.apuntmedia.es/directe/", "Televisión pública de la Comunitat Valenciana con informativos, cultura y series en valenciano."),
    ("Aragón TV", "Aragón TV", "autonomica", "https://www.aragontelevision.es/directo", "Canal autonómico de Aragón con cobertura de las tres provincias y programas de éxito rural."),
    ("Aragón TV Internacional", "Aragón TV Int", "autonomica", "https://www.aragontelevision.es/directo", "Emisión para el exterior de la televisión pública aragonesa."),
    ("CMM TV", "CMM TV", "autonomica", "https://www.cmmedia.es/en-directo/tv", "Castilla-La Mancha Media: información cercana de las comarcas manchegas, folclore y festejos."),
    ("Canal Extremadura", "Canal Extremadura", "autonomica", "https://www.canalextremadura.es/directo/tv", "La televisión pública extremeña con magacines comarcales, naturaleza y actualidad de la región."),
    ("Canal Extremadura SAT", "Extremadura SAT", "autonomica", "https://www.canalextremadura.es/directo/tv", "Señal exterior de Canal Extremadura para el seguimiento de la actualidad autonómica."),
    ("TPA7 Asturias", "TPA7", "autonomica", "https://www.rtpa.es/tpa-television", "Televisión del Principado de Asturias con noticias, deportes autóctonos y cultura asturiana."),
    ("TPA8 Asturias", "TPA8", "autonomica", "https://www.rtpa.es/tpa-television", "Segunda señal de la RTPA con contenidos complementarios y cultura del Principado."),
    ("IB3 TV Illes Balears", "IB3 TV", "autonomica", "https://ib3.org/directe", "Canal autonómico público de las Islas Baleares (Mallorca, Menorca, Ibiza y Formentera)."),
    ("TV Canaria", "TV Canaria", "autonomica", "https://rtvc.es/en-directo/", "Radio Televisión Canaria: información de las ocho islas del archipiélago y tradiciones canarias."),
    ("La 7 CyL", "La 7 CyL", "autonomica", "https://www.cyltv.es/EnDirecto", "Televisión autonómica privada de Castilla y León con informativos autonómicos y provinciales."),
    ("La 7 Murcia", "La 7 Murcia", "autonomica", "https://www.la7tv.es/directo/", "Televisión autonómica pública de la Región de Murcia con informativos y actualidad local."),
    ("Navarra TV", "Navarra TV", "autonomica", "https://www.natv.es/directo", "Canal de referencia de la actualidad sociopolítica y cultural de la Comunidad Foral de Navarra."),
    ("Navarra TV 2", "Navarra TV 2", "autonomica", "https://www.natv.es/directo", "Segunda señal de Navarra TV con espacios divulgativos y deporte navarro."),
    ("Atlántico TV", "Atlántico TV", "autonomica", "https://atlanticotv.es/", "Canal local canario con actualidad comarcal de las Islas Canarias."),
    ("La Ocho Mediterráneo", "La Ocho Mediterráneo", "autonomica", "https://laocho.tv/", "Televisión de proximidad en la Comunitat Valenciana."),
    ("7teleValencia", "7 TeleValencia", "autonomica", "https://7televalencia.com/", "Emisión local de las comarcas valencianas y fiestas populares."),
    ("Levante TV", "Levante TV", "autonomica", "https://levantetv.es/", "La televisión comarcal de Valencia vinculada al diario Levante-EMV."),
    ("Información TV", "Información TV", "autonomica", "https://informaciontv.es/", "Canal de proximidad de Alicante y comarcas."),
    ("Popular TV Cantabria", "Popular TV Cantabria", "autonomica", "https://populartvcantabria.com/", "Canal regional de proximidad para Cantabria."),
    ("Popular TV Región de Murcia", "Popular TV Murcia", "autonomica", "https://populartv.net/", "Canal local con contenidos informativos de la Región de Murcia."),
    ("Radio Televisión Ceuta", "RTVCE Ceuta", "autonomica", "https://rtvce.es/", "Televisión pública de la ciudad autónoma de Ceuta."),
    ("Nós Televisión", "Nós TV", "autonomica", "https://nos.gal/", "Canal gallego de divulgación cultural y sociedad civil."),
    ("La 7 Rioja", "La 7 Rioja", "autonomica", "https://tvrioja.com/", "Canal autonómico con noticias y actualidad de La Rioja."),

    # --- DOCUMENTALES & ESTILO DE VIDA (30 channels) ---
    ("National Geographic HD", "National Geographic", "documentales", "https://nationalgeographic.es/", "Exploración científica, misterios del cosmos, arqueología y maravillas del reino animal."),
    ("Nat Geo Wild HD", "Nat Geo Wild", "documentales", "https://nationalgeographic.es/", "El canal 100% dedicado a la fauna salvaje, grandes depredadores y ecosistemas extremos."),
    ("Discovery", "Discovery Channel", "documentales", "https://discoverychannel.es/", "Ingeniería de vanguardia, supervivencia humana extrema, tecnología y ciencia aplicada."),
    ("Historia", "Canal Historia", "documentales", "https://canalhistoria.es/", "Grandes batallas, civilizaciones milenarias, enigmas históricos y líderes mundiales."),
    ("Odisea", "Odisea", "documentales", "https://odisea.es/", "Naturaleza en ultra alta definición, tecnología puntera y el futuro de nuestro planeta."),
    ("AMC Crime", "AMC Crime", "documentales", "https://amcselekt.es/canales/amc-crime/", "El único canal dedicado a la criminología, psicología forense e investigaciones reales."),
    ("AMC Break", "AMC Break", "documentales", "https://amcselekt.es/canales/amc-break/", "Docurrealities extremos, empeños, rescates y desafíos fuera de lo común."),
    ("Canal Cocina", "Canal Cocina", "documentales", "https://canalcocina.es/", "El canal gastronómico de referencia en España con los mejores chefs y recetas del mundo."),
    ("AMC Living", "Decasa / Living", "documentales", "https://amcselekt.es/canales/amc-living/", "Decoración de interiores, reformas espectaculares, jardinería y bienestar."),
    ("AMC Selekt TV", "AMC Selekt", "documentales", "https://amcselekt.es/", "Lo mejor de la oferta temática documental, culinaria y cultural de AMC."),
    ("BBC History", "BBC History", "documentales", "https://bbc.com/", "Documentales históricos con la inconfundible calidad narrativa de la BBC."),
    ("BBC Earth", "BBC Earth", "documentales", "https://bbc.com/", "La cúspide del documental de naturaleza con la producción de la unidad de historia natural de la BBC."),
    ("BBC Top Gear", "Top Gear Channel", "documentales", "https://bbc.com/", "El mítico espacio de motor, coches de ensueño y retos hilarantes."),
    ("BBC Lifestyle", "BBC Lifestyle", "documentales", "https://bbc.com/", "Estilo de vida, moda, tendencias británicas y reformas sorprendentes."),
    ("BBC Food", "BBC Food", "documentales", "https://bbc.com/", "Programas culinarios y grandes concursos gastronómicos internacionales."),
    ("NatureTime", "NatureTime", "documentales", "https://naturetime.tv/", "Relajación con paisajes naturales, fauna y sonidos de la tierra."),
    ("Historia y Vida", "Historia y Vida", "documentales", "https://historiayvida.es/", "Divulgación histórica rigurosa basada en la prestigiosa revista española."),
    ("Love the Planet", "Love the Planet", "documentales", "https://lovetheplanet.tv/", "Sensibilización medioambiental, biodiversidad y sostenibilidad."),
    ("Love Wine", "Love Wine", "documentales", "https://lovewine.tv/", "Cultura enológica, bodegas emblemáticas y viajes gastronómicos."),
    ("VinTV", "VinTV", "documentales", "https://vintv.es/", "Canal dedicado al mundo del vino y las mejores denominaciones de origen."),
    ("Vivir con perros", "Vivir con perros", "documentales", "https://vivirconperros.tv/", "Consejos de adiestramiento, cuidados caninos y razas fascinantes."),
    ("Vivir con gatos", "Vivir con gatos", "documentales", "https://vivircongatos.tv/", "El canal dedicado a los felinos domésticos y su comportamiento."),
    ("Sangre Fría", "Sangre Fría", "documentales", "https://sangrefria.tv/", "Casos policiales sin resolver, crímenes pasionales e intriga."),
    ("Anime Visión", "Anime Visión", "documentales", "https://animevision.tv/", "Canal dedicado a la animación japonesa y la cultura otaku."),
    ("Anime Visión Classics", "Anime Classics", "documentales", "https://animevision.tv/", "Series míticas de anime de los años 80 y 90 que marcaron a generaciones."),
    ("AMC Anime", "AMC Anime", "documentales", "https://amcselekt.es/", "Largometrajes de animación japonesa contemporánea."),
    ("AMC+ Connect", "AMC+ Connect", "documentales", "https://amcplus.es/", "Avances y series exclusivas del universo expandido de AMC+."),
    ("Dviaje", "Dviaje", "documentales", "https://dviaje.tv/", "Rutas turísticas de ensueño, mochileros y expediciones por el planeta."),
    ("Dpelis", "Dpelis", "documentales", "https://dpelis.tv/", "Reportajes sobre rodajes, making-of y anécdotas de Hollywood."),
    ("Escapa TV", "Escapa TV", "documentales", "https://escapatv.com/", "Canal dedicado al turismo activo, senderismo y escapadas de fin de semana."),

    # --- INFANTIL & FAMILIA (9 channels) ---
    ("Disney Channel", "Disney Channel", "infantil", "https://tv.disney.es/", "Magia Disney: series originales infantiles, películas animadas y comedia."),
    ("Nickelodeon HD", "Nickelodeon", "infantil", "https://nickelodeon.es/", "El hogar de Bob Esponja, Loud House, Henry Danger y las mejores risas infantiles."),
    ("Nick JR", "Nick Jr.", "infantil", "https://nickjr.es/", "Contenidos preescolares educativos con La Patrulla Canina y Blaze."),
    ("Dreamworks HD", "DreamWorks", "infantil", "https://dreamworks.com/", "Grandes aventuras animadas: Madagascar, Shrek, Cómo entrenar a tu dragón y Trolls."),
    ("Baby TV", "Baby TV", "infantil", "https://babytv.com/", "Canal pionero diseñado por expertos en desarrollo infantil para bebés y preescolares."),
    ("Pocoyó", "Canal Pocoyó", "infantil", "https://pocoyo.com/", "Las divertidas y formativas aventuras de Pocoyó, Elly, Pato y Loula."),
    ("Toon Goggles", "Toon Goggles", "infantil", "https://toongoggles.com/", "Series de animación segura y videojuegos educativos para niños."),
    ("Gametoon", "Gametoon", "infantil", "https://gametoon.box/", "eSports, gaming y los títulos más populares de la comunidad jugadora."),
    ("Lolly Kids", "Lolly Kids", "infantil", "https://lollykids.tv/", "Música, talento infantil y concursos de jóvenes artistas."),

    # --- MÚSICA (9 channels) ---
    ("MTV España", "MTV España", "musica", "https://mtv.es/", "Videoclips de los mayores éxitos mundiales, reality shows juveniles y los premios EMA."),
    ("Sol Música", "Sol Música", "musica", "https://solmusica.com/", "El canal líder de la música en español: pop, rock, indie y entrevistas exclusivas."),
    ("Mezzo", "Mezzo", "musica", "https://mezzo.tv/", "El canal de referencia de música clásica, ópera, danza contemporánea y jazz."),
    ("Mezzo Live HD", "Mezzo Live", "musica", "https://mezzo.tv/", "Conciertos en directo desde las salas de ópera y filarmónicas más prestigiosas del mundo."),
    ("Classica HD", "Classica", "musica", "https://classica.de/", "Las mejores orquestas, directores legendarios y recitales clásicos."),
    ("Qello concerts", "Qello Concerts", "musica", "https://qello.com/", "Los conciertos más memorables de la historia del rock, pop y leyendas de la música."),
    ("Qwest TV", "Qwest TV", "musica", "https://qwest.tv/", "Curado por Quincy Jones: jazz, soul, funk y ritmos globales."),
    ("TRACE Latina", "TRACE Latina", "musica", "https://trace.tv/", "Reggaetón, bachata, trap latino y ritmos urbanos."),
    ("TRACE Urban", "TRACE Urban", "musica", "https://trace.tv/", "Hip-hop, R&B y las tendencias más potentes de la música urbana global."),

    # --- NOTICIAS & GENERALISTAS (11 channels) ---
    ("EuroNews", "Euronews", "noticias", "https://es.euronews.com/", "La perspectiva europea de la actualidad mundial 24 horas al día en español."),
    ("BBC World News Europe HD", "BBC News Europe", "noticias", "https://bbc.com/news", "El canal internacional de noticias líder de la BBC con corresponsales globales."),
    ("CNN International Europe", "CNN International", "noticias", "https://edition.cnn.com/", "Líder global en información internacional y directos de última hora."),
    ("Al Jazeera English HD", "Al Jazeera English", "noticias", "https://aljazeera.com/", "Noticias internacionales con cobertura profunda del hemisferio sur y Oriente Medio."),
    ("France 24 (en Francais)", "France 24", "noticias", "https://france24.com/", "Información global y análisis geopolítico desde París."),
    ("CNBC Europe HD", "CNBC Europe", "noticias", "https://cnbc.com/", "Mercados financieros, economía global, tecnología y análisis bursátil."),
    ("Bloomberg TV Europe", "Bloomberg TV", "noticias", "https://bloomberg.com/", "Líder indiscutible en información de mercados, cotizaciones y finanzas."),
    ("CGTN Español", "CGTN Español", "noticias", "https://espanol.cgtn.com/", "Noticias internacionales y cultura desde Pekín en español."),
    ("Negocios TV", "Negocios TV", "noticias", "https://negocios.es/", "Canal español de información económica, geopolítica y mercados en tiempo real."),
    ("El Toro TV", "El Toro TV", "noticias", "https://eltorotv.com/", "Canal de análisis político, opinión y actualidad nacional española."),
    ("Canal RED", "Canal RED", "noticias", "https://canalred.tv/", "Canal de televisión centrado en la actualidad sociopolítica y el debate."),

    # --- FAST & STREAMING ABIERTO (10 channels) ---
    ("Runtime Cine y Series", "Runtime Cine", "fast", "https://runtime.tv/", "Canal FAST con películas taquilleras y series populares gratis."),
    ("Runtime Acción", "Runtime Acción", "fast", "https://runtime.tv/", "Cine de acción, persecuciones y thrillers de alta intensidad."),
    ("Runtime Comedia", "Runtime Comedia", "fast", "https://runtime.tv/", "Comedias divertidas y risas garantizadas para toda la familia."),
    ("Runtime Thriller-Terror", "Runtime Terror", "fast", "https://runtime.tv/", "Suspense psicológico, cine de miedo y misterio."),
    ("Runtime Crimen", "Runtime Crimen", "fast", "https://runtime.tv/", "Series policíacas e investigaciones criminales."),
    ("Runtime Romance", "Runtime Romance", "fast", "https://runtime.tv/", "Comedias románticas, dramas de amor y cine emotivo."),
    ("RunTime Clásicos", "Runtime Clásicos", "fast", "https://runtime.tv/", "Cine clásico y largometrajes dorados de Hollywood."),
    ("RunTime Familia", "Runtime Familia", "fast", "https://runtime.tv/", "Películas y animación recomendadas para todas las edades."),
    ("Runtime Series", "Runtime Series", "fast", "https://runtime.tv/", "Maratones de series de ficción continuas."),
    ("TR3CE", "TRECE +", "fast", "https://trecetv.es/", "Señal temática complementaria de cine y actualidad.")
]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[\+\s\.]+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text

dial = len(channels_200) + 1

for xmltv_id, name, group, stream_url, desc in additional_specs:
    if len(channels_200) >= 200:
        break
    if xmltv_id in used_xmltv:
        continue

    doble_info = ch_map.get(xmltv_id, {})
    logo = doble_info.get('logo', '')
    if not logo:
        safe_name = urllib.parse.quote(name)
        logo = f"https://raw.githubusercontent.com/davidmuma/picons_dobleM/master/icon/{safe_name}.png"

    slug = slugify(name)
    if slug in used_slugs:
        slug = f"{slug}-{dial}"
    used_slugs.add(slug)
    used_xmltv.add(xmltv_id)

    channels_200.append({
        "id": slug,
        "xmltvId": xmltv_id,
        "name": name,
        "number": dial,
        "group": group,
        "logo": logo,
        "streamUrl": stream_url,
        "description": desc
    })
    dial += 1

print(f"Curated {len(channels_200)} channels!")

with open('src/data/channels.json', 'w', encoding='utf-8') as f:
    json.dump(channels_200, f, ensure_ascii=False, indent=2)

print("Saved to src/data/channels.json!")
