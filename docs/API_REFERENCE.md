# ðŸ“¡ API Reference â€” Assistant Matanne

Documentation complÃ¨te de l'API REST FastAPI, organisÃ©e par modules fonctionnels et vÃ©rifiÃ©e pendant la phase 10.

## VÃ©rification Phase 10

- Audit code du 1 avril 2026: **622 handlers HTTP** dÃ©tectÃ©s dans `src/api/routes/*.py`.
- Le document reste organisÃ© par modules fonctionnels pour la lisibilitÃ©.
- RÃ©fÃ©rence stricte des schÃ©mas de rÃ©ponse: voir `docs/API_SCHEMAS.md` (auto-gÃ©nÃ©rÃ©).

## Vue d'ensemble

| Attribut             | Valeur                                            |
| -------------------- | ------------------------------------------------- |
| **Base URL**         | `http://localhost:8000`                           |
| **Documentation**    | `/docs` (Swagger), `/redoc` (ReDoc)               |
| **Version**          | v1 (`/api/v1/...`)                                |
| **Authentification** | JWT Bearer Token (`Authorization: Bearer <token>`) |
| **Rate Limiting**    | 60 req/min standard, 10 req/min IA                |
| **Pagination**       | Offset (`page`, `page_size`) + Cursor (`cursor`)  |

### RÃ©ponses communes

| Code | Description |
| ------ | ------------- |
| 200  | SuccÃ¨s |
| 201  | CrÃ©ation rÃ©ussie |
| 401  | Non authentifiÃ© |
| 403  | AccÃ¨s refusÃ© |
| 404  | Ressource introuvable |
| 422  | Erreur de validation |
| 429  | Rate limit dÃ©passÃ© |
| 500  | Erreur serveur |

### Pagination standard

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

## SantÃ© & Informations

| MÃ©thode | Path | Description |
| --------- | ------ | ------------- |
| GET | `/` | Informations sur l'API (nom, version, status) |
| GET | `/health` | Ã‰tat de l'API et de la base de donnÃ©es |

---

## ðŸ” Auth â€” `/api/v1/auth` (4 endpoints)

Authentification via Supabase Auth + JWT.

| MÃ©thode | Path | Description |
| --------- | ------ | ------------- |
| POST | `/auth/login` | Connexion (email, password) â†’ `TokenResponse` |
| POST | `/auth/register` | Inscription (email, password, nom) â†’ `TokenResponse` (201) |
| POST | `/auth/refresh` | RafraÃ®chit le token JWT |
| GET | `/auth/me` | Profil de l'utilisateur connectÃ© â†’ `UserInfoResponse` |

> **Mode dev** : `ENVIRONMENT=development` active l'auto-auth sans token.

### Login

```bash
curl -X POST /api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
```

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

---

## ðŸ½ï¸ Recettes â€” `/api/v1/recettes` (6 endpoints)

CRUD complet des recettes.

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/recettes` | `page`, `page_size`, `categorie?`, `search?` | Liste paginÃ©e avec filtres |
| GET | `/recettes/{id}` | â€” | DÃ©tail d'une recette |
| POST | `/recettes` | Body: `RecetteCreate` | CrÃ©e une recette |
| PUT | `/recettes/{id}` | Body: `RecetteCreate` | Remplacement complet |
| PATCH | `/recettes/{id}` | Body: `RecettePatch` | Mise Ã  jour partielle |
| DELETE | `/recettes/{id}` | â€” | Supprime une recette |

---

## ðŸ›’ Courses â€” `/api/v1/courses` (11 endpoints)

Listes de courses avec collaboration WebSocket.

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/courses` | `page`, `page_size`, `active_only=True` | Liste des listes de courses |
| POST | `/courses` | Body: `CourseListCreate` | CrÃ©e une liste (201) |
| GET | `/courses/{id}` | â€” | DÃ©tail avec articles |
| PUT | `/courses/{id}` | Body: `CourseListCreate` | Met Ã  jour le nom |
| DELETE | `/courses/{id}` | â€” | Supprime liste + articles |
| POST | `/courses/{id}/items` | Body: `CourseItemBase` | Ajoute un article (201) |
| PUT | `/courses/{id}/items/{item_id}` | Body: `CourseItemBase` | Met Ã  jour un article |
| DELETE | `/courses/{id}/items/{item_id}` | â€” | Supprime un article |
| GET | `/courses/{id}/export` | `group_by=categorie` | Export texte brut |
| POST | `/courses/{id}/checkout-items` | Body: `CheckoutCoursesRequest` | Checkout batch â†’ maj inventaire |
| POST | `/courses/{id}/scan-barcode-checkout` | Body: `ScanBarcodeCheckoutRequest` | Checkout via code-barres |

### WebSocket â€” `/api/v1/ws/courses/{liste_id}`

Collaboration temps rÃ©el sur les listes de courses.

**Connexion:**
```
ws://localhost:8000/api/v1/ws/courses/{liste_id}?user_id=abc123&username=Anne
```

| Param | Type | Description |
| ------- | ------ | ------------- |
| `liste_id` | `int` (path) | ID de la liste de courses |
| `user_id` | `str` (query, requis) | Identifiant utilisateur |
| `username` | `str` (query, dÃ©faut: "Anonyme") | Nom affichÃ© |

**Messages Client â†’ Serveur** (JSON, champ `action`) :

| Action | Champs | Description |
| -------- | -------- | ------------- |
| `item_added` | `item: {nom, quantite, unite}` | Article ajoutÃ© |
| `item_removed` | `item_id: int` | Article supprimÃ© |
| `item_checked` | `item_id: int, checked: bool` | Article cochÃ©/dÃ©cochÃ© |
| `item_updated` | `item_id: int, updates: {...}` | Article modifiÃ© |
| `list_renamed` | `new_name: str` | Liste renommÃ©e |
| `user_typing` | `typing: bool` | Indicateur de saisie |
| `ping` | â€” | Keep-alive |

**Messages Serveur â†’ Clients** (JSON, champ `type`) :

| Type | Champs | Description |
| ------ | -------- | ------------- |
| `sync` | `action, user_id, username, timestamp, ...data` | Broadcast d'une modification |
| `user_joined` | `user_id, username, timestamp` | Nouvel utilisateur connectÃ© |
| `user_left` | `user_id, username, timestamp` | Utilisateur dÃ©connectÃ© |
| `users_list` | `users: [{user_id, username, connected_at}]` | Liste des connectÃ©s (envoyÃ© Ã  la connexion) |
| `error` | `message: str` | Erreur (action inconnue) |
| `pong` | â€” | RÃ©ponse au ping |

Les modifications `item_added`, `item_removed`, `item_checked` et `list_renamed` sont persistÃ©es en base de donnÃ©es.

---

## ðŸ“¦ Inventaire â€” `/api/v1/inventaire` (6 endpoints)

Gestion des stocks alimentaires.

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/inventaire` | `page`, `page_size=50`, `categorie?`, `emplacement?`, `stock_bas?`, `peremption_proche?` | Liste avec filtres avancÃ©s |
| POST | `/inventaire` | Body: `InventaireItemCreate` | CrÃ©e un article |
| GET | `/inventaire/barcode/{code}` | â€” | Recherche par code-barres |
| GET | `/inventaire/{id}` | â€” | DÃ©tail article |
| PUT | `/inventaire/{id}` | Body: `InventaireItemUpdate` | Met Ã  jour (partiel via exclude_unset) |
| DELETE | `/inventaire/{id}` | â€” | Supprime |

---

## ðŸ“… Planning â€” `/api/v1/planning` (4 endpoints)

Planification des repas de la semaine.

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/planning/semaine` | `date_debut?` (ISO datetime) | Planning de la semaine |
| POST | `/planning/repas` | Body: `RepasCreate` | Planifie un repas (upsert) |
| PUT | `/planning/repas/{id}` | Body: `RepasCreate` | Met Ã  jour un repas |
| DELETE | `/planning/repas/{id}` | â€” | Supprime un repas |

---

## ðŸ¤– Suggestions IA â€” `/api/v1/suggestions` (2 endpoints)

Suggestions via Mistral AI (rate limitÃ© : 10 req/min).

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/suggestions/recettes` | `contexte="repas Ã©quilibrÃ©"`, `nombre=3` (1-10) | Suggestions recettes |
| GET | `/suggestions/planning` | `jours=7` (1-14), `personnes=4` (1-20) | Planning complet IA |

---

## ðŸ‘¨â€ðŸ‘©â€ðŸ‘§â€ðŸ‘¦ Famille â€” `/api/v1/famille` (37 endpoints)

### Contexte familial (1) â€” Phase M

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/contexte` | â€” | Contexte familial global (jalons prochains, rappels, suggestions achats urgents, mÃ©tÃ©o) |

### Enfants & Jalons (5)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/enfants` | `page`, `page_size`, `actif=True` | Liste profils enfants |
| GET | `/famille/enfants/{id}` | â€” | DÃ©tail enfant |
| GET | `/famille/enfants/{id}/jalons` | `categorie?` | Jalons de dÃ©veloppement |
| POST | `/famille/enfants/{id}/jalons` | Body: titre, description, categorie, date_atteint | Ajoute un jalon (201) |
| DELETE | `/famille/enfants/{id}/jalons/{jalon_id}` | â€” | Supprime un jalon |

### ActivitÃ©s (6) â€” Phase O : `suggestions_struct` pour prÃ©-remplissage

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/activites` | `page`, `page_size`, `type_activite?`, `statut?`, `date_debut?`, `date_fin?`, `cursor?` | Liste (offset + cursor) |
| GET | `/famille/activites/{id}` | â€” | DÃ©tail activitÃ© |
| POST | `/famille/activites` | Body: titre, type_activite, date_prevue... | CrÃ©e (201) |
| PATCH | `/famille/activites/{id}` | Body: champs partiels | Met Ã  jour |
| DELETE | `/famille/activites/{id}` | â€” | Supprime |
| POST | `/famille/activites/suggestions-ia-auto` | Body: `{type_prefere?, nb_suggestions?}` | Suggestions IA mÃ©tÃ©o-adaptÃ©es ; retourne `suggestions` (texte) + `suggestions_struct` (liste d'objets prÃ©-remplissables) |

### Budget familial (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/budget` | `page`, `page_size=50`, `categorie?`, `date_debut?`, `date_fin?` | DÃ©penses familiales |
| GET | `/famille/budget/stats` | `mois?` (1-12), `annee?` (2020-2030) | Statistiques budget |
| POST | `/famille/budget` | Body: date, categorie, montant, magasin... | Ajoute dÃ©pense (201) |
| DELETE | `/famille/budget/{id}` | â€” | Supprime |

### Achats famille (3) â€” Phase P

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/achats` | `page`, `page_size`, `categorie?`, `priorite?` | Liste des achats famille (non achetÃ©s en prioritÃ©) |
| POST | `/famille/achats` | Body: nom, categorie, priorite, description?, suggere_par? | CrÃ©e un achat (201) |
| POST | `/famille/achats/suggestions` | Body: `{}` (contexte infÃ©rÃ© automatiquement) | GÃ©nÃ¨re des suggestions d'achats proactives IA (anniversaires, jalons, saison) |

> **RÃ©ponse `/achats/suggestions`** : `{ suggestions: [{titre, description, source, fourchette_prix?, ou_acheter?, pertinence?}], total }` â€” source âˆˆ `"anniversaire" | "jalon" | "saison"`

### Shopping (1)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/shopping` | `liste?`, `categorie?`, `actif=True` | Articles shopping familial (liste gÃ©nÃ©rale) |

### Routines familiales (5)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/routines` | `actif?` | Routines avec Ã©tapes |
| GET | `/famille/routines/{id}` | â€” | DÃ©tail routine |
| POST | `/famille/routines` | Body: nom, type, est_active, etapes[] | CrÃ©e (201) |
| PATCH | `/famille/routines/{id}` | Body: nom, type, est_active | Met Ã  jour |
| DELETE | `/famille/routines/{id}` | â€” | Supprime |

### Anniversaires (5)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/anniversaires` | `relation?`, `actif=True` | TriÃ©s par jours restants |
| GET | `/famille/anniversaires/{id}` | â€” | DÃ©tail |
| POST | `/famille/anniversaires` | Body: `AnniversaireCreate` | CrÃ©e (201) |
| PATCH | `/famille/anniversaires/{id}` | Body: `AnniversairePatch` | Met Ã  jour |
| DELETE | `/famille/anniversaires/{id}` | â€” | Supprime |

### Ã‰vÃ©nements familiaux (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/evenements` | `type_evenement?`, `actif=True` | Liste Ã©vÃ©nements |
| POST | `/famille/evenements` | Body: `EvenementFamilialCreate` | CrÃ©e (201) |
| PATCH | `/famille/evenements/{id}` | Body: `EvenementFamilialPatch` | Met Ã  jour |
| DELETE | `/famille/evenements/{id}` | â€” | Supprime |

### Journal familial (3) â€” Phase R

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/famille/journal/resumer-semaine` | Body: `{date_debut?, style?}` | GÃ©nÃ¨re un rÃ©sumÃ© IA de la semaine (alias de `POST /famille/journal/ia-semaine`) |
| POST | `/famille/journal/ia-semaine` | Body: `{date_debut?, style?}` | GÃ©nÃ¨re un rÃ©sumÃ© IA et le sauvegarde avec tag `resume-ia` |
| POST | `/famille/journal/retrospective` | Body: `{periode?}` | RÃ©trospective IA longue pÃ©riode |

---

## ðŸ¡ Maison â€” `/api/v1/maison` (111 endpoints)

Module le plus vaste â€” gestion complÃ¨te du foyer.

### Projets domestiques (5)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/projets` | `page`, `page_size`, `statut?`, `priorite?` | Liste projets |
| GET | `/maison/projets/{id}` | â€” | DÃ©tail avec tÃ¢ches |
| POST | `/maison/projets` | Body: dict | CrÃ©e (201) |
| PATCH | `/maison/projets/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/projets/{id}` | â€” | Supprime |

### Routines maison (2)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/routines` | `categorie?`, `actif=True` | Liste routines |
| GET | `/maison/routines/{id}` | â€” | DÃ©tail avec tÃ¢ches |

### Entretien (4 + 1 dashboard)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/entretien` | `categorie?`, `piece?`, `fait?` | TÃ¢ches d'entretien |
| POST | `/maison/entretien` | Body: dict | CrÃ©e (201) |
| PATCH | `/maison/entretien/{id}` | Body: dict | Met Ã  jour / marque faite |
| DELETE | `/maison/entretien/{id}` | â€” | Supprime |
| GET | `/maison/entretien/sante-appareils` | â€” | Dashboard santÃ© appareils |

### Jardin (6)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/jardin` | `type_element?`, `statut?` | Ã‰lÃ©ments du jardin |
| GET | `/maison/jardin/{id}/journal` | â€” | Journal d'entretien |
| POST | `/maison/jardin` | Body: dict | Ajoute Ã©lÃ©ment (201) |
| PATCH | `/maison/jardin/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/jardin/{id}` | â€” | Supprime |
| GET | `/maison/jardin/calendrier-semis` | `mois?` (1-12) | Calendrier des semis |

### Stocks consommables (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/stocks` | `categorie?`, `alerte_stock=False` | Stocks maison |
| POST | `/maison/stocks` | Body: dict | CrÃ©e (201) |
| PATCH | `/maison/stocks/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/stocks/{id}` | â€” | Supprime |

### Meubles / Wishlist (5)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/meubles` | `piece?`, `statut?`, `priorite?` | Wishlist meubles |
| POST | `/maison/meubles` | Body: dict | CrÃ©e (201) |
| PATCH | `/maison/meubles/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/meubles/{id}` | â€” | Supprime |
| GET | `/maison/meubles/budget` | â€” | RÃ©sumÃ© budget meubles |

### Cellier (9)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/cellier` | `categorie?`, `emplacement?` | Articles du cellier |
| GET | `/maison/cellier/alertes/peremption` | `jours=14` (1-90) | Alertes pÃ©remption |
| GET | `/maison/cellier/alertes/stock` | â€” | Alertes stock bas |
| GET | `/maison/cellier/stats` | â€” | Statistiques cellier |
| GET | `/maison/cellier/{id}` | â€” | DÃ©tail article |
| POST | `/maison/cellier` | Body: dict | Ajoute (201) |
| PATCH | `/maison/cellier/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/cellier/{id}` | â€” | Supprime |
| PATCH | `/maison/cellier/{id}/quantite` | Body: `{delta: int}` | Ajuste quantitÃ© +/- |

### Artisans (9)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/artisans` | `metier?` | Carnet d'adresses |
| GET | `/maison/artisans/stats` | â€” | Stats artisans |
| GET | `/maison/artisans/{id}` | â€” | DÃ©tail |
| POST | `/maison/artisans` | Body: dict | CrÃ©e (201) |
| PATCH | `/maison/artisans/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/artisans/{id}` | â€” | Supprime |
| GET | `/maison/artisans/{id}/interventions` | â€” | Historique interventions |
| POST | `/maison/artisans/{id}/interventions` | Body: dict | Enregistre intervention (201) |
| DELETE | `/maison/artisans/interventions/{id}` | â€” | Supprime intervention |

### Contrats (7)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/contrats` | `type_contrat?`, `statut?` | Liste contrats |
| GET | `/maison/contrats/alertes` | `jours=60` (1-365) | Renouvellements Ã  venir |
| GET | `/maison/contrats/resume-financier` | â€” | RÃ©sumÃ© financier |
| GET | `/maison/contrats/{id}` | â€” | DÃ©tail |
| POST | `/maison/contrats` | Body: dict | CrÃ©e (201) |
| PATCH | `/maison/contrats/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/contrats/{id}` | â€” | Supprime |

### Garanties (10)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/garanties` | `statut?`, `piece?` | Liste garanties |
| GET | `/maison/garanties/alertes` | `jours=60` (1-365) | Garanties expirant |
| GET | `/maison/garanties/stats` | â€” | Stats garanties |
| GET | `/maison/garanties/{id}` | â€” | DÃ©tail |
| POST | `/maison/garanties` | Body: dict | Enregistre (201) |
| PATCH | `/maison/garanties/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/garanties/{id}` | â€” | Supprime |
| GET | `/maison/garanties/{id}/incidents` | â€” | Incidents SAV |
| POST | `/maison/garanties/{id}/incidents` | Body: dict | Enregistre incident (201) |
| PATCH | `/maison/garanties/incidents/{id}` | Body: dict | Met Ã  jour incident |

### Diagnostics immobiliers (6)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/diagnostics` | â€” | Diagnostics immobiliers |
| GET | `/maison/diagnostics/alertes` | `jours=90` (1-365) | ValiditÃ© expirant |
| GET | `/maison/diagnostics/validite-types` | â€” | DurÃ©es validitÃ© par type |
| POST | `/maison/diagnostics` | Body: dict | Enregistre (201) |
| PATCH | `/maison/diagnostics/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/diagnostics/{id}` | â€” | Supprime |

### Estimations immobiliÃ¨res (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/estimations` | â€” | Estimations |
| GET | `/maison/estimations/derniere` | â€” | DerniÃ¨re estimation |
| POST | `/maison/estimations` | Body: dict | Enregistre (201) |
| DELETE | `/maison/estimations/{id}` | â€” | Supprime |

### Ã‰co-Tips (5)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/eco-tips` | `actif_only=False` | Actions Ã©cologiques |
| GET | `/maison/eco-tips/{id}` | â€” | DÃ©tail |
| POST | `/maison/eco-tips` | Body: dict | CrÃ©e (201) |
| PATCH | `/maison/eco-tips/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/eco-tips/{id}` | â€” | Supprime |

### DÃ©penses maison (8)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/depenses` | `mois?` (1-12), `annee?` | DÃ©penses maison |
| GET | `/maison/depenses/stats` | â€” | Stats globales |
| GET | `/maison/depenses/historique/{categorie}` | `nb_mois=12` (1-36) | Historique par catÃ©gorie |
| GET | `/maison/depenses/energie/{type_energie}` | `nb_mois=12` (1-36) | Conso Ã©nergie |
| GET | `/maison/depenses/{id}` | â€” | DÃ©tail |
| POST | `/maison/depenses` | Body: dict | Enregistre (201) |
| PATCH | `/maison/depenses/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/depenses/{id}` | â€” | Supprime |

### Nuisibles (5)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/nuisibles` | â€” | Traitements anti-nuisibles |
| GET | `/maison/nuisibles/prochains` | `jours=30` (1-180) | Prochains traitements |
| POST | `/maison/nuisibles` | Body: dict | Enregistre (201) |
| PATCH | `/maison/nuisibles/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/nuisibles/{id}` | â€” | Supprime |

### Devis comparatifs (6)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/devis` | `projet_id?` | Devis |
| POST | `/maison/devis` | Body: dict | CrÃ©e (201) |
| PATCH | `/maison/devis/{id}` | Body: dict | Met Ã  jour |
| DELETE | `/maison/devis/{id}` | â€” | Supprime |
| POST | `/maison/devis/{id}/lignes` | Body: dict | Ajoute une ligne (201) |
| POST | `/maison/devis/{id}/choisir` | â€” | Accepte un devis |

### Entretien saisonnier (6)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/entretien-saisonnier` | â€” | TÃ¢ches saisonniÃ¨res |
| GET | `/maison/entretien-saisonnier/alertes` | â€” | TÃ¢ches Ã  faire ce mois |
| POST | `/maison/entretien-saisonnier` | Body: dict | CrÃ©e (201) |
| DELETE | `/maison/entretien-saisonnier/{id}` | â€” | Supprime |
| PATCH | `/maison/entretien-saisonnier/{id}/fait` | â€” | Marque fait |
| POST | `/maison/entretien-saisonnier/reset` | â€” | Reset annuel checklist |

### RelevÃ©s compteurs (3)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/releves` | â€” | RelevÃ©s compteurs |
| POST | `/maison/releves` | Body: dict | Enregistre (201) |
| DELETE | `/maison/releves/{id}` | â€” | Supprime |

### Visualisation maison (5)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/visualisation/pieces` | `etage?` | PiÃ¨ces avec dÃ©tails |
| GET | `/maison/visualisation/etages` | â€” | Ã‰tages disponibles |
| GET | `/maison/visualisation/pieces/{id}/historique` | â€” | Historique travaux |
| GET | `/maison/visualisation/pieces/{id}/objets` | â€” | Objets dans une piÃ¨ce |
| POST | `/maison/visualisation/positions` | Body: `{pieces: [...]}` | Sauvegarde layout drag-and-drop |

### Hub maison (1)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/hub/stats` | â€” | Stats dashboard maison |

---

## ðŸŽ® Jeux â€” `/api/v1/jeux` (11 endpoints)

Paris sportifs et loterie.

### Ã‰quipes (2)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/jeux/equipes` | `championnat?`, `search?` | Ã‰quipes football |
| GET | `/jeux/equipes/{id}` | â€” | DÃ©tail Ã©quipe |

### Matchs (2)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/jeux/matchs` | `page`, `page_size`, `championnat?`, `joue?`, `date_debut?`, `date_fin?`, `cursor?` | Liste (offset + cursor) |
| GET | `/jeux/matchs/{id}` | â€” | DÃ©tail avec paris |

### Paris sportifs (5)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/jeux/paris` | `page`, `page_size=50`, `statut?`, `est_virtuel?` | Liste paris |
| GET | `/jeux/paris/stats` | `est_virtuel?` | Statistiques |
| POST | `/jeux/paris` | Body: match_id, prediction, cote, mise... | CrÃ©e (201) |
| PATCH | `/jeux/paris/{id}` | Body: statut, gain, notes | Met Ã  jour |
| DELETE | `/jeux/paris/{id}` | â€” | Supprime |

### Loto (2)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/jeux/loto/tirages` | `page`, `page_size=50` | Tirages loto |
| GET | `/jeux/loto/grilles` | `est_virtuelle?` | Grilles jouÃ©es |

---

## ðŸ“Š Dashboard â€” `/api/v1/dashboard` (1 endpoint)

| MÃ©thode | Path | Description |
| --------- | ------ | ------------- |
| GET | `/dashboard` | DonnÃ©es agrÃ©gÃ©es : stats, budget mois, activitÃ©s, alertes |

---

## ðŸ³ Batch Cooking â€” `/api/v1/batch-cooking` (7 endpoints)

Sessions de prÃ©paration en lot.

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/batch-cooking` | `page`, `page_size`, `statut?` | Liste sessions |
| GET | `/batch-cooking/{id}` | â€” | DÃ©tail avec Ã©tapes |
| POST | `/batch-cooking` | Body: `SessionBatchCreate` | CrÃ©e session |
| PATCH | `/batch-cooking/{id}` | Body: `SessionBatchPatch` | Met Ã  jour |
| DELETE | `/batch-cooking/{id}` | â€” | Supprime |
| GET | `/batch-cooking/preparations` | `consomme?` | PrÃ©parations en stock |
| GET | `/batch-cooking/config` | â€” | Configuration batch |

---

## â™»ï¸ Anti-Gaspillage â€” `/api/v1/anti-gaspillage` (1 endpoint)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/anti-gaspillage` | `jours=7` (1-30) | Score, articles urgents, recettes rescue |

---

## âš™ï¸ PrÃ©fÃ©rences â€” `/api/v1/preferences` (3 endpoints)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/preferences` | â€” | PrÃ©fÃ©rences utilisateur |
| PUT | `/preferences` | Body: `PreferencesCreate` | Upsert complet |
| PATCH | `/preferences` | Body: `PreferencesPatch` | Mise Ã  jour partielle |

---

## ðŸ“„ Export PDF â€” `/api/v1/export` (1 endpoint)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/export/pdf` | `type_export` (courses, planning, recette, budget), `id_ressource?` | GÃ©nÃ¨re PDF (StreamingResponse) |

> `id_ressource` requis pour `type_export=recette` et `type_export=planning`.

---

## ðŸ“† Calendriers â€” `/api/v1/calendriers` (6 endpoints)

Calendriers externes synchronisÃ©s.

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/calendriers` | `provider?`, `enabled?` | Liste calendriers |
| GET | `/calendriers/{id}` | â€” | DÃ©tail |
| GET | `/calendriers/evenements` | `page`, `page_size=50`, `calendrier_id?`, `date_debut?`, `date_fin?`, `all_day?`, `cursor?` | Ã‰vÃ©nements (offset + cursor) |
| GET | `/calendriers/evenements/{id}` | â€” | DÃ©tail Ã©vÃ©nement |
| GET | `/calendriers/evenements/aujourd-hui` | â€” | Ã‰vÃ©nements du jour |
| GET | `/calendriers/evenements/semaine` | `date_debut?` | Ã‰vÃ©nements semaine groupÃ©s par jour |

---

## ðŸ“‘ Documents â€” `/api/v1/documents` (5 endpoints)

Documents familiaux (passeports, assurances, etc.).

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/documents` | `categorie?`, `membre?`, `expire?`, `search?`, `page`, `page_size` | Liste avec filtres |
| GET | `/documents/{id}` | â€” | DÃ©tail |
| POST | `/documents` | Body: `DocumentCreate` | CrÃ©e (201) |
| PATCH | `/documents/{id}` | Body: `DocumentPatch` | Met Ã  jour |
| DELETE | `/documents/{id}` | â€” | Soft delete (actif=False) |

---

## ðŸ”§ Utilitaires â€” `/api/v1/utilitaires` (24 endpoints)

### Notes mÃ©mo (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/notes` | `categorie?`, `epingle?`, `archive=False`, `search?` | Notes |
| POST | `/utilitaires/notes` | Body: `NoteCreate` | CrÃ©e |
| PATCH | `/utilitaires/notes/{id}` | Body: `NotePatch` | Met Ã  jour |
| DELETE | `/utilitaires/notes/{id}` | â€” | Supprime |

### Journal de bord (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/journal` | `humeur?`, `limit=30` (1-365) | EntrÃ©es journal |
| POST | `/utilitaires/journal` | Body: `JournalCreate` | CrÃ©e |
| PATCH | `/utilitaires/journal/{id}` | Body: `JournalPatch` | Met Ã  jour |
| DELETE | `/utilitaires/journal/{id}` | â€” | Supprime |

### Contacts utiles (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/contacts` | `categorie?`, `favori?`, `search?` | Contacts |
| POST | `/utilitaires/contacts` | Body: `ContactCreate` | CrÃ©e |
| PATCH | `/utilitaires/contacts/{id}` | Body: `ContactPatch` | Met Ã  jour |
| DELETE | `/utilitaires/contacts/{id}` | â€” | Supprime |

### Liens favoris (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/liens` | `categorie?`, `favori?` | Liens |
| POST | `/utilitaires/liens` | Body: `LienCreate` | CrÃ©e |
| PATCH | `/utilitaires/liens/{id}` | Body: `LienPatch` | Met Ã  jour |
| DELETE | `/utilitaires/liens/{id}` | â€” | Supprime |

### Mots de passe maison (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/passwords` | `categorie?` | Mots de passe (chiffrÃ©s) |
| POST | `/utilitaires/passwords` | Body: `MotDePasseCreate` | CrÃ©e |
| PATCH | `/utilitaires/passwords/{id}` | Body: `MotDePassePatch` | Met Ã  jour |
| DELETE | `/utilitaires/passwords/{id}` | â€” | Supprime |

### Ã‰nergie (4)

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/energie` | `type_energie?` (electricite/gaz/eau), `annee?` | RelevÃ©s Ã©nergie |
| POST | `/utilitaires/energie` | Body: `EnergieCreate` | CrÃ©e |
| PATCH | `/utilitaires/energie/{id}` | Body: `EnergiePatch` | Met Ã  jour |
| DELETE | `/utilitaires/energie/{id}` | â€” | Supprime |

---

## ðŸ”” Push Notifications â€” `/api/v1/push` (3 endpoints)

Web Push via service worker.

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/push/subscribe` | Body: `PushSubscriptionRequest` | Enregistre abonnement |
| DELETE | `/push/unsubscribe` | Body: `PushUnsubscribeRequest` | Supprime abonnement |
| GET | `/push/status` | â€” | Statut notifications |

---

## ðŸ”— Webhooks â€” `/api/v1/webhooks` (6 endpoints)

Webhooks sortants avec signature HMAC.

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/webhooks` | Body: `WebhookCreate` | CrÃ©e (secret HMAC auto-gÃ©nÃ©rÃ©) (201) |
| GET | `/webhooks` | â€” | Liste mes webhooks |
| GET | `/webhooks/{id}` | â€” | DÃ©tail |
| PUT | `/webhooks/{id}` | Body: `WebhookUpdate` | Met Ã  jour |
| DELETE | `/webhooks/{id}` | â€” | Supprime (204) |
| POST | `/webhooks/{id}/test` | â€” | Ping de test |

---

## ðŸ“ Upload â€” `/api/v1/upload` (3 endpoints)

Upload vers Supabase Storage.

| MÃ©thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/upload` | `bucket="documents"`, Body: `UploadFile` (multipart, 10MB max) | Upload fichier |

---

## RÃ©sumÃ© par module

| Module | PrÃ©fixe | Endpoints |
| -------- | --------- | ----------- |
| Auth | `/api/v1/auth` | 4 |
| Recettes | `/api/v1/recettes` | 6 |
| Courses | `/api/v1/courses` | 11 |
| Inventaire | `/api/v1/inventaire` | 6 |
| Planning | `/api/v1/planning` | 4 |
| Suggestions IA | `/api/v1/suggestions` | 2 |
| Famille | `/api/v1/famille` | 29 |
| Maison | `/api/v1/maison` | 111 |
| Jeux | `/api/v1/jeux` | 11 |
| Dashboard | `/api/v1/dashboard` | 1 |
| Batch Cooking | `/api/v1/batch-cooking` | 7 |
| Anti-Gaspillage | `/api/v1/anti-gaspillage` | 1 |
| PrÃ©fÃ©rences | `/api/v1/preferences` | 3 |
| Export PDF | `/api/v1/export` | 1 |
| Calendriers | `/api/v1/calendriers` | 6 |
| Documents | `/api/v1/documents` | 5 |
| Utilitaires | `/api/v1/utilitaires` | 24 |
| Push | `/api/v1/push` | 3 |
| Webhooks | `/api/v1/webhooks` | 6 |
| Upload | `/api/v1/upload` | 3 |
| **Total** | | **242** |
