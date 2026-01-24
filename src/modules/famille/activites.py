"""
Module Activités Familiales - Planning sorties, jeux, moments ensemble
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.core.database import get_db_context
from src.core.models import FamilyActivity


# ===================================
# HELPERS
# ===================================


def charger_activites(statut_filtre: str = None, limit: int = 50) -> pd.DataFrame:
    """Charge les activités familiales"""
    with get_db_context() as db:
        query = db.query(FamilyActivity).order_by(FamilyActivity.date_prevue.desc())

        if statut_filtre:
            query = query.filter(FamilyActivity.statut == statut_filtre)

        activites = query.limit(limit).all()

        return pd.DataFrame(
            [
                {
                    "id": a.id,
                    "titre": a.titre,
                    "description": a.description or "",
                    "type": a.type_activite,
                    "date": a.date_prevue,
                    "duree": a.duree_heures or 0,
                    "lieu": a.lieu or "",
                    "participants": a.qui_participe or [],
                    "cout_estime": a.cout_estime or 0,
                    "cout_reel": a.cout_reel or 0,
                    "statut": a.statut,
                    "notes": a.notes or "",
                }
                for a in activites
            ]
        )


def ajouter_activite(
    titre: str,
    description: str,
    type_activite: str,
    date_prevue: date,
    duree_heures: float = None,
    lieu: str = None,
    qui_participe: list = None,
    cout_estime: float = None,
    notes: str = None,
):
    """Ajoute une nouvelle activité"""
    with get_db_context() as db:
        activite = FamilyActivity(
            titre=titre,
            description=description,
            type_activite=type_activite,
            date_prevue=date_prevue,
            duree_heures=duree_heures,
            lieu=lieu,
            qui_participe=qui_participe,
            cout_estime=cout_estime,
            notes=notes,
        )
        db.add(activite)
        db.commit()


def marquer_terminee(activite_id: int, cout_reel: float = None):
    """Marque une activité comme terminée"""
    with get_db_context() as db:
        activite = db.query(FamilyActivity).filter(FamilyActivity.id == activite_id).first()
        if activite:
            activite.statut = "terminé"
            if cout_reel is not None:
                activite.cout_reel = cout_reel
            db.commit()


def supprimer_activite(activite_id: int):
    """Supprime une activité"""
    with get_db_context() as db:
        activite = db.query(FamilyActivity).filter(FamilyActivity.id == activite_id).first()
        if activite:
            db.delete(activite)
            db.commit()


def get_activites_semaine() -> pd.DataFrame:
    """Retourne les activités de la semaine"""
    today = date.today()
    semaine_fin = today + timedelta(days=7)

    return charger_activites().query(f"date >= @today and date <= @semaine_fin")


def get_budget_activites(mois: int = 1, annee: int = None) -> dict:
    """Calcule le budget activités du mois/année"""
    if annee is None:
        annee = date.today().year

    with get_db_context() as db:
        cutoff_debut = date(annee, mois, 1)
        if mois == 12:
            cutoff_fin = date(annee + 1, 1, 1) - timedelta(days=1)
        else:
            cutoff_fin = date(annee, mois + 1, 1) - timedelta(days=1)

        activites = (
            db.query(FamilyActivity)
            .filter(FamilyActivity.date_prevue >= cutoff_debut)
            .filter(FamilyActivity.date_prevue <= cutoff_fin)
            .all()
        )

        total_estime = sum([a.cout_estime or 0 for a in activites])
        total_reel = sum([a.cout_reel or 0 for a in activites])

        return {
            "total_estime": total_estime,
            "total_reel": total_reel,
            "nb_activites": len(activites),
        }


# Suggestions d'activités par type
SUGGESTIONS_ACTIVITES = {
    "Parc": [
        {
            "titre": "Jeux au parc",
            "description": "Toboggan, balançoire, bac à sable",
            "duree": 1.5,
            "cout": 0,
        },
        {
            "titre": "Pique-nique au parc",
            "description": "Repas en plein air, picnic en famille",
            "duree": 2,
            "cout": 10,
        },
    ],
    "Musée/Culture": [
        {
            "titre": "Musée enfants",
            "description": "Musée adapté aux enfants, découverte",
            "duree": 2,
            "cout": 15,
        },
        {
            "titre": "Zoo/Parc animalier",
            "description": "Découverte animaux, apprentissage",
            "duree": 3,
            "cout": 20,
        },
    ],
    "Piscine/Eau": [
        {
            "titre": "Piscine",
            "description": "Nage, apprentissage aquatique",
            "duree": 1.5,
            "cout": 5,
        },
        {
            "titre": "Plage",
            "description": "Jeux de sable, mer, détente",
            "duree": 4,
            "cout": 0,
        },
    ],
    "Jeu Maison": [
        {
            "titre": "Soirée jeux de société",
            "description": "Jeux en famille, divertissement",
            "duree": 2,
            "cout": 0,
        },
        {
            "titre": "Pyjama party",
            "description": "Film + gâteaux + dodo ensemble",
            "duree": 3,
            "cout": 0,
        },
    ],
    "Sport": [
        {
            "titre": "Foot au parc",
            "description": "Ballon, jeu libre, dépense énergie",
            "duree": 1,
            "cout": 0,
        },
        {
            "titre": "Vélo famille",
            "description": "Balade à vélo, détente active",
            "duree": 1.5,
            "cout": 0,
        },
    ],
    "Autre": [
        {
            "titre": "Sortie shopping",
            "description": "Achats vêtements, jouets, courses",
            "duree": 2,
            "cout": 0,
        },
        {
            "titre": "Restaurant",
            "description": "Manger en famille au restaurant",
            "duree": 1.5,
            "cout": 30,
        },
    ],
}


# ===================================
# MODULE PRINCIPAL
# ===================================


def app():
    """Module Activités Familiales"""

    st.title("🎨 Activités Familiales")
    st.caption("Planning sorties, jeux et moments ensemble")

    st.markdown("---")

    # ===================================
    # TABS
    # ===================================

    tab1, tab2, tab3 = st.tabs(
        ["📅 Planning semaine", "💡 Idées d'activités", "💰 Budget"]
    )

    # ===================================
    # TAB 1 : PLANNING SEMAINE
    # ===================================

    with tab1:
        st.subheader("📅 Cette semaine")

        # Ajouter activité
        with st.expander("➕ Planifier une activité", expanded=False):
            with st.form("form_activite"):
                titre = st.text_input("Nom de l'activité *", placeholder="Ex: Parc dimanche")

                col_a1, col_a2 = st.columns(2)

                with col_a1:
                    type_activite = st.selectbox(
                        "Type d'activité *",
                        ["Parc", "Musée/Culture", "Piscine/Eau", "Jeu Maison", "Sport", "Autre"],
                    )

                    date_activite = st.date_input("Date *", value=date.today())

                    duree = st.number_input("Durée (heures)", 0.5, 12.0, 1.5, 0.5)

                with col_a2:
                    lieu = st.text_input("Lieu", placeholder="Ex: Parc de la ville")

                    qui = st.multiselect(
                        "Qui participe?",
                        ["Jules", "Maman", "Papa", "Famille"],
                        default=["Jules", "Maman", "Papa"],
                    )

                    cout_estime = st.number_input("Coût estimé (€)", 0.0, 1000.0, 0.0)

                description = st.text_area(
                    "Description / Notes",
                    placeholder="Détails, ce qu'on va faire, etc.",
                )

                submitted = st.form_submit_button("📅 Ajouter", type="primary")

                if submitted:
                    if not titre or not type_activite:
                        st.error("Nom et type sont obligatoires")
                    else:
                        ajouter_activite(
                            titre,
                            description or None,
                            type_activite.lower(),
                            date_activite,
                            duree_heures=duree,
                            lieu=lieu or None,
                            qui_participe=qui if qui else None,
                            cout_estime=cout_estime if cout_estime > 0 else None,
                        )
                        st.success(f"✅ Activité '{titre}' planifiée!")
                        st.balloons()
                        st.rerun()

        st.markdown("---")

        # Activités semaine
        df_semaine = get_activites_semaine()

        if df_semaine.empty:
            st.info("Aucune activité planifiée cette semaine. Ajoute-en une! 🎯")
        else:
            st.write(f"**{len(df_semaine)} activités cette semaine**")

            # Grouper par jour
            for jour_unique in sorted(df_semaine["date"].unique()):
                df_jour = df_semaine[df_semaine["date"] == jour_unique]

                jour_str = jour_unique.strftime("%A %d/%m/%Y")
                with st.expander(f"📅 {jour_str} ({len(df_jour)} activité(s))", expanded=True):
                    for _, row in df_jour.iterrows():
                        col_act1, col_act2, col_act3 = st.columns([2, 2, 1])

                        with col_act1:
                            st.markdown(f"**{row['titre']}**")
                            st.caption(f"📍 {row['lieu']}" if row['lieu'] else "")
                            if row["description"]:
                                st.write(row["description"])

                        with col_act2:
                            st.caption(f"⏱️ {row['duree']:.1f}h")
                            if row["cout_estime"] > 0:
                                st.caption(f"💰 {row['cout_estime']:.0f}€")
                            if row["participants"]:
                                st.caption(f"👥 {', '.join(row['participants'])}")

                        with col_act3:
                            if row["statut"] == "planifié":
                                if st.button(
                                    "✅ Terminé", key=f"complete_{row['id']}", use_container_width=True
                                ):
                                    cout = st.number_input(
                                        f"Coût réel ({row['titre']})?",
                                        0.0,
                                        1000.0,
                                        float(row["cout_estime"] or 0),
                                    )
                                    marquer_terminee(row["id"], cout)
                                    st.success("Activité terminée! 🎉")
                                    st.rerun()
                            else:
                                st.caption("✅ Terminé")

    # ===================================
    # TAB 2 : IDÉES D'ACTIVITÉS
    # ===================================

    with tab2:
        st.subheader("💡 Idées d'activités par type")

        st.info("💡 Clique sur une activité pour la planifier")

        # Afficher suggestions par type
        for type_activite, suggestions in SUGGESTIONS_ACTIVITES.items():
            st.markdown(f"### {type_activite}")

            col_sugg1, col_sugg2 = st.columns(2)

            for idx, suggestion in enumerate(suggestions):
                with (col_sugg1 if idx % 2 == 0 else col_sugg2):
                    with st.container(border=True):
                        st.markdown(f"**{suggestion['titre']}**")
                        st.write(suggestion["description"])

                        col_info1, col_info2 = st.columns(2)

                        with col_info1:
                            st.caption(f"⏱️ {suggestion['duree']:.1f}h")

                        with col_info2:
                            if suggestion["cout"] > 0:
                                st.caption(f"💰 ~{suggestion['cout']}€")
                            else:
                                st.caption("💰 Gratuit")

                        if st.button(
                            "📅 Planifier",
                            key=f"plan_{type_activite}_{suggestion['titre']}",
                            use_container_width=True,
                        ):
                            ajouter_activite(
                                suggestion["titre"],
                                suggestion["description"],
                                type_activite.lower(),
                                date.today() + timedelta(days=1),
                                duree_heures=suggestion["duree"],
                                cout_estime=suggestion["cout"] if suggestion["cout"] > 0 else None,
                                qui_participe=["Jules", "Maman", "Papa"],
                            )
                            st.success(f"✅ Activité planifiée!")
                            st.rerun()

    # ===================================
    # TAB 3 : BUDGET
    # ===================================

    with tab3:
        st.subheader("💰 Budget activités")

        # Mois/année
        col_budget1, col_budget2 = st.columns(2)

        with col_budget1:
            mois = st.number_input("Mois", 1, 12, date.today().month)

        with col_budget2:
            annee = st.number_input("Année", 2020, 2100, date.today().year)

        # Calculer budget
        budget = get_budget_activites(mois, annee)

        # Afficher stats
        col_b1, col_b2, col_b3 = st.columns(3)

        with col_b1:
            st.metric("Activités", budget["nb_activites"])

        with col_b2:
            st.metric("Budget estimé", f"{budget['total_estime']:.0f}€")

        with col_b3:
            st.metric("Dépensé réel", f"{budget['total_reel']:.0f}€")

        st.markdown("---")

        # Détail activités du mois
        st.write(f"**Activités {mois}/{annee}**")

        df_mois = charger_activites()

        if not df_mois.empty:
            # Filtrer par mois/année
            df_mois["date"] = pd.to_datetime(df_mois["date"])
            df_mois = df_mois[
                (df_mois["date"].dt.month == mois) & (df_mois["date"].dt.year == annee)
            ]

            if df_mois.empty:
                st.info("Aucune activité ce mois")
            else:
                # Tableau
                df_display = df_mois[["date", "titre", "type", "cout_estime", "cout_reel"]].copy()
                df_display["date"] = pd.to_datetime(df_display["date"]).dt.strftime("%d/%m/%Y")
                df_display.columns = ["Date", "Activité", "Type", "Estimé (€)", "Réel (€)"]

                st.dataframe(df_display, use_container_width=True, hide_index=True)

                # Graphique (simple)
                st.write("**Dépenses par type**")

                df_par_type = df_mois.groupby("type")[["cout_estime", "cout_reel"]].sum()

                st.bar_chart(df_par_type)


if __name__ == "__main__":
    app()
