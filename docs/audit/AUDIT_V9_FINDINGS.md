# Audit V9 - Résultats et Actions

## Résumé des corrections appliquées

### ✅ Corrections effectuées

1. **Gamification importe Streamlit dans services** (🔴 Haute)
   - **Fichier**: `src/services/core/gamification.py`
   - **Correction**: Remplacé `import streamlit as st` par l'abstraction `SessionStorage` de `src.core.storage`
   - **Impact**: Le service peut maintenant être testé sans Streamlit et respecte l'architecture découplée

2. **football_compat.py duplication** (🟡 Moyenne)
   - **Fichier supprimé**: `src/services/jeux/_internal/football_helpers.py` (219 LOC)
   - **Raison**: Fichier non utilisé (aucun import trouvé), code dupliqué avec `football_compat.py`
   - **Impact**: Code base nettoyé, réduction de 219 LOC de dette technique

3. **Garmin + Google Calendar sans @avec_resilience** (🟡 Moyenne)
   - **Fichiers modifiés**:
     - `src/services/famille/calendrier/google_auth.py`: Ajout `@avec_resilience` sur `handle_google_callback`
     - `src/services/famille/calendrier/google_tokens.py`: Ajout `@avec_resilience` sur `_refresh_google_token`
   - **Note**: Le service Garmin avait déjà `@avec_resilience` sur ses méthodes HTTP

---

## Items clarifiés (non-issues)

### Cache deprecated non supprimé (🟢 Basse - Faux positif)

- **Fichier**: `src/core/caching/cache.py` (203 LOC, pas 163)
- **Status**: Ce n'est PAS du dead code
- **Raison**: C'est une façade rétro-compatible documentée comme deprecated mais **activement utilisée** par:
  - `src/core/state/manager.py`
  - `src/modules/parametres/cache.py`
  - `src/modules/jeux/utils.py`
  - `src/services/cuisine/planning/global_planning.py`
  - `src/services/cuisine/recettes/service.py`
  - Et plusieurs autres fichiers
- **Recommandation**: Maintenir jusqu'à migration complète vers `@avec_cache`

### Fichiers parasites dans modules (🟢 Basse - Faux positif)

- **Recherche effectuée**: Aucun fichier `.txt` ou `.log` trouvé dans `src/modules/`
- **Status**: Les fichiers mentionnés n'existent pas ou ont déjà été supprimés

---

## Items à traiter ultérieurement (hors scope)

### 🔴 Priorité haute

1. **DB direct dans modules UI** (~52 appels `obtenir_contexte_db` dans `src/modules/`)
   - **Fichiers impactés**:
     - `src/modules/maison/utils.py` (8 appels)
     - `src/modules/maison/entretien/__init__.py` (4 appels)
     - `src/modules/maison/jardin_zones.py` (3 appels)
     - `src/modules/maison/projets/__init__.py` (5 appels)
     - `src/modules/maison/meubles/crud.py` (6 appels)
     - `src/modules/maison/eco_tips/crud.py` (5 appels)
     - `src/modules/maison/energie/data.py` (1 appel)
     - `src/modules/maison/jardin/__init__.py` (3 appels)
     - `src/modules/planning/cockpit_familial.py` (8 appels)
   - **Refactoring recommandé**: Créer des services dédiés et utiliser le pattern `@avec_session_db`

2. **Tests skippés (~20 restants)** - Voir pytest markers
3. **Coverage fichiers 0%** - barcode, rapports/generation, plan_jardin
4. **Déployer SQL sur Supabase** - ⬛ En attente

### 🟡 Priorité moyenne

1. **Double héritage BaseService + BaseAIService fragile** (3 services)
   - **Fichiers**:
     - `src/services/cuisine/planning/planning_ia_mixin.py`
     - `src/services/cuisine/courses/service.py`
   - **Recommandation**: Migrer vers composition plutôt qu'héritage multiple

2. **@cached_fragment sous-utilisé** - De nombreux graphiques Plotly lourds sans cache fragment

3. **KeyNamespace manquant dans cuisine/**
   - Tous les modules cuisine utilisent déjà KeyNamespace ✓
   - Vérification: `batch_cooking`, `inventaire`, `planificateur_repas`, `courses`, `recettes` - tous ont KeyNamespace

4. **error_boundary manquant dans ~30% des modules**
   - `src/modules/accueil/` - déjà corrigé (dashboard.py, resume_hebdo.py ont error_boundary)
   - `src/modules/famille/` - déjà corrigé (activites, suivi_perso, weekend, jules ont error_boundary)
   - `src/modules/parametres/` - utilise BaseModule qui gère les erreurs via render_tabs
   - **Status**: La plupart des modules critiques sont déjà protégés

### 🟢 Priorité basse

1. **VAPID keys generation** - ⬛ En attente (notifications push)
2. **Reconnaissance vocale** - ⬛ Planifié pour V10

---

## Statistiques de couverture

- **Tests en échec**: 48 (pre-existing - DB mocks, JulesAI)
- **Tests skippés**: ~20 restants (vs 322 initialement)

---

## Prochaines étapes recommandées

1. Créer des tickets pour le refactoring DB → services
2. Traiter les 48 tests en échec par lots (DB mocks puis JulesAI)
3. Planifier la migration SQL vers Supabase
4. Considérer la migration des héritages multiples vers la composition
