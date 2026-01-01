"""
Module Inventaire - IMPORTS CORRIGÉS
"""
import streamlit as st
from datetime import date, timedelta
from typing import Optional, List, Dict

# ✅ Services
from src.services.inventaire import inventaire_service, CATEGORIES, EMPLACEMENTS
from src.services.ai_services import create_inventaire_ai_service

# ✅ UI
from src.ui.base_module import create_module_ui
from src.ui.domain import inventory_card, stock_alert
from src.ui.feedback import smart_spinner, ProgressTracker, show_success, show_error
from src.ui.components import Modal, empty_state, badge

# ✅ Validation (CORRIGÉ - validation_unified)
from src.core.validation_unified import (
    validate_and_sanitize_form,
    INVENTAIRE_SCHEMA,
    show_validation_errors
)

# ✅ Cache & State
from src.core.cache import Cache
from src.core.state import get_state

# ✅ Constants (NOUVEAU)
from src.core.constants import (
    ITEMS_PER_PAGE_INVENTAIRE,
    CATEGORIES_INVENTAIRE,
    EMPLACEMENTS_INVENTAIRE,
    INVENTAIRE_SEUIL_CRITIQUE_RATIO,
    INVENTAIRE_JOURS_PEREMPTION_ALERTE
)

# Config
from .configs import get_inventaire_config


# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module inventaire"""
    st.title("📦 Inventaire Intelligent")

    tab1, tab2, tab3 = st.tabs([
        "📋 Inventaire",
        "🤖 Analyse IA",
        "⚙️ Paramètres"
    ])

    with tab1:
        render_inventaire()

    with tab2:
        render_analyse_ia()

    with tab3:
        render_parametres()


# ═══════════════════════════════════════════════════════════
# TAB 1: INVENTAIRE
# ═══════════════════════════════════════════════════════════

def render_inventaire():
    """Affichage inventaire avec alertes"""
    inventaire = inventaire_service.get_inventaire_complet()

    if not inventaire:
        empty_state("Inventaire vide", "📦", "Ajoute ton premier article")
        render_add_form()
        return

    # Alertes critiques
    articles_critiques = [
        art for art in inventaire
        if art.get("statut") in ["critique", "sous_seuil", "peremption_proche"]
    ]

    if articles_critiques:
        stock_alert(
            articles_critiques,
            on_click=lambda article_id: view_article(article_id),
            key="alert_inventaire"
        )

    # Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Articles", len(inventaire))

    with col2:
        stock_bas = len([a for a in inventaire if a.get("statut") == "sous_seuil"])
        st.metric("Stock Bas", stock_bas, delta=None if stock_bas == 0 else "⚠️")

    with col3:
        peremption = len([a for a in inventaire if a.get("statut") == "peremption_proche"])
        st.metric("Péremption", peremption, delta=None if peremption == 0 else "⏳")

    with col4:
        critiques = len([a for a in inventaire if a.get("statut") == "critique"])
        st.metric("Critiques", critiques, delta=None if critiques == 0 else "🔴")

    # Actions
    col_add, col_scan = st.columns(2)

    with col_add:
        if st.button("➕ Ajouter Article", type="primary", use_container_width=True):
            st.session_state.show_add_form = True

    with col_scan:
        if st.button("📸 Scanner (TODO)", use_container_width=True):
            st.info("Scan de tickets bientôt disponible !")

    if st.session_state.get("show_add_form", False):
        render_add_form()

    st.markdown("---")

    # Filtres
    col_cat, col_emp, col_stat = st.columns(3)

    with col_cat:
        categorie_filter = st.selectbox("Catégorie", ["Toutes"] + CATEGORIES, key="filter_cat")

    with col_emp:
        emplacement_filter = st.selectbox("Emplacement", ["Tous"] + EMPLACEMENTS, key="filter_emp")

    with col_stat:
        statut_filter = st.selectbox(
            "Statut",
            ["Tous", "ok", "sous_seuil", "peremption_proche", "critique"],
            key="filter_stat"
        )

    # Filtrer
    filtered = inventaire

    if categorie_filter != "Toutes":
        filtered = [a for a in filtered if a.get("categorie") == categorie_filter]

    if emplacement_filter != "Tous":
        filtered = [a for a in filtered if a.get("emplacement") == emplacement_filter]

    if statut_filter != "Tous":
        filtered = [a for a in filtered if a.get("statut") == statut_filter]

    st.markdown(f"### 📦 Articles ({len(filtered)})")

    for article in filtered:
        inventory_card(
            article=article,
            on_adjust=lambda art_id, delta: adjust_stock(art_id, delta),
            on_add_to_cart=lambda art_id: add_to_courses(art_id),
            key=f"inv_{article['id']}"
        )


def render_add_form():
    """Formulaire ajout article"""
    with st.expander("➕ Ajouter un Article", expanded=True):
        with st.form("add_inventaire_form"):
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
                    "Date péremption (optionnel)",
                    value=None,
                    min_value=date.today()
                )

            col_submit, col_cancel = st.columns(2)

            with col_submit:
                submitted = st.form_submit_button("✅ Ajouter", type="primary", use_container_width=True)

            with col_cancel:
                cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)

            if cancelled:
                st.session_state.show_add_form = False
                st.rerun()

            if submitted:
                form_data = {
                    "nom": nom,
                    "categorie": categorie,
                    "quantite": quantite,
                    "unite": unite,
                    "quantite_min": quantite_min,
                    "emplacement": emplacement,
                    "date_peremption": date_peremption if date_peremption else None
                }

                # ✅ Validation avec validation_unified
                is_valid, sanitized = validate_and_sanitize_form("inventaire", form_data)

                if is_valid:
                    try:
                        from src.utils.helpers import find_or_create_ingredient

                        ingredient_id = find_or_create_ingredient(
                            nom=sanitized["nom"],
                            unite=sanitized["unite"],
                            categorie=sanitized["categorie"]
                        )

                        inventaire_service.create({
                            "ingredient_id": ingredient_id,
                            "quantite": sanitized["quantite"],
                            "quantite_min": sanitized["quantite_min"],
                            "emplacement": sanitized["emplacement"],
                            "date_peremption": sanitized["date_peremption"]
                        })

                        Cache.invalidate("inventaire")
                        show_success(f"✅ Article '{sanitized['nom']}' ajouté !")

                        st.session_state.show_add_form = False
                        st.rerun()

                    except Exception as e:
                        show_error(f"❌ Erreur: {str(e)}")


def adjust_stock(article_id: int, delta: float):
    """Ajuste stock"""
    try:
        article = inventaire_service.get_by_id(article_id)

        if not article:
            show_error("Article introuvable")
            return

        new_qty = max(0, article.quantite + delta)
        inventaire_service.update(article_id, {"quantite": new_qty})

        Cache.invalidate("inventaire")

        icon = "➕" if delta > 0 else "➖"
        show_success(f"{icon} Stock ajusté: {new_qty}")

        st.rerun()

    except Exception as e:
        show_error(f"❌ Erreur: {str(e)}")


def add_to_courses(article_id: int):
    """Ajoute article aux courses"""
    try:
        from src.services.courses import courses_service

        article = inventaire_service.get_by_id(article_id)

        if not article:
            show_error("Article introuvable")
            return

        courses_service.create({
            "ingredient_id": article.ingredient_id,
            "quantite_necessaire": article.quantite_min,
            "priorite": "haute"
        })

        show_success(f"🛒 '{article.ingredient.nom}' ajouté aux courses !")

    except Exception as e:
        show_error(f"❌ Erreur: {str(e)}")


def view_article(article_id: int):
    """Affiche détails article"""
    st.session_state.viewing_article_id = article_id
    st.rerun()


# ═══════════════════════════════════════════════════════════
# TAB 2: ANALYSE IA
# ═══════════════════════════════════════════════════════════

def render_analyse_ia():
    """Analyse IA de l'inventaire"""
    st.markdown("### 🤖 Analyse Intelligente")

    inventaire = inventaire_service.get_inventaire_complet()

    if not inventaire:
        empty_state("Inventaire vide", "📦")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Articles", len(inventaire))

    with col2:
        critiques = len([a for a in inventaire if a.get("statut") in ["critique", "sous_seuil"]])
        st.metric("Articles à commander", critiques)

    with col3:
        peremption = len([a for a in inventaire if a.get("statut") == "peremption_proche"])
        st.metric("Péremption proche", peremption)

    if st.button("🚀 Analyser l'Inventaire", type="primary", use_container_width=True):
        analyze_inventory_with_ai(inventaire)


async def analyze_inventory_with_ai(inventaire: List[Dict]):
    """Analyse inventaire avec IA"""
    ai_service = create_inventaire_ai_service()

    try:
        analyse = await ai_service.analyser_inventaire(inventaire)

        if not analyse:
            st.warning("Aucune analyse disponible")
            return

        st.markdown("### 📊 Résultats de l'Analyse")

        if analyse.get("articles_prioritaires"):
            st.markdown("#### 🔴 Articles à Commander en Priorité")

            for art in analyse["articles_prioritaires"]:
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**{art['nom']}**")
                        st.caption(art.get('raison', ''))

                    with col2:
                        if st.button("🛒 Ajouter", key=f"add_{art['nom']}", use_container_width=True):
                            article = next(
                                (a for a in inventaire if a['nom'].lower() == art['nom'].lower()),
                                None
                            )
                            if article:
                                add_to_courses(article['id'])

        if analyse.get("alertes_peremption"):
            st.markdown("#### ⏳ Alertes Péremption")

            for alerte in analyse["alertes_peremption"]:
                st.warning(
                    f"⚠️ **{alerte['nom']}** périme dans {alerte['jours_restants']} jour(s)"
                )

        if analyse.get("suggestions"):
            st.markdown("#### 💡 Suggestions d'Optimisation")

            for suggestion in analyse["suggestions"]:
                st.info(f"💡 {suggestion}")

    except Exception as e:
        show_error(f"❌ Erreur analyse: {str(e)}")
        st.exception(e)


# ═══════════════════════════════════════════════════════════
# TAB 3: PARAMÈTRES
# ═══════════════════════════════════════════════════════════

def render_parametres():
    """Paramètres module inventaire"""
    st.markdown("### ⚙️ Paramètres")

    st.markdown("#### 📦 Import/Export")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 📥 Importer")

        uploaded_file = st.file_uploader(
            "Fichier CSV/JSON",
            type=["csv", "json"],
            key="import_inventaire"
        )

        if uploaded_file:
            import_inventaire_file(uploaded_file)

    with col2:
        st.markdown("##### 📤 Exporter")

        format_export = st.selectbox("Format", ["csv", "json"], key="export_format")

        if st.button("📥 Télécharger", use_container_width=True):
            export_inventaire(format_export)

    st.markdown("---")
    st.markdown("#### 🧹 Maintenance")

    col3, col4 = st.columns(2)

    with col3:
        if st.button("🗑️ Supprimer Articles Périmés", use_container_width=True):
            delete_expired_items()

    with col4:
        if st.button("🗑️ Vider Cache", use_container_width=True):
            Cache.invalidate("inventaire")
            show_success("Cache vidé !")

    st.markdown("---")
    st.markdown("#### 📊 Statistiques")

    stats = inventaire_service.get_stats(
        group_by_fields=["emplacement"],
        count_filters={
            "stock_bas": {"quantite": {"lte": "quantite_min"}},
        }
    )

    col5, col6 = st.columns(2)

    with col5:
        st.metric("Total Articles", stats.get("total", 0))

    with col6:
        st.json(stats.get("by_emplacement", {}))


def import_inventaire_file(file):
    """Importe inventaire"""
    try:
        from src.services.inventaire import InventaireImporter

        if file.name.endswith('.csv'):
            content = file.read().decode('utf-8')
            importer = InventaireImporter()
            items, errors = importer.from_csv(content)
        else:
            content = file.read().decode('utf-8')
            importer = InventaireImporter()
            items, errors = importer.from_json(content)

        if errors:
            st.warning(f"⚠️ {len(errors)} erreurs")
            with st.expander("Voir erreurs"):
                for error in errors:
                    st.error(error)

        if not items:
            st.error("Aucun article valide")
            return

        progress = ProgressTracker("Import inventaire", total=len(items))

        imported = 0
        for i, item in enumerate(items):
            try:
                # ✅ Validation avec validation_unified
                is_valid, sanitized = validate_and_sanitize_form("inventaire", item)

                if is_valid:
                    from src.utils.helpers import find_or_create_ingredient

                    ingredient_id = find_or_create_ingredient(
                        nom=sanitized["nom"],
                        unite=sanitized["unite"],
                        categorie=sanitized.get("categorie", "Autre")
                    )

                    inventaire_service.create({
                        "ingredient_id": ingredient_id,
                        "quantite": sanitized["quantite"],
                        "quantite_min": sanitized.get("quantite_min", 1.0),
                        "emplacement": sanitized.get("emplacement"),
                        "date_peremption": sanitized.get("date_peremption")
                    })

                    imported += 1
                    progress.update(i+1, f"✅ {sanitized['nom']}")
                else:
                    progress.update(i+1, f"❌ Invalide")

            except Exception as e:
                progress.update(i+1, f"❌ Erreur: {str(e)}")

        progress.complete(f"✅ {imported}/{len(items)} articles importés")
        Cache.invalidate("inventaire")

    except Exception as e:
        show_error(f"❌ Erreur import: {str(e)}")


def export_inventaire(format: str):
    """Exporte inventaire"""
    try:
        from src.services.inventaire import InventaireExporter

        inventaire = inventaire_service.get_inventaire_complet()

        if not inventaire:
            st.warning("Aucun article à exporter")
            return

        exporter = InventaireExporter()

        if format == "csv":
            data = exporter.to_csv(inventaire)
            st.download_button("📥 Télécharger CSV", data, "inventaire_export.csv", "text/csv")
        else:
            data = exporter.to_json(inventaire)
            st.download_button("📥 Télécharger JSON", data, "inventaire_export.json", "application/json")

        show_success(f"✅ {len(inventaire)} articles exportés")

    except Exception as e:
        show_error(f"❌ Erreur export: {str(e)}")


def delete_expired_items():
    """Supprime articles périmés"""
    try:
        inventaire = inventaire_service.get_inventaire_complet()

        expired = [
            art for art in inventaire
            if art.get("date_peremption") and art["date_peremption"] < date.today()
        ]

        if not expired:
            st.info("Aucun article périmé")
            return

        st.warning(f"⚠️ {len(expired)} articles périmés à supprimer")

        for art in expired:
            st.write(f"• {art['nom']} (périmé le {art['date_peremption']})")

        if st.button("Confirmer Suppression", type="primary"):
            deleted = 0

            for art in expired:
                inventaire_service.delete(art["id"])
                deleted += 1

            Cache.invalidate("inventaire")
            show_success(f"✅ {deleted} articles supprimés")
            st.rerun()

    except Exception as e:
        show_error(f"❌ Erreur: {str(e)}")