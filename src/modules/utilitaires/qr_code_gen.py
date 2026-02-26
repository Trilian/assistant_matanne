"""
Module QR Code Generator — Génération de QR codes multi-usages.

Génère des QR codes pour texte libre, WiFi, liens URL,
recettes à partager, et listes de courses.
"""

import io
import logging

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("qr_code")


def _generer_qr(contenu: str, taille: int = 10) -> bytes | None:
    """Génère un QR code en PNG bytes."""
    try:
        import qrcode
        from qrcode.image.styledpil import StyledPilImage

        qr = qrcode.QRCode(version=1, box_size=taille, border=2)
        qr.add_data(contenu)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        # Fallback: API externe
        try:
            import urllib.parse
            import urllib.request

            encoded = urllib.parse.quote(contenu)
            url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                return resp.read()
        except Exception as e:
            logger.error(f"QR code fallback échoué: {e}")
            return None


@profiler_rerun("qr_code_gen")
def app():
    """Point d'entrée module QR Code."""
    st.title("📱 Générateur de QR Codes")
    st.caption("Créez des QR codes pour partager infos, WiFi, recettes...")

    with error_boundary(titre="Erreur QR code"):
        tab1, tab2, tab3 = st.tabs(["📝 Texte / URL", "📶 WiFi", "🍽️ Recette / Courses"])

        with tab1:
            _qr_texte()
        with tab2:
            _qr_wifi()
        with tab3:
            _qr_recette_courses()


def _qr_texte():
    """QR code pour texte ou URL."""
    st.subheader("📝 Texte ou URL")

    contenu = st.text_area(
        "Contenu à encoder",
        height=100,
        placeholder="https://example.com ou n'importe quel texte",
        key=_keys("texte_contenu"),
    )

    if contenu and st.button("🔲 Générer", key=_keys("gen_texte"), use_container_width=True):
        qr_bytes = _generer_qr(contenu)
        if qr_bytes:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(qr_bytes, caption="QR Code", width=250)
            with col2:
                st.download_button(
                    "⬇️ Télécharger PNG",
                    data=qr_bytes,
                    file_name="qrcode.png",
                    mime="image/png",
                    key=_keys("dl_texte"),
                )
                st.code(contenu, language=None)
        else:
            st.error("Impossible de générer le QR code.")


def _qr_wifi():
    """QR code WiFi (scannez pour se connecter)."""
    st.subheader("📶 QR Code WiFi")
    st.caption("Scannez pour connecter automatiquement un appareil au WiFi")

    col1, col2 = st.columns(2)
    with col1:
        ssid = st.text_input("Nom du réseau (SSID)", key=_keys("wifi_ssid"))
        securite = st.selectbox(
            "Sécurité",
            options=["WPA", "WEP", "nopass"],
            key=_keys("wifi_sec"),
        )
    with col2:
        password = st.text_input(
            "Mot de passe",
            type="password",
            key=_keys("wifi_pass"),
            disabled=securite == "nopass",
        )
        hidden = st.checkbox("Réseau masqué", key=_keys("wifi_hidden"))

    if ssid and st.button("🔲 Générer QR WiFi", key=_keys("gen_wifi"), use_container_width=True):
        # Format WiFi QR standard
        hidden_str = "true" if hidden else "false"
        wifi_str = f"WIFI:T:{securite};S:{ssid};P:{password};H:{hidden_str};;"

        qr_bytes = _generer_qr(wifi_str)
        if qr_bytes:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(qr_bytes, caption=f"WiFi: {ssid}", width=250)
            with col2:
                st.success(f"✅ QR WiFi pour **{ssid}** généré !")
                st.download_button(
                    "⬇️ Télécharger",
                    data=qr_bytes,
                    file_name=f"wifi_{ssid}.png",
                    mime="image/png",
                    key=_keys("dl_wifi"),
                )
                st.info("💡 Imprimez-le et collez-le près du routeur !")


def _qr_recette_courses():
    """QR code pour partager une recette ou une liste de courses."""
    st.subheader("🍽️ Recette ou Liste de Courses")

    mode = st.radio(
        "Type",
        options=["Recette rapide", "Liste de courses"],
        horizontal=True,
        key=_keys("rc_mode"),
    )

    if mode == "Recette rapide":
        nom = st.text_input("Nom de la recette", key=_keys("rc_nom"))
        ingredients = st.text_area(
            "Ingrédients (un par ligne)",
            height=100,
            key=_keys("rc_ingredients"),
        )
        instructions = st.text_area("Instructions", height=100, key=_keys("rc_instructions"))

        if nom and st.button("🔲 Générer", key=_keys("gen_recette"), use_container_width=True):
            texte = (
                f"🍽️ {nom}\n\n📋 Ingrédients:\n{ingredients}\n\n👨‍🍳 Préparation:\n{instructions}"
            )
            qr_bytes = _generer_qr(texte)
            if qr_bytes:
                st.image(qr_bytes, caption=nom, width=250)
                st.download_button(
                    "⬇️ Télécharger",
                    data=qr_bytes,
                    file_name=f"recette_{nom.replace(' ', '_')}.png",
                    mime="image/png",
                    key=_keys("dl_recette"),
                )
    else:
        articles = st.text_area(
            "Articles (un par ligne)",
            height=150,
            placeholder="Pain\nLait\nOeufs\nFromage",
            key=_keys("rc_articles"),
        )

        if articles and st.button("🔲 Générer", key=_keys("gen_courses"), use_container_width=True):
            texte = f"🛒 Liste de courses:\n{articles}"
            qr_bytes = _generer_qr(texte)
            if qr_bytes:
                st.image(qr_bytes, caption="Liste de courses", width=250)
                st.download_button(
                    "⬇️ Télécharger",
                    data=qr_bytes,
                    file_name="liste_courses.png",
                    mime="image/png",
                    key=_keys("dl_courses"),
                )
