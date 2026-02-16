"""
Script pour configurer la clÃ© API Football-Data et tester
"""

from pathlib import Path


def ajouter_cle_api():
    """Ajoute une clÃ© API Ã  .env.local"""

    env_local = Path(".env.local")

    print("=" * 60)
    print("ðŸ”§ Configuration API Football-Data.org")
    print("=" * 60)
    print()

    print("1ï¸âƒ£  S'inscrire sur: https://www.football-data.org/client/register")
    print("2ï¸âƒ£  Obtenir une clÃ© API gratuite (10 req/min)")
    print("3ï¸âƒ£  La copier ci-dessous")
    print()

    api_key = input("ðŸ”‘ Entrer votre clÃ© API: ").strip()

    if not api_key:
        print("âŒ ClÃ© vide, annulation")
        return False

    # VÃ©rifier si .env.local existe
    contenu = ""
    if env_local.exists():
        with open(env_local) as f:
            contenu = f.read()

    # Ajouter ou remplacer la clÃ©
    if "FOOTBALL_DATA_API_KEY=" in contenu:
        lines = contenu.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("FOOTBALL_DATA_API_KEY="):
                lines[i] = f"FOOTBALL_DATA_API_KEY={api_key}"
        contenu = "\n".join(lines)
        print("ðŸ”„ Remplacement de la clÃ© API existante...")
    else:
        if contenu and not contenu.endswith("\n"):
            contenu += "\n"
        contenu += f"FOOTBALL_DATA_API_KEY={api_key}\n"
        print("âœ… Ajout de la clÃ© API...")

    # Ã‰crire dans .env.local
    with open(env_local, "w") as f:
        f.write(contenu)

    print(f"âœ… ClÃ© API ajoutÃ©e Ã  {env_local}")
    print()
    print("ðŸš€ Maintenant, redÃ©marrer Streamlit:")
    print("   streamlit run src/app.py")
    print()

    return True


if __name__ == "__main__":
    ajouter_cle_api()
