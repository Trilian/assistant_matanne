# Référence des Composants UI

Guide complet des composants UI réutilisables de l'application.

## Architecture

```
src/ui/
├── __init__.py          # Point d'entrée unifié
├── components/          # Composants UI réutilisables
│   ├── atoms.py         # Badge, état vide, etc.
│   ├── alertes.py       # Alertes stock
│   ├── charts.py        # Graphiques Plotly
│   ├── data.py          # Pagination, tableaux
│   ├── dynamic.py       # Modale, listes dynamiques
│   ├── forms.py         # Formulaires, recherche
│   ├── layouts.py       # Grilles, cartes, sections
│   ├── metrics.py       # Cartes métriques avancées
│   └── system.py        # Santé système, timeline
├── core/                # Modules CRUD génériques
│   ├── module_config.py # Configuration module
│   ├── crud_renderer.py # Rendu CRUD automatique
│   ├── base_form.py     # Constructeur formulaires
│   └── base_io.py       # Import/export
├── feedback/            # Notifications, spinners
│   ├── spinners.py      # Indicateurs chargement
│   └── toasts.py        # Notifications temporaires
├── layout/              # Header, sidebar, footer
├── tablet/              # Mode tablette/cuisine
│   ├── config.py        # TabletMode enum
│   ├── styles.py        # CSS tablette
│   ├── widgets.py       # Boutons tactiles
│   └── kitchen.py       # Vue recette cuisine
└── integrations/        # Intégrations externes
    └── google_calendar.py
```

---

## Composants de Base (atoms.py)

### `badge(texte, couleur)`

Badge coloré pour statuts, tags.

```python
from src.ui.components import badge

badge("Actif", "#4CAF50")          # Vert
badge("En attente", "#FF9800")    # Orange
badge("Terminé", "#2196F3")       # Bleu
```

### `etat_vide(message, icone, sous_texte)`

Affichage état vide centré.

```python
from src.ui.components import etat_vide

etat_vide("Aucune recette", "🍽️", "Ajoutez-en une")
```

### `carte_metrique(label, valeur, delta, couleur)`

Carte métrique simple. Pour version avancée, voir `carte_metrique_avancee`.

```python
from src.ui.components import carte_metrique

carte_metrique("Total", "42", "+5", "#f0f0f0")
```

### `notification(message, type)`

Notification immédiate (wrapper Streamlit). Pour notifications temporaires, utilisez les toasts.

```python
from src.ui.components import notification

notification("Sauvegardé", "success")    # st.success
notification("Erreur!", "error")          # st.error
notification("Attention", "warning")      # st.warning
notification("Info", "info")              # st.info
```

### `separateur(texte)`

Séparateur horizontal avec texte optionnel.

```python
from src.ui.components import separateur

separateur()        # Simple ligne
separateur("OU")    # Avec texte
```

### `boite_info(titre, contenu, icone)`

Boîte d'information stylée.

```python
from src.ui.components import boite_info

boite_info("Astuce", "Utilisez Ctrl+S pour sauvegarder", "💡")
```

---

## Alertes (alertes.py)

### `alerte_stock(...)`

Alerte pour stock bas.

```python
from src.ui.components import alerte_stock

alerte_stock(produit="Lait", quantite=1, seuil=3)
```

---

## Graphiques (charts.py)

Tous les graphiques utilisent Plotly et sont cachés avec `@st.cache_data(ttl=300)`.

### `graphique_repartition_repas(data)`

Graphique circulaire des types de repas.

```python
from src.ui.components import graphique_repartition_repas

data = [
    {"type": "Petit-déjeuner", "count": 7},
    {"type": "Déjeuner", "count": 7},
    {"type": "Dîner", "count": 7},
]
graphique_repartition_repas(data)
```

### `graphique_inventaire_categories(data)`

Barres horizontales par catégorie d'inventaire.

```python
from src.ui.components import graphique_inventaire_categories

data = [
    {"categorie": "Fruits", "quantite": 15},
    {"categorie": "Légumes", "quantite": 20},
]
graphique_inventaire_categories(data)
```

### `graphique_activite_semaine(data)`

Courbe d'activité sur 7 jours.

```python
from src.ui.components import graphique_activite_semaine

data = [
    {"jour": "Lun", "activites": 5},
    {"jour": "Mar", "activites": 3},
    # ...
]
graphique_activite_semaine(data)
```

### `graphique_progression_objectifs(data)`

Barres de progression vers objectifs.

```python
from src.ui.components import graphique_progression_objectifs

data = [
    {"objectif": "Sport", "progression": 75, "cible": 100},
    {"objectif": "Lecture", "progression": 50, "cible": 60},
]
graphique_progression_objectifs(data)
```

---

## Métriques Avancées (metrics.py)

### `carte_metrique_avancee(...)`

Carte métrique complète avec icône, delta, gradient et lien optionnel.
Cachée avec `@st.cache_data(ttl=60)`.

```python
from src.ui.components import carte_metrique_avancee

carte_metrique_avancee(
    titre="Recettes",
    valeur="42",
    icone="🍽️",
    delta="+5 cette semaine",
    delta_positif=True,
    sous_titre="Dernière: Tarte aux pommes",
    couleur="#4CAF50",
    lien_module="recettes"  # Navigation auto
)
```

### `widget_jules_apercu()`

Widget d'aperçu pour Jules (enfant).

```python
from src.ui.components import widget_jules_apercu

widget_jules_apercu()
```

### `widget_meteo_jour()`

Widget météo du jour.

```python
from src.ui.components import widget_meteo_jour

widget_meteo_jour()
```

---

## Système (system.py)

### `indicateur_sante_systeme()`

Retourne les données de santé système.

```python
from src.ui.components import indicateur_sante_systeme

donnees = indicateur_sante_systeme()
# {"status": "ok", "db": "connected", "cache": "active", ...}
```

### `afficher_sante_systeme()`

Affiche le dashboard de santé système.

```python
from src.ui.components import afficher_sante_systeme

afficher_sante_systeme()
```

### `afficher_timeline_activites(activites)`

Timeline verticale d'activités.

```python
from src.ui.components import afficher_timeline_activites

activites = [
    {"heure": "08:00", "titre": "Réveil", "icone": "☀️"},
    {"heure": "09:00", "titre": "Sport", "icone": "🏃"},
]
afficher_timeline_activites(activites)
```

---

## Formulaires (forms.py)

### `champ_formulaire(label, type, **kwargs)`

Champ de formulaire générique.

```python
from src.ui.components import champ_formulaire

valeur = champ_formulaire("Nom", "text", placeholder="Entrez le nom")
valeur = champ_formulaire("Quantité", "number", min_value=0, max_value=100)
valeur = champ_formulaire("Date", "date")
```

### `barre_recherche(texte_indicatif, cle)`

Barre de recherche avec icône.

```python
from src.ui.components import barre_recherche

terme = barre_recherche("Rechercher recettes...", "search_recettes")
```

### `panneau_filtres(config, prefixe_cle)`

Panneau de filtres dynamique.

```python
from src.ui.components import panneau_filtres

config = {
    "categorie": ["Entrée", "Plat", "Dessert"],
    "difficulte": ["Facile", "Moyen", "Difficile"],
}
filtres = panneau_filtres(config, "recettes")
# {"categorie": "Plat", "difficulte": "Facile"}
```

### `filtres_rapides(options, cle)`

Boutons de filtres rapides.

```python
from src.ui.components import filtres_rapides

selection = filtres_rapides(["Tous", "Favoris", "Récents"], "filtre_recettes")
```

---

## Données (data.py)

### `pagination(total, par_page, key)`

Contrôles de pagination.

```python
from src.ui.components import pagination

page_actuelle, total_pages = pagination(100, 20, "pagination_recettes")
```

### `ligne_metriques(stats)`

Ligne de métriques horizontale.

```python
from src.ui.components import ligne_metriques

stats = [
    {"label": "Total", "value": 42},
    {"label": "Actifs", "value": 30},
    {"label": "Archivés", "value": 12},
]
ligne_metriques(stats)
```

### `boutons_export(data, nom_fichier, formats, cle)`

Boutons d'export CSV/JSON.

```python
from src.ui.components import boutons_export

boutons_export(
    data=liste_recettes,
    nom_fichier="recettes_export",
    formats=["csv", "json"],
    cle="export_recettes"
)
```

### `tableau_donnees(data, colonnes)`

Tableau de données stylé.

```python
from src.ui.components import tableau_donnees

tableau_donnees(
    data=recettes_df,
    colonnes=["nom", "categorie", "temps_preparation"]
)
```

### `barre_progression(valeur, maximum, label)`

Barre de progression.

```python
from src.ui.components import barre_progression

barre_progression(75, 100, "Progression")
```

### `indicateur_statut(statut, texte)`

Indicateur de statut coloré.

```python
from src.ui.components import indicateur_statut

indicateur_statut("success", "Connecté")
indicateur_statut("error", "Déconnecté")
indicateur_statut("warning", "En attente")
```

---

## Layouts (layouts.py)

### `disposition_grille(items, colonnes, render_func)`

Grille responsive.

```python
from src.ui.components import disposition_grille

def render_recette(recette):
    st.write(recette.nom)

disposition_grille(recettes, colonnes=3, render_func=render_recette)
```

### `carte_item(titre, metadonnees, statut, ...)`

Carte d'item générique.

```python
from src.ui.components import carte_item

carte_item(
    titre="Tarte aux pommes",
    metadonnees=["30 min", "Facile"],
    statut="favori",
    couleur_statut="#FFD700",
    url_image="https://...",
    actions=[("Voir", lambda: ...)]
)
```

### `section_pliable(titre, contenu, ouverte)`

Section accordéon.

```python
from src.ui.components import section_pliable

with section_pliable("Détails", ouverte=False):
    st.write("Contenu caché par défaut")
```

### `disposition_onglets(onglets)`

Onglets personnalisés.

```python
from src.ui.components import disposition_onglets

tab = disposition_onglets(["Vue", "Édition", "Historique"])
```

### `conteneur_carte(titre, icone)`

Conteneur carte avec header.

```python
from src.ui.components import conteneur_carte

with conteneur_carte("Statistiques", "📊"):
    st.metric("Total", 42)
```

---

## Composants Dynamiques (dynamic.py)

### `Modale`

Modale popup.

```python
from src.ui.components import Modale

modale = Modale("Confirmation")
if modale.ouvrir():
    st.write("Êtes-vous sûr?")
    if st.button("Confirmer"):
        modale.fermer()
```

### `ListeDynamique`

Liste avec ajout/suppression dynamique.

```python
from src.ui.components import ListeDynamique

liste = ListeDynamique("ingredients", ["Farine", "Sucre"])
elements = liste.render()  # Retourne liste mise à jour
```

### `AssistantEtapes`

Assistant multi-étapes (wizard).

```python
from src.ui.components import AssistantEtapes

assistant = AssistantEtapes(["Info", "Ingrédients", "Instructions"])
etape = assistant.render()

if etape == 0:
    # Formulaire info
    pass
elif etape == 1:
    # Formulaire ingrédients
    pass
```

---

## Feedback (feedback/)

### Toasts (notifications temporaires)

```python
from src.ui.feedback import afficher_succes, afficher_erreur, afficher_avertissement, afficher_info

afficher_succes("Sauvegardé!")           # 3 sec
afficher_erreur("Échec de connexion")    # 5 sec
afficher_avertissement("Stock bas")      # 4 sec
afficher_info("Mise à jour disponible")  # 3 sec
```

### Spinners

```python
from src.ui.feedback import spinner_intelligent, indicateur_chargement, chargeur_squelette

with spinner_intelligent("Chargement..."):
    # Opération longue
    pass

indicateur_chargement()  # Spinner animé

chargeur_squelette(lignes=5)  # Skeleton loader
```

### Classes

```python
from src.ui.feedback import SuiviProgression, EtatChargement, GestionnaireNotifications

# Progression
progress = SuiviProgression(total=100)
progress.mettre_a_jour(50)

# État chargement
etat = EtatChargement()
etat.demarrer("Chargement recettes")
etat.terminer()

# Notifications (file avec expiration)
GestionnaireNotifications.afficher("Message", "success", duree=3)
GestionnaireNotifications.rendre()  # Dans le main
```

---

## Mode Tablette (tablet/)

### Configuration

```python
from src.ui.tablet import TabletMode, get_tablet_mode, set_tablet_mode

# Modes: NORMAL, TABLET, KITCHEN
mode = get_tablet_mode()
set_tablet_mode(TabletMode.KITCHEN)
```

### Styles

```python
from src.ui.tablet import TABLET_CSS, KITCHEN_MODE_CSS, apply_tablet_mode, close_tablet_mode

apply_tablet_mode()    # Active le CSS tablette
close_tablet_mode()    # Remet en mode normal
```

### Widgets Tactiles

```python
from src.ui.tablet import tablet_button, tablet_select_grid, tablet_number_input, tablet_checklist

# Bouton large tactile
if tablet_button("Valider", icon="✓", key="btn_valider"):
    # Action
    pass

# Grille de sélection
selection = tablet_select_grid(
    options=["Entrée", "Plat", "Dessert"],
    key="select_type"
)

# Input numérique avec +/-
quantite = tablet_number_input(
    label="Quantité",
    value=4,
    min_val=1,
    max_val=20,
    key="qty"
)

# Checklist tactile
selections = tablet_checklist(
    items=["Œufs", "Lait", "Farine"],
    key="ingredients"
)
```

### Vue Cuisine

```python
from src.ui.tablet import render_kitchen_recipe_view, render_mode_selector

# Sélecteur de mode UI
render_mode_selector()

# Vue recette format cuisine (grandes étapes, navigation tactile)
render_kitchen_recipe_view(recette)
```

---

## Intégrations (integrations/)

### Google Calendar

```python
from src.ui.integrations import (
    verifier_config_google,
    render_google_calendar_config,
    render_sync_status,
    render_quick_sync_button,
    GOOGLE_SCOPES,
    REDIRECT_URI_LOCAL
)

# Vérifier la configuration
if verifier_config_google():
    render_sync_status()
    render_quick_sync_button()
else:
    render_google_calendar_config()
```

---

## Module CRUD Générique (core/)

### ConfigurationModule

Dataclass de configuration pour générer un module CRUD complet.

```python
from src.ui.core import ConfigurationModule, creer_module_ui

config = ConfigurationModule(
    name="recettes",
    title="Recettes",
    icon="🍽️",
    service=recette_service,
    display_fields=[{"key": "nom", "label": "Nom"}],
    search_fields=["nom", "description"],
    filters_config={"categorie": ["Entrée", "Plat", "Dessert"]},
    stats_config=[{"label": "Total", "value_key": "count"}],
    actions=[{"label": "Voir", "icon": "👁️", "callback": voir_recette}],
    status_field="statut",
    status_colors={"actif": "#4CAF50", "archive": "#9E9E9E"},
    items_per_page=20,
)

module = creer_module_ui(config)
module.render()  # UI complète générée automatiquement
```

### ConstructeurFormulaire

Générateur de formulaires dynamiques.

```python
from src.ui.core import ConstructeurFormulaire

builder = ConstructeurFormulaire()
builder.ajouter_texte("nom", "Nom de la recette", requis=True)
builder.ajouter_nombre("temps", "Temps (min)", min_val=5, max_val=240)
builder.ajouter_selection("categorie", "Catégorie", ["Entrée", "Plat", "Dessert"])

if builder.valider():
    donnees = builder.obtenir_donnees()
    # {"nom": "...", "temps": 30, "categorie": "Plat"}
```

---

## Bonnes Pratiques

### Import Recommandé

```python
# ✅ Import depuis le point d'entrée unifié
from src.ui import badge, carte_metrique_avancee, afficher_succes

# ✅ Import spécifique si besoin de tout un module
from src.ui.tablet import TabletMode, get_tablet_mode

# ❌ Éviter les imports profonds
from src.ui.components.atoms import badge  # Fonctionne mais moins propre
```

### Cache

Les composants avec calculs coûteux utilisent `@st.cache_data`:

- Graphiques: `ttl=300` (5 min)
- Métriques: `ttl=60` (1 min)

### Performance

Pour le chargement différé des modules, voir `src/core/lazy_loader.py`.
Chaque module métier (`src/modules/`) exporte une fonction `app()` comme point d'entrée.

---

## Imports

```python
# Import depuis le point d'entrée unifié
from src.ui import badge, carte_metrique_avancee, afficher_succes

# Import spécifique si besoin de tout un module
from src.ui.tablet import TabletMode, get_tablet_mode

# Import direct depuis sous-module
from src.ui.components import graphique_repartition_repas
from src.ui.integrations import verifier_config_google
from src.ui.core import ConfigurationModule, ModuleUIBase
```
