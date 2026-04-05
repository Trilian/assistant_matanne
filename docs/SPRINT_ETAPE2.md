# Sprint — Étape 2 : Restructuration fichiers

> **Statut** : ✅ Terminé  
> **Date** : Avril 2026 (Étape 2 de l'audit complet)

---

## Checklist

| # | Tâche | Statut | Détails |
|---|-------|--------|---------|
| 1 | Découper webhooks_telegram.py en sous-modules | ✅ | Package `src/api/routes/telegram/` créé avec 10 sous-modules |
| 2 | Réorganiser src/services/maison/ en sous-packages | ⏭️ | Reporté (complexité imports, nécessite migration progressive) |
| 3 | Réorganiser src/services/utilitaires/ en sous-packages | ⏭️ | Reporté (même raison) |
| 4 | Fusionner docs admin (3 → 1) | ✅ | `ADMIN.md` créé, 3 anciens fichiers supprimés |
| 5 | Fusionner INTER_MODULES.md + INTER_MODULES_MAP.md | ✅ | Diagramme Mermaid + tableau lecture rapide intégrés dans INTER_MODULES.md |
| 6 | Mettre à jour OWASP_AUDIT.md | ✅ | Références "Phase 2" supprimées du titre et du contenu |
| 7 | Nettoyer les références Phase dans tous les docs | ✅ | ARCHITECTURE.md, API_SCHEMAS.md, DEVELOPER_SETUP.md nettoyés |
| 8 | Standardiser le nommage paramètres API | ✅ | 27 endpoints renommés (donnees/maj) sur 10 fichiers routes |

---

## Détail des changements

### 1. Découpage webhooks_telegram.py → package telegram/

Fichier monolithique de 2206 lignes découpé en 10 sous-modules :

| Module | Contenu | ~Lignes |
|--------|---------|---------|
| `_helpers.py` | Fonctions utilitaires (normalisation, extraction, emoji, boutons) | ~130 |
| `_schemas.py` | COMMANDES_TELEGRAM, schémas Pydantic, LIBELLES_MAGASINS | ~50 |
| `_menus.py` | Menu principal, menus par module, aide | ~90 |
| `_cuisine.py` | Commandes cuisine (planning, courses, inventaire, recettes, batch) | ~400 |
| `_famille.py` | Commandes famille (jules, budget, météo, weekend, rapport) | ~250 |
| `_maison.py` | Commandes maison (tâches, jardin, énergie, rappels) | ~200 |
| `_outils.py` | Timer, note, photo frigo, aide photo | ~120 |
| `_callbacks.py` | Handlers de callbacks boutons interactifs | ~350 |
| `_dispatcher.py` | Dispatch des slash-commands | ~100 |
| `_routes.py` | Routes FastAPI (webhook + 3 POST d'envoi) | ~250 |

- `__init__.py` re-exporte `router` + fonctions pour backward-compat tests
- `webhooks_telegram.py` conservé comme shim de re-export (DEPRECATED)
- `main.py` mis à jour pour importer depuis `telegram` package

### 4. Fusion docs admin

3 fichiers fusionnés en un seul `docs/ADMIN.md` :
- `ADMIN_GUIDE.md` (130 lignes) — procédures opératoires
- `ADMIN_QUICK_REFERENCE.md` (110 lignes) — aide-mémoire
- `ADMIN_RUNBOOK.md` (500 lignes) — runbook complet 51 endpoints

Structure du fichier unifié :
1. Vue d'ensemble + pré-requis
2. Référence rapide (quick commands, feature flags, séquences)
3. Référence complète 51 endpoints (8 catégories)
4. Procédures opérationnelles
5. Procédures de diagnostic

### 5. Fusion INTER_MODULES

`INTER_MODULES_MAP.md` intégré dans `INTER_MODULES.md` :
- Diagramme Mermaid des flux ajouté
- Tableau de lecture rapide (21 bridges) ajouté
- Section "Consolidation Phase 2" supprimée
- Références croisées nettoyées

### 6-7. Nettoyage Phase références

| Fichier | Modification |
|---------|-------------|
| `OWASP_AUDIT.md` | Titre "Phase 2" → "Audit OWASP", section "Points livrés pendant cette phase" → "Points livrés" |
| `ARCHITECTURE.md` | "Consolidation Phase 6" → "Consolidation", "finitions Phase 6" neutre |
| `API_SCHEMAS.md` | "Complément Phase 6" → "Endpoints métier actifs", "frontend Phase 6" → "frontend" |
| `DEVELOPER_SETUP.md` | "Vérification rapide Phase 6" → "Vérification rapide" |
| `CHANGELOG.md` | Non touché (historique, doit rester tel quel) |

### 8. Standardisation paramètres API

Convention appliquée : `donnees` pour POST/PUT (create), `maj` pour PATCH (update).

| Fichier | Nombre endpoints | Modifications |
|---------|-----------------|---------------|
| `courses.py` | 5 | data→donnees (×3), data→maj, item→maj |
| `utilitaires.py` | 6 | patch→maj (×6) |
| `famille.py` | 4 | donnees→maj (×2), payload→maj (×2) |
| `recettes.py` | 3 | recette→donnees (×2), patch→maj |
| `planning.py` | 2 | repas→donnees, repas→maj |
| `inventaire.py` | 2 | item→donnees, item→maj |
| `batch_cooking.py` | 1 | patch→maj |
| `documents.py` | 1 | donnees→maj |
| `preferences.py` | 1 | patch→maj |
| `webhooks.py` | 2 | data→donnees, data→maj |

> **Note** : Les routes admin (`admin_*.py`), IA (`ia_*.py`, `suggestions.py`) et innovations (`innovations.py`) utilisent encore `body` ou `payload` — à standardiser dans un sprint dédié.

---

## Tâches reportées

### Services/maison et services/utilitaires en sous-packages (tâches 2-3)

Reportées car la réorganisation en sous-packages (`crud/`, `ia/`, `bridges/`) nécessite :
- Migration progressive des 43 fichiers (maison) et 16 fichiers (utilitaires)
- Mise à jour des `__init__.py` avec lazy loading
- Mise à jour de tous les imports dans routes, tests et services croisés
- Risque de régressions sur les 21+ bridges inter-modules

**Recommandation** : Planifier en sprint dédié avec tests de non-régression systématiques.
