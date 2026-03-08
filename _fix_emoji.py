"""Fix double-encoded emojis in cuisine module files."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

files_to_fix = [
    "src/modules/cuisine/recettes/liste.py",
    "src/modules/cuisine/recettes/detail.py",
    "src/modules/cuisine/recettes/generation_ia.py",
    "src/modules/cuisine/batch_cooking_temps.py",
]

for relpath in files_to_fix:
    filepath = os.path.join(BASE, relpath)
    if not os.path.exists(filepath):
        print(f"SKIP (not found): {relpath}")
        continue

    with open(filepath, "rb") as f:
        raw = f.read()

    original = raw

    # ⏱️ = U+23F1 U+FE0F  -> UTF-8: e2 8f b1 ef b8 8f
    # Double-encoded in cp1252->UTF-8: c3a2 c28f c2b1 c3af c2b8 c28f
    raw = raw.replace(
        b"\xc3\xa2\xc2\x8f\xc2\xb1\xc3\xaf\xc2\xb8\xc2\x8f",
        "\u23f1\ufe0f".encode("utf-8"),
    )

    # ⚫ = U+26AB -> UTF-8: e2 9a ab
    # Double-encoded: c3a2 c5a1 c2ab
    raw = raw.replace(
        b"\xc3\xa2\xc5\xa1\xc2\xab",
        "\u26ab".encode("utf-8"),
    )

    # ❄️ = U+2744 U+FE0F -> UTF-8: e2 9d 84 ef b8 8f
    # Double-encoded: c3a2 c29d c284 c3af c2b8 c28f
    raw = raw.replace(
        b"\xc3\xa2\xc2\x9d\xc2\x84\xc3\xaf\xc2\xb8\xc2\x8f",
        "\u2744\ufe0f".encode("utf-8"),
    )

    # 🐟£ in batch_cooking_temps.py (double-encoded)
    # 🐟 = U+1F41F -> UTF-8: f0 9f 90 9f
    # Double-encoded from cp1252: might appear as noise
    # Let's just check and fix known patterns

    if raw != original:
        with open(filepath, "wb") as f:
            f.write(raw)
        print(f"FIXED: {relpath}")
    else:
        print(f"OK (no change): {relpath}")

# Also check batch_cooking_temps.py for the 🐟£ issue
bt_path = os.path.join(BASE, "src/modules/cuisine/batch_cooking_temps.py")
if os.path.exists(bt_path):
    with open(bt_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "🐟£" in content:
        content = content.replace("🐟£", "🟡")  # Mercredi was 🟡 or similar
        with open(bt_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("FIXED: batch_cooking_temps.py (🐟£ -> 🟡)")
