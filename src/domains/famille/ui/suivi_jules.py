"""
Module Suivi Jules avec Agent IA intégré
Suivi du développement avec conseils adaptés à l'Ã¢ge
"""

import asyncio
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.core.ai_agent import AgentIA
from src.core.database import get_db_context
from src.core.models import ChildProfile, WellbeingEntry
from src.utils.formatters import format_quantity

# Logique métier pure
from src.domains.famille.logic.suivi_jules_logic import (
    calculer_age,
    formater_age,
    get_etapes_age,
    calculer_moyenne_sommeil,
    analyser_humeurs,
    valider_entree_bien_etre,
    valider_milestone
)

# ===================================
# HELPERS
# ===================================


def get_child_profile() -> ChildProfile:
    """Récupère le profil de Jules"""
    with get_db_context() as db:
        child = db.query(ChildProfile).filter(ChildProfile.name == "Jules").first()

        if not child:
            # Créer le profil si inexistant
            child = ChildProfile(
                name="Jules", birth_date=date(2024, 6, 22), notes="Notre petit bout de chou â¤ï¸"
            )
            db.add(child)
            db.commit()
            db.refresh(child)

        return child


def calculer_age(birth_date: date) -> dict:
    """Calcule l'Ã¢ge en jours, semaines, mois"""
    today = date.today()
    delta = today - birth_date

    jours = delta.days
    semaines = jours // 7
    mois = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)

    # Ajuster si le jour n'est pas encore passé
    if today.day < birth_date.day:
        mois -= 1

    return {"jours": jours, "semaines": semaines, "mois": mois, "annees": mois // 12}


def get_etapes_developpement(age_mois: int) -> list[dict]:
    """Retourne les étapes clés du développement selon l'Ã¢ge"""
    etapes = {
        0: [
            "Réflexes primitifs (succion, préhension)",
            "Vision floue, reconnaît visages proches",
            "Dort 16-18h par jour",
        ],
        1: [
            "Commence à sourire",
            "Suit des objets du regard",
            "Meilleure coordination main-bouche",
        ],
        2: ["Babillage (ah, oh, eu)", "Tient sa tête", "Reconnaît les visages familiers"],
        3: ["Rit aux éclats", "Attrape les objets", "Se retourne sur le ventre"],
        4: ["Assis avec soutien", "Exploration bouche-main", "Différencie voix connues/inconnues"],
        5: [
            "Diversification alimentaire possible",
            "Transfère objets d'une main à l'autre",
            "Babillage plus complexe (ba-ba, ma-ma)",
        ],
        6: ["Tient assis seul", "Début de la position 4 pattes", "Angoisse de séparation"],
        9: ["Se met debout avec appui", "Premiers mots (papa, maman)", "Joue à coucou-caché"],
        12: ["Marche avec aide ou seul", "Premiers pas", "Comprend des consignes simples"],
    }

    # Trouver l'étape la plus proche
    mois_cle = min(etapes.keys(), key=lambda x: abs(x - age_mois))
    return etapes.get(mois_cle, ["Développement en cours"])


def charger_entrees_bien_etre(child_id: int, limit: int = 30) -> pd.DataFrame:
    """Charge les entrées de bien-être"""
    with get_db_context() as db:
        entries = (
            db.query(WellbeingEntry)
            .filter(WellbeingEntry.child_id == child_id)
            .order_by(WellbeingEntry.date.desc())
            .limit(limit)
            .all()
        )

        return pd.DataFrame(
            [
                {
                    "id": e.id,
                    "date": e.date,
                    "humeur": e.mood,
                    "sommeil": e.sleep_hours,
                    "activite": e.activity,
                    "notes": e.notes or "",
                }
                for e in entries
            ]
        )


def ajouter_entree(child_id: int, humeur: str, sommeil: float, activite: str, notes: str):
    """Ajoute une entrée de bien-être"""
    with get_db_context() as db:
        entry = WellbeingEntry(
            child_id=child_id,
            date=date.today(),
            mood=humeur,
            sleep_hours=sommeil,
            activity=activite,
            notes=notes,
        )
        db.add(entry)
        db.commit()


# ===================================
# MODULE PRINCIPAL
# ===================================


def app():
    """Module Suivi Jules avec IA intégrée"""

    st.title("🗑️ Suivi de Jules")
    st.caption("Développement et conseils adaptés avec l'IA")

    # Récupérer l'agent IA
    agent: AgentIA = st.session_state.get("agent_ia")

    # Récupérer le profil de Jules
    jules = get_child_profile()
    age = calculer_age(jules.birth_date)

    # ===================================
    # HEADER - INFO JULES
    # ===================================

    st.markdown("---")

    col_info1, col_info2, col_info3 = st.columns([2, 1, 1])

    with col_info1:
        st.markdown(f"### 🗑️ {jules.name}")
        st.caption(f"Né le {jules.birth_date.strftime('%d/%m/%Y')}")

        if jules.notes:
            st.info(jules.notes)

    with col_info2:
        st.metric("Ã‚ge", f"{age['mois']} mois", delta=f"{age['semaines']} semaines")
        st.metric("Jours de vie", age["jours"])

    with col_info3:
        # Prochaine étape importante
        prochaine_etape = ""
        if age["mois"] < 3:
            prochaine_etape = "3 mois : Rires"
        elif age["mois"] < 6:
            prochaine_etape = "6 mois : Assis"
        elif age["mois"] < 12:
            prochaine_etape = "12 mois : Marche"
        else:
            prochaine_etape = "Développement continu"

        st.metric("Prochaine étape", prochaine_etape)

    st.markdown("---")

    # ===================================
    # TABS PRINCIPAUX
    # ===================================

    tab1, tab2, tab3, tab4 = st.tabs(
        ["[CHART] Tableau de bord", "– Conseils IA", "📥 Journal", "👧 Statistiques"]
    )

    # ===================================
    # TAB 1 : TABLEAU DE BORD
    # ===================================

    with tab1:
        st.subheader("Développement actuel")

        # Ã‰tapes du développement
        st.markdown("### 🎯 Ã‰tapes clés du développement")

        etapes = get_etapes_developpement(age["mois"])

        for etape in etapes:
            st.success(f"âœ… {etape}")

        st.markdown("---")

        # Dernières entrées
        st.markdown("### 👶 Dernières observations")

        df = charger_entrees_bien_etre(jules.id, limit=7)

        if df.empty:
            st.info("Aucune observation encore. Commence à noter les progrès !")
        else:
            # Graphique sommeil
            col_graph1, col_graph2 = st.columns(2)

            with col_graph1:
                st.markdown("**💰 Sommeil (7 derniers jours)**")
                if not df["sommeil"].isnull().all():
                    st.line_chart(df.set_index("date")["sommeil"])
                else:
                    st.caption("Pas de données de sommeil")

            with col_graph2:
                st.markdown("**📋 Humeur**")
                humeur_counts = df["humeur"].value_counts()
                st.bar_chart(humeur_counts)

            # Liste des entrées
            st.markdown("---")
            st.markdown("**Dernières observations**")

            for _, row in df.head(5).iterrows():
                with st.expander(
                    f"{row['date'].strftime('%d/%m/%Y')} - {row['humeur']}", expanded=False
                ):
                    st.write(f"**Sommeil :** {row['sommeil']}h")
                    st.write(f"**Activité :** {row['activite']}")
                    if row["notes"]:
                        st.write(f"**Notes :** {row['notes']}")

        # Ajout rapide
        st.markdown("---")
        st.markdown("### âš¡ Ajouter une observation rapide")

        with st.form("form_quick_entry"):
            col_q1, col_q2, col_q3 = st.columns(3)

            with col_q1:
                humeur = st.selectbox("Humeur", ["📋 Bien", "📷 Moyen", "📷ž Mal"])

            with col_q2:
                sommeil = st.number_input("Heures de sommeil", 0.0, 24.0, 10.0, 0.5)

            with col_q3:
                activite = st.text_input("Activité", placeholder="Ex: Promenade")

            notes = st.text_area("Notes (optionnel)", placeholder="Observations...")

            submitted = st.form_submit_button("âž• Ajouter", type="primary")

            if submitted:
                ajouter_entree(jules.id, humeur, sommeil, activite, notes)
                st.success("âœ… Observation ajoutée")
                st.balloons()
                st.rerun()

    # ===================================
    # TAB 2 : CONSEILS IA
    # ===================================

    with tab2:
        st.subheader("– Conseils personnalisés par l'IA")

        if not agent:
            st.error("Agent IA non disponible")
        else:
            st.info(f"🔔 Conseils adaptés à l'Ã¢ge de Jules ({age['mois']} mois)")

            # Options
            col_c1, col_c2 = st.columns(2)

            with col_c1:
                domaine = st.selectbox(
                    "Domaine",
                    [
                        "Général",
                        "Sommeil",
                        "Alimentation",
                        "Développement moteur",
                        "Développement cognitif",
                        "Socialisation",
                    ],
                )

            with col_c2:
                st.write("")
                st.write("")
                generer = st.button(
                    "âœ¨ Demander conseil à l'IA", type="primary", use_container_width=True
                )

            if generer:
                with st.spinner("– L'IA prépare des conseils personnalisés..."):
                    try:
                        # Récupérer contexte
                        df_recent = charger_entrees_bien_etre(jules.id, limit=7)

                        contexte = {
                            "age_mois": age["mois"],
                            "domaine": domaine,
                            "observations_recentes": (
                                df_recent.to_dict("records") if not df_recent.empty else []
                            ),
                        }

                        # Appel IA
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        try:
                            conseils = loop.run_until_complete(
                                agent.conseiller_developpement(age["mois"], contexte)
                            )
                        finally:
                            loop.close()

                        st.session_state["conseils_jules"] = conseils
                        st.success("âœ… Conseils générés !")

                    except Exception as e:
                        st.error(f"Erreur IA : {e}")

            # Afficher les conseils
            if "conseils_jules" in st.session_state:
                conseils = st.session_state["conseils_jules"]

                st.markdown("---")

                # Conseils
                if "conseils" in conseils:
                    st.markdown("### 🔔 Conseils")
                    for conseil in conseils["conseils"]:
                        st.success(f"âœ… {conseil}")

                # Activités
                if "activites" in conseils:
                    st.markdown("### 🎨 Activités suggérées")
                    for activite in conseils["activites"]:
                        st.info(f"🎯 {activite}")

                # Alertes
                if "alertes" in conseils and conseils["alertes"]:
                    st.markdown("### âš ï¸ Points d'attention")
                    for alerte in conseils["alertes"]:
                        st.warning(f"âš ï¸ {alerte}")

                # Bouton pour sauvegarder
                if st.button("🎯 Sauvegarder ces conseils dans le journal"):
                    notes_conseil = f"Conseils IA ({domaine}):\n"
                    notes_conseil += "\n".join([f"- {c}" for c in conseils.get("conseils", [])])

                    ajouter_entree(
                        jules.id,
                        humeur="📋 Bien",
                        sommeil=0.0,
                        activite="Conseils IA",
                        notes=notes_conseil,
                    )

                    st.success("âœ… Conseils sauvegardés dans le journal")
                    del st.session_state["conseils_jules"]

            # Raccourcis conseils
            st.markdown("---")
            st.markdown("### 📤 Conseils rapides")

            col_r1, col_r2, col_r3 = st.columns(3)

            raccourcis = [
                ("💰 Sommeil", "Sommeil"),
                ("📱 Alimentation", "Alimentation"),
                ("¸ Motricité", "Développement moteur"),
                ("🍽️ Cognitif", "Développement cognitif"),
                ("💡 Social", "Socialisation"),
                ("🎨 Lecture", "Général"),
            ]

            for i, (label, dom) in enumerate(raccourcis):
                col = [col_r1, col_r2, col_r3][i % 3]
                with col:
                    if st.button(label, use_container_width=True, key=f"quick_{dom}"):
                        st.session_state["domaine_conseil"] = dom
                        st.rerun()

    # ===================================
    # TAB 3 : JOURNAL COMPLET
    # ===================================

    with tab3:
        st.subheader("📥 Journal de bord")

        # Formulaire détaillé
        with st.form("form_journal"):
            st.markdown("### âž• Nouvelle entrée")

            col_j1, col_j2 = st.columns(2)

            with col_j1:
                _date_entry = st.date_input("Date", value=date.today())
                humeur = st.selectbox("Humeur", ["📋 Bien", "📷 Moyen", "📷ž Mal"])
                sommeil = st.number_input("Heures de sommeil", 0.0, 24.0, 10.0, 0.5)

            with col_j2:
                activite = st.text_input("Activité principale", placeholder="Ex: Sortie au parc")

                # Catégories supplémentaires
                categories = st.multiselect(
                    "Catégories",
                    [
                        "Progrès moteur",
                        "Progrès langage",
                        "Santé",
                        "Socialisation",
                        "Alimentation",
                        "Autre",
                    ],
                )

            notes = st.text_area(
                "Notes détaillées",
                height=150,
                placeholder="Décris la journée, les progrès, les moments marquants...",
            )

            submitted = st.form_submit_button("🎯 Enregistrer", type="primary")

            if submitted:
                notes_complete = notes
                if categories:
                    notes_complete += f"\n\nCatégories: {', '.join(categories)}"

                ajouter_entree(jules.id, humeur, sommeil, activite, notes_complete)
                st.success("âœ… Entrée enregistrée dans le journal")
                st.balloons()
                st.rerun()

        st.markdown("---")

        # Liste complète du journal
        st.markdown("### 📅 Historique complet")

        df_journal = charger_entrees_bien_etre(jules.id, limit=100)

        if not df_journal.empty:
            # Filtres
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                filtre_humeur = st.multiselect(
                    "Filtrer par humeur", ["📋 Bien", "📷 Moyen", "📷ž Mal"]
                )

            with col_f2:
                periode = st.selectbox("Période", ["7 derniers jours", "30 derniers jours", "Tout"])

            # Appliquer filtres
            df_filtre = df_journal.copy()

            if filtre_humeur:
                df_filtre = df_filtre[df_filtre["humeur"].isin(filtre_humeur)]

            if periode == "7 derniers jours":
                cutoff = date.today() - timedelta(days=7)
                df_filtre = df_filtre[df_filtre["date"] >= cutoff]
            elif periode == "30 derniers jours":
                cutoff = date.today() - timedelta(days=30)
                df_filtre = df_filtre[df_filtre["date"] >= cutoff]

            # Afficher
            st.dataframe(
                df_filtre[["date", "humeur", "sommeil", "activite", "notes"]],
                use_container_width=True,
                column_config={
                    "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                    "humeur": "Humeur",
                    "sommeil": st.column_config.NumberColumn("Sommeil (h)", format="%.1f"),
                    "activite": "Activité",
                    "notes": st.column_config.TextColumn("Notes", width="large"),
                },
            )

            # Export
            st.markdown("---")
            if st.button("🧹 Exporter le journal (CSV)"):
                csv = df_filtre.to_csv(index=False)
                st.download_button(
                    "Télécharger",
                    csv,
                    f"journal_jules_{date.today().strftime('%Y%m%d')}.csv",
                    "text/csv",
                )
        else:
            st.info("Journal vide. Commence à noter les progrès de Jules !")

    # ===================================
    # TAB 4 : STATISTIQUES
    # ===================================

    with tab4:
        st.subheader("👧 Statistiques et analyses")

        df_stats = charger_entrees_bien_etre(jules.id, limit=90)

        if df_stats.empty:
            st.info("Pas assez de données pour les statistiques")
        else:
            # Métriques globales
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)

            with col_m1:
                st.metric("Entrées totales", len(df_stats))

            with col_m2:
                avg_sleep = df_stats["sommeil"].mean()
                st.metric("Sommeil moyen", f"{format_quantity(avg_sleep)}h")

            with col_m3:
                humeur_bien = len(df_stats[df_stats["humeur"] == "📋 Bien"])
                pct_bien = (humeur_bien / len(df_stats)) * 100
                st.metric('Jours "Bien"', f"{pct_bien:.0f}%")

            with col_m4:
                activites_uniques = df_stats["activite"].nunique()
                st.metric("Activités variées", activites_uniques)

            st.markdown("---")

            # Graphiques
            col_g1, col_g2 = st.columns(2)

            with col_g1:
                st.markdown("### 💰 Ã‰volution du sommeil")
                st.line_chart(df_stats.set_index("date")["sommeil"])

            with col_g2:
                st.markdown("### 📋 Répartition humeur")
                humeur_counts = df_stats["humeur"].value_counts()
                st.bar_chart(humeur_counts)

            # Activités les plus fréquentes
            st.markdown("---")
            st.markdown("### 🎯 Activités favorites")

            top_activites = df_stats["activite"].value_counts().head(10)

            for activite, count in top_activites.items():
                st.write(f"â€¢ **{activite}** : {count} fois")

            # Demander analyse IA
            st.markdown("---")

            if agent and st.button("– Analyse IA des tendances", type="primary"):
                with st.spinner("– Analyse en cours..."):
                    try:
                        # Préparer données
                        donnees_sommeil = [
                            {"date": str(row["date"]), "heures": row["sommeil"]}
                            for _, row in df_stats.iterrows()
                            if pd.notna(row["sommeil"])
                        ]

                        donnees_humeur = [
                            {"date": str(row["date"]), "humeur": row["humeur"]}
                            for _, row in df_stats.iterrows()
                        ]

                        # Appel IA
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        try:
                            analyse = loop.run_until_complete(
                                agent.analyser_bien_etre(donnees_sommeil, donnees_humeur)
                            )
                        finally:
                            loop.close()

                        # Afficher résultats
                        st.success("âœ… Analyse terminée")

                        if "tendances" in analyse:
                            st.info(f"**Tendances :** {analyse['tendances']}")

                        if "recommandations" in analyse:
                            st.markdown("**Recommandations :**")
                            for reco in analyse["recommandations"]:
                                st.write(f"â€¢ {reco}")

                        if "score_bien_etre" in analyse:
                            st.metric("Score bien-être", f"{analyse['score_bien_etre']}/100")

                    except Exception as e:
                        st.error(f"Erreur IA : {e}")

