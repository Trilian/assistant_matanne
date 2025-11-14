class CloudService:
    """Service cloud minimal pour test."""

    def save_data(self, key, value):
        # Pour l’instant, juste afficher
        print(f"[Cloud] Sauvegarde {key}: {value}")

    def load_data(self, key):
        # Retourne toujours None pour test
        print(f"[Cloud] Chargement {key}")
        return None
