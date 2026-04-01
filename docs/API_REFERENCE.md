# 📡 API Reference — Assistant Matanne

Documentation complète de l'API REST FastAPI, organisée par modules fonctionnels et vérifiée pendant la phase 10.

## Vérification Phase 10

- Audit code du 1 avril 2026: **622 handlers HTTP** détectés dans `src/api/routes/*.py`.
- Le document reste organisé par modules fonctionnels pour la lisibilité.
- Référence stricte des schémas de réponse: voir `docs/API_SCHEMAS.md` (auto-généré).

## Vue d'ensemble

| Attribut             | Valeur                                            |
| -------------------- | ------------------------------------------------- |
| **Base URL**         | `http://localhost:8000`                           |
| **Documentation**    | `/docs` (Swagger), `/redoc` (ReDoc)               |
| **Version**          | v1 (`/api/v1/...`)                                |
| **Authentification** | JWT Bearer Token (`Authorization: Bearer <token>`) |
| **Rate Limiting**    | 60 req/min standard, 10 req/min IA                |
| **Pagination**       | Offset (`page`, `page_size`) + Cursor (`cursor`)  |

### Réponses communes

| Code | Description |
|------|-------------|
| 200  | Succès |
| 201  | Création réussie |
| 401  | Non authentifié |
| 403  | Accès refusé |
| 404  | Ressource introuvable |
| 422  | Erreur de validation |
| 429  | Rate limit dépassé |
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

## Santé & Informations

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/` | Informations sur l'API (nom, version, status) |
| GET | `/health` | État de l'API et de la base de données |

---

## 🔐 Auth — `/api/v1/auth` (4 endpoints)

Authentification via Supabase Auth + JWT.

| Méthode | Path | Description |
|---------|------|-------------|
| POST | `/auth/login` | Connexion (email, password) → `TokenResponse` |
| POST | `/auth/register` | Inscription (email, password, nom) → `TokenResponse` (201) |
| POST | `/auth/refresh` | Rafraîchit le token JWT |
| GET | `/auth/me` | Profil de l'utilisateur connecté → `UserInfoResponse` |

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

## 🍽️ Recettes — `/api/v1/recettes` (6 endpoints)

CRUD complet des recettes.

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/recettes` | `page`, `page_size`, `categorie?`, `search?` | Liste paginée avec filtres |
| GET | `/recettes/{id}` | — | Détail d'une recette |
| POST | `/recettes` | Body: `RecetteCreate` | Crée une recette |
| PUT | `/recettes/{id}` | Body: `RecetteCreate` | Remplacement complet |
| PATCH | `/recettes/{id}` | Body: `RecettePatch` | Mise à jour partielle |
| DELETE | `/recettes/{id}` | — | Supprime une recette |

---

## 🛒 Courses — `/api/v1/courses` (11 endpoints)

Listes de courses avec collaboration WebSocket.

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/courses` | `page`, `page_size`, `active_only=True` | Liste des listes de courses |
| POST | `/courses` | Body: `CourseListCreate` | Crée une liste (201) |
| GET | `/courses/{id}` | — | Détail avec articles |
| PUT | `/courses/{id}` | Body: `CourseListCreate` | Met à jour le nom |
| DELETE | `/courses/{id}` | — | Supprime liste + articles |
| POST | `/courses/{id}/items` | Body: `CourseItemBase` | Ajoute un article (201) |
| PUT | `/courses/{id}/items/{item_id}` | Body: `CourseItemBase` | Met à jour un article |
| DELETE | `/courses/{id}/items/{item_id}` | — | Supprime un article |
| GET | `/courses/{id}/export` | `group_by=categorie` | Export texte brut |
| POST | `/courses/{id}/checkout-items` | Body: `CheckoutCoursesRequest` | Checkout batch → maj inventaire |
| POST | `/courses/{id}/scan-barcode-checkout` | Body: `ScanBarcodeCheckoutRequest` | Checkout via code-barres |

### WebSocket — `/api/v1/ws/courses/{liste_id}`

Collaboration temps réel sur les listes de courses.

**Connexion:**
```
ws://localhost:8000/api/v1/ws/courses/{liste_id}?user_id=abc123&username=Anne
```

| Param | Type | Description |
|-------|------|-------------|
| `liste_id` | `int` (path) | ID de la liste de courses |
| `user_id` | `str` (query, requis) | Identifiant utilisateur |
| `username` | `str` (query, défaut: "Anonyme") | Nom affiché |

**Messages Client → Serveur** (JSON, champ `action`) :

| Action | Champs | Description |
|--------|--------|-------------|
| `item_added` | `item: {nom, quantite, unite}` | Article ajouté |
| `item_removed` | `item_id: int` | Article supprimé |
| `item_checked` | `item_id: int, checked: bool` | Article coché/décoché |
| `item_updated` | `item_id: int, updates: {...}` | Article modifié |
| `list_renamed` | `new_name: str` | Liste renommée |
| `user_typing` | `typing: bool` | Indicateur de saisie |
| `ping` | — | Keep-alive |

**Messages Serveur → Clients** (JSON, champ `type`) :

| Type | Champs | Description |
|------|--------|-------------|
| `sync` | `action, user_id, username, timestamp, ...data` | Broadcast d'une modification |
| `user_joined` | `user_id, username, timestamp` | Nouvel utilisateur connecté |
| `user_left` | `user_id, username, timestamp` | Utilisateur déconnecté |
| `users_list` | `users: [{user_id, username, connected_at}]` | Liste des connectés (envoyé à la connexion) |
| `error` | `message: str` | Erreur (action inconnue) |
| `pong` | — | Réponse au ping |

Les modifications `item_added`, `item_removed`, `item_checked` et `list_renamed` sont persistées en base de données.

---

## 📦 Inventaire — `/api/v1/inventaire` (6 endpoints)

Gestion des stocks alimentaires.

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/inventaire` | `page`, `page_size=50`, `categorie?`, `emplacement?`, `stock_bas?`, `peremption_proche?` | Liste avec filtres avancés |
| POST | `/inventaire` | Body: `InventaireItemCreate` | Crée un article |
| GET | `/inventaire/barcode/{code}` | — | Recherche par code-barres |
| GET | `/inventaire/{id}` | — | Détail article |
| PUT | `/inventaire/{id}` | Body: `InventaireItemUpdate` | Met à jour (partiel via exclude_unset) |
| DELETE | `/inventaire/{id}` | — | Supprime |

---

## 📅 Planning — `/api/v1/planning` (4 endpoints)

Planification des repas de la semaine.

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/planning/semaine` | `date_debut?` (ISO datetime) | Planning de la semaine |
| POST | `/planning/repas` | Body: `RepasCreate` | Planifie un repas (upsert) |
| PUT | `/planning/repas/{id}` | Body: `RepasCreate` | Met à jour un repas |
| DELETE | `/planning/repas/{id}` | — | Supprime un repas |

---

## 🤖 Suggestions IA — `/api/v1/suggestions` (2 endpoints)

Suggestions via Mistral AI (rate limité : 10 req/min).

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/suggestions/recettes` | `contexte="repas équilibré"`, `nombre=3` (1-10) | Suggestions recettes |
| GET | `/suggestions/planning` | `jours=7` (1-14), `personnes=4` (1-20) | Planning complet IA |

---

## 👨‍👩‍👧‍👦 Famille — `/api/v1/famille` (37 endpoints)

### Contexte familial (1) — Phase M

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/famille/contexte` | — | Contexte familial global (jalons prochains, rappels, suggestions achats urgents, météo) |

### Enfants & Jalons (5)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/famille/enfants` | `page`, `page_size`, `actif=True` | Liste profils enfants |
| GET | `/famille/enfants/{id}` | — | Détail enfant |
| GET | `/famille/enfants/{id}/jalons` | `categorie?` | Jalons de développement |
| POST | `/famille/enfants/{id}/jalons` | Body: titre, description, categorie, date_atteint | Ajoute un jalon (201) |
| DELETE | `/famille/enfants/{id}/jalons/{jalon_id}` | — | Supprime un jalon |

### Activités (6) — Phase O : `suggestions_struct` pour pré-remplissage

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/famille/activites` | `page`, `page_size`, `type_activite?`, `statut?`, `date_debut?`, `date_fin?`, `cursor?` | Liste (offset + cursor) |
| GET | `/famille/activites/{id}` | — | Détail activité |
| POST | `/famille/activites` | Body: titre, type_activite, date_prevue... | Crée (201) |
| PATCH | `/famille/activites/{id}` | Body: champs partiels | Met à jour |
| DELETE | `/famille/activites/{id}` | — | Supprime |
| POST | `/famille/activites/suggestions-ia-auto` | Body: `{type_prefere?, nb_suggestions?}` | Suggestions IA météo-adaptées ; retourne `suggestions` (texte) + `suggestions_struct` (liste d'objets pré-remplissables) |

### Budget familial (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/famille/budget` | `page`, `page_size=50`, `categorie?`, `date_debut?`, `date_fin?` | Dépenses familiales |
| GET | `/famille/budget/stats` | `mois?` (1-12), `annee?` (2020-2030) | Statistiques budget |
| POST | `/famille/budget` | Body: date, categorie, montant, magasin... | Ajoute dépense (201) |
| DELETE | `/famille/budget/{id}` | — | Supprime |

### Achats famille (3) — Phase P

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/famille/achats` | `page`, `page_size`, `categorie?`, `priorite?` | Liste des achats famille (non achetés en priorité) |
| POST | `/famille/achats` | Body: nom, categorie, priorite, description?, suggere_par? | Crée un achat (201) |
| POST | `/famille/achats/suggestions` | Body: `{}` (contexte inféré automatiquement) | Génère des suggestions d'achats proactives IA (anniversaires, jalons, saison) |

> **Réponse `/achats/suggestions`** : `{ suggestions: [{titre, description, source, fourchette_prix?, ou_acheter?, pertinence?}], total }` — source ∈ `"anniversaire" | "jalon" | "saison"`

### Shopping (1)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/famille/shopping` | `liste?`, `categorie?`, `actif=True` | Articles shopping familial (liste générale) |

### Routines familiales (5)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/famille/routines` | `actif?` | Routines avec étapes |
| GET | `/famille/routines/{id}` | — | Détail routine |
| POST | `/famille/routines` | Body: nom, type, est_active, etapes[] | Crée (201) |
| PATCH | `/famille/routines/{id}` | Body: nom, type, est_active | Met à jour |
| DELETE | `/famille/routines/{id}` | — | Supprime |

### Anniversaires (5)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/famille/anniversaires` | `relation?`, `actif=True` | Triés par jours restants |
| GET | `/famille/anniversaires/{id}` | — | Détail |
| POST | `/famille/anniversaires` | Body: `AnniversaireCreate` | Crée (201) |
| PATCH | `/famille/anniversaires/{id}` | Body: `AnniversairePatch` | Met à jour |
| DELETE | `/famille/anniversaires/{id}` | — | Supprime |

### Événements familiaux (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/famille/evenements` | `type_evenement?`, `actif=True` | Liste événements |
| POST | `/famille/evenements` | Body: `EvenementFamilialCreate` | Crée (201) |
| PATCH | `/famille/evenements/{id}` | Body: `EvenementFamilialPatch` | Met à jour |
| DELETE | `/famille/evenements/{id}` | — | Supprime |

### Journal familial (3) — Phase R

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| POST | `/famille/journal/resumer-semaine` | Body: `{date_debut?, style?}` | Génère un résumé IA de la semaine (alias de `POST /famille/journal/ia-semaine`) |
| POST | `/famille/journal/ia-semaine` | Body: `{date_debut?, style?}` | Génère un résumé IA et le sauvegarde avec tag `resume-ia` |
| POST | `/famille/journal/retrospective` | Body: `{periode?}` | Rétrospective IA longue période |

---

## 🏡 Maison — `/api/v1/maison` (111 endpoints)

Module le plus vaste — gestion complète du foyer.

### Projets domestiques (5)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/projets` | `page`, `page_size`, `statut?`, `priorite?` | Liste projets |
| GET | `/maison/projets/{id}` | — | Détail avec tâches |
| POST | `/maison/projets` | Body: dict | Crée (201) |
| PATCH | `/maison/projets/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/projets/{id}` | — | Supprime |

### Routines maison (2)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/routines` | `categorie?`, `actif=True` | Liste routines |
| GET | `/maison/routines/{id}` | — | Détail avec tâches |

### Entretien (4 + 1 dashboard)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/entretien` | `categorie?`, `piece?`, `fait?` | Tâches d'entretien |
| POST | `/maison/entretien` | Body: dict | Crée (201) |
| PATCH | `/maison/entretien/{id}` | Body: dict | Met à jour / marque faite |
| DELETE | `/maison/entretien/{id}` | — | Supprime |
| GET | `/maison/entretien/sante-appareils` | — | Dashboard santé appareils |

### Jardin (6)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/jardin` | `type_element?`, `statut?` | Éléments du jardin |
| GET | `/maison/jardin/{id}/journal` | — | Journal d'entretien |
| POST | `/maison/jardin` | Body: dict | Ajoute élément (201) |
| PATCH | `/maison/jardin/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/jardin/{id}` | — | Supprime |
| GET | `/maison/jardin/calendrier-semis` | `mois?` (1-12) | Calendrier des semis |

### Stocks consommables (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/stocks` | `categorie?`, `alerte_stock=False` | Stocks maison |
| POST | `/maison/stocks` | Body: dict | Crée (201) |
| PATCH | `/maison/stocks/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/stocks/{id}` | — | Supprime |

### Meubles / Wishlist (5)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/meubles` | `piece?`, `statut?`, `priorite?` | Wishlist meubles |
| POST | `/maison/meubles` | Body: dict | Crée (201) |
| PATCH | `/maison/meubles/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/meubles/{id}` | — | Supprime |
| GET | `/maison/meubles/budget` | — | Résumé budget meubles |

### Cellier (9)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/cellier` | `categorie?`, `emplacement?` | Articles du cellier |
| GET | `/maison/cellier/alertes/peremption` | `jours=14` (1-90) | Alertes péremption |
| GET | `/maison/cellier/alertes/stock` | — | Alertes stock bas |
| GET | `/maison/cellier/stats` | — | Statistiques cellier |
| GET | `/maison/cellier/{id}` | — | Détail article |
| POST | `/maison/cellier` | Body: dict | Ajoute (201) |
| PATCH | `/maison/cellier/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/cellier/{id}` | — | Supprime |
| PATCH | `/maison/cellier/{id}/quantite` | Body: `{delta: int}` | Ajuste quantité +/- |

### Artisans (9)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/artisans` | `metier?` | Carnet d'adresses |
| GET | `/maison/artisans/stats` | — | Stats artisans |
| GET | `/maison/artisans/{id}` | — | Détail |
| POST | `/maison/artisans` | Body: dict | Crée (201) |
| PATCH | `/maison/artisans/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/artisans/{id}` | — | Supprime |
| GET | `/maison/artisans/{id}/interventions` | — | Historique interventions |
| POST | `/maison/artisans/{id}/interventions` | Body: dict | Enregistre intervention (201) |
| DELETE | `/maison/artisans/interventions/{id}` | — | Supprime intervention |

### Contrats (7)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/contrats` | `type_contrat?`, `statut?` | Liste contrats |
| GET | `/maison/contrats/alertes` | `jours=60` (1-365) | Renouvellements à venir |
| GET | `/maison/contrats/resume-financier` | — | Résumé financier |
| GET | `/maison/contrats/{id}` | — | Détail |
| POST | `/maison/contrats` | Body: dict | Crée (201) |
| PATCH | `/maison/contrats/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/contrats/{id}` | — | Supprime |

### Garanties (10)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/garanties` | `statut?`, `piece?` | Liste garanties |
| GET | `/maison/garanties/alertes` | `jours=60` (1-365) | Garanties expirant |
| GET | `/maison/garanties/stats` | — | Stats garanties |
| GET | `/maison/garanties/{id}` | — | Détail |
| POST | `/maison/garanties` | Body: dict | Enregistre (201) |
| PATCH | `/maison/garanties/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/garanties/{id}` | — | Supprime |
| GET | `/maison/garanties/{id}/incidents` | — | Incidents SAV |
| POST | `/maison/garanties/{id}/incidents` | Body: dict | Enregistre incident (201) |
| PATCH | `/maison/garanties/incidents/{id}` | Body: dict | Met à jour incident |

### Diagnostics immobiliers (6)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/diagnostics` | — | Diagnostics immobiliers |
| GET | `/maison/diagnostics/alertes` | `jours=90` (1-365) | Validité expirant |
| GET | `/maison/diagnostics/validite-types` | — | Durées validité par type |
| POST | `/maison/diagnostics` | Body: dict | Enregistre (201) |
| PATCH | `/maison/diagnostics/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/diagnostics/{id}` | — | Supprime |

### Estimations immobilières (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/estimations` | — | Estimations |
| GET | `/maison/estimations/derniere` | — | Dernière estimation |
| POST | `/maison/estimations` | Body: dict | Enregistre (201) |
| DELETE | `/maison/estimations/{id}` | — | Supprime |

### Éco-Tips (5)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/eco-tips` | `actif_only=False` | Actions écologiques |
| GET | `/maison/eco-tips/{id}` | — | Détail |
| POST | `/maison/eco-tips` | Body: dict | Crée (201) |
| PATCH | `/maison/eco-tips/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/eco-tips/{id}` | — | Supprime |

### Dépenses maison (8)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/depenses` | `mois?` (1-12), `annee?` | Dépenses maison |
| GET | `/maison/depenses/stats` | — | Stats globales |
| GET | `/maison/depenses/historique/{categorie}` | `nb_mois=12` (1-36) | Historique par catégorie |
| GET | `/maison/depenses/energie/{type_energie}` | `nb_mois=12` (1-36) | Conso énergie |
| GET | `/maison/depenses/{id}` | — | Détail |
| POST | `/maison/depenses` | Body: dict | Enregistre (201) |
| PATCH | `/maison/depenses/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/depenses/{id}` | — | Supprime |

### Nuisibles (5)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/nuisibles` | — | Traitements anti-nuisibles |
| GET | `/maison/nuisibles/prochains` | `jours=30` (1-180) | Prochains traitements |
| POST | `/maison/nuisibles` | Body: dict | Enregistre (201) |
| PATCH | `/maison/nuisibles/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/nuisibles/{id}` | — | Supprime |

### Devis comparatifs (6)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/devis` | `projet_id?` | Devis |
| POST | `/maison/devis` | Body: dict | Crée (201) |
| PATCH | `/maison/devis/{id}` | Body: dict | Met à jour |
| DELETE | `/maison/devis/{id}` | — | Supprime |
| POST | `/maison/devis/{id}/lignes` | Body: dict | Ajoute une ligne (201) |
| POST | `/maison/devis/{id}/choisir` | — | Accepte un devis |

### Entretien saisonnier (6)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/entretien-saisonnier` | — | Tâches saisonnières |
| GET | `/maison/entretien-saisonnier/alertes` | — | Tâches à faire ce mois |
| POST | `/maison/entretien-saisonnier` | Body: dict | Crée (201) |
| DELETE | `/maison/entretien-saisonnier/{id}` | — | Supprime |
| PATCH | `/maison/entretien-saisonnier/{id}/fait` | — | Marque fait |
| POST | `/maison/entretien-saisonnier/reset` | — | Reset annuel checklist |

### Relevés compteurs (3)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/releves` | — | Relevés compteurs |
| POST | `/maison/releves` | Body: dict | Enregistre (201) |
| DELETE | `/maison/releves/{id}` | — | Supprime |

### Visualisation maison (5)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/visualisation/pieces` | `etage?` | Pièces avec détails |
| GET | `/maison/visualisation/etages` | — | Étages disponibles |
| GET | `/maison/visualisation/pieces/{id}/historique` | — | Historique travaux |
| GET | `/maison/visualisation/pieces/{id}/objets` | — | Objets dans une pièce |
| POST | `/maison/visualisation/positions` | Body: `{pieces: [...]}` | Sauvegarde layout drag-and-drop |

### Hub maison (1)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/maison/hub/stats` | — | Stats dashboard maison |

---

## 🎮 Jeux — `/api/v1/jeux` (11 endpoints)

Paris sportifs et loterie.

### Équipes (2)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/jeux/equipes` | `championnat?`, `search?` | Équipes football |
| GET | `/jeux/equipes/{id}` | — | Détail équipe |

### Matchs (2)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/jeux/matchs` | `page`, `page_size`, `championnat?`, `joue?`, `date_debut?`, `date_fin?`, `cursor?` | Liste (offset + cursor) |
| GET | `/jeux/matchs/{id}` | — | Détail avec paris |

### Paris sportifs (5)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/jeux/paris` | `page`, `page_size=50`, `statut?`, `est_virtuel?` | Liste paris |
| GET | `/jeux/paris/stats` | `est_virtuel?` | Statistiques |
| POST | `/jeux/paris` | Body: match_id, prediction, cote, mise... | Crée (201) |
| PATCH | `/jeux/paris/{id}` | Body: statut, gain, notes | Met à jour |
| DELETE | `/jeux/paris/{id}` | — | Supprime |

### Loto (2)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/jeux/loto/tirages` | `page`, `page_size=50` | Tirages loto |
| GET | `/jeux/loto/grilles` | `est_virtuelle?` | Grilles jouées |

---

## 📊 Dashboard — `/api/v1/dashboard` (1 endpoint)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/dashboard` | Données agrégées : stats, budget mois, activités, alertes |

---

## 🍳 Batch Cooking — `/api/v1/batch-cooking` (7 endpoints)

Sessions de préparation en lot.

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/batch-cooking` | `page`, `page_size`, `statut?` | Liste sessions |
| GET | `/batch-cooking/{id}` | — | Détail avec étapes |
| POST | `/batch-cooking` | Body: `SessionBatchCreate` | Crée session |
| PATCH | `/batch-cooking/{id}` | Body: `SessionBatchPatch` | Met à jour |
| DELETE | `/batch-cooking/{id}` | — | Supprime |
| GET | `/batch-cooking/preparations` | `consomme?` | Préparations en stock |
| GET | `/batch-cooking/config` | — | Configuration batch |

---

## ♻️ Anti-Gaspillage — `/api/v1/anti-gaspillage` (1 endpoint)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/anti-gaspillage` | `jours=7` (1-30) | Score, articles urgents, recettes rescue |

---

## ⚙️ Préférences — `/api/v1/preferences` (3 endpoints)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/preferences` | — | Préférences utilisateur |
| PUT | `/preferences` | Body: `PreferencesCreate` | Upsert complet |
| PATCH | `/preferences` | Body: `PreferencesPatch` | Mise à jour partielle |

---

## 📄 Export PDF — `/api/v1/export` (1 endpoint)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| POST | `/export/pdf` | `type_export` (courses, planning, recette, budget), `id_ressource?` | Génère PDF (StreamingResponse) |

> `id_ressource` requis pour `type_export=recette` et `type_export=planning`.

---

## 📆 Calendriers — `/api/v1/calendriers` (6 endpoints)

Calendriers externes synchronisés.

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/calendriers` | `provider?`, `enabled?` | Liste calendriers |
| GET | `/calendriers/{id}` | — | Détail |
| GET | `/calendriers/evenements` | `page`, `page_size=50`, `calendrier_id?`, `date_debut?`, `date_fin?`, `all_day?`, `cursor?` | Événements (offset + cursor) |
| GET | `/calendriers/evenements/{id}` | — | Détail événement |
| GET | `/calendriers/evenements/aujourd-hui` | — | Événements du jour |
| GET | `/calendriers/evenements/semaine` | `date_debut?` | Événements semaine groupés par jour |

---

## 📑 Documents — `/api/v1/documents` (5 endpoints)

Documents familiaux (passeports, assurances, etc.).

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/documents` | `categorie?`, `membre?`, `expire?`, `search?`, `page`, `page_size` | Liste avec filtres |
| GET | `/documents/{id}` | — | Détail |
| POST | `/documents` | Body: `DocumentCreate` | Crée (201) |
| PATCH | `/documents/{id}` | Body: `DocumentPatch` | Met à jour |
| DELETE | `/documents/{id}` | — | Soft delete (actif=False) |

---

## 🔧 Utilitaires — `/api/v1/utilitaires` (24 endpoints)

### Notes mémo (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/utilitaires/notes` | `categorie?`, `epingle?`, `archive=False`, `search?` | Notes |
| POST | `/utilitaires/notes` | Body: `NoteCreate` | Crée |
| PATCH | `/utilitaires/notes/{id}` | Body: `NotePatch` | Met à jour |
| DELETE | `/utilitaires/notes/{id}` | — | Supprime |

### Journal de bord (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/utilitaires/journal` | `humeur?`, `limit=30` (1-365) | Entrées journal |
| POST | `/utilitaires/journal` | Body: `JournalCreate` | Crée |
| PATCH | `/utilitaires/journal/{id}` | Body: `JournalPatch` | Met à jour |
| DELETE | `/utilitaires/journal/{id}` | — | Supprime |

### Contacts utiles (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/utilitaires/contacts` | `categorie?`, `favori?`, `search?` | Contacts |
| POST | `/utilitaires/contacts` | Body: `ContactCreate` | Crée |
| PATCH | `/utilitaires/contacts/{id}` | Body: `ContactPatch` | Met à jour |
| DELETE | `/utilitaires/contacts/{id}` | — | Supprime |

### Liens favoris (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/utilitaires/liens` | `categorie?`, `favori?` | Liens |
| POST | `/utilitaires/liens` | Body: `LienCreate` | Crée |
| PATCH | `/utilitaires/liens/{id}` | Body: `LienPatch` | Met à jour |
| DELETE | `/utilitaires/liens/{id}` | — | Supprime |

### Mots de passe maison (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/utilitaires/passwords` | `categorie?` | Mots de passe (chiffrés) |
| POST | `/utilitaires/passwords` | Body: `MotDePasseCreate` | Crée |
| PATCH | `/utilitaires/passwords/{id}` | Body: `MotDePassePatch` | Met à jour |
| DELETE | `/utilitaires/passwords/{id}` | — | Supprime |

### Énergie (4)

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| GET | `/utilitaires/energie` | `type_energie?` (electricite/gaz/eau), `annee?` | Relevés énergie |
| POST | `/utilitaires/energie` | Body: `EnergieCreate` | Crée |
| PATCH | `/utilitaires/energie/{id}` | Body: `EnergiePatch` | Met à jour |
| DELETE | `/utilitaires/energie/{id}` | — | Supprime |

---

## 🔔 Push Notifications — `/api/v1/push` (3 endpoints)

Web Push via service worker.

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| POST | `/push/subscribe` | Body: `PushSubscriptionRequest` | Enregistre abonnement |
| DELETE | `/push/unsubscribe` | Body: `PushUnsubscribeRequest` | Supprime abonnement |
| GET | `/push/status` | — | Statut notifications |

---

## 🔗 Webhooks — `/api/v1/webhooks` (6 endpoints)

Webhooks sortants avec signature HMAC.

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| POST | `/webhooks` | Body: `WebhookCreate` | Crée (secret HMAC auto-généré) (201) |
| GET | `/webhooks` | — | Liste mes webhooks |
| GET | `/webhooks/{id}` | — | Détail |
| PUT | `/webhooks/{id}` | Body: `WebhookUpdate` | Met à jour |
| DELETE | `/webhooks/{id}` | — | Supprime (204) |
| POST | `/webhooks/{id}/test` | — | Ping de test |

---

## 📁 Upload — `/api/v1/upload` (3 endpoints)

Upload vers Supabase Storage.

| Méthode | Path | Params | Description |
|---------|------|--------|-------------|
| POST | `/upload` | `bucket="documents"`, Body: `UploadFile` (multipart, 10MB max) | Upload fichier |

---

## Résumé par module

| Module | Préfixe | Endpoints |
|--------|---------|-----------|
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
| Préférences | `/api/v1/preferences` | 3 |
| Export PDF | `/api/v1/export` | 1 |
| Calendriers | `/api/v1/calendriers` | 6 |
| Documents | `/api/v1/documents` | 5 |
| Utilitaires | `/api/v1/utilitaires` | 24 |
| Push | `/api/v1/push` | 3 |
| Webhooks | `/api/v1/webhooks` | 6 |
| Upload | `/api/v1/upload` | 3 |
| **Total** | | **242** |
