"""
Onglets du module Projets Maison.

Chaque onglet est une fonction recevant un KeyNamespace pour éviter
les collisions de clés widget Streamlit.
"""

import asyncio
import logging
from datetime import date, timedelta

import streamlit as st

from src.core.decorators import avec_session_db
from src.core.models import Project, ProjectTask
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

CATEGORIES = [
    "travaux",
    "renovation",
    "amenagement",
    "reparation",
    "decoration",
    "jardin",
    "exterieur",
]

PRIORITES = ["haute", "moyenne", "basse"]

STATUTS = ["en_cours", "termine", "annule"]

CATEGORY_ICONS = {
    "travaux": "🔨",
    "renovation": "🏠",
    "amenagement": "🛋️",
    "reparation": "🔧",
    "decoration": "🎨",
    "jardin": "🌿",
    "exterieur": "🏡",
}


# ═══════════════════════════════════════════════════════════
# ONGLET LISTE
# ═══════════════════════════════════════════════════════════


def onglet_liste(keys: KeyNamespace):
    """Affiche la liste des projets existants avec filtres."""
    from src.services.maison import get_projets_service

    service = get_projets_service()

    # Filtres
    col_filtre1, col_filtre2 = st.columns(2)
    with col_filtre1:
        filtre_statut = st.selectbox(
            "Statut",
            ["Tous", "en_cours", "termine", "annule"],
            key=keys("filtre_statut"),
        )
    with col_filtre2:
        filtre_priorite = st.selectbox(
            "Priorité",
            ["Toutes", "haute", "moyenne", "basse"],
            key=keys("filtre_priorite"),
        )

    # Charger les projets
    statut = filtre_statut if filtre_statut != "Tous" else None
    projets = service.obtenir_projets(statut=statut)

    # Filtre priorité local
    if filtre_priorite != "Toutes":
        projets = [p for p in projets if p.priorite == filtre_priorite]

    if not projets:
        st.info("Aucun projet trouvé. Créez votre premier projet dans l'onglet '➕ Nouveau Projet'.")
        return

    st.markdown(f"**{len(projets)} projet(s)**")

    for projet in projets:
        icon = CATEGORY_ICONS.get(getattr(projet, "description", "")[:20], "🏗️")
        _afficher_projet_card(projet, keys, icon)


def _afficher_projet_card(projet: Project, keys: KeyNamespace, icon: str = "🏗️"):
    """Affiche une carte de projet."""
    with st.container(border=True):
        col_info, col_actions = st.columns([3, 1])

        with col_info:
            st.markdown(f"### {icon} {projet.nom}")
            if projet.description:
                st.caption(projet.description[:100])

            # Badges
            priorite_class = f"badge-{projet.priorite}"
            statut_class = f"badge-{projet.statut}"
            st.markdown(
                f'<span class="projet-badge {priorite_class}">{projet.priorite}</span> '
                f'<span class="projet-badge {statut_class}">{projet.statut}</span>',
                unsafe_allow_html=True,
            )

            # Dates
            dates_parts = []
            if projet.date_debut:
                dates_parts.append(f"Début: {projet.date_debut.strftime('%d/%m/%Y')}")
            if projet.date_fin_prevue:
                dates_parts.append(f"Fin prévue: {projet.date_fin_prevue.strftime('%d/%m/%Y')}")
            if dates_parts:
                st.caption(" | ".join(dates_parts))

        with col_actions:
            # Boutons d'action
            if projet.statut == "en_cours":
                if st.button("✅ Terminer", key=keys(f"terminer_{projet.id}")):
                    _terminer_projet(projet.id)
                    st.rerun()

            if st.button("🗑️ Supprimer", key=keys(f"supprimer_{projet.id}")):
                _supprimer_projet(projet.id)
                st.rerun()

        # Tâches du projet
        if projet.tasks:
            with st.expander(f"📝 {len(projet.tasks)} tâche(s)", expanded=False):
                for tache in sorted(projet.tasks, key=lambda t: t.ordre if t.ordre else 0):
                    done = tache.statut == "termine"
                    prefix = "✅" if done else "⬜"
                    st.markdown(f"{prefix} **{tache.nom}** — {tache.description or ''}")


# ═══════════════════════════════════════════════════════════
# ONGLET CRÉATION
# ═══════════════════════════════════════════════════════════


def onglet_creation(keys: KeyNamespace):
    """Formulaire de création de projet avec estimation IA."""
    st.subheader("Créer un nouveau projet")

    with st.form(key=keys("form_nouveau_projet")):
        nom = st.text_input("Nom du projet *", placeholder="ex: Repeindre la chambre")
        description = st.text_area(
            "Description détaillée",
            placeholder="ex: Chambre de 15m², 2 couches de peinture, murs + plafond",
        )
        col1, col2 = st.columns(2)
        with col1:
            categorie = st.selectbox("Catégorie", CATEGORIES, key=keys("categorie_nouveau"))
        with col2:
            priorite = st.selectbox("Priorité", PRIORITES, index=1, key=keys("priorite_nouveau"))

        col3, col4 = st.columns(2)
        with col3:
            date_debut = st.date_input("Date de début", value=date.today(), key=keys("date_debut"))
        with col4:
            date_fin = st.date_input(
                "Date de fin prévue",
                value=date.today() + timedelta(days=30),
                key=keys("date_fin"),
            )

        estimation_ia = st.checkbox(
            "🤖 Estimation IA (budget, matériaux, tâches)", value=True
        )
        submitted = st.form_submit_button("🏗️ Créer le projet", use_container_width=True)

    if submitted and nom:
        with st.spinner("Création du projet en cours..."):
            projet = _creer_projet(
                nom=nom,
                description=description,
                categorie=categorie,
                priorite=priorite,
                date_debut=date_debut,
                date_fin_prevue=date_fin,
            )
            if projet:
                st.success(f"✅ Projet **{nom}** créé avec succès !")

                # Estimation IA optionnelle
                if estimation_ia and description:
                    _afficher_estimation_ia(nom, description, categorie)
            else:
                st.error("Erreur lors de la création du projet.")
    elif submitted:
        st.warning("Le nom du projet est obligatoire.")


def _afficher_estimation_ia(nom: str, description: str, categorie: str):
    """Affiche l'estimation IA pour un projet."""
    from src.services.maison import get_projets_service

    service = get_projets_service()

    with st.spinner("🤖 Estimation IA en cours..."):
        try:
            estimation = asyncio.run(
                service.estimer_projet(nom, description, categorie)
            )

            st.divider()
            st.subheader("📊 Estimation IA")

            # Budget
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                st.metric("Budget min", f"{estimation.budget_estime_min}€")
            with col_b2:
                st.metric("Budget max", f"{estimation.budget_estime_max}€")
            with col_b3:
                st.metric("Durée estimée", f"{estimation.duree_estimee_jours} jour(s)")

            # Matériaux
            if estimation.materiels_necessaires:
                st.markdown("#### 🛒 Matériaux nécessaires")
                for mat in estimation.materiels_necessaires:
                    prix_txt = f" — {mat.prix_estime}€" if mat.prix_estime else ""
                    magasin_txt = f" ({mat.magasin_suggere})" if mat.magasin_suggere else ""
                    st.markdown(f"- **{mat.nom}** x{mat.quantite}{prix_txt}{magasin_txt}")
                    if mat.alternatif_eco:
                        st.caption(f"  💡 Alternative éco: {mat.alternatif_eco}")

            # Tâches suggérées
            if estimation.taches_suggerees:
                st.markdown("#### 📝 Tâches suggérées")
                for tache in estimation.taches_suggerees:
                    duree = f" ({tache.duree_estimee_min} min)" if tache.duree_estimee_min else ""
                    st.markdown(f"{tache.ordre}. **{tache.nom}**{duree}")

            # Risques & Conseils
            col_r, col_c = st.columns(2)
            with col_r:
                if estimation.risques_identifies:
                    st.markdown("#### ⚠️ Risques")
                    for risque in estimation.risques_identifies:
                        st.markdown(f"- {risque}")
            with col_c:
                if estimation.conseils_ia:
                    st.markdown("#### 💡 Conseils")
                    for conseil in estimation.conseils_ia:
                        st.markdown(f"- {conseil}")

        except Exception as e:
            logger.warning(f"Estimation IA échouée: {e}")
            st.warning("L'estimation IA n'est pas disponible pour le moment.")


# ═══════════════════════════════════════════════════════════
# ONGLET TIMELINE
# ═══════════════════════════════════════════════════════════


def onglet_timeline(keys: KeyNamespace):
    """Affiche la timeline des projets en cours."""
    from src.services.maison import get_projets_service

    service = get_projets_service()
    projets = service.obtenir_projets(statut="en_cours")

    if not projets:
        st.info("Aucun projet en cours.")
        return

    st.subheader(f"📅 {len(projets)} projet(s) en cours")

    for projet in projets:
        with st.container(border=True):
            st.markdown(f"**{projet.nom}**")

            # Progression
            if projet.tasks:
                total = len(projet.tasks)
                termines = sum(1 for t in projet.tasks if t.statut == "termine")
                pct = int((termines / total) * 100) if total > 0 else 0
                st.progress(pct / 100, text=f"{termines}/{total} tâches ({pct}%)")
            else:
                st.progress(0, text="Pas de tâches définies")

            # Dates
            if projet.date_debut and projet.date_fin_prevue:
                today = date.today()
                total_days = (projet.date_fin_prevue - projet.date_debut).days
                elapsed = (today - projet.date_debut).days
                if total_days > 0:
                    time_pct = min(100, max(0, int((elapsed / total_days) * 100)))
                    remaining = max(0, (projet.date_fin_prevue - today).days)
                    st.caption(
                        f"⏱️ {time_pct}% du temps écoulé — "
                        f"{remaining} jour(s) restant(s)"
                    )
                    if time_pct > 80 and projet.tasks:
                        taches_restantes = total - termines
                        if taches_restantes > 0:
                            st.warning(
                                f"⚠️ {taches_restantes} tâche(s) restante(s) "
                                f"avec seulement {remaining} jour(s) restant(s)"
                            )


# ═══════════════════════════════════════════════════════════
# ONGLET ROI
# ═══════════════════════════════════════════════════════════


def onglet_roi(keys: KeyNamespace):
    """Calculateur ROI pour rénovations énergétiques."""
    st.subheader("💰 Calculateur ROI Rénovation Énergétique")
    st.caption("Estimez les économies et le temps de retour de vos projets de rénovation.")

    col1, col2 = st.columns(2)
    with col1:
        type_renovation = st.selectbox(
            "Type de rénovation",
            [
                "Isolation combles",
                "Isolation murs",
                "Fenêtres double vitrage",
                "Chaudière condensation",
                "Pompe à chaleur",
                "Panneaux solaires",
                "Chauffe-eau thermodynamique",
            ],
            key=keys("type_renovation"),
        )
    with col2:
        cout = st.number_input(
            "Coût estimé (€)",
            min_value=100,
            max_value=50000,
            value=5000,
            step=500,
            key=keys("cout_renovation"),
        )

    if st.button("📊 Calculer le ROI", key=keys("btn_roi"), use_container_width=True):
        from decimal import Decimal

        from src.services.maison import get_projets_service

        service = get_projets_service()

        with st.spinner("🤖 Calcul ROI en cours..."):
            try:
                roi = asyncio.run(
                    service.calculer_roi(type_renovation, Decimal(str(cout)))
                )

                st.divider()

                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.markdown(
                        '<div class="roi-card">'
                        f'<h3>{roi.get("economies_annuelles", 0)}€/an</h3>'
                        "<p>Économies estimées</p></div>",
                        unsafe_allow_html=True,
                    )
                with col_r2:
                    retour = roi.get("retour_annees")
                    st.markdown(
                        '<div class="roi-card">'
                        f'<h3>{retour or "N/A"} ans</h3>'
                        "<p>Retour sur investissement</p></div>",
                        unsafe_allow_html=True,
                    )
                with col_r3:
                    aides = roi.get("aides_estimees", 0)
                    st.markdown(
                        '<div class="roi-card">'
                        f"<h3>{aides}€</h3>"
                        "<p>Aides estimées</p></div>",
                        unsafe_allow_html=True,
                    )

            except Exception as e:
                logger.warning(f"Calcul ROI échoué: {e}")
                st.warning("Le calcul ROI n'est pas disponible pour le moment.")


# ═══════════════════════════════════════════════════════════
# HELPERS CRUD
# ═══════════════════════════════════════════════════════════


@avec_session_db
def _creer_projet(
    nom: str,
    description: str,
    categorie: str,
    priorite: str,
    date_debut: date | None,
    date_fin_prevue: date | None,
    db=None,
) -> Project | None:
    """Crée un nouveau projet en DB."""
    try:
        projet = Project(
            nom=nom,
            description=description,
            statut="en_cours",
            priorite=priorite,
            date_debut=date_debut,
            date_fin_prevue=date_fin_prevue,
        )
        db.add(projet)
        db.commit()
        db.refresh(projet)
        return projet
    except Exception as e:
        logger.error(f"Erreur création projet: {e}")
        db.rollback()
        return None


@avec_session_db
def _terminer_projet(projet_id: int, db=None):
    """Marque un projet comme terminé."""
    projet = db.query(Project).get(projet_id)
    if projet:
        projet.statut = "termine"
        projet.date_fin_reelle = date.today()
        db.commit()


@avec_session_db
def _supprimer_projet(projet_id: int, db=None):
    """Supprime un projet."""
    projet = db.query(Project).get(projet_id)
    if projet:
        db.delete(projet)
        db.commit()
