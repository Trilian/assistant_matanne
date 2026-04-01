# ?? Guide Module Dashboard

> Tableau de bord familial avec m?triques agr?g?es de tous les modules.

---

## Vue d'ensemble

Le **Dashboard** est la page d'accueil de l'application. Il agr?ge les donn?es cl?s de chaque module pour offrir une vue synth?tique de l'?tat familial.

**URL** : `/` (page d'accueil)  
**Service backend** : `src/services/dashboard/service.py`  
**Route API** : `src/api/routes/dashboard.py` (`/api/v1/dashboard`)  
**Frontend** : `frontend/src/app/(app)/page.tsx`

---

## Widgets

| Widget | Description | Source |
| -------- | ------------- | -------- |
| Repas du jour | Repas planifi?s (d?jeuner, d?ner) | Planning |
| Courses en attente | Nombre de listes non termin?es | Courses |
| T?ches en retard | T?ches entretien/projets en retard | Maison |
| Anniversaires proches | Prochains anniversaires famille | Famille |
| M?t?o | M?t?o du jour + alertes | Int?grations |
| Budget mensuel | D?penses vs budget, reste | Finances |
| Stock bas | Articles inventaire en quantit? faible | Inventaire |
| Prochains ?v?nements | ?v?nements planifi?s cette semaine | Planning |

---

## API

| M?thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/dashboard` | Donn?es agr?g?es du dashboard |
| GET | `/api/v1/dashboard/taches-retard` | T?ches en retard (limite configurable) |

---

## Architecture

```
Frontend (page.tsx)
  ? GET /api/v1/dashboard
    ? src/api/routes/dashboard.py
      ? src/services/dashboard/service.py
        ? Requ?tes ORM sur : Repas, ListeCourses, Projet, TacheEntretien,
           AnniversaireFamille, Depense, BudgetMensuel, Inventaire
```

Le service dashboard utilise `@avec_cache(ttl=60)` pour les donn?es agr?g?es (rafra?chissement chaque minute).

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation compl?te.
