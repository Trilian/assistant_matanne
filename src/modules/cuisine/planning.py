"""
Module Planning - Refactorisé avec BaseModuleCuisine
✅ Adapté à la structure spécifique jours/repas
"""
import streamlit as st
import asyncio
from datetime import timedelta, date
from typing import Dict, List

from .core import BaseModuleCuisine
from src.services.planning import planning_service, repas_service
from src.services.ai_services import create_planning_generation_service
from src.ui.feedback import LoadingState, show_success, show_error
from src.ui.components import empty_state, badge
from src.utils.constants import JOURS_SEMAINE, TYPES_REPAS


class PlanningModule(BaseModuleCuisine):
    """Module Planning optimisé avec structure spécifique"""

    def __init__(self):
        super().__init__(
            title="Planning Hebdomadaire",
            icon="🗓️",
            service=planning_service,
            schema_name="planning",
            cache_key="planning"
        )
        self.ai_service = create_planning_generation_service()

    # ═══════════════════════════════════════════════════════
    # OVERRIDE : Structure complètement différente
    # ═══════════════════════════════════════════════════════

    def render_bibliotheque(self):
        """Override : affichage calendrier au lieu de liste"""

        # Navigation semaine
        if "semaine_actuelle" not in st.session_state:
            st.session_state.semaine_actuelle = planning_service.get_semaine_debut()

        semaine = st.session_state.semaine_actuelle

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("⬅️ Précédente", use_container_width=True):
                st.session_state.semaine_actuelle = semaine - timedelta(days=7)
                from src.core.cache import Cache
                Cache.invalidate("planning_semaine")
                st.rerun()

        with col2:
            st.markdown(
                f"<div style='text-align:center; padding:0.5rem;'>"
                f"<strong>Semaine du {semaine.strftime('%d/%m/%Y')}</strong>"
                f"</div>",
                unsafe_allow_html=True
            )

        with col3:
            if st.button("Suivante ➡️", use_container_width=True):
                st.session_state.semaine_actuelle = semaine + timedelta(days=7)
                from src.core.cache import Cache
                Cache.invalidate("planning_semaine")
                st.rerun()

        st.markdown("---")

        # Charger planning
        planning = planning_service.get_planning_semaine(semaine)

        if not planning:
            empty_state(
                "Aucun planning pour cette semaine",
                "📅",
                "Crée un planning pour commencer"
            )

            if st.button("➕ Créer Planning", type="primary", use_container_width=True):
                self._create_empty_planning(semaine)

            return

        # Structure complète
        structure = planning_service.get_planning_structure(planning.id)

        # Stats rapides
        total_repas = sum(len(j["repas"]) for j in structure["jours"])

        col_stats1, col_stats2, col_stats3 = st.columns(3)

        with col_stats1:
            st.metric("Repas Planifiés", total_repas)

        with col_stats2:
            repas_bebe = sum(
                1 for j in structure["jours"]
                for r in j["repas"]
                if r.get("est_adapte_bebe")
            )
            st.metric("👶 Adaptés Bébé", repas_bebe)

        with col_stats3:
            temps_total = sum(
                r.get("recette", {}).get("temps_total", 0)
                for j in structure["jours"]
                for r in j["repas"]
                if r.get("recette")
            )
            st.metric("⏱️ Temps Total", f"{temps_total}min")

        # Actions rapides
        col_act1, col_act2, col_act3 = st.columns(3)

        with col_act1:
            if st.button("➕ Ajouter Repas", use_container_width=True):
                st.session_state.show_add_repas_form = True

        with col_act2:
            if st.button("🤖 Générer IA", use_container_width=True):
                st.session_state.active_tab = 1
                st.rerun()

        with col_act3:
            if st.button("🛒 Liste Courses", use_container_width=True):
                self._generate_shopping_list(structure)

        st.markdown("---")

        # Afficher par jour
        for jour_data in structure["jours"]:
            self._render_jour(jour_data, planning.id)

    def _render_jour(self, jour_data: Dict, planning_id: int):
        """Affiche un jour du planning"""
        jour_nom = jour_data["nom_jour"]
        date_jour = jour_data["date"]
        repas = jour_data["repas"]

        is_today = date_jour == date.today()

        with st.expander(
                f"{'🔵 ' if is_today else ''}{jour_nom} {date_jour.strftime('%d/%m')} ({len(repas)} repas)",
                expanded=is_today
        ):
            if repas:
                for idx, repas_data in enumerate(repas):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Type repas
                        type_icons = {
                            "petit_déjeuner": "🌅",
                            "déjeuner": "☀️",
                            "goûter": "🍪",
                            "dîner": "🌙"
                        }
                        icon = type_icons.get(repas_data["type"], "🍽️")

                        st.markdown(f"#### {icon} {repas_data['type'].replace('_', ' ').title()}")

                        if repas_data.get("recette"):
                            recette = repas_data["recette"]
                            st.markdown(f"**{recette['nom']}**")
                            st.caption(
                                f"⏱️ {recette.get('temps_total', 0)}min • "
                                f"🍽️ {repas_data['portions']}p"
                            )

                            if repas_data.get("est_adapte_bebe"):
                                badge("👶 Bébé", "#4CAF50")
                        else:
                            st.info("Aucune recette assignée")

                    with col2:
                        if st.button("✏️", key=f"edit_repas_{repas_data['id']}", help="Modifier"):
                            st.session_state.editing_repas_id = repas_data["id"]
                            st.rerun()

                        if st.button("🗑️", key=f"del_repas_{repas_data['id']}", help="Supprimer"):
                            self._delete_repas(repas_data["id"])

                        if st.button("✅", key=f"done_repas_{repas_data['id']}", help="Fait"):
                            self._mark_repas_done(repas_data["id"])

                    if idx < len(repas) - 1:
                        st.markdown("---")
            else:
                st.info("🍽️ Aucun repas planifié")

            # Bouton ajout
            if st.button(
                    "➕ Ajouter un repas",
                    key=f"add_repas_jour_{jour_data['jour_idx']}",
                    use_container_width=True
            ):
                self._add_repas_jour(planning_id, jour_data["jour_idx"], date_jour)

    # ═══════════════════════════════════════════════════════
    # IMPLÉMENTATION MÉTHODES ABSTRAITES (minimale)
    # ═══════════════════════════════════════════════════════

    def load_items(self) -> List[Dict]:
        """Charge plannings (non utilisé dans render_bibliotheque)"""
        return []

    def render_stats(self, items: List[Dict]):
        """Stats (géré dans render_bibliotheque)"""
        pass

    def render_filters(self, items: List[Dict]) -> List[Dict]:
        """Filtres (non applicable)"""
        return items

    def render_item_card(self, item: Dict):
        """Carte (non applicable)"""
        pass

    def render_form_fields(self) -> Dict:
        """Formulaire planning (non applicable)"""
        return {}

    def render_ia_config(self) -> Dict:
        """Config génération IA"""
        st.markdown("#### Configuration Foyer")

        col1, col2 = st.columns(2)

        with col1:
            nb_adultes = st.number_input("Adultes", min_value=1, max_value=10, value=2)
            nb_enfants = st.number_input("Enfants", min_value=0, max_value=10, value=1)

        with col2:
            a_bebe = st.checkbox("👶 Bébé (adapter recettes)", value=False)
            batch_cooking = st.checkbox("🍳 Batch cooking", value=False)

        st.markdown("#### Contraintes")

        contraintes = []

        col_c1, col_c2 = st.columns(2)

        with col_c1:
            temps_max_soir = st.slider(
                "Temps max soirs de semaine (min)",
                min_value=15,
                max_value=90,
                value=45
            )
            contraintes.append(f"Soirs: max {temps_max_soir}min")

        with col_c2:
            vegetarien = st.checkbox("🥬 Repas végétariens", value=False)
            if vegetarien:
                contraintes.append("2-3 repas végétariens")

        preferences = st.text_area(
            "Préférences alimentaires (optionnel)",
            placeholder="Ex: Pas de poisson le lundi...",
            height=100
        )

        if preferences:
            contraintes.extend(preferences.split("\n"))

        return {
            "nb_adultes": nb_adultes,
            "nb_enfants": nb_enfants,
            "a_bebe": a_bebe,
            "batch_cooking": batch_cooking,
            "contraintes": contraintes
        }

    async def generate_with_ia(self, config: Dict):
        """Génération IA planning"""
        semaine_debut = st.session_state.get(
            "semaine_actuelle",
            planning_service.get_semaine_debut()
        )

        loading = LoadingState("Génération Planning Complet")

        try:
            # Étape 1: Génération IA
            loading.add_step("Appel IA pour génération")

            planning_data = await self.ai_service.generer_planning_semaine(
                config={
                    "nb_adultes": config["nb_adultes"],
                    "nb_enfants": config["nb_enfants"],
                    "a_bebe": config["a_bebe"],
                    "batch_cooking_actif": config["batch_cooking"]
                },
                semaine_debut=semaine_debut,
                contraintes=config["contraintes"]
            )

            if not planning_data:
                loading.error_step(error_msg="Échec génération IA")
                return

            loading.complete_step()

            # Étape 2: Validation
            loading.add_step("Validation des données")

            if not planning_data.jours or len(planning_data.jours) != 7:
                loading.error_step(error_msg="Planning incomplet")
                return

            loading.complete_step()

            # Étape 3: Sauvegarde DB
            loading.add_step("Sauvegarde en base de données")

            planning_id = planning_service.create({
                "semaine_debut": semaine_debut,
                "nom": f"Planning IA - {semaine_debut.strftime('%d/%m')}",
                "genere_par_ia": True
            }).id

            # Créer repas
            for jour_data in planning_data.jours:
                jour_idx = jour_data.get("jour", 0)
                date_repas = semaine_debut + timedelta(days=jour_idx)

                for repas_data in jour_data.get("repas", []):
                    repas_service.create({
                        "planning_id": planning_id,
                        "jour_semaine": jour_idx,
                        "date": date_repas,
                        "type_repas": repas_data.get("type", "dîner"),
                        "recette_id": None,  # TODO: Rechercher/créer recette
                        "portions": repas_data.get("portions", 4),
                        "est_adapte_bebe": config.get("a_bebe", False),
                        "notes": f"Suggestion IA: {repas_data.get('nom_recette', '')}"
                    })

            loading.complete_step()

            loading.finish("Planning généré avec succès !")

            from src.core.cache import Cache
            Cache.invalidate("planning_semaine")
            st.rerun()

        except Exception as e:
            loading.error_step(error_msg=str(e))
            show_error(f"❌ Erreur génération: {str(e)}")

    # ═══════════════════════════════════════════════════════
    # MÉTHODES CUSTOM
    # ═══════════════════════════════════════════════════════

    def _create_empty_planning(self, semaine_debut: date):
        """Crée planning vide"""
        try:
            planning_service.create({
                "semaine_debut": semaine_debut,
                "nom": f"Semaine {semaine_debut.strftime('%d/%m')}"
            })

            from src.core.cache import Cache
            Cache.invalidate("planning_semaine")
            show_success("✅ Planning créé !")
            st.rerun()

        except Exception as e:
            show_error(f"❌ Erreur: {str(e)}")

    def _add_repas_jour(self, planning_id: int, jour_idx: int, date_repas: date):
        """Ajoute repas pour un jour"""
        st.session_state.adding_repas_planning_id = planning_id
        st.session_state.adding_repas_jour = jour_idx
        st.session_state.adding_repas_date = date_repas
        st.rerun()

    def _delete_repas(self, repas_id: int):
        """Supprime repas"""
        try:
            repas_service.delete(repas_id)
            from src.core.cache import Cache
            Cache.invalidate("planning_semaine")
            show_success("🗑️ Repas supprimé")
            st.rerun()

        except Exception as e:
            show_error(f"❌ Erreur: {str(e)}")

    def _mark_repas_done(self, repas_id: int):
        """Marque repas comme fait"""
        try:
            repas_service.update(repas_id, {"statut": "terminé"})
            from src.core.cache import Cache
            Cache.invalidate("planning_semaine")
            show_success("✅ Repas marqué fait")
            st.rerun()

        except Exception as e:
            show_error(f"❌ Erreur: {str(e)}")

    def _generate_shopping_list(self, planning_structure: Dict):
        """Génère liste courses depuis planning"""
        st.info("Utilise l'onglet 'Courses' puis 'Génération IA' pour créer la liste automatiquement !")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module"""
    module = PlanningModule()
    module.render()