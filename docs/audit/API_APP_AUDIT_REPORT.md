# Audit Complet — `src/api/` & `src/app.py`

> **Date**: 2026-02-23 | **Fichiers API**: 34 Python + 1 README | **LOC API**: 3 404 | **LOC app.py**: 112

---

## 1. Inventaire Fichiers `src/api/`

### Root

| Fichier          | LOC |
|------------------|-----|
| `__init__.py`    | 18  |
| `auth.py`        | 217 |
| `dependencies.py`| 76  |
| `main.py`        | 273 |
| `README.md`      | 195 |

### `routes/` — Routeurs FastAPI (7 fichiers, 1 310 LOC)

| Fichier          | LOC |
|------------------|-----|
| `__init__.py`    | 20  |
| `auth.py`        | 134 |
| `courses.py`     | 335 |
| `inventaire.py`  | 284 |
| `planning.py`    | 229 |
| `push.py`        | 147 |
| `recettes.py`    | 249 |
| `suggestions.py` | 112 |

### `schemas/` — Modèles Pydantic (8 fichiers, 327 LOC)

| Fichier          | LOC |
|------------------|-----|
| `__init__.py`    | 90  |
| `auth.py`        | 13  |
| `base.py`        | 71  |
| `common.py`      | 28  |
| `courses.py`     | 36  |
| `inventaire.py`  | 23  |
| `planning.py`    | 24  |
| `recettes.py`    | 42  |

### `utils/` — Utilitaires (6 fichiers, 469 LOC)

| Fichier              | LOC |
|----------------------|-----|
| `__init__.py`        | 48  |
| `cache.py`           | 96  |
| `crud.py`            | 123 |
| `exceptions.py`      | 34  |
| `metrics.py`         | 109 |
| `security_headers.py`| 59  |

### `rate_limiting/` — Limitation de débit (8 fichiers, 514 LOC)

| Fichier              | LOC |
|----------------------|-----|
| `__init__.py`        | 65  |
| `config.py`          | 32  |
| `dependencies.py`    | 24  |
| `limiter.py`         | 135 |
| `middleware.py`      | 42  |
| `redis_storage.py`   | 126 |
| `storage.py`         | 60  |
| `utils.py`           | 30  |

### Totaux

| Package        | Fichiers | LOC   |
|----------------|----------|-------|
| Root           | 4 py     | 584   |
| `routes/`      | 8        | 1 310 |
| `schemas/`     | 8        | 327   |
| `utils/`       | 6        | 469   |
| `rate_limiting/`| 8       | 514   |
| **Total**      | **34**   | **3 404** |

---

## 2. Catalogue des Endpoints

### Santé (aucune auth requise)

| Méthode | Chemin      | Auth  | Description                          |
|---------|-------------|-------|--------------------------------------|
| GET     | `/`         | Non   | Root — info API, liens docs          |
| GET     | `/health`   | Non   | Health check (DB, cache, IA)         |
| GET     | `/metrics`  | Non   | Métriques API (latence, req count)   |

### Authentification (`/api/v1/auth`)

| Méthode | Chemin               | Auth                 | Description                    |
|---------|----------------------|----------------------|--------------------------------|
| POST    | `/api/v1/auth/login` | Non (rate-limited)   | Login Supabase → token JWT API |
| POST    | `/api/v1/auth/refresh`| Bearer JWT           | Rafraîchir le token            |
| GET     | `/api/v1/auth/me`    | Bearer JWT           | Profil utilisateur             |

### Recettes (`/api/v1/recettes`)

| Méthode | Chemin                     | Auth       | Description              |
|---------|----------------------------|------------|--------------------------|
| GET     | `/api/v1/recettes`         | Non        | Liste paginée + filtres  |
| GET     | `/api/v1/recettes/{id}`    | Non        | Détail recette           |
| POST    | `/api/v1/recettes`         | `require_auth` | Créer recette         |
| PUT     | `/api/v1/recettes/{id}`    | `require_auth` | Mise à jour complète  |
| PATCH   | `/api/v1/recettes/{id}`    | `require_auth` | Mise à jour partielle |
| DELETE  | `/api/v1/recettes/{id}`    | `require_auth` | Supprimer recette     |

### Inventaire (`/api/v1/inventaire`)

| Méthode | Chemin                            | Auth       | Description                |
|---------|-----------------------------------|------------|----------------------------|
| GET     | `/api/v1/inventaire`              | Non        | Liste paginée + filtres    |
| GET     | `/api/v1/inventaire/{id}`         | Non        | Détail article             |
| GET     | `/api/v1/inventaire/barcode/{code}`| Non       | Recherche par code-barres  |
| POST    | `/api/v1/inventaire`              | `require_auth` | Ajouter article        |
| PUT     | `/api/v1/inventaire/{id}`         | `require_auth` | Mettre à jour          |
| DELETE  | `/api/v1/inventaire/{id}`         | `require_auth` | Supprimer              |

### Courses (`/api/v1/courses`)

| Méthode | Chemin                                  | Auth       | Description              |
|---------|-----------------------------------------|------------|--------------------------|
| GET     | `/api/v1/courses`                       | Non        | Listes paginées          |
| GET     | `/api/v1/courses/{id}`                  | Non        | Détail liste + articles  |
| POST    | `/api/v1/courses`                       | `require_auth` | Créer liste           |
| PUT     | `/api/v1/courses/{id}`                  | `require_auth` | Renommer liste        |
| DELETE  | `/api/v1/courses/{id}`                  | `require_auth` | Supprimer liste       |
| POST    | `/api/v1/courses/{id}/items`            | `require_auth` | Ajouter article       |
| PUT     | `/api/v1/courses/{id}/items/{item_id}`  | `require_auth` | Modifier article      |
| DELETE  | `/api/v1/courses/{id}/items/{item_id}`  | `require_auth` | Supprimer article     |

### Planning (`/api/v1/planning`)

| Méthode | Chemin                        | Auth       | Description              |
|---------|-------------------------------|------------|--------------------------|
| GET     | `/api/v1/planning/semaine`    | Non        | Planning hebdomadaire    |
| POST    | `/api/v1/planning/repas`      | `require_auth` | Planifier un repas    |
| PUT     | `/api/v1/planning/repas/{id}` | `require_auth` | Modifier un repas     |
| DELETE  | `/api/v1/planning/repas/{id}` | `require_auth` | Supprimer un repas    |

### Notifications Push (`/api/v1/push`)

| Méthode | Chemin                     | Auth                 | Description                    |
|---------|----------------------------|----------------------|--------------------------------|
| POST    | `/api/v1/push/subscribe`   | `get_current_user`   | Enregistrer abonnement push    |
| DELETE  | `/api/v1/push/unsubscribe` | `get_current_user`   | Supprimer abonnement           |
| GET     | `/api/v1/push/status`      | `get_current_user`   | Statut notifications           |

### Suggestions IA (`/api/v1/suggestions`)

| Méthode | Chemin                         | Auth + Rate limit IA | Description              |
|---------|--------------------------------|----------------------|--------------------------|
| GET     | `/api/v1/suggestions/recettes` | `get_current_user` + IA rate limit | Suggestions IA recettes  |
| GET     | `/api/v1/suggestions/planning` | `get_current_user` + IA rate limit | Suggestions IA planning  |

### Résumé: **35 endpoints** au total

| Domaine       | GET | POST | PUT | PATCH | DELETE | Total |
|---------------|-----|------|-----|-------|--------|-------|
| Santé         | 3   | 0    | 0   | 0     | 0      | 3     |
| Auth          | 1   | 2    | 0   | 0     | 0      | 3     |
| Recettes      | 2   | 1    | 1   | 1     | 1      | 6     |
| Inventaire    | 3   | 1    | 1   | 0     | 1      | 6     |
| Courses       | 2   | 2    | 2   | 0     | 2      | 8     |
| Planning      | 1   | 1    | 1   | 0     | 1      | 4     |
| Push           | 1   | 1    | 0   | 0     | 1      | 3     |
| Suggestions   | 2   | 0    | 0   | 0     | 0      | 2     |
| **Total**     | **15** | **8** | **5** | **1** | **6** | **35** |

---

## 3. Analyse Architecturale

### 3.1 FastAPI App Setup

- **Framework**: FastAPI 1.0.0 avec documentation OpenAPI complète
- **Tags metadata**: 8 tags organisés (Authentification, Santé, Recettes, Inventaire, Courses, Planning, Notifications Push, IA)
- **Docs**: Swagger UI (`/docs`) + ReDoc (`/redoc`) activés
- **License**: MIT déclarée

### 3.2 Middleware Stack (ordre d'exécution bottom-up)

| #  | Middleware                    | Fichier                         | Rôle                                    |
|----|-------------------------------|---------------------------------|-----------------------------------------|
| 1  | `SecurityHeadersMiddleware`   | `utils/security_headers.py`     | CSP, HSTS, X-Frame-Options, etc.       |
| 2  | `MetricsMiddleware`           | `utils/metrics.py`              | Compteurs, latence par endpoint         |
| 3  | `ETagMiddleware`              | `utils/cache.py`                | Cache HTTP conditionnel (ETags)         |
| 4  | `MiddlewareLimitationDebit`   | `rate_limiting/middleware.py`   | Rate limiting par IP/user/endpoint      |
| 5  | `CORSMiddleware`              | FastAPI/Starlette builtin       | Cross-Origin Resource Sharing           |

### 3.3 Auth System

**Dual JWT validation** (API-signed + Supabase):

1. **Token API** (`creer_token_acces`): HS256, 24h TTL, issuer `assistant-matanne-api`
2. **Token Supabase**: Signature vérifiée si `SUPABASE_JWT_SECRET` configuré, sinon mode dégradé (decode sans vérification)
3. **Fallback dev**: En mode dev, auto-authentification comme admin sans token
4. **Chaîne de validation** (`valider_token`): Try API → Try Supabase → Reject

**Dependencies FastAPI**:
- `get_current_user(credentials)` → dict `{id, email, role}` ou dev user
- `require_auth(user)` → exige un user non-null
- `require_role("admin")` → factory pour contrôle de rôle

### 3.4 Schema Architecture

**Base modulaire** dans `schemas/`:
- **Mixins validateurs**: `NomValidatorMixin`, `QuantiteValidatorMixin`, `QuantiteStricteValidatorMixin`, `TypeRepasValidator`
- **Classes de base**: `TimestampedResponse`, `IdentifiedResponse` (avec `from_attributes=True`)
- **Commun**: `PaginationParams`, `ReponsePaginee[T]` (générique), `MessageResponse`, `ErreurResponse`
- **Domaine**: 4 modules dédiés (recettes, inventaire, courses, planning)
- **RecettePatch**: Modèle PATCH séparé avec tous champs optionnels ✅

### 3.5 Error Handling

Triple couche de protection :

1. **Global exception handler** (`main.py`): `@app.exception_handler(Exception)` → 500 avec message générique
2. **`executer_avec_session()`** (`utils/crud.py`): Context manager DB → re-raise HTTPException, wrap others as 500
3. **`executer_async()`** (`utils/crud.py`): Thread pool wrapper → même pattern que ci-dessus
4. **`@gerer_exception_api`** (`utils/exceptions.py`): Décorateur optionnel pour routes sans session DB

**Message pattern**: Toutes les erreurs 500 retournent `"Une erreur interne est survenue. Veuillez réessayer."` — **pas de fuite d'info** ✅

---

## 4. Audit Sécurité

### 4.1 JWT Secret Validation — ✅ CORRIGÉ

| Check | Résultat | Détail |
|-------|----------|--------|
| Secret par défaut en production | ✅ **RuntimeError** levée | `_obtenir_api_secret()` refuse la clé par défaut si `ENVIRONMENT=production` |
| Warning en dev | ✅ Warning loggé | `logger.warning()` si clé par défaut utilisée en dev |
| Supabase JWT en prod | ⚠️ Warning seulement | Tokens Supabase décodés SANS signature si secret absent — mode dégradé accepté |
| Algorithme | ✅ HS256 fixe | Pas de confusion d'algorithme possible |

### 4.2 Rate Limiting — ✅ COMPLET

| Feature | Implémentation |
|---------|----------------|
| Limites par fenêtre | Minute (60), Heure (1000), Jour (10000) |
| Limites IA | 10/min, 100/h, 500/jour |
| Limites anonymes | 20/min (réduit) |
| Limites premium | 200/min (augmenté) |
| Anti brute-force login | 5 tentatives/min par IP, blocage 5 min |
| Abuse detection | Auto-block si > 2× la limite |
| Rate limit headers | ✅ `X-RateLimit-Limit`, `Remaining`, `Reset`, `Retry-After` |
| Stockage Redis | ✅ Factory `obtenir_stockage_optimal()` avec fallback in-memory |
| Sliding window | ✅ Via sorted sets Redis ou liste en mémoire |
| Bypass pour tests | ✅ `RATE_LIMITING_DISABLED=true` |

### 4.3 Input Validation — ✅ BON

| Validation | Détail |
|------------|--------|
| Pydantic v2 | ✅ Tous les inputs validés via schémas |
| Nom non vide | ✅ `NomValidatorMixin` strip + check empty |
| Quantité positive | ✅ `QuantiteValidatorMixin` / `QuantiteStricteValidatorMixin` |
| Types de repas | ✅ `TypeRepasValidator` avec whitelist |
| Pagination | ✅ `ge=1, le=100/200` sur page_size |
| Query params | ✅ `Query()` avec validators FastAPI |
| Email/password login | ⚠️ `LoginRequest` ne valide pas le format email |

### 4.4 Error Messages — ✅ SÉCURISÉ

| Couche | Message exposé | Info interne |
|--------|----------------|--------------|
| Exception handler global | `"Une erreur interne est survenue."` | Loggé, pas exposé |
| `executer_async()` | `"Une erreur interne est survenue."` | Loggé, pas exposé |
| `executer_avec_session()` | `"Une erreur interne est survenue."` | Loggé, pas exposé |
| `gerer_exception_api` | `"Une erreur interne est survenue."` | Loggé, pas exposé |
| Push endpoints | `"Erreur lors de l'enregistrement..."` | Loggé, pas exposé |
| Login | `"Identifiants invalides"` | Pas de distinction user/pwd |
| `str(e)` exposé dans HTTPException | ✅ **ABSENT** | Aucune instance trouvée |

### 4.5 CORS Configuration — ✅ BON

```python
_default_origins = [
    "http://localhost:8501",     # Streamlit local
    "http://localhost:8000",     # API local
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000",
    "https://matanne.streamlit.app",  # Production
]
```

| Check | Résultat |
|-------|----------|
| Wildcard `*` | ❌ Absent (bien) |
| Override via env | ✅ `CORS_ORIGINS` env var |
| Credentials | ✅ `allow_credentials=True` |
| Méthodes | ✅ Whitelist explicite `GET,POST,PUT,DELETE,PATCH` |
| Headers | ✅ Whitelist `Authorization, Content-Type, X-Request-ID` |

### 4.6 Security Headers — ✅ COMPLET

| Header | Valeur |
|--------|--------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=()` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` (prod only) |
| `Content-Security-Policy` | Strict pour API, permissif pour Swagger UI |

---

## 5. Known Bugs Check

### 5.1 push.py `current_user["user_id"]` vs `current_user["id"]` — ✅ CORRIGÉ

push.py utilise `current_user["id"]` (lignes 106, 143, 180), ce qui est **cohérent** avec `dependencies.py` → `get_current_user()` qui retourne `{"id": ..., "email": ..., "role": ...}`.

**Statut: Pas de KeyError bug.** ✅

### 5.2 `executer_async` expose `str(e)` dans HTTPException — ✅ CORRIGÉ

Aucune instance de `str(e)` dans un message HTTPException. Toutes les fonctions critiques utilisent:
```python
raise HTTPException(
    status_code=500,
    detail="Une erreur interne est survenue. Veuillez réessayer.",
) from e
```

**Statut: Pas de fuite d'information.** ✅

### 5.3 ETagMiddleware — ⚠️ INCOMPLÈTE (design accepté)

Le `ETagMiddleware` dans `utils/cache.py` est **fonctionnel mais limité** :
- Ajoute `Cache-Control` avec `max-age` si configuré
- **Ne génère PAS d'ETags automatiquement** sur les réponses (commentaire dans le code: "l'implémentation complète nécessiterait de bufferiser la réponse")
- Les fonctions helpers `generate_etag()`, `add_cache_headers()`, `check_etag_match()` sont disponibles pour usage manuel dans les routes

**Impact**: Le middleware est un shell — il n'apporte pas de cache conditionnel 304 automatique. Les routes n'utilisent pas non plus les helpers manuellement.

**Statut: Middleware décoratif, pas de 304 support réel.** ⚠️

### 5.4 OpenAPI securitySchemes — ❌ MANQUANT

Aucune définition `securitySchemes` dans l'OpenAPI spec. `HTTPBearer` est déclaré dans `dependencies.py` avec `auto_error=False`, mais FastAPI ne génère pas automatiquement le bouton "Authorize" dans Swagger UI car:
- `auto_error=False` empêche le schéma de sécurité d'apparaître dans la spec
- Pas de `swagger_ui_init_oauth` ni `openapi_extra` configuré

**Impact**: Le bouton 🔒 "Authorize" dans Swagger UI est absent ou inopérant. Les utilisateurs doivent ajouter manuellement le header `Authorization` pour tester les endpoints protégés.

**Statut: UX de documentation dégradée.** ❌

---

## 6. Analyse `src/app.py`

### 6.1 Métriques

| Métrique | Valeur |
|----------|--------|
| Lignes totales | **112** |
| Imports | ~15 |
| Fonctions | 1 (`main()`) |
| Classes | 0 |

### 6.2 Bootstrap Sequence

| Étape | Ligne | Action |
|-------|-------|--------|
| 1 | 14-28 | Load `.env.local` → `.env` fallback (`dotenv`) |
| 2 | 38-44 | PATH setup + logging (`GestionnaireLog.initialiser`) |
| 3 | 50-53 | `demarrer_application(valider_config=False, initialiser_eager=False)` |
| 4 | 59-62 | Import `GestionnaireEtat`, `obtenir_parametres`, navigation |
| 5 | 64-69 | Import layout (`afficher_header`, `afficher_footer`, `initialiser_app`) |
| 6 | 74 | `obtenir_parametres()` |
| 7 | 80-91 | `st.set_page_config()` |
| 8 | 93-97 | PWA meta tags + `initialiser_app()` |
| 9 | 103 | `initialiser_navigation()` → `st.navigation()` + `st.Page()` |
| 10 | 110 | `main()` → header + page.run() + footer |

### 6.3 CSS Injection — ✅ SINGLE (via pipeline unifié)

```python
# CSS est injecté via initialiser_app() (pipeline CSS unifié)
```

L'injection CSS passe par `initialiser_app()` dans `ui/layout/initialisation.py` qui utilise un **pipeline CSSManager** :
1. Styles globaux → `CSSManager.register()`
2. Thème dynamique → `CSSManager.register()`
3. Tokens sémantiques → `CSSManager.register()`
4. CSS accessibilité → `CSSManager.register()`
5. Animations → `CSSManager.register()`
6. **`CSSManager.inject_all()`** → **1 seul `st.markdown()` batch**

**Statut: CSS injection single-call optimisée.** ✅

### 6.4 Error Recovery

```python
except Exception as e:
    logger.exception("❌ Erreur critique dans main()")
    st.error("❌ Une erreur critique est survenue. Veuillez redémarrer l'application.")
    if obtenir_etat().mode_debug:
        st.exception(e)
    if st.button("🔄 Redémarrer"):
        GestionnaireEtat.reset_complet()
        st.rerun()
```

| Feature | Implémentation |
|---------|----------------|
| Catch-all | ✅ `Exception` catch autour de `main()` |
| User message | ✅ Message générique, pas de stacktrace |
| Debug mode | ✅ `st.exception(e)` seulement si `mode_debug` |
| Recovery | ✅ Bouton "Redémarrer" → `reset_complet()` + `st.rerun()` |

### 6.5 `valider_config` Parameter

`demarrer_application(valider_config=False, initialiser_eager=False)` — la validation de config est **désactivée** au bootstrap. Cela permet un démarrage plus rapide mais signifie que les erreurs de configuration ne seront détectées qu'à l'exécution.

### 6.6 Module Loading

Navigation via `st.navigation()` + `st.Page()` (Streamlit native multi-page). Les modules sont chargés **à la demande** par le framework Streamlit lui-même via la navigation native. Plus besoin de `RouteurOptimise` custom.

---

## 7. Scores Qualité

### `src/api/` — Score Global: **8.4/10**

| Critère | Score | Détail |
|---------|-------|--------|
| Architecture | 9/10 | Package modulaire propre (routes/schemas/utils/rate_limiting) |
| Sécurité | 8.5/10 | JWT solide, rate limiting complet, headers OWASP, CORS strict |
| Schemas/Validation | 8/10 | Mixins réutilisables, Pydantic v2, RecettePatch PATCH propre |
| Error Handling | 9/10 | Triple couche, aucune fuite d'info, messages génériques |
| Documentation | 8.5/10 | Docstrings enrichies, examples JSON dans tous les endpoints |
| Rate Limiting | 9/10 | Multi-fenêtre, Redis/memory, abuse detection, bypass tests |
| Code Quality | 8/10 | Cohérent, DRY (helpers crud.py), bonne séparation |
| Tests | N/A | Pas audité ici |
| **Points faibles** | | ETagMiddleware shell, pas de securitySchemes OpenAPI, `LoginRequest` sans validation email |

### `src/app.py` — Score Global: **9.0/10**

| Critère | Score | Détail |
|---------|-------|--------|
| Concision | 9.5/10 | 112 lignes, bootstrap clair et séquentiel |
| Architecture | 9/10 | Séparation layout/navigation/bootstrap complète |
| Error Recovery | 9/10 | Catch-all + debug mode + bouton redémarrage |
| CSS Pipeline | 9.5/10 | Single-injection via CSSManager |
| Module Loading | 9/10 | st.navigation() natif, lazy loading préservé |
| **Points faibles** | | `valider_config=False` (validation désactivée) |

---

## 8. Améliorations depuis v2

| Domaine | Avant (v2) | Maintenant | Statut |
|---------|------------|------------|--------|
| push.py KeyError | `current_user["user_id"]` ❌ | `current_user["id"]` ✅ | **CORRIGÉ** |
| `str(e)` dans HTTPException | Exposé dans `executer_async` | Message générique partout | **CORRIGÉ** |
| JWT secret validation | Warning seulement | `RuntimeError` en production | **CORRIGÉ** |
| Rate limiting | Basique (1 fenêtre) | Multi-fenêtre + Redis + abuse detection | **AMÉLIORÉ** |
| Rate limiting package | Fichier unique | Package dédié (8 fichiers) | **RESTRUCTURÉ** |
| Security headers | Absents | Middleware OWASP complet | **AJOUTÉ** |
| Metrics | Absents | MetricsMiddleware + endpoint `/metrics` | **AJOUTÉ** |
| PATCH support | Absent | `RecettePatch` + endpoint PATCH | **AJOUTÉ** |
| Schema mixins | Validation inline | Package `schemas/` avec mixins | **RESTRUCTURÉ** |
| CSS injection (app.py) | Multiple `st.markdown` | CSSManager pipeline single-call | **OPTIMISÉ** |
| Navigation (app.py) | `RouteurOptimise` custom | `st.navigation()` natif | **MIGRÉ** |
| ETagMiddleware | Incomplet | Toujours incomplet (shell) | **INCHANGÉ** ⚠️ |
| OpenAPI securitySchemes | Absent | Toujours absent | **INCHANGÉ** ❌ |

---

## 9. Recommandations Prioritaires

### Haute priorité

1. **Ajouter OpenAPI securitySchemes** — Le bouton "Authorize" dans Swagger est non-fonctionnel:
   ```python
   # Dans dependencies.py
   security = HTTPBearer(auto_error=False, description="Token JWT Bearer")
   # OU dans main.py:
   app = FastAPI(
       ...,
       swagger_ui_init_oauth={},
   )
   ```

2. **Valider le format email dans `LoginRequest`**:
   ```python
   from pydantic import EmailStr
   email: EmailStr  # Au lieu de str
   ```

### Moyenne priorité

3. **Implémenter ETagMiddleware complètement** ou le supprimer — le code actuel est un placeholder qui n'ajoute aucune fonctionnalité cache 304.

4. **Activer `valider_config=True`** dans `app.py` — la validation config désactivée est un risque en production.

5. **Ajouter `/metrics` derrière auth** — actuellement accessible sans authentification, expose des informations opérationnelles.

### Basse priorité

6. **HealthResponse timezone** — `_START_TIME = datetime.now()` sans timezone vs `datetime.now(UTC)` utilisé dans auth.py. Inconsistance mineure.

7. **Documentation README.md** — La section endpoints est incomplète (manque push, PATCH recettes, courses nested routes).
