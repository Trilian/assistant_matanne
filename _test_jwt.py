"""Quick test to verify PyJWT installation."""
try:
    import jwt
    print(f"PyJWT OK: {jwt.__version__}")
except ImportError:
    print("PyJWT NOT INSTALLED")
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "PyJWT"],
        capture_output=True, text=True
    )
    print(result.stdout[-200:] if result.stdout else "no stdout")
    print(result.stderr[-200:] if result.stderr else "no stderr")
    try:
        import jwt
        print(f"PyJWT NOW OK: {jwt.__version__}")
    except ImportError:
        print("STILL NOT INSTALLED")
