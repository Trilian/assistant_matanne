"""
Module Planificateur de Repas Intelligent - UI Streamlit

Interface style Jow:
- Générateur IA de menus équilibrés
- Apprentissage des goûts (👍/👎) persistant en DB
- Versions Jules intégrées
- Suggestions alternatives
- Validation équilibre nutritionnel
"""

import json
from datetime import date, timedelta

import streamlit as st

from src.core.constants import JOURS_SEMAINE
from src.core.date_utils import jour_debut_from_nom
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


def _sauvegarder_planning_db(
    planning_data: dict, date_debut: date, date_fin: date, genere_par_ia: bool = False
) -> bool:
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

        # Calculer les jours réels entre date_debut et date_fin
        nb_jours = (date_fin - date_debut).days + 1
        jours_dates = [date_debut + timedelta(days=i) for i in range(nb_jours)]
        jours_noms = [JOURS_SEMAINE[d.weekday()] for d in jours_dates]

        # Mapping des jours présents dans planning_data
        for i, (jour_nom, jour_date) in enumerate(zip(jours_noms, jours_dates, strict=False)):
            # Chercher le jour dans les données
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
                genere_par_ia=genere_par_ia,
            )
            if planning is not None:
                # Persister les métadonnées (suggestions bio, conseils batch) dans notes
                try:
                    meta = {
                        "conseils_batch": st.session_state.get(SK.PLANNING_CONSEILS, ""),
                        "suggestions_bio": st.session_state.get(SK.PLANNING_SUGGESTIONS_BIO, []),
                        "ingredients_communs": st.session_state.get(
                            SK.PLANNING_INGREDIENTS_COMMUNS, {}
                        ),
                    }
                    service.update(planning.id, {"notes": json.dumps(meta, ensure_ascii=False)})
                except Exception as e:
                    _logger.warning(f"Impossible de sauvegarder les métadonnées du planning: {e}")
                return True
            return False
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


def _charger_planning_actif_db(
    planning_id: int | None = None,
) -> tuple[dict, date | None, str, list]:
    """
    Charge le planning actif (ou un planning spécifique) depuis la base de données
    et le convertit en format session_state pour restaurer l'affichage.

    Args:
        planning_id: ID du planning à charger. Si None, charge le planning actif.

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
        planning = service.get_planning(planning_id=planning_id)

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

        # Décoder les métadonnées depuis le champ notes (JSON)
        notes_raw = planning.notes or ""
        conseils = ""
        suggestions_bio = []
        try:
            notes_parsed = json.loads(notes_raw)
            if isinstance(notes_parsed, dict):
                conseils = notes_parsed.get("conseils_batch", "")
                suggestions_bio = notes_parsed.get("suggestions_bio", [])
            else:
                conseils = notes_raw
        except (json.JSONDecodeError, TypeError):
            conseils = notes_raw

        return planning_data, date_debut, conseils, suggestions_bio

    except Exception as e:
        _logger.debug(f"Erreur chargement planning actif: {e}")
        return {}, None, "", []


def _afficher_selection_manuelle(date_debut: date, date_fin: date):
    """Affiche la sélection manuelle de recettes pour chaque jour/slot."""
    from src.services.cuisine.recettes import obtenir_service_recettes

    service_recettes = obtenir_service_recettes()
    if not service_recettes:
        st.error("Service recettes indisponible")
        return

    all_recipes = service_recettes.get_all(limit=500)
    if not all_recipes:
        st.info("Aucune recette en base. Ajoutez des recettes d'abord.")
        return

    recipe_names = {r.nom: r for r in all_recipes}
    recipe_options = ["(Aucun)"] + sorted(recipe_names.keys())

    nb_jours = (date_fin - date_debut).days + 1
    planning = {}

    for i in range(nb_jours):
        jour_date = date_debut + timedelta(days=i)
        jour_nom = JOURS_SEMAINE[jour_date.weekday()]

        with st.expander(f"{jour_nom} {jour_date.strftime('%d/%m')}", expanded=(i < 3)):
            col_midi, col_soir = st.columns(2)
            with col_midi:
                midi_choice = st.selectbox(
                    "Midi",
                    recipe_options,
                    key=_keys("manual_midi", i),
                )
            with col_soir:
                soir_choice = st.selectbox(
                    "Soir",
                    recipe_options,
                    key=_keys("manual_soir", i),
                )

            jour_data = {}
            if midi_choice != "(Aucun)" and midi_choice in recipe_names:
                r = recipe_names[midi_choice]
                jour_data["midi"] = {
                    "nom": r.nom,
                    "id": r.id,
                    "proteine": r.type_proteines,
                    "temps_minutes": r.temps_preparation or 30,
                    "difficulte": r.difficulte or "moyen",
                }
            if soir_choice != "(Aucun)" and soir_choice in recipe_names:
                r = recipe_names[soir_choice]
                jour_data["soir"] = {
                    "nom": r.nom,
                    "id": r.id,
                    "proteine": r.type_proteines,
                    "temps_minutes": r.temps_preparation or 30,
                    "difficulte": r.difficulte or "moyen",
                }
            if jour_data:
                planning[jour_nom] = jour_data

    if st.button("Valider mon planning", type="primary", use_container_width=True):
        if not planning:
            st.warning("Sélectionnez au moins un repas")
        else:
            st.session_state[SK.PLANNING_DATA] = planning
            st.session_state[SK.PLANNING_VALIDE] = False
            st.success(f"✅ Planning créé avec {sum(len(v) for v in planning.values())} repas")
            rerun()


def _matcher_recettes_db(planning: dict):
    """Match les noms de recettes IA contre la DB et injecte les ID (matching normalisé)."""
    try:
        from src.services.cuisine.recettes import obtenir_service_recettes
        from src.services.cuisine.recettes.utils import normaliser_nom_recette

        service = obtenir_service_recettes()
        if not service:
            return

        all_recipes = service.get_all(limit=500)
        # Construire un mapping nom normalisé → id (garder le premier trouvé)
        name_to_id = {}
        for r in all_recipes:
            key = normaliser_nom_recette(r.nom)
            if key and key not in name_to_id:
                name_to_id[key] = r.id

        matched = 0
        for _jour, repas in planning.items():
            for slot in ["midi", "soir"]:
                meal = repas.get(slot)
                if meal and isinstance(meal, dict) and not meal.get("id"):
                    nom_norm = normaliser_nom_recette(meal.get("nom", ""))
                    if nom_norm in name_to_id:
                        meal["id"] = name_to_id[nom_norm]
                        matched += 1
        if matched:
            import logging

            logging.getLogger(__name__).info(f"{matched} recettes matchées avec la DB")
    except Exception:
        pass


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
            # Ne restaurer les dates que si le planning est encore actuel (pas dans le passé)
            if date_db and date_db >= date.today() - timedelta(days=date.today().weekday()):
                st.session_state[SK.PLANNING_DATE_DEBUT] = date_db
            if conseils_db:
                st.session_state[SK.PLANNING_CONSEILS] = conseils_db
            if bio_db:
                st.session_state[SK.PLANNING_SUGGESTIONS_BIO] = bio_db
        else:
            st.session_state[SK.PLANNING_DATA] = {}

    if SK.PLANNING_DATE_DEBUT not in st.session_state:
        # Par défaut: prochain jour de début de semaine selon les préférences
        today = date.today()
        prefs_init = charger_preferences()
        _jour_debut_wd = jour_debut_from_nom(prefs_init.jour_debut_semaine)
        days_until_start = (_jour_debut_wd - today.weekday()) % 7
        if days_until_start == 0:
            # On est le jour de début, rester à aujourd'hui
            st.session_state[SK.PLANNING_DATE_DEBUT] = today
        else:
            st.session_state[SK.PLANNING_DATE_DEBUT] = today + timedelta(days=days_until_start)

    if SK.PLANNING_DATE_FIN not in st.session_state:
        # Par défaut: 6 jours après le début (semaine complète)
        debut = st.session_state[SK.PLANNING_DATE_DEBUT]
        st.session_state[SK.PLANNING_DATE_FIN] = debut + timedelta(days=6)

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
                    "📅 Début",
                    value=st.session_state[SK.PLANNING_DATE_DEBUT],
                    format="DD/MM/YYYY",
                )
                st.session_state[SK.PLANNING_DATE_DEBUT] = date_debut

            with col2:
                date_fin = st.date_input(
                    "📅 Fin",
                    value=st.session_state[SK.PLANNING_DATE_FIN],
                    min_value=date_debut,
                    max_value=date_debut + timedelta(days=13),
                    format="DD/MM/YYYY",
                )
                st.session_state[SK.PLANNING_DATE_FIN] = date_fin

            with col3:
                nb_jours = (date_fin - date_debut).days + 1
                jours_noms = [
                    JOURS_SEMAINE[((date_debut + timedelta(days=i)).weekday())]
                    for i in range(nb_jours)
                ]
                st.caption(f"{nb_jours} jours")
                st.caption(f"{jours_noms[0]} → {jours_noms[-1]}")

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

            # Plats imposés par l'utilisateur
            with st.expander("🍽️ Plats souhaités cette semaine (optionnel)", expanded=False):
                st.caption(
                    "Indiquez les plats que vous voulez manger cette semaine (un par ligne). "
                    "L'IA les intégrera au planning et complétera avec d'autres recettes équilibrées."
                )
                plats_text = st.text_area(
                    "Mes plats souhaités",
                    value=st.session_state.get(SK.PLANNING_RECETTES_IMPOSEES, ""),
                    placeholder="Ex:\nGnocchi à la crème\nEnchiladas\nKnacki purée\nSaucisses flageolets",
                    key=_keys("recettes_imposees"),
                    height=120,
                    label_visibility="collapsed",
                )
                st.session_state[SK.PLANNING_RECETTES_IMPOSEES] = plats_text
                recettes_imposees = [
                    line.strip() for line in plats_text.split("\n") if line.strip()
                ]
                if recettes_imposees:
                    st.success(
                        f"✅ {len(recettes_imposees)} plat(s) imposé(s) — "
                        "l'IA les intégrera au planning."
                    )

            st.divider()

            # ── Mode de planification ──
            st.markdown("##### Mode de planification")
            planning_mode = st.radio(
                "Source des recettes",
                ["Générer avec IA", "Utiliser mes recettes", "Mix des deux"],
                horizontal=True,
                key=_keys("planning_mode"),
                label_visibility="collapsed",
            )
            st.session_state[SK.PLANNING_MODE] = planning_mode

            st.divider()

            # ── Mode "Mes recettes" : sélection manuelle ──
            if planning_mode == "Utiliser mes recettes":
                _afficher_selection_manuelle(date_debut, date_fin)

            # ── Mode IA ou Mix ──
            else:
                # Bouton génération
                _bases = st.session_state.get(SK.PLANNING_BASES_CHOISIES, {}) or None
                _recettes_imp = [
                    line.strip()
                    for line in st.session_state.get(SK.PLANNING_RECETTES_IMPOSEES, "").split("\n")
                    if line.strip()
                ] or None
                col_gen1, col_gen2, col_gen3 = st.columns([2, 2, 1])

                with col_gen1:
                    if st.button(
                        "🎲 Générer une semaine", type="primary", use_container_width=True
                    ):
                        with st.spinner("🤖 L'IA réfléchit à vos menus..."):
                            # Calculer les jours à planifier depuis les dates choisies
                            nb_jours_plan = (date_fin - date_debut).days + 1
                            jours_a_planifier = [
                                JOURS_SEMAINE[(date_debut + timedelta(days=i)).weekday()]
                                for i in range(nb_jours_plan)
                            ]
                            result = generer_semaine_ia(
                                date_debut,
                                date_fin=date_fin,
                                jours_a_planifier=jours_a_planifier,
                                bases_choisies=_bases,
                                recettes_imposees=_recettes_imp,
                                mode="mixte" if planning_mode == "Mix des deux" else "ia",
                            )

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
                                                plat = meal["plat"]
                                                planning[jour][slot] = {
                                                    **plat,
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

                                # Recalculer le résumé réchauffés depuis les données réelles
                                rechauffe_resume = []
                                for jour_nom, repas_jour in planning.items():
                                    for tr in ["midi", "soir"]:
                                        slot_data = repas_jour.get(tr)
                                        if (
                                            slot_data
                                            and isinstance(slot_data, dict)
                                            and slot_data.get("est_rechauffe")
                                        ):
                                            rechauffe_resume.append(
                                                {
                                                    "midi": f"{jour_nom} {tr}",
                                                    "source": slot_data.get(
                                                        "rechauffe_de", "?"
                                                    ),
                                                    "plat": slot_data.get("nom", "?"),
                                                }
                                            )
                                st.session_state[SK.PLANNING_RECHAUFFE_RESUME] = rechauffe_resume

                                st.session_state[SK.PLANNING_VALIDE] = False

                                # Matcher les noms IA contre les recettes existantes en DB
                                _matcher_recettes_db(planning)

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
                                st.success(
                                    f"✅ {len(noms_stock)} produits chargés depuis votre stock"
                                )
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

                # Afficher par jour — mapping correct jour/date
                nb_jours_affich = (date_fin - date_debut).days + 1
                planning_data = st.session_state[SK.PLANNING_DATA]
                for i in range(nb_jours_affich):
                    jour_date = date_debut + timedelta(days=i)
                    jour_nom = JOURS_SEMAINE[jour_date.weekday()]
                    # Chercher le jour dans les données du planning
                    repas = None
                    for j, d in planning_data.items():
                        if j.lower().startswith(jour_nom.lower()):
                            repas = d
                            break
                    if repas:
                        afficher_jour_planning(jour_nom, jour_date, repas, f"jour_{i}")

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
                        _is_ia = (
                            st.session_state.get(SK.PLANNING_MODE, "") != "Utiliser mes recettes"
                        )
                        with st.spinner("Sauvegarde en cours..."):
                            saved = _sauvegarder_planning_db(
                                st.session_state[SK.PLANNING_DATA],
                                date_debut,
                                date_fin,
                                genere_par_ia=_is_ia,
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
                                _is_ia = (
                                    st.session_state.get(SK.PLANNING_MODE, "")
                                    != "Utiliser mes recettes"
                                )
                                saved = _sauvegarder_planning_db(
                                    st.session_state[SK.PLANNING_DATA],
                                    date_debut,
                                    date_fin,
                                    genere_par_ia=_is_ia,
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
                        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
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
                        with col4:
                            if st.button(
                                "📂 Revoir",
                                key=_keys("charger_planning", plan["id"]),
                                use_container_width=True,
                                help="Restaure ce planning comme planning actif pour le revoir ou le modifier",
                            ):
                                planning_db, date_db, conseils_db, bio_db = (
                                    _charger_planning_actif_db(planning_id=plan["id"])
                                )
                                if planning_db:
                                    st.session_state[SK.PLANNING_DATA] = planning_db
                                    st.session_state[SK.PLANNING_VALIDE] = True
                                    if date_db:
                                        st.session_state[SK.PLANNING_DATE_DEBUT] = date_db
                                        st.session_state[SK.PLANNING_DATE_FIN] = (
                                            date_db + timedelta(days=6)
                                        )
                                    if conseils_db:
                                        st.session_state[SK.PLANNING_CONSEILS] = conseils_db
                                    if bio_db:
                                        st.session_state[SK.PLANNING_SUGGESTIONS_BIO] = bio_db
                                    st.toast(
                                        f"✅ Planning du {plan['debut'].strftime('%d/%m')} restauré"
                                    )
                                    rerun()
                                else:
                                    st.error("❌ Impossible de charger ce planning")
                        with col5:
                            _del_key = _keys("suppr_planning", plan["id"])
                            _confirm_key = _keys("confirm_suppr", plan["id"])
                            if st.session_state.get(_confirm_key):
                                if st.button(
                                    "⚠️ Confirmer",
                                    key=_del_key,
                                    use_container_width=True,
                                    type="primary",
                                ):
                                    try:
                                        from src.services.cuisine.planning import (
                                            obtenir_service_planning,
                                        )

                                        service = obtenir_service_planning()
                                        service.delete(plan["id"])
                                        st.session_state[_confirm_key] = False
                                        st.toast("✅ Planning supprimé")
                                        rerun()
                                    except Exception as e:
                                        import logging

                                        logging.getLogger(__name__).error(
                                            f"Erreur suppression planning: {e}"
                                        )
                                        st.error("❌ Erreur lors de la suppression")
                            else:
                                if st.button(
                                    "🗑️",
                                    key=_del_key,
                                    use_container_width=True,
                                    help="Supprimer ce planning",
                                ):
                                    st.session_state[_confirm_key] = True
                                    rerun()
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
