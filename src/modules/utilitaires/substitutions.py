"""
Module Substitutions d'Ingrédients — Base de données de remplacement.

Quand il manque un ingrédient, trouvez rapidement par quoi
le remplacer avec les bonnes proportions.
"""

import logging

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("substitutions")

# Base de données des substitutions courantes
SUBSTITUTIONS = {
    "Beurre": [
        {
            "remplacement": "Huile d'olive",
            "proportion": "80% du poids",
            "notes": "Pour cuisson, pas pâtisserie",
        },
        {
            "remplacement": "Huile de coco",
            "proportion": "Même quantité",
            "notes": "Bon pour pâtisserie",
        },
        {
            "remplacement": "Compote de pommes",
            "proportion": "50% du poids",
            "notes": "Gâteaux moelleux, moins gras",
        },
        {
            "remplacement": "Purée d'amande",
            "proportion": "Même quantité",
            "notes": "Riche en nutriments",
        },
        {
            "remplacement": "Margarine",
            "proportion": "Même quantité",
            "notes": "Alternative directe",
        },
    ],
    "Œufs": [
        {"remplacement": "Compote de pommes", "proportion": "60g par œuf", "notes": "Pour gâteaux"},
        {
            "remplacement": "Banane écrasée",
            "proportion": "½ banane par œuf",
            "notes": "Goût banane léger",
        },
        {
            "remplacement": "Graines de lin + eau",
            "proportion": "1 c.à.s. + 3 c.à.s. eau",
            "notes": "Laisser gonfler 5min",
        },
        {
            "remplacement": "Graines de chia + eau",
            "proportion": "1 c.à.s. + 3 c.à.s. eau",
            "notes": "Laisser gonfler 15min",
        },
        {"remplacement": "Yaourt nature", "proportion": "60g par œuf", "notes": "Pour moelleux"},
        {"remplacement": "Tofu soyeux", "proportion": "60g par œuf", "notes": "Texture crémeuse"},
    ],
    "Lait": [
        {"remplacement": "Lait d'avoine", "proportion": "Même quantité", "notes": "Goût neutre"},
        {
            "remplacement": "Lait d'amande",
            "proportion": "Même quantité",
            "notes": "Légèrement sucré",
        },
        {"remplacement": "Lait de coco", "proportion": "Même quantité", "notes": "Goût exotique"},
        {
            "remplacement": "Lait de soja",
            "proportion": "Même quantité",
            "notes": "Riche en protéines",
        },
        {
            "remplacement": "Eau + beurre",
            "proportion": "Même qté eau + 1 c.à.s. beurre",
            "notes": "Dépannage rapide",
        },
    ],
    "Crème fraîche": [
        {"remplacement": "Yaourt grec", "proportion": "Même quantité", "notes": "Plus léger"},
        {
            "remplacement": "Crème de coco",
            "proportion": "Même quantité",
            "notes": "Version végétale",
        },
        {"remplacement": "Fromage blanc", "proportion": "Même quantité", "notes": "Moins gras"},
        {"remplacement": "Ricotta", "proportion": "Même quantité", "notes": "Plus texturé"},
    ],
    "Farine de blé": [
        {"remplacement": "Farine de riz", "proportion": "Même quantité", "notes": "Sans gluten"},
        {
            "remplacement": "Fécule de maïs",
            "proportion": "50% de la quantité",
            "notes": "Pour épaissir",
        },
        {
            "remplacement": "Farine de sarrasin",
            "proportion": "Même quantité",
            "notes": "Goût prononcé",
        },
        {"remplacement": "Poudre d'amande", "proportion": "Même quantité", "notes": "Plus riche"},
        {
            "remplacement": "Farine d'épeautre",
            "proportion": "Même quantité",
            "notes": "Contient du gluten",
        },
    ],
    "Sucre blanc": [
        {
            "remplacement": "Miel",
            "proportion": "75% de la quantité",
            "notes": "Réduire liquide de 25%",
        },
        {
            "remplacement": "Sirop d'érable",
            "proportion": "75% de la quantité",
            "notes": "Goût distinctif",
        },
        {
            "remplacement": "Sucre de coco",
            "proportion": "Même quantité",
            "notes": "Index glycémique bas",
        },
        {"remplacement": "Cassonade", "proportion": "Même quantité", "notes": "Goût caramel"},
        {
            "remplacement": "Compote de pommes",
            "proportion": "Même quantité",
            "notes": "Réduit sucre et gras",
        },
        {
            "remplacement": "Stévia",
            "proportion": "¼ c.à.c. pour 1 c.à.s. sucre",
            "notes": "Très sucrant",
        },
    ],
    "Ail": [
        {
            "remplacement": "Poudre d'ail",
            "proportion": "¼ c.à.c. par gousse",
            "notes": "Goût moins vif",
        },
        {
            "remplacement": "Ail des ours",
            "proportion": "5 feuilles par gousse",
            "notes": "Saison mars-mai",
        },
        {"remplacement": "Échalote", "proportion": "1 petite par gousse", "notes": "Plus doux"},
    ],
    "Oignon": [
        {"remplacement": "Échalote", "proportion": "2 échalotes par oignon", "notes": "Plus fin"},
        {"remplacement": "Poireau", "proportion": "1 blanc de poireau", "notes": "Plus doux"},
        {
            "remplacement": "Poudre d'oignon",
            "proportion": "1 c.à.s. par oignon",
            "notes": "Dépannage",
        },
    ],
    "Vinaigre balsamique": [
        {
            "remplacement": "Vinaigre de cidre + miel",
            "proportion": "Même qté + 1 c.à.c. miel",
            "notes": "Approche du goût",
        },
        {"remplacement": "Jus de citron", "proportion": "Même quantité", "notes": "Plus acide"},
    ],
    "Levure chimique": [
        {
            "remplacement": "Bicarbonate + citron",
            "proportion": "¼ c.à.c. + quelques gouttes",
            "notes": "Par c.à.c. de levure",
        },
        {
            "remplacement": "Blancs d'œufs montés",
            "proportion": "2 blancs",
            "notes": "Donne du volume",
        },
    ],
    "Chapelure": [
        {
            "remplacement": "Flocons d'avoine mixés",
            "proportion": "Même quantité",
            "notes": "Plus nutritif",
        },
        {"remplacement": "Pain rassis mixé", "proportion": "Même quantité", "notes": "Anti-gaspi"},
        {
            "remplacement": "Crackers émiettés",
            "proportion": "Même quantité",
            "notes": "Ajoute du croustillant",
        },
    ],
}


@profiler_rerun("substitutions")
def app():
    """Point d'entrée module Substitutions d'Ingrédients."""
    st.title("🔄 Substitutions d'Ingrédients")
    st.caption("Trouvez par quoi remplacer un ingrédient manquant")

    with error_boundary(titre="Erreur substitutions"):
        # Recherche rapide
        recherche = st.text_input(
            "🔍 Quel ingrédient cherchez-vous à remplacer ?",
            placeholder="Beurre, œufs, lait...",
            key=_keys("recherche"),
        )

        st.divider()

        if recherche:
            resultats = {k: v for k, v in SUBSTITUTIONS.items() if recherche.lower() in k.lower()}
            if resultats:
                for ingredient, subs in resultats.items():
                    _afficher_ingredient(ingredient, subs)
            else:
                st.warning(f"Aucune substitution trouvée pour « {recherche} ».")
                st.info("💡 Parcourez la liste complète ci-dessous.")
                for ingredient, subs in SUBSTITUTIONS.items():
                    _afficher_ingredient(ingredient, subs)
        else:
            for ingredient, subs in SUBSTITUTIONS.items():
                _afficher_ingredient(ingredient, subs)


def _afficher_ingredient(ingredient: str, substitutions: list[dict]):
    """Affiche les substitutions pour un ingrédient."""
    with st.expander(f"🔄 **{ingredient}** ({len(substitutions)} alternatives)"):
        for sub in substitutions:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 2])
                with col1:
                    st.markdown(f"**→ {sub['remplacement']}**")
                with col2:
                    st.caption(f"📏 {sub['proportion']}")
                with col3:
                    st.caption(f"💡 {sub['notes']}")
