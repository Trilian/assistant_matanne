# -*- coding: utf-8 -*-
"""
Configuration specifique pour les tests d'integration.

Les tests d'integration utilisent une vraie base de donnees SQLite
et testent les workflows complets entre plusieurs composants.

Execution: pytest tests/integration/ -m integration
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, patch

from src.core.models import (
    Base,
    Recette,
    Ingredient,
    RecetteIngredient,
    EtapeRecette,
    ArticleInventaire,
    Planning,
    Repas,
    ArticleCourses,
    Routine,
    RoutineTask,
    WellbeingEntry,
    Project,
    ProjectTask,
    GardenItem,
    GardenLog,
    ChildProfile,
)


# =====================================================
# FIXTURES BASE DE DONNEES INTEGRATION
# =====================================================


@pytest.fixture(scope="module")
def integration_engine():
    """Moteur de base de donnees pour tests d'integration."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
        poolclass=StaticPool,
    )
    
    # Patch JSONB -> JSON pour SQLite
    from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
    original_process = SQLiteTypeCompiler.process
    
    def patched_process(self, type_, **kw):
        from sqlalchemy.dialects.postgresql import JSONB
        if isinstance(type_, JSONB):
            return "JSON"
        return original_process(self, type_, **kw)
    
    SQLiteTypeCompiler.process = patched_process
    
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        except Exception:
            pass
        cursor.close()
    
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def int_db(integration_engine):
    """Session de base de donnees pour tests d'integration."""
    connection = integration_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


# =====================================================
# MOCKS IA (eviter appels reels)
# =====================================================


@pytest.fixture(autouse=True)
def mock_ia_client():
    """Mock automatique du client IA pour tous les tests d'integration."""
    with patch("src.core.ai.obtenir_client_ia") as mock:
        client = MagicMock()
        client.chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='{"items": []}'))]
        )
        mock.return_value = client
        yield client


# =====================================================
# FIXTURES DONNEES DE BASE (Cuisine)
# =====================================================


@pytest.fixture
def ingredients_base(int_db):
    """Cree un ensemble d'ingredients de base pour les tests."""
    ingredients = [
        Ingredient(nom="Poulet", unite="kg", categorie="Proteines"),
        Ingredient(nom="Tomates", unite="kg", categorie="Legumes"),
        Ingredient(nom="Oignons", unite="pcs", categorie="Legumes"),
        Ingredient(nom="Riz", unite="kg", categorie="Feculents"),
        Ingredient(nom="Pates", unite="kg", categorie="Feculents"),
        Ingredient(nom="Lait", unite="L", categorie="Laitier"),
        Ingredient(nom="Beurre", unite="g", categorie="Laitier"),
        Ingredient(nom="Huile olive", unite="L", categorie="Condiments"),
        Ingredient(nom="Sel", unite="g", categorie="Condiments"),
        Ingredient(nom="Poivre", unite="g", categorie="Condiments"),
    ]
    for ing in ingredients:
        int_db.add(ing)
    int_db.commit()
    
    return {ing.nom: ing for ing in ingredients}


@pytest.fixture
def recettes_base(int_db, ingredients_base):
    """Cree un ensemble de recettes de base avec ingredients."""
    # Recette 1: Poulet roti
    poulet_roti = Recette(
        nom="Poulet roti aux herbes",
        description="Delicieux poulet roti dore",
        temps_preparation=20,
        temps_cuisson=90,
        portions=6,
        difficulte="facile",
        type_repas="diner",
        saison="toute_saison",
    )
    int_db.add(poulet_roti)
    int_db.flush()
    
    int_db.add(RecetteIngredient(
        recette_id=poulet_roti.id,
        ingredient_id=ingredients_base["Poulet"].id,
        quantite=1.5,
        unite="kg"
    ))
    int_db.add(RecetteIngredient(
        recette_id=poulet_roti.id,
        ingredient_id=ingredients_base["Beurre"].id,
        quantite=50,
        unite="g"
    ))
    
    # Recette 2: Pates tomate
    pates_tomate = Recette(
        nom="Pates sauce tomate",
        description="Pates italiennes classiques",
        temps_preparation=10,
        temps_cuisson=20,
        portions=4,
        difficulte="facile",
        type_repas="diner",
        saison="toute_saison",
    )
    int_db.add(pates_tomate)
    int_db.flush()
    
    int_db.add(RecetteIngredient(
        recette_id=pates_tomate.id,
        ingredient_id=ingredients_base["Pates"].id,
        quantite=500,
        unite="g"
    ))
    int_db.add(RecetteIngredient(
        recette_id=pates_tomate.id,
        ingredient_id=ingredients_base["Tomates"].id,
        quantite=400,
        unite="g"
    ))
    
    # Recette 3: Riz au poulet
    riz_poulet = Recette(
        nom="Riz au poulet",
        description="Riz savoureux cuit avec poulet",
        temps_preparation=15,
        temps_cuisson=30,
        portions=4,
        difficulte="moyen",
        type_repas="dejeuner",
        saison="toute_saison",
    )
    int_db.add(riz_poulet)
    int_db.flush()
    
    int_db.add(RecetteIngredient(
        recette_id=riz_poulet.id,
        ingredient_id=ingredients_base["Riz"].id,
        quantite=300,
        unite="g"
    ))
    int_db.add(RecetteIngredient(
        recette_id=riz_poulet.id,
        ingredient_id=ingredients_base["Poulet"].id,
        quantite=500,
        unite="g"
    ))
    
    int_db.commit()
    
    return {
        "poulet_roti": poulet_roti,
        "pates_tomate": pates_tomate,
        "riz_poulet": riz_poulet,
    }


@pytest.fixture
def inventaire_base(int_db, ingredients_base):
    """Cree un inventaire de base avec differents etats."""
    articles = [
        ArticleInventaire(
            ingredient_id=ingredients_base["Riz"].id,
            quantite=2.0,
            quantite_min=0.5,
            emplacement="Placard",
        ),
        ArticleInventaire(
            ingredient_id=ingredients_base["Pates"].id,
            quantite=0.3,
            quantite_min=0.5,
            emplacement="Placard",
        ),
        ArticleInventaire(
            ingredient_id=ingredients_base["Lait"].id,
            quantite=0.2,
            quantite_min=1.0,
            emplacement="Frigo",
        ),
        ArticleInventaire(
            ingredient_id=ingredients_base["Beurre"].id,
            quantite=200,
            quantite_min=100,
            emplacement="Frigo",
            date_peremption=date.today() + timedelta(days=3),
        ),
    ]
    for article in articles:
        int_db.add(article)
    int_db.commit()
    
    return articles


# =====================================================
# FIXTURES DONNEES DE BASE (Famille)
# =====================================================


@pytest.fixture
def routines_base(int_db):
    """Cree des routines familiales de base."""
    routines = []
    
    routine_matin = Routine(
        nom="Routine matinale",
        description="Preparer la journee",
        frequence="quotidien",
        categorie="matin",
        actif=True,
    )
    int_db.add(routine_matin)
    int_db.flush()
    
    taches_matin = [
        RoutineTask(routine_id=routine_matin.id, nom="Reveil", ordre=1),
        RoutineTask(routine_id=routine_matin.id, nom="Petit-dejeuner", ordre=2),
        RoutineTask(routine_id=routine_matin.id, nom="Douche", ordre=3),
        RoutineTask(routine_id=routine_matin.id, nom="Habillage", ordre=4),
    ]
    for tache in taches_matin:
        int_db.add(tache)
    
    routines.append(routine_matin)
    
    routine_soir = Routine(
        nom="Routine du soir Jules",
        description="Coucher de Jules",
        frequence="quotidien",
        categorie="soir",
        actif=True,
    )
    int_db.add(routine_soir)
    int_db.flush()
    
    taches_soir = [
        RoutineTask(routine_id=routine_soir.id, nom="Bain", ordre=1),
        RoutineTask(routine_id=routine_soir.id, nom="Pyjama", ordre=2),
        RoutineTask(routine_id=routine_soir.id, nom="Histoire", ordre=3),
        RoutineTask(routine_id=routine_soir.id, nom="Dodo", ordre=4),
    ]
    for tache in taches_soir:
        int_db.add(tache)
    
    routines.append(routine_soir)
    int_db.commit()
    
    return routines


@pytest.fixture
def wellbeing_base(int_db):
    """Cree des entrees de bien-etre familial."""
    entrees = [
        WellbeingEntry(
            date=date.today() - timedelta(days=2),
            mood="bon",
            activity="Visite pediatre",
            notes="Bilan de sante de Jules - tout va bien!",
        ),
        WellbeingEntry(
            date=date.today() - timedelta(days=1),
            mood="excellent",
            activity="Premier mot",
            notes="Jules a dit papa clairement!",
        ),
        WellbeingEntry(
            date=date.today(),
            mood="neutre",
            activity="Nouveau legume",
            notes="Jules a goute les epinards - pas fan",
        ),
    ]
    for entree in entrees:
        int_db.add(entree)
    int_db.commit()
    
    return entrees


@pytest.fixture
def child_profile(int_db):
    """Cree un profil d'enfant (Jules)."""
    jules = ChildProfile(
        name="Jules",
        date_of_birth=date.today() - timedelta(days=19*30),
        notes="Notre petit Jules",
    )
    int_db.add(jules)
    int_db.commit()
    return jules


# =====================================================
# FIXTURES DONNEES DE BASE (Maison)
# =====================================================


@pytest.fixture
def projets_maison(int_db):
    """Cree des projets maison de base."""
    projets = []
    
    projet_peinture = Project(
        nom="Repeindre chambre Jules",
        description="Refaire la peinture de la chambre en bleu ciel",
        priorite="haute",
        statut="en_cours",
        date_debut=date.today() - timedelta(days=5),
        date_fin_prevue=date.today() + timedelta(days=10),
    )
    int_db.add(projet_peinture)
    int_db.flush()
    
    taches_peinture = [
        ProjectTask(project_id=projet_peinture.id, nom="Acheter peinture", statut="termine"),
        ProjectTask(project_id=projet_peinture.id, nom="Proteger meubles", statut="termine"),
        ProjectTask(project_id=projet_peinture.id, nom="Premiere couche", statut="en_cours"),
        ProjectTask(project_id=projet_peinture.id, nom="Deuxieme couche", statut="a_faire"),
    ]
    for tache in taches_peinture:
        int_db.add(tache)
    
    projets.append(projet_peinture)
    
    projet_jardin = Project(
        nom="Amenager potager",
        description="Creer un petit potager dans le jardin",
        priorite="moyenne",
        statut="planifie",
        date_debut=date.today() + timedelta(days=30),
        date_fin_prevue=date.today() + timedelta(days=60),
    )
    int_db.add(projet_jardin)
    projets.append(projet_jardin)
    
    int_db.commit()
    return projets


@pytest.fixture
def potager_base(int_db):
    """Cree des plantes du potager."""
    plantes = [
        GardenItem(
            nom="Tomates cerises",
            type="legume",
            location="Potager nord",
            date_plantation=date.today() - timedelta(days=30),
        ),
        GardenItem(
            nom="Basilic",
            type="aromatique",
            location="Jardiniere cuisine",
            date_plantation=date.today() - timedelta(days=15),
        ),
        GardenItem(
            nom="Courgettes",
            type="legume",
            location="Potager sud",
            date_plantation=date.today() - timedelta(days=20),
        ),
    ]
    for plante in plantes:
        int_db.add(plante)
    int_db.commit()
    
    return plantes


# =====================================================
# FIXTURES DONNEES DE BASE (Planning)
# =====================================================


@pytest.fixture
def planning_semaine(int_db, recettes_base):
    """Cree un planning de semaine avec des repas."""
    today = date.today()
    debut_semaine = today - timedelta(days=today.weekday())
    fin_semaine = debut_semaine + timedelta(days=6)
    
    planning = Planning(
        nom=f"Semaine du {debut_semaine.strftime('%d/%m')}",
        semaine_debut=debut_semaine,
        semaine_fin=fin_semaine,
        actif=True,
    )
    int_db.add(planning)
    int_db.flush()
    
    # Creer des repas pour la semaine
    recettes = list(recettes_base.values())
    repas_crees = []
    
    for i in range(5):  # 5 jours
        date_repas = debut_semaine + timedelta(days=i)
        for j, type_repas in enumerate(["dejeuner", "diner"]):
            repas = Repas(
                planning_id=planning.id,
                date_repas=date_repas,
                type_repas=type_repas,
                recette_id=recettes[(i + j) % len(recettes)].id,
                portion_ajustee=4,
            )
            int_db.add(repas)
            repas_crees.append(repas)
    
    int_db.commit()
    
    return {
        "planning": planning,
        "repas": repas_crees,
    }
