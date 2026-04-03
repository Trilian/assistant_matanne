"""
Tests unitaires pour jeux.py

Module: src.core.models.jeux
"""

from src.core.models.jeux import (
    Equipe,
    Match,
    PariSportif,
    TirageLoto,
    GrilleLoto,
    ResultatMatchEnum,
    StatutPariEnum,
    TypePariEnum,
    ChampionnatEnum,
)


class TestJeux:
    """Tests pour le module jeux."""

    class TestResultatMatchEnum:
        """Tests pour la classe ResultatMatchEnum."""

        def test_resultatmatchenum_creation(self):
            assert ResultatMatchEnum.VICTOIRE_DOMICILE == "1"
            assert ResultatMatchEnum.NUL == "N"
            assert ResultatMatchEnum.VICTOIRE_EXTERIEUR == "2"

        def test_resultatmatchenum_est_str_enum(self):
            assert isinstance(ResultatMatchEnum.NUL, str)

    class TestStatutPariEnum:
        """Tests pour la classe StatutPariEnum."""

        def test_statutparienum_creation(self):
            assert StatutPariEnum.EN_ATTENTE == "en_attente"
            assert StatutPariEnum.GAGNE == "gagne"
            assert StatutPariEnum.PERDU == "perdu"

        def test_statutparienum_valeurs(self):
            valeurs = [s.value for s in StatutPariEnum]
            assert "annule" in valeurs

    class TestTypePariEnum:
        """Tests pour la classe TypePariEnum."""

        def test_typeparienum_creation(self):
            assert TypePariEnum.RESULTAT_MATCH == "1N2"
            assert TypePariEnum.BTTS == "les_deux_marquent"

        def test_typeparienum_est_str_enum(self):
            assert isinstance(TypePariEnum.OVER_UNDER, str)

    class TestChampionnatEnum:
        """Tests pour la classe ChampionnatEnum."""

        def test_championnatenum_creation(self):
            assert ChampionnatEnum.LIGUE_1 == "Ligue 1"
            assert ChampionnatEnum.PREMIER_LEAGUE == "Premier League"

        def test_championnatenum_valeurs(self):
            valeurs = [c.value for c in ChampionnatEnum]
            assert "Champions League" in valeurs

    class TestEquipe:
        """Tests pour la classe Equipe."""

        def test_equipe_creation(self):
            equipe = Equipe(
                nom="Paris Saint-Germain",
                nom_court="PSG",
                championnat="ligue_1",
                pays="France",
            )
            assert equipe.nom == "Paris Saint-Germain"
            assert equipe.nom_court == "PSG"
            assert equipe.championnat == "ligue_1"

        def test_equipe_tablename(self):
            assert Equipe.__tablename__ == "jeux_equipes"

    class TestMatch:
        """Tests pour la classe Match."""

        def test_match_creation(self):
            match = Match(
                equipe_domicile_id=1,
                equipe_exterieur_id=2,
                championnat="ligue_1",
            )
            assert match.equipe_domicile_id == 1
            assert match.championnat == "ligue_1"

        def test_match_tablename(self):
            assert Match.__tablename__ == "jeux_matchs"

    class TestPariSportif:
        """Tests pour la classe PariSportif."""

        def test_pari_creation(self):
            pari = PariSportif(
                match_id=1,
                type_pari="1N2",
                prediction="1",
                cote=1.85,
            )
            assert pari.type_pari == "1N2"
            assert pari.cote == 1.85

    class TestTirageLoto:
        """Tests pour la classe TirageLoto."""

        def test_tirage_creation(self):
            tirage = TirageLoto(
                numero_1=5,
                numero_2=12,
                numero_3=23,
                numero_4=34,
                numero_5=45,
                numero_chance=3,
            )
            assert tirage.numero_1 == 5
            assert tirage.numero_chance == 3

        def test_tirage_tablename(self):
            assert TirageLoto.__tablename__ == "jeux_tirages_loto"

    class TestGrilleLoto:
        """Tests pour la classe GrilleLoto."""

        def test_grille_creation(self):
            grille = GrilleLoto(
                numero_1=5,
                numero_2=12,
                numero_3=23,
                numero_4=34,
                numero_5=45,
                numero_chance=3,
                source_prediction="aleatoire",
            )
            assert grille.source_prediction == "aleatoire"

        def test_grille_tablename(self):
            assert GrilleLoto.__tablename__ == "jeux_grilles_loto"
