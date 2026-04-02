"""Tests Sprint 8 pour EnergieAnomaliesIAService."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from src.services.maison.energie_anomalies_ia import EnergieAnomaliesIAService


class TestEnergieAnomaliesScoring:
    def test_score_anormalite_borne(self):
        assert EnergieAnomaliesIAService._score_anormalite(-150.0) == 100
        assert EnergieAnomaliesIAService._score_anormalite(0.0) == 0
        assert EnergieAnomaliesIAService._score_anormalite(22.8) == 22

    def test_severite_seuils(self):
        assert EnergieAnomaliesIAService._severite(10) == "faible"
        assert EnergieAnomaliesIAService._severite(20) == "moyenne"
        assert EnergieAnomaliesIAService._severite(40) == "elevee"
        assert EnergieAnomaliesIAService._severite(80) == "critique"


class TestEnergieAnomaliesAnalyse:
    def _service_sans_init(self) -> EnergieAnomaliesIAService:
        # Evite l'initialisation du client IA pour les tests unitaires purs.
        return EnergieAnomaliesIAService.__new__(EnergieAnomaliesIAService)

    def _db_mock_with_rows(self, rows: list[SimpleNamespace]) -> MagicMock:
        query = MagicMock()
        query.filter.return_value = query
        query.group_by.return_value = query
        query.order_by.return_value = query
        query.limit.return_value = query
        query.all.return_value = rows

        db = MagicMock()
        db.query.return_value = query
        return db

    def test_analyser_anomalies_retourne_message_si_aucun_releve(self):
        service = self._service_sans_init()
        service._generer_explications_ia = MagicMock(return_value=[])
        db = self._db_mock_with_rows([])

        resultat = service.analyser_anomalies(type_compteur="electricite", nb_mois=6, db=db)

        assert resultat["type"] == "electricite"
        assert resultat["points"] == []
        assert resultat["anomalies"] == []
        assert resultat["score_anormalite_global"] == 0
        assert "Aucun releve" in resultat["message"]

    def test_analyser_anomalies_detecte_un_ecart_et_enrichit_explication(self):
        service = self._service_sans_init()
        rows = [
            SimpleNamespace(mois="2026-01-01", conso=120.0),
            SimpleNamespace(mois="2026-02-01", conso=125.0),
            SimpleNamespace(mois="2026-03-01", conso=200.0),
        ]
        db = self._db_mock_with_rows(rows)

        service._generer_explications_ia = MagicMock(
            return_value=[
                {
                    "mois": "2026-03",
                    "explication": "Hausse ponctuelle chauffage",
                    "causes_probables": ["froid"],
                    "actions_recommandees": ["verifier isolation"],
                }
            ]
        )

        resultat = service.analyser_anomalies(
            type_compteur="electricite",
            nb_mois=3,
            seuil_pct=20.0,
            db=db,
        )

        assert resultat["total"] == 3
        assert resultat["nb_anomalies"] == 1
        anomalie = resultat["anomalies"][0]
        assert anomalie["mois"] == "2026-03"
        assert anomalie["severite"] in {"moyenne", "elevee", "critique"}
        assert anomalie["explication"] == "Hausse ponctuelle chauffage"

    def test_generer_explications_utilise_fallback_si_ia_en_erreur(self):
        service = self._service_sans_init()
        service.call_with_list_parsing_sync = MagicMock(side_effect=RuntimeError("IA indisponible"))

        anomalies = [
            {
                "mois": "2026-04",
                "conso": 180.0,
                "ecart_pct": 35.0,
                "score_anormalite": 35,
            }
        ]

        explications = service._generer_explications_ia(
            type_compteur="gaz",
            anomalies=anomalies,
            moyenne=120.0,
        )

        assert len(explications) == 1
        assert explications[0]["mois"] == "2026-04"
        assert "Variation" in explications[0]["explication"]
        assert len(explications[0]["causes_probables"]) >= 1
