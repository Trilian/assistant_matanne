# Interactions Inter-Modules

> Cartographie des flux déjà présents entre modules et des zones encore à étendre.

---

## Mécanismes utilisés

Les interactions cross-module reposent principalement sur:

- services métier qui consomment des modèles d'autres domaines
- bus d'événements domaine `src/services/core/events/`
- jobs planifiés dans `src/services/core/cron/jobs.py`
- agrégations dashboard
- dispatcher de notifications

Le bus d'événements est documenté dans `src/services/core/events/__init__.py` et permet de découpler les services.

---

## Interactions en production

| Source | Destination | Mécanisme | État |
|--------|-------------|-----------|------|
| Planning repas | Courses | génération de liste depuis le planning | actif |
| Famille / Jules | Cuisine | adaptation enfant et recettes contextualisées | actif |
| Maison / Entretien | Planning | tâches et routines visibles dans les vues de suivi | actif partiel |
| Dashboard | Tous les modules | agrégation métriques | actif |
| Cron jobs | Notifications | rappels et alertes programmés | actif |
| Automations | Courses / Notifications | moteur Si→Alors simple | actif |
| Planning | Google Calendar | sync externe planifiée | actif |
| Inventaire | Courses | stock bas -> liste de courses | actif |
| Famille | Activités IA | jalon -> invalidation suggestions et notification | actif |
| Dashboard | Garmin + Cuisine + Inventaire | score bien-être et points famille consolidés | actif |
| Habitat Plans IA | Scénarios Habitat | calcul de score pondéré | actif |
| Habitat Déco IA | Finances Maison | synchronisation budget dépense | actif partiel |

---

## Exemples vérifiés dans le code

### Document -> Notification

Quand un document arrive à échéance, un événement `document.echeance_proche` peut déclencher une notification ntfy.

### Jalon Jules -> Suggestions d'activités

Quand un jalon est ajouté:

- le cache des suggestions d'activités est invalidé
- une notification informe que de nouvelles suggestions sont disponibles

### Inventaire -> Courses

Le job `alerte_stock_bas`:

- parcourt l'inventaire
- crée ou réutilise une liste active
- ajoute les articles manquants
- notifie l'utilisateur

### Planning -> Google Calendar

Le job `sync_google_calendar` synchronise les calendriers externes Google actifs par utilisateur.

### Automations -> Notifications / Courses

Le moteur actuel supporte:

- déclencheur `stock_bas`
- action `ajouter_courses`
- action `notifier`

---

## Bridges phase 5 et suivants

| Bridge | Source -> Destination | Statut |
|--------|------------------------|--------|
| `inter_module_inventaire_planning.py` | Inventaire -> Planning recettes | actif |
| `inter_module_jules_nutrition.py` | Jules -> Nutrition planning | actif |
| `inter_module_saison_menu.py` | Saisonnalité -> Planning IA | actif |
| `inter_module_meteo_activites.py` | Météo -> Activités famille | actif |
| `inter_module_entretien_courses.py` | Entretien -> Courses | actif |
| `inter_module_charges_energie.py` | Charges -> Analyse énergie | actif |
| `inter_module_weekend_courses.py` | Weekend -> Courses | actif |
| `inter_module_documents_calendrier.py` | Documents -> Calendrier | actif |

## Points à enrichir

- granularité des événements émis sur certains flux historiques
- observabilité bout-en-bout par bridge (latence, erreurs)
- tests de charge ciblés sur les interactions les plus fréquentes

---

## Recommandations d'implémentation

- privilégier le bus d'événements pour les réactions non bloquantes
- garder les synchronisations lourdes dans les jobs cron
- éviter les appels directs entre services quand un événement suffit
- documenter chaque nouveau flux ici lors de son ajout
