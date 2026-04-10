"""Service checklist anniversaires.

Objectif: proposer et synchroniser une checklist vivante
(âge, intérêts, préférences, échéance) sans écraser les items manuels.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import (
    AchatFamille,
    AnniversaireFamille,
    ChecklistAnniversaire,
    ItemChecklistAnniversaire,
    PreferenceUtilisateur,
)
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory


def _relation_est_enfant(relation: str | None) -> bool:
    if not relation:
        return False
    return relation.lower() in {"enfant", "fils", "fille", "neveu", "niece", "nièce"}


def _profil_anniversaire(age: int, relation: str | None) -> str:
    if age <= 3:
        return "tout_petit"
    if age <= 7:
        return "enfant"
    if age <= 12:
        return "pre_ado"
    if age <= 17:
        return "ado"
    if _relation_est_enfant(relation):
        return "enfant"
    return "adulte"


def _template_categorie_par_profil(profil: str) -> dict[str, list[dict[str, Any]]]:
    if profil in {"tout_petit", "enfant", "pre_ado"}:
        return {
            "cadeau": [
                {
                    "libelle": "Cadeau principal",
                    "budget_estime": 40.0,
                    "priorite": "haute",
                    "quand": "j-7",
                },
                {
                    "libelle": "Petit cadeau bonus",
                    "budget_estime": 15.0,
                    "priorite": "moyenne",
                    "quand": "j-3",
                },
            ],
            "activite": [
                {
                    "libelle": "Animation / activité ludique",
                    "budget_estime": 35.0,
                    "priorite": "moyenne",
                    "quand": "j-7",
                },
            ],
            "repas": [
                {
                    "libelle": "Goûter + boissons",
                    "budget_estime": 30.0,
                    "priorite": "haute",
                    "quand": "j-2",
                },
            ],
            "decoration": [
                {
                    "libelle": "Ballons et décoration",
                    "budget_estime": 20.0,
                    "priorite": "moyenne",
                    "quand": "j-3",
                },
            ],
        }
    return {
        "cadeau": [
            {
                "libelle": "Cadeau principal",
                "budget_estime": 60.0,
                "priorite": "haute",
                "quand": "j-7",
            },
        ],
        "repas": [
            {
                "libelle": "Repas / dîner",
                "budget_estime": 80.0,
                "priorite": "haute",
                "quand": "j-3",
            },
        ],
        "organisation": [
            {
                "libelle": "Invitations / coordination",
                "budget_estime": 0.0,
                "priorite": "moyenne",
                "quand": "j-14",
            },
        ],
        "decoration": [
            {
                "libelle": "Ambiance légère",
                "budget_estime": 20.0,
                "priorite": "basse",
                "quand": "j-2",
            },
        ],
    }


class ServiceChecklistsAnniversaire(BaseService[ChecklistAnniversaire]):
    """Gère les checklists anniversaires avec synchronisation auto."""

    def __init__(self) -> None:
        super().__init__(model=ChecklistAnniversaire, cache_ttl=300)

    def _preferences(self, db: Session, user_id: str | None) -> PreferenceUtilisateur | None:
        if user_id:
            pref = (
                db.query(PreferenceUtilisateur)
                .filter(PreferenceUtilisateur.user_id == user_id)
                .first()
            )
            if pref:
                return pref
        return db.query(PreferenceUtilisateur).order_by(desc(PreferenceUtilisateur.id)).first()

    def _achats_recents(self, db: Session, relation: str | None) -> list[AchatFamille]:
        query = db.query(AchatFamille).filter(AchatFamille.achete.is_(True))
        if _relation_est_enfant(relation):
            query = query.filter(AchatFamille.pour_qui.in_(["jules", "famille"]))
        return query.order_by(desc(AchatFamille.date_achat), desc(AchatFamille.id)).limit(50).all()

    def _suggestions_dynamiques(
        self,
        anniv: AnniversaireFamille,
        pref: PreferenceUtilisateur | None,
        achats: list[AchatFamille],
    ) -> list[dict[str, Any]]:
        profil = _profil_anniversaire(anniv.age, anniv.relation)
        templates = _template_categorie_par_profil(profil)

        items: list[dict[str, Any]] = []
        ordre = 10
        for categorie, elements in templates.items():
            for element in elements:
                items.append(
                    {
                        "categorie": categorie,
                        "libelle": element["libelle"],
                        "budget_estime": element.get("budget_estime"),
                        "priorite": element.get("priorite", "moyenne"),
                        "quand": element.get("quand"),
                        "source": "auto",
                        "score_pertinence": 0.8,
                        "raison_suggestion": f"Profil {profil} + relation {anniv.relation}",
                        "ordre": ordre,
                    }
                )
                ordre += 10

        # Boost intérêts culture/gaming pour ados/adultes
        interets = []
        if pref:
            interets.extend(pref.interets_gaming or [])
            interets.extend(pref.interets_culture or [])
        if interets:
            items.append(
                {
                    "categorie": "cadeau",
                    "libelle": f"Idée cadeau intérêt: {interets[0]}",
                    "budget_estime": 35.0,
                    "priorite": "moyenne",
                    "quand": "j-7",
                    "source": "auto",
                    "score_pertinence": 0.9,
                    "raison_suggestion": "Centre d'intérêt détecté dans les préférences",
                    "ordre": ordre,
                }
            )
            ordre += 10

        # Déduplication simple avec historique achats
        noms_achats = {a.nom.lower().strip() for a in achats if a.nom}
        filtres: list[dict[str, Any]] = []
        for item in items:
            if item["libelle"].lower().strip() not in noms_achats:
                filtres.append(item)

        # Temporalité: ajoute un rappel urgence en approche
        if anniv.jours_restants <= 7:
            filtres.append(
                {
                    "categorie": "organisation",
                    "libelle": "Vérifier confirmations invités",
                    "budget_estime": 0.0,
                    "priorite": "haute",
                    "quand": "j-1",
                    "source": "auto",
                    "score_pertinence": 0.95,
                    "raison_suggestion": "Anniversaire imminent (<=7 jours)",
                    "ordre": ordre,
                }
            )

        return filtres

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def generer_apercu_auto(
        self,
        anniversaire_id: int,
        user_id: str | None = None,
        *,
        db: Session | None = None,
    ) -> dict[str, Any]:
        if db is None:
            return {}
        anniv = (
            db.query(AnniversaireFamille)
            .filter(AnniversaireFamille.id == anniversaire_id, AnniversaireFamille.actif.is_(True))
            .first()
        )
        if not anniv:
            return {}

        pref = self._preferences(db, user_id)
        achats = self._achats_recents(db, anniv.relation)
        items_auto = self._suggestions_dynamiques(anniv, pref, achats)
        budget_total = round(sum(float(i.get("budget_estime") or 0) for i in items_auto), 2)

        return {
            "anniversaire_id": anniv.id,
            "nom_personne": anniv.nom_personne,
            "age": anniv.age,
            "jours_restants": anniv.jours_restants,
            "profil": _profil_anniversaire(anniv.age, anniv.relation),
            "budget_total_suggere": budget_total,
            "items_auto": items_auto,
            "genere_le": datetime.utcnow().isoformat(),
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def synchroniser_checklist_auto(
        self,
        anniversaire_id: int,
        user_id: str | None = None,
        force_recalcul_budget: bool = False,
        *,
        db: Session | None = None,
    ) -> dict[str, Any]:
        if db is None:
            return {}

        anniv = (
            db.query(AnniversaireFamille)
            .filter(AnniversaireFamille.id == anniversaire_id, AnniversaireFamille.actif.is_(True))
            .first()
        )
        if not anniv:
            return {}

        preview = self.generer_apercu_auto(anniversaire_id, user_id=user_id, db=db)
        if not preview:
            return {}

        checklist = (
            db.query(ChecklistAnniversaire)
            .filter(
                ChecklistAnniversaire.anniversaire_id == anniversaire_id,
                ChecklistAnniversaire.completee.is_(False),
            )
            .order_by(desc(ChecklistAnniversaire.id))
            .first()
        )
        if checklist is None:
            checklist = ChecklistAnniversaire(
                anniversaire_id=anniversaire_id,
                nom=f"Préparation anniversaire {anniv.nom_personne}",
                date_limite=anniv.prochain_anniversaire,
                budget_total=preview.get("budget_total_suggere"),
            )
            db.add(checklist)
            db.flush()

        # Ne jamais toucher aux items manuels
        db.query(ItemChecklistAnniversaire).filter(
            ItemChecklistAnniversaire.checklist_id == checklist.id,
            ItemChecklistAnniversaire.source == "auto",
        ).delete(synchronize_session=False)

        for item in preview.get("items_auto", []):
            db.add(
                ItemChecklistAnniversaire(
                    checklist_id=checklist.id,
                    categorie=item.get("categorie", "autre"),
                    libelle=item.get("libelle", "Item"),
                    budget_estime=item.get("budget_estime"),
                    priorite=item.get("priorite", "moyenne"),
                    quand=item.get("quand"),
                    source="auto",
                    score_pertinence=item.get("score_pertinence"),
                    raison_suggestion=item.get("raison_suggestion"),
                    ordre=item.get("ordre", 0),
                )
            )

        if force_recalcul_budget or checklist.budget_total is None:
            checklist.budget_total = preview.get("budget_total_suggere")
        checklist.maj_auto_le = datetime.utcnow()

        db.commit()
        db.refresh(checklist)

        obtenir_bus().emettre(
            "anniversaire.checklist_auto_sync",
            {
                "anniversaire_id": anniversaire_id,
                "checklist_id": checklist.id,
                "items_auto": len(preview.get("items_auto", [])),
            },
            source="ServiceChecklistsAnniversaire",
        )

        return self.serialiser_checklist(checklist, db)

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def lister_checklists(
        self, anniversaire_id: int, *, db: Session | None = None
    ) -> list[dict[str, Any]]:
        if db is None:
            return []
        checklists = (
            db.query(ChecklistAnniversaire)
            .filter(ChecklistAnniversaire.anniversaire_id == anniversaire_id)
            .order_by(desc(ChecklistAnniversaire.id))
            .all()
        )
        return [self.serialiser_checklist(c, db) for c in checklists]

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def ajouter_item_manuel(
        self,
        checklist_id: int,
        payload: dict[str, Any],
        *,
        db: Session | None = None,
    ) -> dict[str, Any]:
        if db is None:
            return {}
        checklist = (
            db.query(ChecklistAnniversaire).filter(ChecklistAnniversaire.id == checklist_id).first()
        )
        if not checklist:
            return {}

        item = ItemChecklistAnniversaire(
            checklist_id=checklist_id,
            categorie=payload.get("categorie", "autre"),
            libelle=payload.get("libelle", "Item"),
            budget_estime=payload.get("budget_estime"),
            priorite=payload.get("priorite", "moyenne"),
            responsable=payload.get("responsable"),
            quand=payload.get("quand"),
            source="manuel",
            ordre=payload.get("ordre", 1000),
            notes=payload.get("notes"),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return self.serialiser_item(item)

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def modifier_item(
        self,
        item_id: int,
        patch: dict[str, Any],
        *,
        db: Session | None = None,
    ) -> dict[str, Any]:
        if db is None:
            return {}
        item = (
            db.query(ItemChecklistAnniversaire)
            .filter(ItemChecklistAnniversaire.id == item_id)
            .first()
        )
        if not item:
            return {}

        for champ in [
            "fait",
            "budget_reel",
            "budget_estime",
            "priorite",
            "responsable",
            "quand",
            "notes",
            "libelle",
            "categorie",
        ]:
            if champ in patch:
                setattr(item, champ, patch[champ])

        db.commit()
        db.refresh(item)
        return self.serialiser_item(item)

    def serialiser_item(self, item: ItemChecklistAnniversaire) -> dict[str, Any]:
        return {
            "id": item.id,
            "checklist_id": item.checklist_id,
            "categorie": item.categorie,
            "libelle": item.libelle,
            "budget_estime": item.budget_estime,
            "budget_reel": item.budget_reel,
            "fait": item.fait,
            "priorite": item.priorite,
            "responsable": item.responsable,
            "quand": item.quand,
            "source": item.source,
            "score_pertinence": item.score_pertinence,
            "raison_suggestion": item.raison_suggestion,
            "ordre": item.ordre,
            "notes": item.notes,
            "cree_le": item.cree_le.isoformat() if item.cree_le else None,
        }

    def item_vers_achat_prefill(
        self,
        item_id: int,
        *,
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Retourne les données pré-remplies pour créer un achat depuis un item checklist."""
        if db is None:
            return {}
        item = (
            db.query(ItemChecklistAnniversaire)
            .filter(ItemChecklistAnniversaire.id == item_id)
            .first()
        )
        if not item:
            return {}

        checklist = (
            db.query(ChecklistAnniversaire)
            .filter(ChecklistAnniversaire.id == item.checklist_id)
            .first()
        )
        anniv_nom = ""
        pour_qui = "famille"
        if checklist:
            anniv = (
                db.query(AnniversaireFamille)
                .filter(AnniversaireFamille.id == checklist.anniversaire_id)
                .first()
            )
            if anniv:
                anniv_nom = anniv.nom_personne or ""
                relation = (anniv.relation or "").lower()
                if relation in {"jules", "enfant", "fils", "fille"}:
                    pour_qui = "jules"
                elif relation in {"anne", "maman"}:
                    pour_qui = "anne"
                elif relation in {"mathieu", "papa"}:
                    pour_qui = "mathieu"

        # Mapping catégorie checklist → catégorie achat
        _cat_map = {
            "cadeau": "cadeaux",
            "decoration": "maison",
            "repas": "alimentation",
            "activite": "loisirs",
            "gouter": "alimentation",
            "logistique": "maison",
        }
        categorie_achat = _cat_map.get(item.categorie, "divers")

        description = item.notes or (f"Anniversaire de {anniv_nom}" if anniv_nom else "")
        return {
            "nom": item.libelle,
            "categorie": categorie_achat,
            "prix_estime": item.budget_estime,
            "pour_qui": pour_qui,
            "description": description,
            "source_item_id": item_id,
            "source_checklist_id": item.checklist_id,
        }

    def serialiser_checklist(self, checklist: ChecklistAnniversaire, db: Session) -> dict[str, Any]:
        items = (
            db.query(ItemChecklistAnniversaire)
            .filter(ItemChecklistAnniversaire.checklist_id == checklist.id)
            .order_by(
                ItemChecklistAnniversaire.categorie.asc(), ItemChecklistAnniversaire.ordre.asc()
            )
            .all()
        )
        items_ser = [self.serialiser_item(i) for i in items]

        depense = sum(float(i.get("budget_reel") or 0) for i in items_ser)
        total = float(checklist.budget_total or 0)
        total_items = len(items_ser)
        total_faits = sum(1 for i in items_ser if i.get("fait"))

        par_categorie: dict[str, list[dict[str, Any]]] = {}
        for item in items_ser:
            par_categorie.setdefault(item["categorie"], []).append(item)

        return {
            "id": checklist.id,
            "anniversaire_id": checklist.anniversaire_id,
            "nom": checklist.nom,
            "budget_total": checklist.budget_total,
            "budget_depense": round(depense, 2),
            "budget_restant": round(total - depense, 2),
            "date_limite": checklist.date_limite.isoformat() if checklist.date_limite else None,
            "completee": checklist.completee,
            "maj_auto_le": checklist.maj_auto_le.isoformat() if checklist.maj_auto_le else None,
            "items_total": total_items,
            "items_faits": total_faits,
            "taux_completion": round((total_faits / total_items) * 100, 2) if total_items else 0,
            "items_par_categorie": par_categorie,
            "cree_le": checklist.cree_le.isoformat() if checklist.cree_le else None,
        }


@service_factory("checklists_anniversaire", tags={"famille", "anniversaire"})
def obtenir_service_checklists_anniversaire() -> ServiceChecklistsAnniversaire:
    return ServiceChecklistsAnniversaire()
