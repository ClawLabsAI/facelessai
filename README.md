# FacelessAI

**Motor de contenido con IA para canales _faceless_**: de la idea al guion (y al vídeo)
sin aparecer en cámara. Genera ideas virales, las puntúa, escribe el guion, produce la voz
y monta el MP4 vertical — con control de coste por vídeo.

> **Modelo BYOK (_Bring Your Own Key_)**: usas tus propias claves de API. Tus claves se
> guardan **solo en tu navegador** y se envían **únicamente** al proveedor correspondiente.
> Nunca pasan por servidores de FacelessAI.

---

## Qué hace

| Módulo | Descripción |
|---|---|
| **Pipeline** | Idea → Score IA → Guion → Voz → Vídeo → Borrador, en 6 pasos guiados |
| **Canales** | Gestión multi-canal con nicho, idioma, voz y afiliados propios |
| **AutoPilot** | Genera y aprueba contenido solo, por umbral de score, en ciclos |
| **Batch** | Semana completa de vídeos de una tacada |
| **Scheduler** | Cola de publicación con horas óptimas por nicho |
| **Analytics** | Coste real de IA, stats por canal y por plataforma |
| **Modelos IA** | 6 tiers (de gratis a ultra) con coste por vídeo transparente |
| **Extras** | Clipping de vídeos largos, espía de canales, clonado a otro mercado, afiliados |

## Requisitos

- Un navegador moderno. **No hay instalación**: la app es un único `index.html`.
- **Clave de Anthropic** (imprescindible para ideas/guion/score).
- Opcionales: OpenAI o ElevenLabs (voz), Pexels (clips), HeyGen/D-ID/Runway/Kling (vídeo IA).
- Opcional: backend propio (`main.py`) si quieres render de MP4 con FFmpeg.

## Empezar

1. Abre la app y ve a **⚙️ Configuración**.
2. Pega tu clave de Anthropic y pulsa **Probar**.
3. En **⚡ Modelos IA** elige un tier (recomendado: *Económico* para empezar).
4. Crea un canal en **Mis canales**.
5. Ve a **Pipeline** y genera tu primer vídeo.

Guía de validación paso a paso: [`docs/SMOKE-TEST.md`](docs/SMOKE-TEST.md).

## Backend opcional (render de MP4)

```bash
pip install -r requirements.txt
export FAI_API_KEY="una-clave-larga-y-secreta"      # protege el backend
export FAI_ALLOWED_ORIGINS="https://tu-dominio"      # CORS
uvicorn main:app --host 0.0.0.0 --port 8000
```

Luego pega la URL y la clave en **⚙️ Configuración → Backend**.

> ⚠️ **Define siempre `FAI_API_KEY` en producción.** Sin ella el backend acepta peticiones
> sin autenticar y cualquiera podría consumir tu cómputo. Variables disponibles:
> `FAI_API_KEY`, `FAI_ALLOWED_ORIGINS`, `FAI_RATE_LIMIT_MAX`, `FAI_RATE_LIMIT_WINDOW`, `FAI_FILE_TTL`.

## Desarrollo

```bash
npm test          # comprobaciones estáticas (sintaxis, duplicados, invariante de fichero único)
npm run build     # minificado opcional -> dist/index.html
```

- Arquitectura y decisiones: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Auditoría y hoja de ruta: [`docs/AUDIT-2026-07.md`](docs/AUDIT-2026-07.md)

## Privacidad

Todos los datos (canales, borradores, claves, ajustes) viven en el `localStorage` de tu
navegador. No hay cuentas ni servidor de datos. Borra tus claves antes de ceder el equipo.

## Licencia

Software propietario — ver [`LICENSE`](LICENSE).
