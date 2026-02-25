# Guide des Composants UI

Documentation complète du Design System de l'application Assistant Matanne.

## Table des matières

- [Architecture](#architecture)
- [Composants atomiques](#composants-atomiques)
- [Patterns UI](#patterns-ui)
- [Conventions](#conventions)
- [Registre @composant_ui](#registre-composant_ui)
- [Tokens & Thèmes](#tokens--thèmes)

---

## Architecture

Le module `src/ui/` suit le pattern **Atomic Design** avec 5 couches :

```
src/ui/
├── components/          # Atomes & molécules (widgets réutilisables)
│   ├── atoms.py         # Badge, état vide, carte métrique, boîte info
│   ├── charts.py        # Graphiques Plotly (répartition repas, inventaire)
│   ├── data.py          # Pagination, tableaux, export CSV
│   ├── dynamic.py       # Dialog de confirmation (@st.dialog)
│   ├── filters.py       # Filtres et recherche
│   ├── forms.py         # Champs de formulaire
│   ├── layouts.py       # Grilles, cartes
│   ├── metrics.py       # Cartes métriques avancées
│   ├── streaming.py     # Composants streaming IA
│   └── system.py        # Santé système, timeline
├── feedback/            # Retour utilisateur
│   ├── spinners.py      # Indicateurs de chargement
│   ├── progress_v2.py   # Barres de progression
│   └── toasts.py        # Notifications temporaires
├── layout/              # Mise en page application
│   ├── header.py        # En-tête avec navigation
│   ├── sidebar.py       # Barre latérale + menu
│   ├── footer.py        # Pied de page
│   └── styles.py        # CSS global injecté
├── tablet/              # Mode tablette/cuisine
├── views/               # Vues spécifiques (auth, météo, jeux)
├── integrations/        # Services externes (Google Calendar)
├── tokens.py            # Design tokens bruts
├── tokens_semantic.py   # Tokens sémantiques (dark mode)
├── theme.py             # Thème dynamique
├── a11y.py              # Accessibilité WCAG
├── animations.py        # Animations CSS
├── fragments.py         # Décorateurs @ui_fragment, @cached_fragment, @lazy
├── registry.py          # Registre @composant_ui
└── __init__.py          # Point d'entrée (~90 exports)
```

### Import centralisé

```python
# Import recommandé — tout via src.ui
from src.ui import (
    badge,
    etat_vide,
    afficher_succes,
    afficher_erreur,
    confirm_dialog,
    Variante,
)
```

---

## Composants atomiques

### Badge

Affiche un badge coloré avec texte et variante sémantique.

```python
from src.ui import badge, Variante

badge("En cours", variante=Variante.INFO)
badge("Urgent", variante=Variante.DANGER)
badge("Complété", variante=Variante.SUCCESS)
```

### État vide

Message informatif quand il n'y a pas de données.

```python
from src.ui import etat_vide

etat_vide("Aucune recette trouvée", "🍳")
```

### Carte métrique

KPI avec delta et tendance.

```python
from src.ui import carte_metrique

carte_metrique("Recettes", 42, delta="+5", tendance="hausse")
```

### Boîte d'information

Encadré contextuel avec icône et variante.

```python
from src.ui import boite_info, Variante

boite_info("Astuce", "Utilisez le batch cooking le dimanche", "💡", variante=Variante.INFO)
```

### Dialog de confirmation

Dialog modal pour actions destructives utilisant `@st.dialog` natif.

```python
from src.ui import confirm_dialog

if st.button("🗑️ Supprimer"):
    confirm_dialog(
        "Supprimer cette recette ?",
        "Cette action est irréversible.",
        on_confirm=lambda: supprimer_recette(recette_id),
    )
```

### Graphiques

Graphiques Plotly avec cache automatique.

```python
from src.ui import graphique_repartition_repas, graphique_inventaire_categories

# Répartition des repas sur le planning
graphique_repartition_repas(planning_data)

# Catégories d'inventaire
graphique_inventaire_categories(inventaire_data)
```

---

## Patterns UI

### 1. `@ui_fragment` — Fragment Streamlit isolé

Isole un bloc UI pour éviter les reruns complets de la page.

```python
from src.ui.fragments import ui_fragment

@ui_fragment
def mon_composant(data: list[dict]):
    """Composant isolé — ne provoque pas de rerun global."""
    st.subheader("Mon bloc")
    for item in data:
        st.write(item["nom"])
```

### 2. `@cached_fragment` — Fragment avec cache TTL

Combine fragment isolé + cache temporel. Idéal pour les graphiques lourds.

```python
from src.ui.fragments import cached_fragment

@cached_fragment(ttl=300)  # Cache 5 minutes
def graphique_evolution(data: list[dict]):
    """Graphique Plotly mis en cache."""
    fig = px.line(...)
    st.plotly_chart(fig, use_container_width=True)
```

### 3. `@lazy` — Chargement conditionnel

Charge un composant seulement quand une condition est remplie.

```python
from src.ui.fragments import lazy

@lazy(condition=lambda: st.session_state.get("afficher_details"), show_skeleton=True)
def details_avances(data: dict):
    """Chargé uniquement si l'utilisateur active les détails."""
    st.json(data)
```

### 4. `error_boundary` — Gestion d'erreurs UI

Encapsule un bloc UI avec gestion d'erreurs gracieuse.

```python
from src.modules._framework import error_boundary

with error_boundary("chargement_recettes"):
    afficher_liste_recettes(recettes)
# Si une exception survient → message d'erreur convivial au lieu d'un crash
```

### 5. `smart_spinner` — Spinner contextuel

Spinner avec messages dynamiques selon la durée.

```python
from src.ui.feedback import smart_spinner

with smart_spinner("Génération IA en cours...", messages_delai={
    3: "L'IA réfléchit...",
    10: "Presque fini...",
}):
    resultat = service_ia.generer(prompt)
```

---

## Conventions

### Nommage

| Pattern | Usage | Exemple |
|---------|-------|---------|
| `afficher_*` | Fonction qui rend du HTML/Streamlit | `afficher_badges_jardin()` |
| `obtenir_*` | Fonction qui retourne des données | `obtenir_theme_actif()` |
| `definir_*` | Fonction qui modifie un état | `definir_mode_tablette()` |
| `carte_*` | Widget carte/card | `carte_metrique()` |
| `graphique_*` | Widget graphique Plotly | `graphique_repartition_repas()` |

### Variantes sémantiques

Toujours utiliser `Variante` au lieu de couleurs brutes :

```python
from src.ui import Variante

# ✅ Bon
badge("OK", variante=Variante.SUCCESS)

# ❌ Éviter
st.markdown('<span style="color: green">OK</span>', unsafe_allow_html=True)
```

Variantes disponibles :
- `Variante.PRIMARY` — action principale
- `Variante.SUCCESS` — succès, validation
- `Variante.WARNING` — attention, avertissement
- `Variante.DANGER` — erreur, suppression
- `Variante.INFO` — information neutre
- `Variante.SECONDARY` — action secondaire

### Accessibilité (WCAG)

```python
from src.ui import A11y

# Vérifier le contraste
assert A11y.est_conforme_aa("#212529", "#ffffff")

# Attributs ARIA
A11y.attrs(role="navigation", label="Menu principal")
```

### Thème sombre

Utiliser les tokens sémantiques pour le support dark mode automatique :

```python
from src.ui.tokens_semantic import Sem

html = f'''
<div style="
    background: {Sem.SURFACE};
    color: {Sem.ON_SURFACE};
    border: 1px solid {Sem.BORDER};
">
    Contenu adaptatif
</div>
'''
```

---

## Registre @composant_ui

Tous les composants publics doivent être décorés avec `@composant_ui` pour
apparaître dans le catalogue du Design System.

### Décoration d'un composant

```python
from src.ui.registry import composant_ui

@composant_ui(
    categorie="feedback",
    exemple='spinner_intelligent("Chargement...")',
    tags=("loading", "animation"),
)
def spinner_intelligent(message: str = "Chargement..."):
    """Spinner avec messages dynamiques."""
    ...
```

### Consultation du registre

```python
from src.ui.registry import obtenir_registre, lister_categories

# Toutes les catégories
categories = lister_categories()  # ["atoms", "feedback", "charts", ...]

# Composants d'une catégorie
registre = obtenir_registre()
for nom, meta in registre.items():
    if meta.category == "atoms":
        print(f"{nom}: {meta.description}")
```

### Catalogue interactif

Le module `src/modules/design_system.py` fournit un explorateur interactif
type **Storybook** accessible via le menu de l'application. Il utilise
`BaseModule` pour une navigation à onglets.

---

## Tokens & Thèmes

### Tokens bruts (`tokens.py`)

```python
from src.ui.tokens import Couleur, Espacement, Rayon

Couleur.PRIMAIRE       # "#1976D2"
Couleur.SUCCES         # "#2E7D32"
Espacement.SM          # "0.5rem"
Rayon.MD               # "8px"
```

### Tokens sémantiques (`tokens_semantic.py`)

Les tokens sémantiques s'adaptent automatiquement au thème clair/sombre :

```python
from src.ui.tokens_semantic import Sem

Sem.SURFACE        # var(--surface)
Sem.ON_SURFACE     # var(--on-surface)
Sem.PRIMARY        # var(--primary)
Sem.BORDER         # var(--border)
```

### Thème dynamique (`theme.py`)

```python
from src.ui.theme import obtenir_theme, appliquer_theme

theme = obtenir_theme()  # "clair" | "sombre" | "auto"
appliquer_theme("sombre")
```
