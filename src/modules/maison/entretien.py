"""
Module Entretien - Gestion du menage et routines domestiques
Suivi des tâches quotidiennes, planification hebdomadaire, IA d'optimisation
"""

from datetime import date

import streamlit as st

from src.core.ai import ClientIA
from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db
from src.core.models import Routine, RoutineTask

# Logique metier pure
from src.modules.maison.utils import (
    charger_routines,
    clear_maison_cache,
    get_stats_entretien,
    get_taches_today,
)
from src.services.base import BaseAIService

# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# SERVICE IA ENTRETIEN
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


class EntretienService(BaseAIService):
    """Service IA pour optimisation du menage et routines"""

    def __init__(self, client: ClientIA = None):
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client, cache_prefix="entretien", default_ttl=3600, service_name="entretien"
        )

    async def creer_routine(self, nom: str, description: str = "") -> str:
        """Cree une routine avec tâches suggerees"""
        prompt = f"""Pour la routine "{nom}" {description},
suggère 5-8 tâches pratiques et dans un ordre logique.
Format: "- Tâche : description courte"."""

        return await self.call_with_cache(
            prompt=prompt, system_prompt="Tu es expert en organisation domestique", max_tokens=600
        )

    async def optimiser_semaine(self, types_taches: str) -> str:
        """Optimise la distribution des tâches sur la semaine"""
        prompt = f"""Propose une repartition optimale pour ces tâches menagères:
{types_taches}

Organise par jour (Lun-Dim) pour equilibrer la charge et ne pas surcharger un jour."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en planification et organisation du temps",
            max_tokens=700,
        )

    async def conseil_temps_estime(self, tache: str) -> str:
        """Estime le temps pour une tâche menagère"""
        prompt = f"""Pour la tâche menagère "{tache}",
estime le temps necessaire (min/max), la frequence ideale et des astuces."""

        return await self.call_with_cache(
            prompt=prompt, system_prompt="Tu es expert en optimisation du menage", max_tokens=400
        )

    async def conseil_efficacite(self) -> str:
        """Donne des astuces pour gagner du temps au menage"""
        prompt = """Donne 5 astuces pratiques pour rendre le menage plus efficace et moins chronophage.
Sois specifique et actionnable."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en organisation domestique et efficacite",
            max_tokens=500,
        )


def get_entretien_service() -> EntretienService:
    """Factory pour obtenir le service entretien"""
    return EntretienService()


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# HELPERS MÉTIER
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@avec_session_db
def creer_routine(nom: str, categorie: str, frequence: str, description: str = "", db=None) -> int:
    """Cree une nouvelle routine"""
    try:
        routine = Routine(
            nom=nom, categorie=categorie, frequence=frequence, description=description, actif=True
        )
        db.add(routine)
        db.commit()
        db.refresh(routine)
        clear_maison_cache()
        return routine.id
    except Exception as e:
        st.error(f"❌ Erreur creation routine: {e}")
        return None


@avec_session_db
@avec_session_db
def ajouter_tache_routine(
    routine_id: int,
    nom: str,
    description: str = "",
    heure_prevue: str = None,
    ordre: int = 1,
    db=None,
) -> bool:
    """Ajoute une tâche à une routine"""
    try:
        tache = RoutineTask(
            routine_id=routine_id,
            nom=nom,
            description=description,
            heure_prevue=heure_prevue,
            ordre=ordre,
        )
        db.add(tache)
        db.commit()
        clear_maison_cache()
        return True
    except Exception as e:
        st.error(f"❌ Erreur ajout tâche: {e}")
        return False


@avec_session_db
def marquer_tache_faite(task_id: int, db=None) -> bool:
    """Marque une tâche comme faite aujourd'hui"""
    try:
        tache = db.query(RoutineTask).get(task_id)
        if tache:
            tache.fait_le = date.today()
            db.commit()
            clear_maison_cache()
            return True
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
    return False


@avec_session_db
def desactiver_routine(routine_id: int, db=None) -> bool:
    """Desactive une routine"""
    try:
        routine = db.query(Routine).get(routine_id)
        if routine:
            routine.actif = False
            db.commit()
            clear_maison_cache()
            return True
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
    return False


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


def app():
    """Point d'entree module Entretien"""
    st.title("🧹 Entretien & Menage")
    st.caption("Gestion des routines et tâches menagères avec IA")

    service = get_entretien_service()

    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # STATISTIQUES
    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    stats = get_stats_entretien()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Routines actives", stats["routines_actives"])

    with col2:
        st.metric("Tâches total", stats["total_taches"])

    with col3:
        st.metric("Faites aujourd'hui", stats["taches_today"])

    with col4:
        st.metric("Progression", f"{stats['completion_today']:.0f}%")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    tab1, tab2, tab3, tab4 = st.tabs(
        ["✓ Aujourd'hui", "🔄 Routines", "🤖 Assistant IA", "➕ Créer"]
    )

    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TAB 1: TÂCHES AUJOURD'HUI
    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    with tab1:
        st.subheader("Checklist d'aujourd'hui")

        taches = get_taches_today()

        if not taches:
            st.success("✨ Aucune tâche pour aujourd'hui!")
        else:
            # Tri par heure
            taches_triees = sorted(taches, key=lambda x: x.get("heure", ""))

            # Progression
            faites = len([t for t in taches if t["fait"]])
            progression = (faites / len(taches) * 100) if taches else 0

            st.progress(progression / 100)
            st.caption(f"✅ {faites}/{len(taches)} tâches faites ({progression:.0f}%)")

            st.markdown("---")

            # Affichage
            for tache in taches_triees:
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    emoji = "✅" if tache["fait"] else "⏳"
                    st.markdown(f"### {emoji} {tache['nom']}")

                    if tache.get("description"):
                        st.caption(tache["description"])

                    if tache.get("heure"):
                        st.caption(f"🎯 {tache['heure']}")

                with col2:
                    if not tache["fait"]:
                        if st.button(
                            "✅ Fait", key=f"check_{tache['id']}", use_container_width=True
                        ):
                            if marquer_tache_faite(tache["id"]):
                                st.success("✅ Tâche marquee!")
                                st.rerun()

                with col3:
                    if tache["fait"]:
                        st.success("✅")

                st.divider()

    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TAB 2: ROUTINES
    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    with tab2:
        st.subheader("Mes routines")

        df_routines = charger_routines()

        if df_routines.empty:
            st.info("Aucune routine creee. Creez-en une!")
        else:
            # Filtre par categorie
            categories = ["Tous"] + sorted(df_routines["categorie"].unique().tolist())
            filtre_cat = st.selectbox("Filtrer par categorie", categories)

            if filtre_cat != "Tous":
                df_routines = df_routines[df_routines["categorie"] == filtre_cat]

            for idx, routine in df_routines.iterrows():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### {routine['nom']}")

                    # Barre de progression
                    st.progress(routine["completion"] / 100)
                    st.caption(
                        f"📊 {routine['completion']:.0f}% • "
                        f"{routine['tasks_aujourd_hui']}/{routine['tasks_count']} tâches • "
                        f"Frequence: {routine['frequence']}"
                    )

                    if routine["description"]:
                        st.caption(routine["description"])

                with col2:
                    if st.button("⚙️", key=f"settings_{routine['id']}", use_container_width=True):
                        if desactiver_routine(routine["id"]):
                            st.info("Routine desactivee")
                            st.rerun()

                # Tâches
                with st.expander("Voir tâches"):
                    with obtenir_contexte_db() as session:
                        taches_routine = (
                            session.query(RoutineTask).filter_by(routine_id=routine["id"]).all()
                        )

                        if not taches_routine:
                            st.caption("Aucune tâche")
                        else:
                            for t in taches_routine:
                                col_t1, col_t2 = st.columns([4, 1])

                                with col_t1:
                                    emoji = "✅" if t.fait_le == date.today() else "⏳"
                                    st.caption(f"{emoji} {t.nom}")
                                    if t.heure_prevue:
                                        st.caption(f"🎯 {t.heure_prevue}")

                                with col_t2:
                                    if t.fait_le != date.today():
                                        if st.button(
                                            "✅", key=f"tache_{t.id}", use_container_width=True
                                        ):
                                            if marquer_tache_faite(t.id):
                                                st.rerun()

                st.divider()

    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TAB 3: ASSISTANT IA
    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    with tab3:
        st.subheader("🤖 Assistant Entretien IA")

        # Creer routine avec IA
        st.markdown("#### 📅 Creer une routine avec IA")

        col_r1, col_r2 = st.columns(2)

        with col_r1:
            routine_nom = st.text_input("Nom de la routine", placeholder="Ex: Nettoyage cuisine")

        with col_r2:
            routine_freq = st.selectbox(
                "Frequence", ["quotidien", "hebdomadaire", "mensuel", "hebdomadaire 2x"]
            )

        if st.button("👶 Generer tâches", use_container_width=True):
            if routine_nom:
                with st.spinner("IA cree la routine..."):
                    try:
                        import asyncio

                        taches = asyncio.run(
                            service.creer_routine(routine_nom, f"Frequence: {routine_freq}")
                        )
                        if taches:
                            st.success(taches)

                            # Proposer de creer
                            if st.button("✅ Creer cette routine", use_container_width=True):
                                r_id = creer_routine(routine_nom, "General", routine_freq)
                                if r_id:
                                    st.success("Routine creee!")
                    except Exception as e:
                        st.warning(f"âš ï¸ IA indisponible: {e}")

        st.markdown("---")

        # Optimiser semaine
        st.markdown("#### 🧹️ Optimiser la semaine")

        types = st.text_area(
            "Lister les tâches (une par ligne)",
            placeholder="Nettoyage salle de bain\nLessive\nVaisselle\n...",
            height=120,
        )

        if st.button("💡 Proposer repartition", use_container_width=True):
            if types:
                with st.spinner("Optimisation en cours..."):
                    try:
                        import asyncio

                        repartition = asyncio.run(service.optimiser_semaine(types))
                        if repartition:
                            st.info(repartition)
                    except Exception as e:
                        st.warning(f"âš ï¸ IA indisponible: {e}")

        st.markdown("---")

        # Astuces
        st.markdown("#### 👶 Astuces d'efficacite")

        if st.button("💰 Obtenir astuces", use_container_width=True):
            with st.spinner("Recherche astuces..."):
                try:
                    import asyncio

                    astuces = asyncio.run(service.conseil_efficacite())
                    if astuces:
                        st.success(astuces)
                except Exception as e:
                    st.warning(f"âš ï¸ IA indisponible: {e}")

        st.markdown("---")

        # Estimer temps
        st.markdown("#### ⏱️ Estimer temps d'une tâche")

        tache_temps = st.text_input("Nom de la tâche", placeholder="Ex: Nettoyer la salle de bain")

        if st.button("Estimer", use_container_width=True):
            if tache_temps:
                with st.spinner("Estimation..."):
                    try:
                        import asyncio

                        temps = asyncio.run(service.conseil_temps_estime(tache_temps))
                        if temps:
                            st.info(temps)
                    except Exception as e:
                        st.warning(f"âš ï¸ IA indisponible: {e}")

    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    # TAB 4: CRÉER ROUTINE
    # ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

    with tab4:
        st.subheader("Creer une nouvelle routine")

        with st.form("form_routine"):
            nom_r = st.text_input("Nom *", placeholder="Ex: Nettoyage salle de bain")

            col_r1, col_r2 = st.columns(2)

            with col_r1:
                categorie_r = st.selectbox(
                    "Categorie",
                    ["Cuisine", "Salle de bain", "Chambres", "Salon", "Exterieur", "Autre"],
                )

            with col_r2:
                frequence_r = st.selectbox(
                    "Frequence", ["quotidien", "hebdomadaire", "bi-hebdomadaire", "mensuel"]
                )

            desc_r = st.text_area("Description", placeholder="Details de la routine...", height=80)

            nb_taches = st.number_input("Nombre de tâches à ajouter", 1, 10, 3)

            submitted = st.form_submit_button("✅ Creer routine", type="primary")

            if submitted:
                if not nom_r:
                    st.error("Nom obligatoire")
                else:
                    r_id = creer_routine(nom_r, categorie_r, frequence_r, desc_r)
                    if r_id:
                        st.success(f"✅ Routine '{nom_r}' creee!")
                        st.rerun()

        st.markdown("---")

        # Templates
        st.markdown("### 📅 Templates rapides")

        templates = [
            {
                "nom": "Nettoyage cuisine",
                "categorie": "Cuisine",
                "freq": "quotidien",
                "taches": [
                    "Laver vaisselle",
                    "Nettoyer plan de travail",
                    "Balayer",
                    "Vider poubelle",
                ],
            },
            {
                "nom": "Salle de bain",
                "categorie": "Salle de bain",
                "freq": "hebdomadaire",
                "taches": ["Toilettes", "Baignoire/douche", "Lavabo", "Miroir", "Sol"],
            },
            {
                "nom": "Lessive",
                "categorie": "Chambres",
                "freq": "hebdomadaire",
                "taches": ["Trier linge", "Laver", "Secher", "Plier", "Ranger"],
            },
        ]

        for templ in templates:
            if st.button(f"📅 {templ['nom']}", use_container_width=True):
                r_id = creer_routine(templ["nom"], templ["categorie"], templ["freq"])
                if r_id:
                    for ordre, tache_nom in enumerate(templ["taches"], 1):
                        ajouter_tache_routine(r_id, tache_nom, ordre=ordre)
                    st.success("✅ Routine creee!")
                    st.rerun()


if __name__ == "__main__":
    app()
