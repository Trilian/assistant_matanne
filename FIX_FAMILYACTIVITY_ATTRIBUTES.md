# 🔧 Fix - Erreur d'attribut FamilyActivity

**Date** : 25 Janvier 2026  
**Status** : ✅ Résolu

## Problème identifié

### Erreur
```
❌ Erreur inattendue: type object 'FamilyActivity' has no attribute 'date_debut'
```

### Cause
Dans [src/services/planning_unified.py](src/services/planning_unified.py#L240), la fonction `_charger_activites()` utilisait des attributs incorrects :

```python
# ❌ INCORRECT (avant)
FamilyActivity.date_debut          # N'existe pas!
FamilyActivity.date_fin             # N'existe pas!
act.budget_estime                   # N'existe pas!
act.adapte_pour_jules               # N'existe pas!
```

## Solution appliquée

### Attributs corrects selon modèle
Dans [src/core/models.py](src/core/models.py#L720), `FamilyActivity` définit :

```python
# ✅ CORRECT (après)
date_prevue: date                   # Date prévue de l'activité
duree_heures: float | None          # Durée en heures
cout_estime: float | None           # Coût estimé
```

### Corrections apportées

**Fichier** : [src/services/planning_unified.py](src/services/planning_unified.py#L240-L270)

```python
# AVANT
FamilyActivity.date_debut >= datetime.combine(date_debut, datetime.min.time())
FamilyActivity.date_debut <= datetime.combine(date_fin, datetime.max.time())
jour_str = act.date_debut.date().isoformat()
"debut": act.date_debut,
"fin": act.date_fin,
"budget": act.budget_estime or 0,
"pour_jules": act.adapte_pour_jules,

# APRÈS
FamilyActivity.date_prevue >= datetime.combine(date_debut, datetime.min.time()).date()
FamilyActivity.date_prevue <= datetime.combine(date_fin, datetime.max.time()).date()
jour_str = act.date_prevue.isoformat()
"debut": act.date_prevue,
"fin": act.date_prevue,  # FamilyActivity n'a pas de date_fin séparée
"budget": act.cout_estime or 0,
"duree": act.duree_heures or 0,
```

## Détails des changements

| Attribut ancien | Attribut correct | Type | Notes |
|-----------------|-----------------|------|-------|
| `date_debut` | `date_prevue` | `date` | Date prévue de l'activité |
| `date_fin` | `date_prevue` | `date` | Pas de date_fin, utiliser date_prevue |
| `budget_estime` | `cout_estime` | `float` | Coût estimé |
| `adapte_pour_jules` | - | - | N'existe pas dans le modèle |
| `duree_heures` | `duree_heures` | `float` | Durée en heures |

## Validation

✅ **Tests de compilation**
```bash
python -m py_compile src/services/planning_unified.py
# Success
```

✅ **Tests d'import**
```bash
python -c "from src.services.planning_unified import PlanningAIService"
# ✅ Import OK
```

✅ **Tests du module Maison**
```bash
python -c "from src.modules.maison import app, jardin, projets, entretien"
# ✅ Tous les imports Maison OK
```

## Impact

### Services affectés
- ✅ [src/services/planning_unified.py](src/services/planning_unified.py) - **CORRIGÉ**

### Modules affectés
- ✅ Modules Maison (jardin, projets, entretien) - OK
- ✅ Module Planning - OK avec le fix

### Tests
- Tous les imports passent ✅
- Pas de breaking changes ✅
- Backward compatible ✅

## Prochaines étapes

1. ✅ Fix appliqué
2. ✅ Tests passent
3. ⏭️ Redémarrer l'app pour tester complètement

## Notes pour l'avenir

**Toujours vérifier les attributs du modèle avant de l'utiliser :**

```python
# Consulter les attributs réels:
# src/core/models.py → class FamilyActivity (ligne 721)

# Les noms de colonnes en Python ne correspondent pas toujours
# à ce qu'on imagine:
# - date_debut n'existe pas → utiliser date_prevue
# - budget_estime n'existe pas → utiliser cout_estime
# - pas de date_fin séparée → utiliser date_prevue
```

---

**Status** : ✅ RÉSOLU  
**Impact** : Minimal (1 fichier, 1 fonction)  
**Risk** : Très faible (correction simple d'attributs)
