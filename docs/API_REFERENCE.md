# ?? API Reference ? Assistant Matanne

Documentation compl?te de l'API REST FastAPI, organis?e par modules fonctionnels et v?rifi?e pendant la phase 10.

## V?rification Phase 10

- Audit code du 1 avril 2026: **622 handlers HTTP** d?tect?s dans `src/api/routes/*.py`.
- Le document reste organis? par modules fonctionnels pour la lisibilit?.
- R?f?rence stricte des sch?mas de r?ponse: voir `docs/API_SCHEMAS.md` (auto-g?n?r?).

## Vue d'ensemble

| Attribut             | Valeur                                            |
| -------------------- | ------------------------------------------------- |
| **Base URL**         | `http://localhost:8000`                           |
| **Documentation**    | `/docs` (Swagger), `/redoc` (ReDoc)               |
| **Version**          | v1 (`/api/v1/...`)                                |
| **Authentification** | JWT Bearer Token (`Authorization: Bearer <token>`) |
| **Rate Limiting**    | 60 req/min standard, 10 req/min IA                |
| **Pagination**       | Offset (`page`, `page_size`) + Cursor (`cursor`)  |

### R?ponses communes

| Code | Description |
| ------ | ------------- |
| 200  | Succ?s |
| 201  | Cr?ation r?ussie |
| 401  | Non authentifi? |
| 403  | Acc?s refus? |
| 404  | Ressource introuvable |
| 422  | Erreur de validation |
| 429  | Rate limit d?pass? |
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

## Sant? & Informations

| M?thode | Path | Description |
| --------- | ------ | ------------- |
| GET | `/` | Informations sur l'API (nom, version, status) |
| GET | `/health` | ?tat de l'API et de la base de donn?es |

---

## ?? Auth ? `/api/v1/auth` (4 endpoints)

Authentification via Supabase Auth + JWT.

| M?thode | Path | Description |
| --------- | ------ | ------------- |
| POST | `/auth/login` | Connexion (email, password) ? `TokenResponse` |
| POST | `/auth/register` | Inscription (email, password, nom) ? `TokenResponse` (201) |
| POST | `/auth/refresh` | Rafra?chit le token JWT |
| GET | `/auth/me` | Profil de l'utilisateur connect? ? `UserInfoResponse` |

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

## ??? Recettes ? `/api/v1/recettes` (6 endpoints)

CRUD complet des recettes.

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/recettes` | `page`, `page_size`, `categorie?`, `search?` | Liste pagin?e avec filtres |
| GET | `/recettes/{id}` | ? | D?tail d'une recette |
| POST | `/recettes` | Body: `RecetteCreate` | Cr?e une recette |
| PUT | `/recettes/{id}` | Body: `RecetteCreate` | Remplacement complet |
| PATCH | `/recettes/{id}` | Body: `RecettePatch` | Mise ? jour partielle |
| DELETE | `/recettes/{id}` | ? | Supprime une recette |

---

## ?? Courses ? `/api/v1/courses` (11 endpoints)

Listes de courses avec collaboration WebSocket.

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/courses` | `page`, `page_size`, `active_only=True` | Liste des listes de courses |
| POST | `/courses` | Body: `CourseListCreate` | Cr?e une liste (201) |
| GET | `/courses/{id}` | ? | D?tail avec articles |
| PUT | `/courses/{id}` | Body: `CourseListCreate` | Met ? jour le nom |
| DELETE | `/courses/{id}` | ? | Supprime liste + articles |
| POST | `/courses/{id}/items` | Body: `CourseItemBase` | Ajoute un article (201) |
| PUT | `/courses/{id}/items/{item_id}` | Body: `CourseItemBase` | Met ? jour un article |
| DELETE | `/courses/{id}/items/{item_id}` | ? | Supprime un article |
| GET | `/courses/{id}/export` | `group_by=categorie` | Export texte brut |
| POST | `/courses/{id}/checkout-items` | Body: `CheckoutCoursesRequest` | Checkout batch ? maj inventaire |
| POST | `/courses/{id}/scan-barcode-checkout` | Body: `ScanBarcodeCheckoutRequest` | Checkout via code-barres |

### WebSocket ? `/api/v1/ws/courses/{liste_id}`

Collaboration temps r?el sur les listes de courses.

**Connexion:**
```
ws://localhost:8000/api/v1/ws/courses/{liste_id}?user_id=abc123&username=Anne
```

| Param | Type | Description |
| ------- | ------ | ------------- |
| `liste_id` | `int` (path) | ID de la liste de courses |
| `user_id` | `str` (query, requis) | Identifiant utilisateur |
| `username` | `str` (query, d?faut: "Anonyme") | Nom affich? |

**Messages Client ? Serveur** (JSON, champ `action`) :

| Action | Champs | Description |
| -------- | -------- | ------------- |
| `item_added` | `item: {nom, quantite, unite}` | Article ajout? |
| `item_removed` | `item_id: int` | Article supprim? |
| `item_checked` | `item_id: int, checked: bool` | Article coch?/d?coch? |
| `item_updated` | `item_id: int, updates: {...}` | Article modifi? |
| `list_renamed` | `new_name: str` | Liste renomm?e |
| `user_typing` | `typing: bool` | Indicateur de saisie |
| `ping` | ? | Keep-alive |

**Messages Serveur ? Clients** (JSON, champ `type`) :

| Type | Champs | Description |
| ------ | -------- | ------------- |
| `sync` | `action, user_id, username, timestamp, ...data` | Broadcast d'une modification |
| `user_joined` | `user_id, username, timestamp` | Nouvel utilisateur connect? |
| `user_left` | `user_id, username, timestamp` | Utilisateur d?connect? |
| `users_list` | `users: [{user_id, username, connected_at}]` | Liste des connect?s (envoy? ? la connexion) |
| `error` | `message: str` | Erreur (action inconnue) |
| `pong` | ? | R?ponse au ping |

Les modifications `item_added`, `item_removed`, `item_checked` et `list_renamed` sont persist?es en base de donn?es.

---

## ?? Inventaire ? `/api/v1/inventaire` (6 endpoints)

Gestion des stocks alimentaires.

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/inventaire` | `page`, `page_size=50`, `categorie?`, `emplacement?`, `stock_bas?`, `peremption_proche?` | Liste avec filtres avanc?s |
| POST | `/inventaire` | Body: `InventaireItemCreate` | Cr?e un article |
| GET | `/inventaire/barcode/{code}` | ? | Recherche par code-barres |
| GET | `/inventaire/{id}` | ? | D?tail article |
| PUT | `/inventaire/{id}` | Body: `InventaireItemUpdate` | Met ? jour (partiel via exclude_unset) |
| DELETE | `/inventaire/{id}` | ? | Supprime |

---

## ?? Planning ? `/api/v1/planning` (4 endpoints)

Planification des repas de la semaine.

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/planning/semaine` | `date_debut?` (ISO datetime) | Planning de la semaine |
| POST | `/planning/repas` | Body: `RepasCreate` | Planifie un repas (upsert) |
| PUT | `/planning/repas/{id}` | Body: `RepasCreate` | Met ? jour un repas |
| DELETE | `/planning/repas/{id}` | ? | Supprime un repas |

---

## ?? Suggestions IA ? `/api/v1/suggestions` (2 endpoints)

Suggestions via Mistral AI (rate limit? : 10 req/min).

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/suggestions/recettes` | `contexte="repas ?quilibr?"`, `nombre=3` (1-10) | Suggestions recettes |
| GET | `/suggestions/planning` | `jours=7` (1-14), `personnes=4` (1-20) | Planning complet IA |

---

## ??????????? Famille ? `/api/v1/famille` (37 endpoints)

### Contexte familial (1) ? Phase M

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/contexte` | ? | Contexte familial global (jalons prochains, rappels, suggestions achats urgents, m?t?o) |

### Enfants & Jalons (5)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/enfants` | `page`, `page_size`, `actif=True` | Liste profils enfants |
| GET | `/famille/enfants/{id}` | ? | D?tail enfant |
| GET | `/famille/enfants/{id}/jalons` | `categorie?` | Jalons de d?veloppement |
| POST | `/famille/enfants/{id}/jalons` | Body: titre, description, categorie, date_atteint | Ajoute un jalon (201) |
| DELETE | `/famille/enfants/{id}/jalons/{jalon_id}` | ? | Supprime un jalon |

### Activit?s (6) ? Phase O : `suggestions_struct` pour pr?-remplissage

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/activites` | `page`, `page_size`, `type_activite?`, `statut?`, `date_debut?`, `date_fin?`, `cursor?` | Liste (offset + cursor) |
| GET | `/famille/activites/{id}` | ? | D?tail activit? |
| POST | `/famille/activites` | Body: titre, type_activite, date_prevue... | Cr?e (201) |
| PATCH | `/famille/activites/{id}` | Body: champs partiels | Met ? jour |
| DELETE | `/famille/activites/{id}` | ? | Supprime |
| POST | `/famille/activites/suggestions-ia-auto` | Body: `{type_prefere?, nb_suggestions?}` | Suggestions IA m?t?o-adapt?es ; retourne `suggestions` (texte) + `suggestions_struct` (liste d'objets pr?-remplissables) |

### Budget familial (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/budget` | `page`, `page_size=50`, `categorie?`, `date_debut?`, `date_fin?` | D?penses familiales |
| GET | `/famille/budget/stats` | `mois?` (1-12), `annee?` (2020-2030) | Statistiques budget |
| POST | `/famille/budget` | Body: date, categorie, montant, magasin... | Ajoute d?pense (201) |
| DELETE | `/famille/budget/{id}` | ? | Supprime |

### Achats famille (3) ? Phase P

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/achats` | `page`, `page_size`, `categorie?`, `priorite?` | Liste des achats famille (non achet?s en priorit?) |
| POST | `/famille/achats` | Body: nom, categorie, priorite, description?, suggere_par? | Cr?e un achat (201) |
| POST | `/famille/achats/suggestions` | Body: `{}` (contexte inf?r? automatiquement) | G?n?re des suggestions d'achats proactives IA (anniversaires, jalons, saison) |

> **R?ponse `/achats/suggestions`** : `{ suggestions: [{titre, description, source, fourchette_prix?, ou_acheter?, pertinence?}], total }` ? source ? `"anniversaire" | "jalon" | "saison"`

### Shopping (1)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/shopping` | `liste?`, `categorie?`, `actif=True` | Articles shopping familial (liste g?n?rale) |

### Routines familiales (5)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/routines` | `actif?` | Routines avec ?tapes |
| GET | `/famille/routines/{id}` | ? | D?tail routine |
| POST | `/famille/routines` | Body: nom, type, est_active, etapes[] | Cr?e (201) |
| PATCH | `/famille/routines/{id}` | Body: nom, type, est_active | Met ? jour |
| DELETE | `/famille/routines/{id}` | ? | Supprime |

### Anniversaires (5)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/anniversaires` | `relation?`, `actif=True` | Tri?s par jours restants |
| GET | `/famille/anniversaires/{id}` | ? | D?tail |
| POST | `/famille/anniversaires` | Body: `AnniversaireCreate` | Cr?e (201) |
| PATCH | `/famille/anniversaires/{id}` | Body: `AnniversairePatch` | Met ? jour |
| DELETE | `/famille/anniversaires/{id}` | ? | Supprime |

### ?v?nements familiaux (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/famille/evenements` | `type_evenement?`, `actif=True` | Liste ?v?nements |
| POST | `/famille/evenements` | Body: `EvenementFamilialCreate` | Cr?e (201) |
| PATCH | `/famille/evenements/{id}` | Body: `EvenementFamilialPatch` | Met ? jour |
| DELETE | `/famille/evenements/{id}` | ? | Supprime |

### Journal familial (3) ? Phase R

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/famille/journal/resumer-semaine` | Body: `{date_debut?, style?}` | G?n?re un r?sum? IA de la semaine (alias de `POST /famille/journal/ia-semaine`) |
| POST | `/famille/journal/ia-semaine` | Body: `{date_debut?, style?}` | G?n?re un r?sum? IA et le sauvegarde avec tag `resume-ia` |
| POST | `/famille/journal/retrospective` | Body: `{periode?}` | R?trospective IA longue p?riode |

---

## ?? Maison ? `/api/v1/maison` (111 endpoints)

Module le plus vaste ? gestion compl?te du foyer.

### Projets domestiques (5)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/projets` | `page`, `page_size`, `statut?`, `priorite?` | Liste projets |
| GET | `/maison/projets/{id}` | ? | D?tail avec t?ches |
| POST | `/maison/projets` | Body: dict | Cr?e (201) |
| PATCH | `/maison/projets/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/projets/{id}` | ? | Supprime |

### Routines maison (2)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/routines` | `categorie?`, `actif=True` | Liste routines |
| GET | `/maison/routines/{id}` | ? | D?tail avec t?ches |

### Entretien (4 + 1 dashboard)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/entretien` | `categorie?`, `piece?`, `fait?` | T?ches d'entretien |
| POST | `/maison/entretien` | Body: dict | Cr?e (201) |
| PATCH | `/maison/entretien/{id}` | Body: dict | Met ? jour / marque faite |
| DELETE | `/maison/entretien/{id}` | ? | Supprime |
| GET | `/maison/entretien/sante-appareils` | ? | Dashboard sant? appareils |

### Jardin (6)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/jardin` | `type_element?`, `statut?` | ?l?ments du jardin |
| GET | `/maison/jardin/{id}/journal` | ? | Journal d'entretien |
| POST | `/maison/jardin` | Body: dict | Ajoute ?l?ment (201) |
| PATCH | `/maison/jardin/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/jardin/{id}` | ? | Supprime |
| GET | `/maison/jardin/calendrier-semis` | `mois?` (1-12) | Calendrier des semis |

### Stocks consommables (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/stocks` | `categorie?`, `alerte_stock=False` | Stocks maison |
| POST | `/maison/stocks` | Body: dict | Cr?e (201) |
| PATCH | `/maison/stocks/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/stocks/{id}` | ? | Supprime |

### Meubles / Wishlist (5)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/meubles` | `piece?`, `statut?`, `priorite?` | Wishlist meubles |
| POST | `/maison/meubles` | Body: dict | Cr?e (201) |
| PATCH | `/maison/meubles/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/meubles/{id}` | ? | Supprime |
| GET | `/maison/meubles/budget` | ? | R?sum? budget meubles |

### Cellier (9)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/cellier` | `categorie?`, `emplacement?` | Articles du cellier |
| GET | `/maison/cellier/alertes/peremption` | `jours=14` (1-90) | Alertes p?remption |
| GET | `/maison/cellier/alertes/stock` | ? | Alertes stock bas |
| GET | `/maison/cellier/stats` | ? | Statistiques cellier |
| GET | `/maison/cellier/{id}` | ? | D?tail article |
| POST | `/maison/cellier` | Body: dict | Ajoute (201) |
| PATCH | `/maison/cellier/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/cellier/{id}` | ? | Supprime |
| PATCH | `/maison/cellier/{id}/quantite` | Body: `{delta: int}` | Ajuste quantit? +/- |

### Artisans (9)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/artisans` | `metier?` | Carnet d'adresses |
| GET | `/maison/artisans/stats` | ? | Stats artisans |
| GET | `/maison/artisans/{id}` | ? | D?tail |
| POST | `/maison/artisans` | Body: dict | Cr?e (201) |
| PATCH | `/maison/artisans/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/artisans/{id}` | ? | Supprime |
| GET | `/maison/artisans/{id}/interventions` | ? | Historique interventions |
| POST | `/maison/artisans/{id}/interventions` | Body: dict | Enregistre intervention (201) |
| DELETE | `/maison/artisans/interventions/{id}` | ? | Supprime intervention |

### Contrats (7)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/contrats` | `type_contrat?`, `statut?` | Liste contrats |
| GET | `/maison/contrats/alertes` | `jours=60` (1-365) | Renouvellements ? venir |
| GET | `/maison/contrats/resume-financier` | ? | R?sum? financier |
| GET | `/maison/contrats/{id}` | ? | D?tail |
| POST | `/maison/contrats` | Body: dict | Cr?e (201) |
| PATCH | `/maison/contrats/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/contrats/{id}` | ? | Supprime |

### Garanties (10)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/garanties` | `statut?`, `piece?` | Liste garanties |
| GET | `/maison/garanties/alertes` | `jours=60` (1-365) | Garanties expirant |
| GET | `/maison/garanties/stats` | ? | Stats garanties |
| GET | `/maison/garanties/{id}` | ? | D?tail |
| POST | `/maison/garanties` | Body: dict | Enregistre (201) |
| PATCH | `/maison/garanties/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/garanties/{id}` | ? | Supprime |
| GET | `/maison/garanties/{id}/incidents` | ? | Incidents SAV |
| POST | `/maison/garanties/{id}/incidents` | Body: dict | Enregistre incident (201) |
| PATCH | `/maison/garanties/incidents/{id}` | Body: dict | Met ? jour incident |

### Diagnostics immobiliers (6)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/diagnostics` | ? | Diagnostics immobiliers |
| GET | `/maison/diagnostics/alertes` | `jours=90` (1-365) | Validit? expirant |
| GET | `/maison/diagnostics/validite-types` | ? | Dur?es validit? par type |
| POST | `/maison/diagnostics` | Body: dict | Enregistre (201) |
| PATCH | `/maison/diagnostics/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/diagnostics/{id}` | ? | Supprime |

### Estimations immobili?res (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/estimations` | ? | Estimations |
| GET | `/maison/estimations/derniere` | ? | Derni?re estimation |
| POST | `/maison/estimations` | Body: dict | Enregistre (201) |
| DELETE | `/maison/estimations/{id}` | ? | Supprime |

### ?co-Tips (5)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/eco-tips` | `actif_only=False` | Actions ?cologiques |
| GET | `/maison/eco-tips/{id}` | ? | D?tail |
| POST | `/maison/eco-tips` | Body: dict | Cr?e (201) |
| PATCH | `/maison/eco-tips/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/eco-tips/{id}` | ? | Supprime |

### D?penses maison (8)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/depenses` | `mois?` (1-12), `annee?` | D?penses maison |
| GET | `/maison/depenses/stats` | ? | Stats globales |
| GET | `/maison/depenses/historique/{categorie}` | `nb_mois=12` (1-36) | Historique par cat?gorie |
| GET | `/maison/depenses/energie/{type_energie}` | `nb_mois=12` (1-36) | Conso ?nergie |
| GET | `/maison/depenses/{id}` | ? | D?tail |
| POST | `/maison/depenses` | Body: dict | Enregistre (201) |
| PATCH | `/maison/depenses/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/depenses/{id}` | ? | Supprime |

### Nuisibles (5)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/nuisibles` | ? | Traitements anti-nuisibles |
| GET | `/maison/nuisibles/prochains` | `jours=30` (1-180) | Prochains traitements |
| POST | `/maison/nuisibles` | Body: dict | Enregistre (201) |
| PATCH | `/maison/nuisibles/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/nuisibles/{id}` | ? | Supprime |

### Devis comparatifs (6)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/devis` | `projet_id?` | Devis |
| POST | `/maison/devis` | Body: dict | Cr?e (201) |
| PATCH | `/maison/devis/{id}` | Body: dict | Met ? jour |
| DELETE | `/maison/devis/{id}` | ? | Supprime |
| POST | `/maison/devis/{id}/lignes` | Body: dict | Ajoute une ligne (201) |
| POST | `/maison/devis/{id}/choisir` | ? | Accepte un devis |

### Entretien saisonnier (6)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/entretien-saisonnier` | ? | T?ches saisonni?res |
| GET | `/maison/entretien-saisonnier/alertes` | ? | T?ches ? faire ce mois |
| POST | `/maison/entretien-saisonnier` | Body: dict | Cr?e (201) |
| DELETE | `/maison/entretien-saisonnier/{id}` | ? | Supprime |
| PATCH | `/maison/entretien-saisonnier/{id}/fait` | ? | Marque fait |
| POST | `/maison/entretien-saisonnier/reset` | ? | Reset annuel checklist |

### Relev?s compteurs (3)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/releves` | ? | Relev?s compteurs |
| POST | `/maison/releves` | Body: dict | Enregistre (201) |
| DELETE | `/maison/releves/{id}` | ? | Supprime |

### Visualisation maison (5)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/visualisation/pieces` | `etage?` | Pi?ces avec d?tails |
| GET | `/maison/visualisation/etages` | ? | ?tages disponibles |
| GET | `/maison/visualisation/pieces/{id}/historique` | ? | Historique travaux |
| GET | `/maison/visualisation/pieces/{id}/objets` | ? | Objets dans une pi?ce |
| POST | `/maison/visualisation/positions` | Body: `{pieces: [...]}` | Sauvegarde layout drag-and-drop |

### Hub maison (1)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/maison/hub/stats` | ? | Stats dashboard maison |

---

## ?? Jeux ? `/api/v1/jeux` (11 endpoints)

Paris sportifs et loterie.

### ?quipes (2)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/jeux/equipes` | `championnat?`, `search?` | ?quipes football |
| GET | `/jeux/equipes/{id}` | ? | D?tail ?quipe |

### Matchs (2)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/jeux/matchs` | `page`, `page_size`, `championnat?`, `joue?`, `date_debut?`, `date_fin?`, `cursor?` | Liste (offset + cursor) |
| GET | `/jeux/matchs/{id}` | ? | D?tail avec paris |

### Paris sportifs (5)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/jeux/paris` | `page`, `page_size=50`, `statut?`, `est_virtuel?` | Liste paris |
| GET | `/jeux/paris/stats` | `est_virtuel?` | Statistiques |
| POST | `/jeux/paris` | Body: match_id, prediction, cote, mise... | Cr?e (201) |
| PATCH | `/jeux/paris/{id}` | Body: statut, gain, notes | Met ? jour |
| DELETE | `/jeux/paris/{id}` | ? | Supprime |

### Loto (2)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/jeux/loto/tirages` | `page`, `page_size=50` | Tirages loto |
| GET | `/jeux/loto/grilles` | `est_virtuelle?` | Grilles jou?es |

---

## ?? Dashboard ? `/api/v1/dashboard` (1 endpoint)

| M?thode | Path | Description |
| --------- | ------ | ------------- |
| GET | `/dashboard` | Donn?es agr?g?es : stats, budget mois, activit?s, alertes |

---

## ?? Batch Cooking ? `/api/v1/batch-cooking` (7 endpoints)

Sessions de pr?paration en lot.

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/batch-cooking` | `page`, `page_size`, `statut?` | Liste sessions |
| GET | `/batch-cooking/{id}` | ? | D?tail avec ?tapes |
| POST | `/batch-cooking` | Body: `SessionBatchCreate` | Cr?e session |
| PATCH | `/batch-cooking/{id}` | Body: `SessionBatchPatch` | Met ? jour |
| DELETE | `/batch-cooking/{id}` | ? | Supprime |
| GET | `/batch-cooking/preparations` | `consomme?` | Pr?parations en stock |
| GET | `/batch-cooking/config` | ? | Configuration batch |

---

## ?? Anti-Gaspillage ? `/api/v1/anti-gaspillage` (1 endpoint)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/anti-gaspillage` | `jours=7` (1-30) | Score, articles urgents, recettes rescue |

---

## ?? Pr?f?rences ? `/api/v1/preferences` (3 endpoints)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/preferences` | ? | Pr?f?rences utilisateur |
| PUT | `/preferences` | Body: `PreferencesCreate` | Upsert complet |
| PATCH | `/preferences` | Body: `PreferencesPatch` | Mise ? jour partielle |

---

## ?? Export PDF ? `/api/v1/export` (1 endpoint)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/export/pdf` | `type_export` (courses, planning, recette, budget), `id_ressource?` | G?n?re PDF (StreamingResponse) |

> `id_ressource` requis pour `type_export=recette` et `type_export=planning`.

---

## ?? Calendriers ? `/api/v1/calendriers` (6 endpoints)

Calendriers externes synchronis?s.

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/calendriers` | `provider?`, `enabled?` | Liste calendriers |
| GET | `/calendriers/{id}` | ? | D?tail |
| GET | `/calendriers/evenements` | `page`, `page_size=50`, `calendrier_id?`, `date_debut?`, `date_fin?`, `all_day?`, `cursor?` | ?v?nements (offset + cursor) |
| GET | `/calendriers/evenements/{id}` | ? | D?tail ?v?nement |
| GET | `/calendriers/evenements/aujourd-hui` | ? | ?v?nements du jour |
| GET | `/calendriers/evenements/semaine` | `date_debut?` | ?v?nements semaine group?s par jour |

---

## ?? Documents ? `/api/v1/documents` (5 endpoints)

Documents familiaux (passeports, assurances, etc.).

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/documents` | `categorie?`, `membre?`, `expire?`, `search?`, `page`, `page_size` | Liste avec filtres |
| GET | `/documents/{id}` | ? | D?tail |
| POST | `/documents` | Body: `DocumentCreate` | Cr?e (201) |
| PATCH | `/documents/{id}` | Body: `DocumentPatch` | Met ? jour |
| DELETE | `/documents/{id}` | ? | Soft delete (actif=False) |

---

## ?? Utilitaires ? `/api/v1/utilitaires` (24 endpoints)

### Notes m?mo (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/notes` | `categorie?`, `epingle?`, `archive=False`, `search?` | Notes |
| POST | `/utilitaires/notes` | Body: `NoteCreate` | Cr?e |
| PATCH | `/utilitaires/notes/{id}` | Body: `NotePatch` | Met ? jour |
| DELETE | `/utilitaires/notes/{id}` | ? | Supprime |

### Journal de bord (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/journal` | `humeur?`, `limit=30` (1-365) | Entr?es journal |
| POST | `/utilitaires/journal` | Body: `JournalCreate` | Cr?e |
| PATCH | `/utilitaires/journal/{id}` | Body: `JournalPatch` | Met ? jour |
| DELETE | `/utilitaires/journal/{id}` | ? | Supprime |

### Contacts utiles (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/contacts` | `categorie?`, `favori?`, `search?` | Contacts |
| POST | `/utilitaires/contacts` | Body: `ContactCreate` | Cr?e |
| PATCH | `/utilitaires/contacts/{id}` | Body: `ContactPatch` | Met ? jour |
| DELETE | `/utilitaires/contacts/{id}` | ? | Supprime |

### Liens favoris (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/liens` | `categorie?`, `favori?` | Liens |
| POST | `/utilitaires/liens` | Body: `LienCreate` | Cr?e |
| PATCH | `/utilitaires/liens/{id}` | Body: `LienPatch` | Met ? jour |
| DELETE | `/utilitaires/liens/{id}` | ? | Supprime |

### Mots de passe maison (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/passwords` | `categorie?` | Mots de passe (chiffr?s) |
| POST | `/utilitaires/passwords` | Body: `MotDePasseCreate` | Cr?e |
| PATCH | `/utilitaires/passwords/{id}` | Body: `MotDePassePatch` | Met ? jour |
| DELETE | `/utilitaires/passwords/{id}` | ? | Supprime |

### ?nergie (4)

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| GET | `/utilitaires/energie` | `type_energie?` (electricite/gaz/eau), `annee?` | Relev?s ?nergie |
| POST | `/utilitaires/energie` | Body: `EnergieCreate` | Cr?e |
| PATCH | `/utilitaires/energie/{id}` | Body: `EnergiePatch` | Met ? jour |
| DELETE | `/utilitaires/energie/{id}` | ? | Supprime |

---

## ?? Push Notifications ? `/api/v1/push` (3 endpoints)

Web Push via service worker.

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/push/subscribe` | Body: `PushSubscriptionRequest` | Enregistre abonnement |
| DELETE | `/push/unsubscribe` | Body: `PushUnsubscribeRequest` | Supprime abonnement |
| GET | `/push/status` | ? | Statut notifications |

---

## ?? Webhooks ? `/api/v1/webhooks` (6 endpoints)

Webhooks sortants avec signature HMAC.

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/webhooks` | Body: `WebhookCreate` | Cr?e (secret HMAC auto-g?n?r?) (201) |
| GET | `/webhooks` | ? | Liste mes webhooks |
| GET | `/webhooks/{id}` | ? | D?tail |
| PUT | `/webhooks/{id}` | Body: `WebhookUpdate` | Met ? jour |
| DELETE | `/webhooks/{id}` | ? | Supprime (204) |
| POST | `/webhooks/{id}/test` | ? | Ping de test |

---

## ?? Upload ? `/api/v1/upload` (3 endpoints)

Upload vers Supabase Storage.

| M?thode | Path | Params | Description |
| --------- | ------ | -------- | ------------- |
| POST | `/upload` | `bucket="documents"`, Body: `UploadFile` (multipart, 10MB max) | Upload fichier |

---

## R?sum? par module

| Module | Pr?fixe | Endpoints |
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
| Pr?f?rences | `/api/v1/preferences` | 3 |
| Export PDF | `/api/v1/export` | 1 |
| Calendriers | `/api/v1/calendriers` | 6 |
| Documents | `/api/v1/documents` | 5 |
| Utilitaires | `/api/v1/utilitaires` | 24 |
| Push | `/api/v1/push` | 3 |
| Webhooks | `/api/v1/webhooks` | 6 |
| Upload | `/api/v1/upload` | 3 |
| **Total** | | **242** |
