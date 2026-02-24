# Audit Complet — `src/ui/` Package

**Date**: 2026-02-23  
**Scope**: `src/ui/` — Design System & UI Layer  
**Format**: Inventaire + Analyse qualitative + Vérification ROADMAP Phase 5

---

## 1. Inventaire Complet des Fichiers

### Racine `src/ui/`

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 216 |
| `a11y.py` | 288 |
| `animations.py` | 224 |
| `fragments.py` | 453 |
| `keys.py` | 204 |
| `registry.py` | 122 |
| `theme.py` | 319 |
| `tokens.py` | 245 |
| `tokens_semantic.py` | 214 |
| `utils.py` | 34 |
| `README.md` | 185 |
| **Sous-total racine** | **2,504** |

### `components/` (12 fichiers .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 149 |
| `alertes.py` | 36 |
| `atoms.py` | 395 |
| `charts.py` | 122 |
| `data.py` | 157 |
| `dynamic.py` | 106 |
| `filters.py` | 241 |
| `forms.py` | 203 |
| `layouts.py` | 121 |
| `metrics.py` | 169 |
| `metrics_row.py` | 248 |
| `streaming.py` | 235 |
| `system.py` | 127 |
| **Sous-total** | **2,309** |

### `engine/` (2 fichiers .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 33 |
| `css.py` | 432 |
| **Sous-total** | **465** |

### `feedback/` (5 fichiers .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 61 |
| `progress_v2.py` | 306 |
| `results.py` | 139 |
| `spinners.py` | 71 |
| `toasts.py` | 115 |
| **Sous-total** | **692** |

### `grid/` (1 fichier .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 512 |
| **Sous-total** | **512** |

### `integrations/` (2 fichiers .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 23 |
| `google_calendar.py` | 155 |
| **Sous-total** | **178** |

### `layout/` (6 fichiers .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 17 |
| `footer.py` | 13 |
| `header.py` | 39 |
| `initialisation.py` | 93 |
| `sidebar.py` | 118 |
| `styles.py` | 227 |
| **Sous-total** | **507** |

### `state/` (2 fichiers .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 35 |
| `url.py` | 410 |
| **Sous-total** | **445** |

### `system/` (1 fichier .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 18 |
| **Sous-total** | **18** |

### `tablet/` (6 fichiers .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 52 |
| `config.py` | 19 |
| `kitchen.py` | 173 |
| `styles.py` | 391 |
| `timer.py` | 197 |
| `widgets.py` | 163 |
| **Sous-total** | **995** |

### `testing/` (2 fichiers .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 26 |
| `visual_regression.py` | 292 |
| **Sous-total** | **318** |

### `views/` (11 fichiers .py)

| Fichier | LOC |
|---------|-----|
| `__init__.py` | 90 |
| `authentification.py` | 181 |
| `design_system.py` | 203 |
| `historique.py` | 68 |
| `import_recettes.py` | 128 |
| `jeux.py` | 74 |
| `meteo.py` | 136 |
| `notifications.py` | 194 |
| `pwa.py` | 103 |
| `sauvegarde.py` | 81 |
| `synchronisation.py` | 80 |
| **Sous-total** | **1,338** |

### Totaux

| Catégorie | Fichiers .py | LOC |
|-----------|:------------:|----:|
| Racine UI | 10 | 2,319 |
| components/ | 13 | 2,309 |
| engine/ | 2 | 465 |
| feedback/ | 5 | 692 |
| grid/ | 1 | 512 |
| integrations/ | 2 | 178 |
| layout/ | 6 | 507 |
| state/ | 2 | 445 |
| system/ | 1 | 18 |
| tablet/ | 6 | 995 |
| testing/ | 2 | 318 |
| views/ | 11 | 1,338 |
| **TOTAL** | **61** | **10,096** |

(+ README.md = 185 LOC, docs/ folder empty)

---

## 2. Analyse par Subpackage

### `tokens.py` — Score: 9/10

- **LOC**: 245 | **Exports**: 9 classes/fonctions
- `Couleur` (48 members), `Espacement`, `Rayon`, `Typographie`, `Ombre`, `Transition`, `ZIndex`, `Variante` — all `StrEnum`
- `obtenir_couleurs_variante()`, `gradient()`, `gradient_subtil()`
- Excellent: Single source of truth for raw design values
- Minor: One hardcoded `"#ffffff"` in `obtenir_couleurs_variante` for accent variant

### `tokens_semantic.py` — Score: 9/10

- **LOC**: 214 | **Exports**: `Sem` enum, `injecter_tokens_semantiques()`
- 26 CSS custom properties (`var(--sem-*)`) with full light/dark mappings
- Proper `prefers-color-scheme: dark` media query for auto mode
- Excellent abstraction layer between raw tokens and component use

### `theme.py` — Score: 8/10

- **LOC**: 319 | **Exports**: `ModeTheme`, `DensiteAffichage`, `Theme`, `obtenir_theme`, `definir_theme`, `appliquer_theme`, `afficher_selecteur_theme`
- Full light/dark/auto with CSS generation
- Dark mode CSS applies `.stApp`, sidebar, inputs, expanders overrides
- Density support (compact/normal/confortable)
- Minor: `afficher_selecteur_theme` could use `@ui_fragment`

### `a11y.py` — Score: 8.5/10

- **LOC**: 288 | **Exports**: `A11y` class (9 static methods)
- `sr_only()`, `sr_only_html()`, `live_region()`, `attrs()`, `landmark()`, `ratio_contraste()`, `verifier_aa()`, `verifier_aaa()`, `injecter_css()`
- WCAG 2.1 contrast ratio calculation, skip links, `.sr-only` CSS
- Focus-visible, prefers-reduced-motion included
- Weakness: Only adopted in 2 files outside itself (`design_system.py`, `initialisation.py`)

### `animations.py` — Score: 8.5/10

- **LOC**: 224 | **Exports**: `Animation` enum (12 animations), `animer()`, `injecter_animations()`
- 12 @keyframes, stagger children, hover micro-interactions
- Proper `prefers-reduced-motion: no-preference` wrapper
- Retrocompat aliases (`.animate-in`)

### `registry.py` — Score: 8/10

- **LOC**: 122 | **Exports**: `ComponentMeta`, `composant_ui`, `obtenir_catalogue`, `rechercher_composants`, `lister_composants`
- Decorator-based auto-registration with introspection
- Signature, source file, line, tags capture
- Well designed for auto-generated docs

### `fragments.py` — Score: 8.5/10

- **LOC**: 453 | **Exports**: `ui_fragment`, `auto_refresh`, `isolated`, `lazy`, `with_loading`, `cached_fragment`, `FragmentGroup`
- Proper `st.fragment` feature detection with fallback
- `run_every` support check for auto_refresh (Streamlit 1.36+)
- `FragmentGroup` for coordinated multi-fragment refresh
- Minor: skeleton `_render_skeleton()` uses hardcoded `#f0f0f0`/`#e0e0e0`

### `keys.py` — Score: 8/10

- **LOC**: 204 | **Exports**: `KeyNamespace`, `widget_keys`
- Scoped key generation with namespace prefixes preventing collision
- Sub-namespace support, collision detection in debug mode
- Thread-safe singleton registry

### `components/` — Score: 8/10

- **Files**: 13 | **LOC**: 2,309
- All components use `@composant_ui` decorator (36 registrations total)
- XSS-safe via `echapper_html()` on all user text
- ARIA attributes (`role`, `aria-label`) present on atoms
- Pure `_html()` functions for testability (`badge_html`, `boite_info_html`, `boule_loto_html`)
- `StyleSheet.create_class()` for deduplication
- Categories: atoms(7), data(5), filters(3), forms(4), layouts(2), metrics(7), streaming(2), system(3), alertes(1), charts(2)

### `engine/` — Score: 9/10

- **Files**: 2 | **LOC**: 465
- Unified CSS engine: blocks, atomic classes, keyframes
- MD5-based deduplication, session_state hash invalidation
- Batch injection (single `st.markdown` per render cycle)
- Compat aliases: `CSSManager`, `StyleSheet` → `CSSEngine`
- File loading from `static/css/`

### `feedback/` — Score: 7.5/10

- **Files**: 5 | **LOC**: 692
- `progress_v2.py` (306 LOC) — `SuiviProgression` with `st.status`
- `results.py` — Result-to-Streamlit bridging
- `toasts.py` — Notification helpers
- `spinners.py` — Smart spinner with token usage
- Good overall but `progress_v2.py` is dense

### `grid/` — Score: 8/10

- **Files**: 1 | **LOC**: 512
- Composable layout system: `Row`, `Grid`, `Stack`, `Gap`
- Context manager API (`with Row(2) as r:`)
- Responsive breakpoints, helper shortcuts
- All in single `__init__.py` — could be split

### `layout/` — Score: 7.5/10

- **Files**: 6 | **LOC**: 507
- `initialisation.py` — Bootstrap pipeline (CSS injection chain)
- `styles.py` — Global CSS with legacy var bridge to semantic tokens
- `sidebar.py`, `header.py`, `footer.py` — App shell
- See Design System Health section for styles.py analysis

### `state/` — Score: 8/10

- **Files**: 2 | **LOC**: 445
- `url.py` (410 LOC) — Deep linking via `st.query_params`
- `URLState`, `sync_to_url`, `get_url_param`, `set_url_param`
- URL-synced widgets: `tabs_with_url`, `selectbox_with_url`, `pagination_with_url`

### `tablet/` — Score: 7/10

- **Files**: 6 | **LOC**: 995
- Kitchen mode with step-by-step recipe display
- Timer with progress bar
- Touch-optimized widgets (large buttons, grids)
- `styles.py` (391 LOC) — Heavy CSS, some hardcoded fallback colors
- Uses `var(--sem-*)` with fallbacks but 2 pure hardcoded hex in gradient

### `testing/` — Score: 8/10

- **Files**: 2 | **LOC**: 318
- `SnapshotTester` with hash-based comparison
- `UPDATE_SNAPSHOTS=1` env var for updates
- `assert_html_contains`, `assert_html_not_contains`, `normalize_html`
- Well-designed for CI snapshot regression

### `integrations/` — Score: 6.5/10

- **Files**: 2 | **LOC**: 178
- Only Google Calendar integration
- Minimal — could be external

### `views/` — Score: 6.5/10

- **Files**: 11 | **LOC**: 1,338
- `design_system.py` — Interactive component catalog (uses registry)
- Several views still use inline `style=` with hardcoded CSS
- Some bypass design system (see Section 7)

### `system/` — Score: 5/10

- **Files**: 1 | **LOC**: 18
- Thin re-export wrapper over `engine` (`StyleSheet`, `styled`, `css_class`)
- Could be removed — adds indirection without value

---

## 3. Design System Health Check

### Token Import Adoption

| Source | Files Importing | Who |
|--------|:---:|-----|
| `tokens.py` (`Couleur`, etc.) | **15** | atoms, charts, metrics, metrics_row, layouts, filters (via components), spinners, system, header, styles, theme, design_system, notifications, pwa, synchronisation, jeux |
| `tokens_semantic.py` (`Sem`) | **3** | theme.py, initialisation.py, metrics_row.py |

**Analysis**: Raw tokens (`Couleur`) are well adopted (15 files). Semantic tokens (`Sem`) have very low direct adoption (only 3 files). Most components reference `Couleur.XXX` directly rather than `Sem.XXX` vars.

### Hardcoded Color Strings (outside tokens.py/tokens_semantic.py)

| File | Count | Context |
|------|:-----:|---------|
| `a11y.py` | 2 | Used as `var(--sem-*)` **fallbacks** — acceptable |
| `fragments.py` | 1 | `#f0f0f0`/`#e0e0e0` in skeleton loader — should use tokens |
| `components/layouts.py` | 1 | Minor |
| `components/metrics_row.py` | 2 | Minor |
| `engine/css.py` | 1 | In docstring example |
| `tablet/styles.py` | 2 | `#FF6B6B`/`#ee5a5a` in gradient — **NOT** in `var()` fallback |

**Verdict**: 9 instances in non-token files. Most are `var(--sem-*, fallback)` patterns (acceptable). **2 true violations** in `tablet/styles.py` (hardcoded timer gradient) and **1** in `fragments.py` (skeleton).

### `layout/styles.py` — Legacy `:root` CSS Vars

**Status**: `:root` variables are present BUT they are **bridges** to semantic tokens, not duplicates:
```css
--accent: var(--sem-interactive, #4CAF50);
--text-primary: var(--sem-on-surface, #212529);
--bg-surface: var(--sem-surface, #ffffff);
```

The Couleur constants serve as fallbacks. The variables resolve to `--sem-*` values at runtime. **This is correct architecture** — legacy CSS vars cascade to semantic tokens for dark mode.

**Verdict**: No duplication bug. `.badge-success`, `.metric-card`, etc. use `var(--sem-*)` with Couleur fallbacks.

### Dark Mode — Is It Functional?

| Component | Status |
|-----------|--------|
| Semantic token injection (`injecter_tokens_semantiques()`) | ✅ Light/dark/auto mappings complete |
| Theme CSS overrides (`.stApp`, sidebar, inputs) | ✅ Generated in `theme.py` |
| Toggle in UI (`afficher_selecteur_theme()`) | ✅ Accessible via Paramètres > Affichage |
| Global styles bridge (`styles.py`) | ✅ `var(--sem-*, fallback)` pattern |
| Auto mode (`prefers-color-scheme`) | ✅ Media query injection |
| `components/atoms.py` badge styles | ⚠️ Uses raw `Couleur.XXX` not `Sem.XXX` — hardcoded in light mode |
| `tablet/styles.py` | ⚠️ 2 hardcoded gradients won't adapt to dark |
| `fragments.py` skeleton | ⚠️ Hardcoded `#f0f0f0` won't adapt |

**Verdict**: Dark mode **infrastructure is complete** (tokens, injection, theme, toggle). **Partially functional** at component level — global layout adapts, but individual atoms (`badge`, `carte_metrique`) use raw `Couleur` values that don't respond to dark mode. Full dark mode requires migrating components from `Couleur.XXX` to `Sem.XXX`.

---

## 4. ROADMAP Phase 5 Verification

### 4.1 Dark Mode Toggle in `parametres/affichage.py`

**Status**: ✅ **DONE**

`affichage.py` imports `afficher_selecteur_theme` from `src.ui.theme` and calls it in the `afficher_display_config()` function (line 22-25). The toggle offers Clair/Sombre/Auto modes with accent color and density options.

### 4.2 Design System Module Registered in Navigation + Router

**Status**: ✅ **DONE**

- Module file exists at `src/modules/design_system.py` (218 LOC) with `app()` function
- Registered in `MODULE_REGISTRY` at `src/core/lazy_loader.py` line 271: `"design_system": {"path": "src.modules.design_system"}`
- View file at `src/ui/views/design_system.py` (203 LOC) with interactive catalog

### 4.3 Visual Tests (`test_ui_snapshots.py`)

**Status**: ✅ **DONE**

- Test file at `tests/test_ui_snapshots.py` (261 LOC)
- 3 test classes: `TestBadgeSnapshots` (11 tests), `TestBoiteInfoSnapshots` (7 tests), `TestBouleLotoSnapshots` (6 tests)
- Plus `TestSnapshotUtilities` (3 tests) — **27 total test cases**
- Uses pure functions: `badge_html()`, `boite_info_html()`, `boule_loto_html()`
- `SnapshotTester` with hash comparison, `UPDATE_SNAPSHOTS=1` support
- `assert_html_contains`, `assert_html_not_contains`, `normalize_html`
- Tests cover: all 6 variantes, custom colors, XSS escape, ARIA attributes, snapshot stability, cross-component isolation

### 4.4 PWA Icons in `static/icons/`

**Status**: ✅ **DONE**

8 icons generated at standard PWA sizes:
- `icon-72x72.png`
- `icon-96x96.png`
- `icon-128x128.png`
- `icon-144x144.png`
- `icon-152x152.png`
- `icon-192x192.png`
- `icon-384x384.png`
- `icon-512x512.png`

### 4.5 ReactiveServiceMixin Stale Docstring in `circuit_breaker.py`

**Status**: ✅ **DONE** — No matches found for "ReactiveServiceMixin" in `src/core/resilience/` or `src/core/ai/circuit_breaker.py`. The stale docstring has been removed.

### Phase 5 Summary

| Item | Status |
|------|--------|
| Dark Mode toggle | ✅ |
| Design System module | ✅ |
| Visual regression tests | ✅ (27 tests) |
| PWA icons | ✅ (8 sizes) |
| Stale docstring removed | ✅ |

**Phase 5: 5/5 complete**

---

## 5. Component Catalog (`@composant_ui` Registry)

**Total registered**: 36 components across 8 categories

### atoms (7 components)
| Component | File | Tags |
|-----------|------|------|
| `badge` | atoms.py | badge, label |
| `etat_vide` | atoms.py | empty, placeholder |
| `carte_metrique` | atoms.py | metric, kpi |
| `separateur` | atoms.py | divider, separator |
| `boite_info` | atoms.py | info, callout |
| `boule_loto` | atoms.py | loto, ball, jeux |
| `alerte_stock` | alertes.py | alert, stock |

### filters (3 components)
| Component | File | Tags |
|-----------|------|------|
| `afficher_barre_filtres` | filters.py | — |
| `afficher_recherche` | filters.py | recherche |
| `afficher_filtres_rapides` | filters.py | — |

### forms (4 components)
| Component | File | Tags |
|-----------|------|------|
| `champ_formulaire` | forms.py | — |
| `barre_recherche` | forms.py | — |
| `panneau_filtres` | forms.py | — |
| `filtres_rapides` | forms.py | — |

### data (5 components)
| Component | File | Tags |
|-----------|------|------|
| `pagination` | data.py | pagination, navigation |
| `ligne_metriques` | data.py | — |
| `boutons_export` | data.py | — |
| `tableau_donnees` | data.py | table, dataframe |
| `barre_progression` | data.py | progress, bar |

### layouts (2 components)
| Component | File | Tags |
|-----------|------|------|
| `disposition_grille` | layouts.py | grid, layout |
| `carte_item` | layouts.py | card, item |

### metrics (7 components)
| Component | File | Tags |
|-----------|------|------|
| `carte_metrique_avancee` | metrics.py | — |
| `widget_jules_apercu` | metrics.py | jules, famille, dashboard |
| `widget_meteo_jour` | metrics.py | — |
| `afficher_metriques_row` | metrics_row.py | — |
| `afficher_stats_cards` | metrics_row.py | — |
| `afficher_kpi_banner` | metrics_row.py | — |
| `afficher_progress_metrics` | metrics_row.py | — |

### streaming (2 components)
| Component | File | Tags |
|-----------|------|------|
| `streaming_response` | streaming.py | — |
| `streaming_section` | streaming.py | — |

### system (3 components)
| Component | File | Tags |
|-----------|------|------|
| `indicateur_sante_systeme` | system.py | — |
| `afficher_sante_systeme` | system.py | health, monitoring |
| `afficher_timeline_activites` | system.py | — |

---

## 6. Accessibility Audit

### `A11y` Exports

| Method | Type | Purpose |
|--------|------|---------|
| `injecter_css()` | CSS injection | `.sr-only`, skip-link, focus-visible |
| `sr_only(texte)` | Streamlit output | Screen-reader-only text |
| `sr_only_html(texte)` | Pure HTML | Returns SR-only span |
| `live_region(message)` | Streamlit output | ARIA live region announcements |
| `attrs(role, label, ...)` | Pure HTML | Generate ARIA attribute strings |
| `landmark(html, role, label)` | Pure HTML | Wrap content in ARIA landmark |
| `ratio_contraste(fg, bg)` | Utility | WCAG 2.1 contrast ratio calc |
| `verifier_aa(fg, bg)` | Utility | Check WCAG AA (≥4.5) |
| `verifier_aaa(fg, bg)` | Utility | Check WCAG AAA (≥7.0) |

### Adoption in Components

| Where | What |
|-------|------|
| `atoms.py` | `role="status"`, `aria-label` on all badges/cartes; `role="note"` on boite_info; `role="img"` on boule_loto; `role="group"` on carte_metrique; `aria-hidden="true"` on decorative icons |
| `layout/initialisation.py` | `A11y.injecter_css()` called at startup |
| `views/design_system.py` | `A11y.injecter_css()` called |
| `layout/styles.py` | `*:focus-visible` styles, `prefers-reduced-motion: reduce` |
| `animations.py` | Full `prefers-reduced-motion: no-preference` wrap |

### Gaps

- **Low direct adoption**: Only 2 non-self files import `A11y` class
- **components/**: Most components add ARIA attrs manually (inline `role=`, `aria-label=`), not via `A11y.attrs()` helper
- **views/**: No ARIA landmarks, no `sr_only()` usage
- **contrast checks**: Available but never called in production code  
- **skip-link**: CSS is injected but no `<a class="skip-link">` is rendered anywhere

**Score: 6/10** — Good infrastructure, weak adoption beyond atoms.

---

## 7. Views Package — Design System Bypass Analysis

### Files Using Inline CSS

| File | Inline `style=` | Hardcoded Colors | Design System Used? |
|------|:---:|:---:|:---:|
| `notifications.py` | 8 instances | `rgba(255,255,255,0.3)` | ❌ Heavy inline CSS, no tokens |
| `synchronisation.py` | 3 instances | None direct | ⚠️ Partial, some inline |
| `pwa.py` | 2 instances | None | ⚠️ JS button styles inline |
| `jeux.py` | 2 instances | Uses `Couleur.NOTIFICATIONS_BADGE` | ✅ Token colors |
| `design_system.py` | 0 | None | ✅ Uses registry + tokens |
| `authentification.py` | — | — | ✅ |
| `meteo.py` | — | — | ✅ |
| `historique.py` | — | — | ✅ |
| `import_recettes.py` | — | — | ✅ |
| `sauvegarde.py` | — | — | ✅ |

**Major offenders**: `notifications.py` — Push permission UI is built entirely with inline CSS and doesn't use design tokens at all. `synchronisation.py` and `pwa.py` have moderate inline CSS.

**Verdict**: 3/10 views bypass the design system to varying degrees. Most egregious is `notifications.py` which constructs full UI components with raw style attributes.

---

## 8. Fragments Analysis

### Decorators Available

| Decorator | Purpose | Streamlit Requirement |
|-----------|---------|----------------------|
| `@ui_fragment` | Basic isolated fragment | st.fragment (1.33+) |
| `@auto_refresh(seconds=N)` | Periodic auto-refresh | st.fragment + run_every (1.36+) |
| `@isolated` | Alias for `@ui_fragment` | 1.33+ |
| `@lazy(condition=...)` | Conditional loading with placeholder/skeleton | 1.33+ |
| `@with_loading(message=...)` | Loading state wrapper | None (always works) |
| `@cached_fragment(ttl=N)` | `st.cache_data` + `st.fragment` combo | 1.33+ |
| `FragmentGroup` | Coordinate multiple fragments | 1.33+ |

### Adoption Across `src/modules/`

| Metric | Value |
|--------|:-----:|
| Files using fragment decorators | **49** |
| Total decorator usages | **107** |
| `@ui_fragment` usages | ~95 |
| `@auto_refresh` usages | ~3 |
| `@cached_fragment` usages | ~0 |
| `@lazy` / `@lazy_fragment` usages | ~0 (referenced in framework example only) |

### Usage Breakdown by Module Domain

| Domain | Files | Decorator Usages |
|--------|:-----:|:----------------:|
| `parametres/` | 7 | 7 |
| `maison/` (jardin, entretien, charges, depenses) | 10 | ~25 |
| `utilitaires/` (barcode, rapports, notifications_push) | 6 | ~15 |
| `jeux/` | 3 | ~5 |
| `cuisine/` | 8+ | ~20 |
| `famille/` | 5+ | ~15 |
| `_framework/` (examples) | 2 | ~3 |
| Other | ~8 | ~17 |

**Analysis**: `@ui_fragment` dominates usage (89%). Advanced patterns (`@auto_refresh`, `@cached_fragment`, `@lazy`) are barely used outside of `notifications_push.py`. `FragmentGroup` is defined but no adoption found in modules.

---

## 9. Overall Scores Summary

| Subpackage | Files | LOC | Score |
|------------|:-----:|:---:|:-----:|
| `tokens.py` | 1 | 245 | 9/10 |
| `tokens_semantic.py` | 1 | 214 | 9/10 |
| `engine/` | 2 | 465 | 9/10 |
| `registry.py` | 1 | 122 | 8/10 |
| `fragments.py` | 1 | 453 | 8.5/10 |
| `animations.py` | 1 | 224 | 8.5/10 |
| `a11y.py` | 1 | 288 | 8.5/10 |
| `theme.py` | 1 | 319 | 8/10 |
| `components/` | 13 | 2,309 | 8/10 |
| `grid/` | 1 | 512 | 8/10 |
| `keys.py` | 1 | 204 | 8/10 |
| `state/` | 2 | 445 | 8/10 |
| `testing/` | 2 | 318 | 8/10 |
| `layout/` | 6 | 507 | 7.5/10 |
| `feedback/` | 5 | 692 | 7.5/10 |
| `tablet/` | 6 | 995 | 7/10 |
| `views/` | 11 | 1,338 | 6.5/10 |
| `integrations/` | 2 | 178 | 6.5/10 |
| `system/` | 1 | 18 | 5/10 |
| **OVERALL** | **61** | **10,096** | **7.8/10** |

---

## 10. Critical Issues & Recommendations

### Must Fix

1. **`Sem` adoption gap**: Only 3 files use `Sem.*` tokens. Components (`atoms.py`, `metrics.py`) use hardcoded `Couleur.XXX` values that break dark mode. Migrate badge styles, carte_metrique, boite_info to use `var(--sem-*)` CSS properties.

2. **`notifications.py` inline CSS**: Completely bypasses design system. Refactor to use tokens + `StyleSheet`/`CSSEngine`.

3. **`fragments.py` skeleton**: Replace `#f0f0f0`/`#e0e0e0` with `Sem.SURFACE_ALT`/`Sem.BORDER_SUBTLE`.

### Should Fix

4. **`system/` package**: Only 18 LOC re-exporting from `engine/`. Consider removing and importing directly from `engine/`.

5. **`tablet/styles.py`** hardcoded gradients: Replace `#FF6B6B`/`#ee5a5a` with `Couleur.TIMER_BG_START`/`Couleur.TIMER_BG_END` references.

6. **A11y adoption**: Add `A11y.attrs()` usage in views. Add a rendered skip-link element. Use `A11y.live_region()` for toast notifications.

7. **Advanced fragments**: Promote `@cached_fragment` and `@lazy` usage in heavy modules (cuisine, planning).

### Nice to Have

8. **`grid/__init__.py`**: 512 LOC in a single file — split into `row.py`, `grid.py`, `stack.py`, `shortcuts.py`.

9. **README.md outdated**: References `hooks.py` and `html_builder.py` which don't exist in the current file tree.

10. **Component test coverage**: Only atoms have pure `_html()` functions for snapshot testing. Add `_html()` variants for `carte_metrique_avancee`, `alerte_stock`, etc.

---

*Report generated from complete analysis of 61 Python files (10,096 LOC) in `src/ui/`.*
