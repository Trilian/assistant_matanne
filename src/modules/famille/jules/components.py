"""
Module Jules - Composants UI
"""

from .ai_service import JulesAIService
from .utils import (
    CATEGORIES_CONSEILS,
    FamilyPurchase,
    date,
    get_achats_jules_en_attente,
    get_activites_pour_age,
    get_age_jules,
    get_taille_vetements,
    obtenir_contexte_db,
    st,
)


def afficher_dashboard():
    """Affiche le dashboard Jules"""
    age = get_age_jules()
    tailles = get_taille_vetements(age["mois"])
    achats = get_achats_jules_en_attente()

    st.subheader("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎂 Âge", f"{age['mois']} mois", f"{age['semaines']} semaines")

    with col2:
        st.metric("👕 Taille vêtements", tailles["vetements"])

    with col3:
        st.metric("👟 Pointure", tailles["chaussures"])

    # Achats suggeres
    if achats:
        st.markdown("---")
        st.markdown("**🛒 Achats suggeres:**")
        for achat in achats[:3]:
            emoji = "🔴" if achat.priorite in ["urgent", "haute"] else "🟡"
            st.write(f"{emoji} {achat.nom} ({achat.categorie.replace('jules_', '')})")


def afficher_activites():
    """Affiche les activites du jour"""
    age = get_age_jules()
    activites = get_activites_pour_age(age["mois"])

    st.subheader("🎨 Activites du jour")

    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        filtre_lieu = st.selectbox("Lieu", ["Tous", "Interieur", "Exterieur"], key="filtre_lieu")
    with col2:
        if st.button("🤖 Suggestions IA"):
            st.session_state["jules_show_ai_activities"] = True

    # Filtrer
    if filtre_lieu == "Interieur":
        activites = [a for a in activites if a.get("interieur", True)]
    elif filtre_lieu == "Exterieur":
        activites = [a for a in activites if not a.get("interieur", True)]

    # Afficher
    for i, act in enumerate(activites):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{act['emoji']} {act['nom']}**")
                st.caption(f"⏱️ {act['duree']} • {'🏠' if act.get('interieur') else '🌳'}")
                st.write(act["description"])
            with col2:
                if st.button("✅ Fait", key=f"act_done_{i}"):
                    st.success("Super ! 🎉")

    # Suggestions IA
    if st.session_state.get("jules_show_ai_activities"):
        st.markdown("---")
        st.markdown("**🤖 Suggestions IA:**")

        with st.spinner("Generation en cours..."):
            try:
                import asyncio

                service = JulesAIService()
                meteo = "interieur" if filtre_lieu != "Exterieur" else "exterieur"
                result = asyncio.run(service.suggerer_activites(age["mois"], meteo))
                st.markdown(result)
            except Exception as e:
                st.error(f"Erreur IA: {e}")

        if st.button("Fermer"):
            st.session_state["jules_show_ai_activities"] = False
            st.rerun()


def afficher_shopping():
    """Affiche le shopping Jules"""
    age = get_age_jules()
    tailles = get_taille_vetements(age["mois"])

    st.subheader("🛒 Shopping Jules")

    # Info tailles
    st.info(
        f"📏 Taille actuelle: **{tailles['vetements']}** • Pointure: **{tailles['chaussures']}**"
    )

    # Tabs par categorie
    tabs = st.tabs(["👕 Vêtements", "🧸 Jouets", "🛠️ Équipement", "➕ Ajouter"])

    with tabs[0]:
        afficher_achats_categorie("jules_vetements")

    with tabs[1]:
        afficher_achats_categorie("jules_jouets")

        # Suggestions IA jouets
        if st.button("🤖 Suggerer des jouets"):
            with st.spinner("Generation..."):
                try:
                    import asyncio

                    service = JulesAIService()
                    result = asyncio.run(service.suggerer_jouets(age["mois"]))
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Erreur: {e}")

    with tabs[2]:
        afficher_achats_categorie("jules_equipement")

    with tabs[3]:
        afficher_form_ajout_achat()


def afficher_achats_categorie(categorie: str):
    """Affiche les achats d'une categorie"""
    try:
        with obtenir_contexte_db() as db:
            achats = (
                db.query(FamilyPurchase)
                .filter(FamilyPurchase.categorie == categorie, FamilyPurchase.achete == False)
                .order_by(FamilyPurchase.priorite)
                .all()
            )

            if not achats:
                st.caption("Aucun article en attente")
                return

            for achat in achats:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        prio_emoji = {
                            "urgent": "🔴",
                            "haute": "🟠",
                            "moyenne": "🟡",
                            "basse": "🟢",
                        }.get(achat.priorite, "⚪")
                        st.markdown(f"**{prio_emoji} {achat.nom}**")
                        if achat.taille:
                            st.caption(f"Taille: {achat.taille}")
                        if achat.description:
                            st.caption(achat.description)

                    with col2:
                        if achat.prix_estime:
                            st.write(f"~{achat.prix_estime:.0f}€")

                    with col3:
                        if st.button("✅", key=f"buy_{achat.id}"):
                            achat.achete = True
                            achat.date_achat = date.today()
                            db.commit()
                            st.success("Achete!")
                            st.rerun()
    except Exception as e:
        st.error(f"Erreur: {e}")


def afficher_form_ajout_achat():
    """Formulaire d'ajout d'achat"""
    with st.form("add_purchase_jules"):
        nom = st.text_input("Nom de l'article *")

        col1, col2 = st.columns(2)
        with col1:
            categorie = st.selectbox(
                "Categorie",
                [
                    ("jules_vetements", "👕 Vêtements"),
                    ("jules_jouets", "🧸 Jouets"),
                    ("jules_equipement", "🛠️ Équipement"),
                ],
                format_func=lambda x: x[1],
            )

        with col2:
            priorite = st.selectbox("Priorite", ["moyenne", "haute", "urgent", "basse"])

        col3, col4 = st.columns(2)
        with col3:
            prix = st.number_input("Prix estime (€)", min_value=0.0, step=5.0)
        with col4:
            taille = st.text_input("Taille (optionnel)")

        url = st.text_input("Lien (optionnel)")
        description = st.text_area("Notes", height=80)

        if st.form_submit_button("➕ Ajouter", type="primary"):
            if not nom:
                st.error("Nom requis")
            else:
                try:
                    with obtenir_contexte_db() as db:
                        achat = FamilyPurchase(
                            nom=nom,
                            categorie=categorie[0],
                            priorite=priorite,
                            prix_estime=prix if prix > 0 else None,
                            taille=taille or None,
                            url=url or None,
                            description=description or None,
                            suggere_par="manuel",
                        )
                        db.add(achat)
                        db.commit()
                        st.success(f"✅ {nom} ajoute!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")


def afficher_conseils():
    """Affiche les conseils developpement"""
    age = get_age_jules()

    st.subheader("💡 Conseils Developpement")
    st.caption(f"Adaptes pour {age['mois']} mois")

    # Selection du thème
    cols = st.columns(3)
    themes = list(CATEGORIES_CONSEILS.items())

    for i, (key, info) in enumerate(themes):
        col = cols[i % 3]
        with col:
            if st.button(
                f"{info['emoji']} {info['titre']}", key=f"conseil_{key}", use_container_width=True
            ):
                st.session_state["jules_conseil_theme"] = key

    # Afficher le conseil selectionne
    theme = st.session_state.get("jules_conseil_theme")
    if theme:
        st.markdown("---")
        info = CATEGORIES_CONSEILS[theme]
        st.markdown(f"### {info['emoji']} {info['titre']}")

        with st.spinner("Generation du conseil..."):
            try:
                import asyncio

                service = JulesAIService()
                result = asyncio.run(service.conseil_developpement(age["mois"], theme))
                st.markdown(result)
            except Exception as e:
                st.error(f"Erreur: {e}")
