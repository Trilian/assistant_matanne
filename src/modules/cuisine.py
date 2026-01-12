"""
Module Cuisine Unifié (REFACTORING v2.2)

✅ FIX: Support navigation dynamique depuis lazy loader
✅ Les onglets s'activent automatiquement selon la route

Module complet pour la cuisine fusionnant :
- recettes.py (Gestion recettes)
- inventaire.py (Gestion stock)
- planning.py (Planning hebdo)
- courses.py (Liste courses)

Architecture simplifiée : Tout en 1 module avec tabs dynamiques.
"""

from datetime import date, timedelta

import streamlit as st

# State
from src.core.state import StateManager

# Services unifiés (getters)
from src.services.courses import get_courses_service
from src.services.inventaire import get_inventaire_service
from src.services.planning import get_planning_service
from src.services.recettes import get_recette_service

# UI Components

# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée module cuisine unifié avec navigation dynamique"""
    st.title("🍳 Cuisine")
    st.caption("Gestion complète : Recettes, Inventaire, Planning, Courses")

    # ═══════════════════════════════════════════════════════
    # ✅ RÉCUPÉRER L'ONGLET ACTIF DEPUIS SESSION_STATE
    # ═══════════════════════════════════════════════════════

    # Clé définie par le lazy loader
    active_tab = st.session_state.get("cuisine_active_tab", 0)

    # Labels des onglets
    tab_labels = ["🍽️ Recettes", "📦 Inventaire", "📅 Planning", "🛒 Courses"]

    # ═══════════════════════════════════════════════════════
    # TABS STREAMLIT (avec sélection automatique)
    # ═══════════════════════════════════════════════════════

    # Note: st.tabs ne permet pas de sélectionner programmatiquement
    # Workaround: utiliser des containers conditionnels

    # Afficher les boutons de navigation
    cols = st.columns(4)
    for idx, label in enumerate(tab_labels):
        with cols[idx]:
            if st.button(
                label,
                key=f"tab_btn_{idx}",
                use_container_width=True,
                type="primary" if idx == active_tab else "secondary",
            ):
                st.session_state.cuisine_active_tab = idx
                st.rerun()

    st.markdown("---")

    # ═══════════════════════════════════════════════════════
    # RENDER SECTION ACTIVE
    # ═══════════════════════════════════════════════════════

    if active_tab == 0:
        render_recettes()
    elif active_tab == 1:
        render_inventaire()
    elif active_tab == 2:
        render_planning()
    elif active_tab == 3:
        render_courses()


# ═══════════════════════════════════════════════════════════
# SECTION 1 : RECETTES
# ═══════════════════════════════════════════════════════════


def render_recettes():
    """Section recettes"""
    st.markdown("### 🍽️ Mes Recettes")

    # Sous-tabs
    tab_liste, tab_ajout, tab_ia = st.tabs(["📋 Liste", "➕ Ajouter", "✨ Générer IA"])

    with tab_liste:
        render_recettes_liste()

    with tab_ajout:
        render_recettes_ajout()

    with tab_ia:
        render_recettes_ia()


def render_recettes_liste():
    """Liste des recettes"""
    # Recherche
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Rechercher", placeholder="Nom de recette...")
    with col2:
        _export = st.button("📥 Export", use_container_width=True)

    # Filtres rapides
    col1, col2, col3 = st.columns(3)
    with col1:
        type_repas = st.selectbox("Type repas", ["Tous", "déjeuner", "dîner", "goûter"])
    with col2:
        saison = st.selectbox("Saison", ["Toutes", "printemps", "été", "automne", "hiver"])
    with col3:
        difficulte = st.selectbox("Difficulté", ["Toutes", "facile", "moyen", "difficile"])

    # Charger recettes
    filters = {}
    if type_repas != "Tous":
        filters["type_repas"] = type_repas
    if saison != "Toutes":
        filters["saison"] = saison
    if difficulte != "Toutes":
        filters["difficulte"] = difficulte

    recettes = get_recette_service().search_advanced(term=search if search else None, **filters, limit=50)

    # Stats
    if recettes:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(recettes))
        with col2:
            rapides = len([r for r in recettes if r.temps_total <= 30])
            st.metric("⚡ Rapides", rapides)
        with col3:
            faciles = len([r for r in recettes if r.difficulte == "facile"])
            st.metric("✅ Faciles", faciles)
        with col4:
            st.metric("⭐ Favoris", 0)  # À implémenter

        st.markdown("---")

        # Grille de recettes
        cols = st.columns(3)
        for idx, recette in enumerate(recettes):
            with cols[idx % 3]:
                with st.container():
                    st.markdown(f"**{recette.nom}**")
                    st.caption(
                        f"{recette.temps_total}min • {recette.portions}p • {recette.difficulte}"
                    )

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("👁️ Voir", key=f"voir_{recette.id}", use_container_width=True):
                            StateManager.definir_contexte(recette.id, "recette")
                            st.rerun()
                    with col_b:
                        if st.button(
                            "✏️ Éditer", key=f"edit_{recette.id}", use_container_width=True
                        ):
                            pass  # À implémenter

                    st.markdown("---")
    else:
        st.info("Aucune recette trouvée")


def render_recettes_ajout():
    """Formulaire ajout recette"""
    st.markdown("### ➕ Ajouter une Recette")

    with st.form("form_recette"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom *", placeholder="Ex: Tarte aux pommes")
            temps_prep = st.number_input("Temps préparation (min) *", min_value=1, value=15)
            portions = st.number_input("Portions *", min_value=1, value=4)
            type_repas = st.selectbox(
                "Type repas *", ["déjeuner", "dîner", "goûter", "petit_déjeuner"]
            )

        with col2:
            description = st.text_area("Description", height=100)
            temps_cuisson = st.number_input("Temps cuisson (min)", min_value=0, value=0)
            difficulte = st.selectbox("Difficulté *", ["facile", "moyen", "difficile"])
            saison = st.selectbox("Saison", ["printemps", "été", "automne", "hiver", "toute_année"])

        st.markdown("#### Ingrédients")
        ingredients_text = st.text_area(
            "Ingrédients (un par ligne)", placeholder="200g farine\n3 oeufs\n100ml lait", height=150
        )

        st.markdown("#### Étapes")
        etapes_text = st.text_area(
            "Étapes (une par ligne)",
            placeholder="1. Préchauffer le four\n2. Mélanger les ingrédients\n3. Cuire 30min",
            height=150,
        )

        submitted = st.form_submit_button("💾 Sauvegarder", use_container_width=True)

        if submitted:
            if not nom or not temps_prep:
                st.error("Veuillez remplir les champs obligatoires (*)")
            else:
                # Parser ingrédients
                ingredients = []
                for line in ingredients_text.split("\n"):
                    if line.strip():
                        parts = line.strip().split(" ", 1)
                        if len(parts) == 2:
                            ingredients.append({"nom": parts[1], "quantite": 1.0, "unite": "pcs"})

                # Parser étapes
                etapes = []
                for idx, line in enumerate(etapes_text.split("\n"), 1):
                    if line.strip():
                        etapes.append({"ordre": idx, "description": line.strip()})

                # Créer recette
                data = {
                    "nom": nom,
                    "description": description,
                    "temps_preparation": temps_prep,
                    "temps_cuisson": temps_cuisson,
                    "portions": portions,
                    "difficulte": difficulte,
                    "type_repas": type_repas,
                    "saison": saison,
                    "ingredients": ingredients,
                    "etapes": etapes,
                }

                recette = get_recette_service().create_complete(data)
                if recette:
                    st.success(f"✅ Recette '{nom}' créée !")
                    st.balloons()
                else:
                    st.error("❌ Erreur lors de la création")


def render_recettes_ia():
    """Génération IA de recettes"""
    st.markdown("### ✨ Générer avec l'IA")

    col1, col2 = st.columns(2)

    with col1:
        type_repas = st.selectbox("Type de repas", ["déjeuner", "dîner", "goûter"])
        saison = st.selectbox("Saison", ["printemps", "été", "automne", "hiver", "toute_année"])

    with col2:
        difficulte = st.selectbox("Difficulté", ["facile", "moyen", "difficile"])
        nb_recettes = st.slider("Nombre de recettes", 1, 5, 3)

    ingredients_dispo = st.text_input(
        "Ingrédients disponibles (optionnel)", placeholder="Ex: poulet, tomates, pâtes"
    )

    if st.button("🎲 Générer des recettes", use_container_width=True, type="primary"):
        with st.spinner("Génération en cours..."):
            ingredients_list = (
                [i.strip() for i in ingredients_dispo.split(",")] if ingredients_dispo else None
            )

            recettes = get_recette_service().generer_recettes_ia(
                type_repas=type_repas,
                saison=saison,
                difficulte=difficulte,
                ingredients_dispo=ingredients_list,
                nb_recettes=nb_recettes,
            )

            if recettes:
                st.success(f"✅ {len(recettes)} recettes générées !")

                for idx, recette_data in enumerate(recettes, 1):
                    with st.expander(f"📖 {idx}. {recette_data.get('nom', 'Sans nom')}"):
                        st.write(recette_data.get("description", ""))
                        st.caption(
                            f"⏱️ {recette_data.get('temps_preparation', 0)}min prep + {recette_data.get('temps_cuisson', 0)}min cuisson"
                        )

                        if st.button("➕ Ajouter cette recette", key=f"add_ia_{idx}"):
                            recette = get_recette_service().create_complete(recette_data)
                            if recette:
                                st.success("Recette ajoutée !")
                                st.rerun()
            else:
                st.warning("Aucune recette générée")


# ═══════════════════════════════════════════════════════════
# SECTION 2 : INVENTAIRE
# ═══════════════════════════════════════════════════════════


def render_inventaire():
    """Section inventaire"""
    st.markdown("### 📦 Mon Inventaire")

    # Stats alertes
    alertes = get_inventaire_service().get_alertes()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟡 Stock Bas", len(alertes.get("stock_bas", [])))
    with col2:
        st.metric("🔴 Critique", len(alertes.get("critique", [])))
    with col3:
        st.metric("⏳ Péremption", len(alertes.get("peremption_proche", [])))

    if any(alertes.values()):
        with st.expander("⚠️ Voir les alertes", expanded=True):
            for article in alertes.get("critique", [])[:5]:
                st.error(
                    f"🔴 **{article['ingredient_nom']}** : {article['quantite']}{article['unite']} (seuil: {article['quantite_min']})"
                )

    st.markdown("---")

    # Liste inventaire
    inventaire = get_inventaire_service().get_inventaire_complet()

    if inventaire:
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            emplacement_filter = st.selectbox(
                "Emplacement", ["Tous", "Frigo", "Congélateur", "Placard"]
            )
        with col2:
            search = st.text_input("🔍 Rechercher")

        # Filtrer
        filtered = inventaire
        if emplacement_filter != "Tous":
            filtered = [a for a in filtered if a.get("emplacement") == emplacement_filter]
        if search:
            filtered = [a for a in filtered if search.lower() in a["ingredient_nom"].lower()]

        # Afficher
        for article in filtered[:20]:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                statut_emoji = {
                    "ok": "🟢",
                    "stock_bas": "🟡",
                    "critique": "🔴",
                    "peremption_proche": "⏳",
                }
                st.write(
                    f"{statut_emoji.get(article['statut'], '⚪')} **{article['ingredient_nom']}**"
                )

            with col2:
                st.write(f"{article['quantite']}{article['unite']}")

            with col3:
                if st.button("➕", key=f"add_{article['id']}"):
                    get_inventaire_service().ajuster_quantite(article["id"], 1, "ajout")
                    st.rerun()

            with col4:
                if st.button("➖", key=f"sub_{article['id']}"):
                    get_inventaire_service().ajuster_quantite(article["id"], 1, "retrait")
                    st.rerun()
    else:
        st.info("Inventaire vide")


# ═══════════════════════════════════════════════════════════
# SECTION 3 : PLANNING
# ═══════════════════════════════════════════════════════════


def render_planning():
    """Section planning"""
    st.markdown("### 📅 Planning Hebdomadaire")

    # Navigation semaine
    if "semaine_actuelle" not in st.session_state:
        today = date.today()
        st.session_state.semaine_actuelle = today - timedelta(days=today.weekday())

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Semaine précédente", use_container_width=True):
            st.session_state.semaine_actuelle -= timedelta(days=7)
            st.rerun()
    with col2:
        semaine = st.session_state.semaine_actuelle
        st.markdown(f"**Semaine du {semaine.strftime('%d/%m/%Y')}**")
    with col3:
        if st.button("Semaine suivante ➡️", use_container_width=True):
            st.session_state.semaine_actuelle += timedelta(days=7)
            st.rerun()

    # Charger planning
    planning = get_planning_service().get_planning_semaine(st.session_state.semaine_actuelle)

    if planning:
        st.success(f"✅ Planning : {planning['nom']}")

        # Afficher par jour
        for i in range(7):
            jour = st.session_state.semaine_actuelle + timedelta(days=i)
            jour_str = jour.strftime("%Y-%m-%d")

            with st.expander(f"📆 {jour.strftime('%A %d/%m')}", expanded=(i < 2)):
                repas_jour = planning["repas_par_jour"].get(jour_str, [])

                if repas_jour:
                    for repas in repas_jour:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(
                                f"**{repas['type_repas']}** : {repas['recette_nom'] or 'Non défini'}"
                            )
                        with col2:
                            checked = st.checkbox(
                                "✅", value=repas["prepare"], key=f"prep_{repas['id']}"
                            )
                            if checked != repas["prepare"]:
                                get_planning_service().marquer_repas_prepare(repas["id"], checked)
                        with col3:
                            if st.button("✏️", key=f"edit_repas_{repas['id']}"):
                                pass  # À implémenter
                else:
                    st.caption("Aucun repas planifié")
    else:
        st.info("Aucun planning pour cette semaine")

        if st.button("🎲 Générer un planning IA", type="primary"):
            with st.spinner("Génération..."):
                planning = get_planning_service().generer_planning_ia(st.session_state.semaine_actuelle)
                if planning:
                    st.success("Planning généré !")
                    st.rerun()


# ═══════════════════════════════════════════════════════════
# SECTION 4 : COURSES
# ═══════════════════════════════════════════════════════════


def render_courses():
    """Section liste de courses"""
    st.markdown("### 🛒 Liste de Courses")

    # Charger liste
    courses = get_courses_service().get_liste_courses(achetes=False)

    if courses:
        st.metric("Articles", len(courses))
        st.markdown("---")

        for article in courses:
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                priorite_emoji = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}
                st.write(
                    f"{priorite_emoji.get(article['priorite'], '⚪')} **{article['ingredient_nom']}** ({article['quantite_necessaire']}{article['unite']})"
                )

            with col2:
                checked = st.checkbox(
                    "✅",
                    value=article["achete"],
                    key=f"achete_{article['id']}",
                    label_visibility="collapsed",
                )
                if checked != article["achete"]:
                    get_courses_service().marquer_achete(article["id"], checked)
                    st.rerun()

            with col3:
                if st.button("🗑️", key=f"del_{article['id']}"):
                    get_courses_service().delete(article["id"])
                    st.rerun()

        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Tout marquer acheté", use_container_width=True):
                for article in courses:
                    get_courses_service().marquer_achete(article["id"], True)
                st.rerun()
        with col2:
            if st.button("📥 Export CSV", use_container_width=True):
                csv = get_courses_service().export_to_csv(courses)
                st.download_button("⬇️ Télécharger", csv, "courses.csv", "text/csv")
    else:
        st.info("Liste de courses vide")

        if st.button("🎲 Suggérer avec l'IA", type="primary"):
            with st.spinner("Analyse inventaire..."):
                suggestions = get_courses_service().generer_suggestions_ia_depuis_inventaire()
                if suggestions:
                    st.success(f"{len(suggestions)} suggestions !")
                    for sugg in suggestions:
                        if st.button(f"➕ {sugg['nom']}", key=f"add_sugg_{sugg['nom']}"):
                            get_courses_service().ajouter_article(
                                sugg["nom"],
                                sugg["quantite"],
                                sugg.get("unite", "pcs"),
                                sugg.get("priorite", "moyenne"),
                            )
                            st.rerun()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = ["app"]
