"""
Module Recettes - Gestion complète des recettes

Fonctionnalités:
- Liste des recettes avec filtres et pagination
- Détail recette avec badges, historique et versions
- Ajout manuel de recettes
- Génération de recettes avec l'IA
- Génération d'images pour les recettes
"""

import json
import os
import shutil
import uuid
from pathlib import Path

import requests
import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.services.cuisine.recettes import get_recipe_import_service
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

# Re-export public API (lazy-imported dans app())
from .utils import formater_quantite

_keys = KeyNamespace("recettes")


@profiler_rerun("recettes")
def app():
    """Point d'entrée module recettes"""
    from src.services.cuisine.recettes import obtenir_service_recettes

    # Import externe pour l'onglet import
    from ..recettes_import import afficher_importer
    from .ajout import afficher_ajouter_manuel
    from .detail import afficher_detail_recette
    from .generation_ia import afficher_generer_ia
    from .liste import afficher_liste

    st.title("🍽️ Mes Recettes")
    st.caption("Gestion complète de votre base de recettes")

    # Assistant de démarrage (wizard) CTA
    if st.button("➕ Assistant démarrage", key=_keys("show_wizard_cta")):
        st.session_state[_keys("show_wizard")] = True
        # initialize wizard transient state
        st.session_state.setdefault(_keys("wizard_mode"), "Manuel")
        st.session_state.setdefault(_keys("wizard_preview"), None)
        rerun()
    # ── Outils cuisine ──
    _c1, _c2, _c3, _c4 = st.columns(4)
    with _c1:
        if st.button("⚖️ Convertisseur", key="rec_nav_conv", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("convertisseur_unites")
            rerun()
    with _c2:
        if st.button("🔢 Portions", key="rec_nav_port", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("calculatrice_portions")
            rerun()
    with _c3:
        if st.button("🔄 Substitutions", key="rec_nav_sub", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("substitutions")
            rerun()
    with _c4:
        if st.button("🥕 Saisons", key="rec_nav_sais", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("saisonnalite")
            rerun()

    # Afficher le wizard si demandé
    if _keys("show_wizard") in st.session_state and st.session_state.get(_keys("show_wizard")):
        st.markdown("### ✨ Assistant démarrage — Aide rapide pour ajouter vos premières recettes")

        # Mode (préservé dans session_state)
        mode = st.selectbox("Mode", ["Manuel", "Importer (URL)", "IA"], key=_keys("wizard_mode"))

        # MANUEL: champs essentiels
        if mode == "Manuel":
            st.info("Créer une recette minimale en quelques secondes")
            nom = st.text_input("Nom de la recette", key=_keys("wizard_nom"))
            type_repas = st.selectbox(
                "Type de repas",
                ["petit_dejeuner", "dejeuner", "dîner", "goûter", "aperitif", "dessert"],
                key=_keys("wizard_type_repas"),
            )
            col1, col2 = st.columns(2)
            with col1:
                portions = st.number_input(
                    "Portions", min_value=1, max_value=20, value=2, key=_keys("wizard_portions")
                )
            with col2:
                temps = st.number_input(
                    "Temps préparation (min)",
                    min_value=0,
                    max_value=600,
                    value=10,
                    key=_keys("wizard_temps"),
                )

            if st.button("Créer la recette minimale", key=_keys("wizard_create_manual")):
                service = obtenir_service_recettes()
                if not nom:
                    st.error("Le nom est requis")
                elif not service:
                    st.error("Service recettes indisponible")
                else:
                    try:
                        data = {
                            "nom": nom,
                            "type_repas": type_repas,
                            "description": "Créée depuis l'assistant de démarrage",
                            "temps_preparation": int(temps),
                            "temps_cuisson": 0,
                            "portions": int(portions),
                            "difficulte": "facile",
                            "saison": "toute_année",
                            "ingredients": [],
                            "etapes": [],
                        }
                        recette = service.create_complete(data)
                        st.success(f"Recette '{recette.nom}' créée !")
                        st.session_state[_keys("show_wizard")] = False
                        rerun()
                    except Exception as e:
                        st.error(f"Erreur création: {e}")

        # IMPORT URL: extraire, preview et sauvegarder (téléchargement image si possible)
        elif mode == "Importer (URL)":
            st.info("Importer une recette depuis une URL (ex: Marmiton)")
            url = st.text_input("URL à importer", key=_keys("wizard_url"))
            if st.button("Extraire et prévisualiser", key=_keys("wizard_extract")):
                importer = get_recipe_import_service()
                service = obtenir_service_recettes()
                if not importer:
                    st.error("Service d'import non disponible")
                else:
                    try:
                        with st.spinner("Extraction en cours..."):
                            result = importer.import_from_url(url)
                        if not result or not result.success or not result.recipe:
                            st.error("Impossible d'extraire la recette depuis l'URL fournie")
                        else:
                            recipe_data = result.recipe.model_dump()
                            st.session_state[_keys("wizard_preview")] = recipe_data
                            st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erreur import: {e}")

            # Si preview disponible, afficher et proposer sauvegarde
            preview = st.session_state.get(_keys("wizard_preview"))
            if preview:
                st.markdown("#### Aperçu importé")
                st.write(preview.get("nom", "-"))
                st.write(preview.get("description", ""))
                st.markdown("**Ingrédients**")
                for ing in preview.get("ingredients", []):
                    st.write(f"- {ing}")
                st.markdown("**Étapes**")
                for s in preview.get("etapes", []):
                    st.write(f"- {s}")

                if st.button("Importer et sauvegarder", key=_keys("wizard_save_import")):
                    service = obtenir_service_recettes()
                    if not service:
                        st.error("Service recettes indisponible")
                    else:
                        # Gérer image: tenter de télécharger l'URL si remote
                        image_path = None
                        image_url = preview.get("image_url")
                        try:
                            if image_url and image_url.startswith("http"):
                                images_dir = Path("data") / "recettes_images"
                                images_dir.mkdir(parents=True, exist_ok=True)
                                ext = (
                                    os.path.splitext(image_url)[1].split("?")[0].lstrip(".")
                                    or "jpg"
                                )
                                fname = f"{uuid.uuid4().hex}.{ext}"
                                dest = images_dir / fname
                                r = requests.get(image_url, stream=True, timeout=10)
                                if r.status_code == 200:
                                    with open(dest, "wb") as f:
                                        shutil.copyfileobj(r.raw, f)
                                    image_path = str(dest)
                                else:
                                    image_path = image_url
                        except Exception:
                            image_path = image_url

                        try:
                            created = service.create_from_import(
                                nom=preview.get("nom", "Importée"),
                                type_repas=preview.get("categorie")
                                or preview.get("type_repas", "dîner"),
                                description=preview.get("description", ""),
                                temps_preparation=int(preview.get("temps_preparation", 0) or 0),
                                temps_cuisson=int(preview.get("temps_cuisson", 0) or 0),
                                portions=int(preview.get("portions", 1) or 1),
                                difficulte=preview.get("difficulte", "moyen"),
                                ingredients_textes=preview.get("ingredients", []),
                                etapes_textes=preview.get("etapes", []),
                                image_path=image_path,
                            )
                            if created:
                                st.success("Recette importée et sauvegardée !")
                                st.session_state[_keys("wizard_preview")] = None
                                st.session_state[_keys("show_wizard")] = False
                                rerun()
                            else:
                                st.error("Erreur lors de la sauvegarde de la recette importée")
                        except Exception as e:
                            st.error(f"Erreur sauvegarde import: {e}")

        # IA: simple option to generate one sample via service (kept minimal)
        else:
            st.info("Génération IA: créez des recettes via l'IA (option rapide)")
            type_repas = st.selectbox(
                "Type de repas",
                ["petit_dejeuner", "dejeuner", "dîner", "goûter", "aperitif", "dessert"],
                key=_keys("wizard_ia_type"),
            )
            nb = st.number_input(
                "Nombre de recettes à générer",
                min_value=1,
                max_value=5,
                value=1,
                key=_keys("wizard_ia_nb"),
            )
            if st.button("Générer et sauvegarder", key=_keys("wizard_ia_go")):
                service = obtenir_service_recettes()
                if not service:
                    st.error("Service recettes indisponible")
                else:
                    try:
                        suggestions = service.generer_recettes_ia(
                            type_repas=type_repas, nb_recettes=int(nb)
                        )
                        if not suggestions:
                            st.warning("Aucune recette générée")
                        else:
                            created_count = 0
                            for s in suggestions:
                                try:
                                    data = {
                                        "nom": s.nom,
                                        "type_repas": getattr(s, "type_repas", type_repas),
                                        "description": getattr(s, "description", ""),
                                        "temps_preparation": getattr(s, "temps_preparation", 0),
                                        "temps_cuisson": getattr(s, "temps_cuisson", 0),
                                        "portions": getattr(s, "portions", 2),
                                        "difficulte": getattr(s, "difficulte", "moyen"),
                                        "ingredients": getattr(s, "ingredients", []),
                                        "etapes": getattr(s, "etapes", []),
                                    }
                                    service.create_complete(data)
                                    created_count += 1
                                except Exception:
                                    continue
                            st.success(f"{created_count} recette(s) IA ajoutée(s)")
                            st.session_state[_keys("show_wizard")] = False
                            rerun()

                    except Exception as e:
                        st.error(f"Erreur génération IA: {e}")

        # Charger exemples
        if st.button("Charger recettes d'exemple", key=_keys("load_examples")):
            try:
                fpath = Path("data") / "recettes_standard.json"
                if not fpath.exists():
                    st.error("Fichier d'exemples introuvable")
                else:
                    service = obtenir_service_recettes()
                    if not service:
                        st.error("Service recettes indisponible")
                    else:
                        with open(fpath, encoding="utf-8") as fh:
                            data = json.load(fh)
                        count = 0
                        for item in data:
                            try:
                                service.create_complete(item)
                                count += 1
                            except Exception:
                                # Ignorer les erreurs d'une recette et continuer
                                continue
                        st.success(f"{count} recettes d'exemple importées")
                        st.session_state[_keys("show_wizard")] = False
                        rerun()
            except Exception as e:
                st.error(f"Erreur chargement exemples: {e}")

    # Gérer l'état de la vue détails
    if _keys("detail_id") not in st.session_state:
        st.session_state[_keys("detail_id")] = None

    # Si une recette est sélectionnée, afficher son détail
    if st.session_state[_keys("detail_id")] is not None:
        service = obtenir_service_recettes()
        if service is not None:
            recette = service.get_by_id_full(st.session_state[_keys("detail_id")])
            if recette:
                # Bouton retour en haut avec icône visible
                col_retour, col_titre = st.columns([1, 10])
                with col_retour:
                    if st.button("⬅️", help="Retour à la liste", use_container_width=True):
                        st.session_state[_keys("detail_id")] = None
                        rerun()
                with col_titre:
                    st.write(f"**{recette.nom}**")
                st.divider()
                afficher_detail_recette(recette)
                return
        st.error("❌ Recette non trouvée")
        st.session_state[_keys("detail_id")] = None

    # Sous-tabs avec deep linking URL et persistence d'état
    TAB_LABELS = ["📋 Liste", "➕ Ajouter Manuel", "📥 Importer", "⏰ Générer IA", "💬 Assistant"]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tab_liste, tab_ajout, tab_import, tab_ia, tab_chat = st.tabs(TAB_LABELS)

    with tab_liste:
        with error_boundary(titre="Erreur liste recettes"):
            afficher_liste()

    with tab_ajout:
        with error_boundary(titre="Erreur ajout recette"):
            afficher_ajouter_manuel()

    with tab_import:
        with error_boundary(titre="Erreur import recette"):
            afficher_importer()

    with tab_ia:
        with error_boundary(titre="Erreur génération IA"):
            afficher_generer_ia()

    with tab_chat:
        with error_boundary(titre="Erreur assistant cuisine"):
            from src.ui.components import afficher_chat_contextuel

            st.caption("Posez vos questions cuisine à l'assistant IA")
            afficher_chat_contextuel("recettes")


__all__ = [
    "app",
    "afficher_liste",
    "afficher_detail_recette",
    "afficher_ajouter_manuel",
    "afficher_generer_ia",
    "formater_quantite",
]
