# ðŸ“Š Guide Module Dashboard

> Tableau de bord familial avec mÃ©triques agrÃ©gÃ©es de tous les modules.

---

## Vue d'ensemble

Le **Dashboard** est la page d'accueil de l'application. Il agrÃ¨ge les donnÃ©es clÃ©s de chaque module pour offrir une vue synthÃ©tique de l'Ã©tat familial.

**URL** : `/` (page d'accueil)  
**Service backend** : `src/services/dashboard/service.py`  
**Route API** : `src/api/routes/dashboard.py` (`/api/v1/dashboard`)  
**Frontend** : `frontend/src/app/(app)/page.tsx`

---

## Widgets

| Widget | Description | Source |
| -------- | ------------- | -------- |
| Repas du jour | Repas planifiÃ©s (dÃ©jeuner, dÃ®ner) | Planning |
| Courses en attente | Nombre de listes non terminÃ©es | Courses |
| TÃ¢ches en retard | TÃ¢ches entretien/projets en retard | Maison |
| Anniversaires proches | Prochains anniversaires famille | Famille |
| MÃ©tÃ©o | MÃ©tÃ©o du jour + alertes | IntÃ©grations |
| Budget mensuel | DÃ©penses vs budget, reste | Finances |
| Stock bas | Articles inventaire en quantitÃ© faible | Inventaire |
| Prochains Ã©vÃ©nements | Ã‰vÃ©nements planifiÃ©s cette semaine | Planning |

---

## API

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/dashboard` | DonnÃ©es agrÃ©gÃ©es du dashboard |
| GET | `/api/v1/dashboard/taches-retard` | TÃ¢ches en retard (limite configurable) |

---

## Architecture

```
Frontend (page.tsx)
  â†’ GET /api/v1/dashboard
    â†’ src/api/routes/dashboard.py
      â†’ src/services/dashboard/service.py
        â†’ RequÃªtes ORM sur : Repas, ListeCourses, Projet, TacheEntretien,
           AnniversaireFamille, Depense, BudgetMensuel, Inventaire
```

Le service dashboard utilise `@avec_cache(ttl=60)` pour les donnÃ©es agrÃ©gÃ©es (rafraÃ®chissement chaque minute).

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complÃ¨te.
