"""
Tests for API module.

⚠️ TESTS IGNORÉS PAR DÉFAUT (--ignore=tests/api dans pytest.ini)
═══════════════════════════════════════════════════════════════════
Ces ~150 tests sont actuellement désactivés car ils nécessitent une refonte
pour gérer correctement:
- L'authentification (erreurs 401)
- Les erreurs de base de données mockées (500)
- La structure de réponse différente selon les endpoints

Pour exécuter les tests API:
    pytest tests/api -v --ignore=  # Reset le --ignore

Couvre:
- REST API endpoints (GET, POST, PUT, DELETE, PATCH)
- Authentification et autorisation
- Rate limiting
- Caching
- Erreurs et validation
"""
