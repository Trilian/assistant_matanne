"""
Génère les icônes PWA à partir d'une image SVG de base.

Usage:
    python scripts/generate_pwa_icons.py

Requiert: Pillow (pip install Pillow)

Génère des PNG de tailles variées dans static/icons/
pour le manifest.json de la PWA.
"""

from __future__ import annotations

import io
import struct
import zlib
from pathlib import Path

# Tailles requises par le manifest.json
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]
ICONS_DIR = Path(__file__).parent.parent / "static" / "icons"


def _create_png(size: int, bg_color: tuple[int, int, int] = (102, 126, 234)) -> bytes:
    """Crée un PNG minimal avec un arrière-plan coloré et un emoji-style 'M'.

    Génère un PNG valide sans dépendances externes (pure Python).
    Pour des icônes de production, remplacer par de vraies images.

    Args:
        size: Taille en pixels (carré)
        bg_color: Couleur RGB de fond

    Returns:
        Bytes du fichier PNG
    """
    r, g, b = bg_color

    # Créer les données brutes du pixel (RGBA)
    raw_data = bytearray()
    center = size / 2
    radius = size * 0.42  # Cercle principal

    for y in range(size):
        raw_data.append(0)  # Filter byte
        for x in range(size):
            # Distance au centre
            dx = x - center
            dy = y - center
            dist = (dx * dx + dy * dy) ** 0.5

            if dist <= radius:
                # Intérieur du cercle: couleur de fond
                raw_data.extend([r, g, b, 255])
            else:
                # Extérieur: transparent
                raw_data.extend([0, 0, 0, 0])

    # Construire le PNG
    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)

    # Signature PNG
    png = b"\x89PNG\r\n\x1a\n"

    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png += _chunk(b"IHDR", ihdr_data)

    # IDAT
    compressed = zlib.compress(bytes(raw_data), 9)
    png += _chunk(b"IDAT", compressed)

    # IEND
    png += _chunk(b"IEND", b"")

    return png


def main():
    """Point d'entrée: génère toutes les icônes."""
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"📱 Génération des icônes PWA dans {ICONS_DIR}")

    for size in ICON_SIZES:
        filename = f"icon-{size}x{size}.png"
        filepath = ICONS_DIR / filename

        png_data = _create_png(size)
        filepath.write_bytes(png_data)

        print(f"  ✅ {filename} ({len(png_data):,} bytes)")

    print(f"\n✅ {len(ICON_SIZES)} icônes générées.")
    print("💡 Pour des icônes de production, remplacez par de vraies images.")


if __name__ == "__main__":
    main()
