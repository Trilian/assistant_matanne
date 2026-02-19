"""Quick test to verify API loads with auth routes."""
import sys
try:
    from src.api.main import app
    routes = [r for r in app.routes if hasattr(r, 'methods')]
    with open('_test_result.txt', 'w') as f:
        f.write(f"OK - {len(routes)} routes\n")
        for r in routes:
            if '/auth' in r.path:
                f.write(f"  {r.methods} {r.path}\n")
    print(f"OK: {len(routes)} routes")
except Exception as e:
    with open('_test_result.txt', 'w') as f:
        import traceback
        f.write(f"ERREUR: {e}\n")
        f.write(traceback.format_exc())
    print(f"ERREUR: {e}")
    sys.exit(1)
