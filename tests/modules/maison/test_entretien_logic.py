"""
Tests pour src/modules/maison/entretien/logic.py

Tests des fonctions de génération tâches entretien et badges.
"""

from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest


class TestBadgesEntretien:
    """Tests pour les badges d'entretien."""

    def test_import_badges(self):
        """Test import de la liste des badges."""
        from src.modules.maison.entretien.logic import BADGES_ENTRETIEN

        assert isinstance(BADGES_ENTRETIEN, list)
        assert len(BADGES_ENTRETIEN) > 0

    def test_badge_premiere_tache(self):
        """Test badge première tâche."""
        from src.modules.maison.entretien.logic import BADGES_ENTRETIEN

        badge = next(b for b in BADGES_ENTRETIEN if b["id"] == "premiere_tache")

        assert badge["condition"]({"taches_accomplies": 1})
        assert not badge["condition"]({"taches_accomplies": 0})

    def test_badge_maison_nickel(self):
        """Test badge score >= 90."""
        from src.modules.maison.entretien.logic import BADGES_ENTRETIEN

        badge = next(b for b in BADGES_ENTRETIEN if b["id"] == "maison_nickel")

        assert badge["condition"]({"score": 90})
        assert badge["condition"]({"score": 100})
        assert not badge["condition"]({"score": 89})

    def test_badge_streak_7(self):
        """Test badge 7 jours streak."""
        from src.modules.maison.entretien.logic import BADGES_ENTRETIEN

        badge = next(b for b in BADGES_ENTRETIEN if b["id"] == "streak_7")

        assert badge["condition"]({"streak": 7})
        assert badge["condition"]({"streak": 30})
        assert not badge["condition"]({"streak": 6})

    def test_badge_streak_30(self):
        """Test badge 30 jours streak."""
        from src.modules.maison.entretien.logic import BADGES_ENTRETIEN

        badge = next(b for b in BADGES_ENTRETIEN if b["id"] == "streak_30")

        assert badge["condition"]({"streak": 30})
        assert not badge["condition"]({"streak": 29})

    def test_badge_inventaire_complet(self):
        """Test badge 10+ équipements."""
        from src.modules.maison.entretien.logic import BADGES_ENTRETIEN

        badge = next(b for b in BADGES_ENTRETIEN if b["id"] == "inventaire_complet")

        assert badge["condition"]({"nb_objets": 10})
        assert not badge["condition"]({"nb_objets": 9})

    def test_badge_assidu(self):
        """Test badge 50+ tâches accomplies."""
        from src.modules.maison.entretien.logic import BADGES_ENTRETIEN

        badge = next(b for b in BADGES_ENTRETIEN if b["id"] == "assidu")

        assert badge["condition"]({"taches_accomplies": 50})
        assert not badge["condition"]({"taches_accomplies": 49})

    def test_tous_badges_ont_attributs(self):
        """Test que tous les badges ont les attributs requis."""
        from src.modules.maison.entretien.logic import BADGES_ENTRETIEN

        for badge in BADGES_ENTRETIEN:
            assert "id" in badge
            assert "nom" in badge
            assert "emoji" in badge
            assert "description" in badge
            assert "condition" in badge
            assert callable(badge["condition"])


class TestGenererTachesEntretien:
    """Tests pour generer_taches_entretien."""

    @patch("src.modules.maison.entretien.logic.charger_catalogue_entretien")
    def test_sans_objets(self, mock_catalogue):
        """Test génération sans objets."""
        mock_catalogue.return_value = {"categories": {}}

        from src.modules.maison.entretien.logic import generer_taches_entretien

        taches = generer_taches_entretien([], [])
        assert taches == []

    @patch("src.modules.maison.entretien.logic.charger_catalogue_entretien")
    def test_avec_objet_sans_historique(self, mock_catalogue):
        """Test tâche créée si jamais fait."""
        mock_catalogue.return_value = {
            "categories": {
                "electromenager": {
                    "icon": "🔌",
                    "objets": {
                        "lave-vaisselle": {
                            "nom": "Lave-vaisselle",
                            "taches": [
                                {
                                    "nom": "Nettoyer filtre",
                                    "frequence_jours": 30,
                                    "duree_min": 10,
                                }
                            ],
                        }
                    },
                }
            }
        }

        from src.modules.maison.entretien.logic import generer_taches_entretien

        mes_objets = [{"objet_id": "lave-vaisselle", "categorie_id": "electromenager"}]
        taches = generer_taches_entretien(mes_objets, [])

        assert len(taches) == 1
        assert taches[0]["tache_nom"] == "Nettoyer filtre"
        assert taches[0]["priorite"] in ["urgente", "haute", "moyenne"]

    @patch("src.modules.maison.entretien.logic.charger_catalogue_entretien")
    def test_historique_recent(self, mock_catalogue):
        """Test pas de tâche si fait récemment."""
        mock_catalogue.return_value = {
            "categories": {
                "electromenager": {
                    "icon": "🔌",
                    "objets": {
                        "aspirateur": {
                            "nom": "Aspirateur",
                            "taches": [{"nom": "Vider sac", "frequence_jours": 7, "duree_min": 5}],
                        }
                    },
                }
            }
        }

        from src.modules.maison.entretien.logic import generer_taches_entretien

        mes_objets = [{"objet_id": "aspirateur", "categorie_id": "electromenager"}]
        historique = [
            {
                "objet_id": "aspirateur",
                "tache_nom": "Vider sac",
                "date": date.today().isoformat(),
            }
        ]
        taches = generer_taches_entretien(mes_objets, historique)

        assert len(taches) == 0

    @patch("src.modules.maison.entretien.logic.charger_catalogue_entretien")
    def test_historique_ancien(self, mock_catalogue):
        """Test tâche créée si historique ancien."""
        mock_catalogue.return_value = {
            "categories": {
                "electromenager": {
                    "icon": "🔌",
                    "objets": {
                        "aspirateur": {
                            "nom": "Aspirateur",
                            "taches": [{"nom": "Vider sac", "frequence_jours": 7, "duree_min": 5}],
                        }
                    },
                }
            }
        }

        from src.modules.maison.entretien.logic import generer_taches_entretien

        mes_objets = [{"objet_id": "aspirateur", "categorie_id": "electromenager"}]
        old_date = (date.today() - timedelta(days=10)).isoformat()
        historique = [
            {
                "objet_id": "aspirateur",
                "tache_nom": "Vider sac",
                "date": old_date,
            }
        ]
        taches = generer_taches_entretien(mes_objets, historique)

        assert len(taches) == 1

    @patch("src.modules.maison.entretien.logic.charger_catalogue_entretien")
    def test_tri_priorite(self, mock_catalogue):
        """Test tri par priorité."""
        mock_catalogue.return_value = {
            "categories": {
                "cat1": {
                    "icon": "📦",
                    "objets": {
                        "obj1": {
                            "nom": "Obj1",
                            "taches": [{"nom": "T1", "frequence_jours": 7, "duree_min": 5}],
                        },
                        "obj2": {
                            "nom": "Obj2",
                            "taches": [
                                {
                                    "nom": "T2",
                                    "frequence_jours": 7,
                                    "duree_min": 5,
                                    "obligatoire": True,
                                }
                            ],
                        },
                    },
                }
            }
        }

        from src.modules.maison.entretien.logic import generer_taches_entretien

        mes_objets = [
            {"objet_id": "obj1", "categorie_id": "cat1"},
            {"objet_id": "obj2", "categorie_id": "cat1"},
        ]
        taches = generer_taches_entretien(mes_objets, [])

        # Les duas doivent être générées
        assert len(taches) == 2

    @patch("src.modules.maison.entretien.logic.charger_catalogue_entretien")
    def test_tache_saisonniere(self, mock_catalogue):
        """Test tâche saisonnière ignorée hors saison."""
        mois_actuel = datetime.now().month
        mois_hors_saison = (mois_actuel % 12) + 1  # Mois suivant

        mock_catalogue.return_value = {
            "categories": {
                "cat1": {
                    "icon": "📦",
                    "objets": {
                        "obj1": {
                            "nom": "Obj1",
                            "taches": [
                                {
                                    "nom": "T1",
                                    "frequence_jours": 30,
                                    "duree_min": 10,
                                    "saisonnier": [mois_hors_saison],
                                }
                            ],
                        }
                    },
                }
            }
        }

        from src.modules.maison.entretien.logic import generer_taches_entretien

        mes_objets = [{"objet_id": "obj1", "categorie_id": "cat1"}]
        taches = generer_taches_entretien(mes_objets, [])

        # Tâche ignorée car hors saison
        assert len(taches) == 0

    @patch("src.modules.maison.entretien.logic.charger_catalogue_entretien")
    def test_structure_tache_generee(self, mock_catalogue):
        """Test structure complète d'une tâche générée."""
        mock_catalogue.return_value = {
            "categories": {
                "cat1": {
                    "icon": "📦",
                    "objets": {
                        "obj1": {
                            "nom": "Objet Test",
                            "taches": [
                                {
                                    "nom": "Tâche Test",
                                    "frequence_jours": 30,
                                    "duree_min": 15,
                                    "description": "Description test",
                                }
                            ],
                        }
                    },
                }
            }
        }

        from src.modules.maison.entretien.logic import generer_taches_entretien

        mes_objets = [{"objet_id": "obj1", "categorie_id": "cat1", "piece": "Cuisine"}]
        taches = generer_taches_entretien(mes_objets, [])

        assert len(taches) == 1
        tache = taches[0]

        assert tache["objet_id"] == "obj1"
        assert tache["objet_nom"] == "Objet Test"
        assert tache["categorie_id"] == "cat1"
        assert tache["tache_nom"] == "Tâche Test"
        assert tache["duree_min"] == 15
        assert tache["piece"] == "Cuisine"
        assert "priorite" in tache
        assert "retard_jours" in tache

    @patch("src.modules.maison.entretien.logic.charger_catalogue_entretien")
    def test_objet_inconnu_ignore(self, mock_catalogue):
        """Test que les objets inconnus sont ignorés."""
        mock_catalogue.return_value = {
            "categories": {
                "cat1": {
                    "icon": "📦",
                    "objets": {},  # Pas d'objet défini
                }
            }
        }

        from src.modules.maison.entretien.logic import generer_taches_entretien

        mes_objets = [{"objet_id": "obj_inconnu", "categorie_id": "cat1"}]
        taches = generer_taches_entretien(mes_objets, [])

        assert len(taches) == 0
