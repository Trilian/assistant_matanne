"""
Tests unitaires pour accueil_logic.py
Module de logique métier séparé de l'UI
"""

import pytest
from datetime import datetime, date, timedelta

from src.modules.famille.accueil_logic import (
    # Constantes
    JULIUS_BIRTHDAY,
    NOTIFICATION_TYPES,
    DASHBOARD_SECTIONS,
    # Calculs Julius
    calculer_age_julius,
    calculer_semaines_julius,
    formater_age_julius,
    # Métriques Dashboard
    calculer_metriques_recettes,
    calculer_metriques_inventaire,
    calculer_metriques_courses,
    calculer_metriques_planning,
    calculer_metriques_globales,
    # Notifications
    generer_notifications_inventaire,
    generer_notifications_courses,
    generer_notifications_planning,
    generer_notifications_globales,
    compter_notifications_par_type,
    filtrer_notifications,
    # Activités récentes
    formater_activite_recente,
    calculer_temps_ecoule,
    trier_activites_par_date,
    # Suggestions
    generer_suggestions_actions,
    # Formatage Dashboard
    formater_metrique_card,
    generer_cartes_metriques,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def sample_recettes():
    """Recettes de test"""
    maintenant = datetime.now()
    return [
        {
            "nom": "Tarte aux pommes",
            "favori": True,
            "temps_preparation": 45,
            "derniere_utilisation": maintenant - timedelta(days=2),
        },
        {
            "nom": "Pâtes carbonara",
            "favori": False,
            "temps_preparation": 30,
            "derniere_utilisation": maintenant - timedelta(days=10),
        },
        {
            "nom": "Soupe de légumes",
            "favori": True,
            "temps_preparation": 60,
            "derniere_utilisation": None,
        },
    ]


@pytest.fixture
def sample_inventaire():
    """Inventaire de test"""
    aujourd_hui = date.today()
    return [
        {
            "ingredient_nom": "Lait",
            "quantite": 2,
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": aujourd_hui + timedelta(days=3),
            "prix_unitaire": 1.5,
        },
        {
            "ingredient_nom": "Poulet",
            "quantite": 0,
            "seuil_alerte": 2,
            "seuil_critique": 1,
            "date_peremption": aujourd_hui - timedelta(days=1),  # Périmé
            "prix_unitaire": 8.0,
        },
        {
            "ingredient_nom": "Farine",
            "quantite": 10,
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": aujourd_hui + timedelta(days=180),
            "prix_unitaire": 2.0,
        },
    ]


@pytest.fixture
def sample_courses():
    """Listes de courses de test"""
    return [
        {
            "nom": "Courses semaine",
            "archivee": False,
            "articles": [
                {"nom": "Pommes", "achete": False, "priorite": "haute"},
                {"nom": "Pain", "achete": True, "priorite": "moyenne"},
                {"nom": "Lait", "achete": False, "priorite": "haute"},
            ]
        },
        {
            "nom": "Courses anciennes",
            "archivee": True,
            "articles": [
                {"nom": "Sel", "achete": True, "priorite": "basse"},
            ]
        },
    ]


@pytest.fixture
def sample_planning():
    """Planning de test"""
    aujourd_hui = date.today()
    return [
        {"titre": "Médecin", "date": aujourd_hui},
        {"titre": "Course", "date": aujourd_hui + timedelta(days=1)},
        {"titre": "Fête", "date": aujourd_hui + timedelta(days=10)},
    ]


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════

class TestConstantes:
    """Tests pour les constantes"""
    
    def test_julius_birthday_is_date(self):
        """La date de naissance de Julius est une date"""
        assert isinstance(JULIUS_BIRTHDAY, date)
        assert JULIUS_BIRTHDAY.year == 2023
        assert JULIUS_BIRTHDAY.month == 10
    
    def test_notification_types_complete(self):
        """Types de notifications complets"""
        types_attendus = ["critique", "alerte", "info", "succes"]
        for t in types_attendus:
            assert t in NOTIFICATION_TYPES
            assert "emoji" in NOTIFICATION_TYPES[t]
            assert "color" in NOTIFICATION_TYPES[t]
    
    def test_dashboard_sections_not_empty(self):
        """Sections du dashboard définies"""
        assert len(DASHBOARD_SECTIONS) > 0
        assert "metriques" in DASHBOARD_SECTIONS


# ═══════════════════════════════════════════════════════════
# TESTS CALCULS JULIUS
# ═══════════════════════════════════════════════════════════

class TestCalculsJulius:
    """Tests pour les calculs liés à Julius"""
    
    def test_calculer_age_julius_structure(self):
        """Structure du résultat"""
        result = calculer_age_julius()
        
        assert "mois" in result
        assert "jours" in result
        assert "total_jours" in result
        assert "date_naissance" in result
    
    def test_calculer_age_julius_avec_date(self):
        """Calcul avec date de référence"""
        # 2 mois après la naissance
        date_ref = date(2023, 12, 26)
        result = calculer_age_julius(date_ref)
        
        assert result["mois"] == 2
    
    def test_calculer_age_julius_jours_positifs(self):
        """Les jours sont positifs"""
        result = calculer_age_julius()
        
        assert result["mois"] >= 0
        assert result["jours"] >= 0
        assert result["total_jours"] >= 0
    
    def test_calculer_semaines_julius(self):
        """Calcul des semaines"""
        # 7 jours après = 1 semaine
        date_ref = JULIUS_BIRTHDAY + timedelta(days=7)
        assert calculer_semaines_julius(date_ref) == 1
        
        # 14 jours après = 2 semaines
        date_ref = JULIUS_BIRTHDAY + timedelta(days=14)
        assert calculer_semaines_julius(date_ref) == 2
    
    def test_formater_age_julius(self):
        """Formatage de l'âge"""
        result = formater_age_julius()
        
        assert "mois" in result
        # Devrait contenir des chiffres
        assert any(c.isdigit() for c in result)
    
    def test_formater_age_julius_zero_jours(self):
        """Formatage avec 0 jours"""
        # Exactement N mois
        date_ref = date(2024, 4, 26)  # 6 mois
        result = formater_age_julius(date_ref)
        
        assert "et" not in result  # Pas de "et X jours"
    
    def test_formater_age_julius_un_jour(self):
        """Formatage avec 1 jour"""
        date_ref = date(2024, 4, 27)  # 6 mois et 1 jour
        result = formater_age_julius(date_ref)
        
        assert "1 jour" in result  # Singulier


# ═══════════════════════════════════════════════════════════
# TESTS MÉTRIQUES
# ═══════════════════════════════════════════════════════════

class TestMetriques:
    """Tests pour les fonctions de métriques"""
    
    def test_calculer_metriques_recettes(self, sample_recettes):
        """Métriques des recettes"""
        result = calculer_metriques_recettes(sample_recettes)
        
        assert result["total"] == 3
        assert result["favoris"] == 2
        assert result["moyenne_temps"] == 45  # (45+30+60)/3
    
    def test_calculer_metriques_recettes_vide(self):
        """Métriques avec liste vide"""
        result = calculer_metriques_recettes([])
        
        assert result["total"] == 0
        assert result["favoris"] == 0
        assert result["moyenne_temps"] == 0
    
    def test_calculer_metriques_inventaire(self, sample_inventaire):
        """Métriques de l'inventaire"""
        result = calculer_metriques_inventaire(sample_inventaire)
        
        assert result["total"] == 3
        assert result["alertes"] >= 1  # Au moins le lait
        assert result["perimes"] >= 1  # Le poulet
        assert result["valeur_totale"] >= 0
    
    def test_calculer_metriques_inventaire_vide(self):
        """Métriques inventaire vide"""
        result = calculer_metriques_inventaire([])
        
        assert result["total"] == 0
        assert result["alertes"] == 0
        assert result["perimes"] == 0
    
    def test_calculer_metriques_courses(self, sample_courses):
        """Métriques des courses"""
        result = calculer_metriques_courses(sample_courses)
        
        assert result["listes_actives"] == 1  # Une non archivée
        assert result["articles_a_acheter"] == 2  # Pommes et Lait
        assert result["articles_achetes"] == 1  # Pain
    
    def test_calculer_metriques_courses_vide(self):
        """Métriques courses vides"""
        result = calculer_metriques_courses([])
        
        assert result["listes_actives"] == 0
        assert result["taux_completion"] == 0
    
    def test_calculer_metriques_planning(self, sample_planning):
        """Métriques du planning"""
        result = calculer_metriques_planning(sample_planning)
        
        assert result["total_evenements"] == 3
        assert result["aujourd_hui"] >= 1  # Au moins "Médecin"
    
    def test_calculer_metriques_planning_vide(self):
        """Métriques planning vide"""
        result = calculer_metriques_planning([])
        
        assert result["total_evenements"] == 0
        assert result["aujourd_hui"] == 0
    
    def test_calculer_metriques_globales(
        self, sample_recettes, sample_inventaire, sample_courses, sample_planning
    ):
        """Métriques globales"""
        result = calculer_metriques_globales(
            recettes=sample_recettes,
            inventaire=sample_inventaire,
            courses=sample_courses,
            planning=sample_planning
        )
        
        assert "julius" in result
        assert "recettes" in result
        assert "inventaire" in result
        assert "courses" in result
        assert "planning" in result
        assert "timestamp" in result


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATIONS
# ═══════════════════════════════════════════════════════════

class TestNotifications:
    """Tests pour les fonctions de notifications"""
    
    def test_generer_notifications_inventaire(self, sample_inventaire):
        """Génère notifications inventaire"""
        result = generer_notifications_inventaire(sample_inventaire)
        
        assert len(result) > 0
        # Devrait avoir notification pour le poulet (périmé + critique)
        assert any("Poulet" in n.get("titre", "") for n in result)
    
    def test_generer_notifications_inventaire_structure(self, sample_inventaire):
        """Structure des notifications"""
        result = generer_notifications_inventaire(sample_inventaire)
        
        if result:
            notif = result[0]
            assert "type" in notif
            assert "titre" in notif
            assert "message" in notif
            assert "module" in notif
            assert "priorite" in notif
    
    def test_generer_notifications_courses(self, sample_courses):
        """Génère notifications courses"""
        result = generer_notifications_courses(sample_courses)
        
        # Devrait avoir notification pour articles haute priorité
        assert any("urgents" in n.get("titre", "").lower() for n in result)
    
    def test_generer_notifications_planning(self, sample_planning):
        """Génère notifications planning"""
        result = generer_notifications_planning(sample_planning)
        
        # Devrait mentionner l'événement d'aujourd'hui
        assert len(result) >= 1
    
    def test_generer_notifications_globales(
        self, sample_inventaire, sample_courses, sample_planning
    ):
        """Notifications globales triées"""
        result = generer_notifications_globales(
            inventaire=sample_inventaire,
            courses=sample_courses,
            planning=sample_planning
        )
        
        # Triées par priorité
        if len(result) > 1:
            assert result[0].get("priorite", 99) <= result[-1].get("priorite", 99)
    
    def test_compter_notifications_par_type(self):
        """Compte par type"""
        notifications = [
            {"type": "critique"},
            {"type": "critique"},
            {"type": "alerte"},
            {"type": "info"},
        ]
        
        result = compter_notifications_par_type(notifications)
        
        assert result["critique"] == 2
        assert result["alerte"] == 1
        assert result["info"] == 1
    
    def test_filtrer_notifications(self):
        """Filtre par type"""
        notifications = [
            {"type": "critique", "titre": "A"},
            {"type": "alerte", "titre": "B"},
            {"type": "info", "titre": "C"},
        ]
        
        result = filtrer_notifications(notifications, "critique")
        
        assert len(result) == 1
        assert result[0]["titre"] == "A"
    
    def test_filtrer_notifications_tous(self):
        """Filtre 'tous' retourne tout"""
        notifications = [{"type": "critique"}, {"type": "alerte"}]
        
        result = filtrer_notifications(notifications, "tous")
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS ACTIVITÉS RÉCENTES
# ═══════════════════════════════════════════════════════════

class TestActivitesRecentes:
    """Tests pour les fonctions d'activités récentes"""
    
    def test_formater_activite_recente(self):
        """Formatage d'une activité"""
        activite = {
            "type": "recette",
            "titre": "Ajout tarte",
            "description": "Nouvelle recette",
            "timestamp": datetime.now() - timedelta(hours=2),
        }
        
        result = formater_activite_recente(activite)
        
        assert result["icone"] == "🍳"  # Icône recette
        assert result["titre"] == "Ajout tarte"
        assert "ago" in result
    
    def test_formater_activite_recente_type_inconnu(self):
        """Type inconnu utilise icône par défaut"""
        activite = {"type": "inconnu", "titre": "Test"}
        
        result = formater_activite_recente(activite)
        assert result["icone"] == "📝"  # Icône par défaut
    
    def test_calculer_temps_ecoule_secondes(self):
        """Temps écoulé en secondes"""
        timestamp = datetime.now() - timedelta(seconds=30)
        result = calculer_temps_ecoule(timestamp)
        
        assert "instant" in result.lower()
    
    def test_calculer_temps_ecoule_minutes(self):
        """Temps écoulé en minutes"""
        timestamp = datetime.now() - timedelta(minutes=15)
        result = calculer_temps_ecoule(timestamp)
        
        assert "min" in result
    
    def test_calculer_temps_ecoule_heures(self):
        """Temps écoulé en heures"""
        timestamp = datetime.now() - timedelta(hours=3)
        result = calculer_temps_ecoule(timestamp)
        
        assert "h" in result
    
    def test_calculer_temps_ecoule_hier(self):
        """Temps écoulé = hier"""
        timestamp = datetime.now() - timedelta(days=1)
        result = calculer_temps_ecoule(timestamp)
        
        assert "hier" in result.lower()
    
    def test_calculer_temps_ecoule_jours(self):
        """Temps écoulé en jours"""
        timestamp = datetime.now() - timedelta(days=5)
        result = calculer_temps_ecoule(timestamp)
        
        assert "jours" in result
    
    def test_calculer_temps_ecoule_semaine_plus(self):
        """Temps écoulé > 7 jours"""
        timestamp = datetime.now() - timedelta(days=10)
        result = calculer_temps_ecoule(timestamp)
        
        assert "/" in result  # Format date
    
    def test_calculer_temps_ecoule_none(self):
        """Timestamp None"""
        result = calculer_temps_ecoule(None)
        assert "inconnue" in result.lower()
    
    def test_trier_activites_par_date(self):
        """Tri par date"""
        activites = [
            {"titre": "A", "timestamp": datetime.now() - timedelta(days=5)},
            {"titre": "B", "timestamp": datetime.now() - timedelta(hours=1)},
            {"titre": "C", "timestamp": datetime.now() - timedelta(days=2)},
        ]
        
        result = trier_activites_par_date(activites)
        
        assert result[0]["titre"] == "B"  # Plus récent
        assert result[-1]["titre"] == "A"  # Plus ancien
    
    def test_trier_activites_limit(self):
        """Limite du tri"""
        activites = [{"titre": str(i), "timestamp": datetime.now()} for i in range(20)]
        
        result = trier_activites_par_date(activites, limit=5)
        assert len(result) == 5


# ═══════════════════════════════════════════════════════════
# TESTS SUGGESTIONS
# ═══════════════════════════════════════════════════════════

class TestSuggestions:
    """Tests pour les fonctions de suggestions"""
    
    def test_generer_suggestions_actions(self):
        """Génère des suggestions d'actions"""
        metriques = {
            "inventaire": {"alertes": 10, "perimes": 2},
            "courses": {"articles_a_acheter": 15},
            "planning": {"aujourd_hui": 3},
        }
        
        result = generer_suggestions_actions(metriques, [])
        
        assert len(result) > 0
        # Devrait suggérer de gérer l'inventaire
        assert any("inventaire" in s.get("module", "") for s in result)
    
    def test_generer_suggestions_tri_priorite(self):
        """Suggestions triées par priorité"""
        metriques = {
            "inventaire": {"alertes": 10, "perimes": 5},
            "courses": {"articles_a_acheter": 20},
            "planning": {"aujourd_hui": 1},
        }
        
        result = generer_suggestions_actions(metriques, [])
        
        # Triées par priorité
        if len(result) > 1:
            assert result[0].get("priorite", 99) <= result[-1].get("priorite", 99)


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE DASHBOARD
# ═══════════════════════════════════════════════════════════

class TestFormatageDashboard:
    """Tests pour le formatage du dashboard"""
    
    def test_formater_metrique_card(self):
        """Formatage d'une carte métrique"""
        result = formater_metrique_card(
            titre="Test",
            valeur=42,
            unite="%",
            icone="📊"
        )
        
        assert result["titre"] == "Test"
        assert result["valeur"] == 42
        assert result["unite"] == "%"
        assert result["display"] == "42%"
    
    def test_formater_metrique_card_sans_unite(self):
        """Carte sans unité"""
        result = formater_metrique_card("Test", 42)
        
        assert result["display"] == "42"
    
    def test_generer_cartes_metriques(self):
        """Génère les cartes métriques"""
        metriques = {
            "julius": {"mois": 19, "jours": 5},
            "recettes": {"total": 25},
            "inventaire": {"alertes": 3},
            "courses": {"articles_a_acheter": 8},
        }
        
        result = generer_cartes_metriques(metriques)
        
        assert len(result) == 4
        
        # Vérifie les titres
        titres = [c["titre"] for c in result]
        assert "Julius" in titres
        assert "Recettes" in titres


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════

class TestEdgeCases:
    """Tests pour les cas limites"""
    
    def test_notifications_liste_vide(self):
        """Notifications avec listes vides"""
        result = generer_notifications_globales([], [], [])
        assert isinstance(result, list)
    
    def test_metriques_globales_none(self):
        """Métriques avec None"""
        result = calculer_metriques_globales()
        
        # Devrait retourner des valeurs par défaut
        assert result["recettes"]["total"] == 0
        assert result["inventaire"]["total"] == 0
    
    def test_activites_sans_timestamp(self):
        """Activité sans timestamp"""
        activites = [
            {"titre": "A", "timestamp": None},
            {"titre": "B", "timestamp": datetime.now()},
        ]
        
        result = trier_activites_par_date(activites)
        # Ne doit pas crasher
        assert len(result) == 2
    
    def test_inventaire_date_datetime(self):
        """Date de péremption en datetime"""
        inventaire = [{
            "ingredient_nom": "Test",
            "quantite": 1,
            "seuil_alerte": 5,
            "seuil_critique": 2,
            "date_peremption": datetime.now() - timedelta(days=1),  # datetime, pas date
            "prix_unitaire": 1.0,
        }]
        
        result = calculer_metriques_inventaire(inventaire)
        assert result["perimes"] == 1
