"""
Tests unitaires pour users.py

Module: src.core.models.users
"""

from src.core.models.users import (
    ProfilUtilisateur,
    GarminToken,
    GarminActivityType,
    CategorieAchat,
    PrioriteAchat,
    ActiviteWeekend,
)
from src.core.models.famille import AchatFamille


class TestUsers:
    """Tests pour le module users."""

    class TestGarminActivityType:
        """Tests pour la classe GarminActivityType."""

        def test_garminactivitytype_creation(self):
            assert GarminActivityType.RUNNING == "running"
            assert GarminActivityType.CYCLING == "cycling"

        def test_garminactivitytype_est_str_enum(self):
            assert isinstance(GarminActivityType.RUNNING, str)

    class TestPurchaseCategory:
        """Tests pour la classe CategorieAchat."""

        def test_purchasecategory_creation(self):
            assert CategorieAchat.JULES_VETEMENTS == "jules_vetements"
            assert CategorieAchat.MAISON == "maison"

        def test_purchasecategory_est_str_enum(self):
            assert isinstance(CategorieAchat.JULES_VETEMENTS, str)

    class TestPurchasePriority:
        """Tests pour la classe PrioriteAchat."""

        def test_purchasepriority_creation(self):
            assert PrioriteAchat.URGENT == "urgent"
            assert PrioriteAchat.BASSE == "basse"

        def test_purchasepriority_ordre(self):
            valeurs = [p.value for p in PrioriteAchat]
            assert "urgent" in valeurs
            assert "optionnel" in valeurs

    class TestUserProfile:
        """Tests pour la classe ProfilUtilisateur."""

        def test_userprofile_creation(self):
            profil = ProfilUtilisateur(
                username="anne",
                display_name="Anne",
                email="anne@test.com",
            )
            assert profil.username == "anne"
            assert profil.display_name == "Anne"
            assert profil.email == "anne@test.com"

        def test_userprofile_tablename(self):
            assert ProfilUtilisateur.__tablename__ == "profils_utilisateurs"

    class TestGarminToken:
        """Tests pour la classe GarminToken."""

        def test_garmintoken_creation(self):
            token = GarminToken(
                user_id=1,
                oauth_token="token123",
                oauth_token_secret="secret456",
            )
            assert token.oauth_token == "token123"
            assert token.oauth_token_secret == "secret456"

        def test_garmintoken_tablename(self):
            assert GarminToken.__tablename__ == "garmin_tokens"

    class TestActiviteWeekend:
        """Tests pour la classe ActiviteWeekend."""

        def test_activite_weekend_creation(self):
            act = ActiviteWeekend(
                titre="Parc aventure",
                type_activite="sortie",
                statut="planifie",
            )
            assert act.titre == "Parc aventure"
            assert act.type_activite == "sortie"

    class TestAchatFamille:
        """Tests pour la classe AchatFamille."""

        def test_achat_famille_creation(self):
            achat = AchatFamille(
                nom="Poussette",
                categorie="jules_equipement",
                priorite="haute",
            )
            assert achat.nom == "Poussette"
            assert achat.achete is False or achat.achete is None
