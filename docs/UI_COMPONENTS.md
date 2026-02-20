# Référence des Composants UI

Guide complet des composants UI réutilisables de l'application.
Tous les noms suivent la convention française : `afficher_*`, `obtenir_*`, `definir_*`.

## Architecture

```
src/ui/
├── __init__.py          # Point d'entrée unifié (~90 exports)
├── components/          # Composants UI réutilisables (27 exports)
│   ├── atoms.py         # Badge, état vide, carte métrique, etc.
│   ├── alertes.py       # Alertes stock
│   ├── charts.py        # Graphiques Plotly
│   ├── data.py          # Pagination, tableaux, export
│   ├── dynamic.py       # Modale
│   ├── forms.py         # Formulaires, recherche, filtres
│   ├── layouts.py       # Grilles, cartes
│   ├── metrics.py       # Cartes métriques avancées
│   └── system.py        # Santé système, timeline
├── feedback/            # Notifications, spinners (10 exports)
│   ├── spinners.py      # Indicateurs chargement
│   ├── progress.py      # Suivi progression
│   └── toasts.py        # Notifications temporaires
├── layout/              # Header, sidebar, footer (6 exports, app-level)
│   ├── header.py        # En-tête application
│   ├── sidebar.py       # Barre latérale + menu
│   ├── footer.py        # Pied de page
│   ├── styles.py        # Injection CSS
│   └── init.py          # Initialisation app
├── tablet/              # Mode tablette/cuisine (13 exports)
│   ├── config.py        # ModeTablette enum
│   ├── styles.py        # CSS tablette
│   ├── widgets.py       # Boutons tactiles
│   └── kitchen.py       # Vue recette cuisine
├── views/               # Vues extraites des services (21 exports)
│   ├── authentification.py  # Connexion, profil, rôles
│   ├── historique.py        # Timeline activité
│   ├── import_recettes.py   # Import URL/PDF
│   ├── jeux.py              # Notifications jeux/paris
│   ├── meteo.py             # Météo jardin
│   ├── notifications.py     # Push notifications
│   ├── pwa.py               # Meta tags PWA
│   ├── sauvegarde.py        # Backup/restauration
│   └── synchronisation.py   # Présence, frappe, PWA install
└── integrations/        # Intégrations externes (6 exports)
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

### Notifications (via `GestionnaireNotifications`)

Les notifications passent désormais par `GestionnaireNotifications` dans `src/ui/feedback/toasts.py`.
Utilise `st.toast()` avec déduplication automatique (fenêtre de 3s).

```python
from src.ui.feedback.toasts import GestionnaireNotifications

GestionnaireNotifications.afficher("Sauvegardé", "success")   # st.toast avec ✅
GestionnaireNotifications.afficher("Erreur!", "error")          # st.toast avec ❌
GestionnaireNotifications.afficher("Attention", "warning")      # st.toast avec ⚠️
GestionnaireNotifications.afficher("Info", "info")              # st.toast avec ℹ️
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

---

## Layouts (layouts.py)

### `disposition_grille(items, colonnes_par_ligne, rendu_carte, cle)`

Grille responsive.

```python
from src.ui.components import disposition_grille

def rendu_recette(recette, key):
    st.write(recette["nom"])

disposition_grille(recettes, colonnes_par_ligne=3, rendu_carte=rendu_recette)
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
from src.ui.tablet import ModeTablette, obtenir_mode_tablette, definir_mode_tablette

# Modes: NORMAL, TABLETTE, CUISINE
mode = obtenir_mode_tablette()
definir_mode_tablette(ModeTablette.CUISINE)
```

### Styles

```python
from src.ui.tablet import CSS_TABLETTE, CSS_MODE_CUISINE, appliquer_mode_tablette, fermer_mode_tablette

appliquer_mode_tablette()    # Active le CSS tablette
fermer_mode_tablette()       # Remet en mode normal
```

### Widgets Tactiles

```python
from src.ui.tablet import bouton_tablette, grille_selection_tablette, saisie_nombre_tablette, liste_cases_tablette

# Bouton large tactile
if bouton_tablette("Valider", icon="✓", key="btn_valider"):
    # Action
    pass

# Grille de sélection (3 colonnes par défaut)
selection = grille_selection_tablette(
    options=[{"label": "Entrée"}, {"label": "Plat"}, {"label": "Dessert"}],
    key="select_type"
)

# Input numérique avec boutons +/-
quantite = saisie_nombre_tablette(
    label="Quantité",
    key="qty",
    min_value=1,
    max_value=20,
    default=4
)

# Checklist tactile
selections = liste_cases_tablette(
    items=["Œufs", "Lait", "Farine"],
    key="ingredients"
)
```

### Vue Cuisine

```python
from src.ui.tablet import afficher_vue_recette_cuisine, afficher_selecteur_mode

# Sélecteur de mode UI (dans la sidebar)
afficher_selecteur_mode()

# Vue recette format cuisine (step-by-step, navigation tactile)
afficher_vue_recette_cuisine(recette, cle="kitchen_recipe")
```

---

## Intégrations (integrations/)

### Google Calendar

```python
from src.ui.integrations import (
    verifier_config_google,
    afficher_config_google_calendar,
    afficher_statut_sync_google,
    afficher_bouton_sync_rapide,
    GOOGLE_SCOPES,
    REDIRECT_URI_LOCAL
)

# Vérifier la configuration
if verifier_config_google():
    afficher_statut_sync_google()
    afficher_bouton_sync_rapide()
else:
    afficher_config_google_calendar()
```

---

## Vues Extraites (views/)

Fonctions d'affichage extraites des services pour respecter la séparation UI/logique.

### Authentification (authentification.py)

```python
from src.ui.views import (
    afficher_formulaire_connexion,
    afficher_menu_utilisateur,
    afficher_parametres_profil,
    require_authenticated,
    require_role,
)

# Formulaire de connexion
afficher_formulaire_connexion(rediriger_apres_succes=True)

# Menu utilisateur dans la sidebar
afficher_menu_utilisateur()

# Page paramètres profil
afficher_parametres_profil()

# Décorateurs de protection
@require_authenticated
def page_protegee():
    st.write("Contenu protégé")

@require_role(Role.ADMIN)
def page_admin():
    st.write("Admin uniquement")
```

### Historique (historique.py)

```python
from src.ui.views import afficher_timeline_activite, afficher_activite_utilisateur, afficher_statistiques_activite

# Timeline d'activité récente (10 dernières par défaut)
afficher_timeline_activite(limit=10)

# Activité d'un utilisateur spécifique
afficher_activite_utilisateur(user_id="...")

# Statistiques d'activité globales
afficher_statistiques_activite()
```

### Import Recettes (import_recettes.py)

```python
from src.ui.views import afficher_import_recette

# Interface d'import URL/PDF
afficher_import_recette()
```

### Notifications Push (notifications.py)

```python
from src.ui.views import afficher_demande_permission_push, afficher_preferences_notification

# Demander permission push au navigateur
afficher_demande_permission_push()

# Paramètres de notifications
afficher_preferences_notification()
```

### Météo Jardin (meteo.py)

```python
from src.ui.views import afficher_meteo_jardin

# Alertes météo pour le jardin
afficher_meteo_jardin()
```

### Sauvegarde (sauvegarde.py)

```python
from src.ui.views import afficher_sauvegarde

# Interface backup/restauration complète
afficher_sauvegarde()
```

### Synchronisation (synchronisation.py)

```python
from src.ui.views import (
    afficher_indicateur_presence,
    afficher_indicateur_frappe,
    afficher_statut_synchronisation,
    afficher_invite_installation_pwa,
)

# Utilisateurs connectés en temps réel
afficher_indicateur_presence()

# Indicateurs de frappe
afficher_indicateur_frappe()

# Statut sync
afficher_statut_synchronisation()

# Bouton install PWA
afficher_invite_installation_pwa()
```

### Jeux (jeux.py)

```python
from src.ui.views import afficher_badge_notifications_jeux, afficher_notification_jeux, afficher_liste_notifications_jeux

# Badge compteur non-lues
afficher_badge_notifications_jeux(service=None)

# Notification individuelle
afficher_notification_jeux(notification)

# Liste paginée
afficher_liste_notifications_jeux(service=None, limite=10, type_jeu=None)
```

### PWA (pwa.py)

```python
from src.ui.views import injecter_meta_pwa

# Appelé dans app.py après injecter_css()
injecter_meta_pwa()
```

---

## Bonnes Pratiques

### Import Recommandé

```python
# ✅ Import depuis le point d'entrée unifié
from src.ui import badge, carte_metrique_avancee, afficher_succes, etat_vide

# ✅ Import spécifique par sous-package
from src.ui.tablet import ModeTablette, obtenir_mode_tablette
from src.ui.views import afficher_timeline_activite
from src.ui.integrations import verifier_config_google

# ✅ Import dans _common.py des modules métier
from src.ui.components.atoms import etat_vide  # re-exporté via _common.py

# ❌ Éviter les imports profonds dans le code métier
from src.ui.components.atoms import badge  # Préférer from src.ui import badge
```

### Motif `etat_vide`

Utiliser `etat_vide()` au lieu de `st.info("Aucun ...")` pour les états vides :

```python
from src.ui import etat_vide

# ✅ Composant unifié
etat_vide("Aucune recette trouvée", "🍽️", "Ajoutez votre première recette")

# ❌ Ancien style
st.info("Aucune recette trouvée")
```

### Cache

Les composants avec calculs coûteux utilisent `@st.cache_data`:

- Graphiques: `ttl=300` (5 min)
- Métriques: `ttl=60` (1 min)

### Performance

Pour le chargement différé des modules, voir `src/core/lazy_loader.py`.
Chaque module métier (`src/modules/`) exporte une fonction `app()` comme point d'entrée.

### Nommage

- Fonctions d'affichage : `afficher_*()`
- Fonctions d'obtention : `obtenir_*()`
- Fonctions de définition : `definir_*()`
- Classes : `NomEnFrancais` (PascalCase)
- Constantes : `NOM_EN_MAJUSCULES`

---

## Imports Rapides

```python
# Point d'entrée unifié (~90 exports)
from src.ui import badge, carte_metrique_avancee, afficher_succes

# Sous-packages spécifiques
from src.ui.components import graphique_repartition_repas
from src.ui.feedback import spinner_intelligent, SuiviProgression
from src.ui.tablet import ModeTablette, bouton_tablette
from src.ui.views import afficher_sauvegarde, afficher_timeline_activite
from src.ui.integrations import verifier_config_google

# Layout (réservé à app.py)
from src.ui.layout import afficher_header, afficher_sidebar, injecter_css
```
