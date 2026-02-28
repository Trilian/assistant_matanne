"""
Page Scan Ticket de Caisse — OCR via Pixtral ou saisie texte.

Permet de scanner un ticket de caisse en photo ou de coller
le texte pour extraction automatique des lignes et totaux.
"""

import logging

import streamlit as st

from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("scan_ticket")


def afficher_scan_ticket() -> None:
    """Affiche l'interface complète de scan de ticket de caisse."""
    st.subheader("🧾 Scan Ticket de Caisse")
    st.caption("Scannez ou collez un ticket pour extraire les dépenses automatiquement")

    mode = st.radio(
        "Mode de saisie",
        ["📷 Photo (OCR IA)", "📝 Texte copié-collé"],
        horizontal=True,
        key=_keys("mode"),
    )

    if mode == "📷 Photo (OCR IA)":
        _afficher_mode_photo()
    else:
        _afficher_mode_texte()


def _afficher_mode_photo() -> None:
    """Mode scan photo via Pixtral Vision."""
    uploaded = st.file_uploader(
        "Prends en photo ton ticket",
        type=["jpg", "jpeg", "png", "webp"],
        key=_keys("upload_photo"),
        help="L'IA Pixtral analyse l'image pour extraire les articles et prix.",
    )

    if uploaded is not None:
        # Afficher la photo
        col_img, col_result = st.columns([1, 2])
        with col_img:
            st.image(uploaded, caption="Ticket uploadé", use_container_width=True)

        with col_result:
            if st.button("🔍 Analyser le ticket", key=_keys("analyser_photo"), type="primary"):
                with error_boundary(titre="Erreur OCR"):
                    _analyser_photo(uploaded)


def _analyser_photo(uploaded_file) -> None:
    """Analyse une photo de ticket via Pixtral."""
    import base64

    from src.services.integrations.ticket_caisse import scanner_ticket_vision

    # Convertir en base64
    image_bytes = uploaded_file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    with st.spinner("🤖 Pixtral analyse le ticket..."):
        ticket = scanner_ticket_vision(image_b64)

    _afficher_resultat_ticket(ticket)


def _afficher_mode_texte() -> None:
    """Mode saisie texte copié-collé."""
    texte = st.text_area(
        "Colle le texte de ton ticket ici",
        placeholder="CARREFOUR\nTomates 500g    2.49\nPâtes 500g      1.29\n...",
        height=200,
        key=_keys("texte_ticket"),
    )

    if st.button(
        "🔍 Extraire les données",
        key=_keys("analyser_texte"),
        type="primary",
        disabled=not texte,
    ):
        with error_boundary(titre="Erreur extraction"):
            from src.services.integrations.ticket_caisse import scanner_ticket_texte

            with st.spinner("Analyse du texte..."):
                ticket = scanner_ticket_texte(texte)

            _afficher_resultat_ticket(ticket)


def _afficher_resultat_ticket(ticket) -> None:
    """Affiche le résultat d'un ticket analysé."""
    if not ticket or not ticket.lignes:
        st.warning("Aucun article détecté. Essayez une meilleure photo ou un texte plus lisible.")
        return

    st.success(
        f"✅ {len(ticket.lignes)} article(s) détecté(s) — Total: {ticket.total_calcule:.2f} €"
    )

    if hasattr(ticket, "confiance_ocr") and ticket.confiance_ocr:
        confiance = int(ticket.confiance_ocr * 100)
        st.progress(ticket.confiance_ocr, text=f"Confiance: {confiance}%")

    # Tableau des articles
    import pandas as pd

    df = pd.DataFrame(
        [
            {
                "Article": l.nom,
                "Quantité": l.quantite or 1,
                "Prix unit.": f"{l.prix_unitaire:.2f} €" if l.prix_unitaire else "-",
                "Total": f"{l.prix_total:.2f} €",
            }
            for l in ticket.lignes
        ]
    )

    st.dataframe(df, use_container_width=True, hide_index=True)

    # Actions
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💰 Enregistrer comme dépense", key=_keys("enregistrer_depense")):
            try:
                from src.services.integrations.ticket_caisse import ticket_vers_depenses

                depenses = ticket_vers_depenses(ticket, magasin=ticket.magasin)
                st.success(f"✅ Dépense de {ticket.total_calcule:.2f} € enregistrée !")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

    with col2:
        if st.button("🛒 Ajouter au stock", key=_keys("ajouter_stock")):
            st.info("🔜 Fonctionnalité à venir : ajout automatique à l'inventaire")


__all__ = ["afficher_scan_ticket"]
