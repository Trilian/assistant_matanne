"""
Script de seed - DonnÃ©es de dÃ©monstration
Remplit la base avec des donnÃ©es rÃ©alistes pour tester l'application
"""

import sys
from pathlib import Path

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, timedelta

from src.core.db import obtenir_contexte_db
from src.core.models import (
    ElementJardin,
    EntreeBienEtre,
    EvenementPlanning,
    Ingredient,
    InventoryItem,
    JournalJardin,
    Notification,
    ProfilEnfant,
    ProfilUtilisateur,
    Project,
    Recette,
    RecetteIngredient,
    RepasBatch,
    Routine,
    ShoppingList,
    TacheProjet,
    TacheRoutine,
    User,
    WeatherLog,
)


def clear_database():
    """Nettoie toutes les donnÃ©es (optionnel)"""
    print("ð§¹ Nettoyage de la base...")

    with obtenir_contexte_db() as db:
        # Supprimer dans l'ordre inverse des dÃ©pendances
        db.query(JournalJardin).delete()
        db.query(ElementJardin).delete()
        db.query(TacheProjet).delete()
        db.query(Project).delete()
        db.query(TacheRoutine).delete()
        db.query(Routine).delete()
        db.query(EntreeBienEtre).delete()
        db.query(ProfilEnfant).delete()
        db.query(ShoppingList).delete()
        db.query(RepasBatch).delete()
        db.query(RecetteIngredient).delete()
        db.query(InventoryItem).delete()
        db.query(Recette).delete()
        db.query(Ingredient).delete()
        db.query(EvenementPlanning).delete()
        db.query(WeatherLog).delete()
        db.query(Notification).delete()
        db.query(ProfilUtilisateur).delete()
        db.query(User).delete()

        db.commit()

    print("âœ… Base nettoyÃ©e")


def seed_users():
    """CrÃ©e les utilisateurs"""
    print("ð¤ Création des utilisateurs...")

    with obtenir_contexte_db() as db:
        # Utilisateur principal
        anne = User(
            username="Anne",
            email="anne@matanne.app",
            settings={"theme": "light", "notifications": True, "language": "fr"},
        )
        db.add(anne)
        db.flush()

        # Profils
        profil_anne = ProfilUtilisateur(
            user_id=anne.id,
            profile_name="Anne (Maman)",
            role="parent",
            preferences={"favoris": ["cuisine", "jardin"]},
            is_active=True,
        )

        profil_mathieu = ProfilUtilisateur(
            user_id=anne.id,
            profile_name="Mathieu (Papa)",
            role="parent",
            preferences={"favoris": ["projets", "jardin"]},
            is_active=True,
        )

        db.add_all([profil_anne, profil_mathieu])
        db.commit()

        print(f"âœ… Utilisateur '{anne.username}' crÃ©Ã© avec 2 profils")
        return anne.id


def seed_ingredients():
    """CrÃ©e les ingrÃ©dients de base"""
    print("ðŸ¥• CrÃ©ation des ingrÃ©dients...")

    ingredients_data = [
        # LÃ©gumes
        ("Tomates", "kg", "LÃ©gumes"),
        ("Carottes", "kg", "LÃ©gumes"),
        ("Oignons", "kg", "LÃ©gumes"),
        ("Pommes de terre", "kg", "LÃ©gumes"),
        ("Courgettes", "kg", "LÃ©gumes"),
        ("Poivrons", "pcs", "LÃ©gumes"),
        # FÃ©culents
        ("PÃ¢tes", "g", "FÃ©culents"),
        ("Riz", "g", "FÃ©culents"),
        ("Farine", "g", "FÃ©culents"),
        ("Pain", "pcs", "FÃ©culents"),
        # ProtÃ©ines
        ("Poulet", "g", "ProtÃ©ines"),
        ("Boeuf hachÃ©", "g", "ProtÃ©ines"),
        ("Oeufs", "pcs", "ProtÃ©ines"),
        ("Saumon", "g", "ProtÃ©ines"),
        # Laitier
        ("Lait", "L", "Laitier"),
        ("Fromage rÃ¢pÃ©", "g", "Laitier"),
        ("Yaourts", "pcs", "Laitier"),
        ("Beurre", "g", "Laitier"),
        ("CrÃ¨me fraÃ®che", "mL", "Laitier"),
        # Fruits
        ("Pommes", "pcs", "Fruits"),
        ("Bananes", "pcs", "Fruits"),
        ("Oranges", "pcs", "Fruits"),
        # Ã‰pices et autres
        ("Sel", "g", "Ã‰pices"),
        ("Poivre", "g", "Ã‰pices"),
        ("Huile d'olive", "mL", "Huiles"),
        ("Ail", "pcs", "Ã‰pices"),
    ]

    with obtenir_contexte_db() as db:
        for nom, unite, categorie in ingredients_data:
            ingredient = Ingredient(name=nom, unit=unite, category=categorie)
            db.add(ingredient)

        db.commit()

    print(f"â {len(ingredients_data)} ingrédients créés")


def seed_recipes():
    """ÃCrée des recettes d'exemple"""
    print("ð Création des recettes...")

    with obtenir_contexte_db() as db:
        # Recette 1 : Pâtes à la tomate
        r1 = Recette(
            name="PÃ¢tes Ã  la tomate",
            category="Plat",
            instructions="1. Faire cuire les pÃ¢tes\n2. PrÃ©parer la sauce tomate\n3. MÃ©langer et servir",
            prep_time=10,
            cook_time=15,
            servings=4,
            difficulty="Facile",
        )
        db.add(r1)
        db.flush()

        # IngrÃ©dients pÃ¢tes tomate
        ing_pates = db.query(Ingredient).filter(Ingredient.name == "PÃ¢tes").first()
        ing_tomates = db.query(Ingredient).filter(Ingredient.name == "Tomates").first()
        ing_ail = db.query(Ingredient).filter(Ingredient.name == "Ail").first()

        db.add_all(
            [
                RecetteIngredient(
                    recette_id=r1.id, ingredient_id=ing_pates.id, quantity=400, unit="g"
                ),
                RecetteIngredient(
                    recette_id=r1.id, ingredient_id=ing_tomates.id, quantity=0.5, unit="kg"
                ),
                RecetteIngredient(
                    recette_id=r1.id, ingredient_id=ing_ail.id, quantity=2, unit="pcs"
                ),
            ]
        )

        # Recette 2 : Poulet rÃ´ti
        r2 = Recette(
            name="Poulet rÃ´ti aux lÃ©gumes",
            category="Plat",
            instructions="1. PrÃ©parer le poulet\n2. Couper les lÃ©gumes\n3. Enfourner 45min Ã  180Â°C",
            prep_time=15,
            cook_time=45,
            servings=4,
            difficulty="Moyen",
        )
        db.add(r2)
        db.flush()

        ing_poulet = db.query(Ingredient).filter(Ingredient.name == "Poulet").first()
        ing_carottes = db.query(Ingredient).filter(Ingredient.name == "Carottes").first()
        ing_pdt = db.query(Ingredient).filter(Ingredient.name == "Pommes de terre").first()

        db.add_all(
            [
                RecetteIngredient(
                    recette_id=r2.id, ingredient_id=ing_poulet.id, quantity=1200, unit="g"
                ),
                RecetteIngredient(
                    recette_id=r2.id, ingredient_id=ing_carottes.id, quantity=0.5, unit="kg"
                ),
                RecetteIngredient(
                    recette_id=r2.id, ingredient_id=ing_pdt.id, quantity=0.6, unit="kg"
                ),
            ]
        )

        # Recette 3 : Omelette
        r3 = Recette(
            name="Omelette nature",
            category="Plat",
            instructions="1. Battre les oeufs\n2. Cuire Ã  la poÃªle\n3. Servir chaud",
            prep_time=5,
            cook_time=10,
            servings=2,
            difficulty="Facile",
        )
        db.add(r3)
        db.flush()

        ing_oeufs = db.query(Ingredient).filter(Ingredient.name == "Oeufs").first()
        ing_beurre = db.query(Ingredient).filter(Ingredient.name == "Beurre").first()

        db.add_all(
            [
                RecetteIngredient(
                    recette_id=r3.id, ingredient_id=ing_oeufs.id, quantity=4, unit="pcs"
                ),
                RecetteIngredient(
                    recette_id=r3.id, ingredient_id=ing_beurre.id, quantity=20, unit="g"
                ),
            ]
        )

        # Recette 4 : Gratin dauphinois (gÃ©nÃ©rÃ©e par IA)
        r4 = Recette(
            name="Gratin dauphinois",
            category="Accompagnement",
            instructions="1. Ã‰mincer les pommes de terre\n2. PrÃ©parer la crÃ¨me\n3. Enfourner 1h",
            prep_time=20,
            cook_time=60,
            servings=6,
            difficulty="Moyen",
            ai_generated=True,
            ai_score=92.5,
        )
        db.add(r4)
        db.flush()

        ing_creme = db.query(Ingredient).filter(Ingredient.name == "CrÃ¨me fraÃ®che").first()
        ing_fromage = db.query(Ingredient).filter(Ingredient.name == "Fromage rÃ¢pÃ©").first()

        db.add_all(
            [
                RecetteIngredient(
                    recette_id=r4.id, ingredient_id=ing_pdt.id, quantity=1.0, unit="kg"
                ),
                RecetteIngredient(
                    recette_id=r4.id, ingredient_id=ing_creme.id, quantity=300, unit="mL"
                ),
                RecetteIngredient(
                    recette_id=r4.id, ingredient_id=ing_fromage.id, quantity=150, unit="g"
                ),
            ]
        )

        db.commit()

    print("âœ… 4 recettes crÃ©Ã©es (dont 1 par IA)")


def seed_inventory():
    """Remplit l'inventaire"""
    print("ðŸ“¦ Remplissage de l'inventaire...")

    inventory_data = [
        ("Tomates", 2.5, 1.0, "Frigo"),
        ("Carottes", 1.2, 0.5, "Frigo"),
        ("Oignons", 0.8, 0.3, "Placard"),
        ("Pommes de terre", 3.0, 1.0, "Placard"),
        ("PÃ¢tes", 800, 200, "Placard"),
        ("Riz", 500, 200, "Placard"),
        ("Poulet", 0, 500, "CongÃ©lateur"),  # Stock vide
        ("Oeufs", 6, 6, "Frigo"),
        ("Lait", 0.5, 1.0, "Frigo"),  # Stock bas
        ("Fromage rÃ¢pÃ©", 50, 100, "Frigo"),  # Stock bas
        ("Huile d'olive", 500, 100, "Placard"),
    ]

    with obtenir_contexte_db() as db:
        for nom, qty, seuil, location in inventory_data:
            ingredient = db.query(Ingredient).filter(Ingredient.name == nom).first()
            if ingredient:
                item = InventoryItem(
                    ingredient_id=ingredient.id, quantity=qty, min_quantity=seuil, location=location
                )
                db.add(item)

        db.commit()

    print(f"âœ… {len(inventory_data)} articles ajoutÃ©s Ã  l'inventaire")


def seed_batch_meals():
    """Planifie des repas"""
    print("ðŸ½ï¸ Planification de repas...")

    with obtenir_contexte_db() as db:
        today = date.today()

        # RÃ©cupÃ©rer les recettes
        recettes = db.query(Recette).all()

        for i, recette in enumerate(recettes[:7]):  # 7 jours
            batch = RepasBatch(
                recette_id=recette.id,
                scheduled_date=today + timedelta(days=i),
                portions=4,
                status="TERMINE" if i < 2 else "A_FAIRE",
                ai_planned=(i % 2 == 0),
            )
            db.add(batch)

        db.commit()

    print("âœ… 7 repas planifiÃ©s")


def seed_child_and_family():
    """CrÃ©e Jules et ses donnÃ©es"""
    print("ðŸ‘¶ CrÃ©ation du profil de Jules...")

    with obtenir_contexte_db() as db:
        # Jules
        jules = ProfilEnfant(
            name="Jules", birth_date=date(2024, 6, 22), notes="Notre petit bout de chou â¤ï¸"
        )
        db.add(jules)
        db.flush()

        # EntrÃ©es bien-Ãªtre
        for i in range(7):
            entry = EntreeBienEtre(
                child_id=jules.id,
                date=date.today() - timedelta(days=i),
                mood=["ðŸ˜Š BIEN", "ðŸ˜ MOYEN", "ðŸ˜Š BIEN"][i % 3],
                sleep_hours=7.5 + (i % 3) * 0.5,
                activity=["CrÃ¨che", "Promenade", "Jeux Ã  la maison"][i % 3],
                notes=f"JournÃ©e du {(date.today() - timedelta(days=i)).strftime('%d/%m')}",
            )
            db.add(entry)

        # Routine
        routine = Routine(
            child_id=jules.id,
            name="Routine du soir",
            description="Routine avant le coucher",
            frequency="quotidien",
            is_active=True,
        )
        db.add(routine)
        db.flush()

        # TÃ¢ches de routine
        taches = [
            ("Bain", "19:00", "TERMINE"),
            ("DÃ®ner", "19:30", "TERMINE"),
            ("Brossage dents", "20:00", "A_FAIRE"),
            ("Histoire", "20:15", "A_FAIRE"),
            ("Dodo", "20:30", "A_FAIRE"),
        ]

        for nom, heure, statut in taches:
            task = TacheRoutine(
                routine_id=routine.id, task_name=nom, scheduled_time=heure, status=statut
            )
            db.add(task)

        db.commit()

    print("âœ… Jules et sa routine crÃ©Ã©s")


def seed_projects():
    """CrÃ©e des projets maison"""
    print("ðŸ—ï¸ CrÃ©ation des projets...")

    with obtenir_contexte_db() as db:
        # Projet 1
        p1 = Project(
            name="AmÃ©nagement jardin",
            description="CrÃ©er un potager et une zone dÃ©tente",
            category="ExtÃ©rieur",
            start_date=date(2025, 4, 1),
            end_date=date(2025, 12, 31),
            priority="HAUTE",
            status="EN_COURS",
            progress=35,
        )
        db.add(p1)
        db.flush()

        db.add_all(
            [
                TacheProjet(
                    project_id=p1.id,
                    task_name="PrÃ©parer le sol",
                    status="TERMINE",
                    due_date=date(2025, 4, 15),
                ),
                TacheProjet(
                    project_id=p1.id,
                    task_name="Acheter graines",
                    status="TERMINE",
                    due_date=date(2025, 5, 1),
                ),
                TacheProjet(
                    project_id=p1.id,
                    task_name="Planter lÃ©gumes",
                    status="EN_COURS",
                    due_date=date(2025, 5, 15),
                ),
                TacheProjet(
                    project_id=p1.id,
                    task_name="Installer arrosage",
                    status="A_FAIRE",
                    due_date=date(2025, 6, 1),
                ),
            ]
        )

        # Projet 2
        p2 = Project(
            name="RÃ©novation chambre",
            description="Refaire la peinture et changer les meubles",
            category="IntÃ©rieur",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            priority="MOYENNE",
            status="A_FAIRE",
            progress=0,
        )
        db.add(p2)
        db.flush()

        db.add_all(
            [
                TacheProjet(project_id=p2.id, task_name="Choisir couleurs", status="A_FAIRE"),
                TacheProjet(project_id=p2.id, task_name="Acheter peinture", status="A_FAIRE"),
            ]
        )

        db.commit()

    print("âœ… 2 projets crÃ©Ã©s")


def seed_garden():
    """CrÃ©e le jardin"""
    print("ðŸŒ± Plantation du jardin...")

    with obtenir_contexte_db() as db:
        plantes = [
            ("Tomates cerises", "LÃ©gume", date(2025, 5, 1), date(2025, 8, 1), 3, 2),
            ("Courgettes", "LÃ©gume", date(2025, 5, 10), date(2025, 7, 15), 2, 3),
            ("Basilic", "Aromatique", date(2025, 4, 20), None, 1, 1),
            ("Fraisiers", "Fruit", date(2025, 4, 1), date(2025, 6, 15), 5, 2),
        ]

        for nom, cat, plant, harvest, qty, water_freq in plantes:
            item = ElementJardin(
                name=nom,
                category=cat,
                planting_date=plant,
                harvest_date=harvest,
                quantity=qty,
                watering_frequency_days=water_freq,
                last_watered=date.today() - timedelta(days=1),
            )
            db.add(item)
            db.flush()

            # Ajouter un log
            log = JournalJardin(
                item_id=item.id,
                action="Arrosage",
                date=date.today() - timedelta(days=1),
                notes="Arrosage rÃ©gulier",
            )
            db.add(log)

        db.commit()

    print("âœ… 4 plantes ajoutÃ©es au jardin")


def seed_notifications(user_id: int):
    """CrÃ©e des notifications"""
    print("ðŸ”” CrÃ©ation de notifications...")

    with obtenir_contexte_db() as db:
        notifs = [
            ("Inventaire", "Stock bas : Lait, Fromage rÃ¢pÃ©", "HAUTE", False),
            ("Batch Cooking", "Aucun repas planifiÃ© pour aprÃ¨s-demain", "MOYENNE", False),
            ("Routines", "2 tÃ¢ches du soir en attente", "BASSE", False),
            ("Jardin", "Les tomates ont besoin d'eau", "MOYENNE", True),
        ]

        for module, message, priority, read in notifs:
            notif = Notification(
                user_id=user_id, module=module, message=message, priority=priority, read=read
            )
            db.add(notif)

        db.commit()

    print(f"âœ… {len(notifs)} notifications crÃ©Ã©es")


def main():
    """Point d'entrÃ©e principal"""
    print("=" * 60)
    print("ðŸŒ± SEED DATABASE - Assistant MaTanne v2")
    print("=" * 60)
    print()

    # Demander confirmation pour nettoyer
    response = input("âš ï¸  Nettoyer la base avant (supprime toutes les donnÃ©es) ? (o/N) : ")

    if response.lower() in ["o", "oui", "y", "yes"]:
        clear_database()
        print()

    # Seed
    user_id = seed_users()
    seed_ingredients()
    seed_recipes()
    seed_inventory()
    seed_batch_meals()
    seed_child_and_family()
    seed_projects()
    seed_garden()
    seed_notifications(user_id)

    print()
    print("=" * 60)
    print("âœ… SEED TERMINÃ‰ AVEC SUCCÃˆS")
    print("=" * 60)
    print()
    print("ðŸ“Š RÃ©sumÃ© des donnÃ©es crÃ©Ã©es :")
    print("  â€¢ 1 utilisateur (Anne)")
    print("  â€¢ 2 profils (Anne, Mathieu)")
    print("  â€¢ 26 ingrÃ©dients")
    print("  â€¢ 4 recettes (dont 1 IA)")
    print("  â€¢ 11 articles en inventaire")
    print("  â€¢ 7 repas planifiÃ©s")
    print("  â€¢ 1 enfant (Jules)")
    print("  â€¢ 7 entrÃ©es bien-Ãªtre")
    print("  â€¢ 1 routine (5 tÃ¢ches)")
    print("  â€¢ 2 projets (6 tÃ¢ches)")
    print("  â€¢ 4 plantes au jardin")
    print("  â€¢ 4 notifications")
    print()
    print("ðŸš€ Tu peux maintenant lancer l'application !")
    print("   poetry run streamlit run src/app.py")
    print()


if __name__ == "__main__":
    main()
