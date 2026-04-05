# Audit Accessibilité (a11y) — Assistant Matanne

## Corrections implémentées

### 1. Lien "Aller au contenu principal"

- **Fichier**: `frontend/src/composants/disposition/coquille-app.tsx`
- **Cible**: `<main id="contenu-principal">` (déjà existant dans `contenu-principal.tsx`)
- **Comportement**: Invisible par défaut, apparaît au focus clavier (Tab)

### 2. aria-label sur les boutons icônes

| Fichier | Bouton | aria-label |
|---------|--------|------------|
| `panneau-admin-flottant.tsx` | Fermer (X) | "Fermer le panneau admin" |
| `kanban-projets.tsx` | Supprimer (Trash2) | "Supprimer le projet {nom}" |
| `onglet-artisans.tsx` | Modifier (Pencil) | "Modifier {nom}" |
| `onglet-artisans.tsx` | Supprimer (Trash2) | "Supprimer {nom}" |
| `onglet-projets.tsx` | Supprimer (Trash2) | "Supprimer le projet {nom}" |
| `onglet-entretien.tsx` | Supprimer (Trash2) x2 | "Supprimer la tâche {nom}" |

### 3. Focus visible global

- **Fichier**: `frontend/src/app/globals.css`
- **Règle**: `:focus-visible { outline: 2px solid var(--ring); outline-offset: 2px }`
- **Impact**: Tous les éléments interactifs ont un indicateur de focus clavier visible

## Déjà conforme

| Critère | État | Détails |
|---------|------|---------|
| Contraste couleurs WCAG AA | ✅ | oklch tokens light/dark avec ratios suffisants |
| Landmarks ARIA | ✅ | `<header>`, `<aside>`, `<nav aria-label>`, `<main id>` |
| Navigation mobile aria-label | ✅ | `aria-label="Navigation mobile"` |
| Sidebar navigation aria-label | ✅ | `aria-label="Navigation principale"` |
| Labels de formulaires | ✅ | `<Label htmlFor>` sur la majorité des champs |
| Boutons FAB accessibles | ✅ | Chat IA, assistant vocal, minuteur avec aria-labels |
| Polices lisibles | ✅ | Geist Sans, taille de base 16px |
| lang="fr" | ✅ | Attribut sur `<html>` |
