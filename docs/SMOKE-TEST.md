# FacelessAI — Smoke test end-to-end

Validación manual de los flujos que dependen de APIs reales (lo que el QA de UI no puede
comprobar). Marca cada casilla. Tiempo estimado: **~10–15 min**.

> Antes de empezar: abre la **consola del navegador** (F12) y ejecuta
> `localStorage.setItem('fai_debug','1')` — así verás cualquier error que la app capture
> en silencio. Y `AppState.snapshot()` te muestra el estado interno en cualquier momento.

---

## 0. Pre-flight — ¿qué profundidad quieres probar?

| Nivel | Qué valida | Claves necesarias | Coste aprox. |
|------|------------|-------------------|--------------|
| **A. Mínimo (texto)** | Idea → Score → Guion con IA real | Solo **Anthropic** | ~$0.01 |
| **B. + Audio** | Lo anterior + voz TTS | Anthropic + **OpenAI** (o ElevenLabs) | ~$0.02 |
| **C. Completo (MP4)** | Vídeo final descargable | A/B + **Pexels** + **Backend URL** (TTS/render) | ~$0.05–0.15 |

> Si solo quieres confirmar que "la IA responde de verdad", el **Nivel A** basta y cuesta
> casi nada. El vídeo MP4 (Nivel C) requiere tu backend corriendo.

---

## 1. Configuración (Settings ⚙️)

- [ ] Pega tu **Anthropic API key** y pulsa **Probar** → debe decir "OK / válida".
- [ ] (Nivel B) Pega **OpenAI** (o ElevenLabs) y **Probar**.
- [ ] (Nivel C) Pega **Pexels** y **Probar**; configura **Backend URL** y pulsa **Probar** (debe responder el `/health`).
- [ ] La etiqueta de cabecera pasa a **"✓ N/4 keys configuradas"** (verde).
- [ ] **Recarga la página** y vuelve a Settings → las keys siguen marcadas como guardadas (persistencia OK).

**Si falla:** "Key inválida" = clave mal copiada o sin saldo. El backend sin responder = URL incorrecta o servicio caído.

---

## 2. Tier de modelos (⚡ Modelos IA)

- [ ] Elige un tier para la prueba. **Recomendado: ECONÓMICO** (Claude Haiku + OpenAI TTS) para abaratar el test.
- [ ] Al pulsar la tarjeta, aparece **"✓ ACTIVO"** sobre ella y el badge de cabecera cambia.
- [ ] ⚠️ **No uses GRATIS** salvo que tengas **Ollama** corriendo en `localhost:11434` (si no, las llamadas de IA fallarán con un aviso claro — eso es esperado).

---

## 3. Crear un canal (Mis canales)

- [ ] **+ Crear canal** → nombre (ej. "QA Test"), nicho (Finanzas), idioma (ES), voz.
- [ ] **Crear** → aparece la tarjeta del canal y el badge del sidebar sube a 1.
- [ ] La tarjeta del canal **no** muestra errores (resaltado de canal activo correcto).

---

## 4. Pipeline — el flujo central (Pipeline IA)

Con el canal seleccionado (verás su contexto en el Paso 0):

### Paso 1 — Ideas
- [ ] **🤖 Generar con Claude** → el botón pasa a "⏳ Generando..." y en unos segundos aparecen **varias ideas reales** (no de ejemplo).
- [ ] Selecciona una idea (se resalta).

### Paso 2 — Score IA
- [ ] La idea seleccionada aparece arriba ("IDEA SELECCIONADA").
- [ ] **🤖 Analizar con Claude** → devuelve un **score numérico + métricas** reales.

### Paso 3 — Guion
- [ ] **🤖 Generar con Claude** → escribe un **guion completo** coherente con la idea.
- [ ] Pulsa **✏️ Editar**, cambia una palabra, **💾 Guardar** → el cambio persiste (toast "Script guardado").

### Paso 4 — Voz + Vídeo
- [ ] (Nivel B) **Generar audio** → produce un archivo de voz reproducible.
- [ ] (Nivel C) **Buscar clips** (Pexels) trae vídeos verticales; **Generar MP4** (backend) → al terminar, botón **⬇ Descargar MP4** funcional.
- [ ] (Sin backend) este paso avisará de que falta backend — comportamiento esperado.

### Paso 5 — Exportar
- [ ] Se rellena el resumen del vídeo y se **guarda como borrador** (toast de confirmación).

**Si falla en pasos 1–3:** mira la consola. "Configura tu Anthropic API key" = key no detectada. Timeout a 30s = red lenta o API caída. JSON parse error = respuesta del modelo malformada (reintenta).

---

## 5. Borrador → aprobación (Borradores)

- [ ] El borrador del pipeline aparece en la lista con su canal y score.
- [ ] **Aprobar** → cambia a estado aprobado (color verde).
- [ ] Recarga la página → el borrador **sigue ahí** con su estado (persistencia).

---

## 6. AutoPilot (opcional, 🤖 AutoPilot)

- [ ] Ajusta umbral/intervalo y **Guardar** → recarga y confirma que se mantienen.
- [ ] **▶ Ejecutar ciclo** con un canal activo → el log muestra pasos reales (idea→score→guion) y crea un borrador `source: autopilot`.

---

## 7. Scheduler + Dashboard

- [ ] Un borrador aprobado y auto-programado aparece en **📅 Scheduler** con fecha/hora.
- [ ] En **Dashboard**, los contadores ("Vídeos este mes", "Coste IA") reflejan la actividad de la prueba (el coste IA debe ser > $0 tras las llamadas reales).

---

## 8. Persistencia global (la prueba de fuego)

- [ ] Tras todo lo anterior, **cierra y reabre el navegador** (no solo recargar).
- [ ] Canales, borradores, keys y tier siguen ahí → confirma que nada vive solo en memoria.

---

## Toolkit de depuración

| Acción | Comando en consola |
|--------|--------------------|
| Ver errores capturados | `localStorage.setItem('fai_debug','1')` (luego reproduce el fallo) |
| Ver estado interno | `AppState.snapshot()` |
| Ver borradores guardados | `JSON.parse(localStorage.fai_drafts)` |
| Ver log de coste IA | `JSON.parse(localStorage.fai_analytics)` |
| Resetear todo (¡borra datos!) | `localStorage.clear()` y recargar |

---

## Criterio de "completo de verdad"

✅ Si **Nivel A** pasa entero → la IA de texto funciona end-to-end (el corazón del producto).
✅ Si **Nivel C** pasa → produces y descargas un MP4 real → producto completo.
⚠️ Cualquier paso que falle: anota el mensaje de consola y el paso exacto — con eso se diagnostica en minutos.
