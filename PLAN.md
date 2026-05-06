# FacelessAI — Plan de implementación completo
**Generado:** 2026-05-07 · Versión en producción al generar: v4.32
**✅ COMPLETADO:** 2026-05-07 · Frontend v4.37 · Backend v2.1 — todas las 7 fases ejecutadas
**Objetivo:** Llevar FacelessAI a funcionalidad 100 % — cada vista, tier, pipeline y publicación funciona de extremo a extremo.

## Resumen de fases completadas
| Fase | Descripción | Frontend | Backend |
|---|---|---|---|
| 1 | Bugs lógica (Ultra/Scale tier, score real) | v4.33 | — |
| 2 | AutoPilot pipeline completo + jobs persistentes | v4.34 | v1.7 |
| 3 | Subtítulos, zoom_effect, cleanup, requirements | — | v1.8 |
| 4 | YouTube OAuth PKCE + refresh token | v4.35 | v1.9 |
| 7 | Backend hardening (X-FAI-Key, rate limit, CORS) | v4.36 | v2.0 |
| 5 | Scheduler persistente + TikTok OAuth real | v4.36 | — |
| 6 | UX cleanup (Scale labels, SaaS hidden, English UI) | v4.37 | v2.1 |

---

---

## Estado verificado (Phase 0 — Discovery)

### Backend (`facelessai-backend-production.up.railway.app` — main.py, 596 líneas)
| Endpoint | Estado |
|---|---|
| `GET /` | ✅ 200, devuelve versión 1.6 + ffmpeg 7.1.3 |
| `GET /health` | ✅ 200, `openai_configured: true`, `pexels_configured: true` |
| `GET /pexels/search` | ✅ 200, devuelve resultados reales |
| `POST /tts` | ✅ 405 en GET (confirma que la ruta existe, solo acepta POST) |
| `POST /generate` | ✅ Funciona (no probado con carga completa) |
| `GET /status/{id}` | ✅ Funciona |
| `GET /download/{id}` | ✅ Funciona |
| `GET /youtube/upload` | ❌ 404 — la ruta no existe (upload es browser-side) |

### Frontend (index.html, ~13 000 líneas, GitHub Pages)
- ✅ v4.32 cargando en `https://clawlabsai.github.io/facelessai/`
- ✅ Bugs v4.32 ya corregidos: `_navCallbacks` duplicados, `createChannelFromDisc` duplicada, doble init

### Bugs críticos pendientes confirmados
1. **`callClaude()` línea ~12562**: `prem` → `premium`, `ultra` → `premium` — Ultra usa Sonnet en vez de Opus. [línea 12566 aprox]
2. **AutoPilot** (`runAutopilotCycle` línea ~9199): genera solo idea+script, no pone `videoUrl` en el draft → imposible publicar en YouTube desde AutoPilot.
3. **Score aleatorio** (línea 9251): `Math.floor(72 + Math.random() * 20)` — no es una puntuación de IA real.
4. **YouTube OAuth implicit grant** (línea ~4877): Google ha deprecado `response_type=token`, tokens expiran en 1 h sin refresh.
5. **`generate_srt()`** (backend, líneas 584–595): definida pero nunca llamada — subtítulos completamente muertos.
6. **Parámetros silenciados en `/generate`**: `subtitle_style`, `add_music`, `music_volume`, `zoom_effect`, `lang`, `niche` aceptados pero ignorados en `process_video`.
7. **Jobs en memoria** (backend línea 53): `jobs = {}` — se pierde al reiniciar Railway.
8. **Tier `scale`**: declara `groq-llama-3` pero no existe ningún code path a Groq. Todas las llamadas van a Claude.
9. **TikTok posting** (línea ~2711): stub — `showToast('Guía TikTok API — próximamente')`.
10. **`access_token` en query params** (líneas 160, 190 backend): token OAuth expuesto en logs del servidor.

---

## Phase 1 — Bugs críticos de lógica (index.html)
**Objetivo:** Corregir los fallos que afectan features documentadas como activas (tiers, ultra model, score real).
**Archivo:** `index.html`
**Bump de versión:** v4.32 → v4.33

### 1.1 — Fix Ultra tier en `callClaude()`
**Qué:** En línea ~12566 el mapeo `activeTier === 'ultra' ? 'premium'` hace que Ultra use el mismo modelo que Premium (Sonnet). Debe usar Opus.
**Cómo copiar el patrón:** Leer líneas 12562–12580 de index.html. Cambiar:
```javascript
// ANTES (buggy):
const tierKey = activeTier === 'prem' ? 'premium' : activeTier === 'ultra' ? 'premium' : (activeTier || 'eco');

// DESPUÉS (correcto):
const tierKey = activeTier === 'prem' ? 'premium'
              : activeTier === 'ultra' ? 'ultra'
              : (activeTier || 'eco');
```
Añadir `ultra` a `TIER_CONFIG` si no tiene entrada propia (leer líneas ~4976–4983 para verificar).

### 1.2 — Fix tier `scale` — eliminar Groq fantasma
**Qué:** `scale` en `TIER_CONFIG` declara `llmModel: 'groq-llama-3'` pero no hay code path a Groq. Engaña al usuario.
**Cómo:** Cambiar `llmModel` de `scale` a `'claude-haiku-4-5-20251001'` (modelo económico real disponible). Actualizar el label visual a "Claude Haiku Batch".

### 1.3 — Score real en AutoPilot
**Qué:** Línea ~9251 usa `Math.floor(72 + Math.random() * 20)`. El score debe llamar a `callClaude()` con el hook+script y retornar un número real.
**Patrón existente a copiar:** La función `runScoreReal()` (buscar en index.html) ya genera un score de IA. Invocarla tras generar el script en `runAutopilotCycle()`.
**Precaución:** Añade latencia al ciclo y consume tokens. Envolver en `try/catch` y solo llamar si `activeTier !== 'free'`.

### Verificación Phase 1
- [ ] Grep: `activeTier === 'ultra' ? 'premium'` → 0 resultados
- [ ] En DevTools: cambiar tier a `ultra`, llamar `callClaude('test', null, 10)`, verificar en la petición a Anthropic que el modelo es `claude-opus-*`
- [ ] En DevTools: cambiar tier a `scale`, verificar que `callClaude` usa `claude-haiku-*`
- [ ] Ejecutar un ciclo AutoPilot con tier `eco`; comprobar que el draft creado tiene un campo `score` distinto a un número entre 72 y 92 aleatoriamente fijo

---

## Phase 2 — AutoPilot pipeline completo
**Objetivo:** AutoPilot genera idea → score → script → TTS → Pexels clips → video en backend → `videoUrl` en draft → listo para publicar.
**Archivos:** `index.html`, `_backend_tmp/main.py`
**Bump:** v4.33 → v4.34

### 2.1 — `runAutopilotCycle()` extendido
**Qué:** Tras generar el script, añadir pasos opcionales (controlados por checkbox en UI AutoPilot):
1. **TTS automático**: llamar al backend `POST /tts` con el script (≤500 chars) → obtener `audio_b64`
2. **Pexels clips automáticos**: llamar a `GET /pexels/search?query={niche}&per_page=5` → lista de URLs
3. **Video generation**: `POST /generate` con `audio_b64` + `pexels_clips` → `job_id`
4. **Poll status**: `GET /status/{job_id}` cada 5s hasta `status === 'done'`
5. **Guardar `videoUrl`**: `{BACKEND_URL}/download/{job_id}` en el draft

**Patrón existente a copiar:** La función `generateVideoShop()` (TikTok Shop, línea ~12077) hace exactamente este flujo: POST /generate → poll → guardar videoUrl. Leerla completa y copiar la lógica de polling.

**UI necesaria:** Checkbox en panel AutoPilot "Generar video automáticamente (consume más créditos)". Variable `fai_ap_full_pipeline` en localStorage.

### 2.2 — Backend: hacer `/generate` persistente tras restart
**Qué:** El dict `jobs` en línea 53 de main.py se pierde al reiniciar. Solución mínima: escribir estado de jobs en un archivo JSON en `TEMP_DIR`.
**Patrón:** Usar `json.dump` / `json.load` en las funciones `process_video` y `GET /status/{job_id}`.
**Archivo:** `_backend_tmp/main.py`

### Verificación Phase 2
- [ ] Activar AutoPilot con "Generar video automáticamente" ON, esperar un ciclo
- [ ] Verificar que el draft tiene campo `videoUrl` → botón "Publicar en YouTube" se activa
- [ ] Reiniciar el servicio Railway y comprobar que `GET /status/{job_id}` de un job previo devuelve datos (no 404)

---

## Phase 3 — Subtítulos y parámetros de video activos (backend)
**Objetivo:** Los parámetros `subtitle_style`, `add_music`, `zoom_effect` dejan de silenciarse.
**Archivo:** `_backend_tmp/main.py`
**Bump:** v4.34 → v4.35

### 3.1 — Activar `generate_srt()` en el pipeline
**Qué:** La función `generate_srt(script, duration)` ya está definida (líneas 584–595 de main.py). Nunca se invoca.
**Cómo:** En `process_video()` (línea ~292), tras obtener `audio_duration`, llamar:
```python
srt_content = generate_srt(req.script, audio_duration)
srt_path = job_dir / f"{job_id}.srt"
srt_path.write_text(srt_content, encoding="utf-8")
```
Luego en el ffmpeg `compose_video_audio()` añadir filtro `subtitles={srt_path}` cuando `req.subtitle_style != 'none'`.

### 3.2 — Zoom effect en clips
**Qué:** `zoom_effect: bool = True` es aceptado pero ignorado. En `process_one_clip()` (líneas ~427–494), si `zoom_effect` es True, añadir al filtro ffmpeg: `zoompan=z='if(lte(zoom,1.0),1.5,max(1.001,zoom-0.0015))':d=25:s=1080x1920`.

### 3.3 — Música de fondo
**Qué:** `add_music: bool = False` + `music_volume: float = 0.08`. Si `add_music` es True y existe un archivo `background.mp3` en el directorio de assets del backend, mezclarlo con `amix` en ffmpeg.
**Nota:** Requiere subir un archivo de música libre de derechos al backend. Documentar en README del backend.

### 3.4 — Limpieza de archivos temporales
**Qué:** En caso de error, `job_dir` no se elimina (línea ~403). Añadir `finally: shutil.rmtree(job_dir, ignore_errors=True)` también en el bloque de error.
**Qué 2:** El archivo `diag_test.mp4` no se elimina si falla (línea 102–106 de main.py). Envolver en `try/finally`.

### 3.5 — Limpiar requirements.txt
**Qué:** `yt-dlp` y `openai` están declarados pero nunca importados. Eliminarlos para reducir tiempo de build en Railway.

### Verificación Phase 3
- [ ] `POST /generate` con `subtitle_style: "capcut"` y un script de 3 líneas → video descargado tiene subtítulos visibles
- [ ] `POST /generate` con `zoom_effect: true` → clips tienen zoom-in/out
- [ ] `GET /diag` → `diag_test.mp4` limpiado incluso al forzar error
- [ ] Tiempo de deploy Railway reducido (sin instalar yt-dlp + openai)

---

## Phase 4 — YouTube OAuth moderno (PKCE)
**Objetivo:** Reemplazar el implicit grant obsoleto por Authorization Code + PKCE con refresh token.
**Archivo:** `index.html`
**Bump:** v4.35 → v4.36

### 4.1 — PKCE Authorization Code flow
**Qué:** La función `startYouTubeOAuth()` (línea ~4877) usa `response_type=token` (implicit grant). Google lo deprecó para nuevas apps en 2022.
**Cómo:**
1. Generar `code_verifier` (random 43-128 chars), `code_challenge = base64url(SHA256(verifier))`
2. Redirigir a `https://accounts.google.com/o/oauth2/v2/auth?response_type=code&code_challenge_method=S256&code_challenge={challenge}&...`
3. En el redirect URI (puede ser la propia página GitHub Pages con `?code=...`), intercambiar `code` por tokens vía `POST https://oauth2.googleapis.com/token`
4. Guardar `access_token` + `refresh_token` en localStorage
5. Antes de cada YouTube API call, comprobar si el `access_token` ha expirado (campo `expires_in`) y usar `refresh_token` para renovarlo

**Patrón de referencia:** Google Identity Services (GIS) docs: `https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow#migrating-to-gis`

### 4.2 — Mover tokens de query params a headers
**Qué:** `GET /yt/channel-stats?access_token=...` (backend línea 160) expone el token en logs.
**Cómo backend:** Cambiar los endpoints `/yt/channel-stats` y `/yt/recent-videos` para leer el token del header `Authorization: Bearer {token}`.
**Cómo frontend:** En las llamadas desde index.html, pasar el token en header en vez de query param.

### Verificación Phase 4
- [ ] Flujo OAuth completo: clic "Conectar YouTube" → pantalla de consent Google → redirect back con `?code=...` → tokens guardados en localStorage
- [ ] Después de 1h, la siguiente llamada a YouTube API usa refresh automático sin re-autenticar
- [ ] `GET /yt/channel-stats` con `Authorization: Bearer {token}` devuelve stats correctamente
- [ ] Grep en frontend: `access_token=` en query params → 0 resultados para llamadas backend

---

## Phase 5 — Distribución real: TikTok + Scheduler
**Objetivo:** El Scheduler dispara publicación automática; TikTok posting funcional.
**Archivo:** `index.html`, posiblemente nuevo endpoint en main.py
**Bump:** v4.36 → v4.37

### 5.1 — Scheduler real con setInterval persistente
**Qué:** El AutoPilot programa el siguiente ciclo con `setTimeout` (no `setInterval`), que se pierde si el usuario cierra el tab. Implementar un worker via `localStorage` + `visibilitychange` que compruebe el timestamp al abrir la app.
**Patrón:** Al iniciar (`nav('autopilot')` callback), leer `fai_ap_next_run` de localStorage. Si está en el pasado y AutoPilot está activo, ejecutar `runAutopilotCycle()` inmediatamente.

### 5.2 — TikTok Content Posting API
**Qué:** El botón "Publicar en TikTok" es un stub (`showToast`). La TikTok Content Posting API (v2) permite subir videos via `POST https://open.tiktokapis.com/v2/post/publish/video/init/`.
**Requerimientos:**
- OAuth 2.0 de TikTok (similar al de YouTube): añadir `startTikTokOAuth()` análogo a YouTube
- Scopes: `video.upload`, `video.publish`
- Implementar `publishToTikTok(draftId)` similar a `publishToYouTube(draftId)`
**Referencia:** `https://developers.tiktok.com/doc/content-posting-api-get-started`

### 5.3 — Publicar el Scheduler de cola
**Qué:** `renderPublishQueue()` existe pero desconocemos si es un stub. Leer y completar si es necesario.
**Verificación:** En la vista Scheduler, los drafts aprobados con fecha programada se publican automáticamente.

### Verificación Phase 5
- [ ] Cerrar el tab del app. Abrirlo N horas después. Si AutoPilot activo y hora pasada, ciclo ejecutado automáticamente
- [ ] TikTok OAuth: `startTikTokOAuth()` → consent → token guardado
- [ ] `publishToTikTok(draftId)` de un draft con `videoUrl` → post visible en TikTok Creator Studio
- [ ] Draft con `scheduledAt` en el pasado → se publica al abrir la app

---

## Phase 6 — Limpieza de UX y features "Próximamente"
**Objetivo:** Eliminar o completar los stubs visibles que degradan la percepción de calidad.
**Archivo:** `index.html`
**Bump:** v4.37 → v4.38

### 6.1 — English UI real
**Qué:** Línea ~5593: `showToast('🇬🇧 English UI — próximamente')`. El toggle de idioma es un stub.
**Cómo:** Crear un objeto de traducciones `const I18N = { es: {...}, en: {...} }` con los 50–80 strings más frecuentes en la UI. La función `setLang(lang)` (ya existe) debe iterar todos los elementos con `data-i18n="key"` y reemplazar su `textContent`.

### 6.2 — Templates view real
**Qué:** La vista `view-templates` muestra "Próximamente". La data de hooks ya se guarda en `fai_hooks` (localStorage). `loadSavedHooks()` y `filterHooks()` existen.
**Cómo:** Comprobar si `loadSavedHooks()` ya renderiza la grid. Si sí, eliminar el "Próximamente" del HTML y mostrar la grid directamente.

### 6.3 — Keys declaradas pero sin UI de configuración
**Qué:** `KEYS.socialblade`, `KEYS.kalodata`, `KEYS.hypeauditor` están en `KEY_MAP` pero no tienen campo en Settings y no se usan en ningún fetch.
**Cómo:** Eliminarlos de `KEY_MAP` o añadir los campos en Settings con las URLs de sus APIs si se planea implementarlos.

### 6.4 — Aviso de tier `scale` sin Groq
**Qué:** Tier `scale` muestra "Groq LLaMA 3" en la UI pero no hay implementación.
**Cómo:** Si no se implementa Groq, cambiar la etiqueta del tier a "Claude Haiku Batch (escala)". Si sí se implementa, añadir el code path en `callClaude()`.

### 6.5 — SaaS views
**Qué:** Las 5 vistas SaaS son HTML vacío. Si no son parte del roadmap inmediato, ocultar los ítems del sidebar con `display:none` para no confundir a usuarios.

### Verificación Phase 6
- [ ] Cambiar idioma a English → labels principales de la UI cambian al inglés
- [ ] Vista Templates → muestra hooks guardados (no "Próximamente")
- [ ] KEY_MAP no tiene entradas sin implementación visible
- [ ] Tier `scale` no menciona Groq si no está implementado
- [ ] Sidebar no muestra ítems SaaS vacios

---

## Phase 7 — Hardening de seguridad básico (backend)
**Objetivo:** Proteger los endpoints de abuso gratuito.
**Archivo:** `_backend_tmp/main.py`
**Bump:** v4.38 → v4.39

### 7.1 — API key de acceso al backend
**Qué:** Todos los endpoints son públicos. Cualquiera con la URL puede generar videos y gastar los créditos de Railway + OpenAI.
**Cómo:** Añadir un header requerido `X-FAI-Key` en FastAPI con `Depends()`. La clave se configura via variable de entorno `FAI_SECRET_KEY`. El frontend la lee de localStorage `fai_backend_key` y la envía en cada fetch.

### 7.2 — Rate limiting básico
**Qué:** Sin límite de requests por IP.
**Cómo:** Instalar `slowapi` (compatible con FastAPI). Limitar `/generate` a 5 req/min por IP, `/tts` a 20 req/min.

### 7.3 — Limitar CORS a GitHub Pages
**Qué:** `allow_origins=["*"]` en línea 19. Cambiar a:
```python
allow_origins=[
  "https://clawlabsai.github.io",
  "http://localhost:3000",  # desarrollo local
]
```

### Verificación Phase 7
- [ ] `POST /generate` sin header `X-FAI-Key` → 401
- [ ] `POST /generate` con key correcta → funciona
- [ ] >5 requests a `/generate` en 1 min → 429
- [ ] `curl` desde origen no-permitido → CORS error en browser console

---

## Orden de ejecución recomendado

| # | Phase | Impacto usuario | Esfuerzo |
|---|---|---|---|
| 1 | Phase 1 — Bugs de lógica (tiers, score) | Alto | Bajo (index.html solo) |
| 2 | Phase 2 — AutoPilot pipeline completo | Muy alto | Medio |
| 3 | Phase 3 — Subtítulos + parámetros video | Alto | Medio (backend + frontend) |
| 4 | Phase 4 — YouTube OAuth PKCE | Alto | Medio-alto |
| 5 | Phase 7 — Hardening backend | Crítico (seguridad) | Bajo |
| 6 | Phase 5 — TikTok + Scheduler | Muy alto | Alto |
| 7 | Phase 6 — UX cleanup | Medio | Bajo |

---

## Anti-patrones a evitar

- ❌ No inventar endpoints del backend que no existan en main.py (consultar antes)
- ❌ No usar `response_type=token` para OAuth — es el patrón deprecado
- ❌ No poner tokens/keys en URL query params
- ❌ No usar `jobs[job_id]` sin verificar que la clave existe (KeyError)
- ❌ No llamar a `callClaude()` dentro de AutoPilot sin verificar `checkBudgetAlert()` primero
- ❌ No añadir dependencias a requirements.txt sin usarlas (ver yt-dlp/openai actuales)
- ❌ No hacer commits sin bumpar versión (`v4.XX` en title + logo-sub + `data['_version']`)

---

## Referencias rápidas

| Recurso | Ubicación |
|---|---|
| Backend main.py | `C:\Users\AI\Documents\ClaudeCode\CC_FacelessAI_V3\_backend_tmp\main.py` |
| Frontend SPA | `C:\Users\AI\Documents\ClaudeCode\CC_FacelessAI_V3\index.html` |
| Backend live | `https://facelessai-backend-production.up.railway.app` |
| Frontend live | `https://clawlabsai.github.io/facelessai/` |
| Railway token | En `.claude/settings.local.json` (env var `RAILWAY_TOKEN`) |
| `callClaude()` | index.html línea ~12562 |
| `runAutopilotCycle()` | index.html línea ~9199 |
| `publishToYouTube()` | index.html línea ~8991 |
| `generateVideoShop()` | index.html línea ~12077 (patrón de polling a copiar) |
| `generate_srt()` backend | main.py líneas 584–595 |
| `process_video()` backend | main.py líneas 292–403 |
| `TIER_CONFIG` | index.html líneas ~4976–4983 |
| YouTube OAuth docs | https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow#migrating-to-gis |
| TikTok Content API | https://developers.tiktok.com/doc/content-posting-api-get-started |
