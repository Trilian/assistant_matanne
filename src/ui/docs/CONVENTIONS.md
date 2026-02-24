# Conventions UI

Règles et conventions à respecter pour tous les composants UI.

---

## Nommage

### Fonctions publiques (français)

| Préfixe | Usage | Exemple |
|---------|-------|---------|
| `afficher_*` | Rend du contenu à l'écran | `afficher_badges_jardin()` |
| `obtenir_*` | Retourne une valeur | `obtenir_theme_actif()` |
| `definir_*` | Modifie un état | `definir_mode_tablette()` |
| `creer_*` | Crée un élément | `creer_graphique()` |
| `carte_*` | Widget type card | `carte_metrique()` |
| `graphique_*` | Widget Plotly | `graphique_repartition_repas()` |

### Classes

- **PascalCase français** : `Modale`, `SuiviProgression`, `EtatChargement`
- **Enums** : `Variante`, `ModeTablette`, `Animation`

### Fichiers

- **snake_case** : `atoms.py`, `chat_contextuel.py`, `tokens_semantic.py`
- Un fichier par responsabilité logique

---

## Structure d'un composant

```python
"""Module atoms — composants atomiques réutilisables."""

from src.ui.registry import composant_ui
from src.ui.tokens import Variante

@composant_ui(
    categorie="atoms",
    exemple='badge("Actif", variante=Variante.SUCCESS)',
    tags=("inline", "status"),
)
def badge(texte: str, variante: Variante = Variante.PRIMARY) -> None:
    """Affiche un badge coloré.

    Args:
        texte: Texte du badge.
        variante: Variante sémantique (PRIMARY, SUCCESS, DANGER, etc.).

    Example:
        >>> badge("En cours", variante=Variante.INFO)
    """
    ...
```

### Checklist composant

- [ ] Docstring en français avec Args et Example
- [ ] Décorateur `@composant_ui` avec catégorie et exemple
- [ ] Variantes sémantiques (pas de couleurs brutes)
- [ ] Tokens sémantiques pour le HTML custom (`Sem.*`)
- [ ] Attributs ARIA si interactif (`A11y.aria(...)`)
- [ ] Exporté dans `src/ui/__init__.py`

---

## Imports

### Import recommandé

```python
# Depuis le point d'entrée unifié
from src.ui import badge, etat_vide, Modale, Variante

# Depuis un sous-package spécifique (pour imports internes)
from src.ui.components.atoms import badge
from src.ui.feedback.toasts import afficher_succes
```

### Règles

1. **Point d'entrée unique** : `src.ui` re-exporte tout
2. **Imports paresseux dans les modules** : garder les imports dans `app()`
3. **Pas d'import circulaire** : `src/ui/` n'importe jamais depuis `src/modules/`

---

## Décorateurs UI — Ordre d'empilement

Quand plusieurs décorateurs sont combinés, respecter cet ordre (de haut en bas) :

```python
@composant_ui(categorie="charts", exemple="...")  # 1. Registre (métadonnées)
@st.cache_data(ttl=300)                            # 2. Cache Streamlit (si applicable)
def graphique_repartition_repas(data):              # 3. Fonction
    ...
```

```python
@composant_ui(categorie="feedback", exemple="...")  # 1. Registre
@ui_fragment                                         # 2. Fragment isolé
def afficher_chat_contextuel():                      # 3. Fonction
    ...
```

### Règles

- `@composant_ui` toujours en **premier** (le plus haut)
- `@st.cache_data` avant la fonction mais après `@composant_ui`
- `@ui_fragment` / `@cached_fragment` après `@composant_ui`
- Ne **jamais** combiner `@st.cache_data` et `@ui_fragment` sur la même fonction

---

## Thèmes et couleurs

### Interdits

```python
# ❌ Couleur hex brute
st.markdown('<span style="color: #27ae60">OK</span>', unsafe_allow_html=True)

# ❌ Streamlit color sans variante
st.success("OK")  # Acceptable seulement pour les feedback temporaires
```

### Recommandés

```python
# ✅ Variante sémantique
badge("OK", variante=Variante.SUCCESS)

# ✅ Token sémantique pour HTML custom
from src.ui.tokens_semantic import Sem
html = f'<span style="color: {Sem.SUCCESS}">{texte}</span>'
```

---

## Accessibilité

### Minimum requis

- `aria-label` sur les boutons sans texte visible (icônes seules)
- `role` sur les conteneurs sémantiques (`navigation`, `alert`, `status`)
- Contraste WCAG AA (ratio >= 4.5:1 pour le texte normal)

### Vérification

```python
from src.ui import A11y

# Vérifier le contraste
assert A11y.est_conforme_aa(couleur_texte, couleur_fond)

# HTML accessible
from src.ui import HtmlBuilder
nav = (HtmlBuilder("nav")
    .aria(role="navigation", label="Menu principal")
    .child("a", text="Accueil", href="#")
    .build())
```

---

## Tests UI

Les tests UI sont dans `tests/ui/`. Conventions :

```python
# tests/ui/test_atoms.py
import pytest

def test_badge_html_generation():
    """Le badge génère le HTML avec la bonne variante."""
    from src.ui.components.atoms import badge_html
    html = badge_html("Test", variante="success")
    assert "Test" in html
    assert "success" in html

def test_badge_vide():
    """Le badge gère le texte vide gracieusement."""
    from src.ui.components.atoms import badge_html
    html = badge_html("")
    assert html  # Ne crashe pas
```
