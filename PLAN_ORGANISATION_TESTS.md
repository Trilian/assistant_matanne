# 🗂️ Plan d'Organisation des Tests - Assistant Matanne

**Date**: 29 janvier 2026  
**Fichiers actuels**: 116 fichiers de tests  
**Objectif**: Organiser en ~15-20 fichiers logiques (pas 5, trop peu!)

---

## 📊 Analyse des 116 Fichiers Actuels

### ✅ Fichiers à GARDER (bien organisés)

#### Tests de Logique Pure (Priority 1)
- ✅ `test_all_logic_clean.py` (52 tests, 94% réussite) - **EXCELLENT**
- ✅ `test_logic_modules_pure.py` (40 tests cuisine) - **BON**
- ⚠️ `test_all_logic_modules.py` - **DOUBLON partiel** avec les 2 au-dessus

#### Tests Unitaires Spécialisés (à garder séparés)
- ✅ `test_ai_parser.py` - Tests IA/parsing
- ✅ `test_ai_cache.py` - Cache IA
- ✅ `test_ai_agent_sync.py` - Agent IA
- ✅ `test_cache.py` - Cache général
- ✅ `test_cache_multi.py` - Multi-level cache
- ✅ `test_database.py` - Base de données
- ✅ `test_decorators.py` - Décorateurs
- ✅ `test_state.py` - Gestion état
- ✅ `test_lazy_loader.py` - Chargement différé
- ✅ `test_weather.py` - Météo/jardin

### ❌ Fichiers DOUBLONS à Fusionner

#### Doublons Modules (redondance énorme)
```
❌ test_modules_cuisine.py           ]
❌ test_module_cuisine_complet.py    ] → FUSIONNER dans test_modules_cuisine_integration.py
❌ test_module_cuisine_courses.py    ]
❌ test_module_cuisine_recettes.py   ]
❌ test_modules_mocked_cuisine.py    ]

❌ test_modules_famille.py           ]
❌ test_module_famille_complet.py    ] → FUSIONNER dans test_modules_famille_integration.py
❌ test_module_famille_helpers.py    ]
❌ test_modules_mocked_famille.py    ]
❌ test_famille.py                   ]
❌ test_famille_avance.py            ]
❌ test_famille_complete.py          ]

❌ test_modules_maison.py            ]
❌ test_module_maison.py             ] → FUSIONNER dans test_modules_maison_integration.py
❌ test_module_maison_complet.py     ]
❌ test_module_maison_helpers.py     ]
❌ test_modules_mocked_maison.py     ]
❌ test_maison_planning_avance.py    ]

❌ test_modules_planning.py          ]
❌ test_module_planning_complet.py   ] → FUSIONNER dans test_modules_planning_integration.py
❌ test_module_planning_vue_ensemble.py ]
❌ test_modules_mocked_planning.py   ]
❌ test_planning.py                  ]
❌ test_planning_module.py           ]
```

**Total doublons modules: 24 fichiers → 4 fichiers**

#### Doublons Services
```
❌ test_courses.py                   ]
❌ test_courses_module.py            ] → FUSIONNER dans test_services_courses.py
❌ test_courses_logic.py             ]   (la logique va dans test_logic_cuisine.py)

❌ test_inventaire.py                ]
❌ test_inventaire_logic.py          ] → FUSIONNER dans test_services_inventaire.py
❌ test_inventaire_schemas.py        ]

❌ test_recettes.py                  → test_services_recettes.py
❌ test_accueil.py                   → test_modules_root.py
❌ test_accueil_logic.py             → DÉJÀ dans test_all_logic_clean.py
```

#### Doublons Validators
```
❌ test_validators.py                ]
❌ test_validators_pydantic.py       ] → FUSIONNER dans test_validators_complete.py
❌ test_validators_common.py         ]
❌ test_validators_food.py           ]
❌ test_utils_validators.py          ]
```

**Total doublons validators: 5 fichiers → 1 fichier**

#### Doublons UI
```
❌ test_ui_components.py             ]
❌ test_ui_atoms.py                  ] → test_ui_components_complete.py
❌ test_ui_base_form.py              ]
❌ test_ui_forms.py                  ]

❌ test_ui_data.py                   ]
❌ test_ui_layouts.py                ] → test_ui_layouts_data.py
❌ test_ui_progress.py               ]
❌ test_ui_spinners.py               ]
❌ test_ui_toasts.py                 ]
❌ test_ui_tablet_mode.py            ]
```

**Total doublons UI: 10 fichiers → 2 fichiers**

#### Doublons Formatters/Helpers
```
❌ test_formatters.py                ]
❌ test_formatters_dates.py          ] → test_utils_formatters.py
❌ test_formatters_numbers.py        ]
❌ test_formatters_text.py           ]
❌ test_formatters_units.py          ]

❌ test_helpers.py                   ]
❌ test_helpers_data.py              ] → test_utils_helpers.py
❌ test_helpers_stats.py             ]
❌ test_food_helpers.py              ]
❌ test_utils_helpers_extended.py    ]
```

**Total doublons utils: 10 fichiers → 2 fichiers**

#### Doublons Imports/Coverage
```
❌ test_modules_import.py            ]
❌ test_modules_import_coverage.py   ] → SUPPRIMER (tests d'import basiques)
❌ test_modules_integration.py       ]
❌ test_modules_coverage_boost.py    ]
❌ test_app_coverage.py              ]
❌ test_coverage_improvements.py     ]
```

**Total à supprimer: 6 fichiers** (tests artificiels pour augmenter couverture)

---

## 🎯 Structure Cible (15-20 fichiers)

### 📁 Tests de Logique Pure (3 fichiers)

```
tests/logic/
├── test_logic_cuisine.py          # recettes, inventaire, courses (52 tests)
├── test_logic_maison.py           # jardin, projets, entretien (18 tests)
└── test_logic_famille_planning.py # famille (40 tests) + planning (27 tests)
```

**Total: ~137 tests de logique pure**

### 📁 Tests d'Intégration Modules (4 fichiers)

```
tests/integration/
├── test_modules_cuisine.py        # Fusion 5 fichiers doublons
├── test_modules_famille.py        # Fusion 7 fichiers doublons
├── test_modules_maison.py         # Fusion 6 fichiers doublons
└── test_modules_planning.py       # Fusion 6 fichiers doublons
```

### 📁 Tests Services (5 fichiers)

```
tests/services/
├── test_services_recettes.py      # Service recettes
├── test_services_inventaire.py    # Service inventaire + schemas
├── test_services_courses.py       # Service courses
├── test_services_ai.py            # IA général (suggestions, prédictions)
└── test_services_comprehensive.py # ✅ GARDER (déjà complet)
```

### 📁 Tests Core (8 fichiers) - À GARDER

```
tests/core/
├── test_ai_parser.py              # ✅ GARDER
├── test_ai_cache.py               # ✅ GARDER
├── test_ai_agent_sync.py          # ✅ GARDER
├── test_cache.py                  # ✅ GARDER
├── test_cache_multi.py            # ✅ GARDER
├── test_database.py               # ✅ GARDER
├── test_decorators.py             # ✅ GARDER
├── test_state.py                  # ✅ GARDER
└── test_lazy_loader.py            # ✅ GARDER
```

### 📁 Tests UI (2 fichiers)

```
tests/ui/
├── test_ui_components.py          # Fusion 10 fichiers UI
└── test_ui_advanced.py            # Tablet, toasts, progress
```

### 📁 Tests Utils (2 fichiers)

```
tests/utils/
├── test_utils_formatters.py       # Tous formatters
└── test_utils_validators.py       # Tous validators
```

### 📁 Tests Spécialisés (8 fichiers) - À GARDER

```
tests/
├── test_weather.py                # ✅ GARDER (complet)
├── test_recipe_import.py          # ✅ GARDER
├── test_predictions.py            # ✅ GARDER
├── test_notifications.py          # ✅ GARDER (ou fusionner 3 fichiers notif)
├── test_planning_unified.py       # ✅ GARDER
├── test_planning_components.py    # ✅ GARDER
├── test_barcode.py                # ✅ GARDER
├── test_parametres.py             # ✅ GARDER
├── test_rapports.py               # ✅ GARDER
├── test_dashboard_widgets.py      # ✅ GARDER
├── test_calendar_sync.py          # ✅ GARDER
└── test_redis_multi_tenant.py     # ✅ GARDER
```

### 📁 Tests E2E (2 fichiers)

```
tests/e2e/
├── test_e2e.py                    # ✅ GARDER
└── test_e2e_streamlit.py          # ✅ GARDER
```

### 📁 Tests Optionnels (à évaluer)

```
tests/optional/
├── test_auth.py                   # Auth (si utilisé)
├── test_backup.py                 # Backup (si utilisé)
├── test_budget.py                 # Budget (si utilisé)
├── test_offline.py                # Offline (PWA)
├── test_pwa.py                    # PWA
├── test_camera_scanner.py         # Scanner (si utilisé)
└── test_performance.py            # Performance
```

---

## 📊 Résumé de la Réorganisation

### Avant
- **116 fichiers** de tests
- **~50 doublons** identifiés
- Structure désorganisée

### Après
- **~32 fichiers** bien organisés:
  - 3 tests logique pure
  - 4 tests intégration modules
  - 5 tests services
  - 9 tests core (à garder)
  - 2 tests UI
  - 2 tests utils
  - 12 tests spécialisés (à garder)
  - 2 tests E2E
  - 7 optionnels (à évaluer)

### Gain
- **-84 fichiers** (suppression doublons)
- **72% de réduction**
- Structure claire et maintenable

---

## 🗑️ Fichiers à SUPPRIMER (Code Mort)

### Tests Artificiels de Couverture
```bash
❌ test_modules_import.py               # Tests d'import basiques
❌ test_modules_import_coverage.py      # Artificiel
❌ test_modules_coverage_boost.py       # Artificiel
❌ test_app_coverage.py                 # Artificiel
❌ test_coverage_improvements.py        # Artificiel
```

### Doublons test_*_logic.py (déjà dans test_all_logic_clean.py)
```bash
❌ test_accueil_logic.py                # Dans test_all_logic_clean.py
❌ test_courses_logic.py                # Dans test_all_logic_clean.py
❌ test_inventaire_logic.py             # Dans test_all_logic_clean.py
```

### Fichiers Mocked (remplacés par tests intégration)
```bash
❌ test_modules_mocked_cuisine.py
❌ test_modules_mocked_famille.py
❌ test_modules_mocked_maison.py
❌ test_modules_mocked_planning.py
```

### Fichiers "Avancé/Complet" (doublons)
```bash
❌ test_famille_avance.py               # Fusionner dans test_modules_famille.py
❌ test_famille_complete.py             # Fusionner
❌ test_module_cuisine_complet.py       # Fusionner
❌ test_module_famille_complet.py       # Fusionner
❌ test_module_maison_complet.py        # Fusionner
❌ test_module_planning_complet.py      # Fusionner
❌ test_maison_planning_avance.py       # Fusionner
```

### Fichiers API/Push (si non utilisés)
```bash
❌ test_api.py                          # Si API pas utilisée
❌ test_api_extended.py                 # Si API pas utilisée
❌ test_push_notifications_extended.py  # Si push pas utilisé
❌ test_action_history.py               # Si historique pas utilisé
❌ test_image_recipe_utils.py           # Si images recettes pas utilisé
```

**Total à supprimer immédiatement: ~25 fichiers de code mort**

---

## 🚀 Plan d'Action

### Phase 1: Supprimer le Code Mort (URGENT)
```bash
# Supprimer tests artificiels
rm test_modules_import.py test_modules_import_coverage.py
rm test_modules_coverage_boost.py test_app_coverage.py
rm test_coverage_improvements.py

# Supprimer doublons logique
rm test_accueil_logic.py test_courses_logic.py test_inventaire_logic.py

# Supprimer mocked
rm test_modules_mocked_*.py

# Supprimer "avancé/complet"
rm test_*_avance.py test_*_complete.py test_module_*_complet.py
```

**Gain immédiat: -20 fichiers**

### Phase 2: Organiser en dossiers
```bash
mkdir -p tests/{logic,integration,services,core,ui,utils,e2e}
# Déplacer les fichiers dans les bons dossiers
```

### Phase 3: Fusionner les doublons (progressif)
1. Fusionner modules cuisine (5 → 1)
2. Fusionner modules famille (7 → 1)
3. Fusionner modules maison (6 → 1)
4. Fusionner modules planning (6 → 1)
5. Fusionner UI (10 → 2)
6. Fusionner validators (5 → 1)
7. Fusionner formatters (5 → 1)

---

## ✅ Recommandation Finale

**Ne pas réduire à 5 fichiers** - Trop peu, difficile à naviguer!

**Structure idéale: ~30-35 fichiers organisés**
- 3 logique pure
- 4 intégration modules  
- 5 services
- 9 core (garder séparés)
- 2 UI
- 2 utils
- 12 spécialisés
- 2 E2E

**Bénéfices**:
- ✅ Réduction de 72% (116 → 32)
- ✅ Structure claire par domaine
- ✅ Facile à trouver les tests
- ✅ Maintenabilité améliorée
- ✅ Pas trop consolidé (évite fichiers géants)

**Prochaine étape**: Valider la structure et commencer Phase 1 (suppression code mort).
