"""
Mixin IA pour la génération de plannings.

Contient les méthodes de génération IA extraites de ServicePlanning:
- generer_planning_ia: Génération complète d'un planning hebdomadaire via Mistral AI
- suggerer_recettes_equilibrees: Suggestions de recettes équilibrées par jour

Ces méthodes utilisent BaseAIService (via MRO) pour l'appel IA avec
rate limiting et cache automatiques.
"""

import logging
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.caching import obtenir_cache
from src.core.date_utils.helpers import obtenir_noms_jours_semaine
from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import Planning, Repas
from src.core.monitoring import chronometre
from src.services.core.event_bus_mixin import emettre_evenement_simple

from .nutrition import determine_protein_type
from .types import JourPlanning, ParametresEquilibre, RecetteEnrichieIA

logger = logging.getLogger(__name__)


class PlanningIAGenerationMixin:
    """
    Mixin contenant les méthodes de génération IA pour le planning.

    Dépendances MRO:
    - BaseAIService → call_with_list_parsing_sync, rate limiting
    - PlanningAIMixin → build_planning_context (contexte métier)

    Usage:
        class ServicePlanning(BaseService, BaseAIService, PlanningAIMixin, PlanningIAGenerationMixin):
            ...
    """

    # ═══════════════════════════════════════════════════════════
    # HELPERS INTERNES
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _trouver_ou_creer_recette(db: Session, nom: str) -> int:
        """Retourne l'id d'une recette existante (lookup insensible à la casse)
        ou crée un stub minimal si elle n'existe pas encore."""
        from src.core.models.recettes import Recette

        recette = db.query(Recette).filter(func.lower(Recette.nom) == nom.lower()).first()
        if recette is None:
            recette = Recette(nom=nom, temps_preparation=30)
            db.add(recette)
            db.flush()
        return recette.id

    # ═══════════════════════════════════════════════════════════
    # SUGGESTIONS ÉQUILIBRÉES
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def suggerer_recettes_equilibrees(
        self,
        semaine_debut: date,
        parametres: ParametresEquilibre,
        db: Session | None = None,
    ) -> list[dict]:
        """Suggère des recettes équilibrées pour chaque jour.

        Retourne 3 options par jour avec score d'équilibre.
        Utilise les fonctions pures de planning.utils.

        Args:
            semaine_debut: Date de début de semaine
            parametres: Contraintes d'équilibre
            db: Database session

        Returns:
            List de dicts {jour, type_repas, suggestions: [{nom, description, raison}]}
        """
        from src.core.models import Recette

        # Utiliser planning.utils pour les jours de la semaine
        jours_semaine = obtenir_noms_jours_semaine()
        suggestions_globales = []

        for idx, jour_name in enumerate(jours_semaine):
            jour_lower = jour_name.lower()
            date_jour = semaine_debut + timedelta(days=idx)

            # Utiliser planning.utils pour déterminer le type de protéine
            type_proteine, raison_jour = determine_protein_type(
                jour_lower,
                poisson_jours=parametres.poisson_jours,
                viande_rouge_jours=parametres.viande_rouge_jours,
                vegetarien_jours=parametres.vegetarien_jours,
            )

            # Requête base pour récupérer 3 recettes de ce type
            query = db.query(Recette).filter(Recette.est_equilibre)

            # Filtrer par type de protéine
            if type_proteine == "poisson":
                query = query.filter(Recette.type_proteines.ilike("%poisson%"))
            elif type_proteine == "viande_rouge":
                query = query.filter(Recette.type_proteines.ilike("%viande%"))
            elif type_proteine == "vegetarien":
                query = query.filter(Recette.est_vegetarien)

            # Exclure les ingrédients interdits
            for ingredient_exc in parametres.ingredients_exclus:
                # Filtre basique (devrait utiliser une vraie relation en prod)
                query = query.filter(~Recette.description.ilike(f"%{ingredient_exc}%"))

            # Récupérer 3 suggestions
            recettes = query.limit(3).all()

            suggestions_jour = []
            for recette in recettes:
                suggestions_jour.append(
                    {
                        "id": recette.id,
                        "nom": recette.nom,
                        "description": recette.description,
                        "temps_total": (recette.temps_preparation or 0)
                        + (recette.temps_cuisson or 0),
                        "type_repas": "dejeuner" if idx % 2 == 0 else "diner",
                        "raison": raison_jour,
                        "type_proteines": recette.type_proteines,
                    }
                )

            # Si pas assez, ajouter des recettes équilibrées quelconques
            if len(suggestions_jour) < 3:
                autres = (
                    db.query(Recette)
                    .filter(Recette.id.notin_([s["id"] for s in suggestions_jour]))
                    .limit(3 - len(suggestions_jour))
                    .all()
                )

                for recette in autres:
                    suggestions_jour.append(
                        {
                            "id": recette.id,
                            "nom": recette.nom,
                            "description": recette.description,
                            "temps_total": (recette.temps_preparation or 0)
                            + (recette.temps_cuisson or 0),
                            "type_repas": "dejeuner" if idx % 2 == 0 else "diner",
                            "raison": "📝 Alternative équilibrée",
                            "type_proteines": getattr(recette, "type_proteines", "mixte"),
                        }
                    )

            suggestions_globales.append(
                {
                    "jour": jour_name,
                    "jour_index": idx,
                    "date": date_jour.isoformat(),
                    "raison_jour": raison_jour,
                    "suggestions": suggestions_jour[:3],
                }
            )

        logger.info(f"✅ Generated {len(suggestions_globales)} days of balanced suggestions")
        return suggestions_globales

    # ═══════════════════════════════════════════════════════════
    # GÉNÉRATION IA PLANNING HEBDOMADAIRE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @chronometre("ia.planning.generer", seuil_alerte_ms=15000)
    @avec_session_db
    def generer_planning_ia(
        self,
        semaine_debut: date,
        preferences: dict[str, Any] | None = None,
        db: Session | None = None,
    ) -> Planning | None:
        """Génère un planning hebdomadaire avec l'IA.

        Generates a complete weekly meal plan using Mistral AI.
        Includes breakfast/lunch/dinner organization.

        Args:
            semaine_debut: Start date of the week (Monday)
            preferences: Optional preferences dict for meal types, dietary restrictions, etc.
            db: Database session (injected by @avec_session_db)

        Returns:
            Planning object with generated meals, or None if generation fails
        """
        # Utilisation du Mixin pour contexte planning
        context = self.build_planning_context(
            config=preferences or {},
            semaine_debut=semaine_debut.strftime("%d/%m/%Y"),
        )

        semaine_fin = semaine_debut + timedelta(days=6)

        # Construire prompt ultra-direct (comme pour recettes)
        prompt = f"""GENERATE A 7-DAY MEAL PLAN (MONDAY-SUNDAY) IN JSON FORMAT ONLY.

CONTEXT:
{context}

OUTPUT ONLY THIS JSON STRUCTURE (no other text, no markdown, no code blocks):
{{"items": [
  {{
    "jour": "Lundi",
    "petit_dejeuner": "Tartines beurre confiture",
    "petit_dejeuner_est_recette": false,
    "dejeuner": "Pâtes carbonara",
    "dejeuner_entree": "Salade verte",
    "dejeuner_entree_est_recette": false,
    "dejeuner_laitage": "Yaourt nature",
    "dejeuner_dessert": "Tarte aux pommes",
    "dejeuner_dessert_est_recette": true,
    "gouter": "Pain au chocolat",
    "gouter_est_recette": false,
    "diner": "Salade niçoise",
    "diner_entree": null,
    "diner_entree_est_recette": false,
    "diner_laitage": "Fromage",
    "diner_dessert": "Fruit de saison",
    "diner_dessert_est_recette": false
  }}
]}}

RULES:
1. Return ONLY valid JSON with exactly 7 items (one per day: Lundi→Dimanche)
2. dejeuner and diner (le PLAT principal): always a real recipe name to cook (3-50 chars)
3. petit_dejeuner: simple text on weekdays (tartines, céréales, fruit), can be est_recette=true on weekend (crêpes, gaufres...)
4. entree/dessert: optional — include only if the meal complexity warrants it; est_recette=true only if real preparation steps needed
5. laitage: text only (yaourt, fromage blanc, fromage, petits-suisses...) — never est_recette
6. gouter: MANDATORY — always a non-null short text. est_recette=true only for real preparations. Never leave null.
7. Ensure variety throughout the week — alternate proteins (fish Mon/Thu, red meat Tue, vegetarian Wed, poultry Fri)
8. null is valid ONLY for entree, laitage, dessert — never for gouter
9. No explanations, no text, ONLY JSON"""

        logger.info(f"🤖 Generating AI weekly plan starting {semaine_debut}")

        # Appel IA avec auto rate limiting & parsing
        # use_cache=False : chaque génération doit produire un planning UNIQUE (pas de réponse recyclée)
        planning_data = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=JourPlanning,
            system_prompt="Return ONLY valid JSON. No text before or after JSON. Never use markdown code blocks.",
            max_items=7,
            temperature=0.5,
            max_tokens=3000,
            use_cache=False,
        )

        # Log de debug pour voir la réponse
        if not planning_data:
            logger.warning(
                f"⚠️ Aucune donnée IA reçue pour le planning {semaine_debut} — l'appel Mistral n'a pas produit de résultat parsable."
            )
            from src.core.exceptions import ErreurServiceIA

            raise ErreurServiceIA(
                "Aucune donnée retournée par Mistral pour la génération du planning",
                message_utilisateur="L'IA n'a pas pu générer le planning. Vérifiez la clé Mistral ou réessayez.",
            )

        # Planning IA réussi
        logger.info(f"✅ Generated planning with {len(planning_data)} days using AI")

        # Archiver les plannings existants de la même semaine pour éviter les doublons.
        # (brouillons orphelins laissés par des générations précédentes)
        semaine_fin = semaine_debut + timedelta(days=6)
        db.query(Planning).filter(
            Planning.semaine_debut == semaine_debut,
            Planning.etat.notin_(["archive"]),
        ).update({"etat": "archive"}, synchronize_session=False)

        # Créer planning en DB
        # etat="brouillon" : le planning généré doit être validé par l'utilisateur
        # avant d'être activé (cf. route POST /{id}/valider).
        planning = Planning(
            nom=f"Planning {semaine_debut.strftime('%d/%m/%Y')}",
            semaine_debut=semaine_debut,
            semaine_fin=semaine_fin,
            etat="brouillon",
            genere_par_ia=True,
        )
        db.add(planning)
        db.flush()

        # Créer repas pour chaque jour
        for idx, jour_data in enumerate(planning_data):
            date_jour = semaine_debut + timedelta(days=idx)

            # Petit-déjeuner (optionnel selon ce que l'IA a fourni)
            if jour_data.petit_dejeuner:
                recette_pdj_id = (
                    self._trouver_ou_creer_recette(db, jour_data.petit_dejeuner)
                    if jour_data.petit_dejeuner_est_recette
                    else None
                )
                db.add(
                    Repas(
                        planning_id=planning.id,
                        date_repas=date_jour,
                        type_repas="petit_dejeuner",
                        notes=jour_data.petit_dejeuner,
                        recette_id=recette_pdj_id,
                    )
                )

            # Déjeuner — plat = toujours une recette stub
            recette_dej_id = self._trouver_ou_creer_recette(db, jour_data.dejeuner)
            entree_dej_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.dejeuner_entree)
                if jour_data.dejeuner_entree and jour_data.dejeuner_entree_est_recette
                else None
            )
            dessert_dej_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.dejeuner_dessert)
                if jour_data.dejeuner_dessert and jour_data.dejeuner_dessert_est_recette
                else None
            )
            db.add(
                Repas(
                    planning_id=planning.id,
                    date_repas=date_jour,
                    type_repas="dejeuner",
                    notes=jour_data.dejeuner,
                    recette_id=recette_dej_id,
                    entree=jour_data.dejeuner_entree,
                    entree_recette_id=entree_dej_recette_id,
                    laitage=jour_data.dejeuner_laitage,
                    dessert=jour_data.dejeuner_dessert,
                    dessert_recette_id=dessert_dej_recette_id,
                )
            )

            # Goûter (obligatoire — fallback si l'IA a quand même renvoyé null)
            if not jour_data.gouter:
                jour_data.gouter = "Fruit de saison"
            if jour_data.gouter:
                recette_gouter_id = (
                    self._trouver_ou_creer_recette(db, jour_data.gouter)
                    if jour_data.gouter_est_recette
                    else None
                )
                db.add(
                    Repas(
                        planning_id=planning.id,
                        date_repas=date_jour,
                        type_repas="gouter",
                        notes=jour_data.gouter,
                        recette_id=recette_gouter_id,
                    )
                )

            # Dîner — plat = toujours une recette stub
            recette_din_id = self._trouver_ou_creer_recette(db, jour_data.diner)
            entree_din_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.diner_entree)
                if jour_data.diner_entree and jour_data.diner_entree_est_recette
                else None
            )
            dessert_din_recette_id = (
                self._trouver_ou_creer_recette(db, jour_data.diner_dessert)
                if jour_data.diner_dessert and jour_data.diner_dessert_est_recette
                else None
            )
            db.add(
                Repas(
                    planning_id=planning.id,
                    date_repas=date_jour,
                    type_repas="diner",
                    notes=jour_data.diner,
                    recette_id=recette_din_id,
                    entree=jour_data.diner_entree,
                    entree_recette_id=entree_din_recette_id,
                    laitage=jour_data.diner_laitage,
                    dessert=jour_data.diner_dessert,
                    dessert_recette_id=dessert_din_recette_id,
                )
            )

        db.commit()
        db.refresh(planning)

        emettre_evenement_simple(
            "planning.modifie",
            {"planning_id": planning.id, "semaine": str(semaine_debut), "action": "genere_ia"},
            source="planning_ia",
        )

        # Invalider cache
        obtenir_cache().invalidate(pattern="planning")

        logger.info(f"✅ Generated AI planning for week starting {semaine_debut}")

        # Enrichir les recettes stubs (étapes + ingrédients) en batches après le commit
        try:
            self.enrichir_recettes_stub_planning(planning.id)
        except Exception as _enr_err:
            logger.warning("[planning] Enrichissement stubs échoué (non bloquant): %s", _enr_err)

        return planning

    # ═══════════════════════════════════════════════════════════
    # ENRICHISSEMENT DES RECETTES STUBS
    # ═══════════════════════════════════════════════════════════

    def enrichir_recettes_stub_planning(self, planning_id: int) -> None:
        """Enrichit en arrière-plan les recettes stubs créées lors de la génération.

        Appelé après ``generer_planning_ia`` via BackgroundTasks : interroge l'IA
        pour obtenir les étapes et ingrédients des recettes qui n'ont encore aucune
        étape enregistrée.

        Args:
            planning_id: ID du planning dont les recettes stubs sont à enrichir.
        """
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models import EtapeRecette, Ingredient, RecetteIngredient, Repas
            from src.core.models.recettes import Recette

            with obtenir_contexte_db() as session:
                # Collecter tous les recette_id liés au planning
                repas_list = session.query(Repas).filter(Repas.planning_id == planning_id).all()
                recette_ids: set[int] = set()
                for r in repas_list:
                    for rid in (r.recette_id, r.entree_recette_id, r.dessert_recette_id):
                        if rid is not None:
                            recette_ids.add(rid)

                if not recette_ids:
                    return

                # Filtrer celles sans étapes (stubs) — stocker (id, nom) pour éviter les objets détachés
                stubs_data: list[tuple[int, str]] = []
                for recette in session.query(Recette).filter(Recette.id.in_(recette_ids)).all():
                    has_etapes = (
                        session.query(EtapeRecette)
                        .filter(EtapeRecette.recette_id == recette.id)
                        .first()
                    ) is not None
                    if not has_etapes:
                        stubs_data.append((recette.id, recette.nom))

            if not stubs_data:
                logger.debug("[planning] Aucune recette stub à enrichir pour planning %d", planning_id)
                return

            self._enrichir_stubs_data(stubs_data, context=f"planning {planning_id}")

        except Exception as exc:
            logger.warning(
                "[planning] Enrichissement stubs ignoré pour planning %d: %s",
                planning_id,
                exc,
                exc_info=True,
            )

    # ═══════════════════════════════════════════════════════════
    # HELPERS SHARED: appel IA + sauvegarde + enrichissement global
    # ═══════════════════════════════════════════════════════════

    def _enrichir_stubs_data(self, stubs_data: list[tuple[int, str]], context: str = "") -> int:
        """Appel IA + sauvegarde étapes/ingrédients pour une liste de stubs ``(id, nom)``.

        Args:
            stubs_data: Tuples ``(id, nom)`` des recettes à enrichir.
            context:    Libellé pour les logs (ex: ``"planning 42"``, ``"global"``).

        Returns:
            Nombre de recettes effectivement enrichies.
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models import EtapeRecette, Ingredient, RecetteIngredient
        from src.core.models.recettes import Recette

        noms = [nom for _, nom in stubs_data]
        logger.info("[planning] Enrichissement IA de %d recette(s) [%s]: %s", len(noms), context, noms)

        # ── Batcher par 5 pour rester sous la limite de tokens Mistral ──────────
        BATCH_SIZE = 5
        total_count = 0
        for batch_start in range(0, len(stubs_data), BATCH_SIZE):
            batch = stubs_data[batch_start : batch_start + BATCH_SIZE]
            total_count += self._enrichir_batch(batch, context=context)

        return total_count

    def _enrichir_batch(self, stubs_data: list[tuple[int, str]], context: str = "") -> int:
        """Enrichit un batch de ≤5 recettes via un seul appel Mistral."""
        from src.core.db import obtenir_contexte_db
        from src.core.models import EtapeRecette, Ingredient, RecetteIngredient
        from src.core.models.recettes import Recette

        noms = [nom for _, nom in stubs_data]
        liste_noms = "\n".join(f"{i + 1}. {nom}" for i, nom in enumerate(noms))
        prompt = f"""For each recipe listed below, generate practical cooking steps and main ingredients.

OUTPUT ONLY THIS JSON (no other text, no markdown, no code blocks):
{{"items": [
  {{
    "nom": "Pâtes carbonara",
    "temps_preparation": 10,
    "temps_cuisson": 15,
    "portions": 4,
    "difficulte": "facile",
    "ingredients": [{{"nom": "spaghetti", "quantite": 400, "unite": "g"}}, {{"nom": "lardons", "quantite": 200, "unite": "g"}}, {{"nom": "oeufs", "quantite": 3, "unite": "pièce"}}],
    "etapes": ["Faire bouillir l'eau salée et cuire les spaghetti al dente.", "Faire revenir les lardons à sec dans une poêle.", "Mélanger les oeufs battus avec le parmesan.", "Égoutter les pâtes, hors du feu mélanger avec les lardons puis la sauce oeufs-parmesan."]
  }}
]}}

RULES:
1. Return ONLY valid JSON — no text before or after
2. One item per recipe, in the SAME ORDER as the input list
3. etapes: array of French strings, 3-8 steps each, describing the actual cooking process
4. ingredients: array of {{nom, quantite, unite}}, 3-12 items
5. Keep nom identical to the input recipe name
6. No explanations, ONLY JSON

Recipes to enrich:
{liste_noms}"""

        enriched = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=RecetteEnrichieIA,
            system_prompt="Return ONLY valid JSON. No text before or after JSON.",
            max_items=len(noms),
            use_cache=False,
            temperature=0.3,
            max_tokens=2500,
        )

        if not enriched:
            logger.warning("[planning] Aucune donnée IA reçue pour l'enrichissement [%s]", context)
            return 0

        stubs_by_nom = {nom.lower(): rid for rid, nom in stubs_data}
        with obtenir_contexte_db() as session:
            count = 0
            for recette_ia in enriched:
                stub_id = stubs_by_nom.get(recette_ia.nom.lower())
                if stub_id is None:
                    for nom_key, rid in stubs_by_nom.items():
                        if recette_ia.nom.lower() in nom_key or nom_key in recette_ia.nom.lower():
                            stub_id = rid
                            break
                if stub_id is None:
                    continue

                db_recette = session.get(Recette, stub_id)
                if db_recette is None:
                    continue

                if recette_ia.temps_preparation:
                    db_recette.temps_preparation = recette_ia.temps_preparation
                if recette_ia.temps_cuisson:
                    db_recette.temps_cuisson = recette_ia.temps_cuisson
                if recette_ia.portions:
                    db_recette.portions = recette_ia.portions
                if recette_ia.difficulte:
                    db_recette.difficulte = recette_ia.difficulte

                for idx, texte in enumerate(recette_ia.etapes, start=1):
                    texte = texte.strip()
                    if texte:
                        session.add(
                            EtapeRecette(
                                recette_id=stub_id,
                                ordre=idx,
                                description=texte,
                            )
                        )

                for ing_data in recette_ia.ingredients:
                    nom_ing = (ing_data.get("nom") or "").strip()
                    if not nom_ing:
                        continue
                    db_ingredient = (
                        session.query(Ingredient).filter(Ingredient.nom == nom_ing).first()
                    )
                    if db_ingredient is None:
                        db_ingredient = Ingredient(
                            nom=nom_ing,
                            unite=ing_data.get("unite") or "pièce",
                        )
                        session.add(db_ingredient)
                        session.flush()
                    session.add(
                        RecetteIngredient(
                            recette_id=stub_id,
                            ingredient_id=db_ingredient.id,
                            quantite=float(ing_data.get("quantite") or 1),
                            unite=ing_data.get("unite") or db_ingredient.unite,
                        )
                    )

                count += 1

            session.commit()
            logger.info("[planning] ✅ %d recette(s) enrichie(s) [%s]", count, context)
            return count

    def enrichir_recettes_stubs_global(self, recette_ids: list[int] | None = None) -> int:
        """Enrichit via l'IA toutes les recettes sans étapes (ou celles de ``recette_ids``).

        Peut être appelé depuis une route admin pour réparer des stubs existants
        sans avoir à régénérer un planning.

        Args:
            recette_ids: IDs à traiter. Si ``None``, toutes les recettes sans étape.

        Returns:
            Nombre de recettes enrichies.
        """
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models import EtapeRecette
            from src.core.models.recettes import Recette

            with obtenir_contexte_db() as session:
                query = session.query(Recette)
                if recette_ids:
                    query = query.filter(Recette.id.in_(recette_ids))
                stubs_data: list[tuple[int, str]] = []
                for recette in query.all():
                    has_etapes = (
                        session.query(EtapeRecette)
                        .filter(EtapeRecette.recette_id == recette.id)
                        .first()
                    ) is not None
                    if not has_etapes:
                        stubs_data.append((recette.id, recette.nom))

            if not stubs_data:
                logger.info("[planning] Aucune recette stub à enrichir (global)")
                return 0

            return self._enrichir_stubs_data(
                stubs_data, context=f"global ({len(stubs_data)} recettes)"
            )

        except Exception as exc:
            logger.warning("[planning] Enrichissement stubs global échoué: %s", exc, exc_info=True)
            return 0
