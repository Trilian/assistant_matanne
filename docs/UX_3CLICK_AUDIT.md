# Audit UX — Règle des 3 clics

> Date : Juillet 2025
> Objectif : Vérifier que les 10 parcours utilisateur les plus fréquents sont accessibles en ≤ 3 clics depuis le tableau de bord.

## Résultat global : ✅ 10/10 parcours conformes

**Maximum observé : 2 clics** — aucun parcours ne dépasse 2 clics.
**60 % des parcours** sont accessibles en **1 seul clic** grâce aux actions rapides et métriques du dashboard.

## Tableau de synthèse

| # | Parcours | Chemin optimal | Clics | OK ? | Dashboard ? |
|---|----------|---------------|-------|------|-------------|
| 1 | Créer une recette | Action rapide « Ajouter recette » | 1 | ✅ | ✅ Oui |
| 2 | Voir le planning semaine | Métrique « Repas aujourd'hui » → `/cuisine/planning` | 1 | ✅ | ✅ Oui |
| 3 | Créer une liste de courses | Action rapide « Ajouter course » | 1 | ✅ | ✅ Oui |
| 4 | Vérifier les alertes inventaire | Métrique « Articles à acheter » → `/cuisine/courses` | 1 | ✅ | ✅ Oui |
| 5 | Consulter les jalons de Jules | Sidebar Famille → Jules | 2 | ✅ | ❌ Non |
| 6 | Ajouter une activité famille | Sidebar Famille → Activités | 2 | ✅ | ❌ Non |
| 7 | Créer une tâche entretien | Action rapide « Nouvelle tâche » | 1 | ✅ | ✅ Oui |
| 8 | Placer un pari sportif | Sidebar Jeux → Paris | 2 | ✅ | ❌ Non |
| 9 | Utiliser le chat IA | FAB Chat IA (mini-chat flottant) | 1 | ✅ | ✅ FAB |
| 10 | Modifier les paramètres | Avatar header → Paramètres | 2 | ✅ | ✅ Header |

## Détail des parcours

### 1. Créer une recette (1 clic)
**Dashboard** → widget « Actions rapides » → bouton « Ajouter recette » → `/cuisine/recettes`
Alternative : Sidebar → Cuisine → Recettes (2 clics)

### 2. Voir le planning semaine (1 clic)
**Dashboard** → carte métrique « Repas aujourd'hui » → `/cuisine/planning`
Alternative : Sidebar → Cuisine → Ma Semaine (2 clics)

### 3. Créer une liste de courses (1 clic)
**Dashboard** → widget « Actions rapides » → bouton « Ajouter course » → `/cuisine/courses`

### 4. Vérifier les alertes inventaire (1 clic)
**Dashboard** → carte métrique « Articles à acheter » → `/cuisine/courses`
Alternative : Sidebar → Cuisine → Frigo & Stock (2 clics)

### 5. Consulter les jalons de Jules (2 clics)
Sidebar → Famille (déplier sous-menu) → Jules → `/famille/jules`
Pas de raccourci dashboard direct.

### 6. Ajouter une activité famille (2 clics)
Sidebar → Famille (déplier sous-menu) → Activités → `/famille/activites`
Pas de raccourci dashboard direct.

### 7. Créer une tâche entretien (1 clic)
**Dashboard** → widget « Actions rapides » → bouton « Nouvelle tâche » → `/maison/entretien`
Métrique « Alertes entretien » aussi disponible en 1 clic.

### 8. Placer un pari sportif (2 clics)
Sidebar → Jeux (déplier sous-menu) → Paris → `/jeux/paris`
Fonctionnalité périphérique, 2 clics largement acceptable.

### 9. Utiliser le chat IA (1 clic)
**FAB (bouton flottant)** → ouverture du mini-chat en popover
Disponible depuis n'importe quelle page. Version complète : FAB → « Ouvrir » (2 clics).

### 10. Modifier les paramètres (2 clics)
Avatar (header) → menu déroulant → « Paramètres » → `/parametres`
Pattern standard des applications web modernes.

## Points d'accélération du dashboard

Le tableau de bord offre 3 types d'accès rapide :
- **Actions rapides** (widget drag-and-drop) : Ajouter recette, Ajouter course, Nouvelle tâche
- **Cartes métriques** : Repas aujourd'hui, Articles à acheter, Alertes entretien (liens cliquables)
- **FAB Chat IA** : Bouton flottant omniprésent

## Recommandations mineures

Les parcours 5, 6 et 8 (Jules, activités, paris) atteignent 2 clics — parfaitement conforme.
Si souhaité, un widget « Jules » ou « Activités famille » pourrait être ajouté au dashboard pour passer à 1 clic, mais ce n'est pas prioritaire.
