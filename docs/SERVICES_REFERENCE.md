# Services Reference — Assistant MaTanne

> Référence mise à jour des packages de services backend, des patterns de factories et des points d'entrée publics les plus utiles.

## Snapshot Phase 10

- Factories détectées (`@service_factory`): **169**
- Domaine le plus dense: cuisine/maison/famille
- Registre central: `src/services/core/registry.py`

---

## Architecture de service

La couche services est organisée par domaine sous `src/services/`:

- `cuisine/`
- `famille/`
- `maison/`
- `jeux/`
- `planning/`
- `dashboard/`
- `utilitaires/`
- `inventaire/`
- `integrations/`
- `rapports/`
- `core/`

Le flux recommandé reste:

1. route FastAPI
2. service métier
3. accès DB via décorateur ou contexte de session
4. publication d'événements ou notifications si nécessaire

---

## Pattern central: `@service_factory`

La plupart des services partagés exposent une factory décorée `@service_factory` qui les enregistre dans le registre central.

Exemple type:

```python
from src.services.core.registry import service_factory

@service_factory("chat_ia", tags={"outils", "ia", "chat"})
def obtenir_chat_ai_service() -> ChatAIService:
    return ChatAIService()
```

Intérêt:

- singleton léger piloté par le registre
- lookup par nom ou tags
- instrumentation et health checks centralisés

---

## Services transversaux `core/`

| Zone | Rôle |
|------|------|
| `core/registry.py` | registre des services et factories |
| `core/base/` | fondations de services, notamment `BaseAIService` |
| `core/events/` | bus d'événements domaine |
| `core/notifications/` | dispatcher et canaux de notification |
| `core/cron/` | scheduler et jobs planifiés |
| `core/backup/` | sauvegardes et restauration |
| `core/utilisateur/` | profils, sécurité, configuration utilisateur |

---

## Domaine Cuisine

Packages repérés:

- `src/services/cuisine/recettes/`
- `src/services/cuisine/planning/`
- `src/services/cuisine/courses/`
- `src/services/cuisine/suggestions/`
- `src/services/cuisine/batch_cooking/`
- `src/services/cuisine/prediction_courses.py`
- `src/services/cuisine/prediction_peremption.py`
- `src/services/cuisine/photo_frigo.py`

Factories publiques fréquentes:

- `obtenir_service_recettes`
- `obtenir_service_planning`
- `obtenir_service_courses`
- `obtenir_service_suggestions`
- `obtenir_service_batch_cooking`
- `obtenir_service_prediction_courses`
- `obtenir_service_prediction_peremption`

Rôle:

- gestion des recettes
- génération de planning repas
- listes de courses
- batch cooking
- enrichissements IA et prédictions

---

## Domaine Famille

Packages repérés:

- activités, routines, budget, achats, anniversaires, documents, voyage
- IA: `jules_ai.py`, `weekend_ai.py`, `soiree_ai.py`, `achats_ia.py`
- intégrations métier: `calendrier_planning.py`, `inter_module_budget_jeux.py`, `inter_module_garmin_health.py`

Factories publiques fréquentes:

- `obtenir_service_jules`
- `obtenir_service_activites`
- `obtenir_service_routines`
- `obtenir_service_achats_famille`
- `obtenir_service_weekend`
- `obtenir_service_documents`
- `obtenir_service_voyage`
- `get_calendar_sync_service`

Rôle:

- pilotage de la vie familiale
- suivi de Jules
- calendrier, routines et rappels
- suggestions IA contextuelles

---

## Domaine Maison

Le package `src/services/maison/` combine des services principaux, des mixins et de nombreux CRUD spécialisés.

Services majeurs:

- `obtenir_jardin_service`
- `obtenir_entretien_service`
- `obtenir_projets_service`
- `obtenir_contexte_maison_service`
- `obtenir_notifications_maison_service`
- `obtenir_visualisation_service`
- `obtenir_catalogue_entretien_service`

Services Habitat (sous-domaine maison avancé):

- `obtenir_service_plans_habitat_ai`
- `obtenir_service_deco_habitat`
- `obtenir_service_scenarios_habitat`
- `obtenir_service_veille_habitat`
- `obtenir_service_dvf_habitat`

CRUD spécialisés exposés:

- artisans
- contrats
- garanties
- diagnostics
- estimations
- cellier
- meubles
- dépenses
- checklists
- nuisibles, devis, entretien saisonnier, relevés

Détail CRUD maison explicitement référencé:

- `ArtisanCrudService`
- `ContratMaisonCrudService`
- `GarantieCrudService`
- `DiagnosticMaisonCrudService`
- `EstimationImmobiliereCrudService`
- `DepenseMaisonCrudService`
- `MeubleCrudService`
- `ChecklistMaisonCrudService`
- `StockMaisonCrudService`

Rôle:

- gestion opérationnelle de la maison
- projets, entretien, jardin, énergie
- contexte quotidien et rappels maison

---

## Domaine Jeux

Le package `src/services/jeux/` agit comme façade paresseuse vers `src/services/jeux/_internal/`.

Services majeurs:

- `get_paris_crud_service`
- `get_loto_crud_service`
- `get_euromillions_crud_service`
- `get_prediction_service`
- `get_backtest_service`
- `get_jeux_ai_service`

Rôle:

- paris sportifs
- loto et Euromillions
- analyse IA et backtest
- jobs spécialisés côté jeux

---

## Domaine Dashboard

Exports confirmés:

- `obtenir_accueil_data_service`
- `obtenir_score_bien_etre_service`
- `obtenir_service_resume_famille_ia`
- `obtenir_service_anomalies_financieres`
- `obtenir_points_famille_service`

Rôle:

- agrégation de données multi-modules
- métriques d'accueil
- résumés IA et anomalies budgétaires

---

## Domaine Utilitaires

Services confirmés:

- notes
- journal
- contacts
- liens
- mots de passe
- presse-papiers
- énergie
- OCR
- météo
- chat IA
- import et export utilitaires
- moteur d'automations

Factories fréquentes:

- `obtenir_notes_service`
- `obtenir_journal_service`
- `obtenir_contacts_service`
- `obtenir_energie_service`
- `obtenir_ocr_service`
- `obtenir_meteo_service`
- `obtenir_chat_ai_service`
- `obtenir_moteur_automations_service`

---

## Domaine Planning

Le package `src/services/planning/` expose surtout:

- `obtenir_service_conflits`
- `obtenir_service_rappels`
- `obtenir_service_suggestions`

Rôle:

- conflits d'horaires
- rappels intelligents
- suggestions de créneaux et d'optimisation planning

---

## Intégrations et rapports

Intégrations utiles repérées:

- `obtenir_service_openfoodfacts`
- `obtenir_multimodal_service`
- `obtenir_webhook_service`
- `obtenir_image_generator_service`
- `obtenir_service_synchronisation_temps_reel`

Intégrations phase 3 suivies en priorité:

- météo jardin: `src/services/integrations/weather/`
- Google Calendar: `src/services/integrations/google_calendar.py`
- Garmin: `src/services/integrations/garmin/service.py`

Rapports:

- `obtenir_service_rapports_pdf`

---

## Services IA à connaître

Services IA explicitement visibles dans le code:

- `obtenir_service_suggestions`
- `obtenir_chat_ai_service`
- `obtenir_service_resume_famille_ia`
- `obtenir_service_anomalies_financieres`
- `get_jeux_ai_service`
- `obtenir_multimodal_service`
- `obtenir_service_prediction_courses`
- `obtenir_service_prediction_peremption`

Voir aussi `docs/AI_SERVICES.md` pour le détail fonctionnel.

---

## Conseils d'usage

- importer via les factories publiques plutôt que d'instancier directement quand le service est enregistré dans le registre
- utiliser `executer_avec_session()` côté routes et `@avec_session_db` côté services
- éviter les appels croisés directs si un événement métier ou un cron suffit

---

## Références associées

- `docs/ARCHITECTURE.md`
- `docs/AI_SERVICES.md`
- `docs/INTER_MODULES.md`
- `docs/CRON_JOBS.md`
- `docs/FRONTEND_ARCHITECTURE.md`
- `docs/ADMIN_GUIDE.md`
- `docs/WHATSAPP_SETUP.md`

