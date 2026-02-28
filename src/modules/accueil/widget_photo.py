"""
Widget photo souvenir du jour.

Affiche une photo aléatoire depuis le dossier data/photos/famille/
avec date et légende. Supporte le mode "Il y a X mois/ans...".

Architecture: dossier local avec métadonnées JSON optionnelles.
Le dossier est créé automatiquement si absent.
"""

import json
import logging
import random
from datetime import date, datetime
from pathlib import Path

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur, Espacement, Rayon
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

_keys = KeyNamespace("photo_souvenir")

# Dossier photos famille
PHOTOS_DIR = Path("data/photos/famille")
METADATA_FILE = PHOTOS_DIR / "metadata.json"
EXTENSIONS_PHOTOS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


# ═══════════════════════════════════════════════════════════
# LOGIQUE MÉTIER
# ═══════════════════════════════════════════════════════════


def _initialiser_dossier():
    """Crée le dossier photos et le fichier metadata si absents."""
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    if not METADATA_FILE.exists():
        metadata = {
            "_description": "Métadonnées des photos famille. Ajoutez des entrées manuellement.",
            "_format": {
                "nom_fichier.jpg": {
                    "date": "YYYY-MM-DD",
                    "legende": "Description de la photo",
                    "personnes": ["Prénom1", "Prénom2"],
                }
            },
            "exemple.jpg": {
                "date": "2024-12-25",
                "legende": "Noël en famille 🎄",
                "personnes": ["Matanne", "Jules"],
            },
        }
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)


def _charger_metadata() -> dict:
    """Charge les métadonnées des photos."""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, encoding="utf-8") as f:
                data = json.load(f)
                # Filtrer les clés qui commencent par _
                return {k: v for k, v in data.items() if not k.startswith("_")}
        except Exception as e:
            logger.debug(f"Erreur lecture metadata: {e}")
    return {}


def _lister_photos() -> list[Path]:
    """Liste toutes les photos du dossier."""
    if not PHOTOS_DIR.exists():
        return []
    return [f for f in PHOTOS_DIR.iterdir() if f.suffix.lower() in EXTENSIONS_PHOTOS]


def _choisir_photo_aleatoire() -> dict | None:
    """Choisit une photo aléatoire avec ses métadonnées.

    Returns:
        Dict {path, date, legende, personnes, il_y_a} ou None.
    """
    photos = _lister_photos()
    if not photos:
        return None

    # Seed basée sur le jour pour garder la même photo toute la journée
    jour_seed = date.today().toordinal()
    rng = random.Random(jour_seed)

    # Prendre en compte le compteur de rafraîchissement
    refresh_count = st.session_state.get(_keys("refresh_count"), 0)
    rng = random.Random(jour_seed + refresh_count)

    photo = rng.choice(photos)
    metadata = _charger_metadata()
    meta = metadata.get(photo.name, {})

    # Calculer "il y a..."
    il_y_a = ""
    if meta.get("date"):
        try:
            photo_date = datetime.strptime(meta["date"], "%Y-%m-%d").date()
            diff = date.today() - photo_date
            if diff.days > 365:
                annees = diff.days // 365
                il_y_a = f"Il y a {annees} an{'s' if annees > 1 else ''}"
            elif diff.days > 30:
                mois = diff.days // 30
                il_y_a = f"Il y a {mois} mois"
            elif diff.days > 0:
                il_y_a = f"Il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
            else:
                il_y_a = "Aujourd'hui"
        except ValueError:
            pass

    return {
        "path": photo,
        "date": meta.get("date", ""),
        "legende": meta.get("legende", ""),
        "personnes": meta.get("personnes", []),
        "il_y_a": il_y_a,
    }


# ═══════════════════════════════════════════════════════════
# WIDGET UI
# ═══════════════════════════════════════════════════════════


@ui_fragment
def afficher_photo_souvenir():
    """Affiche le widget photo souvenir du jour."""
    _initialiser_dossier()

    photo = _choisir_photo_aleatoire()

    container_cls = StyleSheet.create_class(
        {
            "background": "linear-gradient(135deg, #F3E5F5, #E8EAF6)",
            "border-radius": Rayon.XL,
            "padding": Espacement.LG,
            "border-left": f"4px solid {Couleur.ACCENT}",
            "margin-bottom": Espacement.MD,
            "text-align": "center",
        }
    )

    StyleSheet.inject()

    st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)

    st.markdown("### 📸 Souvenir du jour")

    # Upload simple
    uploaded = st.file_uploader("Ajouter une photo", type=["jpg", "jpeg", "png", "webp", "gif"])
    if uploaded:
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
        dest = PHOTOS_DIR / uploaded.name
        # avoid overwrite
        if dest.exists():
            base = dest.stem
            ext = dest.suffix
            i = 1
            while (PHOTOS_DIR / f"{base}_{i}{ext}").exists():
                i += 1
            dest = PHOTOS_DIR / f"{base}_{i}{ext}"
        with open(dest, "wb") as f:
            f.write(uploaded.getbuffer())
        # update metadata minimal entry
        meta = _charger_metadata()
        meta.setdefault(dest.name, {})
        _initialiser_dossier()
        try:
            # write full metadata file preserving header keys
            if METADATA_FILE.exists():
                with open(METADATA_FILE, encoding="utf-8") as fh:
                    raw = json.load(fh)
            else:
                raw = {}
            raw[dest.name] = meta.get(dest.name, {})
            with open(METADATA_FILE, "w", encoding="utf-8") as fh:
                json.dump(raw, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass
        st.success("Photo ajoutée !")

    if photo:
        # Afficher la photo
        try:
            st.image(
                str(photo["path"]),
                use_container_width=True,
            )
        except Exception as e:
            logger.debug(f"Erreur affichage photo: {e}")
            st.info("📷 Photo non disponible")

        # Légende et métadonnées
        if photo.get("il_y_a"):
            st.markdown(
                f'<p style="color: {Couleur.ACCENT}; font-weight: 600; '
                f'font-size: 0.9rem;">📅 {photo["il_y_a"]}</p>',
                unsafe_allow_html=True,
            )

        if photo.get("legende"):
            st.markdown(f"*{photo['legende']}*")

        if photo.get("personnes"):
            personnes_str = " • ".join(f"👤 {p}" for p in photo["personnes"])
            st.caption(personnes_str)

        # Bouton rafraîchir
        if st.button("🔄 Autre souvenir", key=_keys("refresh")):
            count = st.session_state.get(_keys("refresh_count"), 0)
            st.session_state[_keys("refresh_count")] = count + 1
            from src.core.state import rerun

            rerun()
    else:
        st.markdown(
            f'<p style="color: {Sem.ON_SURFACE_SECONDARY}; font-style: italic;">'
            "Ajoutez des photos dans <code>data/photos/famille/</code><br>"
            "pour voir vos souvenirs ici ! 📷"
            "</p>",
            unsafe_allow_html=True,
        )
        st.caption("💡 Ajoutez un fichier `metadata.json` pour les légendes et dates")

    st.markdown("</div>", unsafe_allow_html=True)


__all__ = ["afficher_photo_souvenir"]
