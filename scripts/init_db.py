# scripts/init_db.py

from core.schema_manager import create_all_tables, reset_tables, log_event

def main():
    log_event("=== Initialisation complète de la base de données ===")

    # Option pour reset complet
    user_input = input("Voulez-vous réinitialiser complètement la base ? (oui/non) : ").strip().lower()
    if user_input in ("oui", "o", "yes", "y"):
        log_event("Réinitialisation des tables...")
        reset_tables()
    else:
        log_event("Création des tables manquantes seulement...")
        create_all_tables()

    log_event("Initialisation terminée avec succès.")

if __name__ == "__main__":
    main()
