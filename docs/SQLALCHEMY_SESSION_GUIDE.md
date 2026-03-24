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

**Version:** 1.0  
**Date:** 30 Janvier 2026  
**Auteur:** GitHub Copilot  
**Pour:** Assistant Matanne Codebase
