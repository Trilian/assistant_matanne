# Test d'import relatif pour diagnostiquer pytest
try:
    from ..src.core.models import Base
    print("Import relatif ..src.core.models OK")
except Exception as e:
    print(f"Import relatif ..src.core.models FAILED: {e}")
