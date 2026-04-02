"""
Routes API Famille — Jules (profils enfants, jalons, coaching).

Sous-routeur inclus dans famille.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse, ReponsePaginee
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.schemas.famille import SuggestionsActivitesSimpleRequest
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Famille"])

# ═══════════════════════════════════════════════════════════
# PROFILS ENFANTS
# ═══════════════════════════════════════════════════════════


@router.get("/enfants", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_enfants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    actif: bool = Query(True, description="Filtrer par statut actif"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Liste les profils enfants.

    Returns:
        Réponse paginée avec les profils enfants
    """
    from src.core.models import ProfilEnfant

    def _query():
        with executer_avec_session() as session:
            query = session.query(ProfilEnfant)

            if actif is not None:
                query = query.filter(ProfilEnfant.actif == actif)

            total = query.count()
            items = (
                query.order_by(ProfilEnfant.name)
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [
                    {
                        "id": e.id,
                        "name": e.name,
                        "date_of_birth": e.date_of_birth.isoformat() if e.date_of_birth else None,
                        "gender": e.gender,
                        "notes": e.notes,
                        "actif": e.actif,
                        "taille_vetements": e.taille_vetements or {},
                        "pointure": e.pointure,
                    }
                    for e in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/enfants/{enfant_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_enfant(enfant_id: int, user: dict[str, Any] = Depends(require_auth)):
    """Récupère un profil enfant par son ID."""
    from src.core.models import ProfilEnfant

    def _query():
        with executer_avec_session() as session:
            enfant = session.query(ProfilEnfant).filter(ProfilEnfant.id == enfant_id).first()
            if not enfant:
                raise HTTPException(status_code=404, detail="Enfant non trouvé")

            return {
                "id": enfant.id,
                "name": enfant.name,
                "date_of_birth": enfant.date_of_birth.isoformat() if enfant.date_of_birth else None,
                "gender": enfant.gender,
                "notes": enfant.notes,
                "actif": enfant.actif,
                "cree_le": enfant.cree_le.isoformat() if enfant.cree_le else None,
                "taille_vetements": enfant.taille_vetements or {},
                "pointure": enfant.pointure,
            }

    return await executer_async(_query)


@router.get("/enfants/{enfant_id}/jalons", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def lister_jalons_enfant(
    enfant_id: int,
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les jalons de développement d'un enfant."""
    from src.core.models import Jalon

    def _query():
        with executer_avec_session() as session:
            query = session.query(Jalon).filter(Jalon.child_id == enfant_id)

            if categorie:
                query = query.filter(Jalon.categorie == categorie)

            jalons = query.order_by(Jalon.date_atteint.desc()).all()

            return {
                "items": [
                    {
                        "id": j.id,
                        "titre": j.titre,
                        "description": j.description,
                        "categorie": j.categorie,
                        "date_atteint": j.date_atteint.isoformat(),
                        "photo_url": j.photo_url,
                    }
                    for j in jalons
                ],
                "enfant_id": enfant_id,
            }

    return await executer_async(_query)


@router.post("/enfants/{enfant_id}/jalons", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_jalon(
    enfant_id: int,
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Ajoute un jalon de développement pour un enfant."""
    from src.core.models import Jalon, ProfilEnfant

    def _query():
        with executer_avec_session() as session:
            enfant = session.query(ProfilEnfant).filter(ProfilEnfant.id == enfant_id).first()
            if not enfant:
                raise HTTPException(status_code=404, detail="Enfant non trouvé")

            jalon = Jalon(
                child_id=enfant_id,
                titre=payload["titre"],
                description=payload.get("description"),
                categorie=payload.get("categorie", "autre"),
                date_atteint=payload.get("date_atteint", date.today().isoformat()),
                photo_url=payload.get("photo_url"),
                notes=payload.get("notes"),
                lieu=payload.get("lieu"),
                emotion_parents=payload.get("emotion_parents"),
            )
            session.add(jalon)
            session.commit()
            session.refresh(jalon)

            try:
                from src.services.core.events import obtenir_bus

                obtenir_bus().emettre(
                    "jalon.ajoute",
                    {
                        "jalon_id": jalon.id,
                        "titre": jalon.titre,
                        "nom": jalon.titre,
                        "enfant_id": enfant_id,
                        "categorie": jalon.categorie,
                    },
                    source="famille_jules",
                )
            except Exception:
                pass

            return {
                "id": jalon.id,
                "titre": jalon.titre,
                "categorie": jalon.categorie,
                "date_atteint": jalon.date_atteint.isoformat(),
                "enfant_id": enfant_id,
            }

    return await executer_async(_query)


@router.delete("/enfants/{enfant_id}/jalons/{jalon_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_jalon(
    enfant_id: int,
    jalon_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Supprime un jalon de développement."""
    from src.core.models import Jalon

    def _query():
        with executer_avec_session() as session:
            jalon = (
                session.query(Jalon)
                .filter(Jalon.id == jalon_id, Jalon.child_id == enfant_id)
                .first()
            )
            if not jalon:
                raise HTTPException(status_code=404, detail="Jalon non trouvé")
            session.delete(jalon)
            session.commit()
            return MessageResponse(message=f"Jalon '{jalon.titre}' supprimé")

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# ACTIVITÉS FAMILIALES
# ═══════════════════════════════════════════════════════════
# CROISSANCE OMS 
# ═══════════════════════════════════════════════════════════


@router.get("/jules/croissance", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_croissance_jules(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les normes OMS de croissance pour l'âge de Jules."""
    from src.services.famille.contexte import obtenir_service_contexte_familial
    from src.services.famille.jules import obtenir_service_jules

    def _query():
        jules_service = obtenir_service_jules()
        if not jules_service.get_date_naissance_jules():
            raise HTTPException(status_code=404, detail="Profil Jules non trouvé")
        age_mois = jules_service.get_age_mois()

        contexte_service = obtenir_service_contexte_familial()
        normes = contexte_service.obtenir_croissance_oms(age_mois, sexe="M")

        return {
            "age_mois": age_mois,
            "normes": normes,
        }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS ACTIVITÉS SIMPLIFIÉES 
# ═══════════════════════════════════════════════════════════


@router.post("/activites/suggestions-ia-auto", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_activites_auto(
    payload: SuggestionsActivitesSimpleRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Suggestions d'activités avec météo et âge auto-injectés (sans saisie manuelle)."""
    from src.services.famille.activites import obtenir_service_activites
    from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux
    from src.services.famille.jules import obtenir_service_jules
    from src.services.integrations.weather.service import obtenir_service_meteo

    def _structurer_suggestions_texte(texte: str) -> list[dict[str, Any]]:
        """Convertit le texte IA en suggestions structurées pour pré-remplissage UI."""
        suggestions: list[dict[str, Any]] = []
        if not texte:
            return suggestions

        blocs = [b.strip() for b in texte.split("🎯") if b.strip()]
        for bloc in blocs:
            lignes = [l.strip() for l in bloc.splitlines() if l.strip()]
            titre = lignes[0] if lignes else "Activité familiale"
            description = ""
            duree_minutes = 90
            type_activite = "autre"
            lieu = "interieur"

            for ligne in lignes[1:]:
                low = ligne.lower()
                if "description" in low:
                    description = ligne.split(":", 1)[-1].strip()
                elif "dur" in low and any(c.isdigit() for c in ligne):
                    chiffres = "".join(c if c.isdigit() else " " for c in ligne).split()
                    if chiffres:
                        duree_minutes = int(chiffres[0]) * 60 if "heure" in low else int(chiffres[0])
                elif "météo" in low or "meteo" in low:
                    lieu = "exterieur" if "extérieur" in low or "exterieur" in low else "interieur"

            titre_low = titre.lower()
            if "parc" in titre_low or "balade" in titre_low:
                type_activite = "sortie"
            elif "sport" in titre_low:
                type_activite = "sport"
            elif "atelier" in titre_low or "dessin" in titre_low:
                type_activite = "culture"
            elif "jeu" in titre_low:
                type_activite = "jeu"

            suggestions.append(
                {
                    "titre": titre,
                    "description": description or "Suggestion IA adaptée au contexte du jour.",
                    "type": type_activite,
                    "duree_minutes": duree_minutes,
                    "lieu": lieu,
                }
            )

        return suggestions

    async def _query():
        # Auto-inject météo
        meteo_service = obtenir_service_meteo()
        previsions = meteo_service.get_previsions(nb_jours=3)
        meteo_txt = "variable"
        if previsions:
            meteo_txt = previsions[0].condition or "variable"

        # Force intérieur si pluie
        type_effectif = payload.type_prefere
        if previsions and previsions[0].precipitation_mm > 5 and type_effectif == "les_deux":
            type_effectif = "interieur"

        # Auto-inject âge Jules
        jules_service = obtenir_service_jules()
        age_mois = jules_service.get_age_mois(default=19)

        # Détecter journée libre (férié + crèche fermée dans les 3 prochains jours)
        jours_service = obtenir_service_jours_speciaux()
        prochains = jours_service.prochains_jours_speciaux(nb=5)
        from datetime import timedelta

        journee_libre = any(
            j.date_jour <= date.today() + timedelta(days=3)
            and j.type in ("ferie", "creche")
            for j in prochains
        )

        # Collecter les actions jardin (plantes à arroser, récoltes proches)
        jardin_activites: list[dict] = []
        try:
            from src.services.maison import obtenir_jardin_service

            jardin_svc = obtenir_jardin_service()
            beau_temps = bool(previsions and previsions[0].precipitation_mm < 5)
            if beau_temps:
                for p in jardin_svc.obtenir_plantes_a_arroser():
                    jardin_activites.append({"type": "arrosage", "nom": getattr(p, "nom", str(p))})
                for p in jardin_svc.obtenir_recoltes_proches():
                    jardin_activites.append({"type": "recolte", "nom": getattr(p, "nom", str(p))})
        except Exception as e:
            logger.warning("[famille] Activités jardin non chargées pour suggestions weekend: %s", e)
        prompt_extra = ""
        if journee_libre:
            prompt_extra = " C'est une journée libre (férié ou crèche fermée), propose des activités pour une journée complète."
        if jardin_activites and type_effectif != "interieur":
            noms_jardin = ", ".join(a["nom"] for a in jardin_activites[:3])
            prompt_extra += f" Le jardin a des tâches à faire ({noms_jardin}) : inclure 1 activité jardin avec Jules."

        # Appel au service IA activités existant
        service = obtenir_service_activites()
        if hasattr(service, "suggerer_activites_ia"):
            resultat = service.suggerer_activites_ia(
                age_mois=age_mois,
                meteo=meteo_txt,
                budget_max=payload.budget_max,
            )
            return {
                "suggestions": resultat,
                "suggestions_struct": _structurer_suggestions_texte(str(resultat)),
                "meteo": meteo_txt,
                "journee_libre": journee_libre,
                "jardin_activites": jardin_activites,
            }

        # Fallback: utiliser le service weekend IA
        from src.services.famille.weekend_ai import obtenir_weekend_ai_service

        meteo_enrichi = meteo_txt + (" " + type_effectif if type_effectif != "les_deux" else "") + prompt_extra
        weekend_service = obtenir_weekend_ai_service()
        resultat = await weekend_service.suggerer_activites(
            meteo=meteo_enrichi,
            age_enfant_mois=age_mois,
            budget=int(payload.budget_max),
            nb_suggestions=5,
        )
        return {
            "suggestions": resultat,
            "suggestions_struct": _structurer_suggestions_texte(str(resultat)),
            "meteo": meteo_txt,
            "journee_libre": journee_libre,
            "jardin_activites": jardin_activites,
        }

    return await _query()


@router.get("/jules/activites-suggestions", responses=REPONSES_LISTE)
@gerer_exception_api
async def suggestions_activites_jules_contextuelles(
    contexte: str = Query("meteo_variable", description="Ex: meteo_pluie, meteo_soleil, interieur"),
    budget_max: float = Query(40.0, ge=0, le=300),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """IA5 - Suggestions d'activites Jules selon meteo + creche + age."""
    from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux
    from src.services.famille.jules import obtenir_service_jules
    from src.services.famille.jules_ai import obtenir_jules_ai_service
    from src.services.integrations.weather import obtenir_service_meteo

    def _query() -> dict[str, Any]:
        # Age Jules
        jules_service = obtenir_service_jules()
        age_mois = jules_service.get_age_mois(default=19)

        # Meteo prioritaire: parametre contexte, sinon prevision J0
        meteo_effective = "mixte"
        contexte_l = (contexte or "").lower()
        if "pluie" in contexte_l:
            meteo_effective = "pluie"
        elif "soleil" in contexte_l:
            meteo_effective = "soleil"
        elif "interieur" in contexte_l:
            meteo_effective = "interieur"
        elif "exterieur" in contexte_l:
            meteo_effective = "exterieur"
        else:
            try:
                previsions = obtenir_service_meteo().get_previsions(nb_jours=1)
                if previsions:
                    meteo_effective = getattr(previsions[0], "condition", "mixte") or "mixte"
            except Exception:
                meteo_effective = "mixte"

        # Contexte creche ouverte/fermee
        jours_service = obtenir_service_jours_speciaux()
        creche_fermee = jours_service.est_fermeture_creche(date.today())

        preferences = ["educatif", "motricite", "autonomie"]
        if creche_fermee:
            preferences.append("journee_complete")
        if "pluie" in meteo_effective.lower() or "interieur" in contexte_l:
            preferences.append("interieur")
        if "soleil" in meteo_effective.lower() or "exterieur" in contexte_l:
            preferences.append("exterieur")

        service = obtenir_jules_ai_service()
        suggestions = service.suggerer_activites_enrichies(
            age_mois=age_mois,
            meteo=meteo_effective,
            budget_max=budget_max,
            preferences=preferences,
            nb_suggestions=5,
        )

        return {
            "items": [s.model_dump() for s in suggestions],
            "total": len(suggestions),
            "contexte": {
                "age_mois": age_mois,
                "meteo": meteo_effective,
                "creche_fermee": creche_fermee,
                "contexte_requete": contexte,
            },
        }

    return await executer_async(_query)

# ═══════════════════════════════════════════════════════════
# JULES — ALIMENTS EXCLUS (CT-09)
# ═══════════════════════════════════════════════════════════


@router.get("/jules/aliments-exclus", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def lire_aliments_exclus_jules(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne la liste des aliments exclus pour Jules."""
    from src.core.models.user_preferences import PreferenceUtilisateur
    from sqlalchemy import select as sa_select

    def _query():
        with executer_avec_session() as session:
            user_id = user.get("sub", user.get("id", "dev"))
            pref = session.execute(
                sa_select(PreferenceUtilisateur).where(
                    PreferenceUtilisateur.user_id == user_id
                )
            ).scalar_one_or_none()
            return {
                "aliments_exclus_jules": pref.aliments_exclus_jules if pref else [],
                "age_mois": pref.jules_age_mois if pref else 19,
            }

    return await executer_async(_query)


@router.put("/jules/aliments-exclus", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def mettre_a_jour_aliments_exclus_jules(
    payload: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Met à jour la liste des aliments exclus pour Jules.

    Body: {"aliments_exclus_jules": ["sel", "miel", ...]}
    """
    from src.core.models.user_preferences import PreferenceUtilisateur
    from sqlalchemy import select as sa_select

    aliments = payload.get("aliments_exclus_jules", [])
    if not isinstance(aliments, list):
        raise HTTPException(status_code=422, detail="aliments_exclus_jules doit être une liste")

    def _update():
        with executer_avec_session() as session:
            user_id = user.get("sub", user.get("id", "dev"))
            pref = session.execute(
                sa_select(PreferenceUtilisateur).where(
                    PreferenceUtilisateur.user_id == user_id
                )
            ).scalar_one_or_none()
            if pref is None:
                pref = PreferenceUtilisateur(user_id=user_id)
                session.add(pref)
            pref.aliments_exclus_jules = aliments
            session.commit()
        return MessageResponse(message=f"{len(aliments)} aliment(s) exclus mis à jour pour Jules")

    return await executer_async(_update)


# ═══════════════════════════════════════════════════════════
# JULES — COACHING HEBDOMADAIRE (CT-05)
# ═══════════════════════════════════════════════════════════


@router.get("/jules/coaching-hebdo", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_coaching_hebdo_jules(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Génère le coaching hebdomadaire personnalisé pour Jules (CT-05).

    Retourne un bilan développemental, 3 activités et un conseil alimentation
    adaptés à l'âge actuel de Jules.
    """
    from src.core.models.user_preferences import PreferenceUtilisateur
    from src.services.famille.jules_ai import obtenir_jules_ai_service
    from sqlalchemy import select as sa_select

    def _query():
        with executer_avec_session() as session:
            user_id = user.get("sub", user.get("id", "dev"))
            pref = session.execute(
                sa_select(PreferenceUtilisateur).where(
                    PreferenceUtilisateur.user_id == user_id
                )
            ).scalar_one_or_none()
            age_mois = pref.jules_age_mois if pref else 19

        service = obtenir_jules_ai_service()
        coaching = service.generer_coaching_hebdo(age_mois=age_mois)
        return {
            "age_mois": age_mois,
            "coaching": coaching,
        }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# TIMELINE VIE FAMILIALE (MT-08)
# ═══════════════════════════════════════════════════════════


@router.get("/timeline", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_timeline_famille(
    categorie: str | None = Query(None, description="Filtre: jules | maison | famille | jeux"),
    limite: int = Query(200, ge=1, le=500),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Agrège les événements familiaux multi-modules en timeline chronologique."""

    def _query() -> dict[str, Any]:
        from src.core.models.famille import EvenementFamilial, Jalon
        from src.core.models.jeux import PariSportif
        from src.core.models.maison import Projet

        with executer_avec_session() as session:
            elements: list[dict[str, Any]] = []

            # 1) Jalons Jules
            jalons = session.query(Jalon).order_by(Jalon.date_atteint.desc()).limit(limite).all()
            for j in jalons:
                elements.append(
                    {
                        "id": f"jalon-{j.id}",
                        "categorie": "jules",
                        "date": j.date_atteint.isoformat(),
                        "titre": j.titre,
                        "description": j.description,
                        "meta": {
                            "type": j.categorie,
                            "lieu": j.lieu,
                            "age_mois": j.age_mois_atteint,
                        },
                    }
                )

            # 2) Événements familiaux
            evenements = (
                session.query(EvenementFamilial)
                .filter(EvenementFamilial.actif.is_(True))
                .order_by(EvenementFamilial.date_evenement.desc())
                .limit(limite)
                .all()
            )
            for e in evenements:
                elements.append(
                    {
                        "id": f"famille-{e.id}",
                        "categorie": "famille",
                        "date": e.date_evenement.isoformat(),
                        "titre": e.titre,
                        "description": e.notes,
                        "meta": {
                            "type": e.type_evenement,
                            "participants": e.participants or [],
                        },
                    }
                )

            # 3) Projets maison terminés
            projets = (
                session.query(Projet)
                .filter(Projet.statut.in_(["terminé", "termine", "complete", "complet"]))
                .order_by(Projet.date_fin_reelle.desc(), Projet.date_fin_prevue.desc())
                .limit(limite)
                .all()
            )
            for p in projets:
                dt = p.date_fin_reelle or p.date_fin_prevue or p.date_debut
                if not dt:
                    continue
                elements.append(
                    {
                        "id": f"maison-{p.id}",
                        "categorie": "maison",
                        "date": dt.isoformat(),
                        "titre": p.nom,
                        "description": p.description,
                        "meta": {
                            "priorite": p.priorite,
                            "statut": p.statut,
                        },
                    }
                )

            # 4) Matchs mémorables (ROI >= 30% ou gain >= 50)
            paris = session.query(PariSportif).order_by(PariSportif.cree_le.desc()).limit(limite).all()
            for p in paris:
                mise = float(p.mise or 0)
                gain = float(p.gain or 0)
                if mise <= 0:
                    continue
                roi = ((gain - mise) / mise) * 100
                if roi < 30 and gain < 50:
                    continue
                elements.append(
                    {
                        "id": f"jeux-{p.id}",
                        "categorie": "jeux",
                        "date": p.cree_le.date().isoformat() if p.cree_le else date.today().isoformat(),
                        "titre": f"Pari {p.type_pari} ({p.prediction})",
                        "description": p.notes,
                        "meta": {
                            "cote": p.cote,
                            "mise": mise,
                            "gain": gain,
                            "roi": round(roi, 1),
                        },
                    }
                )

            if categorie:
                cat = categorie.lower().strip()
                elements = [e for e in elements if e["categorie"] == cat]

            elements.sort(key=lambda x: x["date"], reverse=True)
            elements = elements[:limite]

            return {
                "items": elements,
                "total": len(elements),
                "filtres": {
                    "categorie": categorie,
                    "limite": limite,
                },
            }

    return await executer_async(_query)


@router.get("/aujourd-hui-histoire", responses=REPONSES_LISTE)
@gerer_exception_api
async def obtenir_aujourd_hui_histoire(
    limite: int = Query(8, ge=1, le=30),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les souvenirs familiaux correspondant au jour/mois actuel."""

    def _query() -> dict[str, Any]:
        from sqlalchemy import extract

        from src.core.models.famille import EvenementFamilial, Jalon

        aujourd_hui = date.today()
        mois = aujourd_hui.month
        jour = aujourd_hui.day

        with executer_avec_session() as session:
            elements: list[dict[str, Any]] = []

            jalons = (
                session.query(Jalon)
                .filter(
                    extract("month", Jalon.date_atteint) == mois,
                    extract("day", Jalon.date_atteint) == jour,
                )
                .order_by(Jalon.date_atteint.desc())
                .limit(limite)
                .all()
            )
            for j in jalons:
                elements.append(
                    {
                        "id": f"jalon-{j.id}",
                        "type": "jalon",
                        "date_source": j.date_atteint.isoformat(),
                        "titre": j.titre,
                        "description": j.description,
                        "annees_depuis": max(0, aujourd_hui.year - j.date_atteint.year),
                    }
                )

            evenements = (
                session.query(EvenementFamilial)
                .filter(
                    EvenementFamilial.actif.is_(True),
                    extract("month", EvenementFamilial.date_evenement) == mois,
                    extract("day", EvenementFamilial.date_evenement) == jour,
                )
                .order_by(EvenementFamilial.date_evenement.desc())
                .limit(limite)
                .all()
            )
            for e in evenements:
                elements.append(
                    {
                        "id": f"event-{e.id}",
                        "type": "evenement",
                        "date_source": e.date_evenement.isoformat(),
                        "titre": e.titre,
                        "description": e.notes,
                        "annees_depuis": max(0, aujourd_hui.year - e.date_evenement.year),
                    }
                )

            elements.sort(
                key=lambda item: (item["annees_depuis"], item["date_source"]),
                reverse=True,
            )
            elements = elements[:limite]

            return {
                "date": aujourd_hui.isoformat(),
                "items": elements,
                "total": len(elements),
            }

    return await executer_async(_query)

