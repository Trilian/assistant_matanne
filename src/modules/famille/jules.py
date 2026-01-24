"""
Module Jules (19 mois) - Jalons, apprentissages et activités adaptées
"""

from datetime import date

import pandas as pd
import streamlit as st

from src.core.database import get_db_context
from src.core.models import ChildProfile, Milestone, FamilyActivity


# ===================================
# HELPERS
# ===================================


def get_jules_profile() -> ChildProfile:
    """Récupère le profil de Jules"""
    with get_db_context() as db:
        child = db.query(ChildProfile).filter(ChildProfile.name == "Jules").first()

        if not child:
            # Créer le profil si inexistant
            child = ChildProfile(
                name="Jules",
                date_of_birth=date(2024, 6, 22),
                gender="M",
                notes="Notre petit Jules ❤️"
            )
            db.add(child)
            db.commit()
            db.refresh(child)

        return child


def calculer_age(birth_date: date) -> dict:
    """Calcule l'âge en jours, semaines, mois"""
    today = date.today()
    delta = today - birth_date

    jours = delta.days
    semaines = jours // 7
    mois = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)

    if today.day < birth_date.day:
        mois -= 1

    return {"jours": jours, "semaines": semaines, "mois": mois, "annees": mois // 12}


def charger_milestones(child_id: int) -> pd.DataFrame:
    """Charge tous les jalons de Jules"""
    with get_db_context() as db:
        milestones = (
            db.query(Milestone)
            .filter(Milestone.child_id == child_id)
            .order_by(Milestone.date_atteint.desc())
            .all()
        )

        return pd.DataFrame(
            [
                {
                    "id": m.id,
                    "titre": m.titre,
                    "description": m.description or "",
                    "categorie": m.categorie,
                    "date": m.date_atteint,
                    "photo": m.photo_url,
                    "notes": m.notes or "",
                }
                for m in milestones
            ]
        )


def ajouter_milestone(
    child_id: int, titre: str, description: str, categorie: str, date_atteint: date, photo_url: str = None, notes: str = None
):
    """Ajoute un nouveau jalon"""
    with get_db_context() as db:
        milestone = Milestone(
            child_id=child_id,
            titre=titre,
            description=description,
            categorie=categorie,
            date_atteint=date_atteint,
            photo_url=photo_url,
            notes=notes,
        )
        db.add(milestone)
        db.commit()


# Activités recommandées par âge (19 mois)
ACTIVITES_19_MOIS = [
    {
        "titre": "Jeux de ballon",
        "description": "Lancer, attraper, faire rouler. Développe la motricité et la coordination",
        "type": "jeu_moteur",
        "duree": 20,
        "age_min": 18,
    },
    {
        "titre": "Peinture avec doigts",
        "description": "Exploration sensorielle, créativité, développement motricité fine",
        "type": "créatif",
        "duree": 15,
        "age_min": 12,
    },
    {
        "titre": "Musique et danse",
        "description": "Danser, chanter, frapper des objets. Développe l'expression et la coordination",
        "type": "musique",
        "duree": 20,
        "age_min": 12,
    },
    {
        "titre": "Jeux de cachette",
        "description": "Coucou-caché, jeux de chasse. Développe la permanence de l'objet",
        "type": "jeu_cognitif",
        "duree": 15,
        "age_min": 8,
    },
    {
        "titre": "Livres interactifs",
        "description": "Livres tactiles, livres à rabats. Développe le langage et l'intérêt pour la lecture",
        "type": "lecture",
        "duree": 15,
        "age_min": 6,
    },
    {
        "titre": "Jeux d'eau",
        "description": "Versement, éclaboussure, bateaux. Développe motricité et exploration sensorielle",
        "type": "sensoriel",
        "duree": 20,
        "age_min": 12,
    },
    {
        "titre": "Promenades au parc",
        "description": "Explorer la nature, montrer les animaux, laisser explorer",
        "type": "nature",
        "duree": 60,
        "age_min": 0,
    },
    {
        "titre": "Jeux de construction",
        "description": "Blocs, Duplo. Développe la motricité fine et la créativité",
        "type": "construction",
        "duree": 20,
        "age_min": 18,
    },
]


def get_activites_recommandees(age_mois: int) -> list[dict]:
    """Retourne les activités recommandées pour l'âge"""
    return [a for a in ACTIVITES_19_MOIS if a["age_min"] <= age_mois]


def charger_activites_planifiees() -> pd.DataFrame:
    """Charge les activités familiales planifiées"""
    with get_db_context() as db:
        activites = (
            db.query(FamilyActivity)
            .order_by(FamilyActivity.date_prevue.desc())
            .limit(30)
            .all()
        )

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
                    "statut": a.statut,
                    "cout": a.cout_reel or a.cout_estime or 0,
                }
                for a in activites
            ]
        )


def ajouter_activite(titre: str, description: str, type_activite: str, date_prevue: date, **kwargs):
    """Ajoute une nouvelle activité familiale"""
    with get_db_context() as db:
        activite = FamilyActivity(
            titre=titre,
            description=description,
            type_activite=type_activite,
            date_prevue=date_prevue,
            duree_heures=kwargs.get("duree_heures"),
            lieu=kwargs.get("lieu"),
            qui_participe=kwargs.get("qui_participe"),
            age_minimal_recommande=kwargs.get("age_minimal"),
            cout_estime=kwargs.get("cout_estime"),
            notes=kwargs.get("notes"),
        )
        db.add(activite)
        db.commit()


# ===================================
# MODULE PRINCIPAL
# ===================================


def app():
    """Module Jules - Jalons, apprentissages et activités (19 mois)"""

    st.title("👶 Jules - 19 mois")
    st.caption("Jalons, apprentissages et activités adaptées")

    # Récupérer profil Jules
    jules = get_jules_profile()
    age = calculer_age(jules.date_of_birth)

    # ===================================
    # HEADER
    # ===================================

    st.markdown("---")

    col_h1, col_h2, col_h3 = st.columns([2, 1, 1])

    with col_h1:
        st.markdown(f"### 👶 {jules.name}")
        st.caption(f"Né le {jules.date_of_birth.strftime('%d/%m/%Y')}")
        st.write(f"**{age['mois']} mois** ({age['jours']} jours)")

    with col_h2:
        st.metric("Âge", f"{age['mois']}m", f"+{age['jours']} j")

    with col_h3:
        if st.button("📝 Éditer profil"):
            st.info("Édition profil bientôt disponible")

    st.markdown("---")

    # ===================================
    # TABS PRINCIPALES
    # ===================================

    tab1, tab2, tab3 = st.tabs(
        ["📖 Jalons & Apprentissages", "🎮 Activités cette semaine", "🛍️ À acheter"]
    )

    # ===================================
    # TAB 1 : JALONS
    # ===================================

    with tab1:
        st.subheader("📖 Jalons & Apprentissages")

        st.info(
            "💡 Trace les moments importants : premiers mots, premiers pas, nouveaux apprentissages..."
        )

        # Ajouter un jalon
        with st.expander("➕ Ajouter un jalon", expanded=False):
            with st.form("form_milestone"):
                titre = st.text_input("Quoi? *", placeholder="Ex: Premier mot 'maman'")

                col_m1, col_m2 = st.columns(2)

                with col_m1:
                    categorie = st.selectbox(
                        "Catégorie *",
                        ["Langage", "Motricité", "Social", "Cognitif", "Alimentation", "Sommeil", "Autre"],
                    )

                    date_jalon = st.date_input("Date *", value=date.today())

                with col_m2:
                    description = st.text_area(
                        "Détails",
                        placeholder="Description du moment, contexte...",
                        height=100,
                    )

                photo = st.file_uploader("Photo (optionnel)", type=["jpg", "png"])

                notes = st.text_area("Notes", placeholder="Notes supplémentaires...")

                submitted = st.form_submit_button("💾 Sauvegarder", type="primary")

                if submitted:
                    if not titre or not categorie:
                        st.error("Titre et catégorie sont obligatoires")
                    else:
                        photo_url = None
                        # TODO: upload photo si fournie
                        ajouter_milestone(
                            jules.id,
                            titre,
                            description or None,
                            categorie.lower(),
                            date_jalon,
                            photo_url,
                            notes or None,
                        )
                        st.success(f"✅ Jalon '{titre}' enregistré!")
                        st.balloons()
                        st.rerun()

        st.markdown("---")

        # Afficher les jalons
        df_milestones = charger_milestones(jules.id)

        if df_milestones.empty:
            st.info("Aucun jalon encore. Commence à en ajouter ! 📸")
        else:
            # Grouper par catégorie
            for categorie in df_milestones["categorie"].unique():
                df_cat = df_milestones[df_milestones["categorie"] == categorie]

                with st.expander(f"**{categorie.capitalize()}** ({len(df_cat)} jalons)", expanded=True):
                    for _, row in df_cat.iterrows():
                        col_m1, col_m2, col_m3 = st.columns([3, 1, 1])

                        with col_m1:
                            st.markdown(f"**{row['titre']}**")
                            st.caption(f"📅 {row['date'].strftime('%d/%m/%Y')}")
                            if row["description"]:
                                st.write(row["description"])
                            if row["notes"]:
                                st.caption(f"📝 {row['notes']}")

                        with col_m2:
                            if row["photo"]:
                                st.image(row["photo"], use_column_width=True)

                        with col_m3:
                            if st.button("🗑️", key=f"delete_milestone_{row['id']}", help="Supprimer"):
                                # TODO: delete milestone
                                st.success("Supprimé!")

    # ===================================
    # TAB 2 : ACTIVITÉS
    # ===================================

    with tab2:
        st.subheader("🎮 Activités recommandées pour 19 mois")

        activites_recommandees = get_activites_recommandees(age["mois"])

        st.write(f"**{len(activites_recommandees)} activités adaptées à son âge**")

        col_a1, col_a2 = st.columns(2)

        for idx, activite in enumerate(activites_recommandees):
            with (col_a1 if idx % 2 == 0 else col_a2):
                with st.container(border=True):
                    st.markdown(f"### {activite['titre']}")

                    st.write(activite["description"])

                    col_info1, col_info2 = st.columns(2)

                    with col_info1:
                        st.caption(f"⏱️ ~{activite['duree']} min")

                    with col_info2:
                        st.caption(f"📌 {activite['type']}")

                    if st.button(
                        "📅 Planifier",
                        key=f"plan_{idx}",
                        use_container_width=True,
                    ):
                        st.session_state["activite_to_plan"] = activite

        st.markdown("---")

        st.subheader("📅 Activités planifiées")

        df_activites = charger_activites_planifiees()

        if df_activites.empty:
            st.info("Aucune activité planifiée. Commence par en ajouter une ! 🎯")
        else:
            for _, row in df_activites.iterrows():
                col_act1, col_act2 = st.columns([3, 1])

                with col_act1:
                    emoji_statut = "✅" if row["statut"] == "terminé" else "📅"
                    st.write(f"{emoji_statut} **{row['titre']}**")
                    st.caption(f"📅 {row['date'].strftime('%d/%m/%Y')} • 📍 {row['lieu']}")

                with col_act2:
                    if st.button("Marquer terminé", key=f"complete_{row['id']}"):
                        st.success("Activité terminée! 🎉")

    # ===================================
    # TAB 3 : À ACHETER
    # ===================================

    with tab3:
        st.subheader("🛍️ Achats pour Jules")

        st.info("💡 Jouets, vêtements, équipements recommandés pour 19 mois")

        # Catégories d'achat
        categories_achat = {
            "Jouets": [
                "Blocs/Duplo (motricité fine)",
                "Balles molles (jeu moteur)",
                "Livres tactiles (lecture)",
                "Instruments musique (créativité)",
                "Jeux d'eau (sensoriel)",
                "Téléphone jouet (imitation)",
            ],
            "Vêtements": [
                "T-shirts (taille 86-92)",
                "Pantalons (taille 86-92)",
                "Chaussures (pointure 24-26)",
                "Pulls/cardigans",
                "Pyjamas",
            ],
            "Repas": [
                "Assiettes/bols adaptés",
                "Couverts enfant",
                "Gobelet avec bec",
                "Bavoirs",
                "Chaise haute (si pas déjà)",
            ],
        }

        for categorie, articles in categories_achat.items():
            with st.expander(f"📦 {categorie}"):
                for article in articles:
                    col_shop1, col_shop2 = st.columns([3, 1])

                    with col_shop1:
                        st.write(f"• {article}")

                    with col_shop2:
                        if st.button("➕ Courses", key=f"add_courses_{categorie}_{article}"):
                            st.success(f"'{article}' ajouté aux courses! 🛒")


if __name__ == "__main__":
    app()
