"""
Service Contexte Maison — Agrégateur central du briefing quotidien.

Collecte données de 6 sources (alertes, tâches, météo, projets, jardin,
cellier/énergie) et retourne un BriefingMaison contextuel.
Seuls les éléments pertinents apparaissent.
"""

import logging
from datetime import date, timedelta

from src.core.ai import ClientIA, obtenir_client_ia
from src.core.decorators import avec_cache, avec_gestion_erreurs
from src.core.monitoring import chronometre
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

from .schemas import (
    AlerteMaison,
    BriefingMaison,
    MeteoResume,
    TacheJour,
)
from .schemas_enums import NiveauUrgence, TypeAlerteMaison

logger = logging.getLogger(__name__)

# Ordre de tri des niveaux d'urgence (plus petit = plus urgent)
_URGENCE_ORDRE = {
    NiveauUrgence.CRITIQUE: 0,
    NiveauUrgence.HAUTE: 1,
    NiveauUrgence.MOYENNE: 2,
    NiveauUrgence.BASSE: 3,
    NiveauUrgence.INFO: 4,
}

MAX_ALERTES_BRIEFING = 8


class ContexteMaisonService(BaseAIService):
    """Agrégateur central du briefing quotidien maison.

    Collecte et priorise les données de multiples services pour
    retourner un briefing avec uniquement ce qui est pertinent.
    """

    def __init__(self, client: ClientIA | None = None):
        if client is None:
            client = obtenir_client_ia()
        super().__init__(
            client=client,
            cache_prefix="contexte_maison",
            default_ttl=300,
            service_name="contexte_maison",
        )

    # ═══════════════════════════════════════════════════════════
    # API PUBLIQUE
    # ═══════════════════════════════════════════════════════════

    @chronometre("maison.briefing", seuil_alerte_ms=3000)
    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=None)
    def obtenir_briefing(self, date_cible: date | None = None) -> BriefingMaison:
        """Retourne le briefing quotidien maison.

        Agrège 6 sources de données en un seul objet contextuel.
        """
        date_cible = date_cible or date.today()

        alertes = self._collecter_alertes()
        taches = self._collecter_taches_jour()
        meteo = self._evaluer_meteo()
        projets = self._collecter_projets()
        jardin = self._collecter_jardin()
        cellier_energie = self._collecter_cellier_energie()
        contexte_famille = self._collecter_contexte_famille()

        # Trier alertes par urgence, garder top N
        alertes_triees = sorted(alertes, key=lambda a: _URGENCE_ORDRE.get(a.niveau, 9))
        alertes_top = alertes_triees[:MAX_ALERTES_BRIEFING]

        # Construire les priorités (noms des alertes critiques/hautes)
        priorites = [
            a.titre
            for a in alertes_triees
            if a.niveau in (NiveauUrgence.CRITIQUE, NiveauUrgence.HAUTE)
        ]

        # Construire le briefing
        meteo_impact_str = None
        meteo_resume = None
        if meteo:
            meteo_impact_str = meteo.get("description", "")
            meteo_resume = MeteoResume(
                temperature_min=meteo.get("temperature_min"),
                temperature_max=meteo.get("temperature_max"),
                description=meteo.get("description", ""),
                precipitation_mm=meteo.get("precipitation_mm", 0),
                impact_jardin=meteo.get("impact_jardin"),
                impact_menage=meteo.get("impact_menage"),
                alertes_meteo=meteo.get("alertes_meteo", []),
            )

        return BriefingMaison(
            date=date_cible,
            taches_jour=[t.nom for t in taches],
            taches_jour_detail=taches,
            alertes=alertes_top,
            meteo_impact=meteo_impact_str,
            meteo=meteo_resume,
            projets_actifs=[p.get("nom", "") for p in projets],
            priorites=priorites,
            entretiens_saisonniers=cellier_energie.get("saisonniers", []),
            jardin=jardin,
            cellier_alertes=cellier_energie.get("cellier", []),
            energie_anomalies=cellier_energie.get("energie", []),
            contexte_famille=contexte_famille,
        )

    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    def obtenir_toutes_alertes(self) -> list[AlerteMaison]:
        """Retourne TOUTES les alertes (pas juste le top 8)."""
        alertes = self._collecter_alertes()
        return sorted(alertes, key=lambda a: _URGENCE_ORDRE.get(a.niveau, 9))

    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    def obtenir_taches_jour(self) -> list[TacheJour]:
        """Retourne toutes les tâches du jour avec détails."""
        return self._collecter_taches_jour()

    @avec_cache(ttl=86400)
    @avec_gestion_erreurs(default_return="")
    def generer_resume_ia(self, briefing: BriefingMaison) -> str:
        """Génère un résumé IA d'une ligne du briefing (cache 24h)."""
        nb_taches = len(briefing.taches_jour)
        nb_alertes = len(briefing.alertes)
        meteo = briefing.meteo_impact or "météo inconnue"

        prompt = (
            f"Résume en 1 phrase courte et encourageante la journée maison: "
            f"{nb_taches} tâches, {nb_alertes} alertes, météo: {meteo}. "
            f"Tâches: {', '.join(briefing.taches_jour[:5])}."
        )

        result = self.call_with_cache_sync(
            prompt=prompt,
            system_prompt="Tu es un assistant maison bienveillant. Réponds en 1 phrase max, avec un emoji.",
            max_tokens=100,
            temperature=0.8,
        )
        return result or ""

    # ═══════════════════════════════════════════════════════════
    # COLLECTEURS PRIVÉS
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    def _collecter_alertes(self) -> list[AlerteMaison]:
        """Collecte les alertes de toutes les sources."""
        alertes: list[AlerteMaison] = []

        # 1. Cellier — péremptions + stock bas
        try:
            from src.services.maison import get_cellier_crud_service

            service = get_cellier_crud_service()
            for a in service.get_alertes_peremption(jours_horizon=14):
                jours = a.get("jours_restants", 14)
                niveau = NiveauUrgence.HAUTE if jours <= 0 else NiveauUrgence.MOYENNE
                alertes.append(
                    AlerteMaison(
                        type=TypeAlerteMaison.STOCK,
                        niveau=niveau,
                        titre=f"{'Périmé' if jours <= 0 else 'Bientôt périmé'}: {a.get('nom', '?')}",
                        message=f"{'Périmé' if jours <= 0 else f'Expire dans {jours} jours'}",
                        metadata=a,
                    )
                )
            for a in service.get_alertes_stock():
                alertes.append(
                    AlerteMaison(
                        type=TypeAlerteMaison.STOCK,
                        niveau=NiveauUrgence.BASSE,
                        titre=f"Stock bas: {a.get('nom', '?')}",
                        message=f"Quantité: {a.get('quantite', 0)} (seuil: {a.get('seuil', 0)})",
                        metadata=a,
                    )
                )
        except Exception as e:
            logger.warning(f"Collecte alertes cellier échouée: {e}")

        # 4. Entretiens saisonniers du mois non faits
        try:
            from src.services.maison import get_entretien_saisonnier_crud_service

            service = get_entretien_saisonnier_crud_service()
            for e in service.get_alertes_saisonnieres():
                niveau = NiveauUrgence.HAUTE if e.get("obligatoire") else NiveauUrgence.MOYENNE
                alertes.append(
                    AlerteMaison(
                        type=TypeAlerteMaison.ENTRETIEN,
                        niveau=niveau,
                        titre=f"{'⚖️ Obligatoire: ' if e.get('obligatoire') else ''}{e.get('nom', '?')}",
                        message=f"Entretien saisonnier — {e.get('categorie', '')}",
                        action_suggeree="Contacter un professionnel"
                        if e.get("professionnel_requis")
                        else None,
                        metadata=e,
                    )
                )
        except Exception as e:
            logger.warning(f"Collecte alertes saisonnières échouée: {e}")

        # 5. Durée de vie des appareils (via catalogue entretien)
        for alerte in self._evaluer_duree_vie_appareils():
            alertes.append(alerte)

        return alertes

    @avec_gestion_erreurs(default_return=[])
    def _collecter_taches_jour(self) -> list[TacheJour]:
        """Collecte les tâches du jour depuis les différentes sources."""
        taches: list[TacheJour] = []

        # 1. Tâches de routines actives
        try:
            from src.services.maison import get_entretien_service

            service = get_entretien_service()
            for t in service.obtenir_taches_du_jour():
                taches.append(
                    TacheJour(
                        nom=t.nom,
                        categorie="menage",
                        duree_estimee_min=None,
                        source="routine",
                        id_source=t.id,
                    )
                )
        except Exception as e:
            logger.warning(f"Collecte tâches routines échouée: {e}")

        # 2. Tâches d'entretien prévues (TacheEntretien.prochaine_fois == today)
        try:
            from src.core.decorators import avec_session_db
            from src.core.models import TacheEntretien

            @avec_session_db
            def _get_taches_entretien_jour(db=None):
                today = date.today()
                return (
                    db.query(TacheEntretien)
                    .filter(
                        TacheEntretien.prochaine_fois == today,
                        TacheEntretien.fait.is_(False),
                    )
                    .all()
                )

            for t in _get_taches_entretien_jour():
                taches.append(
                    TacheJour(
                        nom=t.nom,
                        categorie=t.categorie or "entretien",
                        duree_estimee_min=t.duree_minutes,
                        priorite=NiveauUrgence.MOYENNE,
                        source="catalogue",
                        id_source=t.id,
                    )
                )
        except Exception as e:
            logger.warning(f"Collecte tâches entretien échouée: {e}")

        # 3. Entretiens saisonniers du mois courant non faits
        try:
            from src.services.maison import get_entretien_saisonnier_crud_service

            service = get_entretien_saisonnier_crud_service()
            for e in service.get_alertes_saisonnieres():
                taches.append(
                    TacheJour(
                        nom=e.get("nom", "?"),
                        categorie=e.get("categorie", "saisonnier"),
                        duree_estimee_min=e.get("duree_minutes"),
                        priorite=NiveauUrgence.HAUTE if e.get("obligatoire") else NiveauUrgence.MOYENNE,
                        source="saisonnier",
                        id_source=e.get("id"),
                    )
                )
        except Exception as e:
            logger.warning(f"Collecte tâches saisonnières échouée: {e}")

        return taches

    @avec_gestion_erreurs(default_return=None)
    def _evaluer_meteo(self) -> dict | None:
        """Récupère la météo du jour et évalue l'impact."""
        try:
            from src.services.integrations.weather import get_meteo_service

            service = get_meteo_service()
            previsions = service.get_previsions(nb_jours=2)
            if not previsions:
                return None

            aujourdhui = previsions[0]
            # Évaluer impact ménage
            pluie = aujourdhui.precipitation_mm > 5
            soleil = aujourdhui.temperature_max > 20 and aujourdhui.precipitation_mm < 2
            impact_menage = None
            if soleil:
                impact_menage = "Idéal pour vitres et linge dehors"
            elif pluie:
                impact_menage = "Reporter tâches extérieures"

            # Alertes jardin
            alertes_meteo = []
            try:
                from src.services.maison import get_jardin_service

                jardin = get_jardin_service()
                import asyncio

                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    # Déjà dans une boucle async — skip les alertes IA
                    pass
                else:
                    alertes_meteo = asyncio.run(
                        jardin.analyser_meteo_impact(
                            temperature_min=aujourdhui.temperature_min,
                            temperature_max=aujourdhui.temperature_max,
                            pluie_mm=aujourdhui.precipitation_mm,
                        )
                    )
            except Exception as e:
                logger.warning(f"Analyse météo jardin échouée: {e}")

            return {
                "temperature_min": aujourdhui.temperature_min,
                "temperature_max": aujourdhui.temperature_max,
                "description": getattr(aujourdhui, "description", ""),
                "precipitation_mm": aujourdhui.precipitation_mm,
                "impact_jardin": "Attention gel" if aujourdhui.temperature_min <= 0 else None,
                "impact_menage": impact_menage,
                "alertes_meteo": alertes_meteo,
            }
        except Exception as e:
            logger.warning(f"Évaluation météo échouée: {e}")
            return None

    @avec_gestion_erreurs(default_return=[])
    def _collecter_projets(self) -> list[dict]:
        """Collecte les projets actifs/urgents."""
        projets = []
        try:
            from src.services.maison import get_projets_service

            service = get_projets_service()
            for p in service.obtenir_projets_urgents():
                projets.append(
                    {
                        "id": p.id,
                        "nom": p.nom,
                        "statut": p.statut,
                        "priorite": p.priorite,
                    }
                )
        except Exception as e:
            logger.warning(f"Collecte projets échouée: {e}")
        return projets

    @avec_gestion_erreurs(default_return=[])
    def _collecter_jardin(self) -> list[dict]:
        """Collecte les actions jardin pertinentes."""
        actions = []
        try:
            from src.services.maison import get_jardin_service

            service = get_jardin_service()

            # Plantes à arroser
            for p in service.obtenir_plantes_a_arroser():
                actions.append(
                    {
                        "type": "arrosage",
                        "nom": getattr(p, "nom", str(p)),
                        "action": f"Arroser {getattr(p, 'nom', '')}",
                    }
                )

            # Récoltes proches
            for p in service.obtenir_recoltes_proches():
                actions.append(
                    {
                        "type": "recolte",
                        "nom": getattr(p, "nom", str(p)),
                        "action": f"Récolter {getattr(p, 'nom', '')}",
                        "date_recolte": str(getattr(p, "date_recolte_prevue", "")),
                    }
                )
        except Exception as e:
            logger.warning(f"Collecte jardin échouée: {e}")

        # Semis du mois depuis le catalogue
        try:
            import json
            from pathlib import Path

            catalogue_path = Path("data/reference/plantes_catalogue.json")
            if catalogue_path.exists():
                with open(catalogue_path, encoding="utf-8") as f:
                    catalogue = json.load(f)
                mois_courant = date.today().month
                plantes = catalogue.get("plantes", catalogue) if isinstance(catalogue, dict) else catalogue
                if isinstance(plantes, list):
                    for plante in plantes:
                        mois_semis = plante.get("mois_semis", [])
                        if mois_courant in mois_semis:
                            actions.append(
                                {
                                    "type": "semis",
                                    "nom": plante.get("nom", "?"),
                                    "action": f"C'est le moment de semer: {plante.get('nom', '?')}",
                                }
                            )
        except Exception as e:
            logger.warning(f"Lecture catalogue plantes échouée: {e}")

        return actions

    @avec_gestion_erreurs(default_return={})
    def _collecter_cellier_energie(self) -> dict:
        """Collecte alertes cellier et anomalies énergie."""
        result: dict = {"cellier": [], "energie": [], "saisonniers": []}

        # Cellier — articles bientôt périmés (7j)
        try:
            from src.services.maison import get_cellier_crud_service

            service = get_cellier_crud_service()
            result["cellier"] = service.get_alertes_peremption(jours_horizon=7)
        except Exception as e:
            logger.warning(f"Collecte cellier échouée: {e}")

        # Énergie — relevés anomalies
        try:
            from src.core.decorators import avec_session_db
            from src.core.models.maison_extensions import ReleveCompteur

            @avec_session_db
            def _check_releves(db=None):
                anomalies = []
                dernier = (
                    db.query(ReleveCompteur)
                    .order_by(ReleveCompteur.date_releve.desc())
                    .first()
                )
                if dernier:
                    jours_sans_releve = (date.today() - dernier.date_releve).days
                    if jours_sans_releve > 30:
                        anomalies.append(
                            {
                                "type": "pas_de_releve",
                                "message": f"Pas de relevé compteur depuis {jours_sans_releve} jours",
                                "jours": jours_sans_releve,
                            }
                        )
                return anomalies

            result["energie"] = _check_releves()
        except Exception as e:
            logger.warning(f"Collecte énergie échouée: {e}")

        # Entretiens saisonniers
        try:
            from src.services.maison import get_entretien_saisonnier_crud_service

            service = get_entretien_saisonnier_crud_service()
            result["saisonniers"] = service.get_alertes_saisonnieres()
        except Exception as e:
            logger.warning(f"Collecte saisonniers échouée: {e}")

        return result

    @avec_gestion_erreurs(default_return=[])
    def _evaluer_duree_vie_appareils(self) -> list[AlerteMaison]:
        """Évalue l'âge des appareils par rapport à leur durée de vie catalogue.

        Retourne des alertes quand un appareil dépasse 80% ou 100% de sa
        durée de vie estimée selon le catalogue d'entretien.
        """
        alertes: list[AlerteMaison] = []

        try:
            from src.core.decorators import avec_session_db
            from src.core.models import ObjetMaison

            @avec_session_db
            def _get_appareils(db=None):
                return (
                    db.query(ObjetMaison)
                    .filter(
                        ObjetMaison.date_achat.isnot(None),
                        ObjetMaison.duree_vie_ans.isnot(None),
                    )
                    .all()
                )

            today = date.today()
            for appareil in _get_appareils():
                if not appareil.date_achat or not appareil.duree_vie_ans:
                    continue

                age_ans = (today - appareil.date_achat).days / 365.25
                duree_vie = float(appareil.duree_vie_ans)
                ratio = age_ans / duree_vie if duree_vie > 0 else 0

                if ratio >= 1.0:
                    alertes.append(
                        AlerteMaison(
                            type=TypeAlerteMaison.ENTRETIEN,
                            niveau=NiveauUrgence.HAUTE,
                            titre=f"⚠️ {appareil.nom} — durée de vie dépassée",
                            message=f"Âge: {age_ans:.1f}ans (durée estimée: {duree_vie}ans). Planifiez un remplacement.",
                            action_suggeree="Obtenir un devis ou envisager le remplacement",
                            metadata={"id": appareil.id, "nom": appareil.nom, "age_ans": round(age_ans, 1)},
                        )
                    )
                elif ratio >= 0.8:
                    alertes.append(
                        AlerteMaison(
                            type=TypeAlerteMaison.ENTRETIEN,
                            niveau=NiveauUrgence.BASSE,
                            titre=f"📊 {appareil.nom} — 80% de durée de vie atteint",
                            message=f"Âge: {age_ans:.1f}ans / {duree_vie}ans estimés. Prévoir le budget remplacement.",
                            action_suggeree="Surveiller les signes d'usure",
                            metadata={"id": appareil.id, "nom": appareil.nom, "age_ans": round(age_ans, 1)},
                        )
                    )

        except Exception as e:
            logger.warning(f"Évaluation durée vie appareils échouée: {e}")

        return alertes


    @avec_gestion_erreurs(default_return={})
    def _collecter_contexte_famille(self) -> dict:
        """Collecte le contexte familial pertinent pour le briefing maison.

        Extrait depuis ContexteFamilialService:
        - Anniversaires dans les 7 prochains jours
        - Crèche fermée aujourd'hui (bool)
        - Activités familiales prévues aujourd'hui
        """
        try:
            from src.services.famille.contexte import obtenir_service_contexte_familial

            contexte = obtenir_service_contexte_familial().obtenir_contexte()
            result: dict = {}

            # Anniversaires J-7
            anniversaires = [
                a for a in (contexte.get("anniversaires_proches") or [])
                if (a.get("jours_restants") or 99) <= 7
            ]
            if anniversaires:
                result["anniversaires_proches"] = anniversaires

            # Crèche fermée aujourd'hui
            jours_speciaux = contexte.get("jours_speciaux") or []
            if any(j.get("type") == "creche" and j.get("jours_restants") == 0 for j in jours_speciaux):
                result["creche_fermee_auj"] = True

            # Activités prévues aujourd'hui
            auj = date.today().isoformat()
            activites_auj = [
                a for a in (contexte.get("activites_a_venir") or [])
                if a.get("date") == auj
            ]
            if activites_auj:
                result["activites_auj"] = activites_auj

            return result
        except Exception as e:
            logger.warning(f"Collecte contexte famille échouée: {e}")
            return {}


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("contexte_maison", tags={"maison"})
def obtenir_contexte_maison_service() -> ContexteMaisonService:
    """Factory singleton pour le service contexte maison."""
    return ContexteMaisonService()


def obtenir_service_contexte_maison() -> ContexteMaisonService:
    """Alias français."""
    return get_contexte_maison_service()


# ─── Aliases rétrocompatibilité  ───────────────────────────────
get_contexte_maison_service = obtenir_contexte_maison_service  # alias rétrocompatibilité 
