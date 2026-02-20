"""Entretien - Onglets de gestion des données (tâches, inventaire, pièces)."""

import logging
from datetime import date

import streamlit as st

from src.core.session_keys import SK
from src.ui import etat_vide

from .data import charger_catalogue_entretien
from .logic import generer_taches_entretien
from .ui import afficher_piece_card, afficher_stats_rapides, afficher_tache_entretien

logger = logging.getLogger(__name__)


def onglet_taches(mes_objets: list[dict], historique: list[dict]):
    """Onglet des tâches automatiques."""
    st.subheader("🎯 Tâches d'entretien")

    taches = generer_taches_entretien(mes_objets, historique)

    if not taches:
        st.success("✨ **Maison impeccable !** Tout est à jour.")
        st.info(
            "Les tâches apparaissent automatiquement selon vos équipements et leur calendrier d'entretien."
        )
        return

    # Stats rapides
    afficher_stats_rapides(taches)

    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        filtre_piece = st.selectbox(
            "Filtrer par pièce",
            ["Toutes"] + list(set(t.get("piece", "") for t in taches if t.get("piece"))),
        )
    with col2:
        filtre_priorite = st.selectbox(
            "Filtrer par priorité", ["Toutes", "Urgente", "Haute", "Moyenne"]
        )

    # Appliquer filtres
    taches_filtrees = taches
    if filtre_piece != "Toutes":
        taches_filtrees = [t for t in taches_filtrees if t.get("piece") == filtre_piece]
    if filtre_priorite != "Toutes":
        taches_filtrees = [
            t for t in taches_filtrees if t.get("priorite") == filtre_priorite.lower()
        ]

    st.divider()

    # Afficher les tâches groupées par catégorie
    categories = {}
    for t in taches_filtrees:
        cat = t.get("categorie_id", "divers")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(t)

    catalogue = charger_catalogue_entretien()

    for cat_id, cat_taches in categories.items():
        cat_data = catalogue.get("categories", {}).get(cat_id, {})

        st.markdown(
            f"""
        <div class="categorie-header">
            <span class="icon">{cat_data.get("icon", "📦")}</span>
            <span class="title">{cat_id.replace("_", " ").capitalize()} ({len(cat_taches)})</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

        for i, tache in enumerate(cat_taches):
            done = afficher_tache_entretien(tache, f"{cat_id}_{i}")
            if done:
                # Enregistrer dans l'historique
                nouvelle_entree = {
                    "objet_id": tache.get("objet_id"),
                    "tache_nom": tache.get("tache_nom"),
                    "date": date.today().isoformat(),
                }
                historique.append(nouvelle_entree)
                st.session_state.historique_entretien = historique
                st.toast(f"✅ {tache['tache_nom']} accompli !")
                st.rerun()


def onglet_inventaire(mes_objets: list[dict]):
    """Onglet de gestion de l'inventaire."""
    st.subheader("📦 Mon Inventaire")

    catalogue = charger_catalogue_entretien()

    # Bouton ajouter
    if st.button("➕ Ajouter un équipement", type="primary", use_container_width=True):
        st.session_state.entretien_mode_ajout = True

    # Mode ajout
    if st.session_state.get(SK.ENTRETIEN_MODE_AJOUT):
        st.markdown("### Ajouter un nouvel équipement")

        with st.form("form_ajout_objet"):
            # Sélection catégorie
            categories = catalogue.get("categories", {})
            cat_options = {
                k: f"{v.get('icon', '📦')} {k.replace('_', ' ').capitalize()}"
                for k, v in categories.items()
            }
            categorie_sel = st.selectbox(
                "Catégorie", options=list(cat_options.keys()), format_func=lambda x: cat_options[x]
            )

            # Sélection objet
            objets_cat = categories.get(categorie_sel, {}).get("objets", {})
            obj_options = {k: v.get("nom", k) for k, v in objets_cat.items()}
            objet_sel = st.selectbox(
                "Type d'équipement",
                options=list(obj_options.keys()),
                format_func=lambda x: obj_options[x],
            )

            # Sélection pièce
            pieces = catalogue.get("pieces_type", {})
            piece_options = {
                k: f"{v.get('icon', '🏠')} {v.get('nom', k)}" for k, v in pieces.items()
            }
            piece_sel = st.selectbox(
                "Pièce", options=list(piece_options.keys()), format_func=lambda x: piece_options[x]
            )

            # Détails optionnels
            col1, col2 = st.columns(2)
            with col1:
                nom_perso = st.text_input(
                    "Nom personnalisé (optionnel)", placeholder="Ex: Frigo cuisine principale"
                )
            with col2:
                date_achat = st.date_input("Date d'achat (optionnel)", value=None)

            marque = st.text_input("Marque/Modèle (optionnel)")

            if st.form_submit_button("✅ Ajouter", type="primary"):
                nouvel_objet = {
                    "objet_id": objet_sel,
                    "categorie_id": categorie_sel,
                    "piece": piece_options[piece_sel].split(" ", 1)[-1] if piece_sel else "",
                    "piece_id": piece_sel,
                    "nom_perso": nom_perso or None,
                    "date_achat": date_achat.isoformat() if date_achat else None,
                    "marque": marque or None,
                    "date_ajout": date.today().isoformat(),
                }
                mes_objets.append(nouvel_objet)
                st.session_state.mes_objets_entretien = mes_objets
                st.session_state.entretien_mode_ajout = False
                st.success(f"✅ {obj_options[objet_sel]} ajouté !")
                st.rerun()

        if st.button("❌ Annuler"):
            st.session_state.entretien_mode_ajout = False
            st.rerun()

    else:
        # Afficher l'inventaire existant
        if not mes_objets:
            st.info(
                "📦 Votre inventaire est vide. Ajoutez vos équipements pour générer automatiquement les tâches d'entretien."
            )

            # Suggestion rapide
            st.markdown("### 💡 Ajout rapide par pièce")

            pieces = catalogue.get("pieces_type", {})
            cols = st.columns(3)

            for i, (piece_id, piece_data) in enumerate(pieces.items()):
                with cols[i % 3]:
                    if st.button(
                        f"{piece_data.get('icon', '🏠')} {piece_data.get('nom', piece_id)}",
                        key=f"quick_{piece_id}",
                        use_container_width=True,
                    ):
                        # Ajouter les objets courants de cette pièce
                        objets_courants = piece_data.get("objets_courants", [])
                        for obj_id in objets_courants:
                            # Trouver la catégorie de l'objet
                            for cat_id, cat_data in catalogue.get("categories", {}).items():
                                if obj_id in cat_data.get("objets", {}):
                                    mes_objets.append(
                                        {
                                            "objet_id": obj_id,
                                            "categorie_id": cat_id,
                                            "piece": piece_data.get("nom", piece_id),
                                            "piece_id": piece_id,
                                            "date_ajout": date.today().isoformat(),
                                        }
                                    )
                                    break

                        st.session_state.mes_objets_entretien = mes_objets
                        st.success(
                            f"✅ {len(objets_courants)} équipements ajoutés pour {piece_data.get('nom')} !"
                        )
                        st.rerun()
            return

        # Grouper par pièce
        par_piece = {}
        for obj in mes_objets:
            piece = obj.get("piece", "Non assigné")
            if piece not in par_piece:
                par_piece[piece] = []
            par_piece[piece].append(obj)

        for piece, objets in par_piece.items():
            with st.expander(f"🏠 **{piece}** ({len(objets)} équipements)", expanded=True):
                for i, obj in enumerate(objets):
                    objet_data = None
                    for cat_data in catalogue.get("categories", {}).values():
                        if obj["objet_id"] in cat_data.get("objets", {}):
                            objet_data = cat_data["objets"][obj["objet_id"]]
                            break

                    nom = obj.get("nom_perso") or (
                        objet_data.get("nom") if objet_data else obj["objet_id"]
                    )
                    nb_taches = len(objet_data.get("taches", [])) if objet_data else 0

                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(
                            f"""
                        <div class="objet-inventaire">
                            <div class="icon">{catalogue.get("categories", {}).get(obj.get("categorie_id"), {}).get("icon", "📦")}</div>
                            <div class="info">
                                <div class="nom">{nom}</div>
                                <div class="piece">{obj.get("marque", "") or "Marque non renseignée"}</div>
                            </div>
                            <div class="stats">
                                <div class="taches-count">{nb_taches} tâches auto</div>
                            </div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    with col2:
                        if st.button("🗑️", key=f"del_obj_{piece}_{i}", help="Supprimer"):
                            # Trouver et supprimer l'objet
                            idx = mes_objets.index(obj)
                            mes_objets.pop(idx)
                            st.session_state.mes_objets_entretien = mes_objets
                            st.rerun()


def onglet_pieces(mes_objets: list[dict], historique: list[dict]):
    """Onglet vue par pièces."""
    st.subheader("🏠 Vue par pièces")

    catalogue = charger_catalogue_entretien()
    taches = generer_taches_entretien(mes_objets, historique)

    # Compter les tâches par pièce
    taches_par_piece = {}
    for t in taches:
        piece = t.get("piece", "Non assigné")
        if piece not in taches_par_piece:
            taches_par_piece[piece] = 0
        taches_par_piece[piece] += 1

    # Grille des pièces
    pieces = catalogue.get("pieces_type", {})

    cols = st.columns(4)
    for i, (piece_id, piece_data) in enumerate(pieces.items()):
        piece_nom = piece_data.get("nom", piece_id)
        nb_taches = taches_par_piece.get(piece_nom, 0)

        with cols[i % 4]:
            # Card cliquable
            afficher_piece_card(piece_id, piece_data, nb_taches)

            if st.button("Voir", key=f"voir_{piece_id}", use_container_width=True):
                st.session_state.piece_selectionnee = piece_nom

    # Détail d'une pièce sélectionnée
    if st.session_state.get(SK.PIECE_SELECTIONNEE):
        piece = st.session_state.piece_selectionnee

        st.divider()
        st.markdown(f"### 📍 {piece}")

        # Tâches de cette pièce
        taches_piece = [t for t in taches if t.get("piece") == piece]

        if taches_piece:
            for i, tache in enumerate(taches_piece):
                done = afficher_tache_entretien(tache, f"piece_{i}")
                if done:
                    historique.append(
                        {
                            "objet_id": tache.get("objet_id"),
                            "tache_nom": tache.get("tache_nom"),
                            "date": date.today().isoformat(),
                        }
                    )
                    st.session_state.historique_entretien = historique
                    st.toast(f"✅ {tache['tache_nom']} accompli !")
                    st.rerun()
        else:
            st.success(f"✨ Tout est à jour dans {piece} !")

        if st.button("← Retour"):
            del st.session_state.piece_selectionnee
            st.rerun()
