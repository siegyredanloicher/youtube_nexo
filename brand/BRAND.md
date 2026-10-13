# Omnia: identidad del canal

**Nombre:** Omnia (latín: "todo"). Internacional: se lee igual en castellano e inglés.
**Descriptor:** Conocimiento para todos · Knowledge for everyone
**Lema:** Entender, no memorizar · Understand, don't memorize
**Estado del nombre:** elegido. Falta comprobar a mano YouTube (@omniaacademy u otro), dominio y marca (EUIPO/OEPM).

## Logotipo (`brand/logo/`)
- Marca: cuatro arcos, uno por nivel (verde, azul, violeta, coral), alrededor del triángulo de Nexo, sobre un cuadrado marino.
- Palabra: "omnia" en Sora Bold, minúsculas, convertida a trazados (el SVG no depende de ninguna fuente).
- Archivos: `omnia_marca.svg`, `omnia_marca_sin_fondo.svg`, `omnia_logo_horizontal.svg`, `omnia_avatar.png` (800x800), `omnia_banner_youtube.png` (2560x1440).
- Se regeneran con `make_logo.py` y `render_assets.py` desde `tokens.json`.
- Zona segura del banner de YouTube: 1546x423 px centrados. El logotipo y el descriptor caben dentro.
- El avatar va a sangre (sin esquinas redondeadas) porque YouTube lo recorta en círculo.
- Uso: sobre fondo crema o marino. Nunca sobre negro. No deformar ni recolorear los arcos.

# Identidad visual del canal

Fuente única: `tokens.json`. En código: `from brand import C, F, nivel, rgb, linear`.

## Colores
| Uso | Valor |
|---|---|
| Fondo base | `#F4EEE4` (crema claro) |
| Fondo alterno / Nexo crema | `#E8DBC9` |
| Superficie (tarjetas) | `#FBF8F2` |
| Tinta principal / azul marino de Nexo | `#1C2A47` |
| Tinta suave | `#4A5873` |

**Nivel (color de Nexo y de la cabecera del curso)**
| Nivel | Relleno | Texto |
|---|---|---|
| ESO (verde) | `#7DD3C0` | `#1F7563` |
| Bachillerato (azul) | `#7CC4F2` | `#1F6B9E` |
| Universidad (violeta) | `#A78BFA` | `#6D4FD6` |
| Avanzado (coral) | `#F8A5A5` | `#B5383F` |

**Términos de fórmulas:** a `#1F6B9E`, b `#B5383F`, c `#1F7563`, d `#8F5E0F`, siempre en ese orden y el mismo término con el mismo color en todo el vídeo.
**Estado:** acierto `#247A50`, error `#B5383F`, aviso `#8F5E0F`.

Todos los colores de texto superan contraste 4,5 sobre el fondo base (se comprueba con `python brand/brand.py`).

## Tipografías (todas gratuitas, licencia OFL)
| Uso | Fuente | Dónde |
|---|---|---|
| Títulos | Sora SemiBold | Google Fonts |
| Texto | Manrope Medium | Google Fonts |
| Fórmulas | STIX Two Math (o Latin Modern Math) | Google Fonts / CTAN |
| Código | JetBrains Mono | Google Fonts |

Descarga los `.ttf` en `brand/fonts/` y no los cambies. Escala en 1080p: título 72, subtítulo 48, cuerpo 36, fórmula 64, pie 24.

## Reglas
- Nunca fondo negro. Modo oscuro, si existe: `#1C2A47`.
- El color de nivel identifica el curso, no resalta términos.
- Máximo 2 familias de texto por pantalla.
- Margen seguro de 96 px.
- Nexo: crema `#E8DBC9`, sombra `#CDB99F`, botas `#BBA88E`, mochila marino `#1C2A47`, acento según nivel.

## Archivos que faltan por añadir
- `brand/logo/` logotipo del canal y versión cuadrada para el avatar
- `brand/logo/intro.mp4` y `cierre.mp4` (3-5 s)
- `brand/fonts/*.ttf`
- Plantilla de miniatura (PNG de 1280x720 con zonas marcadas)
