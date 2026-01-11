# 📚 Exemples Pratiques - Refactoring Phase 1

Guide pratique pour refactoriser votre code avec les nouveaux patterns.

---

## 1️⃣ Utiliser `@with_db_session` dans les Services

### ❌ AVANT (Code ancien)
```python
from src.core.errors import gerer_erreurs
from src.core.database import obtenir_contexte_db

class RecetteService:
    @gerer_erreurs(afficher_dans_ui=True)
    def creer_recette(self, data: dict, db: Session | None = None) -> Recette:
        """Création manuelle de session"""
        def _execute(session: Session) -> Recette:
            recette = Recette(
                nom=data.get("nom"),
                temps_prep=data.get("temps_prep"),
                temps_cuisson=data.get("temps_cuisson"),
                portions=data.get("portions")
            )
            session.add(recette)
            session.commit()
            session.refresh(recette)
            return recette
        
        return self._with_session(_execute, db)
```

### ✅ APRÈS (Code nouveau)
```python
from src.core.decorators import with_db_session
from src.core.validators_pydantic import RecetteInput

class RecetteService:
    @with_db_session
    def creer_recette(self, data: dict, db: Session) -> Recette:
        """Session injectée automatiquement + validation Pydantic"""
        # Validation + nettoyage auto
        validated = RecetteInput(**data)
        
        recette = Recette(**validated.model_dump())
        db.add(recette)
        db.commit()
        db.refresh(recette)
        return recette
```

**Gains:**
- ✅ -50% de boilerplate code
- ✅ Signature plus claire (pas `| None`)
- ✅ Validation centralisée

---

## 2️⃣ Ajouter Validation Pydantic dans les Formulaires

### ❌ AVANT (Validations manuelles)
```python
def render_recettes_ajout():
    """Ajouter recette - version ancienne"""
    with st.form("form_recette"):
        nom = st.text_input("Nom")
        temps_prep = st.number_input("Temps prep (min)", 1, 300)
        temps_cuisson = st.number_input("Temps cuisson (min)", 0, 300)
        portions = st.number_input("Portions", 1, 50, 4)
        
        submitted = st.form_submit_button("Créer")
        
        if submitted:
            # Validations manuelles 😞
            if not nom or len(nom.strip()) == 0:
                st.error("Le nom est vide")
                return
            
            if temps_prep < 1 or temps_prep > 300:
                st.error("Temps prep invalide")
                return
            
            if temps_cuisson < 0 or temps_cuisson > 300:
                st.error("Temps cuisson invalide")
                return
            
            if portions < 1 or portions > 50:
                st.error("Portions invalides")
                return
            
            # Finalement créer la recette
            try:
                recette = recette_service.creer_recette({
                    "nom": nom.strip(),
                    "temps_prep": temps_prep,
                    "temps_cuisson": temps_cuisson,
                    "portions": portions
                })
                st.success(f"✅ Recette '{nom}' créée!")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
```

### ✅ APRÈS (Validation Pydantic)
```python
from src.core.validators_pydantic import RecetteInput

def render_recettes_ajout():
    """Ajouter recette - version optimisée"""
    with st.form("form_recette"):
        nom = st.text_input("Nom")
        temps_prep = st.number_input("Temps prep (min)", 1, 300)
        temps_cuisson = st.number_input("Temps cuisson (min)", 0, 300)
        portions = st.number_input("Portions", 1, 50, 4)
        
        submitted = st.form_submit_button("Créer")
        
        if submitted:
            try:
                # Une seule validation Pydantic! 🎉
                validated = RecetteInput(
                    nom=nom,
                    temps_prep=temps_prep,
                    temps_cuisson=temps_cuisson,
                    portions=portions
                )
                
                recette = recette_service.creer_recette(
                    validated.model_dump()
                )
                st.success(f"✅ Recette '{validated.nom}' créée!")
                st.rerun()
                
            except ValidationError as e:
                # Pydantic donne des erreurs claires
                st.error("❌ Données invalides:")
                for error in e.errors():
                    field = error["loc"][0]
                    msg = error["msg"]
                    st.error(f"  • {field}: {msg}")
```

**Gains:**
- ✅ Zéro validation manuelle
- ✅ Messages d'erreur standards et clairs
- ✅ Champs auto-nettoyés (ex: `.strip()`)
- ✅ Réutilisable dans API, tests, etc.

---

## 3️⃣ Utiliser `@with_cache` pour Cache Automatique

### ❌ AVANT (Cache manuel)
```python
def lister_recettes(self, user_id: int) -> list[Recette]:
    """Listing avec cache manuel"""
    from src.core.cache import Cache
    
    cache_key = f"recettes_user_{user_id}"
    cached = Cache.obtenir(cache_key, ttl=3600)
    if cached:
        return cached
    
    with obtenir_contexte_db() as db:
        recettes = db.query(Recette).filter(
            Recette.user_id == user_id
        ).all()
    
    Cache.definir(cache_key, recettes)
    return recettes
```

### ✅ APRÈS (Cache avec décorateur)
```python
from src.core.decorators import with_cache, with_db_session

class RecetteService:
    @with_cache(ttl=3600, key_func=lambda self, uid: f"recettes_user_{uid}")
    @with_db_session
    def lister_recettes(self, user_id: int, db: Session) -> list[Recette]:
        """Listing - cache géré auto"""
        return db.query(Recette).filter(
            Recette.user_id == user_id
        ).all()
```

**Gains:**
- ✅ Cache géré automatiquement
- ✅ Déclaratif (on voit le TTL en haut)
- ✅ Composable avec autres décorateurs

---

## 4️⃣ Composabilité de Décorateurs

Les décorateurs se composent pour créer des fonctions robustes:

```python
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.validators_pydantic import RecetteInput

class RecetteService:
    
    # Stack complet: Validation + Cache + DB + Erreurs
    @with_error_handling(
        catch=(ErreurBaseDeDonnees, ErreurValidation),
        afficher_dans_ui=True,
        fallback=None
    )
    @with_cache(ttl=3600, key_func=lambda self, rid: f"recette_{rid}")
    @with_db_session
    def get_recette_complete(
        self, 
        recipe_id: int, 
        db: Session
    ) -> Recette | None:
        """
        Récupère recette avec cache + gestion d'erreurs.
        
        Ordre d'exécution:
        1. @with_error_handling capture les exceptions
        2. @with_cache vérifie/stocke en cache
        3. @with_db_session injecte la session
        4. Fonction exécutée
        """
        return db.query(Recette).get(recipe_id)
    
    # Validation avant insertion
    @with_error_handling(catch=ErreurValidation)
    @with_validation(RecetteInput)  # Valide data avant
    @with_db_session
    def creer_recette(
        self,
        data: dict,  # Validé automatiquement
        db: Session
    ) -> Recette:
        """Crée recette avec validation auto"""
        recette = Recette(**data)
        db.add(recette)
        db.commit()
        self._invalider_cache()
        return recette
    
    # Bulk operation avec cache invalidation
    @with_error_handling(catch=ErreurBaseDeDonnees)
    @with_db_session
    def bulk_update_recettes(
        self,
        updates: list[dict],
        db: Session
    ) -> int:
        """Update plusieurs recettes"""
        count = 0
        for update in updates:
            recette_id = update.pop("id")
            db.query(Recette).filter(
                Recette.id == recette_id
            ).update(update)
            count += 1
        db.commit()
        self._invalider_cache()  # Reset all caches
        return count
```

---

## 5️⃣ Refactoriser des Validations Existantes

### ❌ AVANT (Fonction helper manuelle)
```python
from src.core.errors import exiger_champs

def creer_repas(data: dict):
    """Validation manuelle"""
    exiger_champs(data, ["nom", "date_repas", "type_repas"], "repas")
    
    if not isinstance(data["date_repas"], date):
        raise ErreurValidation("date_repas doit être une date")
    
    if data.get("portions", 0) < 1:
        raise ErreurValidation("portions doit être > 0")
    
    # Enfin créer le repas...
```

### ✅ APRÈS (Pydantic)
```python
from src.core.validators_pydantic import RepasInput
from pydantic import ValidationError

def creer_repas(data: dict):
    """Validation Pydantic"""
    try:
        validated = RepasInput(**data)
        # Tous les champs sont validés et typés correctement
        # data["date_repas"] est déjà un date object
        # data["portions"] est déjà un int > 0
        
    except ValidationError as e:
        for error in e.errors():
            raise ErreurValidation(f"{error['loc'][0]}: {error['msg']}")
    
    # Enfin créer le repas...
```

---

## 6️⃣ Tester Facilement avec Pydantic

### Services Sans Streamlit (Testable!)
```python
# test_services.py
import pytest
from src.services.recettes import RecetteService
from src.core.validators_pydantic import RecetteInput
from sqlalchemy.orm import Session

def test_creer_recette(db: Session):
    """Test création recette - avec vraie DB"""
    service = RecetteService()
    
    # Utilise validators Pydantic
    input_data = RecetteInput(
        nom="Tarte aux pommes",
        temps_prep=30,
        temps_cuisson=45,
        portions=6,
        type_repas="dessert"
    )
    
    recette = service.creer_recette(
        input_data.model_dump(),
        db=db
    )
    
    assert recette.id is not None
    assert recette.nom == "Tarte Aux Pommes"  # Auto-capitalisé par validator
    assert recette.portions == 6

def test_creer_recette_validation():
    """Test que validation échoue correctement"""
    with pytest.raises(ValidationError):
        RecetteInput(
            nom="",  # ❌ Vide
            temps_prep=0,  # ❌ doit être > 0
            temps_cuisson=-10,  # ❌ doit être >= 0
            portions=100  # ❌ doit être <= 50
        )
```

---

## 7️⃣ Pattern: Créer un Nouveau Service

### Template Standard
```python
from src.core.decorators import with_db_session, with_cache, with_error_handling
from src.core.validators_pydantic import MonInput
from src.core.errors_base import ErreurNonTrouve
from src.services.types import BaseService
from sqlalchemy.orm import Session

# 1. Créer le validator Pydantic
class MonInput(BaseModel):
    """Validation input"""
    champ1: str = Field(..., min_length=1, max_length=200)
    champ2: int = Field(..., gt=0)
    champ3: Optional[str] = None

# 2. Créer le service
class MonService(BaseService[MonModel]):
    def __init__(self):
        super().__init__(MonModel, cache_ttl=3600)
    
    # 3. Utiliser les décorateurs
    @with_error_handling(catch=ErreurBaseDeDonnees)
    @with_db_session
    def creer(self, data: dict, db: Session) -> MonModel:
        """Créer avec validation"""
        validated = MonInput(**data)
        entity = MonModel(**validated.model_dump())
        db.add(entity)
        db.commit()
        self._invalider_cache()
        return entity
    
    @with_cache(ttl=3600)
    @with_db_session
    def get_by_id(self, id: int, db: Session) -> MonModel | None:
        """Récupérer avec cache"""
        return db.query(MonModel).get(id)
    
    @with_db_session
    def lister(self, skip: int = 0, limit: int = 100, db: Session = None) -> list[MonModel]:
        """Lister avec pagination"""
        return db.query(MonModel).offset(skip).limit(limit).all()
```

---

## 📝 Checklist Refactoring

Quand tu refactorises une fonction:

- [ ] Les validations manuelles sont remplacées par Pydantic
- [ ] `_with_session` est remplacé par `@with_db_session`
- [ ] Les gestions de cache manuelles sont remplacées par `@with_cache`
- [ ] Les erreurs utilisent `errors_base` (sans Streamlit)
- [ ] Les décorateurs sont composés dans le bon ordre
- [ ] Type hints sont complets
- [ ] Fonction testable (pas dépendance Streamlit)
- [ ] Docstring mise à jour

---

## 🎓 Résumé

| Ancien Pattern | Nouveau Pattern | Bénéfice |
|---|---|---|
| `@gerer_erreurs` + `_with_session` | `@with_db_session` | -50% code |
| Validations manuelles | Pydantic validators | 0 bugs validation |
| Cache manuel | `@with_cache` | Déclaratif |
| `errors.py` partout | `errors_base.py` services | Services testables |
| Pas de type hints | Type hints complets | Meilleur IDE support |

---

## 🔗 Références

- [src/core/decorators.py](src/core/decorators.py) - Décorateurs réutilisables
- [src/core/validators_pydantic.py](src/core/validators_pydantic.py) - Schémas Pydantic
- [src/core/errors_base.py](src/core/errors_base.py) - Exceptions pures
- [src/services/base_service.py](src/services/base_service.py) - Exemple utilisation

Next: **Phase 2 - Refactorer services métier** 🚀
