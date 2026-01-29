"""
Module Bien-être avec Agent IA intégré
Suivi du bien-être familial avec analyses intelligentes
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
from src.domains.famille.logic.bien_etre_logic import (
    calculer_score_bien_etre,
    analyser_tendances_bien_etre
)

# ===================================
# HELPERS
# ===================================


def charger_entrees_famille(limit: int = 30) -> pd.DataFrame:
    """Charge toutes les entrées de bien-être (enfants + adultes)"""
    with get_db_context() as db:
        entries = db.query(WellbeingEntry).order_by(WellbeingEntry.date.desc()).limit(limit).all()

        return pd.DataFrame(
            [
                {
                    "id": e.id,
                    "date": e.date,
                    "personne": (
                        db.query(ChildProfile).get(e.child_id).name if e.child_id else e.username
                    ),
                    "humeur": e.mood,
                    "sommeil": e.sleep_hours,
                    "activite": e.activity,
                    "notes": e.notes or "",
                    "is_child": e.child_id is not None,
                }
                for e in entries
            ]
        )


def ajouter_entree_adulte(username: str, humeur: str, sommeil: float, activite: str, notes: str):
    """Ajoute une entrée pour un adulte"""
    with get_db_context() as db:
        entry = WellbeingEntry(
            child_id=None,
            username=username,
            date=date.today(),
            mood=humeur,
            sleep_hours=sommeil,
            activity=activite,
            notes=notes,
        )
        db.add(entry)
        db.commit()


def get_statistiques_globales() -> dict:
    """Calcule les statistiques globales du bien-être familial"""
    with get_db_context() as db:
        # 7 derniers jours
        cutoff = date.today() - timedelta(days=7)

        entries = db.query(WellbeingEntry).filter(WellbeingEntry.date >= cutoff).all()

        if not entries:
            return {"total_entries": 0, "avg_sleep": 0, "pct_bien": 0, "activites_count": 0}

        total = len(entries)
        avg_sleep = (
            sum([e.sleep_hours for e in entries if e.sleep_hours]) / total if total > 0 else 0
        )
        bien_count = len([e for e in entries if "Bien" in e.mood])
        pct_bien = (bien_count / total) * 100 if total > 0 else 0
        activites = len(set([e.activity for e in entries if e.activity]))

        return {
            "total_entries": total,
            "avg_sleep": avg_sleep,
            "pct_bien": pct_bien,
            "activites_count": activites,
        }


def detecter_alertes() -> list[dict]:
    """Détecte les alertes de bien-être"""
    alertes = []

    with get_db_context() as db:
        # Dernières 7 entrées par personne
        cutoff = date.today() - timedelta(days=7)

        entries = db.query(WellbeingEntry).filter(WellbeingEntry.date >= cutoff).all()

        # Grouper par personne
        personnes = {}
        for e in entries:
            key = e.username or (
                db.query(ChildProfile).get(e.child_id).name if e.child_id else "Inconnu"
            )
            if key not in personnes:
                personnes[key] = []
            personnes[key].append(e)

        # Analyser chaque personne
        for personne, entrees in personnes.items():
            # Mauvaise humeur répétée
            mauvaise_humeur = [e for e in entrees if "Mal" in e.mood]
            if len(mauvaise_humeur) >= 3:
                alertes.append(
                    {
                        "type": "ATTENTION",
                        "personne": personne,
                        "message": f"Humeur basse répétée ({len(mauvaise_humeur)}/7 jours)",
                        "action": "Consulter un professionnel si persistant",
                    }
                )

            # Sommeil insuffisant
            sommeils = [e.sleep_hours for e in entrees if e.sleep_hours]
            if sommeils:
                avg_sleep = sum(sommeils) / len(sommeils)
                if avg_sleep < 6.0:
                    alertes.append(
                        {
                            "type": "INFO",
                            "personne": personne,
                            "message": f"Sommeil moyen bas : {format_quantity(avg_sleep)}h/nuit",
                            "action": "Améliorer l'hygiène de sommeil",
                        }
                    )

    return alertes


# ===================================
# MODULE PRINCIPAL
# ===================================


def app():
    """Module Bien-être familial avec IA intégrée"""

    st.title("ðŸ’š Bien-être Familial")
    st.caption("Suivi et analyses du bien-être de toute la famille")

    # Récupérer l'agent IA
    agent: AgentIA = st.session_state.get("agent_ia")

    # ===================================
    # STATISTIQUES GLOBALES
    # ===================================

    stats = get_statistiques_globales()

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    with col_s1:
        st.metric("Entrées (7j)", stats["total_entries"])

    with col_s2:
        st.metric("Sommeil moyen", f"{format_quantity(stats['avg_sleep'])}h")

    with col_s3:
        st.metric('Jours "Bien"', f"{stats['pct_bien']:.0f}%")

    with col_s4:
        st.metric("Activités variées", stats["activites_count"])

    st.markdown("---")

    # ===================================
    # ALERTES
    # ===================================

    alertes = detecter_alertes()

    if alertes:
        st.markdown("### ðŸš¨ Points d'attention")

        for alerte in alertes:
            if alerte["type"] == "ATTENTION":
                st.warning(
                    f"âš ï¸ **{alerte['personne']}** : {alerte['message']}\n\nðŸ’¡ {alerte['action']}"
                )
            else:
                st.info(
                    f"â„¹ï¸ **{alerte['personne']}** : {alerte['message']}\n\nðŸ’¡ {alerte['action']}"
                )

        st.markdown("---")

    # ===================================
    # TABS PRINCIPAUX
    # ===================================

    tab1, tab2, tab3, tab4 = st.tabs(
        ["ðŸ“Š Vue d'ensemble", "âž• Ajouter une entrée", "ðŸ¤– Analyse IA", "ðŸ“ˆ Tendances"]
    )

    # ===================================
    # TAB 1 : VUE D'ENSEMBLE
    # ===================================

    with tab1:
        st.subheader("Bien-être de la famille")

        df = charger_entrees_famille(limit=30)

        if df.empty:
            st.info("Aucune donnée de bien-être. Commence à suivre votre quotidien !")
        else:
            # Sélecteur de personne
            col_f1, col_f2 = st.columns([2, 1])

            with col_f1:
                personnes = ["Tous"] + sorted(df["personne"].unique().tolist())
                personne_filtre = st.selectbox("Filtrer par personne", personnes)

            with col_f2:
                periode = st.selectbox("Période", ["7 jours", "30 jours", "Tout"])

            # Appliquer filtres
            df_filtre = df.copy()

            if personne_filtre != "Tous":
                df_filtre = df_filtre[df_filtre["personne"] == personne_filtre]

            if periode == "7 jours":
                cutoff = date.today() - timedelta(days=7)
                df_filtre = df_filtre[df_filtre["date"] >= cutoff]
            elif periode == "30 jours":
                cutoff = date.today() - timedelta(days=30)
                df_filtre = df_filtre[df_filtre["date"] >= cutoff]

            # Affichage
            if not df_filtre.empty:
                # Graphiques
                col_g1, col_g2 = st.columns(2)

                with col_g1:
                    st.markdown("**ðŸ˜´ Sommeil**")
                    st.line_chart(df_filtre.set_index("date")["sommeil"])

                with col_g2:
                    st.markdown("**ðŸ˜Š Humeur**")
                    humeur_counts = df_filtre["humeur"].value_counts()
                    st.bar_chart(humeur_counts)

                st.markdown("---")

                # Liste des entrées
                st.dataframe(
                    df_filtre[["date", "personne", "humeur", "sommeil", "activite", "notes"]],
                    use_container_width=True,
                    column_config={
                        "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                        "personne": "Personne",
                        "humeur": "Humeur",
                        "sommeil": st.column_config.NumberColumn("Sommeil (h)", format="%.1f"),
                        "activite": "Activité",
                        "notes": st.column_config.TextColumn("Notes", width="large"),
                    },
                )
            else:
                st.info("Aucune donnée pour cette période")

    # ===================================
    # TAB 2 : AJOUTER ENTRÃ‰E
    # ===================================

    with tab2:
        st.subheader("âž• Ajouter une entrée de bien-être")

        with st.form("form_bien_etre"):
            col_a1, col_a2 = st.columns(2)

            with col_a1:
                personne = st.text_input("Pour qui ? *", value="Anne", placeholder="Prénom")

                humeur = st.selectbox("Humeur *", ["ðŸ˜Š Bien", "ðŸ˜ Moyen", "ðŸ˜ž Mal"])

                sommeil = st.number_input("Heures de sommeil", 0.0, 24.0, 7.5, 0.5)

            with col_a2:
                _date_entry = st.date_input("Date", value=date.today())

                activite = st.text_input(
                    "Activité principale", placeholder="Ex: Travail, Sport, Repos..."
                )

                stress_level = st.slider("Niveau de stress", 0, 10, 5)

                notes = st.text_area(
                "Notes / Ressenti",
                height=150,
                placeholder="Comment s'est passée ta journée ? Des préoccupations ? Des moments positifs ?",
            )

            # Ajouter le stress aux notes
            notes_complete = notes
            if stress_level:
                notes_complete += f"\n\nNiveau de stress : {stress_level}/10"

            submitted = st.form_submit_button("ðŸ’¾ Enregistrer", type="primary")

            if submitted:
                if not personne:
                    st.error("Le prénom est obligatoire")
                else:
                    ajouter_entree_adulte(personne, humeur, sommeil, activite, notes_complete)
                    st.success(f"âœ… Entrée enregistrée pour {personne}")
                    st.balloons()
                    st.rerun()

        st.markdown("---")

        # Suggestions IA
        st.markdown("### ðŸ’¡ Suggestions pour améliorer le bien-être")

        suggestions_base = [
            "ðŸƒ Activité physique régulière (30 min/jour)",
            "ðŸ§˜ Méditation ou respiration (10 min/jour)",
            "ðŸ’¤ Routine de sommeil stable (même horaires)",
            "ðŸ‘¥ Temps de qualité en famille",
            "ðŸ“µ Moments sans écrans",
            "ðŸŽ¨ Activité créative ou hobby",
            "ðŸŒ³ Temps dans la nature",
            "ðŸ“– Lecture relaxante",
        ]

        for sugg in suggestions_base[:4]:
            st.info(sugg)

    # ===================================
    # TAB 3 : ANALYSE IA
    # ===================================

    with tab3:
        st.subheader("ðŸ¤– Analyse intelligente du bien-être")

        if not agent:
            st.error("Agent IA non disponible")
        else:
            st.info("ðŸ’¡ L'IA analyse les tendances et donne des recommandations personnalisées")

            # Sélection personne
            df_analyse = charger_entrees_famille(limit=30)

            if not df_analyse.empty:
                personnes_dispo = ["Toute la famille"] + sorted(
                    df_analyse["personne"].unique().tolist()
                )
                personne_analyse = st.selectbox("Analyser pour", personnes_dispo)

                if st.button("ðŸ¤– Lancer l'analyse", type="primary", use_container_width=True):
                    with st.spinner("ðŸ¤– Analyse en cours..."):
                        try:
                            # Filtrer données
                            if personne_analyse != "Toute la famille":
                                df_analyse = df_analyse[df_analyse["personne"] == personne_analyse]

                            # Préparer données
                            donnees_sommeil = [
                                {"date": str(row["date"]), "heures": row["sommeil"]}
                                for _, row in df_analyse.iterrows()
                                if pd.notna(row["sommeil"])
                            ]

                            donnees_humeur = [
                                {"date": str(row["date"]), "humeur": row["humeur"]}
                                for _, row in df_analyse.iterrows()
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

                            st.session_state["analyse_bien_etre"] = analyse
                            st.success("âœ… Analyse terminée")

                        except Exception as e:
                            st.error(f"Erreur IA : {e}")

                # Afficher résultats
                if "analyse_bien_etre" in st.session_state:
                    analyse = st.session_state["analyse_bien_etre"]

                    st.markdown("---")
                    st.markdown("### ðŸ“Š Résultats de l'analyse")

                    # Score
                    if "score_bien_etre" in analyse:
                        col_score1, col_score2, col_score3 = st.columns([1, 2, 1])

                        with col_score2:
                            score = analyse["score_bien_etre"]

                            if score >= 80:
                                _color = "green"
                                emoji = "ðŸ˜Š"
                                msg = "Excellent"
                            elif score >= 60:
                                _color = "orange"
                                emoji = "ðŸ˜"
                                msg = "Correct"
                            else:
                                _color = "red"
                                emoji = "ðŸ˜ž"
                                msg = "Ã€ améliorer"

                            st.markdown(
                                f"""
                                <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;'>
                                    <h1 style='font-size: 4rem; margin: 0;'>{emoji}</h1>
                                    <h2 style='margin: 0.5rem 0;'>{score}/100</h2>
                                    <p style='margin: 0; font-size: 1.2rem;'>{msg}</p>
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )

                    st.markdown("---")

                    # Tendances
                    if "tendances" in analyse:
                        st.markdown("### ðŸ“ˆ Tendances observées")
                        st.info(analyse["tendances"])

                    # Recommandations
                    if "recommandations" in analyse:
                        st.markdown("### ðŸ’¡ Recommandations personnalisées")

                        for i, reco in enumerate(analyse["recommandations"], 1):
                            st.success(f"{i}. {reco}")

                    # Bouton reset
                    if st.button("ðŸ”„ Nouvelle analyse"):
                        del st.session_state["analyse_bien_etre"]
                        st.rerun()
            else:
                st.warning("Pas assez de données pour une analyse. Ajoute des entrées d'abord !")

    # ===================================
    # TAB 4 : TENDANCES
    # ===================================

    with tab4:
        st.subheader("ðŸ“ˆ Tendances à long terme")

        df_tendances = charger_entrees_famille(limit=90)

        if df_tendances.empty:
            st.info("Pas assez de données pour les tendances")
        else:
            # Métriques
            col_t1, col_t2, col_t3 = st.columns(3)

            with col_t1:
                st.metric("Période analysée", f"{len(df_tendances)} jours")

            with col_t2:
                membres = df_tendances["personne"].nunique()
                st.metric("Membres suivis", membres)

            with col_t3:
                avg_entries = len(df_tendances) / 90
                st.metric("Entrées/jour", f"{format_quantity(avg_entries)}")

            st.markdown("---")

            # Ã‰volution du sommeil
            st.markdown("### ðŸ˜´ Ã‰volution du sommeil (90 jours)")

            # Par personne
            for personne in df_tendances["personne"].unique():
                df_p = df_tendances[df_tendances["personne"] == personne]

                st.markdown(f"**{personne}**")
                st.line_chart(df_p.set_index("date")["sommeil"])

            st.markdown("---")

            # Répartition humeur
            st.markdown("### ðŸ˜Š Répartition de l'humeur")

            col_h1, col_h2 = st.columns(2)

            with col_h1:
                humeur_global = df_tendances["humeur"].value_counts()
                st.bar_chart(humeur_global)

            with col_h2:
                st.markdown("**Par personne**")
                for personne in df_tendances["personne"].unique():
                    df_p = df_tendances[df_tendances["personne"] == personne]
                    bien = len(df_p[df_p["humeur"] == "ðŸ˜Š Bien"])
                    total = len(df_p)
                    pct = (bien / total) * 100 if total > 0 else 0

                    st.write(f"â€¢ **{personne}** : {pct:.0f}% bien")

            # Export
            st.markdown("---")
            if st.button("ðŸ“¤ Exporter les données (CSV)"):
                csv = df_tendances.to_csv(index=False)
                st.download_button(
                    "Télécharger",
                    csv,
                    f"bien_etre_famille_{date.today().strftime('%Y%m%d')}.csv",
                    "text/csv",
                )

