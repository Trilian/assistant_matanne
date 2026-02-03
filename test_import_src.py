# Test d'import minimal pour diagnostiquer le problème d'environnement
try:
    from src.core.models import Base
    print("Import src.core.models OK")
except Exception as e:
    print(f"Import src.core.models FAILED: {e}")
