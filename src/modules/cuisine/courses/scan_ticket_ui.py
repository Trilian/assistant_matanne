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

    st.session_state[_keys("ticket_resultat")] = ticket
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

            st.session_state[_keys("ticket_resultat")] = ticket
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
                "Article": l.article,
                "Quantité": l.quantite or 1,
                "Prix unit.": f"{l.prix:.2f} €" if l.prix else "-",
                "Total": f"{l.prix * (l.quantite or 1):.2f} €",
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

                ticket_vers_depenses(ticket, magasin=ticket.magasin)
                st.success(f"✅ Dépense de {ticket.total_calcule:.2f} € enregistrée !")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")

    with col2:
        if st.button("🛒 Ajouter au stock", key=_keys("ajouter_stock")):
            st.session_state[_keys("show_checkout")] = True
            st.rerun()

    # Confirmation checkout (visible après clic)
    if st.session_state.get(_keys("show_checkout")):
        _afficher_checkout_confirmation(ticket)


def _afficher_checkout_confirmation(ticket) -> None:
    """Sélection des articles du ticket à ajouter au stock."""
    st.divider()
    st.subheader("📦 Sélectionner les articles à ajouter au stock")

    selected_lines = {}
    for i, ligne in enumerate(ticket.lignes):
        label = f"{ligne.article}  ×{ligne.quantite or 1}"
        checked = st.checkbox(label, value=True, key=_keys(f"checkout_ligne_{i}"))
        if checked:
            selected_lines[i] = ligne

    col_ok, col_cancel = st.columns(2)
    with col_ok:
        if st.button("✅ Confirmer l'ajout", key=_keys("confirmer_checkout"), type="primary"):
            if selected_lines:
                _executer_checkout_ticket(list(selected_lines.values()))
            else:
                st.warning("Sélectionnez au moins un article.")
    with col_cancel:
        if st.button("❌ Annuler", key=_keys("annuler_checkout")):
            st.session_state[_keys("show_checkout")] = False
            st.rerun()


def _executer_checkout_ticket(lignes: list) -> None:
    """Écrit les lignes sélectionnées dans l'inventaire (matching par nom d'ingrédient)."""
    from src.core.db import obtenir_contexte_db
    from src.core.models import ArticleInventaire, HistoriqueInventaire, Ingredient

    ajoutes: list[str] = []
    non_trouves: list[str] = []

    try:
        with obtenir_contexte_db() as session:
            for ligne in lignes:
                nom = ligne.article.strip()
                ingredient = (
                    session.query(Ingredient)
                    .filter(Ingredient.nom.ilike(f"%{nom}%"))
                    .first()
                )

                if not ingredient:
                    non_trouves.append(nom)
                    continue

                quantite = float(ligne.quantite or 1)
                inv = (
                    session.query(ArticleInventaire)
                    .filter(ArticleInventaire.ingredient_id == ingredient.id)
                    .first()
                )

                if inv:
                    quantite_avant = float(inv.quantite or 0)
                    inv.quantite = quantite_avant + quantite
                    session.add(
                        HistoriqueInventaire(
                            article_id=inv.id,
                            ingredient_id=ingredient.id,
                            type_modification="modification",
                            quantite_avant=quantite_avant,
                            quantite_apres=inv.quantite,
                            notes="Ajout depuis scan ticket caisse",
                        )
                    )
                else:
                    inv = ArticleInventaire(
                        ingredient_id=ingredient.id,
                        quantite=quantite,
                        quantite_min=1.0,
                    )
                    session.add(inv)
                    session.flush()
                    session.add(
                        HistoriqueInventaire(
                            article_id=inv.id,
                            ingredient_id=ingredient.id,
                            type_modification="ajout",
                            quantite_avant=0,
                            quantite_apres=quantite,
                            notes="Ajout depuis scan ticket caisse",
                        )
                    )

                ajoutes.append(ingredient.nom)

            session.commit()

        if ajoutes:
            st.success(f"✅ {len(ajoutes)} article(s) ajouté(s) au stock : {', '.join(ajoutes)}")
        if non_trouves:
            st.warning(
                f"⚠️ {len(non_trouves)} article(s) non trouvé(s) dans l'inventaire "
                f"(introuvables par nom) : {', '.join(non_trouves)}"
            )

        st.session_state[_keys("show_checkout")] = False

    except Exception as e:
        logger.error("Erreur checkout ticket: %s", e)
        st.error(f"❌ Erreur lors de la mise à jour du stock : {e}")


__all__ = ["afficher_scan_ticket"]
