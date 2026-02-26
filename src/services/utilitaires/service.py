"""
Services utilitaires — Notes, Journal, Contacts, Liens, Énergie, Mots de passe.

Fournit les services CRUD et métier pour les nouvelles fonctionnalités
du module utilitaires.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src.core.db import obtenir_contexte_db
from src.core.models.utilitaires import (
    ContactUtile,
    EntreeJournal,
    LienFavori,
    MotDePasseMaison,
    NoteMemo,
    PressePapierEntree,
    ReleveEnergie,
)
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE NOTES / MÉMOS
# ═══════════════════════════════════════════════════════════


class NotesService:
    """Service CRUD pour les notes et mémos."""

    def lister(
        self,
        categorie: str | None = None,
        epingle_seulement: bool = False,
        inclure_archives: bool = False,
    ) -> list[NoteMemo]:
        """Liste les notes avec filtres optionnels."""
        with obtenir_contexte_db() as db:
            query = db.query(NoteMemo)
            if not inclure_archives:
                query = query.filter(NoteMemo.archive == False)  # noqa: E712
            if categorie:
                query = query.filter(NoteMemo.categorie == categorie)
            if epingle_seulement:
                query = query.filter(NoteMemo.epingle == True)  # noqa: E712
            return query.order_by(desc(NoteMemo.epingle), desc(NoteMemo.modifie_le)).all()

    def creer(self, **kwargs: Any) -> NoteMemo:
        """Crée une nouvelle note."""
        with obtenir_contexte_db() as db:
            note = NoteMemo(**kwargs)
            db.add(note)
            db.commit()
            db.refresh(note)
            return note

    def modifier(self, note_id: int, **kwargs: Any) -> NoteMemo | None:
        """Modifie une note existante."""
        with obtenir_contexte_db() as db:
            note = db.query(NoteMemo).get(note_id)
            if note:
                for key, value in kwargs.items():
                    setattr(note, key, value)
                db.commit()
                db.refresh(note)
            return note

    def supprimer(self, note_id: int) -> bool:
        """Supprime une note."""
        with obtenir_contexte_db() as db:
            note = db.query(NoteMemo).get(note_id)
            if note:
                db.delete(note)
                db.commit()
                return True
            return False

    def archiver(self, note_id: int) -> bool:
        """Archive une note."""
        return self.modifier(note_id, archive=True) is not None

    def basculer_epingle(self, note_id: int) -> NoteMemo | None:
        """Bascule l'état épinglé d'une note."""
        with obtenir_contexte_db() as db:
            note = db.query(NoteMemo).get(note_id)
            if note:
                note.epingle = not note.epingle
                db.commit()
                db.refresh(note)
            return note


@service_factory("notes_service", tags={"utilitaires"})
def get_notes_service() -> NotesService:
    """Factory singleton NotesService."""
    return NotesService()


# ═══════════════════════════════════════════════════════════
# SERVICE JOURNAL DE BORD
# ═══════════════════════════════════════════════════════════


class JournalService:
    """Service CRUD pour le journal de bord."""

    def lister(
        self,
        mois: int | None = None,
        annee: int | None = None,
        date_debut: date | None = None,
        date_fin: date | None = None,
    ) -> list[EntreeJournal]:
        """Liste les entrées du journal."""
        with obtenir_contexte_db() as db:
            query = db.query(EntreeJournal)
            if date_debut and date_fin:
                query = query.filter(
                    EntreeJournal.date_entree >= date_debut,
                    EntreeJournal.date_entree <= date_fin,
                )
            elif mois and annee:
                query = query.filter(
                    func.extract("month", EntreeJournal.date_entree) == mois,
                    func.extract("year", EntreeJournal.date_entree) == annee,
                )
            elif annee:
                query = query.filter(func.extract("year", EntreeJournal.date_entree) == annee)
            return query.order_by(desc(EntreeJournal.date_entree)).all()

    def obtenir_par_date(self, date_entree: date) -> EntreeJournal | None:
        """Obtient l'entrée du journal pour une date."""
        with obtenir_contexte_db() as db:
            return db.query(EntreeJournal).filter(EntreeJournal.date_entree == date_entree).first()

    def creer_ou_modifier(self, date_entree: date, **kwargs: Any) -> EntreeJournal:
        """Crée ou modifie l'entrée du jour."""
        with obtenir_contexte_db() as db:
            entree = (
                db.query(EntreeJournal).filter(EntreeJournal.date_entree == date_entree).first()
            )
            if entree:
                for key, value in kwargs.items():
                    setattr(entree, key, value)
            else:
                entree = EntreeJournal(date_entree=date_entree, **kwargs)
                db.add(entree)
            db.commit()
            db.refresh(entree)
            return entree

    def supprimer(self, entree_id: int) -> bool:
        """Supprime une entrée du journal."""
        with obtenir_contexte_db() as db:
            entree = db.query(EntreeJournal).get(entree_id)
            if entree:
                db.delete(entree)
                db.commit()
                return True
            return False

    def statistiques_humeur(self, annee: int | None = None) -> dict[str, int]:
        """Statistiques des humeurs sur une période."""
        with obtenir_contexte_db() as db:
            query = db.query(EntreeJournal.humeur, func.count(EntreeJournal.id)).filter(
                EntreeJournal.humeur.isnot(None)
            )
            if annee:
                query = query.filter(func.extract("year", EntreeJournal.date_entree) == annee)
            results = query.group_by(EntreeJournal.humeur).all()
            return {humeur: count for humeur, count in results}

    def statistiques(self, jours: int = 30) -> dict:
        """Statistiques complètes du journal sur N jours."""
        from datetime import timedelta

        date_limite = date.today() - timedelta(days=jours)
        with obtenir_contexte_db() as db:
            entrees = db.query(EntreeJournal).filter(EntreeJournal.date_entree >= date_limite).all()
            if not entrees:
                return {}

            # Distribution humeurs
            distribution = {}
            for e in entrees:
                if e.humeur:
                    distribution[e.humeur] = distribution.get(e.humeur, 0) + 1

            # Humeur dominante
            humeur_dominante = max(distribution, key=distribution.get) if distribution else "N/A"

            # Énergie moyenne
            energies = [e.energie for e in entrees if e.energie is not None]
            energie_moyenne = sum(energies) / len(energies) if energies else 0

            return {
                "total_entrees": len(entrees),
                "humeur_dominante": humeur_dominante,
                "energie_moyenne": energie_moyenne,
                "distribution_humeurs": distribution,
            }


@service_factory("journal_service", tags={"utilitaires"})
def get_journal_service() -> JournalService:
    """Factory singleton JournalService."""
    return JournalService()


# ═══════════════════════════════════════════════════════════
# SERVICE CONTACTS
# ═══════════════════════════════════════════════════════════


class ContactsService:
    """Service CRUD pour l'annuaire de contacts."""

    def lister(
        self, categorie: str | None = None, recherche: str | None = None
    ) -> list[ContactUtile]:
        """Liste les contacts avec filtres optionnels."""
        with obtenir_contexte_db() as db:
            query = db.query(ContactUtile)
            if categorie:
                query = query.filter(ContactUtile.categorie == categorie)
            if recherche:
                motif = f"%{recherche}%"
                query = query.filter(
                    ContactUtile.nom.ilike(motif)
                    | ContactUtile.specialite.ilike(motif)
                    | ContactUtile.notes.ilike(motif)
                )
            return query.order_by(desc(ContactUtile.favori), ContactUtile.nom).all()

    def creer(self, **kwargs: Any) -> ContactUtile:
        """Crée un contact."""
        with obtenir_contexte_db() as db:
            contact = ContactUtile(**kwargs)
            db.add(contact)
            db.commit()
            db.refresh(contact)
            return contact

    def modifier(self, contact_id: int, **kwargs: Any) -> ContactUtile | None:
        """Modifie un contact."""
        with obtenir_contexte_db() as db:
            contact = db.query(ContactUtile).get(contact_id)
            if contact:
                for key, value in kwargs.items():
                    setattr(contact, key, value)
                db.commit()
                db.refresh(contact)
            return contact

    def supprimer(self, contact_id: int) -> bool:
        """Supprime un contact."""
        with obtenir_contexte_db() as db:
            contact = db.query(ContactUtile).get(contact_id)
            if contact:
                db.delete(contact)
                db.commit()
                return True
            return False


@service_factory("contacts_service", tags={"utilitaires"})
def get_contacts_service() -> ContactsService:
    """Factory singleton ContactsService."""
    return ContactsService()


# ═══════════════════════════════════════════════════════════
# SERVICE LIENS FAVORIS
# ═══════════════════════════════════════════════════════════


class LiensService:
    """Service CRUD pour les liens/bookmarks."""

    def lister(self, categorie: str | None = None) -> list[LienFavori]:
        """Liste les liens favoris."""
        with obtenir_contexte_db() as db:
            query = db.query(LienFavori)
            if categorie:
                query = query.filter(LienFavori.categorie == categorie)
            return query.order_by(desc(LienFavori.favori), desc(LienFavori.modifie_le)).all()

    def creer(self, **kwargs: Any) -> LienFavori:
        """Crée un lien."""
        with obtenir_contexte_db() as db:
            lien = LienFavori(**kwargs)
            db.add(lien)
            db.commit()
            db.refresh(lien)
            return lien

    def modifier(self, lien_id: int, **kwargs: Any) -> LienFavori | None:
        """Modifie un lien."""
        with obtenir_contexte_db() as db:
            lien = db.query(LienFavori).get(lien_id)
            if lien:
                for key, value in kwargs.items():
                    setattr(lien, key, value)
                db.commit()
                db.refresh(lien)
            return lien

    def supprimer(self, lien_id: int) -> bool:
        """Supprime un lien."""
        with obtenir_contexte_db() as db:
            lien = db.query(LienFavori).get(lien_id)
            if lien:
                db.delete(lien)
                db.commit()
                return True
            return False


@service_factory("liens_service", tags={"utilitaires"})
def get_liens_service() -> LiensService:
    """Factory singleton LiensService."""
    return LiensService()


# ═══════════════════════════════════════════════════════════
# SERVICE MOTS DE PASSE
# ═══════════════════════════════════════════════════════════


class MotsDePasseService:
    """Service pour les mots de passe/codes maison avec chiffrement Fernet."""

    def __init__(self):
        self._fernet = None

    def _get_fernet(self, cle_pin: str):
        """Obtient l'instance Fernet à partir d'un PIN."""
        import base64
        import hashlib

        from cryptography.fernet import Fernet

        # Dériver une clé Fernet à partir du PIN
        key = hashlib.sha256(cle_pin.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key)
        return Fernet(fernet_key)

    def chiffrer(self, valeur: str, pin: str) -> str:
        """Chiffre une valeur avec le PIN."""
        fernet = self._get_fernet(pin)
        return fernet.encrypt(valeur.encode()).decode()

    def dechiffrer(self, valeur_chiffree: str, pin: str) -> str | None:
        """Déchiffre une valeur avec le PIN."""
        try:
            fernet = self._get_fernet(pin)
            return fernet.decrypt(valeur_chiffree.encode()).decode()
        except Exception:
            return None

    def lister(self, categorie: str | None = None) -> list[MotDePasseMaison]:
        """Liste les mots de passe (sans déchiffrer)."""
        with obtenir_contexte_db() as db:
            query = db.query(MotDePasseMaison)
            if categorie:
                query = query.filter(MotDePasseMaison.categorie == categorie)
            return query.order_by(MotDePasseMaison.nom).all()

    def creer(self, pin: str, valeur_claire: str, **kwargs: Any) -> MotDePasseMaison:
        """Crée un mot de passe chiffré."""
        valeur_chiffree = self.chiffrer(valeur_claire, pin)
        with obtenir_contexte_db() as db:
            mdp = MotDePasseMaison(valeur_chiffree=valeur_chiffree, **kwargs)
            db.add(mdp)
            db.commit()
            db.refresh(mdp)
            return mdp

    def supprimer(self, mdp_id: int) -> bool:
        """Supprime un mot de passe."""
        with obtenir_contexte_db() as db:
            mdp = db.query(MotDePasseMaison).get(mdp_id)
            if mdp:
                db.delete(mdp)
                db.commit()
                return True
            return False


@service_factory("mots_de_passe_service", tags={"utilitaires", "securite"})
def get_mots_de_passe_service() -> MotsDePasseService:
    """Factory singleton MotsDePasseService."""
    return MotsDePasseService()


# ═══════════════════════════════════════════════════════════
# SERVICE PRESSE-PAPIERS
# ═══════════════════════════════════════════════════════════


class PressePapiersService:
    """Service pour le presse-papiers partagé."""

    def lister(self, limite: int = 20) -> list[PressePapierEntree]:
        """Liste les dernières entrées du presse-papiers."""
        with obtenir_contexte_db() as db:
            return (
                db.query(PressePapierEntree)
                .order_by(desc(PressePapierEntree.epingle), desc(PressePapierEntree.cree_le))
                .limit(limite)
                .all()
            )

    def ajouter(self, contenu: str, auteur: str | None = None) -> PressePapierEntree:
        """Ajoute une entrée."""
        with obtenir_contexte_db() as db:
            entree = PressePapierEntree(contenu=contenu, auteur=auteur)
            db.add(entree)
            db.commit()
            db.refresh(entree)
            return entree

    def supprimer(self, entree_id: int) -> bool:
        """Supprime une entrée."""
        with obtenir_contexte_db() as db:
            entree = db.query(PressePapierEntree).get(entree_id)
            if entree:
                db.delete(entree)
                db.commit()
                return True
            return False

    def basculer_epingle(self, entree_id: int) -> PressePapierEntree | None:
        """Bascule l'épinglage."""
        with obtenir_contexte_db() as db:
            entree = db.query(PressePapierEntree).get(entree_id)
            if entree:
                entree.epingle = not entree.epingle
                db.commit()
                db.refresh(entree)
            return entree


@service_factory("presse_papiers_service", tags={"utilitaires"})
def get_presse_papiers_service() -> PressePapiersService:
    """Factory singleton PressePapiersService."""
    return PressePapiersService()


# ═══════════════════════════════════════════════════════════
# SERVICE ÉNERGIE
# ═══════════════════════════════════════════════════════════


class EnergieService:
    """Service pour le suivi consommation énergie."""

    def lister(
        self,
        type_energie: str | None = None,
        annee: int | None = None,
    ) -> list[ReleveEnergie]:
        """Liste les relevés."""
        with obtenir_contexte_db() as db:
            query = db.query(ReleveEnergie)
            if type_energie:
                query = query.filter(ReleveEnergie.type_energie == type_energie)
            if annee:
                query = query.filter(ReleveEnergie.annee == annee)
            return query.order_by(desc(ReleveEnergie.annee), desc(ReleveEnergie.mois)).all()

    def creer(self, **kwargs: Any) -> ReleveEnergie:
        """Crée un relevé."""
        with obtenir_contexte_db() as db:
            releve = ReleveEnergie(**kwargs)
            db.add(releve)
            db.commit()
            db.refresh(releve)
            return releve

    def modifier(self, releve_id: int, **kwargs: Any) -> ReleveEnergie | None:
        """Modifie un relevé."""
        with obtenir_contexte_db() as db:
            releve = db.query(ReleveEnergie).get(releve_id)
            if releve:
                for key, value in kwargs.items():
                    setattr(releve, key, value)
                db.commit()
                db.refresh(releve)
            return releve

    def supprimer(self, releve_id: int) -> bool:
        """Supprime un relevé."""
        with obtenir_contexte_db() as db:
            releve = db.query(ReleveEnergie).get(releve_id)
            if releve:
                db.delete(releve)
                db.commit()
                return True
            return False

    def totaux_annuels(self, annee: int) -> dict[str, dict]:
        """Calcule les totaux annuels par type d'énergie."""
        with obtenir_contexte_db() as db:
            results = (
                db.query(
                    ReleveEnergie.type_energie,
                    func.sum(ReleveEnergie.consommation).label("total_conso"),
                    func.sum(ReleveEnergie.montant).label("total_montant"),
                    func.count(ReleveEnergie.id).label("nb_releves"),
                )
                .filter(ReleveEnergie.annee == annee)
                .group_by(ReleveEnergie.type_energie)
                .all()
            )
            return {
                r.type_energie: {
                    "total_consommation": float(r.total_conso or 0),
                    "total_montant": float(r.total_montant or 0),
                    "nb_releves": r.nb_releves,
                }
                for r in results
            }


@service_factory("energie_service", tags={"utilitaires", "maison"})
def get_energie_service() -> EnergieService:
    """Factory singleton EnergieService."""
    return EnergieService()
