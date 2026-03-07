"""
Module Planificateur de Repas Intelligent - UI Streamlit

Interface style Jow:
- Générateur IA de menus équilibrés
- Apprentissage des goûts (👍/👎) persistant en DB
- Versions Jules intégrées
- Suggestions alternatives
- Validation équilibre nutritionnel
"""

from datetime import date, timedelta

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.core.state import rerun
from src.modules._framework import avec_gestion_erreurs_ui, error_boundary
from src.ui import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .components import (
    afficher_apprentissage_ia,
    afficher_carte_recette_suggestion,
    afficher_configuration_preferences,
    afficher_jour_planning,
    afficher_resume_equilibre,
)
from .generation import generer_semaine_ia

# Import des fonctions pour exposer l'API publique
from .pdf import generer_pdf_planning_session

# Session keys scopées
_keys = KeyNamespace("planificateur_repas")
from .preferences import (
    ajouter_feedback,
    charger_feedbacks,
    charger_preferences,
    sauvegarder_preferences,
)


def _sauvegarder_planning_db(planning_data: dict, date_debut: date) -> bool:
    """Sauvegarde le planning généré en base de données."""
    import logging

    _logger = logging.getLogger(__name__)

    try:
        from src.services.cuisine.planning import obtenir_service_planning

        from .generation import sauvegarder_recette_ia

        service = obtenir_service_planning()

        # Construire la sélection de recettes
        recettes_selection = {}
        repas_extras = {}  # {slot_key: {entree, dessert, dessert_jules}}
        echecs = []

        # S'assurer de l'ordre des jours (Lundi -> Dimanche)
        jours_ordonnes = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        # Mapping des jours présents dans planning_data
        for i, jour_nom in enumerate(jours_ordonnes):
            # Chercher le jour dans les données (parfois le nom diffère légèrement)
            jour_data = None
            for j, d in planning_data.items():
                if j.lower().startswith(jour_nom.lower()):
                    jour_data = d
                    break

            if not jour_data:
                _logger.debug(f"Jour {jour_nom} absent du planning_data")
                continue

            # Traiter Midi et Soir
            for type_repas in ["midi", "soir"]:
                recette_info = jour_data.get(type_repas)
                if not recette_info or not isinstance(recette_info, dict):
                    _logger.warning(f"{jour_nom} {type_repas}: données manquantes ou invalides")
                    echecs.append(f"{jour_nom} {type_repas}")
                    continue

                # Sauter les repas réchauffés — pas de recette à créer
                if recette_info.get("est_rechauffe"):
                    _logger.debug(f"{jour_nom} {type_repas}: réchauffé, skip")
                    continue

                recette_id = recette_info.get("id")

                # Si pas d'ID, créer la recette en base
                if not recette_id:
                    nom_recette = recette_info.get("nom", "?")
                    _logger.info(f"Sauvegarde recette IA: {nom_recette} ({jour_nom} {type_repas})")
                    recette_id = sauvegarder_recette_ia(recette_info, type_repas)
                    if recette_id:
                        recette_info["id"] = recette_id
                    else:
                        _logger.error(
                            f"Échec sauvegarde recette: {nom_recette} ({jour_nom} {type_repas})"
                        )
                        echecs.append(f"{jour_nom} {type_repas}: {nom_recette}")

                if recette_id:
                    slot_key = f"jour_{i}_{type_repas}"
                    recettes_selection[slot_key] = recette_id
                    # Capturer entrée/dessert
                    repas_extras[slot_key] = {
                        "entree": recette_info.get("entree"),
                        "dessert": recette_info.get("dessert"),
                        "dessert_jules": recette_info.get("dessert_jules"),
                    }

        _logger.info(
            f"Planning: {len(recettes_selection)} recettes mappées, {len(echecs)} échecs: {echecs}"
        )

        if recettes_selection:
            planning = service.creer_planning_avec_choix(
                semaine_debut=date_debut,
                recettes_selection=recettes_selection,
                repas_extras=repas_extras,
            )
            return planning is not None
        else:
            _logger.error("Aucune recette n'a pu être sauvegardée")
    except Exception as e:
        _logger.error(f"Erreur sauvegarde planning: {e}")
    return False


def _charger_historique_plannings() -> list[dict]:
    """Charge l'historique des plannings via ServicePlanning."""
    try:
        from src.services.cuisine.planning import obtenir_service_planning

        service = obtenir_service_planning()
        return service.get_historique_plannings(limit=20)
    except Exception as e:
        import logging

        logging.getLogger(__name__).debug(f"Erreur chargement historique: {e}")
    return []


def _charger_planning_actif_db() -> tuple[dict, date | None, str, list]:
    """
    Charge le planning actif depuis la base de données et le convertit
    en format session_state pour restaurer l'affichage.

    Returns:
        Tuple (planning_data, date_debut, conseils, suggestions_bio)
        planning_data vide si aucun planning actif trouvé.
    """
    import logging

    _logger = logging.getLogger(__name__)

    try:
        from src.core.constants import JOURS_SEMAINE
        from src.services.cuisine.planning import obtenir_service_planning

        service = obtenir_service_planning()
        planning = service.get_planning()  # Charge le planning actif

        if not planning or not planning.repas:
            return {}, None, "", []

        # Convertir les repas DB en format session_state
        planning_data = {}
        date_debut = planning.semaine_debut

        # Regrouper les repas par jour
        repas_par_jour = {}
        for repas in planning.repas:
            jour_idx = (repas.date_repas - date_debut).days
            if 0 <= jour_idx < 7:
                jour_nom = JOURS_SEMAINE[jour_idx]
                if jour_nom not in repas_par_jour:
                    repas_par_jour[jour_nom] = {}

                # Déterminer le slot (midi/soir)
                slot = "midi" if repas.type_repas == "déjeuner" else "soir"

                meal_data = {
                    "nom": repas.recette.nom if repas.recette else "Repas planifié",
                    "id": repas.recette_id,
                    "entree": repas.entree,
                    "dessert": repas.dessert,
                    "dessert_jules": repas.dessert_jules,
                    "notes": repas.notes or "",
                }

                # Enrichir avec les infos de la recette si disponible
                if repas.recette:
                    meal_data.update(
                        {
                            "proteine": repas.recette.type_proteines,
                            "temps_minutes": repas.recette.temps_preparation
                            or repas.recette.temps_cuisson
                            or 30,
                            "difficulte": repas.recette.difficulte or "moyen",
                        }
                    )

                repas_par_jour[jour_nom][slot] = meal_data

        # S'assurer que tous les jours sont présents dans l'ordre
        for jour_nom in JOURS_SEMAINE:
            if jour_nom in repas_par_jour:
                planning_data[jour_nom] = repas_par_jour[jour_nom]

        _logger.info(
            f"✅ Planning actif chargé depuis DB: {len(planning_data)} jours, "
            f"semaine du {date_debut}"
        )
        return planning_data, date_debut, planning.notes or "", []

    except Exception as e:
        _logger.debug(f"Erreur chargement planning actif: {e}")
        return {}, None, "", []


@profiler_rerun("planificateur_repas")
def app():
    """Point d'entrée du module Planificateur de Repas."""

    st.title("🍽️ Planifier mes repas")
    st.caption("Générateur intelligent de menus équilibrés avec adaptation pour Jules")

    # ── Accès rapide ──
    _c1, _c2, _c3, _c4 = st.columns(4)
    with _c1:
        if st.button("📋 Recettes", key="plan_nav_rec", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            rerun()
    with _c2:
        if st.button("🛒 Courses", key="plan_nav_crs", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.courses")
            rerun()
    with _c3:
        if st.button("🥫 Inventaire", key="plan_nav_inv", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.inventaire")
            rerun()
    with _c4:
        if st.button("🍳 Batch Cooking", key="plan_nav_bc", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.batch_cooking_detaille")
            rerun()

    # Initialiser la session — charger le planning actif depuis la DB si la session est vide
    if SK.PLANNING_DATA not in st.session_state or not st.session_state[SK.PLANNING_DATA]:
        planning_db, date_db, conseils_db, bio_db = _charger_planning_actif_db()
        if planning_db:
            st.session_state[SK.PLANNING_DATA] = planning_db
            st.session_state[SK.PLANNING_VALIDE] = True
            if date_db:
                st.session_state[SK.PLANNING_DATE_DEBUT] = date_db
            if conseils_db:
                st.session_state[SK.PLANNING_CONSEILS] = conseils_db
            if bio_db:
                st.session_state[SK.PLANNING_SUGGESTIONS_BIO] = bio_db
        else:
            st.session_state[SK.PLANNING_DATA] = {}

    if SK.PLANNING_DATE_DEBUT not in st.session_state:
        # Par défaut: lundi prochain (début de semaine naturel)
        today = date.today()
        days_until_monday = (0 - today.weekday()) % 7  # 0 = lundi
        if days_until_monday == 0:
            days_until_monday = 7  # Si on est lundi, aller au lundi suivant
        st.session_state[SK.PLANNING_DATE_DEBUT] = today + timedelta(days=days_until_monday)

    # Tabs avec deep linking URL
    TAB_LABELS = ["📅 Planifier", "⚙️ Préférences", "📋 Historique"]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tab_planifier, tab_preferences, tab_historique = st.tabs(TAB_LABELS)

    # ═══════════════════════════════════════════════════════
    # TAB: PLANIFIER
    # ═══════════════════════════════════════════════════════

    with tab_planifier:
        with error_boundary(titre="Erreur planification"):
            # Sélection période
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                date_debut = st.date_input(
                    "📅 Début de la semaine",
                    value=st.session_state[SK.PLANNING_DATE_DEBUT],
                    format="DD/MM/YYYY",
                )
                st.session_state[SK.PLANNING_DATE_DEBUT] = date_debut

            with col2:
                date_fin = date_debut + timedelta(days=6)  # Lundi → Dimanche = 7 jours
                st.markdown(f"**→** Dimanche {date_fin.strftime('%d/%m/%Y')}")

            with col3:
                st.write("")  # Spacer

            st.divider()

            # Apprentissage IA
            with st.expander("🧠 Ce que l'IA a appris", expanded=False):
                afficher_apprentissage_ia()

            st.divider()

            # Choix des ingrédients de base pour la semaine
            from .helpers import FECULENTS_BASE, LEGUMES_BASE, PROTEINES_BASE

            with st.expander("🥕 Choisir mes ingrédients de base (optionnel)", expanded=False):
                st.caption(
                    "Sélectionnez les ingrédients autour desquels construire la semaine, "
                    "ou laissez vide pour laisser l'IA choisir."
                )

                col_b1, col_b2, col_b3 = st.columns(3)

                with col_b1:
                    legumes_sel = st.multiselect(
                        "🥬 Légumes de base",
                        options=LEGUMES_BASE,
                        default=st.session_state.get(SK.PLANNING_BASES_CHOISIES, {}).get(
                            "legumes", []
                        ),
                        placeholder="Ex: carottes, courgettes...",
                        key=_keys("bases_legumes"),
                        max_selections=4,
                    )

                with col_b2:
                    feculents_sel = st.multiselect(
                        "🍚 Féculents de base",
                        options=FECULENTS_BASE,
                        default=st.session_state.get(SK.PLANNING_BASES_CHOISIES, {}).get(
                            "feculents", []
                        ),
                        placeholder="Ex: riz, pâtes...",
                        key=_keys("bases_feculents"),
                        max_selections=3,
                    )

                with col_b3:
                    proteines_sel = st.multiselect(
                        "🥩 Protéines de base",
                        options=PROTEINES_BASE,
                        default=st.session_state.get(SK.PLANNING_BASES_CHOISIES, {}).get(
                            "proteines", []
                        ),
                        placeholder="Ex: poulet, oeufs...",
                        key=_keys("bases_proteines"),
                        max_selections=4,
                    )

                # Sauvegarder les choix en session
                bases_choisies = {}
                if legumes_sel:
                    bases_choisies["legumes"] = legumes_sel
                if feculents_sel:
                    bases_choisies["feculents"] = feculents_sel
                if proteines_sel:
                    bases_choisies["proteines"] = proteines_sel

                st.session_state[SK.PLANNING_BASES_CHOISIES] = bases_choisies

                if bases_choisies:
                    total = sum(len(v) for v in bases_choisies.values())
                    st.success(
                        f"✅ {total} ingrédient(s) sélectionné(s) — "
                        "l'IA construira les repas autour de ces bases."
                    )
                else:
                    st.info("Aucune sélection → l'IA choisira automatiquement les bases.")

            st.divider()

            # Bouton génération
            _bases = st.session_state.get(SK.PLANNING_BASES_CHOISIES, {}) or None
            col_gen1, col_gen2, col_gen3 = st.columns([2, 2, 1])

            with col_gen1:
                if st.button("🎲 Générer une semaine", type="primary", use_container_width=True):
                    with st.spinner("🤖 L'IA réfléchit à vos menus..."):
                        result = generer_semaine_ia(date_debut, bases_choisies=_bases)

                        if result and result.get("semaine"):
                            # Convertir en format interne
                            planning = {}
                            for jour_data in result["semaine"]:
                                jour = jour_data.get("jour", "")
                                planning[jour] = {}
                                for slot in ["midi", "soir"]:
                                    meal = jour_data.get(slot)
                                    if meal and isinstance(meal, dict):
                                        # Nouveau format: {entree, plat, dessert, dessert_jules}
                                        if "plat" in meal and isinstance(meal["plat"], dict):
                                            planning[jour][slot] = {
                                                **meal["plat"],
                                                "entree": meal.get("entree"),
                                                "dessert": meal.get("dessert"),
                                                "dessert_jules": meal.get("dessert_jules"),
                                            }
                                        else:
                                            # Ancien format: {nom, proteine, ...} directement
                                            planning[jour][slot] = meal
                                    else:
                                        planning[jour][slot] = meal
                                # Goûter (inchangé)
                                planning[jour]["gouter"] = jour_data.get("gouter")

                            st.session_state[SK.PLANNING_DATA] = planning
                            st.session_state[SK.PLANNING_CONSEILS] = result.get(
                                "conseils_batch", ""
                            )
                            st.session_state[SK.PLANNING_SUGGESTIONS_BIO] = result.get(
                                "suggestions_bio", []
                            )
                            st.session_state[SK.PLANNING_INGREDIENTS_COMMUNS] = result.get(
                                "ingredients_communs_semaine", {}
                            )
                            st.session_state[SK.PLANNING_RECHAUFFE_RESUME] = result.get(
                                "repas_rechauffe_resume", []
                            )
                            st.session_state[SK.PLANNING_VALIDE] = False

                            st.success("✅ Semaine générée!")
                            rerun()
                        else:
                            st.error("❌ Impossible de générer la semaine")

            with col_gen2:
                if st.button("📦 Utiliser mon stock", use_container_width=True):
                    try:
                        from src.services.inventaire import obtenir_service_inventaire

                        service_inv = obtenir_service_inventaire()
                        stock = service_inv.get_inventaire_complet() if service_inv else []
                        if stock:
                            noms_stock = [p["ingredient_nom"] for p in stock[:20]]
                            st.session_state[SK.PLANNING_STOCK_CONTEXT] = noms_stock
                            st.success(f"✅ {len(noms_stock)} produits chargés depuis votre stock")
                            st.caption("Cliquez sur 'Générer une semaine' pour les intégrer")
                        else:
                            st.info("📦 Stock vide. Ajoutez des produits dans l'inventaire.")
                    except Exception as e:
                        import logging

                        logging.getLogger(__name__).error(f"Erreur chargement stock: {e}")
                        st.warning("⚠️ Impossible de charger le stock")

            with col_gen3:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state[SK.PLANNING_DATA] = {}
                    st.session_state[SK.PLANNING_INGREDIENTS_COMMUNS] = {}
                    st.session_state[SK.PLANNING_RECHAUFFE_RESUME] = []
                    st.session_state[SK.PLANNING_VALIDE] = False
                    rerun()

            st.divider()

            # Afficher le planning
            if st.session_state[SK.PLANNING_DATA]:
                # Résumé équilibre
                afficher_resume_equilibre(st.session_state[SK.PLANNING_DATA])

                st.divider()

                # Afficher par jour
                for i, (jour, repas) in enumerate(st.session_state[SK.PLANNING_DATA].items()):
                    jour_date = date_debut + timedelta(days=i)
                    afficher_jour_planning(jour, jour_date, repas, f"jour_{i}")

                st.divider()

                # Ingrédients communs de la semaine (batch cooking)
                ingredients_communs = st.session_state.get(SK.PLANNING_INGREDIENTS_COMMUNS, {})
                if ingredients_communs:
                    st.markdown("##### 🥕 Ingrédients communs de la semaine")
                    st.caption(
                        "Ces ingrédients reviennent dans plusieurs repas — "
                        "achetez-les en quantité et préparez-les en une fois !"
                    )
                    col_leg, col_fec, col_prot = st.columns(3)
                    with col_leg:
                        legumes = ingredients_communs.get("legumes", [])
                        if legumes:
                            st.markdown("**🥬 Légumes**")
                            for leg in legumes:
                                st.caption(f"• {leg}")
                    with col_fec:
                        feculents = ingredients_communs.get("feculents", [])
                        if feculents:
                            st.markdown("**🍚 Féculents**")
                            for fec in feculents:
                                st.caption(f"• {fec}")
                    with col_prot:
                        proteines = ingredients_communs.get("proteines", [])
                        if proteines:
                            st.markdown("**🥩 Protéines**")
                            for prot in proteines:
                                st.caption(f"• {prot}")

                # Résumé des repas réchauffés
                rechauffe_resume = st.session_state.get(SK.PLANNING_RECHAUFFE_RESUME, [])
                if rechauffe_resume:
                    st.markdown("##### 🔄 Repas réchauffés (moins de cuisine !)")
                    st.caption(
                        f"**{len(rechauffe_resume)} midis** sont des réchauffés de dîners "
                        f"→ seulement **{14 - len(rechauffe_resume)} repas à cuisiner** au lieu de 14"
                    )
                    for r in rechauffe_resume:
                        st.caption(
                            f"• **{r.get('midi', '?')}**: réchauffé de "
                            f"_{r.get('source', '?')}_ ({r.get('plat', '')})"
                        )

                st.divider()

                # Conseils batch
                if st.session_state.get(SK.PLANNING_CONSEILS):
                    st.markdown("##### 🍳 Conseils Batch Cooking")
                    st.info(st.session_state[SK.PLANNING_CONSEILS])

                # Suggestions bio
                if st.session_state.get(SK.PLANNING_SUGGESTIONS_BIO):
                    st.markdown("##### 🌿 Suggestions bio/local")
                    for sug in st.session_state[SK.PLANNING_SUGGESTIONS_BIO]:
                        st.caption(f"• {sug}")

                st.divider()

                # Actions finales
                col_val1, col_val2, col_val3 = st.columns(3)

                with col_val1:
                    if st.button(
                        "💚 Valider ce planning", type="primary", use_container_width=True
                    ):
                        with st.spinner("Sauvegarde en cours..."):
                            saved = _sauvegarder_planning_db(
                                st.session_state[SK.PLANNING_DATA], date_debut
                            )
                        if saved:
                            st.session_state[SK.PLANNING_VALIDE] = True
                            st.success("✅ Planning validé !")
                        else:
                            st.error("❌ Erreur lors de la sauvegarde du planning")

                with col_val2:
                    if st.button("🛒 Aller aux Courses", use_container_width=True):
                        try:
                            # Auto-sauvegarder le planning en DB pour que le module courses le trouve
                            if not st.session_state.get(SK.PLANNING_VALIDE):
                                saved = _sauvegarder_planning_db(
                                    st.session_state[SK.PLANNING_DATA], date_debut
                                )
                                if saved:
                                    st.session_state[SK.PLANNING_VALIDE] = True

                            from src.core.state import GestionnaireEtat

                            GestionnaireEtat.naviguer_vers("cuisine.courses")
                            rerun()
                        except Exception as e:
                            import logging

                            logging.getLogger(__name__).error(f"Erreur navigation courses: {e}")
                            st.error("❌ Erreur lors de la navigation")

                with col_val3:
                    # Export PDF du planning
                    if st.session_state[SK.PLANNING_DATA]:
                        pdf_buffer = generer_pdf_planning_session(
                            planning_data=st.session_state[SK.PLANNING_DATA],
                            date_debut=date_debut,
                            conseils=st.session_state.get(SK.PLANNING_CONSEILS, ""),
                            suggestions_bio=st.session_state.get(SK.PLANNING_SUGGESTIONS_BIO, []),
                        )
                        if pdf_buffer:
                            st.download_button(
                                label="🖨️ Télécharger PDF",
                                data=pdf_buffer,
                                file_name=f"planning_{date_debut.strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                            )
                        else:
                            st.button("🖨️ Imprimer", disabled=True, use_container_width=True)

            else:
                st.info("👆 Cliquez sur 'Générer une semaine' pour commencer")

    # ═══════════════════════════════════════════════════════
    # TAB: PRÉFÉRENCES
    # ═══════════════════════════════════════════════════════

    with tab_preferences:
        with error_boundary(titre="Erreur préférences"):
            afficher_configuration_preferences()

    # ═══════════════════════════════════════════════════════
    # TAB: HISTORIQUE
    # ═══════════════════════════════════════════════════════

    with tab_historique:
        with error_boundary(titre="Erreur historique plannings"):
            st.subheader("📋 Historique des plannings")

            historique_plannings = _charger_historique_plannings()

            if historique_plannings:
                for plan in historique_plannings:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**📅 {plan['nom']}**")
                            st.caption(
                                f"Du {plan['debut'].strftime('%d/%m/%Y')} au {plan['fin'].strftime('%d/%m/%Y')}"
                            )
                        with col2:
                            st.metric("🍽️ Repas", plan["nb_repas"])
                        with col3:
                            badge = "🤖 IA" if plan["genere_par_ia"] else "✍️ Manuel"
                            st.write(badge)
            else:
                etat_vide(
                    "Aucun planning sauvegardé", "💭", "Générez votre premier planning de repas"
                )

            st.divider()

            st.markdown("##### 🧠 Vos feedbacks")
            feedbacks = charger_feedbacks()

            if feedbacks:
                for fb in feedbacks[-10:]:
                    emoji = (
                        "👍"
                        if fb.feedback == "like"
                        else "👎"
                        if fb.feedback == "dislike"
                        else "😐"
                    )
                    st.caption(f"{emoji} {fb.recette_nom} ({fb.date_feedback.strftime('%d/%m')})")
            else:
                st.caption("Pas encore de feedbacks")


__all__ = [
    # Entry point
    "app",
    # PDF
    "generer_pdf_planning_session",
    # Preferences
    "charger_preferences",
    "sauvegarder_preferences",
    "charger_feedbacks",
    "ajouter_feedback",
    # Components
    "afficher_configuration_preferences",
    "afficher_apprentissage_ia",
    "afficher_carte_recette_suggestion",
    "afficher_jour_planning",
    "afficher_resume_equilibre",
    # Generation
    "generer_semaine_ia",
]
