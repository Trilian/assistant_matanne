# Scripts d'Analyse et de Réorganisation des Tests

Ce dossier contient des outils pour analyser, réorganiser et améliorer la couverture des tests dans le projet assistant_matanne.

## Scripts Disponibles

### 1. `analyze_coverage.py` - Analyse de Couverture
Analyse tous les dossiers et fichiers dans `src/` et calcule la couverture pour chaque fichier.

**Usage:**
```bash
python tools/analyze_coverage.py
```

**Sorties:**
- `coverage_analysis_report.md` - Rapport détaillé en markdown
- `coverage_analysis_data.json` - Données brutes JSON
- Affichage dans le terminal

**Ce qu'il fait:**
- Exécute pytest avec coverage
- Analyse la structure des fichiers
- Identifie les tests correspondants
- Génère des recommandations

### 2. `split_large_files.py` - Analyse des Fichiers Volumineux
Identifie les fichiers source dépassant 1000 lignes et suggère des divisions.

**Usage:**
```bash
python tools/split_large_files.py
```

**Sorties:**
- `large_files_analysis.json` - Analyse des fichiers volumineux
- Affichage dans le terminal avec suggestions

**Ce qu'il analyse:**
- Classes volumineuses (>200 lignes)
- Groupes de fonctions par domaine
- Structure AST des fichiers
- Suggestions de refactoring

**Fichiers identifiés (>1000 lignes):**
1. `services/calendar_sync.py` (1295 lignes)
2. `domains/jeux/logic/paris_logic.py` (1265 lignes)
3. `services/recettes.py` (1236 lignes)
4. `services/rapports_pdf.py` (1161 lignes)
5. `services/budget.py` (1154 lignes) - Suggestion: extraire BudgetService
6. `services/inventaire.py` (1096 lignes)

### 3. `reorganize_tests.py` - Analyse de l'Organisation des Tests
Analyse la structure des tests et crée un plan pour établir un mapping 1:1 entre fichiers source et tests.

**Usage:**
```bash
python tools/reorganize_tests.py
```

**Sorties:**
- `test_analysis.json` - Analyse complète de la structure
- `test_reorganization_plan.json` - Plan d'action détaillé
- `test_reorganization_report.md` - Rapport en markdown

**Ce qu'il identifie:**
- Fichiers source sans tests (54 fichiers)
- Fichiers avec tests dupliqués (114 fichiers)
- Nombre total de fonctions de test (14,809)
- Mapping source → tests

### 4. `implement_reorganization.py` - Implémentation de la Réorganisation
Applique le plan de réorganisation généré par `reorganize_tests.py`.

**Usage:**
```bash
# Mode dry-run (par défaut, ne modifie rien)
python tools/implement_reorganization.py

# Mode exécution (applique les modifications)
python tools/implement_reorganization.py --execute
```

**Ce qu'il fait:**
- Crée 54 fichiers de test stub pour les fichiers sans tests
- Consolide 114 fichiers avec tests dupliqués
- Sauvegarde les tests dupliqués en .bak
- Établit une structure 1:1

**⚠️ ATTENTION:** En mode `--execute`, ce script modifie les fichiers! Toujours tester en mode dry-run d'abord.

### 5. `fix_utf8_bom.py` - Correction des Problèmes UTF-8 BOM
Corrige les fichiers Python avec des caractères BOM (U+FEFF) qui causent des erreurs de parsing.

**Usage:**
```bash
# Mode dry-run
python tools/fix_utf8_bom.py

# Mode exécution
python tools/fix_utf8_bom.py --execute
```

**Fichiers affectés:**
- `services/calendar_sync.py`
- `services/recettes.py`
- `services/rapports_pdf.py`
- `services/inventaire.py`

## Workflow Recommandé

### Phase 1: Analyse
```bash
# 1. Analyser la couverture actuelle
python tools/analyze_coverage.py

# 2. Identifier les fichiers volumineux
python tools/split_large_files.py

# 3. Analyser l'organisation des tests
python tools/reorganize_tests.py
```

### Phase 2: Corrections Simples
```bash
# 1. Corriger les problèmes UTF-8 BOM (dry-run d'abord)
python tools/fix_utf8_bom.py
python tools/fix_utf8_bom.py --execute

# 2. Créer les tests manquants et consolider (dry-run d'abord)
python tools/implement_reorganization.py
python tools/implement_reorganization.py --execute
```

### Phase 3: Refactoring Manuel
Après l'analyse, refactoriser manuellement:

1. **Diviser les fichiers volumineux:**
   - Utiliser les suggestions de `split_large_files.py`
   - Créer de nouveaux fichiers pour les classes/fonctions extraites
   - Mettre à jour les imports

2. **Consolider les tests dupliqués:**
   - Examiner les tests dupliqués identifiés
   - Fusionner manuellement le contenu pertinent
   - Supprimer les doublons

3. **Compléter les tests stub:**
   - Les fichiers créés sont des stubs minimaux
   - Ajouter des tests réels pour atteindre 80% de couverture

### Phase 4: Validation
```bash
# 1. Exécuter tous les tests
pytest

# 2. Vérifier la couverture
pytest --cov=src --cov-report=term --cov-report=html

# 3. Ré-analyser après modifications
python tools/analyze_coverage.py
python tools/reorganize_tests.py
```

## Objectifs du Projet

- ✅ **Structure 1:1**: Un fichier de test par fichier source
- ✅ **80% de couverture**: Objectif minimum pour chaque module
- ✅ **Fichiers < 1000 lignes**: Diviser les gros fichiers
- ✅ **Tests organisés**: Structure miroir tests/ ↔ src/
- ✅ **Qualité**: Supprimer/refactorer les tests inefficaces

## Résultats de l'Analyse

### État Initial
- **228 fichiers source** dans `src/`
- **375 fichiers de test** dans `tests/`
- **14,809 fonctions de test** (bien plus que les 10,000 estimés!)
- **174 fichiers avec tests** (76%)
- **54 fichiers sans tests** (24%)
- **114 fichiers avec tests dupliqués**

### Actions Identifiées
1. Créer 54 fichiers de test manquants
2. Consolider 114 fichiers avec tests dupliqués
3. Diviser 6 fichiers volumineux (>1000 lignes)
4. Corriger 5 fichiers avec problèmes UTF-8 BOM
5. Supprimer/refactorer les tests < 80% de couverture

## Notes Importantes

### Sécurité
- Tous les scripts ont un mode dry-run par défaut
- Toujours tester en dry-run avant d'exécuter
- Les fichiers modifiés sont sauvegardés en .bak

### Performance
- L'analyse complète peut prendre plusieurs minutes
- Les tests complets (~15,000 tests) prennent du temps
- Utiliser pytest avec -k pour tester des modules spécifiques

### Maintenance
- Ré-exécuter régulièrement l'analyse après modifications
- Mettre à jour ce README si nouveaux scripts ajoutés
- Conserver les fichiers JSON pour traçabilité

## Support

Pour toute question ou problème:
1. Vérifier la documentation dans chaque script (docstrings)
2. Examiner les rapports générés (markdown + JSON)
3. Consulter le README principal du projet

---

**Dernière mise à jour:** 2026-02-10
**Auteur:** Assistant Copilot + @Trilian
