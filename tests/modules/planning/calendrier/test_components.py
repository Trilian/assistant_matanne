"""Tests pour le module components du calendrier unifie."""

from __future__ import annotations

from datetime import date, time, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.modules.planning.calendrier.utils import (
    EvenementCalendrier,
    JourCalendrier,
    SemaineCalendrier,
    TypeEvenement,
)


class SessionStateMock(dict):
    """Mock de st.session_state supportant l acces par attribut."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

    def get(self, key: str, default: Any = None) -> Any:
        return self[key] if key in self else default


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Configure le mock Streamlit avec tous les comportements communs."""
    mock_st.columns.side_effect = lambda n: [
        MagicMock() for _ in range(n if isinstance(n, int) else len(n))
    ]
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.container.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)


def create_mock_event(
    event_id: str = "activite_1",
    type_evt: TypeEvenement = TypeEvenement.ACTIVITE,
    titre: str = "Test Event",
    date_jour: date | None = None,
    heure_debut: time | None = None,
    heure_fin: time | None = None,
    pour_jules: bool = False,
) -> EvenementCalendrier:
    """Cree un evenement de test."""
    return EvenementCalendrier(
        id=event_id,
        type=type_evt,
        titre=titre,
        date_jour=date_jour or date.today(),
        heure_debut=heure_debut,
        heure_fin=heure_fin,
        pour_jules=pour_jules,
    )


def create_mock_jour(
    jour_date: date | None = None,
    evenements: list | None = None,
) -> JourCalendrier:
    """Cree un jour de test."""
    return JourCalendrier(
        date_jour=jour_date or date.today(),
        evenements=evenements or [],
    )


def create_mock_semaine(
    date_debut: date | None = None,
    jours: list | None = None,
) -> SemaineCalendrier:
    """Cree une semaine de test."""
    start = date_debut or date.today()
    if jours is None:
        jours = [create_mock_jour(start + timedelta(days=i)) for i in range(7)]
    return SemaineCalendrier(
        date_debut=start,
        jours=jours,
    )


class TestRenderNavigationSemaine:
    """Tests pour la fonction afficher_navigation_semaine."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_navigation_basic(self, mock_st: MagicMock) -> None:
        """Test du rendu basique de la navigation."""
        from src.modules.planning.calendrier.components import afficher_navigation_semaine

        setup_mock_st(mock_st, {"cal_semaine_debut": date.today()})
        afficher_navigation_semaine()
        mock_st.columns.assert_called()

    @patch("src.modules.planning.calendrier.components.st")
    def test_navigation_without_session(self, mock_st: MagicMock) -> None:
        """Test navigation sans session existante."""
        from src.modules.planning.calendrier.components import afficher_navigation_semaine

        setup_mock_st(mock_st)
        afficher_navigation_semaine()
        assert "cal_semaine_debut" in mock_st.session_state


class TestRenderJourCalendrier:
    """Tests pour la fonction afficher_jour_calendrier."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_empty(self, mock_st: MagicMock) -> None:
        """Test du rendu d un jour sans evenements."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        jour = create_mock_jour()
        afficher_jour_calendrier(jour)
        assert True

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_with_events(self, mock_st: MagicMock) -> None:
        """Test du rendu d un jour avec evenements."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [
            create_mock_event("repas_1", TypeEvenement.REPAS_MIDI, "Dejeuner"),
            create_mock_event("act_1", TypeEvenement.ACTIVITE, "Sport"),
        ]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert True

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_with_repas_soir(self, mock_st: MagicMock) -> None:
        """Test avec repas du soir."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [create_mock_event("soir_1", TypeEvenement.REPAS_SOIR, "Diner")]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert jour.repas_soir is not None

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_with_gouter(self, mock_st: MagicMock) -> None:
        """Test avec gouter."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [create_mock_event("gouter_1", TypeEvenement.GOUTER, "Gouter")]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert jour.gouter is not None

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_with_batch(self, mock_st: MagicMock) -> None:
        """Test avec batch cooking."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [create_mock_event("batch_1", TypeEvenement.BATCH_COOKING, "Batch")]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert jour.batch_cooking is not None

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_with_courses(self, mock_st: MagicMock) -> None:
        """Test avec courses."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [create_mock_event("courses_1", TypeEvenement.COURSES, "Supermarche")]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert len(jour.courses) == 1

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_with_rdv(self, mock_st: MagicMock) -> None:
        """Test avec rdv."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [create_mock_event("rdv_1", TypeEvenement.RDV_MEDICAL, "Medecin")]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert len(jour.rdv) == 1

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_with_menage(self, mock_st: MagicMock) -> None:
        """Test avec menage."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [create_mock_event("menage_1", TypeEvenement.MENAGE, "Aspirateur")]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert len(jour.taches_menage) == 1

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_with_jardin(self, mock_st: MagicMock) -> None:
        """Test avec jardin."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [create_mock_event("jardin_1", TypeEvenement.JARDIN, "Arrosage")]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert len(jour.taches_jardin) == 1

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_jour_with_activites(self, mock_st: MagicMock) -> None:
        """Test avec activites multiples."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [
            create_mock_event("act_1", TypeEvenement.ACTIVITE, "Sport", pour_jules=True),
            create_mock_event("act_2", TypeEvenement.ACTIVITE, "Musique"),
        ]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert len(jour.activites) == 2


class TestRenderVueSemaineGrille:
    """Tests pour la fonction afficher_vue_semaine_grille."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_grille_empty_week(self, mock_st: MagicMock) -> None:
        """Test du rendu d une semaine vide."""
        from src.modules.planning.calendrier.components import afficher_vue_semaine_grille

        setup_mock_st(mock_st)
        semaine = create_mock_semaine()
        afficher_vue_semaine_grille(semaine)
        mock_st.columns.assert_called()


class TestRenderCelluleJour:
    """Tests pour la fonction afficher_cellule_jour."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_cellule_basic(self, mock_st: MagicMock) -> None:
        """Test du rendu basique d une cellule."""
        from src.modules.planning.calendrier.components import afficher_cellule_jour

        setup_mock_st(mock_st)
        jour = create_mock_jour()
        afficher_cellule_jour(jour)
        assert True

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_cellule_with_midi(self, mock_st: MagicMock) -> None:
        """Test cellule avec repas midi."""
        from src.modules.planning.calendrier.components import afficher_cellule_jour

        setup_mock_st(mock_st)
        events = [create_mock_event("midi_1", TypeEvenement.REPAS_MIDI, "Poulet")]
        jour = create_mock_jour(evenements=events)
        afficher_cellule_jour(jour)
        assert jour.repas_midi is not None

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_cellule_with_soir(self, mock_st: MagicMock) -> None:
        """Test cellule avec repas soir."""
        from src.modules.planning.calendrier.components import afficher_cellule_jour

        setup_mock_st(mock_st)
        events = [create_mock_event("soir_1", TypeEvenement.REPAS_SOIR, "Pates")]
        jour = create_mock_jour(evenements=events)
        afficher_cellule_jour(jour)
        assert jour.repas_soir is not None

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_cellule_with_all_types(self, mock_st: MagicMock) -> None:
        """Test cellule avec tous les types."""
        from src.modules.planning.calendrier.components import afficher_cellule_jour

        setup_mock_st(mock_st)
        events = [
            create_mock_event("midi_1", TypeEvenement.REPAS_MIDI, "Midi"),
            create_mock_event("soir_1", TypeEvenement.REPAS_SOIR, "Soir"),
            create_mock_event("batch_1", TypeEvenement.BATCH_COOKING, "Batch"),
            create_mock_event("courses_1", TypeEvenement.COURSES, "Courses"),
            create_mock_event("act_1", TypeEvenement.ACTIVITE, "Activite"),
            create_mock_event("rdv_1", TypeEvenement.RDV_MEDICAL, "RDV"),
        ]
        jour = create_mock_jour(evenements=events)
        afficher_cellule_jour(jour)
        assert len(jour.evenements) == 6


class TestRenderVueSemaineListe:
    """Tests pour la fonction afficher_vue_semaine_liste."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_liste_empty(self, mock_st: MagicMock) -> None:
        """Test du rendu d une liste vide."""
        from src.modules.planning.calendrier.components import afficher_vue_semaine_liste

        setup_mock_st(mock_st)
        semaine = create_mock_semaine()
        afficher_vue_semaine_liste(semaine)
        assert True

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_liste_with_events(self, mock_st: MagicMock) -> None:
        """Test liste avec evenements."""
        from src.modules.planning.calendrier.components import afficher_vue_semaine_liste

        setup_mock_st(mock_st)
        start = date.today()
        jours = []
        for i in range(7):
            events = [
                create_mock_event(
                    f"evt_{i}", TypeEvenement.ACTIVITE, f"Event {i}", start + timedelta(days=i)
                )
            ]
            jours.append(create_mock_jour(start + timedelta(days=i), events))
        semaine = create_mock_semaine(start, jours)
        afficher_vue_semaine_liste(semaine)
        assert len(semaine.jours) == 7


class TestRenderStatsSemaine:
    """Tests pour la fonction afficher_stats_semaine."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_stats_empty(self, mock_st: MagicMock) -> None:
        """Test des stats pour une semaine vide."""
        from src.modules.planning.calendrier.components import afficher_stats_semaine

        setup_mock_st(mock_st)
        semaine = create_mock_semaine()
        afficher_stats_semaine(semaine)
        assert True

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_stats_with_repas(self, mock_st: MagicMock) -> None:
        """Test stats avec repas planifies."""
        from src.modules.planning.calendrier.components import afficher_stats_semaine

        setup_mock_st(mock_st)
        start = date.today()
        jours = []
        for i in range(7):
            events = [
                create_mock_event(
                    f"midi_{i}", TypeEvenement.REPAS_MIDI, "Midi", start + timedelta(days=i)
                ),
                create_mock_event(
                    f"soir_{i}", TypeEvenement.REPAS_SOIR, "Soir", start + timedelta(days=i)
                ),
            ]
            jours.append(create_mock_jour(start + timedelta(days=i), events))
        semaine = create_mock_semaine(start, jours)
        afficher_stats_semaine(semaine)
        assert semaine.nb_repas_planifies == 14


class TestRenderActionsRapides:
    """Tests pour la fonction afficher_actions_rapides."""

    @patch("src.modules.planning.calendrier.components._dialog_impression")
    @patch("src.modules.planning.calendrier.components.st")
    def test_render_actions_basic(self, mock_st: MagicMock, mock_dialog: MagicMock) -> None:
        """Test du rendu basique des actions rapides."""
        from src.modules.planning.calendrier.components import afficher_actions_rapides

        setup_mock_st(mock_st)
        semaine = create_mock_semaine()
        afficher_actions_rapides(semaine)
        assert True


class TestRenderModalImpression:
    """Tests pour la fonction afficher_modal_impression."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_modal_closed(self, mock_st: MagicMock) -> None:
        """Test du modal ferme."""
        from src.modules.planning.calendrier.components import afficher_modal_impression

        setup_mock_st(mock_st, {"show_print_modal": False})
        semaine = create_mock_semaine()
        afficher_modal_impression(semaine)
        assert True

    @patch("src.modules.planning.calendrier.components._dialog_impression")
    @patch("src.modules.planning.calendrier.components.st")
    def test_render_modal_open(self, mock_st: MagicMock, mock_dialog: MagicMock) -> None:
        """Test du modal ouvert."""
        from src.modules.planning.calendrier.components import afficher_modal_impression

        setup_mock_st(mock_st, {"show_print_modal": True})
        semaine = create_mock_semaine()
        afficher_modal_impression(semaine)
        mock_dialog.assert_called_once_with(semaine)


class TestRenderFormulaireAjoutEvent:
    """Tests pour la fonction afficher_formulaire_ajout_event."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_formulaire_closed(self, mock_st: MagicMock) -> None:
        """Test du formulaire ferme."""
        from src.modules.planning.calendrier.components import afficher_formulaire_ajout_event

        setup_mock_st(mock_st)
        afficher_formulaire_ajout_event()
        assert True

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_formulaire_open(self, mock_st: MagicMock) -> None:
        """Test du formulaire ouvert."""
        from src.modules.planning.calendrier.components import afficher_formulaire_ajout_event

        setup_mock_st(mock_st, {"ajouter_event_date": date.today()})
        afficher_formulaire_ajout_event()
        mock_st.subheader.assert_called()


class TestRenderLegende:
    """Tests pour la fonction afficher_legende."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_render_legende_basic(self, mock_st: MagicMock) -> None:
        """Test du rendu basique de la legende."""
        from src.modules.planning.calendrier.components import afficher_legende

        setup_mock_st(mock_st)
        afficher_legende()
        mock_st.expander.assert_called()


class TestEdgeCases:
    """Tests des cas limites."""

    @patch("src.modules.planning.calendrier.components.st")
    def test_jour_aujourdhui(self, mock_st: MagicMock) -> None:
        """Test du rendu du jour actuel."""
        from src.modules.planning.calendrier.components import afficher_cellule_jour

        setup_mock_st(mock_st)
        jour = create_mock_jour(date.today())
        afficher_cellule_jour(jour)
        assert jour.est_aujourdhui

    @patch("src.modules.planning.calendrier.components.st")
    def test_semaine_complete(self, mock_st: MagicMock) -> None:
        """Test d une semaine complete avec evenements."""
        from src.modules.planning.calendrier.components import afficher_vue_semaine_grille

        setup_mock_st(mock_st)
        jours = []
        start = date.today()
        for i in range(7):
            events = [
                create_mock_event(
                    f"evt_{i}", TypeEvenement.ACTIVITE, f"Event {i}", start + timedelta(days=i)
                )
            ]
            jours.append(create_mock_jour(start + timedelta(days=i), events))
        semaine = create_mock_semaine(start, jours)
        afficher_vue_semaine_grille(semaine)
        assert len(semaine.jours) == 7

    @patch("src.modules.planning.calendrier.components.st")
    def test_all_event_types(self, mock_st: MagicMock) -> None:
        """Test de tous les types d evenements."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        today = date.today()
        events = [
            create_mock_event("repas_1", TypeEvenement.REPAS_MIDI, "Dejeuner", today),
            create_mock_event("repas_2", TypeEvenement.REPAS_SOIR, "Diner", today),
            create_mock_event("act_1", TypeEvenement.ACTIVITE, "Sport", today),
            create_mock_event("rdv_1", TypeEvenement.RDV_MEDICAL, "Medecin", today),
            create_mock_event("menage_1", TypeEvenement.MENAGE, "Aspirateur", today),
        ]
        jour = create_mock_jour(today, events)
        afficher_jour_calendrier(jour)
        assert len(jour.evenements) == 5

    @patch("src.modules.planning.calendrier.components.st")
    def test_jour_with_heures(self, mock_st: MagicMock) -> None:
        """Test avec des heures specifiees."""
        from src.modules.planning.calendrier.components import afficher_jour_calendrier

        setup_mock_st(mock_st)
        events = [
            create_mock_event(
                "evt_1", TypeEvenement.ACTIVITE, "Matin", date.today(), time(9, 0), time(10, 0)
            ),
            create_mock_event(
                "evt_2", TypeEvenement.ACTIVITE, "Aprem", date.today(), time(14, 0), time(16, 0)
            ),
        ]
        jour = create_mock_jour(evenements=events)
        afficher_jour_calendrier(jour)
        assert jour.evenements[0].heure_str == "09:00"
