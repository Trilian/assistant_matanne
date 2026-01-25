# 📚 Documentation Technique - Assistant Matanne

## Table des Matières
1. [Introduction](#1-introduction)
2. [Architecture](#2-architecture)
3. [Core (Infrastructure)](#3-core-infrastructure)
4. [Modules Métier](#4-modules-métier)
5. [Services](#5-services)
6. [Interface Utilisateur](#6-interface-utilisateur)
7. [Base de Données](#7-base-de-données)
8. [Intégration IA](#8-intégration-ia)
9. [Configuration](#9-configuration)
10. [Tests](#10-tests)
11. [Déploiement](#11-déploiement)

---

## 1. Introduction

**Assistant Matanne** est un hub de gestion familiale développé en Python avec Streamlit. Il centralise la gestion des repas, courses, suivi de développement de l'enfant, santé familiale et tâches domestiques.

### Fonctionnalités Principales
- 🍽️ **Cuisine** : Recettes, planification des repas, inventaire, listes de courses
- 👶 **Famille** : Suivi de Jules (19 mois), jalons de développement, activités
- 💪 **Santé** : Routines sportives, objectifs bien-être, suivi quotidien
- 🏡 **Maison** : Projets domestiques, jardin, routines ménagères
- 📅 **Planning** : Calendrier familial, vue hebdomadaire
- 🤖 **IA** : Suggestions de recettes, génération de plannings, adaptations

---

## 2. Architecture

### Vue Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT (Frontend)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Accueil  │ │ Cuisine  │ │ Famille  │ │ Planning │            │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
┌───────▼────────────▼────────────▼────────────▼──────────────────┐
│                        SERVICES LAYER                            │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │
│  │RecetteServ │ │PlanningServ│ │InventaireSv│ │ CoursesServ│    │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘    │
│          │                                │                      │
│  ┌───────▼────────────────────────────────▼──────────────┐      │
│  │              BaseAIService (Mistral)                  │      │
│  │   Rate Limiting │ Cache Sémantique │ JSON Parsing     │      │
│  └───────────────────────────────────────────────────────┘      │
└─────────────────────────────┬────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────┐
│                         CORE LAYER                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Database │ │  Config  │ │Decorators│ │ Errors   │            │
│  └────┬─────┘ └──────────┘ └──────────┘ └──────────┘            │
└───────┼──────────────────────────────────────────────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────┐
│                    PostgreSQL (Supabase)                         │
│       28 Tables │ Alembic Migrations │ SQLAlchemy 2.0 ORM        │
└──────────────────────────────────────────────────────────────────┘
```

### Patterns Utilisés
- **Repository Pattern** : Services encapsulent l'accès DB
- **Factory Pattern** : `get_recette_service()`, `get_planning_service()`
- **Decorator Pattern** : `@with_db_session`, `@with_cache`
- **Lazy Loading** : Modules chargés à la demande
- **Mixin Pattern** : `RecipeAIMixin`, `PlanningAIMixin`

---

## 3. Core (Infrastructure)

### 3.1 `models.py` - Modèles SQLAlchemy (1150 lignes)

Tous les modèles ORM sont centralisés dans un fichier unique.

#### Modèles Principaux

| Modèle | Table | Description |
|--------|-------|-------------|
| `Recette` | `recettes` | Recettes avec métadonnées (bio, robots, nutrition) |
| `Ingredient` | `ingredients` | Référentiel unique d'ingrédients |
| `RecetteIngredient` | `recette_ingredients` | Association N:M avec quantité |
| `EtapeRecette` | `etapes_recette` | Étapes de préparation ordonnées |
| `VersionRecette` | `versions_recette` | Variantes (bébé, batch cooking) |
| `ArticleInventaire` | `inventaire` | Stock avec photos et codes-barres |
| `ArticleCourses` | `liste_courses` | Items à acheter |
| `Planning` | `plannings` | Planning hebdomadaire |
| `Repas` | `repas` | Repas planifié (jour + type) |
| `ChildProfile` | `child_profiles` | Profil enfant (Jules) |
| `Milestone` | `milestones` | Jalons développement |
| `HealthRoutine` | `health_routines` | Routines sportives |
| `HealthEntry` | `health_entries` | Entrées quotidiennes santé |
| `FamilyActivity` | `family_activities` | Activités/sorties famille |
| `CalendarEvent` | `calendar_events` | Événements calendrier |
| `GardenItem` | `garden_items` | Plantes du jardin |

#### Exemple de Modèle

```python
class Recette(Base):
    __tablename__ = "recettes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    temps_preparation: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Flags & Tags
    est_bio: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    compatible_cookeo: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relations
    ingredients: Mapped[list["RecetteIngredient"]] = relationship(
        back_populates="recette", cascade="all, delete-orphan"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint("temps_preparation >= 0", name="ck_temps_prep_positif"),
    )
    
    @property
    def temps_total(self) -> int:
        return self.temps_preparation + self.temps_cuisson
```

### 3.2 `database.py` - Gestion Base de Données

```python
# Context manager pour sessions
with obtenir_contexte_db() as session:
    recettes = session.query(Recette).all()
    session.commit()

# Version sécurisée (retourne None si erreur)
with obtenir_db_securise() as db:
    if db:
        result = db.query(Recette).first()
```

**Fonctionnalités** :
- Création engine avec retry automatique
- Pool de connexions avec `pool_pre_ping`
- Support SSL pour Supabase
- Système de migrations intégré

### 3.3 `decorators.py` - Décorateurs Utilitaires

#### `@with_db_session`
Injecte automatiquement une session DB :

```python
@with_db_session
def creer_recette(data: dict, db: Session) -> Recette:
    recette = Recette(**data)
    db.add(recette)
    db.commit()
    return recette

# Appel sans session (auto-créée)
recette = creer_recette({"nom": "Tarte"})

# Appel avec session existante
with obtenir_contexte_db() as session:
    recette = creer_recette({"nom": "Tarte"}, db=session)
```

#### `@with_cache`
Cache automatique avec TTL :

```python
@with_cache(ttl=1800, key_prefix="recettes")
def charger_recettes(page: int = 1) -> list[Recette]:
    # Logique coûteuse...
    return recettes

# Avec clé personnalisée
@with_cache(ttl=3600, key_func=lambda self, id: f"recette_{id}")
def charger_recette(self, id: int) -> Recette:
    return recette
```

### 3.4 `lazy_loader.py` - Chargement Différé

Réduit le temps de démarrage de **60%** :

```python
class LazyModuleLoader:
    @staticmethod
    def load(module_path: str, reload: bool = False) -> Any:
        if module_path in LazyModuleLoader._cache:
            return LazyModuleLoader._cache[module_path]
        
        module = importlib.import_module(module_path)
        LazyModuleLoader._cache[module_path] = module
        return module
```

### 3.5 `config.py` - Configuration

Configuration via Pydantic Settings avec cascade :

```python
class Parametres(BaseSettings):
    # Application
    APP_NAME: str = "Assistant Matanne"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str  # Requis
    
    # IA
    MISTRAL_API_KEY: str  # Requis
    MISTRAL_MODEL: str = "mistral-small-latest"
    
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
    )
```

**Ordre de priorité** :
1. `.env.local` (développement local)
2. `.env` (fallback)
3. `st.secrets` (Streamlit Cloud)
4. Valeurs par défaut

---

## 4. Modules Métier

### 4.1 Module Accueil (`accueil.py`)

Dashboard central avec :
- Alertes critiques (stock bas, péremption)
- Stats globales (recettes, planning, courses)
- Raccourcis rapides vers modules
- Résumés par domaine

```python
def app():
    """Point d'entrée module accueil"""
    render_critical_alerts()
    render_global_stats()
    render_quick_actions()
    render_cuisine_summary()
    render_inventaire_summary()
```

### 4.2 Module Cuisine (`src/modules/cuisine/`)

| Fichier | Fonctionnalité |
|---------|----------------|
| `recettes.py` | CRUD recettes, filtres avancés, détail |
| `inventaire.py` | Gestion stock, alertes, photos |
| `courses.py` | Listes courses, rayons, priorités |
| `planning.py` | Planification hebdomadaire repas |
| `recettes_import.py` | Import CSV/JSON |

#### Filtres Recettes Avancés
- Type de repas (petit-déj, déjeuner, dîner, goûter)
- Difficulté (facile, moyen, difficile)
- Temps de préparation max
- Score bio/local minimum
- Compatibilité robots (Cookeo, Airfryer...)
- Tags (bébé, batch cooking, congelable)

### 4.3 Module Famille (`src/modules/famille/`)

| Fichier | Fonctionnalité |
|---------|----------------|
| `jules.py` | Suivi développement Jules (19 mois) |
| `suivi_jules.py` | Graphiques évolution |
| `activites.py` | Sorties et activités familiales |
| `sante.py` | Routines sportives, objectifs |
| `bien_etre.py` | Suivi humeur, sommeil |
| `shopping.py` | Listes achats famille |
| `helpers.py` | Fonctions utilitaires cachées |

#### Jalons de Développement (Milestones)
Catégories suivies :
- 🗣️ Langage
- 🚶 Motricité
- 👥 Social
- 🧠 Cognitif
- 🍽️ Alimentation
- 😴 Sommeil

### 4.4 Module Maison (`src/modules/maison/`)

| Fichier | Fonctionnalité |
|---------|----------------|
| `projets.py` | Projets domestiques avec tâches |
| `jardin.py` | Plantes, entretien, récoltes |
| `entretien.py` | Tâches ménagères |
| `helpers.py` | Fonctions partagées |

### 4.5 Module Planning (`src/modules/planning/`)

| Fichier | Fonctionnalité |
|---------|----------------|
| `calendrier.py` | Vue calendrier mensuel |
| `vue_semaine.py` | Vue hebdomadaire |
| `vue_ensemble.py` | Dashboard planning |
| `components/` | Composants spécifiques |

---

## 5. Services

### 5.1 Architecture des Services

```
BaseService[T]                    # CRUD générique
     │
     ├── BaseAIService            # + IA rate limiting, cache
     │        │
     │        ├── RecipeAIMixin   # Contextes métier recettes
     │        ├── PlanningAIMixin # Contextes métier planning
     │        └── ...
     │
     └── Services concrets
          ├── RecetteService
          ├── PlanningService
          ├── InventaireService
          └── CoursesService
```

### 5.2 RecetteService (`recettes.py`)

```python
class RecetteService(BaseService[Recette], BaseAIService, RecipeAIMixin):
    
    # CRUD
    def get_all(self, page: int = 1, per_page: int = 20) -> list[Recette]
    def get_by_id_full(self, recette_id: int) -> Recette | None
    def create(self, data: RecetteInput) -> Recette
    def update(self, recette_id: int, data: dict) -> Recette
    def delete(self, recette_id: int) -> bool
    
    # Recherche avancée
    def search(self, filters: dict) -> list[Recette]
    def get_by_type_repas(self, type_repas: str) -> list[Recette]
    def get_compatible_robot(self, robot: str) -> list[Recette]
    
    # IA
    async def suggerer_recettes(self, context: str) -> list[RecetteSuggestion]
    async def generer_version_bebe(self, recette_id: int) -> VersionBebeGeneree
    async def generer_version_batch(self, recette_id: int) -> VersionBatchCookingGeneree
    async def generer_version_robot(self, recette_id: int, robot: str) -> VersionRobotGeneree
    
    # Import/Export
    def import_csv(self, file) -> int
    def export_json(self) -> str
```

**Factory** :
```python
def get_recette_service() -> RecetteService:
    return RecetteService()
```

### 5.3 PlanningService (`planning.py`)

```python
class PlanningService(BaseService[Planning], BaseAIService, PlanningAIMixin):
    
    def get_planning(self, planning_id: int = None) -> Planning | None
    def get_planning_full(self, planning_id: int) -> Planning | None
    def get_repas_semaine(self, semaine: date) -> list[Repas]
    def create_planning(self, nom: str, debut: date) -> Planning
    def add_repas(self, planning_id: int, recette_id: int, jour: date, type_repas: str)
    
    # IA
    async def generer_planning_ia(self, preferences: dict) -> list[JourPlanning]
```

### 5.4 InventaireService (`inventaire.py`)

```python
class InventaireService:
    def get_inventaire_complet(self) -> list[dict]
    def get_stock_bas(self) -> list[ArticleInventaire]
    def get_peremption_proche(self, jours: int = 7) -> list[ArticleInventaire]
    def update_quantite(self, article_id: int, quantite: float)
    def scan_code_barres(self, code: str) -> dict | None
```

### 5.5 CoursesService (`courses.py`)

```python
class CoursesService:
    def get_liste_active(self) -> list[ArticleCourses]
    def add_article(self, ingredient_id: int, quantite: float)
    def marquer_achete(self, article_id: int)
    def generer_depuis_planning(self, planning_id: int) -> int
    def organiser_par_rayon(self) -> dict[str, list[ArticleCourses]]
```

---

## 6. Interface Utilisateur

### 6.1 Composants (`src/ui/components/`)

| Fichier | Composants |
|---------|------------|
| `atoms.py` | `badge`, `empty_state`, `metric_card`, `toast`, `divider`, `info_box` |
| `forms.py` | `form_field`, `search_bar`, `filter_panel`, `quick_filters` |
| `data.py` | `pagination`, `metrics_row`, `export_buttons`, `data_table`, `progress_bar` |
| `layouts.py` | `grid_layout`, `item_card`, `collapsible_section`, `tabs_layout`, `card_container` |
| `dynamic.py` | `Modal`, `DynamicList`, `Stepper` |

#### Exemples d'utilisation

```python
from src.ui import badge, metric_card, smart_spinner

# Badge coloré
badge("🌱 Bio", "#4CAF50")

# Carte métrique
metric_card(
    title="Recettes",
    value=42,
    delta="+3 cette semaine",
    icon="🍽️"
)

# Spinner intelligent
with smart_spinner("Chargement des recettes..."):
    recettes = service.get_all()
```

### 6.2 Feedback (`src/ui/feedback/`)

```python
from src.ui.feedback import show_success, show_error, smart_spinner

# Messages
show_success("Recette sauvegardée !")
show_error("Erreur de connexion")
show_warning("Stock bas détecté")

# Spinner avec contexte
with smart_spinner("Génération IA en cours..."):
    result = await service.generer()
```

### 6.3 Formulaires (`FormBuilder`)

```python
from src.ui.core import FormBuilder

builder = FormBuilder("nouvelle_recette")
builder.add_text("nom", "Nom de la recette", required=True)
builder.add_number("temps_prep", "Temps (min)", min_value=1)
builder.add_select("difficulte", "Difficulté", ["facile", "moyen", "difficile"])
builder.add_checkbox("est_bio", "Recette bio")

if builder.submit("Créer"):
    data = builder.get_values()
    service.create(data)
```

---

## 7. Base de Données

### 7.1 Schéma Relationnel

```
┌─────────────────┐       ┌─────────────────────┐
│   ingredients   │◄──────│ recette_ingredients │
└────────┬────────┘       └──────────┬──────────┘
         │                           │
         │       ┌───────────────────┘
         │       │
         ▼       ▼
┌─────────────────┐       ┌─────────────────┐
│   inventaire    │       │    recettes     │
└─────────────────┘       └────────┬────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ etapes_recette  │  │versions_recette │  │      repas      │
    └─────────────────┘  └─────────────────┘  └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │    plannings    │
                                              └─────────────────┘
```

### 7.2 Migrations Alembic

```bash
# Créer une migration
python manage.py create_migration "Add new field"

# Appliquer les migrations
python manage.py migrate

# Voir l'historique
alembic history
alembic current
```

### 7.3 Connexion Supabase

```
DATABASE_URL=postgresql://postgres.[project]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

Options de connexion :
- SSL requis (`sslmode=require`)
- Timeout de 10 secondes
- Pool de connexions désactivé (NullPool pour Streamlit)
- Timezone UTC

---

## 8. Intégration IA

### 8.1 Architecture IA

```
┌──────────────────────────────────────────────────────────┐
│                    BaseAIService                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Rate Limiter │  │ Cache Séman. │  │ JSON Parser  │    │
│  │ (60/h, 200/j)│  │ (TTL 1h)     │  │ (Pydantic)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │       ClientIA       │
              │   (Mistral API)      │
              │  - Retry (3x)        │
              │  - Async/Sync        │
              │  - Error handling    │
              └──────────────────────┘
```

### 8.2 Utilisation

```python
class MonService(BaseAIService):
    
    async def generer(self, context: str) -> list[dict]:
        # Cache + Rate limit automatiques
        return await self.call_with_list_parsing(
            prompt=f"Génère pour : {context}",
            item_model=MonSchema,
            system_prompt="Tu es un expert..."
        )
```

### 8.3 Rate Limiting

```python
# Limites configurables dans constants.py
AI_RATE_LIMIT_HOURLY = 60   # Appels par heure
AI_RATE_LIMIT_DAILY = 200   # Appels par jour

# Vérification automatique avant appel
autorise, msg = RateLimitIA.peut_appeler()
if not autorise:
    raise ErreurLimiteDebit(msg)
```

---

## 9. Configuration

### 9.1 Variables d'Environnement

```bash
# .env.local (développement)
DATABASE_URL=postgresql://user:pass@localhost/matanne
MISTRAL_API_KEY=sk-xxxxxxxx
DEBUG=true

# Production (Streamlit Cloud via st.secrets)
[database]
url = "postgresql://..."

[mistral]
api_key = "sk-..."
```

### 9.2 Constants (`constants.py`)

```python
# Cache
CACHE_TTL_RECETTES = 1800  # 30 min
CACHE_MAX_SIZE = 1000

# IA
AI_RATE_LIMIT_HOURLY = 60
AI_RATE_LIMIT_DAILY = 200

# DB
DB_CONNECTION_RETRY = 3
DB_CONNECTION_TIMEOUT = 10
```

---

## 10. Tests

### 10.1 Structure

```
tests/
├── conftest.py              # Fixtures partagées
├── test_recettes.py         # Tests service recettes
├── test_planning.py         # Tests service planning
├── test_courses.py          # Tests service courses
├── test_decorators.py       # Tests décorateurs
├── test_validators.py       # Tests validation Pydantic
├── test_ui_components.py    # Tests composants UI
└── integration/             # Tests d'intégration
```

### 10.2 Fixtures

```python
@pytest.fixture
def db(engine):
    """Session DB SQLite in-memory"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def recette_service(db):
    """Service avec session mockée"""
    return RecetteService(db)
```

### 10.3 Exécution

```bash
# Tous les tests
python manage.py test_coverage

# Fichier spécifique
pytest tests/test_recettes.py -v

# Avec coverage HTML
pytest --cov=src --cov-report=html
```

---

## 11. Déploiement

### 11.1 Local

```bash
# Installer dépendances
poetry install

# Lancer l'app
streamlit run src/app.py
```

### 11.2 Streamlit Cloud

1. Push vers GitHub
2. Connecter repo à Streamlit Cloud
3. Configurer secrets dans dashboard :

```toml
[database]
url = "postgresql://..."

[mistral]
api_key = "sk-..."
```

### 11.3 Docker (optionnel)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "src/app.py"]
```

---

## Annexes

### A. Commandes Utiles

```bash
# Développement
streamlit run src/app.py              # Lancer l'app
python manage.py format_code          # Formatter (black)
python manage.py lint                 # Linter (ruff)

# Base de données
python manage.py migrate              # Appliquer migrations
python manage.py create_migration     # Créer migration
alembic current                       # Version actuelle

# Tests
python manage.py test_coverage        # Tests + coverage
pytest -x                             # Arrêter au premier échec
pytest -k "test_recette"              # Tests par nom
```

### B. Structure d'un Module

```python
"""
Module Example - Description
"""

import streamlit as st
from src.services.example import get_example_service
from src.ui import metric_card, smart_spinner


def app():
    """Point d'entrée module (OBLIGATOIRE)"""
    st.title("📋 Mon Module")
    
    service = get_example_service()
    
    with smart_spinner("Chargement..."):
        data = service.get_all()
    
    for item in data:
        render_item(item)


def render_item(item):
    """Sous-fonction de rendu"""
    st.write(item.nom)
```

### C. Ajouter un Nouveau Modèle

1. Ajouter classe dans `src/core/models.py`
2. Créer migration : `python manage.py create_migration "Add Model"`
3. Appliquer : `python manage.py migrate`
4. Créer service dans `src/services/`
5. Ajouter tests dans `tests/`

---

*Documentation générée le 25 janvier 2026*
