# 📚 Guide Fonctionnalités Assistant Matanne

## Vue d'ensemble

Ce document décrit les fonctionnalités implémentées dans l'application.

---

## 🍳 Import de Recettes

### Sources supportées

| Source           | Statut         | Fichier                         |
| ---------------- | -------------- | ------------------------------- |
| **Marmiton**     | ✅ Fonctionnel | `src/services/recipe_import.py` |
| **CuisineAZ**    | ✅ Fonctionnel | `src/services/recipe_import.py` |
| **Autres sites** | ✅ Fallback IA | Parser générique + Mistral AI   |
| **PDF**          | ⚠️ Basique     | Extraction texte simple         |
| **Manuel**       | ✅ Complet     | Formulaire UI complet           |

### Comment ça marche

```python
from src.services.recipe_import import RecipeImportService

service = RecipeImportService()

# Depuis URL
result = await service.import_from_url("https://www.marmiton.org/...")

# Depuis PDF
result = await service.import_from_pdf(uploaded_file)
```

### Parsers spécialisés

- `MarmitonParser` - Extraction optimisée pour marmiton.org
- `CuisineAZParser` - Pour cuisineaz.com
- `GenericRecipeParser` - Fallback avec IA pour autres sites

---

## 📦 Gestion de l'Inventaire

### Code-barres

| Fonctionnalité    | Statut | Détails               |
| ----------------- | ------ | --------------------- |
| Scanner caméra    | ✅     | WebRTC + zxing        |
| Validation EAN-13 | ✅     | Avec checksum         |
| Validation EAN-8  | ✅     | Avec checksum         |
| Validation UPC    | ✅     | Avec checksum         |
| QR codes          | ✅     | Format alphanumérique |

```python
from src.services.barcode import BarcodeService

service = BarcodeService()
is_valid, type_code = service.valider_barcode("3017620422003")
# (True, "EAN-13")
```

### OpenFoodFacts (NOUVEAU)

Enrichissement automatique des produits scannés:

```python
from src.services.openfoodfacts import get_openfoodfacts_service

service = get_openfoodfacts_service()
produit = service.rechercher_produit("3017620422003")

print(produit.nom)           # "Nutella"
print(produit.marque)        # "Ferrero"
print(produit.nutrition.nutriscore)  # "E"
```

**Données récupérées:**

- Nom, marque, quantité
- Informations nutritionnelles (pour 100g)
- Nutriscore, Nova, Ecoscore
- Ingrédients, allergènes, traces
- Images produit
- Labels (Bio, Sans gluten...)

### Ajout manuel

Interface dans `src/modules/cuisine/ui/inventaire.py`:

- Nom, catégorie, quantité, unité
- Code-barres (optionnel)
- Date de péremption
- Lieu de stockage
- Seuil minimum (pour alertes)

---

## ⚠️ Dates de Péremption

### Modèle de données

```sql
-- Table inventaire
date_peremption DATE,  -- Date limite de consommation

-- Table preparations_batch
date_peremption DATE NOT NULL,  -- Péremption des preps batch
```

### Calcul des alertes

```python
# Dans src/services/predictions.py
jours_restants = (article.date_peremption - date.today()).days

if jours_restants <= 0:
    niveau = "PÉRIMÉ"
elif jours_restants <= 2:
    niveau = "CRITIQUE"
elif jours_restants <= 5:
    niveau = "ATTENTION"
```

### Affichage

- 🔴 **Périmé** - À jeter
- 🟠 **< 2 jours** - À consommer en priorité
- 🟡 **< 5 jours** - Attention
- 🟢 **> 5 jours** - OK

---

## 📊 Seuils de Stock (Réapprovisionnement)

### Modèle de données

```sql
-- Table inventaire
quantite FLOAT NOT NULL,      -- Stock actuel
quantite_min FLOAT NOT NULL,  -- Seuil minimum d'alerte

CONSTRAINT ck_seuil_positif CHECK (quantite_min >= 0)
```

### Logique d'alerte

```python
# Dans src/services/inventaire.py
def calculer_niveau_stock(article) -> str:
    ratio = article.quantite / article.quantite_min if article.quantite_min > 0 else float('inf')

    if ratio <= 0:
        return "RUPTURE"      # Stock = 0
    elif ratio < 1:
        return "CRITIQUE"     # En dessous du seuil
    elif ratio < 1.5:
        return "BAS"          # Proche du seuil
    else:
        return "OK"
```

### Index pour performances

```sql
CREATE INDEX idx_inventaire_stock_bas ON inventaire(quantite, quantite_min);
```

### Prédictions de rupture

```python
from src.services.cuisine.suggestions import InventairePredictionService

service = InventairePredictionService()
prediction = service.predire_rupture_stock(article_id)

print(f"Rupture estimée dans {prediction.jours_avant_rupture} jours")
print(f"Consommation moyenne: {prediction.taux_consommation_jour}/jour")
```

---

## 📅 Google Calendar

### Configuration

Ajoutez dans `.env.local`:

```
GOOGLE_CLIENT_ID=votre_client_id
GOOGLE_CLIENT_SECRET=votre_client_secret
```

### Fonctionnalités

| Fonctionnalité        | Statut         |
| --------------------- | -------------- |
| OAuth2                | ✅ Implémenté  |
| Import événements     | ✅ Fonctionnel |
| Export planning       | ✅ Fonctionnel |
| Sync bidirectionnelle | ✅ Fonctionnel |

### Utilisation

```python
from src.services.calendrier import get_calendar_sync_service

service = get_calendar_sync_service()

# 1. Générer URL d'auth
auth_url = service.get_google_auth_url(user_id, redirect_uri)

# 2. Après callback OAuth
config = service.handle_google_callback(user_id, code, redirect_uri)

# 3. Synchroniser (import + export bidirectionnel)
result = service.sync_google_calendar(config)
# result.events_imported = nombre importés de Google
# result.events_exported = nombre exportés vers Google

# 4. Export uniquement vers Google
result = service.export_planning_to_google(user_id, config)
```

### Export vers Google Calendar

Les repas et activités sont automatiquement exportés:

| Type     | Format                   | Couleur  |
| -------- | ------------------------ | -------- |
| Repas    | 🍽️ Déjeuner: Poulet rôti | Standard |
| Activité | 👨‍👩‍👧 Sortie parc           | Bleu     |

Les événements utilisent `extendedProperties` pour éviter les doublons lors des syncs répétées.

### UI de configuration

Nouveau composant: `src/ui/components/google_calendar_sync.py`

---

## 🛒 Organisation des Courses

### APIs Magasins

**⚠️ IMPORTANT:** Il n'existe PAS d'API publique gratuite pour:

- Carrefour Drive
- Thiriet
- Grand Frais
- Bio Coop
- Picard

### Solution implémentée

Organisation intelligente SANS API directe:

```python
from src.services.courses_organisation import get_courses_organisation_service

service = get_courses_organisation_service()

# Organiser par magasin
listes = service.organiser_liste(articles)

# Export pour Bring! (copier-coller)
texte = service.exporter_bring(listes[Magasin.CARREFOUR_DRIVE])

# Export JSON pour AnyList
json_data = service.exporter_json_anylist(liste)

# HTML imprimable
html = service.generer_html_imprimable(listes)
```

### Mapping automatique magasins

| Type produit | Magasin suggéré |
| ------------ | --------------- |
| Bio          | Bio Coop        |
| Surgelés     | Thiriet         |
| Frais/Herbes | Grand Frais     |
| Général      | Carrefour Drive |

---

## 🏗️ Architecture des nouveaux modules

### Calendrier Unifié

- Logic: `src/modules/planning/logic/calendrier_logic.py`
- UI: `src/modules/planning/ui/calendrier.py`

### Planificateur Repas (style Jow)

- Logic: `src/modules/cuisine/logic/planificateur_repas_logic.py`
- UI: `src/modules/cuisine/ui/planificateur_repas.py`

### Batch Cooking Détaillé

- Logic existante: `src/modules/cuisine/logic/batch_cooking_logic.py`
- UI: `src/modules/cuisine/ui/batch_cooking_detaille.py`

---

## 🔧 Services ajoutés

| Service              | Fichier                                     | Description              |
| -------------------- | ------------------------------------------- | ------------------------ |
| OpenFoodFacts        | `src/services/openfoodfacts.py`             | Enrichissement produits  |
| Courses Organisation | `src/services/courses_organisation.py`      | Organisation par magasin |
| Google Calendar UI   | `src/ui/components/google_calendar_sync.py` | Interface sync           |

---

## ⚙️ Nouveaux Modèles (Migration 016)

Tables ajoutées pour l'apprentissage IA et les intégrations:

### UserPreference

Préférences familiales persistantes (remplace session_state):

```python
from src.core.models import UserPreference

# Champs principaux:
# - user_id: Identifiant unique
# - nb_adultes, jules_present, jules_age_mois
# - temps_semaine, temps_weekend
# - aliments_exclus, aliments_favoris (JSONB)
# - poisson_par_semaine, vegetarien_par_semaine
# - robots, magasins_preferes (JSONB)
```

### RecipeFeedback

Feedbacks 👍/👎 pour apprentissage IA:

```python
from src.core.models import RecipeFeedback, FeedbackType

# Relation avec Recette
feedback = RecipeFeedback(
    user_id="matanne",
    recette_id=123,
    feedback=FeedbackType.LIKE.value,  # "like", "dislike", "neutral"
    contexte="batch_cooking"
)
```

### OpenFoodFactsCache

Cache persistant des produits scannés:

```python
from src.core.models import OpenFoodFactsCache

# Cache automatique via service
cache = OpenFoodFactsCache(
    code_barres="3017620422003",
    nom="Nutella",
    marque="Ferrero",
    nutriscore="E",
    nova_group=4,
    nutrition_data={...}
)
```

### ExternalCalendarConfig

Configuration calendriers externes (Google, Apple):

```python
from src.core.models import ExternalCalendarConfig, CalendarProviderNew

config = ExternalCalendarConfig(
    user_id="matanne",
    provider=CalendarProviderNew.GOOGLE.value,
    name="Calendrier famille",
    access_token="...",
    sync_direction="both"
)
```

### Migration

```bash
# Via Alembic
python manage.py migrate

# Ou SQL direct sur Supabase
sql/016_add_user_preferences.sql
```

---

## ✅ Nettoyage Effectué (2026-02-02)

### Modules UI unifiés

Le routeur `lazy_loader.py` pointe maintenant vers les nouveaux modules:

| Route                      | Ancien             | Nouveau                     |
| -------------------------- | ------------------ | --------------------------- |
| `cuisine.planning_semaine` | `planning.py`      | `planificateur_repas.py`    |
| `cuisine.batch_cooking`    | `batch_cooking.py` | `batch_cooking_detaille.py` |

Les anciens fichiers sont conservés sous:

- `cuisine.planning_legacy` → `planning.py`
- `cuisine.batch_cooking_legacy` → `batch_cooking.py`

### Services Planning consolidés

| Service             | Factory                          | Description                                   |
| ------------------- | -------------------------------- | --------------------------------------------- |
| `PlanningService`   | `get_planning_service()`         | Planning repas classique                      |
| `PlanningAIService` | `get_planning_unified_service()` | Planning unifié (repas + activités + projets) |

Exports ajoutés dans `src/services/__init__.py`:

- `JourPlanning`, `ParametresEquilibre`
- `JourCompletSchema`, `SemaineCompleSchema`

### Tests ajoutés

Nouveau fichier: `tests/services/test_new_services.py`

- Tests OpenFoodFactsService
- Tests CoursesOrganisationService
- Tests Planning exports
- Tests nouveaux modèles UserPreference
