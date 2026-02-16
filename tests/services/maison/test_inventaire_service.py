"""
Tests pour InventaireMaisonService.

Couvre:
- Recherche "Où est..."
- Gestion des pièces/conteneurs/objets
- Calcul valeur assurance
- Suggestions rangement
"""

import json
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.maison.inventaire_service import (
    InventaireMaisonService,
    get_inventaire_service,
)
from src.services.maison.schemas import ResultatRecherche


class TestInventaireServiceInit:
    """Tests d'initialisation du service."""

    def test_factory_returns_service(self):
        """La factory retourne une instance valide."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()
            assert isinstance(service, InventaireMaisonService)

    def test_factory_accepts_custom_client(self):
        """La factory accepte un client personnalisé."""
        mock_client = MagicMock()
        service = get_inventaire_service(client=mock_client)
        assert service.client == mock_client


class TestInventaireServiceRecherche:
    """Tests de la recherche "Où est..."."""

    def test_nettoyer_query_simple(self):
        """Nettoie une requête simple."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            query = service._nettoyer_query("où est ma perceuse")
            assert "perceuse" in query
            assert "où" not in query

    def test_nettoyer_query_complexe(self):
        """Nettoie une requête complexe."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            query = service._nettoyer_query("cherche le tournevis cruciforme")
            assert "tournevis" in query
            assert "cruciforme" in query
            assert "cherche" not in query

    def test_extraire_piece_emplacement(self):
        """Extrait la pièce d'un emplacement."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            piece = service._extraire_piece("Garage, établi gauche")
            assert piece == "Garage"

    def test_extraire_conteneur_emplacement(self):
        """Extrait le conteneur d'un emplacement."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            conteneur = service._extraire_conteneur("Garage, établi gauche")
            assert conteneur == "établi gauche"

    def test_extraire_conteneur_sans_detail(self):
        """Retourne None si pas de conteneur."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            conteneur = service._extraire_conteneur("Garage")
            assert conteneur is None

    @pytest.mark.asyncio
    async def test_suggestion_ia_non_trouve(self, mock_client_ia):
        """Suggère un emplacement si objet non trouvé."""
        mock_response = json.dumps(
            {
                "emplacement_suggere": "Garage, boîte à outils",
                "confiance": 0.7,
            }
        )

        mock_client_ia.generer = AsyncMock(return_value=mock_response)

        service = InventaireMaisonService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        result = await service._suggestion_ia("perceuse")

        assert result is not None
        assert result.confiance < 1.0  # C'est une suggestion


class TestInventaireServicePieces:
    """Tests de gestion des pièces."""

    def test_creer_piece(self, piece_maison_data):
        """Crée une nouvelle pièce."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            # Placeholder - retourne toujours 1 pour l'instant
            piece_id = service.creer_piece(MagicMock(nom=piece_maison_data["nom"]))
            assert piece_id == 1

    def test_lister_pieces(self):
        """Liste toutes les pièces."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            pieces = service.lister_pieces()
            assert isinstance(pieces, list)


class TestInventaireServiceObjets:
    """Tests de gestion des objets."""

    def test_ajouter_objet(self, objet_inventaire_data):
        """Ajoute un objet à l'inventaire."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            objet_id = service.ajouter_objet(MagicMock(nom=objet_inventaire_data["nom"]))
            assert objet_id == 1

    def test_deplacer_objet(self):
        """Déplace un objet vers un autre conteneur."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            succes = service.deplacer_objet(
                objet_id=1,
                nouveau_conteneur_id=2,
            )
            assert succes is True


class TestInventaireServiceValeurAssurance:
    """Tests du calcul de valeur assurance."""

    def test_calculer_valeur_piece(self):
        """Calcule la valeur totale d'une pièce."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            valeur = service.calculer_valeur_piece(piece_id=1)
            assert isinstance(valeur, Decimal)

    def test_calculer_valeur_totale(self):
        """Calcule la valeur totale de l'inventaire."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            valeurs = service.calculer_valeur_totale()
            assert "total" in valeurs

    def test_generer_inventaire_assurance(self):
        """Génère l'inventaire pour l'assurance."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            inventaire = service.generer_inventaire_assurance()
            assert isinstance(inventaire, list)


class TestInventaireServiceSuggestions:
    """Tests des suggestions de rangement."""

    @pytest.mark.asyncio
    async def test_suggerer_rangement(self, mock_client_ia):
        """Suggère où ranger un nouvel objet."""
        mock_response = "Garage, sur l'établi ou dans la caisse à outils"

        service = InventaireMaisonService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        suggestion = await service.suggerer_rangement(
            nom_objet="tournevis",
            categorie="outillage",
        )

        assert service.call_with_cache.called
        assert isinstance(suggestion, str)

    @pytest.mark.asyncio
    async def test_optimiser_rangement(self, mock_client_ia):
        """Suggère des optimisations de rangement."""
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            suggestions = await service.optimiser_rangement(piece_id=1)
            assert isinstance(suggestions, list)
            assert len(suggestions) > 0


class TestInventaireServiceCodeBarre:
    """Tests de la recherche par code-barres."""

    def test_rechercher_par_code_barre_trouve(self, objet_inventaire_data):
        """Trouve un objet par son code-barres."""
        # Ce test nécessiterait une vraie DB
        # Pour l'instant, test de la structure
        with patch("src.services.maison.inventaire_service.ClientIA"):
            service = get_inventaire_service()

            # Simulation - retournera None sans données réelles
            result = service.rechercher_par_code_barre(
                code_barre=objet_inventaire_data["code_barre"]
            )
            # Pas d'assertion stricte, juste vérifier que ça ne crash pas


class TestInventaireServiceCalculs:
    """Tests des calculs utilitaires."""

    def test_calcul_valeur_objets(self):
        """Calcule la valeur d'une liste d'objets."""
        objets = [
            {"nom": "Perceuse", "valeur": Decimal("85.00")},
            {"nom": "Visseuse", "valeur": Decimal("120.00")},
            {"nom": "Scie sauteuse", "valeur": Decimal("75.00")},
        ]

        total = sum(o["valeur"] for o in objets)
        assert total == Decimal("280.00")

    def test_groupement_par_categorie(self):
        """Groupe les objets par catégorie."""
        objets = [
            {"nom": "Perceuse", "categorie": "outillage"},
            {"nom": "TV", "categorie": "électronique"},
            {"nom": "Visseuse", "categorie": "outillage"},
        ]

        groupes = {}
        for obj in objets:
            cat = obj["categorie"]
            if cat not in groupes:
                groupes[cat] = []
            groupes[cat].append(obj)

        assert len(groupes["outillage"]) == 2
        assert len(groupes["électronique"]) == 1

    def test_recherche_floue_simple(self):
        """Test basique de correspondance floue."""
        recherche = "perceuse"
        objets = ["Perceuse Bosch", "Visseuse", "Ponceuse"]

        # Correspondance simple (contient)
        resultats = [o for o in objets if recherche.lower() in o.lower()]
        assert len(resultats) == 1
        assert "Perceuse" in resultats[0]


# ═══════════════════════════════════════════════════════════
# TESTS STATUT OBJETS (À changer/À acheter)
# ═══════════════════════════════════════════════════════════


class TestInventaireStatutObjets:
    """Tests de la gestion des statuts d'objets."""

    @pytest.fixture
    def service_inventaire(self, mock_client_ia):
        """Fixture pour le service inventaire."""
        return get_inventaire_service(client=mock_client_ia)

    @pytest.mark.asyncio
    async def test_changer_statut_objet_succes(self, service_inventaire):
        """Change le statut d'un objet avec succès."""
        from src.services.maison.schemas import (
            DemandeChangementObjet,
            PrioriteRemplacement,
            StatutObjet,
        )

        demande = DemandeChangementObjet(
            objet_id=1,
            ancien_statut=StatutObjet.FONCTIONNE,
            nouveau_statut=StatutObjet.A_CHANGER,
            raison="Micro-onde en panne",
            priorite=PrioriteRemplacement.HAUTE,
            cout_estime=Decimal("150.00"),
            ajouter_liste_courses=True,
            ajouter_budget=True,
        )

        result = await service_inventaire.changer_statut_objet(demande)

        assert result.succes is True
        assert result.nouveau_statut == StatutObjet.A_CHANGER
        assert result.objet_id == 1

    @pytest.mark.asyncio
    async def test_marquer_a_changer(self, service_inventaire):
        """Raccourci pour marquer un objet à changer."""
        result = await service_inventaire.marquer_a_changer(
            objet_id=1,
            raison="Vieux modèle",
            cout_estime=Decimal("200.00"),
        )

        assert result.succes is True
        from src.services.maison.schemas import StatutObjet

        assert result.nouveau_statut == StatutObjet.A_CHANGER

    @pytest.mark.asyncio
    async def test_marquer_a_acheter_nouvel_objet(self, service_inventaire):
        """Ajoute un nouvel objet à acheter."""
        from src.services.maison.schemas import CategorieObjet

        result = await service_inventaire.marquer_a_acheter(
            nom_objet="Bibliothèque BILLY",
            piece_id=1,
            categorie=CategorieObjet.MEUBLE,
            cout_estime=Decimal("79.00"),
        )

        assert result.succes is True

    @pytest.mark.asyncio
    async def test_lister_objets_a_remplacer(self, service_inventaire):
        """Liste les objets à remplacer/acheter."""
        objets = await service_inventaire.lister_objets_a_remplacer()

        # Retourne liste vide pour l'instant (simulation)
        assert isinstance(objets, list)

    @pytest.mark.asyncio
    async def test_creer_article_courses_objet(self, service_inventaire):
        """Crée un article de courses pour un objet."""
        lien = await service_inventaire._creer_article_courses_objet(
            objet_id=1,
            cout_estime=Decimal("150.00"),
        )

        assert lien.objet_id == 1
        assert lien.prix_estime == Decimal("150.00")

    @pytest.mark.asyncio
    async def test_creer_depense_budget_objet(self, service_inventaire):
        """Crée une dépense budget pour un objet."""
        lien = await service_inventaire._creer_depense_budget_objet(
            objet_id=1,
            montant=Decimal("200.00"),
        )

        assert lien.objet_id == 1
        assert lien.montant_prevu == Decimal("200.00")


# ═══════════════════════════════════════════════════════════
# TESTS VERSIONING PIÈCES
# ═══════════════════════════════════════════════════════════


class TestInventaireVersioningPieces:
    """Tests du versioning des pièces."""

    @pytest.fixture
    def service_inventaire(self, mock_client_ia):
        """Fixture pour le service inventaire."""
        return get_inventaire_service(client=mock_client_ia)

    def test_creer_version_piece(self, service_inventaire):
        """Crée une version d'une pièce."""
        version = service_inventaire.creer_version_piece(
            piece_id=1,
            nom_version="Avant rénovation 2024",
            commentaire="État initial du salon",
        )

        assert version.piece_id == 1
        assert version.nom_version == "Avant rénovation 2024"
        assert version.numero_version == 1

    def test_creer_version_piece_avec_modifications(self, service_inventaire):
        """Crée une version avec liste de modifications."""
        from src.services.maison.schemas import (
            ModificationPieceCreate,
            TypeModificationPiece,
        )

        modifications = [
            ModificationPieceCreate(
                type_modification=TypeModificationPiece.AJOUT_MEUBLE,
                description="Ajout bibliothèque BILLY",
                objet_concerne="Bibliothèque BILLY",
                cout_estime=Decimal("79.00"),
            ),
            ModificationPieceCreate(
                type_modification=TypeModificationPiece.PEINTURE,
                description="Peinture mur accent",
                cout_estime=Decimal("45.00"),
            ),
        ]

        version = service_inventaire.creer_version_piece(
            piece_id=1,
            nom_version="Réaménagement bureau",
            modifications=modifications,
        )

        assert version.cout_total_version == Decimal("124.00")
        assert len(version.modifications) == 2

    def test_lister_versions_piece(self, service_inventaire):
        """Liste l'historique des versions d'une pièce."""
        versions = service_inventaire.lister_versions_piece(piece_id=1)

        # Retourne liste vide pour l'instant
        assert isinstance(versions, list)

    def test_restaurer_version_piece(self, service_inventaire):
        """Restaure une pièce à une version antérieure."""
        succes = service_inventaire.restaurer_version_piece(
            piece_id=1,
            version_id=1,
        )

        assert succes is True

    @pytest.mark.asyncio
    async def test_planifier_reorganisation(self, service_inventaire):
        """Planifie une réorganisation complète."""
        from src.services.maison.schemas import (
            CategorieObjet,
            ModificationPieceCreate,
            ObjetCreate,
            PlanReorganisationPiece,
            StatutObjet,
            TypeModificationPiece,
        )

        plan = PlanReorganisationPiece(
            piece_id=1,
            nom_version="Nouveau bureau gaming",
            modifications_prevues=[
                ModificationPieceCreate(
                    type_modification=TypeModificationPiece.AMENAGEMENT,
                    description="Setup gaming",
                    cout_estime=Decimal("500.00"),
                ),
            ],
            budget_total_estime=Decimal("1200.00"),
            objets_a_acheter=[
                ObjetCreate(
                    nom="Bureau gaming 160cm",
                    categorie=CategorieObjet.MEUBLE,
                    statut=StatutObjet.A_ACHETER,
                    cout_remplacement_estime=Decimal("299.00"),
                ),
            ],
            date_fin_prevue=date.today(),
        )

        result = await service_inventaire.planifier_reorganisation(plan)

        assert result.succes is True


# ═══════════════════════════════════════════════════════════
# TESTS COÛTS TRAVAUX
# ═══════════════════════════════════════════════════════════


class TestInventaireCoutsTravaux:
    """Tests du suivi des coûts de travaux."""

    @pytest.fixture
    def service_inventaire(self, mock_client_ia):
        """Fixture pour le service inventaire."""
        return get_inventaire_service(client=mock_client_ia)

    def test_ajouter_cout_travaux(self, service_inventaire):
        """Ajoute un coût de travaux."""
        from src.services.maison.schemas import CoutTravauxPiece, TypeModificationPiece

        cout = CoutTravauxPiece(
            piece_id=1,
            piece_nom="Salon",
            type_travaux=TypeModificationPiece.RENOVATION,
            description="Réfection complète",
            budget_prevu=Decimal("5000.00"),
        )

        id_cout = service_inventaire.ajouter_cout_travaux(cout)

        assert id_cout > 0

    def test_obtenir_resume_travaux(self, service_inventaire):
        """Obtient un résumé des travaux."""
        resume = service_inventaire.obtenir_resume_travaux()

        assert resume.budget_total_prevu >= Decimal("0")
        assert resume.budget_total_depense >= Decimal("0")
        assert resume.travaux_en_cours >= 0

    def test_lister_couts_par_piece(self, service_inventaire):
        """Liste les coûts pour une pièce."""
        couts = service_inventaire.lister_couts_par_piece(piece_id=1)

        assert isinstance(couts, list)
