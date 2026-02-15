"""
UI Feedback - Progress tracking
"""

import time
from datetime import datetime

import streamlit as st


class SuiviProgression:
    """
    Tracker de progression pour opérations longues

    Usage:
        progression = SuiviProgression("Import recettes", total=100)
        for i, item in enumerate(items):
            process_item(item)
            progression.mettre_a_jour(i+1, f"Traitement: {item.name}")
        progression.terminer()
    """

    def __init__(self, operation: str, total: int, afficher_pourcentage: bool = True):
        self.operation = operation
        self.total = total
        self.afficher_pourcentage = afficher_pourcentage
        self.courant = 0
        self.debut = datetime.now()

        # Créer éléments Streamlit
        self.titre_placeholder = st.empty()
        self.barre_progression = st.progress(0)
        self.statut_placeholder = st.empty()

        self._mettre_a_jour_affichage()

    def mettre_a_jour(self, courant: int, statut: str = ""):
        """
        Met à jour la progression

        Args:
            courant: Valeur actuelle (0 à total)
            statut: Message de statut
        """
        self.courant = courant
        self._mettre_a_jour_affichage(statut)

    def incrementer(self, pas: int = 1, statut: str = ""):
        """Incrémente la progression"""
        self.courant = min(self.courant + pas, self.total)
        self._mettre_a_jour_affichage(statut)

    def terminer(self, message: str = ""):
        """Marque comme terminé"""
        self.courant = self.total
        self._mettre_a_jour_affichage()

        temps_ecoule = (datetime.now() - self.debut).total_seconds()

        if message:
            self.statut_placeholder.success(f"✅ {message} (en {temps_ecoule:.1f}s)")
        else:
            self.statut_placeholder.success(f"✅ Terminé en {temps_ecoule:.1f}s")

        # Nettoyer après 2s
        time.sleep(2)
        self.titre_placeholder.empty()
        self.barre_progression.empty()

    def erreur(self, message: str):
        """Affiche une erreur"""
        self.statut_placeholder.error(f"❌ {message}")

    def _mettre_a_jour_affichage(self, statut: str = ""):
        """Met à jour l'affichage"""
        pct_progression = self.courant / self.total if self.total > 0 else 0

        # Titre avec pourcentage
        if self.afficher_pourcentage:
            titre = f"{self.operation} - {pct_progression * 100:.0f}%"
        else:
            titre = f"{self.operation} - {self.courant}/{self.total}"

        self.titre_placeholder.markdown(f"**{titre}**")

        # Barre de progression
        self.barre_progression.progress(pct_progression)

        # Estimation temps restant
        if self.courant > 0 and self.courant < self.total:
            temps_ecoule = (datetime.now() - self.debut).total_seconds()
            estimation_total = temps_ecoule / self.courant * self.total
            restant = estimation_total - temps_ecoule

            msg_statut = f"⏱️ Temps restant: ~{restant:.0f}s"

            if statut:
                msg_statut = f"{statut} • {msg_statut}"

            self.statut_placeholder.caption(msg_statut)
        elif statut:
            self.statut_placeholder.caption(statut)


class EtatChargement:
    """
    Gestion d'états de chargement multiples

    Usage:
        chargement = EtatChargement("Chargement données")

        chargement.ajouter_etape("Connexion DB")
        # ... code ...
        chargement.terminer_etape("Connexion DB")

        chargement.ajouter_etape("Import recettes")
        # ... code ...
        chargement.terminer_etape("Import recettes")

        chargement.finaliser()
    """

    def __init__(self, titre: str):
        self.titre = titre
        self.etapes: list[dict] = []
        self.etape_courante = None
        self.debut = datetime.now()

        # UI
        self.titre_placeholder = st.empty()
        self.etapes_placeholder = st.empty()

        self._mettre_a_jour_affichage()

    def ajouter_etape(self, nom_etape: str):
        """Ajoute une étape"""
        self.etapes.append(
            {
                "name": nom_etape,
                "status": "⏳ En cours...",
                "started_at": datetime.now(),
                "completed": False,
            }
        )
        self.etape_courante = len(self.etapes) - 1
        self._mettre_a_jour_affichage()

    def terminer_etape(self, nom_etape: str | None = None, succes: bool = True):
        """Marque une étape comme terminée"""
        # Trouver l'étape
        if nom_etape:
            idx_etape = next((i for i, s in enumerate(self.etapes) if s["name"] == nom_etape), None)
        else:
            idx_etape = self.etape_courante

        if idx_etape is not None and idx_etape < len(self.etapes):
            etape = self.etapes[idx_etape]

            temps_ecoule = (datetime.now() - etape["started_at"]).total_seconds()

            if succes:
                etape["status"] = f"✅ OK ({temps_ecoule:.1f}s)"
            else:
                etape["status"] = "❌ Erreur"

            etape["completed"] = True
            self._mettre_a_jour_affichage()

    def erreur_etape(self, nom_etape: str | None = None, msg_erreur: str = ""):
        """Marque une étape en erreur"""
        if nom_etape:
            idx_etape = next((i for i, s in enumerate(self.etapes) if s["name"] == nom_etape), None)
        else:
            idx_etape = self.etape_courante

        if idx_etape is not None and idx_etape < len(self.etapes):
            etape = self.etapes[idx_etape]
            etape["status"] = f"❌ {msg_erreur}" if msg_erreur else "❌ Erreur"
            etape["completed"] = True
            self._mettre_a_jour_affichage()

    def finaliser(self, message_succes: str = ""):
        """Termine le chargement"""
        temps_ecoule = (datetime.now() - self.debut).total_seconds()

        if message_succes:
            self.titre_placeholder.success(f"✅ {message_succes} (en {temps_ecoule:.1f}s)")
        else:
            self.titre_placeholder.success(f"✅ {self.titre} terminé (en {temps_ecoule:.1f}s)")

        # Nettoyer après 3s
        time.sleep(3)
        self.titre_placeholder.empty()
        self.etapes_placeholder.empty()

    def _mettre_a_jour_affichage(self):
        """Met à jour l'affichage"""
        terminees = sum(1 for s in self.etapes if s["completed"])
        total = len(self.etapes)

        titre = f"**{self.titre}** ({terminees}/{total})"
        self.titre_placeholder.markdown(titre)

        # Liste des étapes
        etapes_html = "<div style='padding: 1rem; background: #f8f9fa; border-radius: 8px;'>"

        for etape in self.etapes:
            etapes_html += "<div style='margin: 0.5rem 0;'>"
            etapes_html += f"<strong>{etape['name']}</strong> • {etape['status']}"
            etapes_html += "</div>"

        etapes_html += "</div>"

        self.etapes_placeholder.markdown(etapes_html, unsafe_allow_html=True)
