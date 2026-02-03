# 🧹 NETTOYAGE DOCUMENTATION - Plan d'Action

**Date**: Février 3, 2026
**Objectif**: Nettoyer les fichiers doc obsolètes et redondants

---

## 📋 FICHIERS OBSOLÈTES À SUPPRIMER

Ces fichiers sont des **planning/brouillons** de la PHASE 1 (avant les phases 4-5):

### 🔴 À SUPPRIMER (contenu complètement obsolète)

```
❌ PHASE_1_WEEKLY_PLAN.md
   Raison: Planning hebdomadaire initial (semaines 1-8)
   Status: Complètement obsolète (toutes les phases réalisées en 1h!)

❌ PHASE_1_COMPLETION_REPORT.md
   Raison: Rapport initial PHASE 1 uniquement
   Status: Superflue (SESSION_SUMMARY_PHASE_1_5.md est le vrai résumé)

❌ PHASE_1_IMPLEMENTATION_GUIDE.md
   Raison: Guide de PHASE 1 seule
   Status: Obsolète (phases 2-5 aussi complétées)

❌ ACTION_PHASE_1_IMMEDIATEMENT.md
   Raison: Actions immédiates pour PHASE 1
   Status: Complètement terminées (depuis hier!)

❌ PLAN_ACTION_FINAL.md
   Raison: Planning initial des phases 1-5
   Status: Obsolète (phases réalisées différemment que prévu)

❌ MASTER_DASHBOARD.md
   Raison: Dashboard initial
   Status: Remplacé par DASHBOARD_PROGRESS.md

❌ INDEX_NAVIGATION.md
   Raison: Guide de navigation de la doc
   Status: Obsolète (structure doc a changé)

❌ QUICK_START.md
   Raison: Quick start pour commencer les tests
   Status: Obsolète (tests déjà créés et validés)

❌ GUIDE_AMELIORER_TEMPLATES.md
   Raison: Guide de templates
   Status: N/A (templates tests déjà crées)

❌ COVERAGE_REPORTS_INDEX.md
   Raison: Index des rapports de couverture
   Status: Obsolète (structure modifiée)
```

### 🟡 À ARCHIVER (utile pour historique, mais non-critique)

```
📦 COVERAGE_REPORT.md
   Raison: Rapport de base initial (29.37%)
   Décision: Archiver dans docs/archived/ si utile pour historique

📦 COVERAGE_EXECUTIVE_SUMMARY.md
   Raison: Résumé initial de couverture
   Décision: Archiver dans docs/archived/

📦 TEST_COVERAGE_CHECKLIST.md
   Raison: Checklist initiale des phases
   Décision: Archiver (phases sont réalisées)

📦 PHASE_2_PART1_REPORT.md
   Raison: Rapport partial PHASE 2
   Décision: Archiver (superseded par SESSION_SUMMARY)

📦 PHASE_2_PART2_REPORT.md
   Raison: Rapport partial PHASE 2
   Décision: Archiver (superseded par SESSION_SUMMARY)

📦 PHASE_2_PART3_REPORT.md
   Raison: Rapport partial PHASE 2
   Décision: Archiver (superseded par SESSION_SUMMARY)

📦 SUMMARY_LIVRAISON.md
   Raison: Résumé de livraison intermédiaire
   Décision: Archiver
```

### ✅ À GARDER (actuellement utiles)

```
✓ DASHBOARD_PROGRESS.md          → Vue d'ensemble des phases 1-5 ✓
✓ SESSION_SUMMARY_PHASE_1_5.md   → Résumé complet session ✓
✓ README_PHASES_1_5.md           → Guide complet phases 1-5 ✓
✓ ANALYSE_COUVERTURE_REELLE.md   → NOUVEAU - Analyse 55% vs 80% ✓
✓ README.md                      → Documentation projet ✓
✓ ROADMAP.md                     → Feuille de route projet ✓
```

---

## 🎯 PLAN D'EXÉCUTION NETTOYAGE

### Étape 1: Créer dossier archive

```bash
mkdir docs/archived
```

### Étape 2: Archiver les fichiers non-critiques (14 fichiers)

```bash
mv COVERAGE_REPORT.md docs/archived/
mv COVERAGE_EXECUTIVE_SUMMARY.md docs/archived/
mv TEST_COVERAGE_CHECKLIST.md docs/archived/
mv PHASE_2_PART1_REPORT.md docs/archived/
mv PHASE_2_PART2_REPORT.md docs/archived/
mv PHASE_2_PART3_REPORT.md docs/archived/
mv SUMMARY_LIVRAISON.md docs/archived/
```

### Étape 3: Supprimer complètement (10 fichiers)

```bash
rm -f PHASE_1_WEEKLY_PLAN.md
rm -f PHASE_1_COMPLETION_REPORT.md
rm -f PHASE_1_IMPLEMENTATION_GUIDE.md
rm -f ACTION_PHASE_1_IMMEDIATEMENT.md
rm -f PLAN_ACTION_FINAL.md
rm -f MASTER_DASHBOARD.md
rm -f INDEX_NAVIGATION.md
rm -f QUICK_START.md
rm -f GUIDE_AMELIORER_TEMPLATES.md
rm -f COVERAGE_REPORTS_INDEX.md
```

### Étape 4: Vérifier docs/ reste clean

```bash
ls -la docs/
```

### Étape 5: Commit

```bash
git add -A
git commit -m "Cleanup: Archive obsolete doc files from initial phases"
```

---

## 📊 RÉSUMÉ AVANT/APRÈS

### AVANT NETTOYAGE:

```
Racine projet:
├─ 23 fichiers .md dans la racine
├─ Confusion: Lequel lire? Quel est à jour?
├─ Redondance: Multiples "résumés" de couverture
└─ Obsolescence: Phases 1-2-3 docs séparés
```

### APRÈS NETTOYAGE:

```
Racine projet:
├─ 5 fichiers .md (sources de vérité)
│  ├─ README.md (projet)
│  ├─ ROADMAP.md (feuille de route)
│  ├─ DASHBOARD_PROGRESS.md (phases 1-5) ← RÉFÉRENCE
│  ├─ SESSION_SUMMARY_PHASE_1_5.md (résultats)
│  └─ ANALYSE_COUVERTURE_REELLE.md (55% vs 80%)
│
└─ docs/
   ├─ archived/ (14 anciens fichiers pour historique)
   ├─ ARCHITECTURE.md
   ├─ FONCTIONNALITES.md
   └─ ... (autres docs)
```

**Résultat**: Claire, concis, maintenable! ✨

---

## 🎯 DOCUMENTS CLÉS POUR UTILISATEUR

### POUR COMPRENDRE RAPIDEMENT:

1. **[ANALYSE_COUVERTURE_REELLE.md](ANALYSE_COUVERTURE_REELLE.md)** ← ⭐ À LIRE EN PREMIER
   - Pourquoi 55% et non 80%
   - Plan détaillé pour Phase 6-9
   - 17-21 heures pour 80%

2. **[SESSION_SUMMARY_PHASE_1_5.md](SESSION_SUMMARY_PHASE_1_5.md)**
   - 646 tests créés
   - Résultats finaux
   - Architecture tests

3. **[DASHBOARD_PROGRESS.md](DASHBOARD_PROGRESS.md)**
   - Timeline phases 1-5
   - Métrique globales
   - Résumé final

### POUR CONTINUER LES PHASES 6-9:

→ Voir **ANALYSE_COUVERTURE_REELLE.md** section "STRATÉGIE POUR ATTEINDRE 80%"
