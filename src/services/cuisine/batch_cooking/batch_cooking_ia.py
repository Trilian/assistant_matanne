"""
Mixin IA pour le batch cooking — génération de plans et suggestions de recettes.

Deux pipelines de génération :
- generer_plan_ia() : à partir d'IDs recettes en DB → SessionBatchIA (simplifié)
- generer_plan_depuis_planning() : à partir d'un dict planning → dict détaillé
  (pipeline utilisé par le module UI batch_cooking_detaille)
"""

import json
import logging
import math

from sqlalchemy.orm import Session, selectinload

from src.core.decorators import (
    avec_cache,
    avec_gestion_erreurs,
    avec_resilience,
    avec_session_db,
)
from src.core.exceptions import ErreurValidation
from src.core.models import Recette
from src.core.monitoring import chronometre
from src.core.validation.sanitizer import NettoyeurEntrees

from .constantes import ROBOTS_DISPONIBLES, ROBOTS_INFO
from .types import PlanBatchDetailIA, SessionBatchIA

logger = logging.getLogger(__name__)

# Nombre max de recettes par appel IA avant découpage automatique
_MAX_RECETTES_PAR_APPEL = 4
_MAX_TOKENS = 16000

_SYSTEM_PROMPT_DETAIL = (
    "Tu es un chef expérimenté spécialiste du batch cooking familial. "
    "Réponds UNIQUEMENT en JSON valide. Sois très détaillé et concret "
    "sur les découpes, poids, températures et temps."
)


def _sanitiser_texte(texte: str, longueur_max: int = 200) -> str:
    """Sanitize user text before injection into IA prompt."""
    return NettoyeurEntrees.nettoyer_chaine(texte, longueur_max=longueur_max)


def _compter_recettes(planning_data: dict) -> int:
    """Compte le nombre de recettes non-réchauffées dans le planning."""
    count = 0
    for _jour, repas in planning_data.items():
        for type_repas in ("midi", "soir"):
            r = repas.get(type_repas, {})
            if r and isinstance(r, dict) and not r.get("est_rechauffe"):
                count += 1
    return count


def _construire_prompt_detail(
    planning_data: dict, type_session: str, avec_jules: bool, robots_section: str
) -> str:
    """Construit le prompt IA pour la génération batch cooking détaillée.

    Tous les textes utilisateur (noms de recettes, type de session) sont
    sanitisés avant injection pour empêcher le prompt injection.
    """
    type_session_safe = _sanitiser_texte(type_session, 50)
    jules_txt = (
        "Avec Jules (19 mois) - prévoir des tâches simples et sécurisées pour lui"
        if avec_jules
        else "Session solo"
    )

    prompt = f"""Expert batch cooking familial. Génère des instructions détaillées et concrètes.

SESSION: {type_session_safe.upper()}
{jules_txt}

ÉQUIPEMENT:
{robots_section}

RECETTES À PRÉPARER:
"""

    for jour, repas in planning_data.items():
        jour_safe = _sanitiser_texte(str(jour), 50)
        for type_repas in ("midi", "soir"):
            r = repas.get(type_repas, {})
            if r and isinstance(r, dict) and not r.get("est_rechauffe"):
                nom_safe = _sanitiser_texte(r.get("nom", "Recette"), 200)
                prompt += f"\n- {jour_safe} {type_repas}: {nom_safe}"

    prompt += """

RÉPONDS EN JSON VALIDE avec cette structure:
{"session": {"duree_estimee_minutes": 120, "conseils_organisation": ["..."]},
 "recettes": [{"nom": "...", "pour_jours": ["Lundi midi"], "portions": 4,
   "ingredients": [{"nom": "carottes", "quantite": "500g", "decoupe": "rondelles 5mm", "tache_jules": "Laver"}],
   "etapes_batch": [{"titre": "Découper carottes en rondelles 5mm", "duree_minutes": 10, "robot": null, "temperature": null, "est_passif": false, "detail": "Économe, rondelles régulières 5mm", "jules_participation": false, "tache_jules": null}],
   "instructions_finition": ["Réchauffer 3min micro-ondes"],
   "stockage": "Boîte hermétique frigo", "duree_conservation_jours": 3}],
 "moments_jules": [{"temps": "0-15min", "tache": "Laver légumes"}],
 "timeline": [{"debut_min": 0, "fin_min": 15, "tache": "Découpe légumes", "robot": null}]}

RÈGLES:
1. Étapes CONCRÈTES: découpe exacte, grammes, °C, durée. Jamais "les légumes" → nommer chaque légume avec quantité
2. Robot utilisé: programme exact, température, vitesse, durée
3. PARALLÉLISER: pendant qu'un robot tourne (est_passif=true), travailler sur une autre recette. La timeline montre les opérations simultanées
4. Quantités en grammes/ml (sauf pièces: oeufs, oignons). Finition = réchauffage/assaisonnement jour J"""

    if avec_jules:
        prompt += "\n5. Jules 19 mois: UNIQUEMENT laver, mélanger dans un bol, verser (PAS de couteau, PAS de chaleur)"

    prompt += "\n\nRéponds UNIQUEMENT en JSON valide, sans commentaire ni markdown."

    return prompt


def _valider_reponse(response: dict | str | None) -> dict | None:
    """Valide et répare la réponse IA. Retourne un dict valide ou None."""
    if response and isinstance(response, dict):
        logger.info(
            "Réponse IA dict reçue: %d chars, clés=%s, nb_recettes=%d",
            len(str(response)),
            list(response.keys()),
            len(response.get("recettes", [])),
        )
        if "recettes" not in response or not isinstance(response.get("recettes"), list):
            logger.warning("Réponse IA sans 'recettes' valide. Clés: %s", list(response.keys()))
            if "session" in response and isinstance(response["session"], dict):
                inner = response["session"]
                if isinstance(inner.get("recettes"), list):
                    response["recettes"] = inner["recettes"]
                    return response
            return None
        return response

    if response and isinstance(response, str):
        logger.warning("generer_json a retourné une string (%d chars)", len(response))
        try:
            from src.core.ai.parser import AnalyseurIA

            json_str = AnalyseurIA._extraire_objet_json(response)
            json_str = AnalyseurIA._reparer_intelligemment(json_str)
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                logger.info("Parse manuelle réussie: clés=%s", list(parsed.keys()))
                return parsed
        except Exception as e:
            logger.warning("Parse manuelle échouée: %s", e)

    logger.warning("Réponse IA invalide ou vide")
    return None


def _valider_avec_pydantic(data: dict) -> dict:
    """Valide la réponse avec PlanBatchDetailIA (best-effort, ne lève jamais)."""
    try:
        plan = PlanBatchDetailIA.model_validate(data)
        return plan.model_dump()
    except Exception:
        logger.debug("Validation Pydantic permissive échouée, retour du dict brut")
        return data


def _construire_robots_section(robots_user: list[str]) -> str:
    """Construit la section robots du prompt."""
    robots_txt = []
    for r in robots_user:
        info = ROBOTS_INFO.get(r, {})
        parallel = (
            "peut fonctionner en parallèle"
            if info.get("peut_parallele")
            else "UNE tâche à la fois"
        )
        nom = _sanitiser_texte(info.get("nom", r), 50)
        robots_txt.append(f"  - {nom} ({parallel})")
    return "\n".join(robots_txt)


def _decouper_planning(planning_data: dict) -> list[dict]:
    """Découpe le planning en sous-plannings de max _MAX_RECETTES_PAR_APPEL recettes."""
    items: list[tuple[str, str, dict]] = []
    for jour, repas in planning_data.items():
        for type_repas in ("midi", "soir"):
            r = repas.get(type_repas, {})
            if r and isinstance(r, dict) and not r.get("est_rechauffe"):
                items.append((jour, type_repas, r))

    taille_chunk = max(2, math.ceil(len(items) / 2))
    chunks: list[dict] = []
    for i in range(0, len(items), taille_chunk):
        sub: dict = {}
        for jour, type_repas, r in items[i : i + taille_chunk]:
            sub.setdefault(jour, {})[type_repas] = r
        chunks.append(sub)
    return chunks


def _fusionner_resultats(resultats: list[dict]) -> dict:
    """Fusionne plusieurs résultats IA en un seul."""
    if len(resultats) == 1:
        return resultats[0]

    merged: dict = {
        "session": {"duree_estimee_minutes": 0, "conseils_organisation": []},
        "recettes": [],
        "moments_jules": [],
        "timeline": [],
    }

    offset_min = 0
    for r in resultats:
        session = r.get("session", {})
        duree = session.get("duree_estimee_minutes", 0)
        merged["session"]["duree_estimee_minutes"] += duree
        merged["session"]["conseils_organisation"].extend(
            session.get("conseils_organisation", [])
        )
        merged["recettes"].extend(r.get("recettes", []))
        merged["moments_jules"].extend(r.get("moments_jules", []))

        for entry in r.get("timeline", []):
            shifted = {**entry}
            shifted["debut_min"] = entry.get("debut_min", 0) + offset_min
            shifted["fin_min"] = entry.get("fin_min", 0) + offset_min
            merged["timeline"].append(shifted)

        offset_min += duree

    return merged


class BatchCookingIAMixin:
    """Mixin pour les fonctionnalités IA du batch cooking.

    Fournit :
    - generer_plan_ia() : Plan simplifié à partir de recettes DB
    - generer_plan_depuis_planning() : Plan détaillé à partir du planning dict (UI)
    - suggerer_recettes_batch() : Suggestions de recettes
    """

    # ═══════════════════════════════════════════════════════════
    # PIPELINE DÉTAILLÉ (dict planning → instructions complètes)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return={})
    @chronometre("ia.batch_cooking.generer_plan_detail", seuil_alerte_ms=30000)
    def generer_plan_depuis_planning(
        self,
        planning_data: dict,
        type_session: str,
        avec_jules: bool,
        robots_user: list[str] | None = None,
    ) -> dict:
        """Génère les instructions détaillées de batch cooking avec l'IA.

        Inputs sanitisés (anti prompt-injection), retry automatique via
        @avec_resilience, validation Pydantic best-effort.

        Stratégie:
        1. Appel unique si ≤ _MAX_RECETTES_PAR_APPEL recettes
        2. Si échec, retry avec max_tokens augmenté
        3. Si toujours en échec, découpage en sous-groupes + fusion
        """
        if not robots_user:
            robots_user = ["four", "plaques"]

        robots_section = _construire_robots_section(robots_user)
        nb_recettes = _compter_recettes(planning_data)
        logger.info(
            "Batch cooking: %d recettes, session=%s, jules=%s",
            nb_recettes, type_session, avec_jules,
        )

        prompt = _construire_prompt_detail(
            planning_data, type_session, avec_jules, robots_section
        )

        # Tentative 1 : appel unique
        result = self._appel_ia_detail(prompt, max_tokens=_MAX_TOKENS)
        if result:
            return _valider_avec_pydantic(result)

        # Tentative 2 : retry avec plus de tokens
        logger.warning("Tentative 1 échouée, retry avec max_tokens augmenté")
        result = self._appel_ia_detail(prompt, max_tokens=_MAX_TOKENS + 8000)
        if result:
            return _valider_avec_pydantic(result)

        # Tentative 3 : découpage en sous-groupes (si assez de recettes)
        if nb_recettes > 2:
            logger.warning(
                "Tentative 2 échouée, découpage en sous-groupes (%d recettes)", nb_recettes
            )
            chunks = _decouper_planning(planning_data)
            resultats: list[dict] = []
            for i, chunk in enumerate(chunks):
                logger.info(
                    "Génération chunk %d/%d: %d recettes",
                    i + 1, len(chunks), _compter_recettes(chunk),
                )
                chunk_prompt = _construire_prompt_detail(
                    chunk, type_session, avec_jules, robots_section
                )
                chunk_result = self._appel_ia_detail(chunk_prompt)
                if chunk_result:
                    resultats.append(chunk_result)
                else:
                    logger.error("Chunk %d échoué", i + 1)
                    return {}

            merged = _fusionner_resultats(resultats)
            logger.info(
                "Fusion réussie: %d recettes, durée=%dmin",
                len(merged.get("recettes", [])),
                merged.get("session", {}).get("duree_estimee_minutes", 0),
            )
            return _valider_avec_pydantic(merged)

        logger.error("Toutes les tentatives ont échoué pour %d recette(s)", nb_recettes)
        return {}

    @avec_resilience(retry=1, timeout_s=60, fallback=None)
    def _appel_ia_detail(self, prompt: str, max_tokens: int = _MAX_TOKENS) -> dict | None:
        """Effectue un appel IA unique pour le batch cooking détaillé."""
        if not self._client:
            return None

        logger.info("Appel IA batch cooking: prompt=%d chars, max_tokens=%d", len(prompt), max_tokens)

        response = self._client.generer_json(
            prompt=prompt,
            system_prompt=_SYSTEM_PROMPT_DETAIL,
            max_tokens=max_tokens,
        )

        return _valider_reponse(response)

    # ═══════════════════════════════════════════════════════════
    # PIPELINE SIMPLIFIÉ (recettes DB → plan batch)
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
        """Génère un plan de batch cooking optimisé avec l'IA (schéma simplifié)."""
        recettes = (
            db.query(Recette)
            .options(selectinload(Recette.etapes))
            .filter(Recette.id.in_(recettes_ids))
            .all()
        )
        if not recettes:
            raise ErreurValidation("Aucune recette trouvée")

        recettes_context = []
        for r in recettes:
            etapes_text = ""
            if r.etapes:
                etapes_text = "\n".join(
                    [f"  {e.ordre}. {e.description} ({e.duree or '?'} min)" for e in r.etapes]
                )

            recettes_context.append(
                f"""
Recette: {_sanitiser_texte(r.nom, 200)}
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

        logger.info("🤖 Génération plan batch cooking IA (%d recettes)", len(recettes))

        result = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=SessionBatchIA,
            system_prompt="Tu es un chef expert en batch cooking et organisation de cuisine. Retourne UNIQUEMENT du JSON valide, sans aucun texte avant ou après.",
            temperature=0.5,
            max_tokens=4000,
        )

        if result:
            logger.info("✅ Plan batch cooking généré: %d min estimées", result.duree_totale_estimee)

        return result

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS
    # ═══════════════════════════════════════════════════════════

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

        if robots_disponibles:
            for robot in robots_disponibles:
                if robot == "cookeo":
                    query = query.filter(Recette.compatible_cookeo)
                elif robot == "monsieur_cuisine":
                    query = query.filter(Recette.compatible_monsieur_cuisine)
                elif robot == "airfryer":
                    query = query.filter(Recette.compatible_airfryer)

        if avec_jules:
            query = query.filter(Recette.compatible_bebe)

        recettes = query.order_by(Recette.congelable.desc()).limit(nb_recettes * 2).all()
        return recettes[:nb_recettes]
