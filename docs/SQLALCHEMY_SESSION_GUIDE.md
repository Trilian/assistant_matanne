# ðŸ“– Guide: SQLAlchemy Session Management - Best Practices

## ðŸŽ¯ Objectif

Ã‰viter les erreurs `"Parent instance not bound to a Session"` en gÃ©rant correctement les sessions SQLAlchemy.

## âš¡ Les Deux Patterns Principaux

### 1ï¸âƒ£ Pattern Eager Loading (RecommandÃ©)

**Cas d'usage:** Vous savez que vous aurez besoin des relations lors de la rÃ©cupÃ©ration.

```python
from sqlalchemy.orm import joinedload

# Service layer
@with_db_session
def get_planning(self, planning_id=None, db=None):
    """Retourne Planning avec relations prÃ©chargÃ©es"""
    query = db.query(Planning)

    # âœ… Eager load pour Ã©viter lazy load errors
    query = query.options(
        joinedload(Planning.repas).joinedload(Repas.recette)
    )

    if planning_id:
        query = query.filter(Planning.id == planning_id)
    else:
        query = query.filter(Planning.actif == True)

    return query.first()

# UI layer - Utilisation sÃ»re
planning = service.get_planning()

# âœ… Accessible sans erreur (dÃ©jÃ  en mÃ©moire)
for repas in planning.repas:
    print(repas.recette.nom)  # AccÃ¨s safe
```

### 2ï¸âƒ£ Pattern Context Manager (Pour les modifications)

**Cas d'usage:** Vous effectuez des opÃ©rations de lecture/Ã©criture sur BD.

```python
# âœ… BON - Context manager avec statement
with obtenir_contexte_db() as db:
    # OpÃ©ration de lecture
    recipes = db.query(Recette).all()

    # OpÃ©ration de modification
    repas = db.query(Repas).filter_by(id=1).first()
    if repas:
        repas.prepare = True
        db.commit()  # Commit automatiquement avant de fermer la session

# Session fermÃ©e et nettoyÃ©e automatiquement

# âŒ MAUVAIS - Session n'est pas fermÃ©e correctement
db = next(obtenir_contexte_db())  # Anti-pattern!
repas = db.query(Repas).first()
# db reste ouvert ou se ferme de faÃ§on imprÃ©visible
```

## ðŸ”„ Flux RecommandÃ© pour une Route FastAPI

```python
@router.get("/{planning_id}")
@gerer_exception_api
async def obtenir_planning(planning_id: int, user: dict = Depends(require_auth)):
    """ModÃ¨le recommandÃ©"""

    def _query():
        with executer_avec_session() as session:
            # 1ï¸âƒ£ RÃ©cupÃ©rer donnÃ©es avec EAGER LOADING
            planning = (
                session.query(Planning)
                .options(joinedload(Planning.repas).joinedload(Repas.recette))
                .filter(Planning.id == planning_id)
                .first()
            )
            if not planning:
                raise HTTPException(status_code=404, detail="Planning non trouvÃ©")

            # 2ï¸âƒ£ SÃ©rialiser dans la session (relations dÃ©jÃ  chargÃ©es)
            return {
                "id": planning.id,
                "repas": [{"id": r.id, "recette": r.recette.nom} for r in planning.repas],
            }

    return await executer_async(_query)
```

## ðŸŽ¨ Checklist: Nouveaux Services

Quand vous crÃ©ez un nouveau service qui retourne des objets avec relations:

```python
class MonService(BaseService):

    # âœ… Toujours eager load les relations
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

    # âœ… Petite opÃ©ration SANS relations (juste pour modifier)
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

## ðŸš¨ Erreurs Courantes Ã  Ã‰viter

### âŒ Erreur 1: Lazy Load After Session Closed

```python
# MAUVAIS
planning = db.query(Planning).first()  # Sans eager load
db.session.close()  # ou sortir du with
for repas in planning.repas:  # âŒ ERREUR!
    print(repas)
```

### âŒ Erreur 2: Using Generator Wrong

```python
# MAUVAIS - Utiliser le gÃ©nÃ©rateur au lieu du context manager
db = next(obtenir_contexte_db())
data = db.query(Model).all()
# db peut Ãªtre fermÃ© ici

# BON
with obtenir_contexte_db() as db:
    data = db.query(Model).all()
    # db reste ouvert ici
```

### âŒ Erreur 3: Keeping Session Open

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

## ðŸ“Š Joinedload Patterns

### Simple relation

```python
.options(joinedload(Parent.children))
```

### Relation imbriquÃ©e (1-2 niveaux)

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

## ðŸ”’ Bonnes Pratiques en RÃ©sumÃ©

| Practice           | Bon âœ…                       | Mauvais âŒ                     |
| ------------------ | ---------------------------- | ------------------------------ |
| **Session courte** | `with obtenir_contexte_db()` | Garder session longtemps       |
| **Relations**      | `joinedload()` dans service  | Lazy load aprÃ¨s session fermÃ©e |
| **Modifications**  | Context manager sÃ©parÃ©       | RÃ©utiliser la session          |
| **Erreurs**        | Attraper dans le service     | Laisser remonter               |
| **Logging**        | Info au service level        | Rien ou debug                  |

## ðŸ§ª Test: Comment vÃ©rifier

```python
import pytest

def test_planning_relations_accessible():
    """VÃ©rifier que les relations sont accessibles"""
    service = PlanningService()
    planning = service.get_planning()

    # âœ… Ne doit pas lever d'erreur
    assert len(planning.repas) >= 0

    # âœ… Repas et recettes doivent Ãªtre accessibles
    for repas in planning.repas:
        assert repas.recette.nom  # Pas d'erreur ici!

def test_modifications_isolated():
    """VÃ©rifier que les modifications utilisent context managers"""
    service = PlanningService()

    # âœ… Doit marcher sans erreur
    service.marquer_prepare(repas_id=1)
```

## ðŸŽ“ Ressources

- [SQLAlchemy Eager Loading](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html#eager-loading)
- [Context Managers Python](https://docs.python.org/3/library/contextlib.html)
- Error Reference: [sqlalche.me/e/20/bhk3](https://sqlalche.me/e/20/bhk3)

---

**Version:** 1.1 (Sprint H â€” avril 2026)
**Date initiale:** 30 Janvier 2026
**Auteur:** GitHub Copilot
**Pour:** Assistant Matanne Codebase

---

## Mise Ã  jour Sprint H â€” Patterns FastAPI

### Pattern routes FastAPI (`executer_avec_session`)

Dans les routes FastAPI, utiliser `executer_avec_session()` + `executer_async()` :

```python
from src.api.utils import executer_async, executer_avec_session

@router.get("/recettes")
@gerer_exception_api
async def lister_recettes(user: dict = Depends(require_auth)) -> dict:
    def _query():
        # executer_avec_session() gÃ¨re ouverture/fermeture + commit/rollback
        with executer_avec_session() as session:
            recettes = session.query(Recette).filter_by(user_id=user["id"]).all()
            # âœ… SÃ©rialiser DANS le context manager â€” avant fermeture de session
            return [{"id": r.id, "nom": r.nom} for r in recettes]
    # executer_async() exÃ©cute _query dans un thread pool (non-blocking)
    return await executer_async(_query)
```

**RÃ¨gles clÃ©s :**
- `executer_avec_session()` = `obtenir_contexte_db()` adaptÃ© pour les routes
- Ne JAMAIS retourner des objets SQLAlchemy hors du `with` â€” les sÃ©rialiser Ã  l'intÃ©rieur
- `executer_async()` est obligatoire pour les endpoints `async def` â€” Ã©vite le blocage de l'event loop

### Comparatif des 3 patterns

| Pattern | Usage | Fichier |
| --------- | ------- | --------- |
| `executer_avec_session()` | Routes FastAPI | `src/api/utils/__init__.py` |
| `@avec_session_db` | Services mÃ©tier | `src/core/decorators/db.py` |
| `obtenir_contexte_db()` | Flux complexes manuels | `src/core/db/session.py` |

### Anti-pattern : retourner un objet ORM hors session

```python
# âŒ MAUVAIS â€” dÃ©tached instance error Ã  l'accÃ¨s de relations
async def get_recette(id: int):
    def _query():
        with executer_avec_session() as session:
            return session.query(Recette).get(id)  # Retourne l'objet ORM !
    recette = await executer_async(_query)
    return recette.ingredients  # ðŸ’¥ DetachedInstanceError

# âœ… BON â€” sÃ©rialiser dans le context manager
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

Dans les tests, les mÃªmes patterns s'appliquent avec la `test_db` fixture :

```python
def test_create_recette(test_db):
    """test_db est une session SQLite in-memory (conftest.py)"""
    recette = Recette(nom="Tarte", user_id=1)
    test_db.add(recette)
    test_db.commit()
    
    result = test_db.query(Recette).filter_by(nom="Tarte").first()
    assert result.nom == "Tarte"
    # Session nettoyÃ©e automatiquement aprÃ¨s le test (rollback dans conftest)
```
