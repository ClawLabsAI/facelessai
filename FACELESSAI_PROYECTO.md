# FacelessAI — Documento de Contexto del Proyecto
**Última actualización:** Marzo 2026
**Versión actual del dashboard:** v3.26
**URL live:** https://clawlabsai.github.io/facelessai
**Repositorio frontend:** https://github.com/clawlabsai/facelessai (rama: main, archivo: index.html)
**Repositorio backend:** https://github.com/clawlabsai/facelessai-backend
**Backend URL:** https://facelessai-backend-production.up.railway.app

---

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| index.html | Dashboard principal v3.26 |
| keys.html | Página auxiliar para API keys |
| FACELESSAI_PROYECTO.md | Este documento |
| facelessai-backend/main.py | Servidor FastAPI Railway |
| facelessai-backend/requirements.txt | Dependencias Python |
| facelessai-backend/Dockerfile | Docker config Railway |
| facelessai-backend/railway.json | Railway config |

## Gist GitHub
- ID: 86bf7d5a8e7dc233a62a99debcfae390
- Secrets repo: GIST_ID + GIST_TOKEN

---

## API Keys configuradas (localStorage)

| Servicio | Estado | Uso |
|---|---|---|
| Anthropic | ACTIVA sk-ant-api03-... | Ideas, Score, Scripts, Canales IA, Afiliados IA |
| OpenAI | ACTIVA sk-proj-... | TTS audio MP3 + Whisper transcripción |
| Pexels | ACTIVA | Clips de vídeo gratis |
| ElevenLabs | Opcional | Tier Premium |
| GitHub Token | ACTIVO ghp_... | Deploy Gist |

---

## localStorage keys

- fai_key_anthropic, fai_key_openai, fai_key_pexels, fai_key_elevenlabs, fai_key_github
- fai_backend_url — URL del backend Railway
- fai_drafts — borradores guardados (array JSON)
- fai_channels — canales faceless (array JSON)
- fai_clip_channels — canales de clipping (array JSON)
- fai_tts_channels — canales TikTok Shop (array JSON)
- fai_affiliates — programas de afiliados (array JSON)
- fai_lang, fai_gender — idioma y voz activos
- fai_tier — tier de coste activo
- fai_theme, fai_currency, fai_date_fmt — preferencias UI

---

## Backend Railway (FastAPI + FFmpeg + yt-dlp + Whisper)

- URL: https://facelessai-backend-production.up.railway.app
- Puerto: 8080 (variable Railway PORT)
- Health: GET /health → {"status":"ok","ffmpeg":"available"}

### Endpoints disponibles:

**Generación de vídeo:**
- POST /generate — genera MP4 desde audio_b64 + clips Pexels
- GET /status/{job_id} — estado del job
- GET /download/{job_id} — descarga el MP4
- POST /debug — debug del payload recibido

**Clipping:**
- POST /transcribe — descarga YT + Whisper transcripción
- GET /transcribe/status/{job_id}
- POST /clip — descarga YT + corta momentos + convierte 9:16
- GET /clip/status/{job_id}
- GET /clip/download/{job_id}/{clip_index}

### VideoRequest model (actual):
```python
class VideoRequest(BaseModel):
    audio_b64: str         # Base64 encoded audio (REQUERIDO)
    audio_url: str = ""    # Legacy, ignorado pero aceptado para compatibilidad
    pexels_clips: list[str] = []
    script: str = ""
    title: str = "FacelessAI Video"
    lang: str = "es"
    subtitle_style: str = "viral"
```

IMPORTANTE: El frontend siempre envía audio_url: "" junto con audio_b64 para compatibilidad.

### Bug conocido pendiente:
Railway sigue desplegando versión antigua del main.py que requiere audio_url.
El frontend ya envía audio_url vacío como workaround.
Solución definitiva: forzar redeploy limpio en Railway eliminando el servicio y recreando.

---

## Sistema de idiomas y voces (topbar)

| Mercado | Voz hombre | Voz mujer |
|---|---|---|
| Español España | onyx | nova |
| English US | echo | alloy |
| Español Latino | fable | shimmer |

---

## Tiers de coste

| Tier | LLM | TTS | Coste/vídeo |
|---|---|---|---|
| GRATIS | Llama local | Kokoro | $0.00 |
| ECONOMICO | Claude Haiku | OpenAI TTS-1 | ~$0.01 |
| OPTIMIZADO | Claude Sonnet | OpenAI TTS-1 HD | ~$0.06 |
| PREMIUM | Claude Opus | ElevenLabs v3 | ~$0.25 |

---

## Menú sidebar completo (v3.26)

```
── Inicio ──        Dashboard · Canales · Borradores
── Crear ──         Tendencias · Score IA · Pipeline · URL→Vídeo
── Clipping ──      Canales Clipping · Pipeline Clipping
── Biblioteca ──    Plantillas · Clonar canal · Reutilizar
── TikTok Shop ──   Canales Shop · Pipeline Producto · AutoPost Shop
── Marketing ──     Afiliados · Publicidad (placeholder)
── Automatización── AutoPilot · Modelos IA · Presupuesto
── Datos ──         Monetización · Configuración
```

---

## Topbar (v3.26)

[ES/EN/LAT]  [Hombre/Mujer]  [Manual/AutoPilot]  ···  [$hoy]  [deploy icono]  [Generar]

---

## Lo que funciona al 100% (real)

1. Ideas reales con Claude por nicho e idioma
2. Score predictivo real en pipeline (paso 2 auto-analiza idea seleccionada)
3. Scripts reales con Claude (adaptados al idioma/mercado)
4. Pegar script manualmente (sin coste)
5. Edición directa del script generado
6. Audio MP3 real con OpenAI TTS (voz según idioma+genero)
7. Búsqueda clips Pexels (real, con miniaturas, selección múltiple)
8. Flujo 3 botones secuenciales en paso 4 (audio → clips → MP4) con flechas y colores dinámicos
9. Borradores reales en localStorage (con audio URL, script, score)
10. Canales guardados en localStorage (idioma/voz/nicho/genero)
11. Dashboard con datos reales (stats, canales, borradores recientes)
12. Canales view con cards rediseñadas (color por nicho, layout limpio)
13. Descubrimiento de canales con IA (6 oportunidades con score, CPM, saturación)
14. Configuración: keys, backend URL con test, tiers de coste
15. Preferencias: tema oscuro/claro, moneda, formato fecha (persistentes)
16. Selector idioma/voz en topbar (persiste entre sesiones)
17. TikTok Shop: canales, pipeline producto UGC (6 pasos), descubrimiento nichos IA
18. Clipping: canales, pipeline 5 pasos (URL→Transcripción→Selección IA→Clips→Descarga)
19. Sugerencias de canales YouTube para clipping (Claude sugiere 6 por nicho)
20. Afiliados: gestión de links, sugerencias IA, añadir desde sugerencias

---

## Pipeline Principal — flujo paso 4

3 botones secuenciales con flechas y colores dinámicos:
[① Generar audio] → [② Buscar clips] → [③ Generar MP4]

- Botón activo: verde brillante con sombra
- Botón completado: verde outline
- Botón pendiente: gris
- Flechas cambian de gris a verde al completar cada paso
- Si intentas saltarte un paso: aviso y el botón correcto se ilumina

---

## TikTok Shop — módulo completo

Vistas: Canales Shop · Pipeline Producto · AutoPost Shop

Pipeline Producto (6 pasos):
1. URL del producto → Claude extrae nombre, precio, comisión, beneficios
2. Score viral + análisis IA del producto
3. Scripts UGC — 3 variantes (Review / Problema-Solución / Tutorial / Antes-Después) o pegar manual
4. Audio TTS con voz seleccionable
5. Búsqueda clips Pexels + generación MP4
6. Publicar (descarga MP4 + instrucciones TikTok)

---

## Clipping — módulo completo

Vistas: Canales Clipping · Pipeline Clipping

Pipeline Clipping (5 pasos):
1. URL YouTube + sugerencias IA de canales (6 opciones por nicho/idioma)
2. Transcripción con Whisper via Railway
3. Selección IA de momentos virales (Claude analiza transcripción)
4. Generación clips MP4 (Railway: yt-dlp + FFmpeg → 9:16 vertical)
5. Descarga clips individuales

Coste: ~$0.01-0.015 por vídeo procesado

---

## Marketing — módulo

### Afiliados (funcional):
- Stats: total afiliados, comisiones estimadas, links insertados
- Sugerencias IA: Claude sugiere 6 programas por nicho/mercado/tipo
- Mis afiliados: cards con link, comisión, CTA, stats
- Acciones: copiar link, usar en vídeo, eliminar
- Modal creación: nombre, categoría, URL, comisión, cookie, nichos, CTA
- Integración pipeline: "Usar en vídeo" activa el afiliado para el siguiente vídeo

### Publicidad (placeholder):
- Explica por qué tiene sentido para canales faceless
- Roadmap Q2-Q3 2026
- Botón → Afiliados

---

## Configuración — secciones

1. API Keys — Anthropic, OpenAI, Pexels, ElevenLabs con badge, test, diagnóstico
2. Backend de vídeo — URL Railway con test de conexión
3. Tiers de coste — selector + estimador mensual
4. Preferencias generales — Tema · Idioma UI · Moneda · Formato fecha

---

## Próximos pasos prioritarios

### CRÍTICO — Backend Railway
El error 422 (audio_url field required) bloquea la generación de vídeos.
Workaround actual: frontend envía audio_url: "" vacío.
Solución definitiva: eliminar el servicio en Railway y recrearlo para forzar deploy limpio del main.py actual.

### ALTA PRIORIDAD
1. Resolver backend definitivamente
2. Dashboard — gráfico de actividad últimos 7 días
3. Pipeline paso 5 — mostrar preview del MP4 generado en pantalla de aprobación
4. Sidebar badges con contadores reales en tiempo real

### SIGUIENTE
5. YouTube API — publicación directa
6. Tendencias reales — conectar a Google Trends via web search
7. AutoPilot real — cron job en Railway
8. TikTok Content Posting API (requiere app aprobada 2-7 días)

### FUTURO
9. Publicidad de canales (YouTube Ads / Meta Ads)
10. Multi-idioma UI (inglés completo)
11. Multi-usuario / equipo

---

## Changelog versiones

| Versión | Cambios principales |
|---|---|
| v3.0-3.4 | APIs reales, menú reorganizado, fix localStorage |
| v3.5 | Selector idioma/voz topbar, modal canal, descubrimiento IA |
| v3.6 | Borradores reales, score pipeline auto, canales guardados |
| v3.7 | Preferencias generales en Configuración |
| v3.8 | Topbar limpia sin elementos redundantes |
| v3.9 | Backend Railway conectado, campo URL en Configuración |
| v3.10 | Flujo 3 pasos secuenciales en paso 4 |
| v3.11 | Fix duplicate const genBtn en TTS |
| v3.12-3.13 | Flechas entre botones del flujo con IDs y colores dinámicos |
| v3.14 | Tema claro/oscuro funcional, moneda, fecha |
| v3.15 | Fix: TTS no sobreescribe gen-btn |
| v3.16 | Fix: pexels-run-btn con estado propio |
| v3.17-3.18 | Error 422 mejorado, VideoRequest sin audio_url, módulo TikTok Shop HTML |
| v3.19 | Módulo TikTok Shop completo con todas las funciones JS |
| v3.20 | Botón Pegar y edición manual en script |
| v3.21 | Dashboard y Canales con datos reales de localStorage |
| v3.22 | Fix 422: frontend envía audio_url vacío + backend acepta ambos |
| v3.23 | Módulo Clipping completo (canales + pipeline 5 pasos + backend endpoints) |
| v3.24 | Sugerencias IA de canales YouTube para clipping |
| v3.24b | Fix JS: función loadYTInfo sin declaración + deleteChannel duplicado |
| v3.25 | Sidebar labels más visibles, cards canales rediseñadas |
| v3.26 | Módulo Marketing: Afiliados funcional + Publicidad placeholder |

---

## Cómo continuar desde otro PC

1. Ir a claude.ai con tu cuenta — el chat está guardado
2. O pegar este documento al inicio de una conversación nueva
3. Abrir clawlabsai.github.io/facelessai/keys.html
4. Introducir las API keys de nuevo
5. En Configuración → Backend URL → pegar https://facelessai-backend-production.up.railway.app
6. Continuar desde donde se dejó

Actualizado con cada versión del dashboard.
