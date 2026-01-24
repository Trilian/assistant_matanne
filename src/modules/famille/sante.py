"""
Module Santé & Bien-être - Sport, alimentation saine et objectifs familiaux
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.core.database import get_db_context
from src.core.models import HealthRoutine, HealthObjective, HealthEntry


# ===================================
# HELPERS
# ===================================


def charger_routines_santé() -> pd.DataFrame:
    """Charge toutes les routines de santé actives"""
    with get_db_context() as db:
        routines = (
            db.query(HealthRoutine)
            .filter(HealthRoutine.actif == True)
            .order_by(HealthRoutine.cree_le.desc())
            .all()
        )

        return pd.DataFrame(
            [
                {
                    "id": r.id,
                    "nom": r.nom,
                    "type": r.type_routine,
                    "frequence": r.frequence,
                    "duree": r.duree_minutes,
                    "intensite": r.intensite,
                    "jours": r.jours_semaine or [],
                    "calories": r.calories_brulees_estimees or 0,
                    "description": r.description or "",
                }
                for r in routines
            ]
        )


def ajouter_routine_santé(
    nom: str, type_routine: str, frequence: str, duree_minutes: int, intensite: str = "modérée", **kwargs
):
    """Ajoute une nouvelle routine de santé"""
    with get_db_context() as db:
        routine = HealthRoutine(
            nom=nom,
            description=kwargs.get("description"),
            type_routine=type_routine,
            frequence=frequence,
            duree_minutes=duree_minutes,
            intensite=intensite,
            jours_semaine=kwargs.get("jours_semaine"),
            calories_brulees_estimees=kwargs.get("calories"),
            notes=kwargs.get("notes"),
        )
        db.add(routine)
        db.commit()


def charger_objectifs() -> pd.DataFrame:
    """Charge les objectifs de santé"""
    with get_db_context() as db:
        objectifs = (
            db.query(HealthObjective)
            .filter(HealthObjective.statut == "en_cours")
            .order_by(HealthObjective.priorite)
            .all()
        )

        return pd.DataFrame(
            [
                {
                    "id": o.id,
                    "titre": o.titre,
                    "categorie": o.categorie,
                    "valeur_cible": o.valeur_cible,
                    "valeur_actuelle": o.valeur_actuelle or 0,
                    "unite": o.unite,
                    "priorite": o.priorite,
                    "date_cible": o.date_cible,
                    "progression": (o.valeur_actuelle or 0) / o.valeur_cible * 100
                    if o.valeur_cible > 0
                    else 0,
                    "description": o.description or "",
                }
                for o in objectifs
            ]
        )


def ajouter_objectif(
    titre: str, categorie: str, valeur_cible: float, unite: str, date_cible: date, **kwargs
):
    """Ajoute un nouvel objectif de santé"""
    with get_db_context() as db:
        objectif = HealthObjective(
            titre=titre,
            description=kwargs.get("description"),
            categorie=categorie,
            valeur_cible=valeur_cible,
            unite=unite,
            valeur_actuelle=kwargs.get("valeur_actuelle"),
            date_debut=date.today(),
            date_cible=date_cible,
            priorite=kwargs.get("priorite", "moyenne"),
            notes=kwargs.get("notes"),
        )
        db.add(objectif)
        db.commit()


def charger_entrees_recentes(days: int = 7) -> pd.DataFrame:
    """Charge les entrées de santé des X derniers jours"""
    with get_db_context() as db:
        cutoff = date.today() - timedelta(days=days)

        entries = (
            db.query(HealthEntry)
            .filter(HealthEntry.date >= cutoff)
            .order_by(HealthEntry.date.desc())
            .all()
        )

        return pd.DataFrame(
            [
                {
                    "id": e.id,
                    "date": e.date,
                    "type": e.type_activite,
                    "duree": e.duree_minutes,
                    "intensite": e.intensite or "—",
                    "calories": e.calories_brulees or 0,
                    "energie": e.note_energie or 0,
                    "moral": e.note_moral or 0,
                    "ressenti": e.ressenti or "",
                }
                for e in entries
            ]
        )


def ajouter_entree_sante(
    type_activite: str, duree_minutes: int, date_entree: date = None, **kwargs
):
    """Ajoute une entrée de suivi santé"""
    with get_db_context() as db:
        entry = HealthEntry(
            routine_id=kwargs.get("routine_id"),
            date=date_entree or date.today(),
            type_activite=type_activite,
            duree_minutes=duree_minutes,
            intensite=kwargs.get("intensite"),
            calories_brulees=kwargs.get("calories"),
            note_energie=kwargs.get("note_energie"),
            note_moral=kwargs.get("note_moral"),
            ressenti=kwargs.get("ressenti"),
            notes=kwargs.get("notes"),
        )
        db.add(entry)
        db.commit()


def get_stats_semaine() -> dict:
    """Calcule les stats de la semaine"""
    with get_db_context() as db:
        cutoff = date.today() - timedelta(days=7)

        entries = db.query(HealthEntry).filter(HealthEntry.date >= cutoff).all()

        if not entries:
            return {
                "total_seances": 0,
                "total_minutes": 0,
                "total_calories": 0,
                "energie_moyenne": 0,
                "moral_moyen": 0,
            }

        energie_values = [e.note_energie for e in entries if e.note_energie]
        moral_values = [e.note_moral for e in entries if e.note_moral]

        return {
            "total_seances": len(entries),
            "total_minutes": sum([e.duree_minutes for e in entries]),
            "total_calories": sum([e.calories_brulees or 0 for e in entries]),
            "energie_moyenne": sum(energie_values) / len(energie_values) if energie_values else 0,
            "moral_moyen": sum(moral_values) / len(moral_values) if moral_values else 0,
        }


# ===================================
# MODULE PRINCIPAL
# ===================================


def app():
    """Module Santé & Bien-être - Sport et alimentation"""

    st.title("💪 Santé & Bien-être")
    st.caption("Sport, alimentation saine et objectifs familiaux")

    st.markdown("---")

    # ===================================
    # STATS SEMAINE
    # ===================================

    stats = get_stats_semaine()

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)

    with col_s1:
        st.metric("Séances", stats["total_seances"], "cette semaine")

    with col_s2:
        st.metric("Minutes", stats["total_minutes"], f"total")

    with col_s3:
        st.metric("Calories", int(stats["total_calories"]), "brûlées")

    with col_s4:
        st.metric("Moral", f"{stats['moral_moyen']:.1f}/10", "moyenne")

    st.markdown("---")

    # ===================================
    # TABS
    # ===================================

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🏃 Routines Sport", "🎯 Objectifs", "📊 Suivi", "🍎 Alimentation"]
    )

    # ===================================
    # TAB 1 : ROUTINES SPORT
    # ===================================

    with tab1:
        st.subheader("🏃 Routines de sport")

        st.info("💡 Crée des routines de sport régulières (3x/semaine, quotidien, etc.)")

        # Ajouter une routine
        with st.expander("➕ Nouvelle routine", expanded=False):
            with st.form("form_routine"):
                nom = st.text_input("Nom de la routine *", placeholder="Ex: Yoga le matin")

                col_r1, col_r2 = st.columns(2)

                with col_r1:
                    type_routine = st.selectbox(
                        "Type de sport *",
                        ["Yoga", "Gym", "Course", "Marche", "Natation", "Vélo", "HIIT", "Autre"],
                    )

                    frequence = st.text_input(
                        "Fréquence *", placeholder="Ex: 3x/semaine ou quotidien"
                    )

                    duree = st.number_input("Durée (minutes) *", 5, 180, 30)

                with col_r2:
                    intensite = st.selectbox(
                        "Intensité", ["Basse", "Modérée", "Haute"], index=1
                    )

                    jours = st.multiselect(
                        "Jours",
                        ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
                    )

                    calories = st.number_input("Calories estimées (optionnel)", 0, 1000, 0)

                description = st.text_area(
                    "Description", placeholder="Détails de la routine..."
                )

                submitted = st.form_submit_button("💾 Créer", type="primary")

                if submitted:
                    if not nom or not type_routine or not frequence:
                        st.error("Nom, type et fréquence sont obligatoires")
                    else:
                        ajouter_routine_santé(
                            nom,
                            type_routine.lower(),
                            frequence,
                            duree,
                            intensite.lower(),
                            jours_semaine=[j.lower() for j in jours] if jours else None,
                            calories=calories or None,
                            description=description or None,
                        )
                        st.success(f"✅ Routine '{nom}' créée!")
                        st.balloons()
                        st.rerun()

        st.markdown("---")

        # Afficher routines actives
        df_routines = charger_routines_santé()

        if df_routines.empty:
            st.info("Aucune routine de sport. Crée ta première! 🏃")
        else:
            for _, row in df_routines.iterrows():
                with st.container(border=True):
                    col_r1, col_r2, col_r3 = st.columns([2, 2, 1])

                    with col_r1:
                        st.markdown(f"### {row['nom']}")
                        st.caption(f"🏋️ {row['type'].capitalize()}")
                        if row["description"]:
                            st.write(row["description"])

                    with col_r2:
                        st.caption(f"📅 {row['frequence']}")
                        st.caption(f"⏱️ {row['duree']} min")
                        st.caption(f"💪 {row['intensite'].capitalize()}")
                        if row["calories"] > 0:
                            st.caption(f"🔥 ~{row['calories']} cal")

                    with col_r3:
                        col_r3a, col_r3b = st.columns(2)
                        with col_r3a:
                            if st.button("✅ Fait", key=f"done_{row['id']}", use_container_width=True):
                                ajouter_entree_sante(
                                    row["type"],
                                    row["duree"],
                                    intensite=row["intensite"],
                                    calories=row["calories"] if row["calories"] > 0 else None,
                                )
                                st.success("Séance enregistrée! 💪")
                                st.rerun()

                        with col_r3b:
                            if st.button("🗑️", key=f"del_{row['id']}", use_container_width=True):
                                st.info("Suppression bientôt")

    # ===================================
    # TAB 2 : OBJECTIFS
    # ===================================

    with tab2:
        st.subheader("🎯 Objectifs santé")

        st.info("💡 Fixe-toi des objectifs: perte poids, endurance, etc.")

        # Ajouter objectif
        with st.expander("➕ Nouvel objectif", expanded=False):
            with st.form("form_objectif"):
                titre = st.text_input("Objectif *", placeholder="Ex: Courir 5km")

                col_o1, col_o2 = st.columns(2)

                with col_o1:
                    categorie = st.selectbox(
                        "Catégorie *",
                        [
                            "Poids",
                            "Endurance",
                            "Force",
                            "Flexibilité",
                            "Alimentation",
                            "Énergie",
                            "Autre",
                        ],
                    )

                    valeur_cible = st.number_input(
                        "Valeur cible *", 0.0, 999.0, 5.0
                    )

                    unite = st.selectbox(
                        "Unité *", ["kg", "km", "reps", "min", "jours/semaine", "litres"]
                    )

                with col_o2:
                    valeur_actuelle = st.number_input("Valeur actuelle (optionnel)", 0.0)

                    date_cible = st.date_input("Date cible *")

                    priorite = st.selectbox(
                        "Priorité", ["Basse", "Moyenne", "Haute"], index=1
                    )

                description = st.text_area(
                    "Description", placeholder="Pourquoi cet objectif?"
                )

                submitted = st.form_submit_button("💾 Créer", type="primary")

                if submitted:
                    if not titre or not categorie or not valeur_cible or not date_cible:
                        st.error("Titre, catégorie, valeur et date sont obligatoires")
                    else:
                        ajouter_objectif(
                            titre,
                            categorie.lower(),
                            valeur_cible,
                            unite,
                            date_cible,
                            valeur_actuelle=valeur_actuelle if valeur_actuelle > 0 else None,
                            priorite=priorite.lower(),
                            description=description or None,
                        )
                        st.success(f"✅ Objectif '{titre}' créé!")
                        st.balloons()
                        st.rerun()

        st.markdown("---")

        # Afficher objectifs
        df_objectifs = charger_objectifs()

        if df_objectifs.empty:
            st.info("Aucun objectif. Crée-en un! 🎯")
        else:
            for _, row in df_objectifs.iterrows():
                with st.container(border=True):
                    col_o1, col_o2, col_o3 = st.columns([2, 2, 1])

                    with col_o1:
                        st.markdown(f"### {row['titre']}")
                        st.caption(f"📌 {row['categorie'].capitalize()}")
                        if row["description"]:
                            st.write(row["description"])

                    with col_o2:
                        progress = min(row["progression"] / 100, 1.0)
                        st.progress(progress)
                        st.caption(
                            f"{row['valeur_actuelle']:.1f}/{row['valeur_cible']} {row['unite']}"
                        )
                        st.caption(
                            f"📅 Avant {row['date_cible'].strftime('%d/%m/%Y')}"
                        )

                    with col_o3:
                        # Badge priorité
                        if row["priorite"] == "haute":
                            st.markdown("🔴 Haute")
                        elif row["priorite"] == "moyenne":
                            st.markdown("🟡 Moyenne")
                        else:
                            st.markdown("🟢 Basse")

                        # Bouton mise à jour
                        if st.button(
                            "📈 Mettre à jour", key=f"update_{row['id']}", use_container_width=True
                        ):
                            st.info("Mise à jour bientôt")

    # ===================================
    # TAB 3 : SUIVI
    # ===================================

    with tab3:
        st.subheader("📊 Suivi des séances")

        df_entries = charger_entrees_recentes(days=30)

        if df_entries.empty:
            st.info("Aucune séance enregistrée. Commence par une! 🏃")
        else:
            # Stats
            col_stat1, col_stat2, col_stat3 = st.columns(3)

            with col_stat1:
                st.metric("Séances (30j)", len(df_entries))

            with col_stat2:
                st.metric("Minutes (30j)", df_entries["duree"].sum())

            with col_stat3:
                if len(df_entries) > 0:
                    energie_mean = df_entries[df_entries["energie"] > 0]["energie"].mean()
                    st.metric(
                        "Énergie moy", f"{energie_mean:.1f}/10" if energie_mean > 0 else "—"
                    )

            st.markdown("---")

            # Tableau
            st.write("**Détail des 30 derniers jours**")

            df_display = df_entries[["date", "type", "duree", "intensite", "calories"]].copy()
            df_display["date"] = pd.to_datetime(df_display["date"]).dt.strftime("%d/%m/%Y")

            st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ===================================
    # TAB 4 : ALIMENTATION SAINE
    # ===================================

    with tab4:
        st.subheader("🍎 Alimentation saine")

        st.info(
            "💡 Couplée avec le planning repas : recettes saines adaptées à votre nutrition"
        )

        # Principes simples
        col_nutri1, col_nutri2 = st.columns(2)

        with col_nutri1:
            st.markdown("### ✅ À manger régulièrement")
            suggestions_bonnes = [
                "🥗 Légumes variés (couleurs)",
                "🍎 Fruits frais",
                "🥚 Œufs (protéines)",
                "🐟 Poissons gras (oméga-3)",
                "🥜 Fruits secs/noix",
                "🥛 Produits laitiers",
                "🌾 Céréales complètes",
            ]
            for item in suggestions_bonnes:
                st.write(item)

        with col_nutri2:
            st.markdown("### ⚠️ À modérer")
            suggestions_moderation = [
                "🍟 Sucres raffinés",
                "🧂 Trop de sel",
                "🍕 Plats gras/lourds",
                "🥤 Sodas",
                "🍰 Gâteaux industriels",
                "🧈 Beurre excessif",
            ]
            for item in suggestions_moderation:
                st.write(item)

        st.markdown("---")

        st.markdown("### 🔗 Lien avec le planning repas")

        st.info(
            "📋 Consulte le module **Cuisine** pour des recettes saines et équilibrées adaptées à vos objectifs."
        )

        col_recipe1, col_recipe2 = st.columns(2)

        with col_recipe1:
            if st.button("🍽️ Voir recettes saines", use_container_width=True):
                st.write("Redirection vers le module Cuisine (filtré 'équilibré')")

        with col_recipe2:
            if st.button("📅 Planifier une semaine saine", use_container_width=True):
                st.write("Redirection vers le module Planning")


if __name__ == "__main__":
    app()
