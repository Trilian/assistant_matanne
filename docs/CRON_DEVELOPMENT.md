# Guide Developpement CRON

## Objectif

Ce guide explique comment ajouter un nouveau job CRON dans le backend (configuration, schedule, logs, dry run).

## Emplacement des jobs

- Definition des jobs: `src/services/core/cron/jobs.py`
- Schedules: `src/services/core/cron/jobs_schedule.py`
- Orchestration/admin: routes admin et services cron

## Ajouter un nouveau job

1. Implementer la fonction de job
2. Declarer le job dans le registre
3. Ajouter la frequence dans le schedule
4. Exposer un dry run testable
5. Ajouter test unitaire et test integration

## Exemple de job

```python
from datetime import datetime

def job_expiration_recettes_suggestion() -> dict:
    """Detecte les ingredients proches de peremption et prepare une suggestion recette."""
    # Logique metier simplifiee
    items = []
    return {
        "executed_at": datetime.utcnow().isoformat(),
        "items_detectes": len(items),
        "status": "ok",
    }
```

## Exemple d enregistrement schedule

```python
JOBS_SCHEDULE = {
    "job_expiration_recettes_suggestion": {
        "trigger": "cron",
        "hour": 10,
        "minute": 0,
    }
}
```

## Dry run recommande

```python
def dry_run_job_expiration_recettes_suggestion() -> dict:
    resultat = job_expiration_recettes_suggestion()
    return {"dry_run": True, "resultat": resultat}
```

## Logs et supervision

- Logger debut/fin de job
- Logger duree et volume traite
- Marquer explicitement les erreurs recuperables
- Exposer un statut lisible via admin

## Checklist avant merge

- [ ] Job id explicite et unique
- [ ] Schedule documente
- [ ] Dry run disponible
- [ ] Test unitaire present
- [ ] Test d integration cron present
