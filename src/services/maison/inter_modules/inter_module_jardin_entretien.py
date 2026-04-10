"""
Service inter-modules : Jardin saison -> Entretien automatique.

Bridge inter-modules :
- P5-16: generer des taches d'entretien saisonnier selon les plantes
"""

from __future__ import annotations

import json
import logging
from datetime import date as date_type
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


def _mois_depuis_json(mois_raw: str | None) -> set[int]:
    if not mois_raw:
        return set()
    try:
        data = json.loads(mois_raw)
        if isinstance(data, list):
            return {int(m) for m in data if str(m).isdigit()}
    except Exception:
        return set()
    return set()


class JardinEntretienInteractionService:
    """Bridge jardin -> taches entretien saisonnier."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def generer_taches_saisonnieres_depuis_plantes(self, *, db=None) -> dict[str, Any]:
        from src.core.models import TacheEntretien
        from src.core.models.temps_entretien import PlanteJardin

        mois = date_type.today().month
        plantes = db.query(PlanteJardin).all()

        taches_creees = 0
        for plante in plantes:
            mois_semis = _mois_depuis_json(plante.mois_semis)
            mois_recolte = _mois_depuis_json(plante.mois_recolte)
            actions = []

            if mois in mois_semis:
                actions.append(f"Verifier semis pour {plante.nom}")
            if mois in mois_recolte:
                actions.append(f"Planifier recolte pour {plante.nom}")
            if plante.arrosage and plante.arrosage.lower() in {"quotidien", "hebdo"}:
                actions.append(f"Controle arrosage {plante.nom}")

            for action in actions:
                existe = (
                    db.query(TacheEntretien)
                    .filter(TacheEntretien.nom == action, TacheEntretien.fait.is_(False))
                    .first()
                )
                if existe:
                    continue

                tache = TacheEntretien(
                    nom=action,
                    categorie="jardin",
                    description=f"Tache auto saisonniere generee pour {plante.nom}",
                    priorite="normale",
                    fait=False,
                    integrer_planning=True,
                    frequence_jours=7,
                )
                db.add(tache)
                taches_creees += 1

        if taches_creees:
            db.commit()

        return {
            "plantes_analysees": len(plantes),
            "taches_creees": taches_creees,
            "message": f"{taches_creees} tache(s) saisonniere(s) creee(s).",
        }


@service_factory("jardin_entretien_interaction", tags={"maison", "jardin", "entretien"})
def obtenir_service_jardin_entretien_interaction() -> JardinEntretienInteractionService:
    """Factory pour le bridge jardin -> entretien."""
    return JardinEntretienInteractionService()
