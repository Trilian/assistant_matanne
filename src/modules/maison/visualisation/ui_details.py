"""Panneau de détails d'une pièce sélectionnée."""

from __future__ import annotations

import streamlit as st

from .constants import EMOJIS_PIECES, ETAGE_LABELS, STATUT_OBJET_LABELS


def afficher_details_piece(piece_id: int, service):
    """Affiche les détails complets d'une pièce.

    Args:
        piece_id: ID de la pièce.
        service: VisualisationService.
    """
    # Charger les données de la pièce
    pieces = service.obtenir_pieces_avec_details()
    piece = next((p for p in pieces if p["id"] == piece_id), None)

    if not piece:
        st.warning("Pièce non trouvée.")
        return

    type_p = piece.get("type_piece", "autre")
    emoji = EMOJIS_PIECES.get(type_p, "🏠")
    etage_label = ETAGE_LABELS.get(piece["etage"], f"Étage {piece['etage']}")

    # En-tête
    st.markdown(
        f"## {emoji} {piece['nom']}\n"
        f"*{etage_label} · {piece['superficie_m2']}m² · "
        f"{piece['nb_objets']} objets · {piece['nb_travaux']} travaux*"
    )

    st.divider()

    # Sous-onglets
    sub1, sub2, sub3 = st.tabs(["🔨 Travaux", "📦 Objets & Meubles", "🧹 Entretien"])

    with sub1:
        _afficher_travaux(piece_id, service)

    with sub2:
        _afficher_objets(piece_id, service)

    with sub3:
        _afficher_entretien(piece)


def _afficher_travaux(piece_id: int, service):
    """Timeline des travaux pour une pièce."""
    historique = service.obtenir_historique_piece(piece_id)

    if not historique:
        st.info("Aucun travail enregistré pour cette pièce.")
        return

    cout_total = sum(v["cout_total"] for v in historique)
    st.metric("💰 Coût total travaux", f"{cout_total:.0f}€")

    for v in historique:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**v{v['version']} — {v['titre']}**")
                st.caption(f"📅 {v['date_modification']} · {v['type_modification']}")
                if v["description"]:
                    st.write(v["description"])

                # Détails des coûts
                if v["couts_details"]:
                    for c in v["couts_details"]:
                        fournisseur = f" ({c['fournisseur']})" if c["fournisseur"] else ""
                        st.caption(f"  💶 {c['montant']:.0f}€ — {c['libelle']}{fournisseur}")

            with col2:
                if v["cout_total"]:
                    st.metric("Coût", f"{v['cout_total']:.0f}€")

                # Photos avant/après
                if v["photo_avant_url"]:
                    try:
                        st.image(v["photo_avant_url"], caption="Avant", width=120)
                    except Exception:
                        st.caption("📷 Photo avant indisponible")
                if v["photo_apres_url"]:
                    try:
                        st.image(v["photo_apres_url"], caption="Après", width=120)
                    except Exception:
                        st.caption("📷 Photo après indisponible")


def _afficher_objets(piece_id: int, service):
    """Liste des objets et meubles dans la pièce."""
    objets = service.obtenir_objets_piece(piece_id)

    if not objets:
        st.info("Aucun objet enregistré dans cette pièce.")
        return

    # Stats rapides
    nb_ok = sum(1 for o in objets if o["statut"] == "fonctionne")
    nb_pb = len(objets) - nb_ok
    cols = st.columns(3)
    with cols[0]:
        st.metric("📦 Total", len(objets))
    with cols[1]:
        st.metric("✅ Fonctionnels", nb_ok)
    with cols[2]:
        st.metric("⚠️ À traiter", nb_pb)

    # Liste
    for o in objets:
        statut_label = STATUT_OBJET_LABELS.get(o["statut"], o["statut"])
        prix_str = f" · {o['prix_achat']:.0f}€" if o["prix_achat"] else ""
        marque_str = f" · {o['marque']}" if o["marque"] else ""

        with st.container(border=True):
            st.markdown(f"**{o['nom']}** {statut_label}{marque_str}{prix_str}")
            if o["categorie"]:
                st.caption(f"Catégorie: {o['categorie']}")
            if o["priorite_remplacement"]:
                st.caption(f"Priorité remplacement: {o['priorite_remplacement']}")


def _afficher_entretien(piece: dict):
    """Infos entretien pour la pièce (basé sur les données enrichies)."""
    retard = piece.get("taches_retard", 0)

    if retard > 0:
        st.warning(f"⚠️ {retard} tâche(s) d'entretien en retard !")
    else:
        st.success("✅ Entretien à jour")

    st.caption(
        "Les tâches d'entretien sont gérées dans le module **Entretien**. "
        "Allez dans 🏡 Entretien pour plus de détails."
    )
