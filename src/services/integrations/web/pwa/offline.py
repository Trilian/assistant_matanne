"""
Page offline PWA - HTML de la page hors-ligne.

Ce module contient:
- OFFLINE_HTML: Code HTML complet de la page offline
- generate_offline_page(): Génération du fichier offline.html
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


OFFLINE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hors ligne - Assistant Matanne</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
            padding: 20px;
        }
        .container {
            max-width: 400px;
        }
        .icon {
            font-size: 80px;
            margin-bottom: 20px;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 16px;
        }
        p {
            opacity: 0.9;
            line-height: 1.6;
            margin-bottom: 24px;
        }
        button {
            background: white;
            color: #667eea;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.05);
        }
        .tips {
            margin-top: 40px;
            font-size: 14px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">📴</div>
        <h1>Vous êtes hors ligne</h1>
        <p>
            L'application nécessite une connexion internet pour fonctionner.
            Vérifiez votre connexion et réessayez.
        </p>
        <button onclick="location.reload()">Réessayer</button>
        <div class="tips">
            <p>💡 Astuce: Les données consultées récemment sont disponibles en mode hors ligne.</p>
        </div>
    </div>
</body>
</html>
"""


def generate_offline_page(output_path: str | Path) -> Path:
    """
    Génère la page offline.

    Args:
        output_path: Chemin du dossier de sortie

    Returns:
        Chemin du fichier créé
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    offline_path = output_path / "offline.html"
    offline_path.write_text(OFFLINE_HTML, encoding="utf-8")

    logger.info(f"✅ Page offline générée: {offline_path}")
    return offline_path
