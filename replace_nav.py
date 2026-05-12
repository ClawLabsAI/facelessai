import sys

content = open('index.html', 'r', encoding='utf-8').read()

nav_start = content.index('<nav class="nav">')
nav_end   = content.index('</nav>') + len('</nav>')

new_nav = """<nav class="nav">

    <!-- INICIO -->
    <div class="nsl">Inicio</div>
    <div class="ni active" data-view="dashboard">
      <svg viewBox="0 0 16 16" fill="currentColor"><rect x="1" y="1" width="6" height="6" rx="1"/><rect x="9" y="1" width="6" height="6" rx="1"/><rect x="1" y="9" width="6" height="6" rx="1"/><rect x="9" y="9" width="6" height="6" rx="1"/></svg>Dashboard
    </div>
    <div class="ni" data-view="channels">
      <svg viewBox="0 0 16 16" fill="currentColor"><circle cx="5" cy="5" r="2.5"/><circle cx="11" cy="5" r="2.5"/><circle cx="8" cy="11" r="2.5"/></svg>Canales<span class="nb nbg">3</span>
    </div>
    <div class="ni" data-view="drafts">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="1" width="12" height="14" rx="2"/><line x1="5" y1="5" x2="11" y2="5"/><line x1="5" y1="8" x2="11" y2="8"/><line x1="5" y1="11" x2="8" y2="11"/></svg>Borradores<span class="nb nba" id="drafts-nav-badge">3</span>
    </div>

    <!-- CREAR -->
    <div class="nsl" style="margin-top:6px" data-section="crear" onclick="toggleNavSection(this)">Crear<span class="nsl-ch">▾</span></div>
    <div class="ni" data-view="pipeline">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="3" width="14" height="10" rx="2"/><line x1="5" y1="3" x2="5" y2="13"/><line x1="11" y1="3" x2="11" y2="13"/></svg>Pipeline
    </div>
    <div class="ni" data-view="trends">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="1 12 5 7 9 9 13 3 15 3"/><circle cx="13" cy="3" r="1.5" fill="currentColor" stroke="none"/></svg>Tendencias<span class="nb nbr">5\U0001f525</span>
    </div>
    <div class="ni" data-view="score">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="7"/><path d="M8 4v4l3 3"/></svg>Score IA
    </div>
    <div class="ni" data-view="url2video">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 3H3a2 2 0 00-2 2v6a2 2 0 002 2h3M10 3h3a2 2 0 012 2v6a2 2 0 01-2 2h-3M5 8h6"/></svg>URL → Vídeo
    </div>
    <div class="ni" data-view="templates">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="1" width="14" height="10" rx="2"/><line x1="5" y1="14" x2="11" y2="14"/><line x1="8" y1="11" x2="8" y2="14"/></svg>Plantillas<span class="nb nba">12</span>
    </div>
    <div class="ni" data-view="clone">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="4" width="10" height="11" rx="2"/><path d="M5 4V3a2 2 0 012-2h6a2 2 0 012 2v10a2 2 0 01-2 2h-1"/></svg>Clonar canal
    </div>
    <div class="ni" data-view="reuse">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 8a7 7 0 0014 0M15 8a7 7 0 00-14 0"/><polyline points="12 5 15 8 12 11"/><polyline points="4 5 1 8 4 11"/></svg>Reutilizar
    </div>

    <!-- AUTOMATIZAR -->
    <div class="nsl" style="margin-top:6px" data-section="automacion" onclick="toggleNavSection(this)">Automatizar<span class="nsl-ch">▾</span></div>
    <div class="ni" data-view="autopilot">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="3"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.41 1.41M11.54 11.54l1.41 1.41M11.54 3.05l-1.41 1.41M3.05 11.54l1.41 1.41"/></svg>AutoPilot<span class="nb nbg" id="ap-nav-badge">ON</span>
    </div>
    <div class="ni" data-view="scheduler">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="3" width="14" height="12" rx="1"/><path d="M1 7h14M5 1v4M11 1v4"/></svg>Scheduler
    </div>
    <div class="ni" data-view="clipping">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 3l10 10M13 3L3 13"/><circle cx="4" cy="4" r="2"/><circle cx="12" cy="12" r="2"/></svg>Canales Clipping
    </div>
    <div class="ni" data-view="clippipeline">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="7"/><polygon points="6,5 12,8 6,11"/></svg>Pipeline Clipping
    </div>
    <div class="ni" data-view="cliplibrary">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="3" width="14" height="11" rx="1"/><circle cx="5.5" cy="7.5" r="1.5"/><path d="M1 12l3.5-3 3 2.5 3-4 4.5 4.5"/></svg>Mis Clips
    </div>

    <!-- TIKTOK SHOP -->
    <div class="nsl" style="margin-top:6px" data-section="tiktokshop" onclick="toggleNavSection(this)">TikTok Shop<span class="nsl-ch">▾</span></div>
    <div class="ni" data-view="tiktokshop">
      <svg viewBox="0 0 16 16" fill="currentColor"><path d="M9 2a1 1 0 000 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L13 5.414V8a1 1 0 002 0V3a1 1 0 00-1-1H9z"/><path d="M3 5a2 2 0 00-2 2v6a2 2 0 002 2h6a2 2 0 002-2v-3a1 1 0 10-2 0v3H3V7h3a1 1 0 000-2H3z"/></svg>Canales Shop<span class="nb" style="background:#ff004f20;color:#ff004f;border:1px solid #ff004f44;font-size:9px;padding:1px 5px;border-radius:99px;font-family:monospace">NEW</span>
    </div>
    <div class="ni" data-view="tiktokproduct">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="12" height="10" rx="2"/><path d="M5 3V2a1 1 0 011-1h4a1 1 0 011 1v1M8 7v4M6 9h4"/></svg>Pipeline Producto
    </div>
    <div class="ni" data-view="tiktokauto">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 3L3 8l4 2 2 4 4-10z"/></svg>AutoPost Shop
    </div>

    <!-- PERSONAJES IA -->
    <div class="nsl" style="margin-top:6px" data-section="influencer" onclick="toggleNavSection(this)">Personajes IA<span class="nsl-ch">▾</span></div>
    <div class="ni" data-view="influencer">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="5" r="3"/><path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6"/></svg>Mis personajes<span id="influencer-nav-badge" class="nbadge" style="display:none"></span>
    </div>
    <div class="ni" data-view="influencer-contenido">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H2v12h12V2z"/><path d="M5 6h6M5 9h4"/></svg>Contenido IA
    </div>
    <div class="ni" data-view="influencer-video">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="5,3 14,8 5,13"/></svg>Vídeo IA<span class="tag" style="font-size:9px;padding:1px 5px;margin-left:4px;background:var(--bdim);color:var(--purple);border:none">ULTRA</span>
    </div>

    <!-- INTELIGENCIA -->
    <div class="nsl" style="margin-top:6px" data-section="inteligencia" onclick="toggleNavSection(this)">Inteligencia<span class="nsl-ch">▾</span></div>
    <div class="ni" data-view="spychannels">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="6" cy="6" r="4"/><path d="M10 10l4 4"/><path d="M6 3v1M6 9v1M3 6h1M9 6h1"/></svg>Espía de Canales<span class="tag" style="font-size:9px;padding:1px 5px;margin-left:4px;background:#fee2e2;color:var(--red);border:none">NEW</span>
    </div>
    <div class="ni" data-view="affiliation">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 1l1.5 3 3.5.5-2.5 2.5.5 3.5L8 9l-3 1.5.5-3.5L3 4.5 6.5 4z"/></svg>Afiliados<span class="nb" style="background:#f472b620;color:#f472b6;border:1px solid #f472b640;font-size:9px;padding:1px 5px;border-radius:99px;margin-left:4px">NEW</span>
    </div>
    <div class="ni" data-view="analytics">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="1,12 5,7 8,9 11,4 15,6"/></svg>Analytics<span class="nb" style="background:#f472b620;color:#f472b6;border:1px solid #f472b640;font-size:9px;padding:1px 5px;border-radius:99px;margin-left:4px">NEW</span>
    </div>
    <div class="ni" data-view="monetization">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="8" y1="1" x2="8" y2="15"/><path d="M11 4H6.5a2.5 2.5 0 000 5h3a2.5 2.5 0 010 5H5"/></svg>Monetización<span class="nb nbg">$1.2K</span>
    </div>

    <!-- SISTEMA -->
    <div class="nsl" style="margin-top:6px" data-section="sistema" onclick="toggleNavSection(this)">Sistema<span class="nsl-ch">▾</span></div>
    <div class="ni" data-view="models">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="1" width="14" height="10" rx="2"/><line x1="5" y1="14" x2="11" y2="14"/><line x1="8" y1="11" x2="8" y2="14"/></svg>Modelos IA
    </div>
    <div class="ni" data-view="budget">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="7"/><path d="M8 4v4l3 3"/></svg>Presupuesto
    </div>
    <div class="ni" data-view="settings">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="2.5"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.05 3.05l1.41 1.41M11.54 11.54l1.41 1.41M11.54 3.05l-1.41 1.41M3.05 11.54l1.41 1.41"/></svg>Configuración<span class="nb nba" id="settings-badge" style="display:none">!</span>
    </div>

    <!-- SaaS (hidden) -->
    <div style="display:none">
      <div class="ni" data-view="saas-users">Usuarios</div>
      <div class="ni" data-view="saas-billing">Facturación</div>
      <div class="ni" data-view="saas-plans">Planes</div>
      <div class="ni" data-view="saas-admin">Admin</div>
      <div class="ni" data-view="saas-onboarding">Onboarding</div>
    </div>

  </nav>"""

result = content[:nav_start] + new_nav + content[nav_end:]
open('index.html', 'w', encoding='utf-8').write(result)
print('OK - nav replaced, file size:', len(result))
