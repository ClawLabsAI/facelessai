# FacelessAI — Architecture

## Shape

FacelessAI is a **single-file SPA**: everything (HTML, CSS, all JavaScript) lives in
`index.html` (~14k lines, ~900 KB). It is deployed as-is to GitHub Pages — the served file
**is** the source file. There is no framework and no required build step.

State lives in `localStorage` under `fai_*` keys; navigation toggles `.active` on `.view`
elements (all views stay in the DOM). Behavior is wired through inline `on*="globalFn()"`
handlers, so **global function names are part of the public contract** and must not be
renamed or dropped.

## Logical modules (within the one file)

These are conceptual groupings, not separate files. Use them as a map when editing.

| Concern | What it covers |
|---|---|
| **Shared helpers** | `setEl`/`setHTML`, `loadLS`/`saveLS`, `_memoLS` (memoized LS reads), `fetchWithTimeout` + the global fetch-timeout wrapper, `_diag` (gated diagnostics), `AppState` (state inspector), schema migrations (`runMigrations`). |
| **Navigation** | `nav(id)` + per-view on-show callbacks; `VIEWS`/`TITLES`. |
| **Pipeline** | `setPStep`, idea generation (`generateIdeasReal`), scripting (`generateScriptReal`), scoring, TTS, video, draft creation. |
| **Channels** | `getChannels`/`saveChannels`, `renderChannels`, edit-channel modal, per-channel stats (`getChannelStats`). |
| **Drafts** | `getDrafts`/`saveDrafts`/`addDraft` (createdAt normalization + 500-cap), `renderDrafts`. |
| **AutoPilot / Batch** | `runFullAutopilotCycle`, `apGenerateIdea/Script`, `apQuickScore`, interval scheduling, `generateBatch`. |
| **Scoring** | `apQuickScore` (deterministic local), `scoreHookFast`/`getSmartScore` (AI), score view. |
| **Analytics / Monetization** | `renderAnalytics`, tabs, profitability/niche calculators. |
| **AI integrations** | Anthropic, OpenAI/TTS, Pexels, HeyGen, D-ID, Runway, Pika, Kling, YouTube/TikTok OAuth + publish. |
| **Settings** | API keys (`KEY_MAP`, `loadKeys`/`saveKey`/`refreshSettingsDisplay`), tiers (`setActiveTier`, `TIERS`/`renderModels`), preferences. |

## Storage & migrations

- All persistence is `localStorage` `fai_*` keys. Read through `_memoLS`/dedicated getters
  (`getDrafts`, `getChannels`, `getAnalyticsLog`, `getAffiliates`, `getChannelStats`) which
  memoize by raw string and auto-invalidate on write.
- Schema version lives in `fai_schema_version`. To evolve stored data: bump
  `FAI_SCHEMA_VERSION` and add a `FAI_MIGRATIONS[n]` function. `runMigrations()` applies
  pending migrations once on load (a throwing migration is caught, never bricks startup).

## Build & deploy

- **Source `index.html` is canonical and directly deployable.** No build is required.
- `npm test` — static checks (syntax, duplicate functions, empty catches, deploy invariant).
- `npm run build` — **optional** minification via terser → `dist/index.html`
  (~13% smaller). Terser runs with `mangle:false` + `compress.toplevel:false` so the global
  handler names referenced by inline `on*=` attributes are never renamed or dropped.
- `npm run check:dist` — validates the artifact (style lints skipped; minified code legitimately
  strips comments). `scripts/verify-handlers.mjs` cross-checks that every inline-handler
  function still has a definition.
- CI: `.github/workflows/ci.yml` runs `npm test` on push/PR to `main`.

## Debugging

- `localStorage.setItem('fai_debug','1')` surfaces all swallowed errors (`_diag`) and
  `AppState.trace()` logs.
- `AppState.snapshot()` dumps the key mutable globals at any time.

## Known issues / future work

- **Dead inline handlers**: `loadTTStats`, `saveTTStats`, `analyzeTTPerformance`,
  `renderPublishQueue`, `applyNicheToChannel` are referenced by `onclick` but have no
  definition — those buttons throw if clicked. (Pre-existing; surfaced by
  `verify-handlers.mjs`.) Either implement or remove the buttons.
- **Real modularization (deferred)**: splitting into ES modules + a Vite build would enable
  tree-shaking/code-splitting, but changes the deploy model (built output instead of a raw
  file) and is a deliberate, separate project. The minify build above is the non-breaking
  interim win.
- **State management**: ~12 mutable globals are mutated from many sites. `AppState` is a
  read-only inspector foundation; a full getter/setter migration remains future work.
- **Key encryption**: keys are local-only (see Settings disclosure). Real at-rest encryption
  would require a user passphrase (opt-in, not yet implemented).
