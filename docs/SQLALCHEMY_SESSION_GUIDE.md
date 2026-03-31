# 📖 Guide: SQLAlchemy Session Management - Best Practices

## 🎯 Objectif

Éviter les erreurs `"Parent instance not bound to a Session"` en gérant correctement les sessions SQLAlchemy.

## ⚡ Les Deux Patterns Principaux

### 1️⃣ Pattern Eager Loading (Recommandé)

**Cas d'usage:** Vous savez que vous aurez besoin des relations lors de la récupération.

```python
from sqlalchemy.orm import joinedload

# Service layer
@with_db_session
def get_planning(self, planning_id=None, db=None):
    """Retourne Planning avec relations préchargées"""
    query = db.query(Planning)

    # ✅ Eager load pour éviter lazy load errors
    query = query.options(
        joinedload(Planning.repas).joinedload(Repas.recette)
    )

    if planning_id:
        query = query.filter(Planning.id == planning_id)
    else:
        query = query.filter(Planning.actif == True)

    return query.first()

# UI layer - Utilisation sûre
planning = service.get_planning()

# ✅ Accessible sans erreur (déjà en mémoire)
for repas in planning.repas:
    print(repas.recette.nom)  # Accès safe
```

### 2️⃣ Pattern Context Manager (Pour les modifications)

**Cas d'usage:** Vous effectuez des opérations de lecture/écriture sur BD.

```python
# ✅ BON - Context manager avec statement
with obtenir_contexte_db() as db:
    # Opération de lecture
    recipes = db.query(Recette).all()

    # Opération de modification
    repas = db.query(Repas).filter_by(id=1).first()
    if repas:
        repas.prepare = True
        db.commit()  # Commit automatiquement avant de fermer la session

# Session fermée et nettoyée automatiquement

# ❌ MAUVAIS - Session n'est pas fermée correctement
db = next(obtenir_contexte_db())  # Anti-pattern!
repas = db.query(Repas).first()
# db reste ouvert ou se ferme de façon imprévisible
```

## 🔄 Flux Recommandé pour une Route FastAPI

```python
@router.get("/{planning_id}")
@gerer_exception_api
async def obtenir_planning(planning_id: int, user: dict = Depends(require_auth)):
    """Modèle recommandé"""

    def _query():
        with executer_avec_session() as session:
            # 1️⃣ Récupérer données avec EAGER LOADING
            planning = (
                session.query(Planning)
                .options(joinedload(Planning.repas).joinedload(Repas.recette))
                .filter(Planning.id == planning_id)
                .first()
            )
            if not planning:
                raise HTTPException(status_code=404, detail="Planning non trouvé")

            # 2️⃣ Sérialiser dans la session (relations déjà chargées)
            return {
                "id": planning.id,
                "repas": [{"id": r.id, "recette": r.recette.nom} for r in planning.repas],
            }

    return await executer_async(_query)
```

## 🎨 Checklist: Nouveaux Services

Quand vous créez un nouveau service qui retourne des objets avec relations:

```python
class MonService(BaseService):

    # ✅ Toujours eager load les relations
    @with_db_session
    def get_objet_avec_relations(self, id: int, db: Session = None):
        """Retourne objet + relations"""
        from sqlalchemy.orm import joinedload

        return (
            db.query(MonObjet)
            .options(
                joinedload(MonObjet.relation1),
                joinedload(MonObjet.relation2).joinedload(Relation2.sous_relation)
            )
            .filter(MonObjet.id == id)
            .first()
        )

    # ✅ Petite opération SANS relations (juste pour modifier)
    @with_db_session
    def marquer_prepare(self, id: int, db: Session = None) -> bool:
        """Simple update sans relations"""
        objet = db.query(MonObjet).filter(MonObjet.id == id).first()
        if objet:
            objet.prepare = True
            db.commit()
            return True
        return False
```

## 🚨 Erreurs Courantes à Éviter

### ❌ Erreur 1: Lazy Load After Session Closed

```python
# MAUVAIS
planning = db.query(Planning).first()  # Sans eager load
db.session.close()  # ou sortir du with
for repas in planning.repas:  # ❌ ERREUR!
    print(repas)
```

### ❌ Erreur 2: Using Generator Wrong

```python
# MAUVAIS - Utiliser le générateur au lieu du context manager
db = next(obtenir_contexte_db())
data = db.query(Model).all()
# db peut être fermé ici

# BON
with obtenir_contexte_db() as db:
    data = db.query(Model).all()
    # db reste ouvert ici
```

### ❌ Erreur 3: Keeping Session Open

```python
# MAUVAIS - Session trop longue
db = next(obtenir_contexte_db())
for i in range(1000):
    obj = db.query(Model).filter_by(id=i).first()
    # ... traitement ...
# Session ouverte longtemps = risque de fuites

# BON - Context managers courts
for i in range(1000):
    with obtenir_contexte_db() as db:
        obj = db.query(Model).filter_by(id=i).first()
        # ... traitement ...
```

## 📊 Joinedload Patterns

### Simple relation

```python
.options(joinedload(Parent.children))
```

### Relation imbriquée (1-2 niveaux)

```python
.options(
    joinedload(Parent.children)
    .joinedload(Child.grandchildren)
)
```

### Plusieurs relations

```python
.options(
    joinedload(Parent.children),
    joinedload(Parent.other_relation)
)
```

### Relation avec filtre

```python
from sqlalchemy.orm import contains_eager

.outerjoin(Parent.children)
.options(contains_eager(Parent.children))
.filter(Child.active == True)
```

## 🔒 Bonnes Pratiques en Résumé

| Practice           | Bon ✅                       | Mauvais ❌                     |
| ------------------ | ---------------------------- | ------------------------------ |
| **Session courte** | `with obtenir_contexte_db()` | Garder session longtemps       |
| **Relations**      | `joinedload()` dans service  | Lazy load après session fermée |
| **Modifications**  | Context manager séparé       | Réutiliser la session          |
| **Erreurs**        | Attraper dans le service     | Laisser remonter               |
| **Logging**        | Info au service level        | Rien ou debug                  |

## 🧪 Test: Comment vérifier

```python
import pytest

def test_planning_relations_accessible():
    """Vérifier que les relations sont accessibles"""
    service = PlanningService()
    planning = service.get_planning()

    # ✅ Ne doit pas lever d'erreur
    assert len(planning.repas) >= 0

    # ✅ Repas et recettes doivent être accessibles
    for repas in planning.repas:
        assert repas.recette.nom  # Pas d'erreur ici!

def test_modifications_isolated():
    """Vérifier que les modifications utilisent context managers"""
    service = PlanningService()

    # ✅ Doit marcher sans erreur
    service.marquer_prepare(repas_id=1)
```

## 🎓 Ressources

- [SQLAlchemy Eager Loading](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#eager-loading)
- [Context Managers Python](https://docs.python.org/3/library/contextlib.html)
- Error Reference: [sqlalche.me/e/20/bhk3](https://sqlalche.me/e/20/bhk3)

---

**Version:** 1.1 (Sprint H — avril 2026)
**Date initiale:** 30 Janvier 2026
**Auteur:** GitHub Copilot
**Pour:** Assistant Matanne Codebase

---

## Mise à jour Sprint H — Patterns FastAPI

### Pattern routes FastAPI (`executer_avec_session`)

Dans les routes FastAPI, utiliser `executer_avec_session()` + `executer_async()` :

```python
from src.api.utils import executer_async, executer_avec_session

@router.get("/recettes")
@gerer_exception_api
async def lister_recettes(user: dict = Depends(require_auth)) -> dict:
    def _query():
        # executer_avec_session() gère ouverture/fermeture + commit/rollback
        with executer_avec_session() as session:
            recettes = session.query(Recette).filter_by(user_id=user["id"]).all()
            # ✅ Sérialiser DANS le context manager — avant fermeture de session
            return [{"id": r.id, "nom": r.nom} for r in recettes]
    # executer_async() exécute _query dans un thread pool (non-blocking)
    return await executer_async(_query)
```

**Règles clés :**
- `executer_avec_session()` = `obtenir_contexte_db()` adapté pour les routes
- Ne JAMAIS retourner des objets SQLAlchemy hors du `with` — les sérialiser à l'intérieur
- `executer_async()` est obligatoire pour les endpoints `async def` — évite le blocage de l'event loop

### Comparatif des 3 patterns

| Pattern | Usage | Fichier |
|---------|-------|---------|
| `executer_avec_session()` | Routes FastAPI | `src/api/utils/__init__.py` |
| `@avec_session_db` | Services métier | `src/core/decorators/db.py` |
| `obtenir_contexte_db()` | Flux complexes manuels | `src/core/db/session.py` |

### Anti-pattern : retourner un objet ORM hors session

```python
# ❌ MAUVAIS — détached instance error à l'accès de relations
async def get_recette(id: int):
    def _query():
        with executer_avec_session() as session:
            return session.query(Recette).get(id)  # Retourne l'objet ORM !
    recette = await executer_async(_query)
    return recette.ingredients  # 💥 DetachedInstanceError

# ✅ BON — sérialiser dans le context manager
async def get_recette(id: int):
    def _query():
        with executer_avec_session() as session:
            r = session.query(Recette).options(joinedload(Recette.ingredients)).get(id)
            return {
                "id": r.id,
                "nom": r.nom,
                "ingredients": [{"id": i.id, "nom": i.nom} for i in r.ingredients]
            }
    return await executer_async(_query)
```

### Test avec `executer_avec_session`

Dans les tests, les mêmes patterns s'appliquent avec la `test_db` fixture :

```python
def test_create_recette(test_db):
    """test_db est une session SQLite in-memory (conftest.py)"""
    recette = Recette(nom="Tarte", user_id=1)
    test_db.add(recette)
    test_db.commit()
    
    result = test_db.query(Recette).filter_by(nom="Tarte").first()
    assert result.nom == "Tarte"
    # Session nettoyée automatiquement après le test (rollback dans conftest)
```
