# Scoring PNNS, Workflow Batch Cooking, Adaptation Jules

> Référence technique pour les trois sujets les plus spécifiques du module Cuisine.

---

## 1. Scoring PNNS4 (`src/services/planning/nutrition.py`)

### Principe général

Chaque repas planifié reçoit un **score 0–100** calculé selon les recommandations PNNS4 (Programme National Nutrition Santé, 4ème édition). Ce score est stocké dans `repas.score_equilibre` et les alertes texte dans `repas.alertes_equilibre`.

### Règles par type de repas

| Type | Composants évalués | Points par composant |
|------|--------------------|----------------------|
| **Déjeuner** | Légumes + Féculents + Protéines + Laitage + Fruit | 20 pts × 5 = 100 |
| **Dîner** | Légumes + Féculents + Protéines + Laitage | 25 pts × 4 = 100 |
| **Goûter** | Laitage + Fruit + Gâteau sain | 33 pts × 3 ≈ 100 |
| **Petit-déjeuner** | Non évalué | `score = None` |

### Détection des composants

Le service détecte chaque composant en cascade :

1. **Champ DB explicite** (`repas.legumes`, `repas.feculents`, `repas.laitage`, etc.)
2. **FK recette liée** (`repas.legumes_recette_id`, `repas.feculents_recette_id`, etc.)
3. **Mot-clé dans le nom du plat** (heuristique sur `repas.notes` / `recette.nom`)
4. **Catégorie nutritionnelle de la recette** (`recette.categorie_nutritionnelle`)

Exemple : un plat intitulé « Gratin dauphinois » déclenche automatiquement `a_feculents=True` (féculents) et `a_laitage=True` (laitage implicite).

### Distribution protéines semaine

Cibles PNNS hebdomadaires contrôlées via `analyser_distribution_proteines_semaine()` :

| Protéine | Minimum | Maximum | Idéal |
|----------|---------|---------|-------|
| Poisson (dont 1 gras) | 2x | — | 3x |
| Viande rouge | 0x | 3x | 2x |
| Volaille | 0x | — | — |
| Œufs | 0x | 4x | 3x |
| Légumineuses | 3x | — | 3x |

### Niveaux de score

- **Vert** : score ≥ 80
- **Orange** : score 50–79
- **Rouge** : score < 50

### Cas spéciaux

- **Restes** (`est_reste=True`) : légumes et féculents proviennent des champs DB remplis par le générateur IA (fallbacks « Légumes de saison » / « Riz vapeur »). La protéine est vérifiée explicitement via heuristique ou `proteine_accompagnement`.
- **Légumineuses** : comptent à la fois comme féculent ET comme protéine quand c'est le plat principal (ex : lentilles corail).

---

## 2. Workflow Batch Cooking (`src/api/routes/batch_cooking.py`, `src/services/cuisine/`)

### Concept

Le batch cooking est une session de cuisine préparatoire (généralement le dimanche) qui précuisine les composants de la semaine en avance.

### Flux complet

```
Planning semaine (validé)
        │
        ▼
POST /api/v1/batch-cooking/generer-depuis-planning
        │  → Analyse les repas de la semaine
        │  → Identifie les recettes compatible_batch=True
        │  → Regroupe les préparations communes
        ▼
Session Batch (SessionBatch en DB)
        │  - semaine_debut / semaine_fin
        │  - durée estimée (minutes)
        │  - liste d'EtapesBatch ordonnées
        ▼
GET /api/v1/batch-cooking/{session_id}
        │  → Rendu de la session avec étapes détaillées
        ▼
Préparations réalisées → marquées "prêtes" dans RepasBatch
```

### Suggestions intelligentes

`GET /api/v1/batch-cooking/intelligent` — appelle `proposer_batch_cooking_intelligent()` via Mistral :
- Analyse l'historique des repas de la famille
- Suggère les meilleures combinaisons batch (ex : cuire riz + légôtés + sauce bolognaise le même jour)
- Optimise le temps de cuisson simultané (four + plaques)
- Respecte les contraintes équipement (robot, mijoteuse, etc.)

### Modèles DB impliqués

- `SessionBatch` — session globale (date, durée, statut)
- `EtapeBatchCooking` — étape chronologique (quel plat, quel équipement, durée)
- `RepasBatch` — plat préparé en avance lié à un repas planifié
- `VersionRecette` avec `type_version="batch"` — recette adaptée pour la cuisson en grande quantité

### Champ `compatible_batch` sur `Recette`

Les recettes marquées `compatible_batch=True` sont prioritaires dans la génération de sessions. Ce champ est positionné automatiquement par l'IA lors de l'import (si la recette se prête à la cuisson en avance : ragoûts, sauces, céréales, légumineuses, etc.).

---

## 3. Adaptation Jules (`src/services/famille/version_recette_jules.py`)

### Principe

Jules (fils de la famille) mange les mêmes repas que la famille mais dans une **version adaptée** : sans sel ajouté, sans alcool, sans morceaux durs, portions enfant. L'adaptation est générée via Mistral et stockée comme `VersionRecette` avec `type_version="bebe"`.

### Flux de génération

```
Recette originale (Recette)
        │
        ▼
POST /api/v1/recettes/{id}/adapter-jules
        │  → Calcul de la tranche d'âge Jules (age_mois → recommandations_age.json)
        │  → Construction du prompt Mistral avec restrictions
        │  → Génération de la version adaptée
        ▼
VersionRecette (type_version="bebe", recette_parent_id=...)
        │  - instructions adaptées
        │  - ingrédients modifiés
        │  - portions Jules
```

### Données de référence

Le fichier `data/reference/recommandations_age.json` définit les tranches d'âge avec :
- Portions recommandées par aliment
- Aliments interdits (ex : miel < 12 mois, sel < 1 an)
- Aliments limités (ex : poisson fumé, charcuterie)
- Textures recommandées selon l'âge

### Règles invariantes (indépendantes de l'âge)

| Règle | Motif |
|-------|-------|
| **Pas de sel ajouté** | Reins immatures |
| **Pas d'alcool** (y compris en cuisson) | Toxique |
| **Pas de viande/poisson/œuf crus** | Risque bactérien |
| **Pas de lait cru** | Risque bactérien |
| **Morceaux adaptés** | Risque d'étouffement |

### Gestion de la liste d'exclusions configurée

L'utilisateur peut spécifier des aliments que Jules ne mange pas (préférences, allergies) via les préférences famille. Ces exclusions sont transmises au prompt Mistral pour substitution automatique.

### Champ `adaptation_auto` sur `Repas`

Quand `Repas.adaptation_auto=True` (défaut), la version Jules du repas est générée automatiquement lors de la planification IA. Quand `False`, la version Jules est saisie manuellement dans les champs `plat_jules` / `notes_jules`.

### Affichage dans le planning

- **Colonne "Jules"** dans la grille planning : affiche `plat_jules` (texte libre) ou le nom de la `VersionRecette` liée
- Les champs Jules (`dessert_jules`, `dessert_jules_recette_id`) permettent un dessert différent pour Jules (ex : compote sans sucre vs yaourt adulte)
