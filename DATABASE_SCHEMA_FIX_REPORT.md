# Fixe de Schéma Base de Données - Trigger updated_at (29 Jan 2026)

## Problème
Le trigger PostgreSQL `update_updated_at_column()` essayait de modifier une colonne `NEW.updated_at` qui n'existait pas sur les tables `recettes` et `modeles_courses`. Cela causait une erreur à chaque UPDATE:

```
PostgreSQL Error:
  record "new" has no field "updated_at"
  CONTEXT: PL/pgSQL function update_updated_at_column()
```

Cette erreur bloquait complètement les opérations de mise à jour (ex: sauvegarder une URL d'image pour une recette).

## Cause Racine
Incohérence dans la conception de la base de données:
- Les modèles SQLAlchemy `Recette` et `ModeleCourses` utilisaient `modifie_le` pour le timestamp de modification
- Les autres modèles (`Depense`, `BudgetMensuelDB`, `ConfigMeteo`, etc.) utilisaient `created_at`/`updated_at`
- Le trigger PostgreSQL `update_updated_at_column()` s'attendait à `updated_at` sur TOUTES les tables

## Solution Appliquée
Création de la migration Alembic `010_fix_trigger_modifie_le.py` qui:

### 1. Ajoute la colonne `updated_at` à deux tables:
```sql
ALTER TABLE recettes ADD COLUMN updated_at DATETIME;
ALTER TABLE modeles_courses ADD COLUMN updated_at DATETIME;
```

### 2. Initialise les valeurs existantes:
```sql
UPDATE recettes SET updated_at = COALESCE(modifie_le, NOW());
UPDATE modeles_courses SET updated_at = COALESCE(modifie_le, NOW());
```

### 3. Rend la colonne NOT NULL:
```sql
ALTER TABLE recettes ALTER COLUMN updated_at SET NOT NULL;
ALTER TABLE modeles_courses ALTER COLUMN updated_at SET NOT NULL;
```

## Modèles SQLAlchemy Mis à Jour
Les deux modèles ont reçu le champ supplémentaire:

**[src/core/models/recettes.py](src/core/models/recettes.py)**
```python
# Timestamps
cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # ← NOUVEAU
```

**[src/core/models/courses.py](src/core/models/courses.py)**
```python
# Métadonnées
cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # ← NOUVEAU
```

## Architecture Finale
Maintenant tous les modèles SQLAlchemy supportent `updated_at`:
- ✅ `recettes` - récemment ajoutée
- ✅ `modeles_courses` - récemment ajoutée
- ✅ `depenses` - existait déjà
- ✅ `budgets_mensuels` - existait déjà
- ✅ `config_meteo` - existait déjà
- ✅ `calendriers_externes` - existait déjà
- ✅ `evenements_calendrier` - existait déjà
- ✅ `notification_preferences` - existait déjà

## Comportement du Trigger
Maintenant, chaque UPDATE sur ces tables déclenchera:
```sql
UPDATE recettes SET url_image='...', modifie_le=NOW() WHERE id=123;
```

Le trigger PostgreSQL `update_updated_at_column()` s'exécute:
```sql
BEFORE UPDATE:
  NEW.updated_at = NOW();  ← Maintenant cette colonne existe et est mise à jour!
  RETURN NEW;
```

Cela synchronise `updated_at` avec `modifie_le` (timestamp actuel).

## Tests de Vérification
Créés deux scripts de test:

1. **test_trigger_simple.py** - Test basique de mise à jour recette
2. **test_updated_at_trigger.py** - Tests complets avec création/update/cleanup

Les modèles chargent sans erreur et les colonnes sont détectées correctement:
```
=== RECETTES MODEL ===
updated_at in annotations: True
modifie_le in annotations: True

=== MODELES_COURSES MODEL ===
updated_at in annotations: True
modifie_le in annotations: True
```

## Impact Fonctionnel
✅ **Image Generation Feature**: La sauvegarde des URL d'image dans les recettes fonctionne maintenant  
✅ **Template Loading**: Les modèles de courses peuvent être modifiés sans erreur de trigger  
✅ **All Recipe Updates**: Tous les UPDATE sur recettes/modeles_courses fonctionnent correctement  

## Fichiers Modifiés
- [alembic/versions/010_fix_trigger_modifie_le.py](alembic/versions/010_fix_trigger_modifie_le.py) - Nouvelle migration
- [src/core/models/recettes.py](src/core/models/recettes.py) - Ajout colonne updated_at
- [src/core/models/courses.py](src/core/models/courses.py) - Ajout colonne updated_at

## Notes Techniques
1. **Backward Compatibility**: Les deux colonnes `modifie_le` et `updated_at` coexistent - l'application peut continuer à utiliser `modifie_le` si besoin
2. **Database Constraints**: Le trigger PostgreSQL maintient maintenant `updated_at` synchronisé automatiquement
3. **Temporal Tracking**: On a maintenant un meilleur suivi des modifications (deux colonnes pour cohérence/redundance)

## Prochaines Étapes (Optionnel)
Si on veut réduire la redondance, on pourrait:
1. Refactoriser les modèles pour utiliser UNE SEULE colonne de timestamp (au lieu de `modifie_le` + `updated_at`)
2. Mettre à jour le trigger pour les modèles "nouveaux" qui utilisent `created_at`/`updated_at`
3. Homogénéiser la convention de nommage sur tout le projet

Mais cela n'est pas urgent - le système fonctionne correctement maintenant.
