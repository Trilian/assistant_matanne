"""
Mixin IA pour le batch cooking — génération de plans et suggestions de recettes.

Regroupe les méthodes d'intégration IA :
- Génération de plan batch cooking optimisé via Mistral
- Suggestion de recettes adaptées au batch cooking
"""

import logging

from sqlalchemy.orm import Session, selectinload

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.exceptions import ErreurValidation
from src.core.models import Recette
from src.core.monitoring import chronometre

from .constantes import ROBOTS_DISPONIBLES
from .types import SessionBatchIA

logger = logging.getLogger(__name__)


class BatchCookingIAMixin:
    """Mixin pour les fonctionnalités IA du batch cooking.

    Fournit :
    - Génération de plans optimisés via l'IA (parallélisation, robots, Jules)
    - Suggestions de recettes adaptées au batch cooking
    """

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION IA
    # ═══════════════════════════════════════════════════════════

    @avec_cache(
        ttl=3600,
        key_func=lambda self, recettes_ids, robots_disponibles, avec_jules=False: (
            f"batch_plan_{'-'.join(map(str, recettes_ids))}_{avec_jules}"
        ),
    )
    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.batch_cooking.generer_plan", seuil_alerte_ms=15000)
    @avec_session_db
    def generer_plan_ia(
        self,
        recettes_ids: list[int],
        robots_disponibles: list[str],
        avec_jules: bool = False,
        db: Session | None = None,
    ) -> SessionBatchIA | None:
        """Génère un plan de batch cooking optimisé avec l'IA.

        L'IA optimise :
        - L'ordre des étapes pour paralléliser au maximum
        - L'utilisation des robots pour gagner du temps
        - Les conseils pour cuisiner avec un enfant présent
        """
        # Récupérer les recettes
        recettes = (
            db.query(Recette)
            .options(selectinload(Recette.etapes))
            .filter(Recette.id.in_(recettes_ids))
            .all()
        )
        if not recettes:
            raise ErreurValidation("Aucune recette trouvée")

        # Construire le contexte
        recettes_context = []
        for r in recettes:
            etapes_text = ""
            if r.etapes:
                etapes_text = "\n".join(
                    [f"  {e.ordre}. {e.description} ({e.duree or '?'} min)" for e in r.etapes]
                )

            recettes_context.append(
                f"""
Recette: {r.nom}
- Temps préparation: {r.temps_preparation} min
- Temps cuisson: {r.temps_cuisson} min
- Portions: {r.portions}
- Compatible batch: {r.compatible_batch}
- Congelable: {r.congelable}
- Robots: {", ".join(r.robots_compatibles) if r.robots_compatibles else "Aucun"}
- Étapes:
{etapes_text}
"""
            )

        robots_text = ", ".join(
            [ROBOTS_DISPONIBLES.get(r, {}).get("nom", r) for r in robots_disponibles]
        )
        jules_context = (
            """
⚠️ IMPORTANT - JULES (bébé 19 mois) sera présent !
- Éviter les étapes bruyantes pendant la sieste (13h-15h)
- Prévoir des moments calmes où il peut observer/aider
- Signaler les étapes dangereuses (four chaud, friture, couteaux)
- Optimiser pour terminer avant 12h si possible
"""
            if avec_jules
            else ""
        )

        prompt = f"""GÉNÈRE UN PLAN DE BATCH COOKING OPTIMISÉ EN JSON UNIQUEMENT.

RECETTES À PRÉPARER:
{"".join(recettes_context)}

ÉQUIPEMENTS DISPONIBLES:
{robots_text}

{jules_context}

OBJECTIF:
1. Optimiser le temps total en parallélisant les tâches
2. Regrouper les étapes par robot/équipement
3. Prévoir les temps de supervision (cuisson four, etc.)
4. Indiquer clairement les étapes bruyantes

RETOURNE UNIQUEMENT CE JSON (pas de markdown, pas d'explication):
{{
    "recettes": ["Nom recette 1", "Nom recette 2"],
    "duree_totale_estimee": 120,
    "etapes": [
        {{
            "ordre": 1,
            "titre": "Préparer les légumes",
            "description": "Éplucher et couper les carottes, pommes de terre et oignons",
            "duree_minutes": 15,
            "robots": ["hachoir"],
            "groupe_parallele": 0,
            "est_supervision": false,
            "alerte_bruit": true,
            "temperature": null,
            "recette_nom": "Boeuf bourguignon"
        }}
    ],
    "conseils_jules": ["Moment idéal pour Jules: étape 3 (mélanger les ingrédients)"],
    "ordre_optimal": "Commencer par les cuissons longues au four, puis préparer les plats rapides en parallèle"
}}

RÈGLES:
- Les étapes avec le même groupe_parallele peuvent être faites simultanément
- est_supervision=true pour les étapes passives (surveiller la cuisson)
- alerte_bruit=true pour mixeur, hachoir, robot bruyant
- Grouper intelligemment pour minimiser le temps total
"""

        logger.info(f"🤖 Génération plan batch cooking IA ({len(recettes)} recettes)")

        result = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=SessionBatchIA,
            system_prompt="Tu es un chef expert en batch cooking et organisation de cuisine. Retourne UNIQUEMENT du JSON valide, sans aucun texte avant ou après.",
            temperature=0.5,
            max_tokens=4000,
        )

        if result:
            logger.info(f"✅ Plan batch cooking généré: {result.duree_totale_estimee} min estimées")

        return result

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def suggerer_recettes_batch(
        self,
        nb_recettes: int = 4,
        robots_disponibles: list[str] | None = None,
        avec_jules: bool = False,
        planning_id: int | None = None,
        db: Session | None = None,
    ) -> list[Recette]:
        """Suggère des recettes adaptées au batch cooking."""
        query = db.query(Recette).filter(Recette.compatible_batch)

        # Filtrer par robots si spécifié
        if robots_disponibles:
            # Filtre complexe sur les robots
            for robot in robots_disponibles:
                if robot == "cookeo":
                    query = query.filter(Recette.compatible_cookeo)
                elif robot == "monsieur_cuisine":
                    query = query.filter(Recette.compatible_monsieur_cuisine)
                elif robot == "airfryer":
                    query = query.filter(Recette.compatible_airfryer)

        # Filtrer pour bébé si Jules présent
        if avec_jules:
            query = query.filter(Recette.compatible_bebe)

        # Prioriser les recettes congelables
        recettes = query.order_by(Recette.congelable.desc()).limit(nb_recettes * 2).all()

        # Retourner un échantillon varié
        return recettes[:nb_recettes]
