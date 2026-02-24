# Patterns & Bonnes Pratiques UI

Référence des patterns architecturaux utilisés dans le Design System.

---

## 1. Fragment Pattern

### Problème
Streamlit re-exécute tout le script à chaque interaction. Les composants
complexes avec état local (toggle, form) provoquent des reruns inutiles.

### Solution
Utiliser `@ui_fragment` pour isoler les blocs UI.

```python
from src.ui.fragments import ui_fragment

@ui_fragment
def formulaire_recette(recette: dict):
    """Fragment isolé — les interactions internes ne rerun pas la page."""
    with st.form("edit_recette"):
        nom = st.text_input("Nom", value=recette["nom"])
        if st.form_submit_button("Sauver"):
            sauver(nom)
```

### Variantes

| Décorateur | Usage | Cache |
|-----------|-------|-------|
| `@ui_fragment` | Bloc isolé standard | Non |
| `@cached_fragment(ttl=N)` | Bloc avec cache temporel | Oui, N secondes |
| `@lazy(condition=fn)` | Chargement conditionnel | Non |

---

## 2. Error Boundary Pattern

### Problème
Une erreur dans un composant fait crasher toute la page.

### Solution
Encapsuler les sections risquées avec `error_boundary`.

```python
from src.ui import error_boundary

with error_boundary("section_graphiques"):
    # Si plotly n'est pas installé ou les données sont invalides,
    # un message d'erreur s'affiche au lieu d'un crash
    graphique_evolution(data)
```

### Bonnes pratiques
- Un `error_boundary` par section logique (pas par composant)
- Nommer le boundary pour faciliter le debug (le nom apparaît dans les logs)
- Ne pas imbriquer les error boundaries

---

## 3. Service Injection Pattern

### Problème
Les composants UI ne doivent pas instancier directement les services.

### Solution
Les modules utilisent `BaseModule` avec injection de service :

```python
from src.modules._framework import BaseModule, module_app

class MonModule(BaseModule[MonService]):
    nom_module = "mon_module"
    titre = "Mon Module"
    icone = "🔧"

    def obtenir_service(self) -> MonService:
        return get_mon_service()

    def definir_onglets(self) -> list[tuple[str, Callable]]:
        return [
            ("📋 Liste", self.onglet_liste),
            ("➕ Ajouter", self.onglet_ajout),
        ]

    def onglet_liste(self):
        items = self.service.lister()
        for item in items:
            st.write(item.nom)

app = module_app(MonModule)
```

---

## 4. Modale Pattern

### Problème
Streamlit n'a pas de modales natives. Les `st.dialog` sont limités.

### Solution
`Modale` gère l'état d'affichage via `session_state`.

```python
from src.ui import Modale

# Créer une modale avec un ID unique
modal = Modale("confirmer_suppression")

# Bouton déclencheur
if st.button("🗑️ Supprimer"):
    modal.ouvrir()

# Contenu de la modale
if modal.est_affichee():
    st.warning("Êtes-vous sûr ?")
    col1, col2 = st.columns(2)
    with col1:
        if modal.confirmer("Oui, supprimer"):
            supprimer_item()
            modal.fermer()
            st.rerun()
    with col2:
        modal.annuler("Annuler")
```

---

## 5. Composant Registré Pattern

### Problème
Pas de catalogue centralisé des composants UI disponibles.

### Solution
Décorer avec `@composant_ui` pour le registre automatique.

```python
from src.ui.registry import composant_ui

@composant_ui(
    categorie="feedback",
    exemple='mon_spinner("Chargement...")',
    tags=("loading",),
)
def mon_spinner(message: str):
    """Spinner personnalisé."""
    st.spinner(message)
```

### Convention
- Tout composant public doit avoir `@composant_ui`
- Le décorateur se place **avant** `@st.cache_data` ou `@ui_fragment`
- La catégorie correspond au sous-package (`atoms`, `charts`, `feedback`, etc.)

---

## 6. Tokens Sémantiques Pattern

### Problème
Couleurs brutes cassent le dark mode et compliquent le re-theming.

### Solution
Utiliser les CSS custom properties de `tokens_semantic.py`.

```python
from src.ui.tokens_semantic import Sem

# Au lieu de :
html = '<div style="background: #1a1a2e; color: white;">...'

# Préférer :
html = f'<div style="background: {Sem.SURFACE}; color: {Sem.ON_SURFACE};">...'
```

Les tokens sont des `var(--nom)` CSS qui s'adaptent automatiquement au thème.

---

## 7. Hook Pattern

### Problème
Logique de pagination, recherche, filtrage dupliquée entre modules.

### Solution
Hooks composables inspirés de React :

```python
from src.ui.hooks import use_pagination, use_recherche

def afficher_liste_recettes(recettes: list[dict]):
    # Recherche
    filtered, show_search = use_recherche(recettes, ["nom", "categorie"])

    # Pagination
    visible, show_pagination = use_pagination(filtered, per_page=12)

    # Rendu
    show_search()
    for recette in visible:
        afficher_carte_recette(recette)
    show_pagination()
```

---

## Anti-patterns à éviter

| Anti-pattern | Pourquoi | Alternative |
|-------------|----------|-------------|
| `st.markdown` avec CSS inline brut | Casse dark mode | Utiliser `Sem.*` tokens |
| `st.session_state` directement pour nav | Risque de collision | `naviguer("module.page")` |
| `st.cache_data` sur composant UI | Le cache ne gère pas les widgets Streamlit | `@cached_fragment(ttl=N)` |
| Instancier un service dans l'UI | Couplage fort | `BaseModule` + injection |
| Couleurs hex dans les composants | Pas de dark mode | `Variante` sémantique |
| `st.rerun()` dans un fragment | Boucle infinie possible | Gérer l'état localement |
