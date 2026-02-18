"""
Tests pour src/modules/maison/jardin/logic.py

Tests des fonctions de génération tâches jardin et badges.
"""

from datetime import date
from unittest.mock import patch

import pytest


class TestBadgesJardin:
    """Tests pour les badges de jardin."""

    def test_import_badges(self):
        """Test import de la liste des badges."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        assert isinstance(BADGES_JARDIN, list)
        assert len(BADGES_JARDIN) > 0

    def test_badge_premier_semis(self):
        """Test badge premier semis."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        badge = next(b for b in BADGES_JARDIN if b["id"] == "premier_semis")

        assert badge["condition"]({"semis_total": 1})
        assert not badge["condition"]({"semis_total": 0})

    def test_badge_pouce_vert(self):
        """Test badge 10+ plantes."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        badge = next(b for b in BADGES_JARDIN if b["id"] == "pouce_vert")

        assert badge["condition"]({"nb_plantes": 10})
        assert not badge["condition"]({"nb_plantes": 9})

    def test_badge_premiere_recolte(self):
        """Test badge première récolte."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        badge = next(b for b in BADGES_JARDIN if b["id"] == "premiere_recolte")

        assert badge["condition"]({"recoltes_total": 1})
        assert not badge["condition"]({"recoltes_total": 0})

    def test_badge_jardinier_assidu(self):
        """Test badge 7 jours streak."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        badge = next(b for b in BADGES_JARDIN if b["id"] == "jardinier_assidu")

        assert badge["condition"]({"streak": 7})
        assert not badge["condition"]({"streak": 6})

    def test_badge_polyvalent(self):
        """Test badge 5+ variétés."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        badge = next(b for b in BADGES_JARDIN if b["id"] == "polyvalent")

        assert badge["condition"]({"varietes_uniques": 5})
        assert not badge["condition"]({"varietes_uniques": 4})

    def test_badge_autonomie_25(self):
        """Test badge 25% autonomie."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        badge = next(b for b in BADGES_JARDIN if b["id"] == "autosuffisant_25")

        assert badge["condition"]({"autonomie_pourcent": 25})
        assert not badge["condition"]({"autonomie_pourcent": 24})

    def test_badge_autonomie_50(self):
        """Test badge 50% autonomie."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        badge = next(b for b in BADGES_JARDIN if b["id"] == "autosuffisant_50")

        assert badge["condition"]({"autonomie_pourcent": 50})
        assert not badge["condition"]({"autonomie_pourcent": 49})

    def test_badge_eco_expert(self):
        """Test badge pratiques éco."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        badge = next(b for b in BADGES_JARDIN if b["id"] == "eco_expert")

        assert badge["condition"]({"pratiques_eco": 2})
        assert not badge["condition"]({"pratiques_eco": 1})

    def test_tous_badges_ont_attributs(self):
        """Test que tous les badges ont les attributs requis."""
        from src.modules.maison.jardin.logic import BADGES_JARDIN

        for badge in BADGES_JARDIN:
            assert "id" in badge
            assert "nom" in badge
            assert "emoji" in badge
            assert "description" in badge
            assert "condition" in badge
            assert callable(badge["condition"])


class TestGenererTachesJardin:
    """Tests pour generer_taches_jardin."""

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_sans_plantes(self, mock_catalogue):
        """Test génération sans plantes."""
        mock_catalogue.return_value = {"plantes": {}}

        from src.modules.maison.jardin.logic import generer_taches_jardin

        taches = generer_taches_jardin([], {})
        assert isinstance(taches, list)

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_tache_semis_interieur(self, mock_catalogue):
        """Test tâche semis si période bonne."""
        mois_actuel = date.today().month

        mock_catalogue.return_value = {
            "plantes": {
                "tomate": {
                    "nom": "Tomate",
                    "emoji": "🍅",
                    "semis_interieur": [mois_actuel],  # Mois actuel
                }
            }
        }

        from src.modules.maison.jardin.logic import generer_taches_jardin

        taches = generer_taches_jardin([], {})

        semis_taches = [t for t in taches if t.get("type") == "semis"]
        assert len(semis_taches) >= 1
        assert "Tomate" in semis_taches[0]["titre"]

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_pas_semis_si_deja_fait(self, mock_catalogue):
        """Test pas de semis si déjà effectué."""
        mois_actuel = date.today().month

        mock_catalogue.return_value = {
            "plantes": {
                "tomate": {
                    "nom": "Tomate",
                    "emoji": "🍅",
                    "semis_interieur": [mois_actuel],
                }
            }
        }

        from src.modules.maison.jardin.logic import generer_taches_jardin

        mes_plantes = [{"plante_id": "tomate", "semis_fait": True}]
        taches = generer_taches_jardin(mes_plantes, {})

        semis_taches = [
            t for t in taches if t.get("type") == "semis" and "Tomate" in t.get("titre", "")
        ]
        assert len(semis_taches) == 0

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_tache_arrosage_chaleur(self, mock_catalogue):
        """Test tâche arrosage si température élevée."""
        mock_catalogue.return_value = {"plantes": {}}

        from src.modules.maison.jardin.logic import generer_taches_jardin

        mes_plantes = [{"plante_id": "tomate", "plante_en_terre": True}]
        meteo = {"temperature": 30, "pluie_prevue": False}

        taches = generer_taches_jardin(mes_plantes, meteo)

        arrosage_taches = [t for t in taches if t.get("type") == "arrosage"]
        assert len(arrosage_taches) >= 1
        assert arrosage_taches[0]["priorite"] == "urgente"

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_arrosage_haute_priorite(self, mock_catalogue):
        """Test arrosage haute priorité si temp > 20."""
        mock_catalogue.return_value = {"plantes": {}}

        from src.modules.maison.jardin.logic import generer_taches_jardin

        mes_plantes = [{"plante_id": "tomate", "plante_en_terre": True}]
        meteo = {"temperature": 25, "pluie_prevue": False}

        taches = generer_taches_jardin(mes_plantes, meteo)

        arrosage_taches = [t for t in taches if t.get("type") == "arrosage"]
        assert len(arrosage_taches) >= 1
        assert arrosage_taches[0]["priorite"] == "haute"

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_pas_arrosage_si_pluie(self, mock_catalogue):
        """Test pas d'arrosage si pluie prévue."""
        mock_catalogue.return_value = {"plantes": {}}

        from src.modules.maison.jardin.logic import generer_taches_jardin

        mes_plantes = [{"plante_id": "tomate", "plante_en_terre": True}]
        meteo = {"temperature": 25, "pluie_prevue": True}

        taches = generer_taches_jardin(mes_plantes, meteo)

        arrosage_taches = [t for t in taches if t.get("type") == "arrosage"]
        assert len(arrosage_taches) == 0

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_tache_protection_gel(self, mock_catalogue):
        """Test tâche protection si gel prévu."""
        mock_catalogue.return_value = {"plantes": {}}

        from src.modules.maison.jardin.logic import generer_taches_jardin

        mes_plantes = [{"plante_id": "tomate", "plante_en_terre": True}]
        meteo = {"gel_risque": True}

        taches = generer_taches_jardin(mes_plantes, meteo)

        protection_taches = [t for t in taches if t.get("type") == "protection"]
        assert len(protection_taches) >= 1
        assert protection_taches[0]["priorite"] == "urgente"

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_pas_protection_si_pas_plantes_terre(self, mock_catalogue):
        """Test pas de protection si pas de plantes en terre."""
        mock_catalogue.return_value = {"plantes": {}}

        from src.modules.maison.jardin.logic import generer_taches_jardin

        mes_plantes = [{"plante_id": "tomate", "plante_en_terre": False}]
        meteo = {"gel_risque": True}

        taches = generer_taches_jardin(mes_plantes, meteo)

        protection_taches = [t for t in taches if t.get("type") == "protection"]
        assert len(protection_taches) == 0

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_structure_tache(self, mock_catalogue):
        """Test structure d'une tâche générée."""
        mock_catalogue.return_value = {"plantes": {}}

        from src.modules.maison.jardin.logic import generer_taches_jardin

        mes_plantes = [{"plante_id": "tomate", "plante_en_terre": True}]
        meteo = {"temperature": 30, "pluie_prevue": False}

        taches = generer_taches_jardin(mes_plantes, meteo)

        if taches:
            tache = taches[0]
            assert "type" in tache
            assert "titre" in tache
            assert "emoji" in tache
            assert "priorite" in tache
            assert "duree_min" in tache

    @patch("src.modules.maison.jardin.logic.charger_catalogue_plantes")
    def test_tache_plantation_exterieur(self, mock_catalogue):
        """Test tâche plantation si plants prêts."""
        mois_actuel = date.today().month

        mock_catalogue.return_value = {
            "plantes": {
                "tomate": {
                    "nom": "Tomate",
                    "emoji": "🍅",
                    "plantation_exterieur": [mois_actuel],
                }
            }
        }

        from src.modules.maison.jardin.logic import generer_taches_jardin

        # Plant prêt à être repiqué
        mes_plantes = [{"plante_id": "tomate", "semis_fait": True, "plante_en_terre": False}]
        taches = generer_taches_jardin(mes_plantes, {})

        plantation_taches = [t for t in taches if t.get("type") == "plantation"]
        assert len(plantation_taches) >= 1
        assert "Tomate" in plantation_taches[0]["titre"]
        assert plantation_taches[0]["priorite"] == "haute"
