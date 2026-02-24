"""Sprint 5B: Mass rename of English model/class names to French."""

import os
import re

# Class renames - longest first to avoid partial matches
# EXCLUDING CreatedAtMixin/TimestampFullMixin (conflict with existing French classes)
CLASS_RENAMES = [
    ("ExternalCalendarConfig", "ConfigCalendrierExterne"),
    ("NotificationPreference", "PreferenceNotification"),
    ("GarminDailySummary", "ResumeQuotidienGarmin"),
    ("FurniturePriority", "PrioriteMeuble"),
    ("PersistentStateDB", "EtatPersistantDB"),
    ("FurnitureStatus", "StatutMeuble"),
    ("PurchaseCategory", "CategorieAchat"),
    ("PurchasePriority", "PrioriteAchat"),
    ("CalendarProvider", "FournisseurCalendrier"),
    ("PushSubscription", "AbonnementPush"),
    ("MaintenanceTask", "TacheEntretien"),
    ("HealthObjective", "ObjectifSante"),
    ("WeekendActivity", "ActiviteWeekend"),
    ("FamilyPurchase", "AchatFamille"),
    ("FamilyActivity", "ActiviteFamille"),
    ("ExpenseCategory", "CategorieDepense"),
    ("RecipeFeedback", "RetourRecette"),
    ("GarminActivity", "ActiviteGarmin"),
    ("UserPreference", "PreferenceUtilisateur"),
    ("CalendarEvent", "EvenementPlanning"),
    ("WellbeingEntry", "EntreeBienEtre"),
    ("EcoActionType", "TypeActionEcologique"),
    ("RecurrenceType", "TypeRecurrence"),
    ("HealthRoutine", "RoutineSante"),
    ("ShoppingItem", "ArticleAchat"),
    ("SyncDirection", "DirectionSync"),
    ("ActionHistory", "HistoriqueAction"),
    ("ChildProfile", "ProfilEnfant"),
    ("FamilyBudget", "BudgetFamille"),
    ("HouseExpense", "DepenseMaison"),
    ("TemplateItem", "ElementTemplate"),
    ("UserProfile", "ProfilUtilisateur"),
    ("FeedbackType", "TypeRetour"),
    ("ProjectTask", "TacheProjet"),
    ("RoutineTask", "TacheRoutine"),
    ("HealthEntry", "EntreeSante"),
    ("GardenItem", "ElementJardin"),
    ("HouseStock", "StockMaison"),
    ("GardenLog", "JournalJardin"),
    ("BatchMeal", "RepasBatch"),
    ("EcoAction", "ActionEcologique"),
    ("FoodLog", "JournalAlimentaire"),
    ("RoomType", "TypePiece"),
    ("Milestone", "Jalon"),
    ("Furniture", "Meuble"),
]

# Table name renames (sorted longest first)
TABLENAME_RENAMES = [
    ("notification_preferences", "preferences_notifications"),
    ("external_calendar_configs", "configs_calendriers_externes"),
    ("shopping_items_famille", "articles_achats_famille"),
    ("garmin_daily_summaries", "resumes_quotidiens_garmin"),
    ("weekend_activities", "activites_weekend"),
    ("family_purchases", "achats_famille"),
    ("user_preferences", "preferences_utilisateurs"),
    ("recipe_feedbacks", "retours_recettes"),
    ("push_subscriptions", "abonnements_push"),
    ("family_activities", "activites_famille"),
    ("garmin_activities", "activites_garmin"),
    ("wellbeing_entries", "entrees_bien_etre"),
    ("maintenance_tasks", "taches_entretien"),
    ("health_objectives", "objectifs_sante"),
    ("persistent_states", "etats_persistants"),
    ("calendar_events", "evenements_planning"),
    ("template_items", "elements_templates"),
    ("health_routines", "routines_sante"),
    ("family_budgets", "budgets_famille"),
    ("house_expenses", "depenses_maison"),
    ("child_profiles", "profils_enfants"),
    ("health_entries", "entrees_sante"),
    ("action_history", "historique_actions"),
    ("user_profiles", "profils_utilisateurs"),
    ("project_tasks", "taches_projets"),
    ("routine_tasks", "taches_routines"),
    ("house_stocks", "stocks_maison"),
    ("garden_items", "elements_jardin"),
    ("garden_logs", "journaux_jardin"),
    ("batch_meals", "repas_batch"),
    ("eco_actions", "actions_ecologiques"),
    ("food_logs", "journaux_alimentaires"),
    ("milestones", "jalons"),
    ("furniture", "meubles"),
    ("projects", "projets"),
    ("backups", "sauvegardes"),
]

# Compile regex patterns for class renames (word boundary)
CLASS_PATTERNS = [(re.compile(r"\b" + old + r"\b"), new) for old, new in CLASS_RENAMES]


def process_file(fpath: str) -> bool:
    """Process a single file. Returns True if modified."""
    with open(fpath, encoding="utf-8") as fh:
        original = fh.read()

    content = original

    # 1. Apply class name renames (word boundary)
    for pattern, new in CLASS_PATTERNS:
        content = pattern.sub(new, content)

    # 2. Apply tablename renames inside quotes
    for old_table, new_table in TABLENAME_RENAMES:
        # __tablename__ = "old" or "old"
        content = content.replace(f'"{old_table}"', f'"{new_table}"')
        content = content.replace(f"'{old_table}'", f"'{new_table}'")
        # ForeignKey("old_table.col") patterns
        content = content.replace(f'"{old_table}.', f'"{new_table}.')
        content = content.replace(f"'{old_table}.", f"'{new_table}.")

    if content != original:
        with open(fpath, "w", encoding="utf-8") as fh:
            fh.write(content)
        return True
    return False


def main():
    dirs = ["src", "tests", "scripts"]
    modified_files = []
    errors = []

    for d in dirs:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                if not f.endswith(".py"):
                    continue
                fpath = os.path.join(root, f)
                try:
                    if process_file(fpath):
                        modified_files.append(fpath)
                except Exception as e:
                    errors.append(f"{fpath}: {e}")

    print(f"Modified {len(modified_files)} files")
    for f in sorted(modified_files):
        print(f"  {f}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  {e}")


if __name__ == "__main__":
    main()
