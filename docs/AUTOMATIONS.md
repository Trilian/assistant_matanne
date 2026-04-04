# Automations & jobs planifiés

> Référence consolidée du moteur d'automatisation Si→Alors et de son exploitation opérationnelle.
>
> **Dernière mise à jour** : 4 avril 2026 — ce document absorbe l'ancien `docs/AUTOMATION_GUIDE.md`.

---

## Deux mécanismes à distinguer

### 1. Jobs planifiés APScheduler

Ils couvrent les traitements programmés de la plateforme :

- définition des jobs : `src/services/core/cron/jobs.py`
- matrice des horaires : `src/services/core/cron/jobs_schedule.py`
- suivi détaillé : `docs/CRON_JOBS.md`

### 2. Automations métier Si→Alors

Elles permettent à un utilisateur de définir des règles dynamiques stockées en base :

- routes API : `src/api/routes/automations.py`
- moteur : `src/services/utilitaires/automations_engine.py`
- exécution planifiée : job `automations_runner` toutes les 5 minutes
- modèle ORM : `AutomationRegle`

---

## Vue d'ensemble du moteur

| Élément | Rôle |
| --- | --- |
| `AutomationRegle` | persistance des règles actives/inactives |
| `automations_runner` | évaluation périodique des règles actives |
| `executer_automations_actives()` | boucle principale d'exécution |
| `executer_automations_actives_dry_run()` | simulation sans effet métier |
| `executer_automation_par_id()` | exécution ciblée d'une règle |
| `RegleAutomationIA` | format structuré pour la génération assistée par IA |

---

## Déclencheurs supportés (9)

| Type | Description |
|------|-------------|
| `stock_bas` | Articles inventaire sous un seuil |
| `peremption_proche` | Articles arrivant à péremption proche |
| `budget_depassement` | Dépenses du mois au-dessus d'un seuil |
| `meteo_alerte` | Prévision météo contenant un mot-clé (pluie, orage, neige, vent) |
| `anniversaire_proche` | Anniversaires dans une fenêtre de jours |
| `tache_en_retard` | Tâches d'entretien en retard |
| `garmin_inactivite` | Inactivité Garmin au-delà d'un seuil |
| `document_expiration` | Documents arrivant à expiration |
| `recette_sans_photo` | Recettes sans image |

---

## Actions supportées (11)

| Type | Description |
|------|-------------|
| `ajouter_courses` | Ajoute des articles à une liste de courses active |
| `generer_liste_courses` | Alias de `ajouter_courses` |
| `suggerer_recette` | Envoie une notification de suggestion recette |
| `creer_tache_maison` | Crée une tâche d'entretien |
| `ajouter_au_planning` | Crée un événement planning |
| `mettre_a_jour_budget` | Ajoute une dépense d'ajustement budget |
| `generer_rapport_pdf` | Notifie qu'un rapport PDF est prêt |
| `archiver` | Désactive la règle après exécution |
| `notifier` | Notification ntfy + push |
| `envoyer_Telegram` | Notification Telegram |
| `envoyer_email` | Notification email |

---

## API disponible

| Méthode | Route | Usage |
|---------|-------|-------|
| `GET` | `/api/v1/automations` | Lister les automations de l'utilisateur |
| `POST` | `/api/v1/automations/init` | Initialiser depuis les préférences legacy |
| `POST` | `/api/v1/automations` | Créer une automation |
| `PUT` | `/api/v1/automations/{automation_id}` | Modifier une automation |
| `POST` | `/api/v1/automations/{automation_id}/simuler` | Simuler une automation |
| `POST` | `/api/v1/automations/{automation_id}/executer-maintenant` | Exécuter immédiatement (`dry_run` optionnel) |
| `POST` | `/api/v1/automations/generer-ia` | Générer une règle depuis un prompt IA |

---

## Exécution, suivi et exploitation admin

- le job `automations_runner` s'exécute toutes les 5 minutes
- seules les règles actives sont évaluées
- le moteur met à jour `derniere_execution` et incrémente `execution_count`
- le **dry-run** est disponible globalement et par règle

### Endpoints admin utiles

| Endpoint | Usage |
| --- | --- |
| `GET /api/v1/admin/jobs` | vérifier la présence et l'état du runner |
| `POST /api/v1/admin/jobs/automations_runner/run?dry_run=true` | tester le moteur sans effet de bord |
| `GET /api/v1/admin/cockpit` | vue globale santé + jobs récents |
| `GET /api/v1/admin/audit-logs` | relire les actions manuelles récentes |

### Monitoring

- visibilité des exécutions via les routes admin jobs
- historique consolidé des jobs dans `job_executions`
- relance manuelle possible pour diagnostic

---

## Exemple conceptuel

```json
{
  "nom": "Stock bas produits de base",
  "condition": {"type": "stock_bas", "seuil": 2},
  "action": {"type": "ajouter_courses", "quantite": 1},
  "parametres": {}
}
```

---

## Bonnes pratiques

- distinguer clairement **job planifié** et **automation utilisateur**
- documenter tout nouveau déclencheur ou type d'action ici
- privilégier le `dry_run` avant toute règle mutative
- garder les règles idempotentes et compréhensibles côté admin
- réserver `docs/CRON_JOBS.md` aux détails d'horaires et de développement des jobs

---

## Limitations actuelles

- pas d'historique détaillé persistant par **règle** au même niveau que les jobs
- pas de rollback métier avancé
- déclencheurs évalués en polling via CRON, pas en temps réel événementiel

---

## Extensions prévues

Déclencheurs supplémentaires ciblés :

- `document_expirant`
- `peremption_proche`
- `routine_en_retard`
- `seuil_budget_depasse`

Actions supplémentaires ciblées :

- `creer_tache_planning`
- `envoyer_email`
- `envoyer_Telegram`
- `declencher_webhook`

Améliorations structurelles visées :

- historique plus fin des exécutions par règle
- meilleure observabilité des erreurs
- diagnostics plus lisibles côté admin

