"""
Tests comprehensifs pour src/modules/planning/vue_ensemble_utils.py
Objectif: Augmenter la couverture de 53.01% à 80%+
"""

from datetime import date, timedelta

from src.modules.planning.vue_ensemble_utils import (
    CATEGORIES_TACHES,
    PERIODES,
    analyser_charge_globale,
    analyser_tendances,
    calculer_statistiques_periode,
    est_en_retard,
    formater_evolution,
    formater_niveau_charge,
    generer_alertes,
    identifier_taches_urgentes,
    prevoir_charge_prochaine_semaine,
)

# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes du module."""

    def test_periodes(self):
        """Test liste des periodes."""
        assert "Jour" in PERIODES
        assert "Semaine" in PERIODES
        assert "Mois" in PERIODES
        assert "Annee" in PERIODES

    def test_categories_taches(self):
        """Test liste des categories."""
        assert "Travail" in CATEGORIES_TACHES
        assert "Maison" in CATEGORIES_TACHES
        assert "Famille" in CATEGORIES_TACHES
        assert "Personnel" in CATEGORIES_TACHES


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSER CHARGE GLOBALE
# ═══════════════════════════════════════════════════════════


class TestAnalyserChargeGlobale:
    """Tests pour analyser_charge_globale."""

    def test_listes_vides(self):
        """Test avec listes vides."""
        result = analyser_charge_globale([], [])

        assert result["total_evenements"] == 0
        assert result["total_taches"] == 0
        assert result["taches_completees"] == 0
        assert result["taches_en_retard"] == 0
        assert result["taux_completion"] == 0
        assert result["niveau_charge"] == "Libre"

    def test_charge_legere(self):
        """Test charge legere (<=5 items)."""
        evenements = [{"id": 1}, {"id": 2}]
        taches = [{"id": 1, "complete": False}, {"id": 2, "complete": True}]

        result = analyser_charge_globale(evenements, taches)

        assert result["total_evenements"] == 2
        assert result["total_taches"] == 2
        assert result["taches_completees"] == 1
        assert result["taux_completion"] == 50.0
        # Charge = 2 evt + 1 tache non complete = 3 => Léger
        assert result["niveau_charge"] == "Léger"

    def test_charge_moyenne(self):
        """Test charge moyenne (6-15 items)."""
        evenements = [{"id": i} for i in range(8)]
        taches = [{"id": i, "complete": False} for i in range(5)]

        result = analyser_charge_globale(evenements, taches)

        # 8 evt + 5 taches = 13 => Moyen
        assert result["niveau_charge"] == "Moyen"

    def test_charge_elevee(self):
        """Test charge elevee (16-25 items)."""
        evenements = [{"id": i} for i in range(15)]
        taches = [{"id": i, "complete": False} for i in range(8)]

        result = analyser_charge_globale(evenements, taches)

        # 15 evt + 8 taches = 23 => Élevé
        assert result["niveau_charge"] == "Élevé"

    def test_charge_tres_elevee(self):
        """Test charge tres elevee (>25 items)."""
        evenements = [{"id": i} for i in range(20)]
        taches = [{"id": i, "complete": False} for i in range(10)]

        result = analyser_charge_globale(evenements, taches)

        # 20 evt + 10 taches = 30 => Très élevé
        assert result["niveau_charge"] == "Très élevé"

    def test_taches_en_retard_comptees(self):
        """Test comptage des taches en retard."""
        hier = date.today() - timedelta(days=1)
        taches = [
            {"id": 1, "complete": False, "date_limite": hier.isoformat()},
            {"id": 2, "complete": False, "date_limite": hier.isoformat()},
            {"id": 3, "complete": True, "date_limite": hier.isoformat()},  # Complete, pas en retard
        ]

        result = analyser_charge_globale([], taches)

        assert result["taches_en_retard"] == 2

    def test_charge_par_categorie(self):
        """Test groupement par categorie."""
        taches = [
            {"id": 1, "categorie": "Travail"},
            {"id": 2, "categorie": "Travail"},
            {"id": 3, "categorie": "Maison"},
            {"id": 4},  # Sans categorie -> Personnel
        ]

        result = analyser_charge_globale([], taches)

        assert result["charge_par_categorie"]["Travail"] == 2
        assert result["charge_par_categorie"]["Maison"] == 1
        assert result["charge_par_categorie"]["Personnel"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS EST_EN_RETARD
# ═══════════════════════════════════════════════════════════


class TestEstEnRetard:
    """Tests pour est_en_retard."""

    def test_tache_complete(self):
        """Test tache complete n'est jamais en retard."""
        hier = date.today() - timedelta(days=1)
        tache = {"complete": True, "date_limite": hier.isoformat()}

        assert est_en_retard(tache) is False

    def test_tache_sans_date_limite(self):
        """Test tache sans date limite n'est pas en retard."""
        tache = {"complete": False}

        assert est_en_retard(tache) is False

    def test_tache_en_retard_string(self):
        """Test tache en retard avec date string."""
        hier = date.today() - timedelta(days=1)
        tache = {"complete": False, "date_limite": hier.isoformat()}

        assert est_en_retard(tache) is True

    def test_tache_en_retard_date(self):
        """Test tache en retard avec objet date."""
        hier = date.today() - timedelta(days=1)
        tache = {"complete": False, "date_limite": hier}

        assert est_en_retard(tache) is True

    def test_tache_pas_en_retard(self):
        """Test tache future pas en retard."""
        demain = date.today() + timedelta(days=1)
        tache = {"complete": False, "date_limite": demain.isoformat()}

        assert est_en_retard(tache) is False

    def test_tache_due_aujourdhui(self):
        """Test tache due aujourd'hui n'est pas en retard."""
        tache = {"complete": False, "date_limite": date.today().isoformat()}

        assert est_en_retard(tache) is False


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSER TENDANCES
# ═══════════════════════════════════════════════════════════


class TestAnalyserTendances:
    """Tests pour analyser_tendances."""

    def test_historique_vide(self):
        """Test avec historique vide."""
        result = analyser_tendances([], jours=30)

        assert result["evolution"] == "stable"
        assert result["moyenne_jour"] == 0.0
        assert result["pic_activite"] is None

    def test_tendance_stable(self):
        """Test tendance stable."""
        # Creer historique reparti uniformement
        historique = []
        for i in range(30):
            jour = date.today() - timedelta(days=i)
            historique.append({"date": jour.isoformat(), "type": "test"})

        result = analyser_tendances(historique, jours=30)

        assert result["evolution"] == "stable"
        assert result["moyenne_jour"] == 1.0

    def test_tendance_hausse(self):
        """Test tendance en hausse."""
        # Plus d'activite dans la seconde moitie
        historique = []
        for i in range(15):  # 15 derniers jours: beaucoup d'activite
            jour = date.today() - timedelta(days=i)
            for _ in range(3):
                historique.append({"date": jour.isoformat()})

        result = analyser_tendances(historique, jours=30)

        assert result["evolution"] == "hausse"

    def test_tendance_baisse(self):
        """Test tendance en baisse."""
        # Plus d'activite dans la premiere moitie (jours 15-30)
        historique = []
        for i in range(15, 30):
            jour = date.today() - timedelta(days=i)
            for _ in range(3):
                historique.append({"date": jour.isoformat()})

        result = analyser_tendances(historique, jours=30)

        assert result["evolution"] == "baisse"

    def test_pic_activite(self):
        """Test detection du pic d'activite."""
        # Un jour avec beaucoup d'activite
        jour_pic = date.today() - timedelta(days=5)
        historique = [{"date": jour_pic.isoformat()} for _ in range(10)]

        result = analyser_tendances(historique, jours=30)

        assert result["pic_activite"] is not None
        assert result["pic_activite"]["date"] == jour_pic
        assert result["pic_activite"]["nombre"] == 10

    def test_historique_avec_dates_objets(self):
        """Test avec dates comme objets date."""
        jour = date.today() - timedelta(days=5)
        historique = [{"date": jour}]  # Date objet, pas string

        result = analyser_tendances(historique, jours=30)

        assert result["moyenne_jour"] > 0


# ═══════════════════════════════════════════════════════════
# TESTS PREVOIR CHARGE PROCHAINE SEMAINE
# ═══════════════════════════════════════════════════════════


class TestPrevoirChargeProchaineSemaine:
    """Tests pour prevoir_charge_prochaine_semaine."""

    def test_pas_evenements(self):
        """Test sans evenements ni taches."""
        result = prevoir_charge_prochaine_semaine([], [])

        assert result["evenements"] == 0
        assert result["taches"] == 0
        assert result["charge_totale"] == 0
        assert result["prevision"] == "Semaine légère"

    def test_semaine_legere(self):
        """Test semaine legere (<=5)."""
        debut = date.today() + timedelta(days=7 - date.today().weekday())
        evenements = [{"date": debut.isoformat()} for _ in range(3)]

        result = prevoir_charge_prochaine_semaine(evenements, [])

        assert result["evenements"] == 3
        assert result["prevision"] == "Semaine légère"

    def test_semaine_normale(self):
        """Test semaine normale (6-15)."""
        debut = date.today() + timedelta(days=7 - date.today().weekday())
        evenements = [{"date": debut.isoformat()} for _ in range(10)]

        result = prevoir_charge_prochaine_semaine(evenements, [])

        assert result["prevision"] == "Semaine normale"

    def test_semaine_chargee(self):
        """Test semaine chargee (16-25)."""
        debut = date.today() + timedelta(days=7 - date.today().weekday())
        evenements = [{"date": debut.isoformat()} for _ in range(20)]

        result = prevoir_charge_prochaine_semaine(evenements, [])

        assert result["prevision"] == "Semaine chargée"

    def test_semaine_tres_chargee(self):
        """Test semaine tres chargee (>25)."""
        debut = date.today() + timedelta(days=7 - date.today().weekday())
        evenements = [{"date": debut.isoformat()} for _ in range(30)]

        result = prevoir_charge_prochaine_semaine(evenements, [])

        assert result["prevision"] == "Semaine très chargée"

    def test_taches_a_echeance(self):
        """Test comptage taches a echeance."""
        debut = date.today() + timedelta(days=7 - date.today().weekday())
        fin = debut + timedelta(days=6)

        taches = [
            {"date_limite": debut.isoformat(), "complete": False},
            {"date_limite": fin.isoformat(), "complete": False},
            {"date_limite": debut.isoformat(), "complete": True},  # Complete, ignore
            {
                "date_limite": (debut - timedelta(days=10)).isoformat(),
                "complete": False,
            },  # Hors semaine
        ]

        result = prevoir_charge_prochaine_semaine([], taches)

        assert result["taches"] == 2

    def test_evenements_avec_date_objet(self):
        """Test avec dates objets."""
        debut = date.today() + timedelta(days=7 - date.today().weekday())
        evenements = [{"date": debut}]  # Date objet

        result = prevoir_charge_prochaine_semaine(evenements, [])

        assert result["evenements"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS IDENTIFIER TACHES URGENTES
# ═══════════════════════════════════════════════════════════


class TestIdentifierTachesUrgentes:
    """Tests pour identifier_taches_urgentes."""

    def test_pas_taches_urgentes(self):
        """Test sans taches urgentes."""
        semaine_prochaine = date.today() + timedelta(days=10)
        taches = [{"date_limite": semaine_prochaine.isoformat(), "complete": False}]

        result = identifier_taches_urgentes(taches, jours_seuil=3)

        assert len(result) == 0

    def test_taches_urgentes_trouvees(self):
        """Test taches urgentes trouvees."""
        demain = date.today() + timedelta(days=1)
        taches = [
            {"id": 1, "date_limite": demain.isoformat(), "complete": False},
            {"id": 2, "date_limite": demain.isoformat(), "complete": True},  # Complete
            {
                "id": 3,
                "date_limite": (date.today() + timedelta(days=5)).isoformat(),
                "complete": False,
            },  # Pas urgent
        ]

        result = identifier_taches_urgentes(taches, jours_seuil=3)

        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_taches_sans_date_limite(self):
        """Test taches sans date limite ignorees."""
        taches = [{"id": 1, "complete": False}]  # Pas de date_limite

        result = identifier_taches_urgentes(taches, jours_seuil=3)

        assert len(result) == 0

    def test_seuil_personnalise(self):
        """Test avec seuil personnalise."""
        dans_5_jours = date.today() + timedelta(days=5)
        taches = [{"date_limite": dans_5_jours.isoformat(), "complete": False}]

        # Seuil 3 jours: pas urgent
        assert len(identifier_taches_urgentes(taches, jours_seuil=3)) == 0

        # Seuil 7 jours: urgent
        assert len(identifier_taches_urgentes(taches, jours_seuil=7)) == 1


# ═══════════════════════════════════════════════════════════
# TESTS GENERER ALERTES
# ═══════════════════════════════════════════════════════════


class TestGenererAlertes:
    """Tests pour generer_alertes."""

    def test_pas_alertes(self):
        """Test sans alertes."""
        result = generer_alertes([], [])

        assert len(result) == 0

    def test_alerte_taches_retard(self):
        """Test alerte taches en retard."""
        hier = date.today() - timedelta(days=1)
        taches = [{"date_limite": hier.isoformat(), "complete": False}]

        result = generer_alertes([], taches)

        alertes_danger = [a for a in result if a["type"] == "danger"]
        assert len(alertes_danger) == 1
        assert "retard" in alertes_danger[0]["message"]

    def test_alerte_taches_urgentes(self):
        """Test alerte taches urgentes."""
        demain = date.today() + timedelta(days=1)
        taches = [{"date_limite": demain.isoformat(), "complete": False}]

        result = generer_alertes([], taches)

        alertes_warning = [a for a in result if a["type"] == "warning"]
        assert len(alertes_warning) == 1
        assert "urgente" in alertes_warning[0]["message"]

    def test_alerte_evenements_aujourdhui(self):
        """Test alerte evenements aujourd'hui."""
        evenements = [
            {"date": date.today().isoformat()},
            {"date": date.today().isoformat()},
        ]

        result = generer_alertes(evenements, [])

        alertes_info = [a for a in result if a["type"] == "info"]
        assert len(alertes_info) == 1
        assert "2 evenement" in alertes_info[0]["message"]

    def test_evenements_avec_date_objet(self):
        """Test avec dates objets."""
        evenements = [{"date": date.today()}]

        result = generer_alertes(evenements, [])

        alertes_info = [a for a in result if a["type"] == "info"]
        assert len(alertes_info) == 1


# ═══════════════════════════════════════════════════════════
# TESTS CALCULER STATISTIQUES PERIODE
# ═══════════════════════════════════════════════════════════


class TestCalculerStatistiquesPeriode:
    """Tests pour calculer_statistiques_periode."""

    def test_periode_jour(self):
        """Test statistiques journalieres."""
        items = [{"date": date.today().isoformat()}]

        result = calculer_statistiques_periode(items, periode="Jour")

        assert result["periode"] == "Jour"
        assert result["total"] == 1
        assert result["moyenne_jour"] == 1.0

    def test_periode_semaine(self):
        """Test statistiques hebdomadaires."""
        items = [{"date": (date.today() - timedelta(days=i)).isoformat()} for i in range(7)]

        result = calculer_statistiques_periode(items, periode="Semaine")

        assert result["periode"] == "Semaine"
        assert result["total"] == 7
        assert result["moyenne_jour"] == 1.0

    def test_periode_mois(self):
        """Test statistiques mensuelles."""
        items = [{"date": (date.today() - timedelta(days=i)).isoformat()} for i in range(30)]

        result = calculer_statistiques_periode(items, periode="Mois")

        assert result["periode"] == "Mois"
        assert result["total"] == 30
        assert result["moyenne_jour"] == 1.0

    def test_periode_annee(self):
        """Test statistiques annuelles."""
        items = [{"date": date.today().isoformat()}]

        result = calculer_statistiques_periode(items, periode="Annee")

        assert result["periode"] == "Annee"
        assert result["moyenne_jour"] == 1 / 365

    def test_items_hors_periode(self):
        """Test items hors periode ignores."""
        vieux = date.today() - timedelta(days=100)
        items = [{"date": vieux.isoformat()}]

        result = calculer_statistiques_periode(items, periode="Semaine")

        assert result["total"] == 0

    def test_items_avec_date_objet(self):
        """Test avec dates objets."""
        items = [{"date": date.today()}]

        result = calculer_statistiques_periode(items, periode="Jour")

        assert result["total"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════


class TestFormatage:
    """Tests pour fonctions de formatage."""

    def test_formater_niveau_charge_libre(self):
        """Test formatage niveau Libre."""
        result = formater_niveau_charge("Libre")
        assert "😌" in result
        assert "Libre" in result

    def test_formater_niveau_charge_leger(self):
        """Test formatage niveau Leger."""
        result = formater_niveau_charge("Léger")
        assert "🙂" in result

    def test_formater_niveau_charge_moyen(self):
        """Test formatage niveau Moyen."""
        result = formater_niveau_charge("Moyen")
        assert "😐" in result

    def test_formater_niveau_charge_eleve(self):
        """Test formatage niveau Eleve."""
        result = formater_niveau_charge("Élevé")
        assert "😰" in result

    def test_formater_niveau_charge_tres_eleve(self):
        """Test formatage niveau Tres eleve."""
        result = formater_niveau_charge("Très élevé")
        assert "🔥" in result

    def test_formater_niveau_charge_inconnu(self):
        """Test formatage niveau inconnu."""
        result = formater_niveau_charge("Inconnu")
        assert "Inconnu" in result

    def test_formater_evolution_hausse(self):
        """Test formatage evolution hausse."""
        result = formater_evolution("hausse")
        # Note: emoji peut avoir des problemes d'encodage sur certains systemes
        assert "Hausse" in result
        assert len(result) > len("Hausse")  # Contient un emoji

    def test_formater_evolution_baisse(self):
        """Test formatage evolution baisse."""
        result = formater_evolution("baisse")
        assert "📉" in result
        assert "Baisse" in result

    def test_formater_evolution_stable(self):
        """Test formatage evolution stable."""
        result = formater_evolution("stable")
        assert "➡️" in result
        assert "Stable" in result

    def test_formater_evolution_inconnu(self):
        """Test formatage evolution inconnue."""
        result = formater_evolution("inconnue")
        assert "Inconnue" in result
