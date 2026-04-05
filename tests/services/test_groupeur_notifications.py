"""
Tests unitaires pour GroupeurNotifications.

Couvre: regroupement, digest HTML, priorités, icônes.
"""

import pytest

from src.services.core.notifications.groupeur import (
    GroupeurNotifications,
    NotificationPendante,
    TYPE_ICONES,
)


class TestGroupeurNotifications:
    """Tests pour le groupeur de notifications."""

    @pytest.fixture
    def groupeur(self):
        return GroupeurNotifications()

    def test_ajouter_notification(self, groupeur):
        """Ajouter une notification → compteur incrémenté."""
        groupeur.ajouter("cuisine", "Repas planifié", "Planning semaine validé")
        assert groupeur.nombre_pendantes == 1

    def test_ajouter_plusieurs(self, groupeur):
        """Ajouter plusieurs notifications de modules différents."""
        groupeur.ajouter("cuisine", "Repas planifié", "Planning validé")
        groupeur.ajouter("jardin", "Arrosage nécessaire", "Les tomates ont soif")
        groupeur.ajouter("maison", "Entretien prévu", "Vider les filtres")
        assert groupeur.nombre_pendantes == 3

    def test_digest_vide(self, groupeur):
        """Aucune notification → digest vide."""
        assert groupeur.construire_digest() == ""

    def test_digest_contient_titre(self, groupeur):
        """Le digest contient le titre custom."""
        groupeur.ajouter("cuisine", "Test", "msg")
        digest = groupeur.construire_digest(titre_digest="🌅 Bonjour !")
        assert "🌅 Bonjour !" in digest

    def test_digest_format_html(self, groupeur):
        """Le digest utilise le format HTML Telegram."""
        groupeur.ajouter("cuisine", "Repas planifié", "Planning")
        digest = groupeur.construire_digest()
        assert "<b>" in digest

    def test_notifications_critiques(self, groupeur):
        """Notifications priorité ≤ 2 → section critique."""
        groupeur.ajouter("sante", "Urgence", "Alerte santé", priorite=1)
        groupeur.ajouter("cuisine", "Info", "Recette du jour", priorite=4)
        digest = groupeur.construire_digest()
        assert "priorité" in digest.lower()
        assert groupeur.a_des_critiques is True

    def test_pas_de_critiques(self, groupeur):
        """Aucune notification critique."""
        groupeur.ajouter("cuisine", "Info", "test", priorite=3)
        assert groupeur.a_des_critiques is False

    def test_vider(self, groupeur):
        """Vider le groupeur → 0 pendantes."""
        groupeur.ajouter("cuisine", "Test", "msg")
        groupeur.ajouter("maison", "Test2", "msg2")
        groupeur.vider()
        assert groupeur.nombre_pendantes == 0

    def test_icone_module_connu(self, groupeur):
        """Module connu → icône correcte."""
        groupeur.ajouter("jardin", "Test", "msg")
        assert groupeur._pendantes[0].icone == "🌱"

    def test_icone_module_inconnu(self, groupeur):
        """Module inconnu → icône par défaut 📌."""
        groupeur.ajouter("inconnu", "Test", "msg")
        assert groupeur._pendantes[0].icone == "📌"

    def test_digest_max_5_par_module(self, groupeur):
        """Maximum 5 notifications affichées par module dans le digest."""
        for i in range(8):
            groupeur.ajouter("cuisine", f"Notif {i}", f"Message {i}", priorite=4)
        digest = groupeur.construire_digest()
        assert "et 3 autres" in digest

    def test_digest_tri_priorite(self, groupeur):
        """Les notifications sont triées par priorité."""
        groupeur.ajouter("maison", "Bas", "basse prio", priorite=5)
        groupeur.ajouter("sante", "Urgent", "critique", priorite=1)
        groupeur.ajouter("cuisine", "Normal", "normal", priorite=3)
        digest = groupeur.construire_digest()
        # La critique doit apparaître avant les normales
        idx_urgent = digest.index("Urgent")
        idx_normal = digest.index("Normal")
        assert idx_urgent < idx_normal

    def test_footer_singulier(self, groupeur):
        """1 notification → singulier dans le footer."""
        groupeur.ajouter("cuisine", "Test", "msg")
        digest = groupeur.construire_digest()
        assert "1 notification regroupée" in digest

    def test_footer_pluriel(self, groupeur):
        """Plusieurs notifications → pluriel dans le footer."""
        groupeur.ajouter("cuisine", "Test1", "msg")
        groupeur.ajouter("maison", "Test2", "msg")
        digest = groupeur.construire_digest()
        assert "2 notifications regroupées" in digest
