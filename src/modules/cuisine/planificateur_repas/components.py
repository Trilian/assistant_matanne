"""
Module Planificateur de Repas - Composants UI
"""

from datetime import date

import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.ui.keys import KeyNamespace

from .helpers import DESSERTS_FAMILLE, DESSERTS_JULES, ENTREES_SUGGESTIONS
from .preferences import (
    ajouter_feedback,
    charger_feedbacks,
    charger_preferences,
    sauvegarder_preferences,
)
from .utils import PROTEINES, ROBOTS_CUISINE, TEMPS_CATEGORIES, PreferencesUtilisateur

_keys = KeyNamespace("planificateur_ui")


def afficher_configuration_preferences():
    """Affiche le formulaire de configuration des préférences."""

    prefs = charger_preferences()

    st.subheader("⚙️ Mes Préférences Alimentaires")

    with st.form(_keys("form_preferences")):
        # Famille
        st.markdown("##### 👨‍👩‍👦 Ma famille")
        nb_adultes = st.number_input("Adultes", 1, 6, prefs.nb_adultes, key=_keys("nb_adultes"))
        colj1, colj2 = st.columns(2)
        with colj1:
            jules_present = st.checkbox(
                "Jules mange avec nous", value=prefs.jules_present, key=_keys("jules_present")
            )
        with colj2:
            jules_age = st.number_input(
                "Âge Jules (mois)", 6, 36, prefs.jules_age_mois, key=_keys("jules_age")
            )

        st.markdown("##### ⏱️ Temps de cuisine")
        col1, col2 = st.columns(2)

        with col1:
            temps_semaine = st.selectbox(
                "En semaine",
                options=list(TEMPS_CATEGORIES.keys()),
                format_func=lambda x: TEMPS_CATEGORIES[x]["label"],
                index=list(TEMPS_CATEGORIES.keys()).index(prefs.temps_semaine),
                key=_keys("temps_semaine"),
            )
        with col2:
            temps_weekend = st.selectbox(
                "Le weekend",
                options=list(TEMPS_CATEGORIES.keys()),
                format_func=lambda x: TEMPS_CATEGORIES[x]["label"],
                index=list(TEMPS_CATEGORIES.keys()).index(prefs.temps_weekend),
                key=_keys("temps_weekend"),
            )

        st.markdown("##### 🚫 Aliments à éviter")
        exclus = st.text_input(
            "Séparés par des virgules",
            value=", ".join(prefs.aliments_exclus),
            placeholder="Ex: fruits de mer, abats, coriandre",
            key=_keys("aliments_exclus"),
        )

        st.markdown("##### ❤️ Vos basiques adorés")
        favoris = st.text_input(
            "Séparés par des virgules",
            value=", ".join(prefs.aliments_favoris),
            placeholder="Ex: pâtes, poulet, gratins",
            key=_keys("aliments_favoris"),
        )

        st.markdown("##### ⚖️ Équilibre souhaité par semaine")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            poisson_blanc = st.number_input(
                "🐟 Poisson blanc",
                0,
                7,
                prefs.poisson_blanc_par_semaine,
                key=_keys("poisson_blanc_par_semaine"),
                help="Cabillaud, merlu, colin, sole...",
            )
        with col2:
            poisson_gras = st.number_input(
                "🐠 Poisson gras",
                0,
                7,
                prefs.poisson_gras_par_semaine,
                key=_keys("poisson_gras_par_semaine"),
                help="Saumon, sardine, thon, maquereau...",
            )
        with col3:
            vege = st.number_input(
                "🥬 Végétarien max",
                0,
                7,
                prefs.vegetarien_par_semaine,
                key=_keys("vegetarien_par_semaine"),
            )
        with col4:
            viande_rouge = st.number_input(
                "🥩 Viande rouge max", 0, 7, prefs.viande_rouge_max, key=_keys("viande_rouge_max")
            )

        st.markdown("##### 🤖 Mes robots cuisine")
        robots_selected = []
        cols = st.columns(3)
        for i, (robot_id, robot_info) in enumerate(ROBOTS_CUISINE.items()):
            with cols[i % 3]:
                if st.checkbox(
                    f"{robot_info['emoji']} {robot_info['label']}",
                    value=robot_id in prefs.robots,
                    key=_keys("robot_pref", robot_id),
                ):
                    robots_selected.append(robot_id)

        # Soumettre
        if st.form_submit_button("💾 Sauvegarder", type="primary"):
            new_prefs = PreferencesUtilisateur(
                nb_adultes=nb_adultes,
                jules_present=jules_present,
                jules_age_mois=jules_age,
                temps_semaine=temps_semaine,
                temps_weekend=temps_weekend,
                aliments_exclus=[x.strip() for x in exclus.split(",") if x.strip()],
                aliments_favoris=[x.strip() for x in favoris.split(",") if x.strip()],
                poisson_blanc_par_semaine=poisson_blanc,
                poisson_gras_par_semaine=poisson_gras,
                vegetarien_par_semaine=vege,
                viande_rouge_max=viande_rouge,
                robots=robots_selected,
                magasins_preferes=prefs.magasins_preferes,
            )
            sauvegarder_preferences(new_prefs)
            st.success("✅ Préférences sauvegardées!")
            rerun()


def afficher_apprentissage_ia():
    """Affiche ce que l'IA a appris des goûts."""

    feedbacks = charger_feedbacks()

    if not feedbacks:
        st.info("🧠 L'IA n'a pas encore appris vos goûts. Notez les recettes avec 👍/👎 !")
        return

    st.markdown("##### 🧠 L'IA a appris que vous...")

    likes = [f.recette_nom for f in feedbacks if f.feedback == "like"]
    dislikes = [f.recette_nom for f in feedbacks if f.feedback == "dislike"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**👍 Aimez:**")
        if likes:
            for nom in likes[-5:]:
                st.caption(f"• {nom}")
        else:
            st.caption("Pas encore de données")

    with col2:
        st.markdown("**👎 N'aimez pas:**")
        if dislikes:
            for nom in dislikes[-5:]:
                st.caption(f"• {nom}")
        else:
            st.caption("Pas encore de données")


def afficher_carte_recette_suggestion(
    suggestion: dict,
    jour: str,
    type_repas: str,
    key_prefix: str,
):
    """Affiche une carte de recette avec entrée/plat/dessert et actions."""

    with st.container(border=True):
        # ── Badge réchauffé ──
        if suggestion.get("est_rechauffe"):
            rechauffe_source = suggestion.get("rechauffe_de", "")
            st.caption(f"🔄 **Réchauffé** du {rechauffe_source} — *juste à réchauffer !*")
            return  # Pas d'actions pour les réchauffés

        # ── Entrée (si présente) ──
        entree = suggestion.get("entree")
        if entree:
            st.caption(f"🥗 {entree}")

        # ── Plat principal ──
        complexite = suggestion.get("complexite", "")
        badge = " ⚡" if complexite == "simple" else (" 👨‍🍳" if complexite == "elabore" else "")
        st.markdown(f"**🍽️ {suggestion.get('nom', 'Recette')}**{badge}")

        # Tags inline
        tags = []
        if suggestion.get("temps_minutes"):
            tags.append(f"⏱ {suggestion['temps_minutes']}m")
        if suggestion.get("proteine"):
            prot_info = PROTEINES.get(suggestion["proteine"], {})
            tags.append(
                f"{prot_info.get('emoji', '')} {prot_info.get('label', suggestion['proteine'])}"
            )
        if suggestion.get("robot"):
            robot_info = ROBOTS_CUISINE.get(suggestion["robot"], {})
            tags.append(f"{robot_info.get('emoji', '')} {robot_info.get('label', '')}")
        if tags:
            st.caption(" · ".join(tags))

        # ── Desserts ──
        dessert = suggestion.get("dessert")
        dessert_jules = suggestion.get("dessert_jules")
        if dessert or dessert_jules:
            parts = []
            if dessert:
                parts.append(f"🍰 {dessert}")
            if dessert_jules:
                parts.append(f"👶 {dessert_jules}")
            st.caption(" · ".join(parts))

        # ── Actions : ligne compacte de 5 boutons ──
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button("👍", key=f"{key_prefix}_like", help="J'aime", use_container_width=True):
                ajouter_feedback(recette_nom=suggestion.get("nom", ""), feedback="like")
                st.toast("👍 Noté !")

        with col2:
            if st.button(
                "👎", key=f"{key_prefix}_dislike", help="Pas aimé", use_container_width=True
            ):
                ajouter_feedback(recette_nom=suggestion.get("nom", ""), feedback="dislike")
                st.toast("👎 Noté !")

        with col3:
            if st.button(
                "🔄", key=f"{key_prefix}_change", help="Autre suggestion", use_container_width=True
            ):
                from .generation import generer_alternative_ia

                with st.spinner("🤖"):
                    alt = generer_alternative_ia(suggestion, jour, type_repas)
                if alt:
                    planning = st.session_state.get(SK.PLANNING_DATA, {})
                    if jour in planning:
                        old = planning[jour].get(type_repas, {})
                        if old and isinstance(old, dict):
                            for k in ("entree", "dessert", "dessert_jules"):
                                if k not in alt and old.get(k):
                                    alt[k] = old[k]
                        planning[jour][type_repas] = alt
                        st.session_state[SK.PLANNING_DATA] = planning
                        st.toast(f"✅ {alt.get('nom', 'nouvelle recette')}")
                    rerun()
                else:
                    st.warning("⚠️ Aucune alternative")

        with col4:
            if st.button(
                "📝", key=f"{key_prefix}_manual", help="Modifier", use_container_width=True
            ):
                st.session_state[f"_manual_edit_{key_prefix}"] = True
                rerun()

        with col5:
            nom_recette = suggestion.get("nom", "")
            sauvegardees: set = st.session_state.get(SK.RECETTES_IA_SAUVEGARDEES, set())

            # Vérifier aussi la DB (pas juste la session)
            if nom_recette and nom_recette not in sauvegardees:
                try:
                    from src.services.cuisine.recettes import obtenir_service_recettes

                    _svc = obtenir_service_recettes()
                    if _svc and _svc.find_existing_recette(nom_recette):
                        sauvegardees.add(nom_recette)
                        st.session_state[SK.RECETTES_IA_SAUVEGARDEES] = sauvegardees
                except Exception:
                    pass

            if nom_recette in sauvegardees:
                st.button(
                    "✅",
                    key=f"{key_prefix}_saved",
                    disabled=True,
                    use_container_width=True,
                    help="Sauvegardée",
                )
            else:
                if st.button(
                    "💾", key=f"{key_prefix}_save", help="Sauvegarder", use_container_width=True
                ):
                    from .generation import sauvegarder_recette_ia

                    with st.spinner("💾"):
                        recette_id = sauvegarder_recette_ia(suggestion, type_repas)
                    if recette_id:
                        sauvegardees.add(nom_recette)
                        st.session_state[SK.RECETTES_IA_SAUVEGARDEES] = sauvegardees
                        st.toast(f"✅ '{nom_recette}' sauvegardée !")
                        rerun()
                    else:
                        st.toast("❌ Échec", icon="❌")

        # ── Jules ──
        if suggestion.get("jules_adaptation"):
            with st.expander("👶 Jules", expanded=False):
                st.markdown(suggestion["jules_adaptation"])

        # ── Détails recette ──
        with st.expander("📋 Détails", expanded=False):
            details = []
            if suggestion.get("difficulte"):
                details.append(f"**Difficulté:** {suggestion['difficulte']}")
            if suggestion.get("temps_minutes"):
                details.append(f"**Temps:** {suggestion['temps_minutes']} min")
            if suggestion.get("proteine"):
                details.append(f"**Protéine:** {suggestion['proteine']}")
            if suggestion.get("robot"):
                details.append(f"**Robot:** {suggestion['robot']}")
            if details:
                st.markdown(" · ".join(details))

            # Ingrédients et étapes depuis la DB (si la recette est sauvegardée)
            recette_id = suggestion.get("id")
            _found = False

            # 1. Par ID direct
            if recette_id:
                _afficher_details_recette_inline(recette_id)
                _found = True

            # 2. Recherche par nom en DB (matching normalisé)
            if not _found:
                nom_recette = suggestion.get("nom", "")
                if nom_recette:
                    try:
                        from src.services.cuisine.recettes import obtenir_service_recettes

                        svc = obtenir_service_recettes()
                        if svc:
                            existing = svc.find_existing_recette(nom_recette)
                            if existing:
                                _afficher_details_recette_inline(existing.id)
                                # Mettre à jour l'ID dans la suggestion pour les prochains affichages
                                suggestion["id"] = existing.id
                                _found = True
                    except Exception:
                        pass

            # 3. Afficher les données IA disponibles dans la suggestion
            if not _found:
                ingredients = suggestion.get("ingredients", [])
                etapes = suggestion.get("etapes", [])
                if ingredients:
                    st.markdown("**🥕 Ingrédients:**")
                    for ing in ingredients:
                        if isinstance(ing, dict):
                            nom_ing = ing.get("nom", "")
                            q = ing.get("quantite", "")
                            u = ing.get("unite", "")
                            if q and float(q) > 0.01:
                                st.caption(f"• {nom_ing} — {q} {u}")
                            else:
                                st.caption(f"• {nom_ing}")
                        else:
                            st.caption(f"• {ing}")
                if etapes:
                    st.markdown("**👨‍🍳 Préparation:**")
                    for idx_e, etape in enumerate(etapes, 1):
                        if isinstance(etape, dict):
                            st.caption(f"{idx_e}. {etape.get('description', '')}")
                        else:
                            st.caption(f"{idx_e}. {etape}")
                if not ingredients and not etapes:
                    st.caption("💡 Sauvegardez le planning pour générer les détails complets")

        # ── Formulaire changement manuel ──
        if st.session_state.get(f"_manual_edit_{key_prefix}"):
            _afficher_edition_manuelle(suggestion, jour, type_repas, key_prefix)


def _est_recette_fallback(recette) -> bool:
    """Détecte si une recette a des données minimales/fallback (1 ingrédient générique, 1 étape générique)."""
    ingredients = getattr(recette, "ingredients", [])
    etapes = getattr(recette, "etapes", [])

    if len(ingredients) <= 1 and len(etapes) <= 1:
        return True

    # Vérifier si l'unique étape est un fallback "Préparer X selon la recette"
    if len(etapes) == 1:
        desc = getattr(etapes[0], "description", "")
        if "selon la recette" in desc.lower():
            return True

    return False


def _regenerer_details_recette(recette_id: int) -> bool:
    """Régénère les détails (description, ingrédients, étapes, temps) d'une recette existante via l'IA."""
    import logging
    import re

    _logger = logging.getLogger(__name__)

    try:
        from src.core.ai import obtenir_client_ia
        from src.core.db.session import obtenir_contexte_db
        from src.core.models.recettes import EtapeRecette, RecetteIngredient
        from src.services.cuisine.recettes import obtenir_service_recettes

        service = obtenir_service_recettes()
        if not service:
            return False

        recette = service.get_by_id_full(recette_id)
        if not recette:
            return False

        client = obtenir_client_ia()
        if not client:
            return False

        # Contexte robot
        robot_context = ""
        robots = recette.robots_compatibles
        if robots:
            robot_context = f"\nCette recette peut être préparée avec : {', '.join(robots)}. Adapte les étapes si pertinent."

        prompt = f"""Génère les détails complets pour la recette : "{recette.nom}".
Contexte : famille de 2 adultes + 1 bébé de 19 mois.
Protéine principale : {recette.type_proteines or "non spécifiée"}.{robot_context}

Réponds UNIQUEMENT en JSON valide :
{{
  "description": "Description appétissante de la recette en 1-2 phrases",
  "temps_preparation": <temps de préparation en minutes (entier)>,
  "temps_cuisson": <temps de cuisson en minutes (entier)>,
  "portions": <nombre de portions (entier, typiquement 4)>,
  "ingredients": [
    {{"nom": "nom ingrédient", "quantite": 200, "unite": "g"}},
    {{"nom": "autre ingrédient", "quantite": 1, "unite": "pièce"}}
  ],
  "etapes": [
    "Description détaillée de l'étape 1...",
    "Description détaillée de l'étape 2...",
    "Description détaillée de l'étape 3..."
  ]
}}
IMPORTANT:
- La description doit être appétissante et décrire le plat, PAS mentionner l'IA.
- Liste TOUS les ingrédients nécessaires (minimum 4-5), avec des quantités réalistes.
- Détaille TOUTES les étapes de préparation (minimum 3-4 étapes).
- Les temps doivent être réalistes. Les quantités en grammes, cl, pièces, etc."""

        details = client.generer_json(
            prompt,
            system_prompt="Tu es un chef cuisinier expert en cuisine familiale.",
            max_tokens=2000,
        )

        if not details or not isinstance(details, dict):
            return False

        # Mise à jour des champs de la recette
        update_data = {}

        desc_ia = details.get("description", "")
        if desc_ia and "ia" not in desc_ia.lower() and "planificateur" not in desc_ia.lower():
            update_data["description"] = desc_ia

        temps_prep = details.get("temps_preparation")
        if isinstance(temps_prep, int | float) and temps_prep > 0:
            update_data["temps_preparation"] = int(temps_prep)

        temps_cuisson = details.get("temps_cuisson")
        if isinstance(temps_cuisson, int | float) and temps_cuisson > 0:
            update_data["temps_cuisson"] = int(temps_cuisson)

        portions = details.get("portions")
        if isinstance(portions, int | float) and portions > 0:
            update_data["portions"] = int(min(portions, 20))

        if update_data:
            service.update(recette_id, update_data)

        # Remplacer ingrédients et étapes en DB
        ingredients_raw = details.get("ingredients", [])
        etapes_raw = details.get("etapes", [])

        if ingredients_raw and len(ingredients_raw) > 1:
            with obtenir_contexte_db() as db:
                # Supprimer les anciens ingrédients
                db.query(RecetteIngredient).filter(
                    RecetteIngredient.recette_id == recette_id
                ).delete()

                # Créer les nouveaux
                for ing in ingredients_raw:
                    q = ing.get("quantite", 0)
                    unite = ing.get("unite", "pièce")
                    try:
                        if isinstance(q, str):
                            match = re.search(r"(\d+([.,]\d+)?)", q.replace(",", "."))
                            q = float(match.group(1)) if match else 0.01
                        else:
                            q = float(q)
                    except (ValueError, TypeError):
                        q = 0.01
                    if q <= 0:
                        q = 0.01

                    ingredient = service._find_or_create_ingredient(db, ing.get("nom", "inconnu"))
                    ri = RecetteIngredient(
                        recette_id=recette_id,
                        ingredient_id=ingredient.id,
                        quantite=q,
                        unite=unite or "pièce",
                    )
                    db.add(ri)

                db.commit()

        if etapes_raw and len(etapes_raw) > 1:
            with obtenir_contexte_db() as db:
                # Supprimer les anciennes étapes
                db.query(EtapeRecette).filter(EtapeRecette.recette_id == recette_id).delete()

                # Créer les nouvelles
                for idx, etape in enumerate(etapes_raw):
                    desc = etape if isinstance(etape, str) else etape.get("description", "")
                    e = EtapeRecette(
                        recette_id=recette_id,
                        ordre=idx + 1,
                        description=desc,
                    )
                    db.add(e)

                db.commit()

        _logger.info(f"✅ Détails régénérés pour recette {recette_id}: {recette.nom}")
        return True

    except Exception as e:
        _logger.error(f"Erreur régénération détails recette {recette_id}: {e}")
        return False


def _afficher_details_recette_inline(recette_id: int):
    """Affiche les ingrédients et étapes d'une recette sauvegardée en DB (sans expander)."""
    try:
        from src.services.cuisine.recettes import obtenir_service_recettes

        service = obtenir_service_recettes()
        recette = service.get_by_id_full(recette_id) if service else None

        if recette:
            # Ingrédients
            ingredients = getattr(recette, "ingredients", [])
            if ingredients:
                st.markdown("**🥕 Ingrédients:**")
                for ri in ingredients:
                    ingredient = getattr(ri, "ingredient", None)
                    nom_str = getattr(ingredient, "nom", "") if ingredient else ""
                    quantite = getattr(ri, "quantite", 0)
                    unite = getattr(ri, "unite", "")
                    if quantite and quantite > 0.01:
                        st.caption(f"• {nom_str} — {quantite:g} {unite}")
                    else:
                        st.caption(f"• {nom_str}")

            # Étapes
            etapes = getattr(recette, "etapes", [])
            if etapes:
                st.markdown("**👨‍🍳 Préparation:**")
                etapes_triees = sorted(etapes, key=lambda e: getattr(e, "ordre", 0))
                for etape in etapes_triees:
                    ordre = getattr(etape, "ordre", "")
                    desc = getattr(etape, "description", "")
                    st.caption(f"{ordre}. {desc}")

            # Bouton régénérer si données fallback
            if _est_recette_fallback(recette):
                st.warning("Cette recette a des données incomplètes.")
                if st.button(
                    "🔄 Régénérer les détails avec l'IA",
                    key=f"regen_{recette_id}",
                ):
                    with st.spinner("🤖 Régénération en cours..."):
                        if _regenerer_details_recette(recette_id):
                            st.success("✅ Détails régénérés !")
                            rerun()
                        else:
                            st.error("❌ Échec de la régénération")
        else:
            st.caption("Détails non disponibles")
    except Exception:
        st.caption("Détails non disponibles")


def _afficher_details_recette_db(recette_id: int, key_prefix: str):
    """Affiche les ingrédients et étapes d'une recette sauvegardée en DB."""
    with st.expander("📋 Ingrédients & Préparation", expanded=False):
        try:
            from src.services.cuisine.recettes import obtenir_service_recettes

            service = obtenir_service_recettes()
            recette = service.get_by_id_full(recette_id) if service else None

            if recette:
                # Ingrédients
                ingredients = getattr(recette, "ingredients", [])
                if ingredients:
                    st.markdown("**🥕 Ingrédients:**")
                    for ri in ingredients:
                        ingredient = getattr(ri, "ingredient", None)
                        nom_str = getattr(ingredient, "nom", "") if ingredient else ""
                        quantite = getattr(ri, "quantite", 0)
                        unite = getattr(ri, "unite", "")
                        if quantite and quantite > 0.01:
                            st.caption(f"• {nom_str} — {quantite:g} {unite}")
                        else:
                            st.caption(f"• {nom_str}")

                # Étapes
                etapes = getattr(recette, "etapes", [])
                if etapes:
                    st.markdown("**👨‍🍳 Préparation:**")
                    etapes_triees = sorted(etapes, key=lambda e: getattr(e, "ordre", 0))
                    for etape in etapes_triees:
                        ordre = getattr(etape, "ordre", "")
                        desc = getattr(etape, "description", "")
                        st.caption(f"{ordre}. {desc}")
            else:
                st.caption("Détails non disponibles")
        except Exception:
            st.caption("Détails non disponibles")


def _afficher_edition_manuelle(suggestion: dict, jour: str, type_repas: str, key_prefix: str):
    """Formulaire d'édition manuelle d'un repas (sélection recette ou texte libre)."""

    with st.container(border=True):
        st.markdown("##### 📝 Changer le repas")

        # Charger les recettes existantes
        try:
            from src.services.cuisine.recettes import obtenir_service_recettes

            service = obtenir_service_recettes()
            recettes_db = service.get_all() if service else []
            noms_recettes = ["(Texte libre)"] + [r.nom for r in recettes_db if hasattr(r, "nom")]
        except Exception:
            recettes_db = []
            noms_recettes = ["(Texte libre)"]

        choix = st.selectbox(
            "Choisir une recette",
            noms_recettes,
            key=f"{key_prefix}_manual_select",
        )

        if choix == "(Texte libre)":
            nom_libre = st.text_input(
                "Nom du plat",
                value=suggestion.get("nom", ""),
                key=f"{key_prefix}_manual_text",
            )
        else:
            nom_libre = choix

        # Édition entrée/dessert
        col_e, col_d, col_dj = st.columns(3)
        with col_e:
            entree_edit = st.selectbox(
                "🥗 Entrée",
                ["(Aucune)", "(Texte libre)"] + ENTREES_SUGGESTIONS,
                key=f"{key_prefix}_entree_edit",
            )
            if entree_edit == "(Texte libre)":
                entree_edit = st.text_input("Entrée", key=f"{key_prefix}_entree_txt")
            elif entree_edit == "(Aucune)":
                entree_edit = None

        with col_d:
            dessert_edit = st.selectbox(
                "🍰 Dessert",
                ["(Aucun)", "(Texte libre)"] + DESSERTS_FAMILLE,
                key=f"{key_prefix}_dessert_edit",
            )
            if dessert_edit == "(Texte libre)":
                dessert_edit = st.text_input("Dessert", key=f"{key_prefix}_dessert_txt")
            elif dessert_edit == "(Aucun)":
                dessert_edit = None

        with col_dj:
            dessert_j_edit = st.selectbox(
                "👶 Dessert Jules",
                ["(Aucun)", "(Texte libre)"] + DESSERTS_JULES,
                key=f"{key_prefix}_dessertj_edit",
            )
            if dessert_j_edit == "(Texte libre)":
                dessert_j_edit = st.text_input("Dessert Jules", key=f"{key_prefix}_dessertj_txt")
            elif dessert_j_edit == "(Aucun)":
                dessert_j_edit = None

        col_ok, col_cancel = st.columns(2)
        with col_ok:
            if st.button("✅ Appliquer", key=f"{key_prefix}_manual_ok", use_container_width=True):
                planning = st.session_state.get(SK.PLANNING_DATA, {})
                if jour in planning:
                    if choix == "(Texte libre)":
                        new_meal = {
                            "nom": nom_libre,
                            "plaisir": True,
                            "entree": entree_edit,
                            "dessert": dessert_edit,
                            "dessert_jules": dessert_j_edit,
                        }
                    else:
                        # Recette existante: récupérer les infos
                        recette_obj = next(
                            (r for r in recettes_db if hasattr(r, "nom") and r.nom == choix), None
                        )
                        new_meal = {
                            "nom": choix,
                            "id": recette_obj.id if recette_obj else None,
                            "proteine": getattr(recette_obj, "type_proteines", None),
                            "temps_minutes": getattr(recette_obj, "temps_preparation", 30),
                            "entree": entree_edit,
                            "dessert": dessert_edit,
                            "dessert_jules": dessert_j_edit,
                        }
                    planning[jour][type_repas] = new_meal
                    st.session_state[SK.PLANNING_DATA] = planning

                del st.session_state[f"_manual_edit_{key_prefix}"]
                st.toast(f"✅ Repas changé: {nom_libre}")
                rerun()

        with col_cancel:
            if st.button("❌ Annuler", key=f"{key_prefix}_manual_cancel", use_container_width=True):
                del st.session_state[f"_manual_edit_{key_prefix}"]
                rerun()


def afficher_jour_planning(
    jour: str,
    jour_date: date,
    repas_jour: dict,
    key_prefix: str,
):
    """Affiche un jour du planning avec ses repas."""

    with st.expander(f"📅 **{jour}** {jour_date.strftime('%d/%m')}", expanded=True):
        # Midi
        st.markdown("##### 🌞 Midi")
        midi = repas_jour.get("midi")
        if midi:
            afficher_carte_recette_suggestion(midi, jour, "midi", f"{key_prefix}_midi")
        else:
            st.info("Aucun")
            if st.button("➕ Ajouter midi", key=f"{key_prefix}_add_midi"):
                st.session_state[_keys("add_midi", key_prefix)] = True

        st.divider()

        # Soir
        st.markdown("##### 🌙 Soir")
        soir = repas_jour.get("soir")
        if soir:
            afficher_carte_recette_suggestion(soir, jour, "soir", f"{key_prefix}_soir")
        else:
            st.info("Aucun")
            if st.button("➕ Ajouter soir", key=f"{key_prefix}_add_soir"):
                st.session_state[_keys("add_soir", key_prefix)] = True

        # Goûter (optionnel)
        gouter = repas_jour.get("gouter")
        if gouter:
            st.divider()
            st.markdown("##### 🍰 Goûter")
            afficher_carte_recette_suggestion(gouter, jour, "gouter", f"{key_prefix}_gouter")


def afficher_resume_equilibre(planning_data: dict):
    """Affiche le résumé de l'équilibre nutritionnel."""

    # Compter les types de protéines (blanc/gras séparés)
    equilibre = {
        "poisson_blanc": 0,
        "poisson_gras": 0,
        "viande_rouge": 0,
        "volaille": 0,
        "vegetarien": 0,
    }

    # Mapping des catégories PROTEINES → clés equilibre
    _CAT_MAPPING = {
        "poisson_blanc": "poisson_blanc",
        "poisson_gras": "poisson_gras",
        "poisson": "poisson_blanc",  # fallback générique
        "fruits_mer": "poisson_blanc",
        "viande_rouge": "viande_rouge",
        "viande": "viande_rouge",  # porc, etc.
        "volaille": "volaille",
        "vegetarien": "vegetarien",
        "vegan": "vegetarien",
    }

    for jour, repas in planning_data.items():
        for type_repas in ["midi", "soir"]:
            if repas.get(type_repas) and repas[type_repas].get("proteine"):
                prot = repas[type_repas]["proteine"]
                if prot in PROTEINES:
                    cat = PROTEINES[prot]["categorie"]
                    eq_key = _CAT_MAPPING.get(cat)
                    if eq_key:
                        equilibre[eq_key] += 1

    prefs = charger_preferences()

    # Calcul des repas planifiés
    total_slots = 0
    planned = 0
    for jour, repas in planning_data.items():
        for tr in ["midi", "soir"]:
            total_slots += 1
            if repas.get(tr):
                planned += 1

    st.markdown("##### 📊 Équilibre de la semaine")

    # Afficher résumé des repas planifiés
    col_top1, col_top2 = st.columns([1, 3])
    with col_top1:
        valeur_metric = "Aucun" if planned == 0 else f"{planned}/{total_slots}"
        st.metric("🍽️ Repas planifiés", valeur_metric)
    with col_top2:
        if planned == 0:
            st.info("Aucun repas planifié — Cliquez sur 'Générer une semaine' pour commencer !")
        elif planned < total_slots:
            st.info(
                f"{total_slots - planned} repas manquants — Le planificateur IA peut compléter !"
            )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        delta = equilibre["poisson_blanc"] - prefs.poisson_blanc_par_semaine
        st.metric("🐟 P. blanc", equilibre["poisson_blanc"], delta=f"{delta:+d}" if delta else None)

    with col2:
        delta = equilibre["poisson_gras"] - prefs.poisson_gras_par_semaine
        st.metric("🐠 P. gras", equilibre["poisson_gras"], delta=f"{delta:+d}" if delta else None)

    with col3:
        delta = equilibre["vegetarien"] - prefs.vegetarien_par_semaine
        st.metric("🥬 Végé", equilibre["vegetarien"], delta=f"{delta:+d}" if delta else None)

    with col4:
        st.metric("🐔 Volaille", equilibre["volaille"])

    with col5:
        delta = equilibre["viande_rouge"] - prefs.viande_rouge_max
        color = "inverse" if delta > 0 else "normal"
        st.metric(
            "🥩 Rouge",
            equilibre["viande_rouge"],
            delta=f"{delta:+d}" if delta else None,
            delta_color=color,
        )

    # Compteurs simple/élaboré et réchauffé
    nb_simple = 0
    nb_elabore = 0
    nb_rechauffe = 0
    nb_a_cuisiner = 0

    for jour, repas in planning_data.items():
        for tr in ["midi", "soir"]:
            meal = repas.get(tr)
            if meal and isinstance(meal, dict):
                if meal.get("est_rechauffe"):
                    nb_rechauffe += 1
                else:
                    nb_a_cuisiner += 1
                if meal.get("complexite") == "elabore":
                    nb_elabore += 1
                elif meal.get("complexite") == "simple":
                    nb_simple += 1

    if nb_rechauffe > 0 or nb_simple > 0:
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("⚡ Simples", nb_simple)
        with col_r2:
            st.metric("👨‍🍳 Élaborés", nb_elabore)
        with col_r3:
            st.metric(
                "🔄 Réchauffés",
                nb_rechauffe,
                delta=f"{nb_a_cuisiner} à cuisiner",
                delta_color="off",
            )
