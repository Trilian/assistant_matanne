"""
Service inter-modules : Récolte jardin → Recettes semaine suivante.

B6 (I1): Quand une récolte jardin est validée, utiliser l'IA pour
suggérer des recettes utilisant les produits récoltés et les
intégrer dans le planning de la semaine suivante.
"""

import json
import logging
from datetime import date, timedelta
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class JardinRecettesInteractionService:
    """Bridge récolte jardin → suggestions recettes pour la semaine suivante."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def suggerer_recettes_depuis_recolte(
        self,
        *,
        jours_horizon: int = 7,
        limite_recettes: int = 5,
        db=None,
    ) -> dict[str, Any]:
        """Cherche les récoltes récentes et suggère des recettes les utilisant.

        Combine la recherche en base (recettes existantes contenant ces ingrédients)
        avec une suggestion IA pour les produits sans correspondance directe.

        Args:
            jours_horizon: nombre de jours de récolte récente à considérer
            limite_recettes: nombre max de recettes à suggérer
            db: Session DB

        Returns:
            Dict avec recoltes_recentes, recettes_suggerees, suggestions_ia
        """
        from src.core.models import Recette
        from src.core.models.recettes import RecetteIngredient
        from src.core.models.temps_entretien import ActionPlante, PlanteJardin

        # Récupérer les récoltes récentes
        date_limite = date.today() - timedelta(days=jours_horizon)
        actions_recolte = (
            db.query(ActionPlante)
            .join(PlanteJardin, PlanteJardin.id == ActionPlante.plante_id)
            .filter(
                ActionPlante.type_action == "recolte",
                ActionPlante.date_action >= date_limite,
            )
            .all()
        )

        if not actions_recolte:
            # Fallback: chercher les plantes en période de récolte ce mois
            mois_courant = date.today().month
            plantes = db.query(PlanteJardin).all()
            noms_recolte = []
            for p in plantes:
                mois_recolte = self._parser_mois_json(p.mois_recolte)
                if mois_courant in mois_recolte:
                    noms_recolte.append(p.nom.lower())

            if not noms_recolte:
                return {
                    "recoltes_recentes": [],
                    "recettes_suggerees": [],
                    "message": "Aucune récolte récente ni plante en période de récolte.",
                }
        else:
            noms_recolte = list({
                a.plante.nom.lower()
                for a in actions_recolte
                if hasattr(a, "plante") and a.plante
            })

        # Chercher des recettes existantes utilisant ces ingrédients
        from sqlalchemy import func
        from src.core.models import Ingredient

        recettes_trouvees = []
        for nom_produit in noms_recolte:
            ingredients = (
                db.query(Ingredient)
                .filter(func.lower(Ingredient.nom).contains(nom_produit))
                .all()
            )
            ing_ids = [i.id for i in ingredients]
            if not ing_ids:
                continue

            recettes = (
                db.query(Recette)
                .join(RecetteIngredient, RecetteIngredient.recette_id == Recette.id)
                .filter(RecetteIngredient.ingredient_id.in_(ing_ids))
                .limit(limite_recettes)
                .all()
            )
            for r in recettes:
                if r.id not in {rt["id"] for rt in recettes_trouvees}:
                    recettes_trouvees.append({
                        "id": r.id,
                        "nom": r.nom,
                        "temps_total": (r.temps_preparation or 0) + (r.temps_cuisson or 0),
                        "produit_jardin": nom_produit,
                    })

        # Générer des suggestions IA si peu de résultats DB
        suggestions_ia = []
        if len(recettes_trouvees) < limite_recettes:
            suggestions_ia = self._suggerer_via_ia(noms_recolte)

        return {
            "recoltes_recentes": noms_recolte,
            "recettes_suggerees": recettes_trouvees[:limite_recettes],
            "suggestions_ia": suggestions_ia,
            "nb_total": len(recettes_trouvees) + len(suggestions_ia),
            "message": (
                f"{len(noms_recolte)} produit(s) du jardin → "
                f"{len(recettes_trouvees)} recette(s) trouvée(s), "
                f"{len(suggestions_ia)} suggestion(s) IA."
            ),
        }

    @avec_gestion_erreurs(default_return=[])
    def _suggerer_via_ia(self, produits: list[str]) -> list[dict[str, Any]]:
        """Génère des idées de recettes via Mistral pour les produits du jardin."""
        try:
            from src.core.ai import obtenir_client_ia

            client = obtenir_client_ia()
            if not client:
                return []

            prompt = (
                f"Je viens de récolter du jardin : {', '.join(produits)}. "
                "Suggère 3 recettes familiales simples utilisant ces produits. "
                "Réponds en JSON: [{\"nom\": \"...\", \"description\": \"...\", "
                "\"temps_minutes\": 30, \"produits_jardin_utilises\": [\"...\"]}]"
            )
            response = client.generer_json(
                prompt=prompt,
                system_prompt="Tu es un chef cuisinier familial. Réponds uniquement en JSON valide.",
                max_tokens=1000,
                temperature=0.7,
            )

            if isinstance(response, list):
                return response[:3]
            if isinstance(response, dict) and "recettes" in response:
                return response["recettes"][:3]
            return []
        except Exception as e:
            logger.warning(f"Suggestions IA récolte échouées: {e}")
            return []

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def integrer_recette_planning_semaine_suivante(
        self,
        recette_id: int,
        type_repas: str = "soir",
        *,
        db=None,
    ) -> dict[str, Any]:
        """Intègre une recette suggérée dans le planning de la semaine suivante.

        Args:
            recette_id: ID de la recette à planifier
            type_repas: midi ou soir
            db: Session DB

        Returns:
            Dict de confirmation
        """
        from src.core.models import Planning, Recette, Repas

        recette = db.query(Recette).filter_by(id=recette_id).first()
        if not recette:
            return {"ok": False, "message": f"Recette {recette_id} introuvable."}

        # Trouver ou créer le planning de la semaine prochaine
        lundi_prochain = date.today() + timedelta(days=(7 - date.today().weekday()))
        planning = (
            db.query(Planning)
            .filter(Planning.semaine_debut == lundi_prochain)
            .first()
        )
        if not planning:
            planning = Planning(
                semaine_debut=lundi_prochain,
                statut="brouillon",
            )
            db.add(planning)
            db.flush()

        # Trouver le premier jour libre
        repas_existants = (
            db.query(Repas)
            .filter(
                Repas.planning_id == planning.id,
                Repas.type_repas == type_repas,
            )
            .all()
        )
        jours_occupes = {r.date_repas for r in repas_existants if r.date_repas}

        jour_libre = None
        for i in range(7):
            jour = lundi_prochain + timedelta(days=i)
            if jour not in jours_occupes:
                jour_libre = jour
                break

        if not jour_libre:
            return {"ok": False, "message": "Planning semaine prochaine déjà complet."}

        repas = Repas(
            planning_id=planning.id,
            recette_id=recette.id,
            date_repas=jour_libre,
            type_repas=type_repas,
            notes=f"Suggestion jardin — {recette.nom}",
        )
        db.add(repas)
        db.commit()

        logger.info(
            f"✅ Jardin→Planning: {recette.nom} planifié le {jour_libre} ({type_repas})"
        )

        return {
            "ok": True,
            "recette": recette.nom,
            "date": jour_libre.isoformat(),
            "type_repas": type_repas,
            "message": f"{recette.nom} ajouté au planning du {jour_libre.isoformat()} ({type_repas}).",
        }

    @staticmethod
    def _parser_mois_json(mois_raw: str | None) -> set[int]:
        """Parse un champ JSON de mois: '[3,4,5]' → {3, 4, 5}."""
        if not mois_raw:
            return set()
        try:
            data = json.loads(mois_raw)
            if isinstance(data, list):
                return {int(m) for m in data if str(m).isdigit()}
        except Exception:
            return set()
        return set()


@service_factory(
    "jardin_recettes_interaction", tags={"cuisine", "jardin", "recettes", "ia"}
)
def obtenir_service_jardin_recettes() -> JardinRecettesInteractionService:
    """Factory pour le bridge récolte jardin → recettes."""
    return JardinRecettesInteractionService()
