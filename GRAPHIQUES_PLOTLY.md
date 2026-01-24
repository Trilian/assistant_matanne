# 📊 GRAPHIQUES PLOTLY CRÉÉS - Démonstration

## Vue Globale des Visualisations

Depuis le début de cette session, nous avons créé **9+ graphiques interactifs Plotly** répartis sur 4 modules Streamlit.

---

## 1. Module SANTÉ (`sante.py`)

### Graphique #1: Calories vs Durée
```
Type: Dual-Axis Bar + Scatter
Location: Tab "Tracking"
Description: Visualise la relation entre durée de l'activité et calories brûlées

Format:
  Axe gauche (Y1): Calories brûlées (Bar chart bleu)
  Axe droit (Y2): Durée en minutes (Scatter points orange)
  Axe X: Types d'activités (course, yoga, marche, etc.)
  Hover: Calories exactes + durée exacte

Exemple:
  ┌─────────────────────────────────────┐
  │ Calories vs Durée (7 derniers jours)│
  │                                     │
  │    500 ▢▢▢ ◆ ◆ ◆                   │
  │    400 ▢▢▢ ◆ ◆                     │
  │    300 ▢▢  ◆                       │
  │   ┌────────────────────────┬──────┐│
  │   └────────────────────────┴──────┘│
  │      Course Yoga Marche Danse      │
  └─────────────────────────────────────┘
```

### Graphique #2: Énergie & Moral
```
Type: Dual Scatter Lines
Location: Tab "Tracking"
Description: Evolution de l'énergie et du moral sur la semaine

Format:
  Série 1 (Ligne bleu): Niveau énergie (1-10)
  Série 2 (Ligne vert): Niveau moral (1-10)
  Axe X: Dates (7 derniers jours)
  Hover: Date + valeur exacte + impact activité

Exemple:
  ┌──────────────────────────────────┐
  │ Énergie & Moral (Semaine)        │
  │                                  │
  │  10  ◆─────◆                     │
  │   9  │    ╱ │    ╱  ◆            │
  │   8  │   ╱  │   ╱  ╱             │
  │      └──────┴─────────            │
  │ Lun Mar Mer Jeu Ven Sam Dim      │
  └──────────────────────────────────┘
```

---

## 2. Module ACTIVITÉS (`activites_upgraded.py`)

### Graphique #3: Timeline Activités
```
Type: Timeline Plotly (px.timeline)
Location: Tab "Planning Semaine"
Description: Affiche chronologiquement les activités de la semaine

Format:
  Y-axis: Type activité (parc, musée, eau, sport, maison)
  X-axis: Dates (dimanche → dimanche)
  Couleur: Par type activité
  Hover: Titre + date + durée

Exemple:
  ┌──────────────────────────────────────┐
  │ Timeline Activités (Semaine)        │
  │ Sport    ─────────────────────       │
  │ Parc                    ────────     │
  │ Musée        ───────                 │
  │ Eau                         ────     │
  │ ┌──────────────────────────────────┐ │
  │ │ Lun   Mar   Mer   Jeu   Ven      │ │
  └──────────────────────────────────────┘
```

### Graphique #4: Budget Activités par Type
```
Type: Bar Chart (px.bar)
Location: Tab "Budget"
Description: Dépenses totales par type activité

Format:
  X-axis: Types activité
  Y-axis: Montant (€)
  Couleur: Gradient Viridis (bleu → jaune)
  Hover: Type + montant exact + % du total

Exemple:
  ┌──────────────────────────────────────┐
  │ Budget par Type (7 jours)           │
  │                                      │
  │ 100  ┌──────┐                        │
  │  80  │      │    ┌──────┐            │
  │  60  │      │    │      │ ┌─────┐   │
  │  40  │      │    │      │ │     │   │
  │  20  │      │    │      │ │     │   │
  │      └──────┘    └──────┘ └─────┘   │
  │      Sport    Parc  Musée  Eau      │
  └──────────────────────────────────────┘
```

### Graphique #5: Timeline Coûts (Estimé vs Réel)
```
Type: Scatter (dual traces)
Location: Tab "Budget"
Description: Évolution des coûts estimés vs réels sur 30 jours

Format:
  X-axis: Dates (30 derniers jours)
  Y-axis: Montant (€)
  Trace 1: Points bleus = Coûts estimés
  Trace 2: Points rouges = Coûts réels
  Hover: Date + montant estimé + montant réel + écart

Exemple:
  ┌─────────────────────────────────────┐
  │ Coûts Estimé vs Réel (30j)         │
  │                                     │
  │ 150  ◆ (est)    ◆ ◆                 │
  │ 120  ◇ (réel)   ◇  ◇ ◇ ◇            │
  │ 100              ◇      ◇           │
  │  80                      ◆          │
  │      ┌─────────────────────┐        │
  │      │ 1j  10j  20j  30j   │        │
  └─────────────────────────────────────┘
```

---

## 3. Module SHOPPING (`shopping_upgraded.py`)

### Graphique #6: Budget par Catégorie
```
Type: Bar Chart (px.bar)
Location: Tab "Budget"
Description: Répartition des dépenses par catégorie d'articles

Format:
  X-axis: Catégories (épicerie, fruits, hygiène, jouets, etc.)
  Y-axis: Montant (€)
  Couleur: Gradient colorisé (bleu → rouge)
  Hover: Catégorie + montant + % du budget

Exemple:
  ┌─────────────────────────────────────┐
  │ Budget Shopping (7 jours)          │
  │                                     │
  │ 120 ┌──────────┐                    │
  │ 100 │          │     ┌──────┐      │
  │  80 │          │     │      │      │
  │  60 │          │     │      │ ┌──┐ │
  │  40 └──────────┘     │      │ │  │ │
  │  20                  └──────┘ └──┘ │
  │      Épicerie Jouets Hygiène Fruits│
  └─────────────────────────────────────┘
```

### Graphique #7: Estimé vs Réel (Shopping)
```
Type: Bar Dual (Grouped)
Location: Tab "Analytics"
Description: Compare les coûts estimés vs coûts réels par catégorie

Format:
  X-axis: Catégories
  Y-axis: Montant (€)
  Barre 1: Estimé (bleu clair)
  Barre 2: Réel (rose clair)
  Hover: Catégorie + estimé + réel + économies

Exemple:
  ┌─────────────────────────────────────┐
  │ Estimé vs Réel (30j)               │
  │                                     │
  │ 100 ▢▢ ▢▢ ▢▢                        │
  │  80 ▢▢ ▢▢ ▢▢ ▢▢                     │
  │  60 ▢▢ ▢▢ ▢▢ ▢▢ ▢▢                  │
  │  40 ▢▢ ▢▢ ▢▢ ▢▢ ▢▢ ▢▢               │
  │      ┌─────────────────┐            │
  │      │ Est  Réel       │            │
  └─────────────────────────────────────┘
```

---

## 4. Module ACCUEIL (`accueil_upgraded.py`) - DASHBOARD HUB

### Graphique #8: Timeline Activités Semaine
```
Type: Timeline (px.timeline)
Location: Section "Activités cette semaine"
Description: Vue chronologique des activités planifiées

Format:
  Y-axis: Type activité
  X-axis: Jours semaine
  Couleur: Par type
  Hover: Titre + date + détails

Même format que Graphique #3
```

### Graphique #9: Budget - Répartition (Pie)
```
Type: Pie Chart (px.pie)
Location: Section "Budget cette semaine"
Description: Distribution du budget par catégorie

Format:
  Secteurs: 1 par catégorie
  Taille: Proportionnelle au montant
  Étiquettes: Catégorie + % + montant
  Hover: Catégorie + montant exact + %

Exemple:
  ┌─────────────────────────────────────┐
  │ Budget Semaine (Répartition)       │
  │                                     │
  │           ╱────╲                    │
  │        ╱─────────╲                  │
  │      ╱ Jules 25% ╲                 │
  │     │  Activités  │  Nous          │
  │     │    40%  45% │                │
  │      ╲           ╱                  │
  │        ╲───────╱ Santé 10%          │
  │           ╲────╱                    │
  └─────────────────────────────────────┘
```

### Graphique #10: Budget - Courbe Cumulative
```
Type: Line Chart (px.line)
Location: Section "Budget ce mois"
Description: Évolution cumulative des dépenses du mois

Format:
  X-axis: Dates (30 jours du mois)
  Y-axis: Montant cumulé (€)
  Ligne: Courbe montante
  Markers: Points quotidiens
  Hover: Date + cumul exact

Exemple:
  ┌─────────────────────────────────────┐
  │ Cumul Dépenses Mois               │
  │                                     │
  │1500│                         ╱     │
  │1200│                    ╱╱╱        │
  │ 900│                ╱╱            │
  │ 600│            ╱╱                │
  │ 300│        ╱╱                    │
  │   0└───────────────────────────────│
  │     1j  10j  20j  30j              │
  └─────────────────────────────────────┘
```

---

## 5. Module INTÉGRATION CUISINE/COURSES

### Pas de graphiques natifs (utilise autres modules)
- Affiche les graphiques d'autres modules via `@st.cache_data`
- Permet navigation fluide vers sante.py, shopping.py, activites.py

---

## 📊 TABLEAU RÉCAPITULATIF

| # | Graphique | Module | Type | Données | Interactif |
|---|-----------|--------|------|---------|-----------|
| 1 | Calories vs Durée | Santé | Dual-Axis Bar+Scatter | 7 jours | ✅ |
| 2 | Énergie & Moral | Santé | Dual Scatter | 7 jours | ✅ |
| 3 | Timeline Activités | Activités | Timeline | Cette semaine | ✅ |
| 4 | Budget par Type | Activités | Bar | 7 jours | ✅ |
| 5 | Timeline Coûts | Activités | Scatter Dual | 30 jours | ✅ |
| 6 | Budget Shopping | Shopping | Bar | 7-30 jours | ✅ |
| 7 | Estimé vs Réel | Shopping | Bar Dual | 30 jours | ✅ |
| 8 | Timeline Activités | Accueil | Timeline | Cette semaine | ✅ |
| 9 | Budget Pie | Accueil | Pie | 7 jours | ✅ |
| 10 | Cumul Dépenses | Accueil | Line | 30 jours | ✅ |

**Total**: 10 graphiques Plotly interactifs

---

## 🎨 Styles & Couleurs Plotly

### Palettes Utilisées
```python
# Santé: Bleu (énergie), Vert (moral), Orange (calories)
color_continuous_scale="Blues"  # Ou "RdYlGn" pour énergie/moral

# Activités & Shopping: Viridis (bleu → jaune)
color_continuous_scale="Viridis"

# Accueil: Défaut Plotly (couleurs automatiques)
```

### Configurations Communes
```python
# Tous les graphiques incluent:
hovermode="x unified"  # Hover synchronisé
height=400             # Hauteur standard
use_container_width=True  # Adapte largeur

# Tooltips personnalisées:
hover_data={
    "Catégorie": True,
    "Montant": ":.2f",  # Format €
    "Date": "|%d %b"    # Format date
}
```

---

## 🔧 Code Exemple - Créer Un Graphique

```python
import plotly.express as px
import pandas as pd

# Exemple: Budget par Catégorie
df_budget = pd.DataFrame([
    {"Catégorie": "Jules", "Montant": 150},
    {"Catégorie": "Activités", "Montant": 200},
    {"Catégorie": "Nous", "Montant": 300}
])

fig = px.bar(
    df_budget,
    x="Catégorie",
    y="Montant",
    color="Montant",
    color_continuous_scale="Viridis",
    title="Budget par Catégorie",
    hover_data={"Montant": ":.2f"}
)

fig.update_layout(
    height=400,
    hovermode="x unified",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)
```

---

## 📱 Responsivité

Tous les graphiques Plotly sont:
- ✅ Responsive (s'adaptent à la largeur)
- ✅ Interactifs (zoom, pan, hover)
- ✅ Exportables (save as PNG via UI)
- ✅ Mobile-friendly (redimensionnables)

---

## 🎯 Cas d'Usage

### Pour Jules (Parents)
- 📊 Graphiques santé → Tracker bien-être Jules
- 📅 Timeline activités → Planifier semaine
- 💰 Budget pie → Voir dépenses Jules vs famille

### Pour Nous (Parents)
- ⚡ Énergie/moral → Tracker santé parentale
- 💪 Calories/durée → Suivre fitness
- 💸 Budget timeline → Analyser économies

### Pour Gestion (Admin)
- 📈 Cumul dépenses → Budget mensuel
- 📊 Estimé vs réel → Précision estimation
- 🎯 Progression objectives → Atteinte goals

---

## 🚀 Améliorations Futures

Possibles extensions pour les graphiques:
1. **Comparaison mois/mois** (Line chart historique)
2. **Heatmap activités** (Calendrier chaleur)
3. **Scatter 3D** (Calories + Durée + Énergie)
4. **Sunburst** (Budget hiérarchique)
5. **Sankey** (Flux budget catégories)
6. **Gauge** (Progrès objectifs en tempo réel)

---

## ✅ Validation

Tous les graphiques ont été:
- ✅ Testés localement (visual check)
- ✅ Codés avec try/except
- ✅ Configurés avec hover informatif
- ✅ Stylisés pour UX optimal
- ✅ Documentés inline

---

**Status**: 🟢 **TOUS LES GRAPHIQUES PRÊTS POUR PRODUCTION**
