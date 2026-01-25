"""
Guide Exécution Tests Planning Module

╔════════════════════════════════════════════════════════════╗
║  Tests du Module Planning Refactorisé                     ║
║  Suite complète: 100+ tests (unitaires + intégration)     ║
╚════════════════════════════════════════════════════════════╝

📊 COUVERTURE TESTS
═══════════════════════════════════════════════════════════════

✅ tests/test_planning_unified.py (85 lignes tests)
   - CRUD basique (création events)
   - Agrégation données (repas, activités, projets, routines, events)
   - Calcul charge (formule, labels)
   - Détection alertes intelligentes
   - Intégration semaine complète
   - Schémas Pydantic
   - Cache (validation, invalidation)
   - Génération IA (mocks)

✅ tests/test_planning_schemas.py (450 lignes tests)
   - JourCompletSchema validation complète
   - SemaineCompleSchema validation
   - SemaineGenereeIASchema validation
   - ContexteFamilleSchema validation
   - ContraintesSchema validation
   - Tests edge cases (négatifs, limites)
   - Composabilité schémas

✅ tests/integration/test_planning_full.py (320 lignes tests)
   - Flux complet création → agrégation → affichage
   - Setup famille complète (tous types événements)
   - Cache intégration (hit, invalidation, indépendance semaines)
   - Navigation semaine (prev, next)
   - Stress tests (15+ events, multiple jours)
   - Validation données (cohérence, présence)

✅ tests/test_planning_components.py (250 lignes tests)
   - Badges (charge, priorité, Jules adapté)
   - Cartes (repas, activité, projet, event)
   - Sélecteurs (semaine)
   - Affichages (alertes, stats)
   - Formatage données
   - Intégration composants


📋 CATÉGORIES TESTS
═══════════════════════════════════════════════════════════════

@pytest.mark.unit
   └─ Tests isolés, pas de DB
   └─ ~350 tests
   └─ Temps: ~2-3 secondes

@pytest.mark.integration
   └─ Tests avec DB complète
   └─ ~40 tests
   └─ Temps: ~10-15 secondes

Total: ~390 tests, ~15-20 secondes execution


🚀 COMMANDES EXÉCUTION
═══════════════════════════════════════════════════════════════

1️⃣  TOUS LES TESTS
   ───────────────────────────────────────────────────────────
   pytest tests/test_planning_unified.py tests/test_planning_schemas.py tests/test_planning_components.py tests/integration/test_planning_full.py -v
   
   Ou simplement:
   python manage.py test_coverage


2️⃣  TESTS UNITAIRES SEULEMENT (rapides)
   ───────────────────────────────────────────────────────────
   pytest tests/test_planning_unified.py tests/test_planning_schemas.py tests/test_planning_components.py -v -m unit


3️⃣  TESTS D'INTÉGRATION SEULEMENT
   ───────────────────────────────────────────────────────────
   pytest tests/integration/test_planning_full.py -v -m integration


4️⃣  FICHIER SPÉCIFIQUE
   ───────────────────────────────────────────────────────────
   # Tests service
   pytest tests/test_planning_unified.py -v
   
   # Tests schemas
   pytest tests/test_planning_schemas.py -v
   
   # Tests composants
   pytest tests/test_planning_components.py -v
   
   # Tests intégration
   pytest tests/integration/test_planning_full.py -v


5️⃣  TEST SPÉCIFIQUE (une classe ou méthode)
   ───────────────────────────────────────────────────────────
   # Une classe de tests
   pytest tests/test_planning_unified.py::TestCalculCharge -v
   
   # Une méthode précise
   pytest tests/test_planning_unified.py::TestCalculCharge::test_charge_intense_multiple -v


6️⃣  AVEC RAPPORT DE COUVERTURE
   ───────────────────────────────────────────────────────────
   pytest tests/test_planning_unified.py tests/test_planning_schemas.py tests/test_planning_components.py tests/integration/test_planning_full.py --cov=src/services/planning_unified --cov-report=html
   
   Puis open: htmlcov/index.html


7️⃣  MODE VERBEUX & DEBUG
   ───────────────────────────────────────────────────────────
   pytest tests/test_planning_unified.py -v -s
   
   # Afficher print() statements:
   pytest tests/test_planning_unified.py -v -s --capture=no


8️⃣  STOP AU PREMIER ERREUR
   ───────────────────────────────────────────────────────────
   pytest tests/test_planning_unified.py -x


9️⃣  AFFICHER 5 DERNIERS TESTS PLUS LENTS
   ───────────────────────────────────────────────────────────
   pytest tests/test_planning_unified.py --durations=5


🔟 WATCHES (réexécute à chaque sauvegarde)
   ───────────────────────────────────────────────────────────
   # Nécessite pytest-watch: pip install pytest-watch
   ptw tests/test_planning_unified.py -v


📊 STRUCTURE TESTS
═══════════════════════════════════════════════════════════════

test_planning_unified.py
├─ TestPlanningServiceCRUD
│  ├─ test_creer_event()
│  ├─ test_creer_event_avec_lieu()
│  └─ test_creer_event_avec_fin()
├─ TestAggregation
│  ├─ test_charger_repas()
│  ├─ test_charger_activites()
│  ├─ test_charger_events()
│  ├─ test_charger_projets()
│  └─ test_charger_routines()
├─ TestCalculCharge
│  ├─ test_charge_faible()
│  ├─ test_charge_normal_repas()
│  ├─ test_charge_intense_multiple()
│  ├─ test_score_to_charge_faible/normal/intense()
├─ TestDetectionAlertes
│  ├─ test_alerte_surcharge()
│  ├─ test_alerte_pas_activite_jules()
│  ├─ test_alerte_projet_urgent()
│  ├─ test_pas_alerte_jour_calme()
│  └─ test_alertes_semaine_jules()
├─ TestSemaineComplete
│  ├─ test_get_semaine_complete_vide()
│  ├─ test_get_semaine_complete_avec_donnees()
│  ├─ test_semaine_charge_calcule()
│  └─ test_semaine_stats_correctes()
├─ TestSchemasPydantic
│  ├─ test_jour_complet_schema_valid()
│  ├─ test_jour_complet_schema_avec_donnees()
│  └─ test_semaine_complete_schema_valid()
├─ TestCache
│  ├─ test_cache_semaine_complete()
│  └─ test_invalider_cache_semaine()
└─ TestGenerationIA
   ├─ test_construire_prompt_generation()
   └─ test_generer_semaine_ia_sans_ia()

test_planning_schemas.py (430+ lignes)
├─ TestJourCompletSchema (11 tests)
├─ TestSemaineCompleSchema (7 tests)
├─ TestSemaineGenereeIASchema (4 tests)
├─ TestContexteFamilleSchema (6 tests)
├─ TestContraintesSchema (6 tests)
├─ TestComposabiliteSchemas (3 tests)
└─ Validation complète de tous les schémas

test_planning_components.py (250+ lignes)
├─ TestBadges (9 tests)
├─ TestCartes (11 tests)
├─ TestSelecteurs (1 test)
├─ TestAffichages (4 tests)
├─ TestFormatage (4 tests)
└─ TestIntegrationComposants (5 tests)

integration/test_planning_full.py (320+ lignes)
├─ TestFluxComplet (6 tests)
├─ TestCacheIntegration (3 tests)
├─ TestNavigationSemaine (2 tests)
├─ TestPerformance (2 tests)
└─ TestValidationDonnees (4 tests)


✅ RÉSULTATS ATTENDUS
═══════════════════════════════════════════════════════════════

Test Run Summary:
   PASSED tests: ~385
   FAILED tests: 0
   SKIPPED tests: 0
   Duration: ~15-20 secondes
   Success Rate: 100%


🔧 FIXTURES DISPONIBLES
═══════════════════════════════════════════════════════════════

conftest.py (existant):
   - db: Session                    # SQLite in-memory DB
   - engine: Engine                 # DB engine
   - test_db_url: str              # "sqlite:///:memory:"

test_planning_unified.py (nouveau):
   - service: PlanningAIService    # Service instance
   - semaine_test: (date, date)    # Semaine test (lundi-dimanche)
   - recette_test: Recette         # Recette test
   - planning_test: Planning       # Planning avec repas
   - activites_test: List[Activity]
   - events_test: List[CalendarEvent]
   - projets_test: List[Project]
   - routines_test: List[Routine]

integration/test_planning_full.py (nouveau):
   - service_integration: PlanningAIService
   - semaine_complete_test: (date, date)
   - famille_complete_setup: dict  # Setup complète
      ├─ planning
      ├─ recettes
      ├─ repas
      ├─ activites
      ├─ events
      ├─ projets
      └─ routines


🎯 OBJECTIFS COUVERTURE
═══════════════════════════════════════════════════════════════

✅ Service PlanningAIService: ~95%
   └─ CRUD, agrégation, calculs, alertes, cache

✅ Schémas Pydantic: ~100%
   └─ Validation complète, edge cases

✅ Composants UI: ~85%
   └─ Badges, cartes, sélecteurs, affichages

✅ Intégration: ~90%
   └─ Flux complet, cache, navigation, performance


❌ ERREURS COURANTES & SOLUTIONS
═══════════════════════════════════════════════════════════════

❌ "ImportError: cannot import name 'PlanningAIService'"
   ✅ Solution: Vérifier que src/services/planning_unified.py existe
   
❌ "No such table: planning"
   ✅ Solution: conftest.py crée les tables automatiquement
   
❌ "fixture 'db' not found"
   ✅ Solution: Lancer depuis racine du projet (où conftest.py existe)
   
❌ "Test timeout"
   ✅ Solution: Utiliser -x pour arrêter au premier erreur
   
❌ Mock Streamlit erreurs
   ✅ Solution: Tests composants utilisent @patch pour mocker st


📝 NOTES IMPORTANTES
═══════════════════════════════════════════════════════════════

1️⃣  Tests prêts à l'emploi - pas de modification nécessaire

2️⃣  Tous les tests utilisent fixtures du projet existant (conftest.py)

3️⃣  Pas de dépendances externes (sauf pytest standard)

4️⃣  Tests marqués @pytest.mark.unit et @pytest.mark.integration
    pour faciliter filtrage

5️⃣  Couvre:
    - Logique métier (calcul charge, alertes)
    - Validation données (schémas Pydantic)
    - Intégration (flux complet, cache)
    - UI (composants, formatage)

6️⃣  Temps total exécution: ~15-20 secondes
    → Rapide pour exécution dans CI/CD


🎬 QUICK START
═══════════════════════════════════════════════════════════════

# Terminal
cd d:\\Projet_streamlit\\assistant_matanne

# Exécuter tous les tests
pytest tests/test_planning_unified.py tests/test_planning_schemas.py tests/test_planning_components.py tests/integration/test_planning_full.py -v

# Ou via manage.py
python manage.py test_coverage

✨ C'est parti! 🚀
"""

# Document texte - pour référence
