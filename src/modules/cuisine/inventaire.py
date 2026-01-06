"""
Module Inventaire - Refactorisé avec BaseModuleCuisine
✅ -75% de code grâce aux mixins
"""
import streamlit as st
from datetime import date
from typing import Dict, List

from .core import BaseModuleCuisine
from src.services.inventaire import inventaire_service, CATEGORIES, EMPLACEMENTS
from src.services.ai_services import create_inventaire_ai_service
from src.utils.helpers import find_or_create_ingredient
from src.ui.components import badge
from src.utils.constants import STATUT_COLORS


class InventaireModule(BaseModuleCuisine):
    """Module Inventaire optimisé"""

    def __init__(self):
        super().__init__(
            title="Inventaire Intelligent",
            icon="📦",
            service=inventaire_service,
            schema_name="inventaire",
            cache_key="inventaire"
        )
        self.ai_service = create_inventaire_ai_service()

    # ═══════════════════════════════════════════════════════
    # IMPLÉMENTATION MÉTHODES ABSTRAITES
    # ═══════════════════════════════════════════════════════

    def load_items(self) -> List[Dict]:
        """Charge inventaire avec statuts"""
        return self.service.get_inventaire_complet()

    def render_stats(self, items: List[Dict]):
        """Stats inventaire avec alertes"""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Articles", len(items))

        with col2:
            stock_bas = len([a for a in items if a.get("statut") == "sous_seuil"])
            st.metric("Stock Bas", stock_bas, delta="⚠️" if stock_bas > 0 else None)

        with col3:
            peremption = len([a for a in items if a.get("statut") == "peremption_proche"])
            st.metric("Péremption", peremption, delta="⏳" if peremption > 0 else None)

        with col4:
            critiques = len([a for a in items if a.get("statut") == "critique"])
            st.metric("Critiques", critiques, delta="🔴" if critiques > 0 else None)

        # Alertes critiques
        articles_critiques = [
            a for a in items
            if a.get("statut") in ["critique", "sous_seuil", "peremption_proche"]
        ]

        if articles_critiques:
            self._render_stock_alert(articles_critiques[:5])

    def render_filters(self, items: List[Dict]) -> List[Dict]:
        """Filtres inventaire"""
        col1, col2, col3 = st.columns(3)

        with col1:
            categorie = st.selectbox("Catégorie", ["Toutes"] + CATEGORIES)

        with col2:
            emplacement = st.selectbox("Emplacement", ["Tous"] + EMPLACEMENTS)

        with col3:
            statut = st.selectbox(
                "Statut",
                ["Tous", "ok", "sous_seuil", "peremption_proche", "critique"]
            )

        # Filtrer
        filtered = items

        if categorie != "Toutes":
            filtered = [a for a in filtered if a.get("categorie") == categorie]

        if emplacement != "Tous":
            filtered = [a for a in filtered if a.get("emplacement") == emplacement]

        if statut != "Tous":
            filtered = [a for a in filtered if a.get("statut") == statut]

        return filtered

    def render_item_card(self, item: Dict):
        """Carte article inventaire"""
        statut = item.get("statut", "ok")
        couleur = STATUT_COLORS.get(statut, "#f8f9fa")

        with st.container():
            st.markdown(
                f'<div style="border-left: 4px solid {couleur}; padding: 1rem; '
                f'background: {couleur}20; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns([3, 2, 2])

            with col1:
                st.markdown(f"### {item['nom']}")
                st.caption(f"{item['categorie']} • {item.get('emplacement', '—')}")

                # Alerte péremption
                jours = item.get("jours_peremption")
                if jours is not None:
                    if jours <= 3:
                        st.error(f"⏳ Périme dans {jours} jour(s)")
                    elif jours <= 7:
                        st.warning(f"⏳ Dans {jours} jours")

            with col2:
                qty = item['quantite']
                seuil = item.get('seuil', item.get('quantite_min', 1.0))
                delta_text = None
                if qty < seuil:
                    delta_text = f"Seuil: {seuil}"
                st.metric("Stock", f"{qty:.1f} {item['unite']}", delta=delta_text, delta_color="inverse")

            with col3:
                # Actions rapides
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if st.button("➕", key=f"inv_plus_{item['id']}", help="Ajouter 1"):
                        self.adjust_stock(item["id"], 1.0)
                with col_a2:
                    if st.button("➖", key=f"inv_minus_{item['id']}", help="Retirer 1"):
                        self.adjust_stock(item["id"], -1.0)

                if st.button("🛒", key=f"inv_cart_{item['id']}", use_container_width=True):
                    self.add_to_courses(item["id"])

    def render_form_fields(self) -> Dict:
        """Champs formulaire inventaire"""
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom *", max_chars=200)
            categorie = st.selectbox("Catégorie *", CATEGORIES)
            quantite = st.number_input("Quantité *", min_value=0.0, step=0.1, value=1.0)
            unite = st.selectbox("Unité *", ["pcs", "kg", "g", "L", "mL"])

        with col2:
            quantite_min = st.number_input("Seuil", min_value=0.0, step=0.1, value=1.0)
            emplacement = st.selectbox("Emplacement", EMPLACEMENTS)
            date_peremption = st.date_input(
                "Péremption (optionnel)",
                value=None,
                min_value=date.today()
            )

        return {
            "nom": nom,
            "categorie": categorie,
            "quantite": quantite,
            "unite": unite,
            "quantite_min": quantite_min,
            "emplacement": emplacement,
            "date_peremption": date_peremption if date_peremption else None
        }

    def pre_create_hook(self, data: Dict) -> Dict:
        """Créer ingrédient avant article"""
        ingredient_id = find_or_create_ingredient(
            nom=data["nom"],
            unite=data["unite"],
            categorie=data["categorie"]
        )

        return {
            "ingredient_id": ingredient_id,
            "quantite": data["quantite"],
            "quantite_min": data["quantite_min"],
            "emplacement": data["emplacement"],
            "date_peremption": data["date_peremption"]
        }

    def render_ia_config(self) -> Dict:
        """Config analyse IA"""
        st.info("L'IA analysera ton inventaire et suggèrera des optimisations")

        col1, col2 = st.columns(2)

        with col1:
            inclure_alertes = st.checkbox("Inclure alertes péremption", value=True)

        with col2:
            inclure_suggestions = st.checkbox("Inclure suggestions achat", value=True)

        return {
            "alertes": inclure_alertes,
            "suggestions": inclure_suggestions
        }

    async def generate_with_ia(self, config: Dict):
        """Analyse IA inventaire"""
        items = self.load_items()

        if not items:
            st.warning("Inventaire vide")
            return

        try:
            analyse = await self.ai_service.analyser_inventaire(items)

            if not analyse:
                st.warning("Analyse non disponible")
                return

            st.success("✅ Analyse terminée !")

            # Articles prioritaires
            if config["suggestions"] and analyse.get("articles_prioritaires"):
                st.markdown("#### 🔴 À Commander en Priorité")

                for art in analyse["articles_prioritaires"]:
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**{art['nom']}**")
                        st.caption(art.get('raison', ''))

                    with col2:
                        if st.button("🛒", key=f"add_{art['nom']}", use_container_width=True):
                            self._add_item_to_courses(art['nom'])

            # Alertes péremption
            if config["alertes"] and analyse.get("alertes_peremption"):
                st.markdown("#### ⏳ Alertes Péremption")

                for alerte in analyse["alertes_peremption"]:
                    st.warning(
                        f"⚠️ **{alerte['nom']}** périme dans {alerte['jours_restants']} jour(s)"
                    )

            # Suggestions
            if analyse.get("suggestions"):
                st.markdown("#### 💡 Suggestions")

                for suggestion in analyse["suggestions"]:
                    st.info(f"💡 {suggestion}")

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

    # ═══════════════════════════════════════════════════════
    # MÉTHODES CUSTOM
    # ═══════════════════════════════════════════════════════

    def adjust_stock(self, article_id: int, delta: float):
        """Ajuste stock"""
        article = self.service.get_by_id(article_id)

        if article:
            new_qty = max(0, article.quantite + delta)
            self.service.update(article_id, {"quantite": new_qty})

            from src.core.cache import Cache
            Cache.invalidate(dependencies=[f"inventaire_{article_id}"])

            from src.ui.feedback import show_success
            show_success(f"{'➕' if delta > 0 else '➖'} Stock ajusté")
            st.rerun()

    def add_to_courses(self, article_id: int):
        """Ajoute article aux courses"""
        from src.services.courses import courses_service

        article = self.service.get_by_id(article_id)

        if article:
            courses_service.create({
                "ingredient_id": article.ingredient_id,
                "quantite_necessaire": article.quantite_min,
                "priorite": "haute"
            })

            from src.ui.feedback import show_success
            show_success(f"🛒 {article.nom} ajouté aux courses")
            st.rerun()

    def _add_item_to_courses(self, nom: str):
        """Ajoute item par nom aux courses"""
        from src.services.courses import courses_service

        ingredient_id = find_or_create_ingredient(nom, "pcs")

        courses_service.create({
            "ingredient_id": ingredient_id,
            "quantite_necessaire": 1.0,
            "priorite": "haute"
        })

        from src.ui.feedback import show_success
        show_success(f"🛒 {nom} ajouté aux courses")

    def _render_stock_alert(self, articles_critiques: List[Dict]):
        """Widget alertes stock"""
        st.warning(f"⚠️ **{len(articles_critiques)} article(s) en alerte**")

        with st.expander("Voir les alertes", expanded=False):
            for idx, article in enumerate(articles_critiques):
                col1, col2 = st.columns([3, 1])

                with col1:
                    statut_icons = {"ok": "✅", "sous_seuil": "⚠️", "peremption_proche": "⏳", "critique": "🔴"}
                    icon = statut_icons.get(article.get("statut"), "⚠️")
                    st.write(f"{icon} **{article['nom']}** - {article['quantite']:.1f} {article['unite']}")

                with col2:
                    if st.button("Voir", key=f"alert_{idx}", use_container_width=True):
                        self._view_article(article["id"])

    def _view_article(self, article_id: int):
        """Affiche détails article"""
        st.session_state.viewing_article_id = article_id
        st.rerun()

    def render_custom_actions(self):
        """Actions custom inventaire"""
        if st.button("🗑️ Supprimer Périmés", use_container_width=True):
            self._delete_expired_items()

    def _delete_expired_items(self):
        """Supprime articles périmés"""
        items = self.load_items()

        expired = [
            a for a in items
            if a.get("date_peremption") and a["date_peremption"] < date.today()
        ]

        if not expired:
            st.info("Aucun article périmé")
            return

        st.warning(f"⚠️ {len(expired)} articles périmés")

        if st.button("Confirmer Suppression", type="primary"):
            for art in expired:
                self.service.delete(art["id"])

            from src.ui.feedback import show_success
            show_success(f"✅ {len(expired)} articles supprimés")
            st.rerun()


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module"""
    module = InventaireModule()
    module.render()