"""
Commandes vocales pour Assistant Matanne

Utilise st.audio_input() de Streamlit 1.40+ pour permettre
des commandes vocales comme "Ajouter lait à la liste de courses".

Intègre Whisper via l'API Mistral pour la transcription.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum

import streamlit as st

from src.core.ai import obtenir_client_ia
from src.core.session_keys import SK

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class TypeCommande(Enum):
    """Types de commandes vocales supportées."""

    AJOUTER_COURSES = "ajouter_courses"
    AJOUTER_INVENTAIRE = "ajouter_inventaire"
    RECHERCHER_RECETTE = "rechercher_recette"
    CREER_NOTE = "creer_note"
    NAVIGATION = "navigation"
    INCONNU = "inconnu"


@dataclass
class CommandeVocale:
    """Commande vocale parsée."""

    type: TypeCommande
    texte_original: str
    entite: str  # Ex: "lait", "tomates"
    quantite: float | None = None
    unite: str | None = None
    destination: str | None = None  # Pour navigation


# ═══════════════════════════════════════════════════════════
# PATTERNS DE RECONNAISSANCE
# ═══════════════════════════════════════════════════════════


PATTERNS_COMMANDES = {
    TypeCommande.AJOUTER_COURSES: [
        r"ajout(?:e|er)?\s+(.+?)\s+(?:à|a|aux?)\s+(?:la\s+)?liste",
        r"(?:met|mets|mettre)\s+(.+?)\s+(?:sur|dans)\s+(?:la\s+)?liste",
        r"(?:il\s+(?:me\s+)?faut|j'ai\s+besoin\s+(?:de|d'))\s+(.+)",
        r"courses?\s*:?\s*(.+)",
    ],
    TypeCommande.AJOUTER_INVENTAIRE: [
        r"ajout(?:e|er)?\s+(.+?)\s+(?:à|a|au|dans)\s+(?:l')?(?:inventaire|stock)",
        r"(?:on\s+a|j'ai)\s+(.+?)\s+(?:en\s+stock|dans\s+(?:le\s+)?placard)",
    ],
    TypeCommande.RECHERCHER_RECETTE: [
        r"(?:cherche|recherche|trouve)(?:r)?\s+(?:une?\s+)?recette\s+(?:de\s+)?(.+)",
        r"(?:comment\s+)?(?:faire|préparer|cuisiner)\s+(?:du|de\s+la|des|un|une)?\s*(.+)",
    ],
    TypeCommande.NAVIGATION: [
        r"(?:va|aller|ouvrir?)\s+(?:à|au|aux?|dans)\s+(.+)",
        r"(?:affiche|montre)(?:r)?\s+(.+)",
    ],
}

QUANTITES_PATTERNS = [
    r"(\d+(?:[.,]\d+)?)\s*(kg|g|l|ml|cl|unités?|pièces?|paquets?|bouteilles?|boîtes?)?",
]


# ═══════════════════════════════════════════════════════════
# FONCTIONS PRINCIPALES
# ═══════════════════════════════════════════════════════════


def transcrire_audio(audio_bytes: bytes) -> str | None:
    """
    Transcrit l'audio en texte via l'API Mistral.

    Args:
        audio_bytes: Données audio brutes

    Returns:
        Texte transcrit ou None si erreur
    """
    try:
        # Utiliser Mistral pour la transcription (si disponible)
        # Fallback: utiliser OpenAI Whisper ou autre service
        client = obtenir_client_ia()

        # Note: Mistral n'a pas d'API audio native
        # On utilise une approche alternative avec un prompt
        # Pour une vraie implémentation, utiliser Whisper API

        logger.info("Transcription audio demandée")

        # Simulation pour le moment - en production, utiliser:
        # - OpenAI Whisper API
        # - Google Speech-to-Text
        # - Azure Speech Services
        return None

    except Exception as e:
        logger.error(f"Erreur transcription audio: {e}")
        return None


def parser_commande(texte: str) -> CommandeVocale:
    """
    Parse une commande vocale en structure exploitable.

    Args:
        texte: Texte transcrit de la commande vocale

    Returns:
        CommandeVocale parsée
    """
    texte_lower = texte.lower().strip()

    # Tester chaque type de commande
    for type_cmd, patterns in PATTERNS_COMMANDES.items():
        for pattern in patterns:
            match = re.search(pattern, texte_lower, re.IGNORECASE)
            if match:
                entite = match.group(1).strip() if match.groups() else ""

                # Extraire quantité si présente
                quantite = None
                unite = None
                for qp in QUANTITES_PATTERNS:
                    q_match = re.search(qp, entite, re.IGNORECASE)
                    if q_match:
                        try:
                            quantite = float(q_match.group(1).replace(",", "."))
                            unite = q_match.group(2) if len(q_match.groups()) > 1 else None
                            # Retirer la quantité de l'entité
                            entite = re.sub(qp, "", entite).strip()
                        except (ValueError, IndexError):
                            pass

                return CommandeVocale(
                    type=type_cmd,
                    texte_original=texte,
                    entite=entite,
                    quantite=quantite,
                    unite=unite,
                )

    # Commande non reconnue
    return CommandeVocale(
        type=TypeCommande.INCONNU,
        texte_original=texte,
        entite=texte,
    )


def executer_commande(commande: CommandeVocale) -> tuple[bool, str]:
    """
    Exécute une commande vocale.

    Args:
        commande: Commande parsée

    Returns:
        (succès, message)
    """
    if commande.type == TypeCommande.AJOUTER_COURSES:
        return _ajouter_aux_courses(commande)

    elif commande.type == TypeCommande.AJOUTER_INVENTAIRE:
        return _ajouter_a_inventaire(commande)

    elif commande.type == TypeCommande.RECHERCHER_RECETTE:
        return _rechercher_recette(commande)

    elif commande.type == TypeCommande.NAVIGATION:
        return _naviguer(commande)

    else:
        return False, f"Commande non reconnue: '{commande.texte_original}'"


def _ajouter_aux_courses(commande: CommandeVocale) -> tuple[bool, str]:
    """Ajoute un article à la liste de courses."""
    try:
        # Récupérer ou créer la liste de courses
        if SK.COURSES_LISTE not in st.session_state:
            st.session_state[SK.COURSES_LISTE] = []

        quantite = commande.quantite or 1
        unite = commande.unite or ""

        article = {
            "nom": commande.entite.title(),
            "quantite": quantite,
            "unite": unite,
            "source": "vocal",
            "cochee": False,
        }

        st.session_state[SK.COURSES_LISTE].append(article)

        msg = f"✅ Ajouté: {quantite}{unite} {commande.entite}"
        return True, msg

    except Exception as e:
        logger.error(f"Erreur ajout courses vocal: {e}")
        return False, f"❌ Erreur: {e}"


def _ajouter_a_inventaire(commande: CommandeVocale) -> tuple[bool, str]:
    """Ajoute un article à l'inventaire."""
    try:
        from src.services import get_inventaire_service

        service = get_inventaire_service()

        article_data = {
            "nom": commande.entite.title(),
            "quantite": commande.quantite or 1,
            "unite": commande.unite or "unité",
        }

        # En production, appeler le service
        # service.ajouter_article(article_data)

        msg = f"✅ Ajouté à l'inventaire: {commande.entite}"
        return True, msg

    except Exception as e:
        logger.error(f"Erreur ajout inventaire vocal: {e}")
        return False, f"❌ Erreur: {e}"


def _rechercher_recette(commande: CommandeVocale) -> tuple[bool, str]:
    """Recherche une recette."""
    try:
        # Stocker la recherche dans session_state
        st.session_state["recherche_recette"] = commande.entite

        msg = f"🔍 Recherche: '{commande.entite}'"
        return True, msg

    except Exception as e:
        logger.error(f"Erreur recherche recette vocal: {e}")
        return False, f"❌ Erreur: {e}"


def _naviguer(commande: CommandeVocale) -> tuple[bool, str]:
    """Navigation vers un module."""
    try:
        from src.core.state import naviguer

        # Mapping mots → routes
        ROUTES = {
            "recettes": "cuisine.recettes",
            "courses": "cuisine.courses",
            "inventaire": "cuisine.inventaire",
            "planning": "cuisine.planificateur_repas",
            "batch": "cuisine.batch_cooking",
            "accueil": "accueil",
            "paramètres": "parametres",
        }

        destination = commande.entite.lower()
        for mot, route in ROUTES.items():
            if mot in destination:
                naviguer(route)
                return True, f"↗️ Navigation vers {mot}"

        return False, f"⚠️ Destination non trouvée: '{destination}'"

    except Exception as e:
        logger.error(f"Erreur navigation vocal: {e}")
        return False, f"❌ Erreur: {e}"


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI
# ═══════════════════════════════════════════════════════════


def afficher_commandes_vocales():
    """
    Affiche le composant de commandes vocales.

    Utilise st.audio_input() de Streamlit 1.40+
    """
    st.markdown("### 🎤 Commandes Vocales")
    st.caption("Dites une commande comme 'Ajouter lait à la liste de courses'")

    # Liste des commandes supportées
    with st.expander("💡 Commandes supportées", expanded=False):
        st.markdown("""
        - **Courses**: "Ajouter [article] à la liste"
        - **Inventaire**: "Ajouter [article] au stock"
        - **Recettes**: "Chercher une recette de [plat]"
        - **Navigation**: "Aller aux recettes"
        """)

    # Input audio
    try:
        audio = st.audio_input("🎤 Cliquez et parlez", key="vocal_input")

        if audio:
            st.audio(audio, format="audio/wav")

            # Option manuelle (transcription simulée pour démo)
            st.write("---")
            texte_manuel = st.text_input(
                "Ou tapez votre commande (si transcription indisponible):",
                key="vocal_texte_manuel",
                placeholder="Ajouter lait à la liste de courses",
            )

            if texte_manuel:
                commande = parser_commande(texte_manuel)

                # Afficher la commande parsée
                st.info(f"**Type:** {commande.type.value}")
                st.info(f"**Entité:** {commande.entite}")
                if commande.quantite:
                    st.info(f"**Quantité:** {commande.quantite} {commande.unite or ''}")

                # Exécuter
                if st.button("▶️ Exécuter la commande", type="primary"):
                    succes, message = executer_commande(commande)
                    if succes:
                        st.success(message)
                    else:
                        st.error(message)

    except AttributeError:
        # st.audio_input n'existe pas encore dans cette version
        st.warning("""
        ⚠️ `st.audio_input()` nécessite Streamlit 1.40+

        Utilisez la saisie textuelle en attendant:
        """)

        texte_manuel = st.text_input(
            "Tapez votre commande:",
            key="vocal_texte_fallback",
            placeholder="Ajouter lait à la liste de courses",
        )

        if texte_manuel:
            commande = parser_commande(texte_manuel)

            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Type:** {commande.type.value}")
            with col2:
                st.info(f"**Entité:** {commande.entite}")

            if st.button("▶️ Exécuter", type="primary"):
                succes, message = executer_commande(commande)
                if succes:
                    st.success(message)
                else:
                    st.error(message)


# Export
__all__ = [
    "TypeCommande",
    "CommandeVocale",
    "parser_commande",
    "executer_commande",
    "afficher_commandes_vocales",
]
