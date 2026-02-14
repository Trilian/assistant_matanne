# 🔧 Services Reference - Assistant Matanne

Documentation des services backend et de leurs APIs internes.

## Vue d'ensemble

L'architecture des services suit un modèle en couches:

```text
┌─────────────────────────────────────────────────────────┐
│                    UI (Streamlit)                        │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                  Services Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Recettes │ │  Budget  │ │ Weather  │ │  Backup  │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       └────────────┴─────┬──────┴────────────┘          │
│                          │                               │
│                   BaseAIService                          │
│                (rate limit, cache)                       │
└──────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    Core Layer                            │
│  Database │ Models │ AI Client │ Cache │ Config         │
└─────────────────────────────────────────────────────────┘
```

## 📦 Services disponibles

### Recettes (`src/services/recettes/`)

**Service principal de gestion des recettes.**

```python
from src.services.recettes import get_recette_service

service = get_recette_service()

# CRUD
recette = service.creer_recette(data)
recettes = service.lister_recettes(categorie="dessert")
service.mettre_a_jour_recette(id, data)
service.supprimer_recette(id)

# Suggestions IA
suggestions = service.suggerer_recettes(
    type_repas="diner",
    personnes=4,
    temps_max=30
)

# Import URL
recette = service.importer_depuis_url("https://...")
```

| Méthode                           | Description                |
| --------------------------------- | -------------------------- |
| `creer_recette(data)`             | Créer une nouvelle recette |
| `lister_recettes()`               | Liste paginée avec filtres |
| `obtenir_recette(id)`             | Détails d'une recette      |
| `mettre_a_jour_recette(id, data)` | Modifier une recette       |
| `supprimer_recette(id)`           | Supprimer une recette      |
| `suggerer_recettes()`             | Suggestions IA             |
| `importer_depuis_url(url)`        | Import depuis URL          |

---

### Courses (`src/services/courses/`)

**Gestion des listes de courses.**

```python
from src.services.courses import get_courses_service

service = get_courses_service()

# Listes
liste = service.creer_liste("Courses semaine")
listes = service.lister_listes()
service.supprimer_liste(id)

# Articles
service.ajouter_article(liste_id, "Pain", quantite=2)
service.marquer_fait(article_id)
service.generer_depuis_planning(semaine="2025-W03")
```

| Méthode                     | Description                    |
| --------------------------- | ------------------------------ |
| `creer_liste(nom)`          | Nouvelle liste                 |
| `lister_listes()`           | Toutes les listes              |
| `ajouter_article()`         | Ajouter un article             |
| `marquer_fait(id, fait)`    | Toggle article fait            |
| `generer_depuis_planning()` | Générer depuis repas planifiés |
| `suggerer_articles()`       | Suggestions IA                 |

---

### Inventaire (`src/services/inventaire/`)

**Gestion du stock alimentaire.**

```python
from src.services.inventaire import get_inventaire_service

service = get_inventaire_service()

# Stock
articles = service.lister_articles()
article = service.ajouter_article(nom="Lait", quantite=2)
service.consommer(id, quantite=1)

# Code-barres
article = service.rechercher_barcode("3017760000123")
info = service.obtenir_info_produit("3017760000123")

# Alertes
expirant = service.articles_expirant_bientot(jours=7)
```

| Méthode                       | Description               |
| ----------------------------- | ------------------------- |
| `lister_articles()`           | Inventaire complet        |
| `ajouter_article()`           | Ajouter au stock          |
| `consommer(id, qte)`          | Décrémenter quantité      |
| `rechercher_barcode()`        | Recherche par code-barres |
| `obtenir_info_produit()`      | Info OpenFoodFacts        |
| `articles_expirant_bientot()` | Alertes péremption        |

---

### Budget (`src/services/budget/`)

**Suivi des dépenses familiales.**

```python
from src.services.budget import get_budget_service

service = get_budget_service()

# Dépenses
depense = service.ajouter_depense(
    montant=45.50,
    categorie="courses",
    description="Supermarché"
)
depenses = service.lister_depenses(mois="2025-01")
total = service.total_mois("2025-01")

# Budget
budget = service.definir_budget_mensuel(montant=500, categorie="courses")
reste = service.budget_restant("courses", "2025-01")

# Analyse IA
analyse = service.analyser_depenses_ia(mois="2025-01")
```

| Méthode                    | Description        |
| -------------------------- | ------------------ |
| `ajouter_depense()`        | Nouvelle dépense   |
| `lister_depenses()`        | Liste avec filtres |
| `total_mois()`             | Total mensuel      |
| `definir_budget_mensuel()` | Définir un budget  |
| `budget_restant()`         | Calcul reste       |
| `analyser_depenses_ia()`   | Analyse IA         |

---

### Planning (`src/services/planning/`)

**Planification des repas et activités.**

```python
from src.services.planning import get_planning_service

service = get_planning_service()

# Repas
repas = service.ajouter_repas(
    date="2025-01-20",
    type_repas="diner",
    recette_id=42
)
semaine = service.planning_semaine("2025-W03")
service.supprimer_repas(id)

# Suggestions IA
suggestions = service.suggerer_repas_semaine()
```

| Méthode                    | Description           |
| -------------------------- | --------------------- |
| `ajouter_repas()`          | Planifier un repas    |
| `planning_semaine()`       | Récupérer la semaine  |
| `supprimer_repas()`        | Retirer un repas      |
| `suggerer_repas_semaine()` | Suggestions IA        |
| `generer_liste_courses()`  | Liste depuis planning |

---

### Calendrier (`src/services/calendrier/`)

**Synchronisation calendriers externes.**

```python
from src.services.calendrier import get_calendrier_service

service = get_calendrier_service()

# iCal
url = service.generer_ical_url()
events = service.exporter_ical(type="repas")

# Sync externe
service.sync_google_calendar(token)
service.sync_apple_calendar(subscription_url)
```

| Méthode                  | Description   |
| ------------------------ | ------------- |
| `generer_ical_url()`     | URL flux iCal |
| `exporter_ical()`        | Export iCal   |
| `sync_google_calendar()` | Sync Google   |
| `sync_apple_calendar()`  | Sync Apple    |

---

### Weather (`src/services/weather/`)

**Alertes météo pour le jardin.**

```python
from src.services.weather import get_weather_service

service = get_weather_service()

# Météo
meteo = service.obtenir_meteo_actuelle()
previsions = service.previsions_7j()

# Alertes jardin
alertes = service.alertes_jardin()
# Ex: ["⚠️ Gel prévu cette nuit", "🌧️ Pluie demain"]
```

| Méthode                    | Description            |
| -------------------------- | ---------------------- |
| `obtenir_meteo_actuelle()` | Conditions actuelles   |
| `previsions_7j()`          | Prévisions semaine     |
| `alertes_jardin()`         | Alertes pour jardinier |

---

### Backup (`src/services/backup/`)

**Sauvegarde et restauration.**

```python
from src.services.backup import get_backup_service

service = get_backup_service()

# Sauvegarde
backup = service.creer_sauvegarde(tables=["recettes", "inventaire"])
# Retourne: {"id": "...", "fichier": "backup_2025-01-18.json"}

# Restauration
service.restaurer(backup_id)

# Historique
backups = service.lister_sauvegardes()
```

| Méthode                | Description              |
| ---------------------- | ------------------------ |
| `creer_sauvegarde()`   | Nouvelle sauvegarde      |
| `restaurer(id)`        | Restaurer une sauvegarde |
| `lister_sauvegardes()` | Historique               |
| `supprimer_anciens()`  | Nettoyage                |

---

### Notifications (`src/services/notifications/`)

**Notifications push et in-app.**

```python
from src.services.notifications import get_notification_service

service = get_notification_service()

# Abonnement
service.enregistrer_souscription(endpoint, keys)
service.retirer_souscription(endpoint)

# Envoi
service.envoyer_notification(
    titre="Rappel",
    corps="Yaourts expirent demain",
    type="inventaire"
)

# Notifications in-app
notifs = service.lister_notifications(non_lues=True)
service.marquer_lue(id)
```

| Méthode                      | Description          |
| ---------------------------- | -------------------- |
| `enregistrer_souscription()` | Web Push subscribe   |
| `envoyer_notification()`     | Envoyer push         |
| `lister_notifications()`     | In-app notifications |
| `marquer_lue()`              | Marquer comme lue    |

---

### Suggestions (`src/services/suggestions/`)

**Engine de suggestions IA.**

```python
from src.services.suggestions import get_suggestions_service

service = get_suggestions_service()

# Recettes
recettes = service.suggerer_recettes(
    ingredients_disponibles=["poulet", "riz"],
    type_repas="diner",
    temps_max=45
)

# Prédictions
predictions = service.predire_courses_semaine()
# Basé sur historique et habitudes
```

| Méthode                     | Description          |
| --------------------------- | -------------------- |
| `suggerer_recettes()`       | Suggestions recettes |
| `predire_courses_semaine()` | Prédiction courses   |
| `analyser_habitudes()`      | Analyse patterns     |

---

### Garmin (`src/services/garmin/`)

**Intégration tracker fitness Garmin.**

```python
from src.services.garmin import get_garmin_service

service = get_garmin_service()

# Données
activites = service.obtenir_activites(jours=7)
stats = service.statistiques_semaine()

# Sync
service.synchroniser()
```

---

### Batch Cooking (`src/services/batch_cooking/`)

**Planification batch cooking.**

```python
from src.services.batch_cooking import get_batch_cooking_service

service = get_batch_cooking_service()

# Planification
plan = service.generer_plan_batch(
    portions_semaine=20,
    temps_disponible=3  # heures
)

# Liste courses
liste = service.generer_liste_courses_batch(plan_id)
```

---

## 🔧 Base Services

### BaseAIService

Classe de base pour les services utilisant l'IA.

```python
from src.services.base import BaseAIService

class MonService(BaseAIService):
    def ma_methode_ia(self, prompt: str):
        # Utilise automatiquement:
        # - Rate limiting
        # - Cache sémantique
        # - Retry logic
        return self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=MonSchema,
            system_prompt="Tu es un expert..."
        )
```

**Méthodes disponibles:**

- `call_ai_sync(prompt)` - Appel simple
- `call_with_json_parsing_sync(prompt, model)` - Parsing JSON
- `call_with_list_parsing_sync(prompt, item_model)` - Parsing liste

### BaseIOService

Classe de base pour les opérations I/O.

```python
from src.services.base import BaseIOService

class MonService(BaseIOService):
    def exporter_donnees(self):
        return self.exporter_json(data, "export.json")

    def importer_donnees(self, fichier):
        return self.importer_json(fichier)
```

---

## 📚 Conventions

### Factory Pattern

Tous les services exportent une fonction factory:

```python
# Correct
from src.services.recettes import get_recette_service
service = get_recette_service()

# Éviter
from src.services.recettes.service import RecetteService
```

### Injection de session DB

```python
from src.core.decorators import with_db_session

@with_db_session
def ma_fonction(data, db: Session):
    # Session injectée automatiquement
    return db.query(Model).all()
```

### Gestion d'erreurs

```python
from src.core.errors import ErreurBaseDeDonnees, ErreurValidation

try:
    result = service.operation()
except ErreurValidation as e:
    st.error(f"Données invalides: {e}")
except ErreurBaseDeDonnees as e:
    st.error(f"Erreur base de données: {e}")
```

---

## 📚 Voir aussi

- [API_REFERENCE.md](./API_REFERENCE.md) - API REST
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Architecture technique
- [SQLALCHEMY_SESSION_GUIDE.md](./SQLALCHEMY_SESSION_GUIDE.md) - Guide sessions DB
