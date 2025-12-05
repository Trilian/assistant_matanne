"""
Module Inventaire Intelligent
Gestion complète des stocks avec IA intégrée
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import asyncio
from typing import List, Dict, Optional, Tuple

from src.core.database import get_db_context
from src.core.models import (
    Ingredient, ArticleInventaire, ArticleCourses,
    Recette, RecetteIngredient
)
from src.core.ai_agent import AgentIA


# ===================================
# CONSTANTES & CONFIGURATION
# ===================================

CATEGORIES = [
    "Légumes", "Fruits", "Féculents", "Protéines",
    "Laitier", "Épices", "Huiles", "Conserves", "Autre"
]

EMPLACEMENTS = [
    "Frigo", "Congélateur", "Placard", "Cave", "Autre"
]

UNITES = [
    "pcs", "kg", "g", "L", "mL", "sachets", "boîtes", "botte"
]

# Seuils d'alerte
JOURS_PEREMPTION_ALERTE = 7
STATUT_COLORS = {
    "ok": "#d4edda",
    "sous_seuil": "#fff3cd",
    "peremption_proche": "#f8d7da",
    "critique": "#dc3545"
}


# ===================================
# HELPERS - CALCUL STATUTS
# ===================================

def calculer_statut_article(row: pd.Series) -> Tuple[str, str, str]:
    """
    Retourne (statut, couleur, icone) pour un article

    Priorités:
    1. Critique = sous seuil ET péremption proche
    2. Péremption proche
    3. Sous seuil
    4. OK
    """
    today = date.today()

    # Vérifier sous seuil
    sous_seuil = row["quantite"] < row["seuil"]

    # Vérifier péremption
    peremption_proche = False
    if row["peremption"] != "—":
        try:
            date_peremption = datetime.strptime(row["peremption"], "%d/%m/%Y").date()
            jours_restants = (date_peremption - today).days
            peremption_proche = 0 <= jours_restants <= JOURS_PEREMPTION_ALERTE
        except:
            pass

    # Déterminer le statut
    if sous_seuil and peremption_proche:
        return ("critique", STATUT_COLORS["critique"], "🔴")
    elif peremption_proche:
        return ("peremption_proche", STATUT_COLORS["peremption_proche"], "⏳")
    elif sous_seuil:
        return ("sous_seuil", STATUT_COLORS["sous_seuil"], "⚠️")
    else:
        return ("ok", STATUT_COLORS["ok"], "✅")


def get_jours_avant_peremption(date_str: str) -> Optional[int]:
    """Calcule le nombre de jours avant péremption"""
    if date_str == "—":
        return None

    try:
        date_peremption = datetime.strptime(date_str, "%d/%m/%Y").date()
        delta = (date_peremption - date.today()).days
        return delta
    except:
        return None


# ===================================
# HELPERS - CRUD INVENTAIRE
# ===================================

def charger_inventaire(
        search: str = "",
        sous_seuil_only: bool = False,
        peremption_proche_only: bool = False,
        categorie: str = None,
        emplacement: str = None
) -> pd.DataFrame:
    """Charge l'inventaire avec filtres multiples"""
    with get_db_context() as db:
        query = db.query(
            ArticleInventaire.id,
            Ingredient.nom,
            Ingredient.categorie,
            ArticleInventaire.quantite,
            Ingredient.unite,
            ArticleInventaire.quantite_min.label("seuil"),
            ArticleInventaire.emplacement,
            ArticleInventaire.date_peremption,
            ArticleInventaire.derniere_maj
        ).join(
            Ingredient, ArticleInventaire.ingredient_id == Ingredient.id
        )

        # Filtres
        if search:
            query = query.filter(Ingredient.nom.ilike(f"%{search}%"))

        if sous_seuil_only:
            query = query.filter(ArticleInventaire.quantite < ArticleInventaire.quantite_min)

        if categorie and categorie != "Toutes":
            query = query.filter(Ingredient.categorie == categorie)

        if emplacement and emplacement != "Tous":
            query = query.filter(ArticleInventaire.emplacement == emplacement)

        items = query.order_by(Ingredient.nom).all()

        df = pd.DataFrame([{
            "id": item.id,
            "nom": item.nom,
            "categorie": item.categorie or "—",
            "quantite": item.quantite,
            "unite": item.unite,
            "seuil": item.seuil,
            "emplacement": item.emplacement or "—",
            "peremption": item.date_peremption.strftime("%d/%m/%Y") if item.date_peremption else "—",
            "updated": item.derniere_maj
        } for item in items])

        # Filtrer péremption proche côté client
        if peremption_proche_only and not df.empty:
            df["jours_restants"] = df["peremption"].apply(get_jours_avant_peremption)
            df = df[
                (df["jours_restants"].notna()) &
                (df["jours_restants"] >= 0) &
                (df["jours_restants"] <= JOURS_PEREMPTION_ALERTE)
                ]
            df = df.drop(columns=["jours_restants"])

        return df


def ajouter_ou_modifier_article(
        nom: str,
        categorie: str,
        quantite: float,
        unite: str,
        seuil: float,
        emplacement: str = None,
        peremption: date = None,
        article_id: int = None
) -> int:
    """Ajoute ou modifie un article d'inventaire"""
    with get_db_context() as db:
        # Trouver ou créer l'ingrédient
        ingredient = db.query(Ingredient).filter(
            Ingredient.nom == nom
        ).first()

        if not ingredient:
            ingredient = Ingredient(
                nom=nom,
                unite=unite,
                categorie=categorie
            )
            db.add(ingredient)
            db.flush()

        if article_id:
            # Modification
            article = db.query(ArticleInventaire).filter(
                ArticleInventaire.id == article_id
            ).first()

            if article:
                article.quantite = quantite
                article.quantite_min = seuil
                article.emplacement = emplacement
                article.date_peremption = peremption
                article.derniere_maj = datetime.now()
        else:
            # Ajout (vérifier si n'existe pas déjà)
            article_existant = db.query(ArticleInventaire).filter(
                ArticleInventaire.ingredient_id == ingredient.id
            ).first()

            if article_existant:
                # Mise à jour au lieu d'ajout
                article_existant.quantite += quantite
                article_existant.derniere_maj = datetime.now()
                article = article_existant
            else:
                # Création
                article = ArticleInventaire(
                    ingredient_id=ingredient.id,
                    quantite=quantite,
                    quantite_min=seuil,
                    emplacement=emplacement,
                    date_peremption=peremption
                )
                db.add(article)
                db.flush()

        db.commit()
        return article.id


def ajuster_quantite(article_id: int, delta: float):
    """Ajuste la quantité (+ ou -)"""
    with get_db_context() as db:
        article = db.query(ArticleInventaire).filter(
            ArticleInventaire.id == article_id
        ).first()

        if article:
            article.quantite = max(0, article.quantite + delta)
            article.derniere_maj = datetime.now()
            db.commit()
            return article.quantite

    return None


def supprimer_article(article_id: int):
    """Supprime un article de l'inventaire"""
    with get_db_context() as db:
        db.query(ArticleInventaire).filter(
            ArticleInventaire.id == article_id
        ).delete()
        db.commit()


def ajouter_a_liste_courses(ingredient_nom: str, quantite: float):
    """Ajoute un article à la liste de courses"""
    with get_db_context() as db:
        # Récupérer l'ingrédient
        ingredient = db.query(Ingredient).filter(
            Ingredient.nom == ingredient_nom
        ).first()

        if not ingredient:
            return False

        # Vérifier si déjà dans la liste
        article_existant = db.query(ArticleCourses).filter(
            ArticleCourses.ingredient_id == ingredient.id,
            ArticleCourses.achete == False
        ).first()

        if article_existant:
            article_existant.quantite_necessaire += quantite
        else:
            article = ArticleCourses(
                ingredient_id=ingredient.id,
                quantite_necessaire=quantite,
                priorite="haute",
                suggere_par_ia=False
            )
            db.add(article)

        db.commit()
        return True


# ===================================
# HELPERS - IA
# ===================================

async def analyser_inventaire_ia(agent: AgentIA, df: pd.DataFrame) -> Dict:
    """Analyse complète de l'inventaire par l'IA"""

    # Préparer les données pour l'IA
    inventaire_data = []
    problemes_detectes = []

    for _, row in df.iterrows():
        statut, _, _ = calculer_statut_article(row)

        item_data = {
            "nom": row["nom"],
            "quantite": row["quantite"],
            "unite": row["unite"],
            "seuil": row["seuil"],
            "categorie": row["categorie"],
            "statut": statut
        }

        # Ajouter info péremption si pertinent
        jours = get_jours_avant_peremption(row["peremption"])
        if jours is not None and jours <= JOURS_PEREMPTION_ALERTE:
            item_data["jours_avant_peremption"] = jours
            problemes_detectes.append(f"{row['nom']} périme dans {jours} jours")

        if statut == "sous_seuil" or statut == "critique":
            manque = row["seuil"] - row["quantite"]
            problemes_detectes.append(f"{row['nom']} sous le seuil (manque: {manque:.1f} {row['unite']})")

        inventaire_data.append(item_data)

    # Construire le prompt
    prompt = f"""Analyse cet inventaire de {len(inventaire_data)} articles.

PROBLÈMES DÉTECTÉS:
{chr(10).join(f"- {p}" for p in problemes_detectes[:10])}

INVENTAIRE COMPLET:
{inventaire_data[:20]}

Fournis une analyse structurée au format JSON:
{{
  "statut_global": "critique/attention/correct",
  "score": 0-100,
  "problemes": [
    {{
      "type": "stock_bas/peremption/autre",
      "article": "nom",
      "urgence": "haute/moyenne/basse",
      "conseil": "action recommandée"
    }}
  ],
  "recettes_suggerees": ["recette1", "recette2"],
  "courses_recommandees": [
    {{
      "article": "nom",
      "quantite": 1.0,
      "unite": "kg",
      "raison": "pourquoi"
    }}
  ],
  "conseils_generaux": ["conseil1", "conseil2"]
}}

UNIQUEMENT le JSON, aucun texte avant/après!"""

    try:
        response = await agent._call_mistral(
            prompt=prompt,
            system_prompt="Tu es un expert en gestion de stocks alimentaires. Réponds UNIQUEMENT en JSON valide.",
            temperature=0.7,
            max_tokens=1500
        )

        # Parser la réponse
        cleaned = response.strip().replace("```json", "").replace("```", "")
        result = json.loads(cleaned)

        return result

    except Exception as e:
        logger.error(f"Erreur analyse IA: {e}")
        return {
            "statut_global": "erreur",
            "score": 0,
            "problemes": [],
            "recettes_suggerees": [],
            "courses_recommandees": [],
            "conseils_generaux": ["Erreur lors de l'analyse IA"]
        }


async def suggerer_recettes_avec_stock(agent: AgentIA, df: pd.DataFrame, nb: int = 3) -> List[Dict]:
    """Suggère des recettes faisables avec le stock actuel"""

    ingredients_disponibles = [
        f"{row['nom']} ({row['quantite']} {row['unite']})"
        for _, row in df.iterrows()
        if row["quantite"] > 0
    ]

    prompt = f"""Suggère {nb} recettes RÉALISABLES avec ces ingrédients disponibles:

{chr(10).join(ingredients_disponibles[:30])}

IMPORTANT: Les recettes doivent être ENTIÈREMENT faisables avec ces ingrédients (sauf sel/poivre/huile).

Format JSON:
{{
  "recettes": [
    {{
      "nom": "Nom recette",
      "faisabilite": 100,
      "ingredients_utilises": ["ing1", "ing2"],
      "temps_total": 30,
      "raison": "pourquoi cette recette"
    }}
  ]
}}"""

    try:
        response = await agent._call_mistral(
            prompt=prompt,
            system_prompt="Expert cuisinier. Réponds UNIQUEMENT en JSON.",
            temperature=0.8,
            max_tokens=1000
        )

        cleaned = response.strip().replace("```json", "").replace("```", "")
        result = json.loads(cleaned)

        return result.get("recettes", [])

    except Exception as e:
        logger.error(f"Erreur suggestions recettes: {e}")
        return []


def verifier_faisabilite_recette(recette_id: int) -> Tuple[bool, List[str]]:
    """
    Vérifie si une recette est faisable avec le stock actuel
    Retourne (faisable: bool, manquants: List[str])
    """
    with get_db_context() as db:
        # Récupérer la recette et ses ingrédients
        recette = db.query(Recette).filter(Recette.id == recette_id).first()

        if not recette:
            return False, ["Recette introuvable"]

        manquants = []

        for recette_ing in recette.ingredients:
            ingredient = recette_ing.ingredient
            quantite_necessaire = recette_ing.quantite

            # Vérifier le stock
            stock = db.query(ArticleInventaire).filter(
                ArticleInventaire.ingredient_id == ingredient.id
            ).first()

            if not stock or stock.quantite < quantite_necessaire:
                qty_manquante = quantite_necessaire - (stock.quantite if stock else 0)
                manquants.append(
                    f"{ingredient.nom} (manque: {qty_manquante:.1f} {ingredient.unite})"
                )

        return len(manquants) == 0, manquants


def deduire_recette_du_stock(recette_id: int) -> Tuple[bool, str]:
    """
    Déduit les ingrédients d'une recette du stock
    Retourne (succès: bool, message: str)
    """
    with get_db_context() as db:
        recette = db.query(Recette).filter(Recette.id == recette_id).first()

        if not recette:
            return False, "Recette introuvable"

        # Vérifier la faisabilité d'abord
        faisable, manquants = verifier_faisabilite_recette(recette_id)

        if not faisable:
            return False, f"Stock insuffisant: {', '.join(manquants)}"

        # Déduire chaque ingrédient
        for recette_ing in recette.ingredients:
            stock = db.query(ArticleInventaire).filter(
                ArticleInventaire.ingredient_id == recette_ing.ingredient_id
            ).first()

            if stock:
                stock.quantite -= recette_ing.quantite
                stock.quantite = max(0, stock.quantite)  # Pas de négatif
                stock.derniere_maj = datetime.now()

        db.commit()
        return True, f"Stock mis à jour pour '{recette.nom}'"


# ===================================
# UI - COMPOSANTS
# ===================================

def render_statut_badge(statut: str, icone: str):
    """Affiche un badge de statut coloré"""
    labels = {
        "critique": "🔴 CRITIQUE",
        "peremption_proche": "⏳ Péremption proche",
        "sous_seuil": "⚠️ Sous seuil",
        "ok": "✅ OK"
    }

    st.markdown(f"""
    <span style="background-color: {STATUT_COLORS[statut]}; 
                 padding: 0.25rem 0.75rem; 
                 border-radius: 12px; 
                 font-size: 0.875rem; 
                 font-weight: 600;">
        {labels.get(statut, statut)}
    </span>
    """, unsafe_allow_html=True)


def render_article_card(row: pd.Series, key_suffix: str):
    """Affiche une carte article moderne avec actions rapides"""
    statut, couleur, icone = calculer_statut_article(row)

    with st.container():
        st.markdown(f"""
        <div style="background-color: {couleur}; 
                    padding: 1rem; 
                    border-radius: 8px; 
                    border-left: 4px solid {couleur};
                    margin-bottom: 0.5rem;">
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            st.markdown(f"### {icone} {row['nom']}")
            st.caption(f"{row['categorie']} • {row['emplacement']}")

            # Info péremption si pertinent
            jours = get_jours_avant_peremption(row['peremption'])
            if jours is not None and jours <= JOURS_PEREMPTION_ALERTE:
                if jours == 0:
                    st.error("⚠️ Périme AUJOURD'HUI")
                elif jours > 0:
                    st.warning(f"⏳ Péremption dans {jours} jour(s)")

        with col2:
            st.metric(
                "Stock",
                f"{row['quantite']} {row['unite']}",
                delta=f"Seuil: {row['seuil']}" if row['quantite'] < row['seuil'] else None,
                delta_color="inverse" if row['quantite'] < row['seuil'] else "off"
            )

        with col3:
            # Actions rapides
            col_a1, col_a2, col_a3 = st.columns(3)

            with col_a1:
                if st.button("➕", key=f"plus_{key_suffix}", help="Ajouter 1"):
                    ajuster_quantite(row['id'], 1)
                    st.rerun()

            with col_a2:
                if st.button("➖", key=f"minus_{key_suffix}", help="Retirer 1"):
                    ajuster_quantite(row['id'], -1)
                    st.rerun()

            with col_a3:
                if st.button("🛒", key=f"cart_{key_suffix}", help="→ Courses"):
                    manque = max(row['seuil'] - row['quantite'], 1.0)
                    if ajouter_a_liste_courses(row['nom'], manque):
                        st.success(f"✓ {row['nom']} ajouté")
                        st.rerun()


def render_analyse_ia_section(agent: AgentIA, df: pd.DataFrame):
    """Section d'analyse IA complète"""
    st.markdown("### 🤖 Analyse Intelligente")

    if st.button("🚀 Lancer l'analyse IA", type="primary", use_container_width=True):
        with st.spinner("🤖 Analyse en cours..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                analyse = loop.run_until_complete(
                    analyser_inventaire_ia(agent, df)
                )

                st.session_state["analyse_ia"] = analyse
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur: {e}")

    # Afficher les résultats
    if "analyse_ia" in st.session_state:
        analyse = st.session_state["analyse_ia"]

        # Score global
        col_score1, col_score2 = st.columns([1, 2])

        with col_score1:
            score = analyse.get("score", 0)
            st.metric("Score Global", f"{score}/100")

        with col_score2:
            statut = analyse.get("statut_global", "").upper()
            if statut == "CRITIQUE":
                st.error(f"🔴 {statut}")
            elif statut == "ATTENTION":
                st.warning(f"⚠️ {statut}")
            else:
                st.success(f"✅ {statut}")

        st.markdown("---")

        # Problèmes détectés
        if analyse.get("problemes"):
            st.markdown("#### ⚠️ Problèmes Détectés")

            for pb in analyse["problemes"]:
                urgence_color = {
                    "haute": "error",
                    "moyenne": "warning",
                    "basse": "info"
                }.get(pb.get("urgence", "basse"), "info")

                getattr(st, urgence_color)(
                    f"**{pb.get('article', 'Article')}** : {pb.get('conseil', 'Aucun conseil')}"
                )

        st.markdown("---")

        # Recettes suggérées
        if analyse.get("recettes_suggerees"):
            st.markdown("#### 🍽️ Recettes Suggérées")

            for recette in analyse["recettes_suggerees"]:
                st.info(f"• {recette}")

        st.markdown("---")

        # Courses recommandées
        if analyse.get("courses_recommandees"):
            st.markdown("#### 🛒 Courses Recommandées")

            for course in analyse["courses_recommandees"]:
                col_c1, col_c2 = st.columns([3, 1])

                with col_c1:
                    st.write(
                        f"• **{course.get('article')}** : "
                        f"{course.get('quantite', 0)} {course.get('unite', '')}"
                    )
                    st.caption(course.get('raison', ''))

                with col_c2:
                    if st.button("➕", key=f"add_course_{course.get('article')}"):
                        if ajouter_a_liste_courses(
                                course.get('article'),
                                course.get('quantite', 1.0)
                        ):
                            st.success("✓ Ajouté")
                            st.rerun()

        st.markdown("---")

        # Conseils généraux
        if analyse.get("conseils_generaux"):
            st.markdown("#### 💡 Conseils")

            for conseil in analyse["conseils_generaux"]:
                st.info(conseil)


# ===================================
# MODULE PRINCIPAL
# ===================================

def app():
    """Module Inventaire - Point d'entrée"""

    st.title("📦 Inventaire Intelligent")
    st.caption("Gestion complète des stocks avec IA intégrée")

    # Récupérer l'agent IA
    agent: AgentIA = st.session_state.get("agent_ia")

    # ===================================
    # TABS PRINCIPAUX
    # ===================================

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Mon Stock",
        "🤖 Analyse IA",
        "➕ Ajouter/Modifier",
        "📊 Statistiques"
    ])

    # ===================================
    # TAB 1 : MON STOCK
    # ===================================

    with tab1:
        st.subheader("Stock actuel")

        # Filtres
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)

        with col_f1:
            search = st.text_input("🔍 Rechercher", placeholder="Nom...")

        with col_f2:
            categorie_filter = st.selectbox(
                "Catégorie",
                ["Toutes"] + CATEGORIES
            )

        with col_f3:
            emplacement_filter = st.selectbox(
                "Emplacement",
                ["Tous"] + EMPLACEMENTS
            )

        with col_f4:
            st.write("")  # Spacer
            vue_mode = st.selectbox("Vue", ["Cartes", "Tableau"])

        # Filtres rapides
        col_quick1, col_quick2, col_quick3, col_quick4 = st.columns(4)

        with col_quick1:
            show_sous_seuil = st.checkbox("⚠️ Sous seuil uniquement")

        with col_quick2:
            show_peremption = st.checkbox("⏳ Péremption proche")

        with col_quick3:
            if st.button("🔄 Rafraîchir", use_container_width=True):
                st.rerun()

        # Charger les données
        df = charger_inventaire(
            search=search,
            sous_seuil_only=show_sous_seuil,
            peremption_proche_only=show_peremption,
            categorie=categorie_filter,
            emplacement=emplacement_filter
        )

        if df.empty:
            st.info("📝 Aucun article trouvé. Ajoute des articles dans l'onglet '➕ Ajouter'")
        else:
            # Statistiques rapides
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)

            nb_total = len(df)
            nb_sous_seuil = len([
                True for _, row in df.iterrows()
                if row["quantite"] < row["seuil"]
            ])
            nb_peremption = len([
                True for _, row in df.iterrows()
                if get_jours_avant_peremption(row["peremption"]) is not None
                   and 0 <= get_jours_avant_peremption(row["peremption"]) <= JOURS_PEREMPTION_ALERTE
            ])

            with col_s1:
                st.metric("Total articles", nb_total)

            with col_s2:
                st.metric(
                    "Sous seuil",
                    nb_sous_seuil,
                    delta_color="inverse" if nb_sous_seuil > 0 else "off"
                )

            with col_s3:
                st.metric(
                    "Péremption proche",
                    nb_peremption,
                    delta_color="inverse" if nb_peremption > 0 else "off"
                )

            with col_s4:
                categories_uniques = df["categorie"].nunique()
                st.metric("Catégories", categories_uniques)

            st.markdown("---")

            # Affichage selon le mode
            if vue_mode == "Cartes":
                # Vue cartes
                for idx, row in df.iterrows():
                    render_article_card(row, f"card_{idx}")

                    # Actions supplémentaires (expander)
                    with st.expander(f"⚙️ Actions {row['nom']}", expanded=False):
                        col_act1, col_act2, col_act3 = st.columns(3)

                        with col_act1:
                            if st.button("✏️ Modifier", key=f"edit_{idx}"):
                                st.session_state[f"editing_{row['id']}"] = True
                                st.rerun()

                        with col_act2:
                            ajust = st.number_input(
                                "Ajuster de",
                                -100.0, 100.0, 0.0, 0.1,
                                key=f"adjust_{idx}"
                            )

                            if st.button("✓ Appliquer", key=f"apply_{idx}"):
                                if ajust != 0:
                                    ajuster_quantite(row['id'], ajust)
                                    st.success(f"✓ {abs(ajust)} {row['unite']} {'ajoutés' if ajust > 0 else 'retirés'}")
                                    st.rerun()

                        with col_act3:
                            if st.button("🗑️ Supprimer", key=f"del_{idx}", type="secondary"):
                                supprimer_article(row['id'])
                                st.success("✓ Article supprimé")
                                st.rerun()

                    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

            else:
                # Vue tableau
                st.dataframe(
                    df[["nom", "categorie", "quantite", "unite", "seuil", "emplacement", "peremption"]],
                    use_container_width=True,
                    column_config={
                        "nom": "Article",
                        "categorie": "Catégorie",
                        "quantite": st.column_config.NumberColumn("Quantité", format="%.1f"),
                        "unite": "Unité",
                        "seuil": st.column_config.NumberColumn("Seuil", format="%.1f"),
                        "emplacement": "Emplacement",
                        "peremption": "Péremption"
                    }
                )

    # ===================================
    # TAB 2 : ANALYSE IA
    # ===================================

    with tab2:
        if not agent:
            st.error("❌ Agent IA non disponible")
        else:
            df_full = charger_inventaire()

            if df_full.empty:
                st.warning("📝 Inventaire vide. Ajoute des articles d'abord.")
            else:
                render_analyse_ia_section(agent, df_full)

                st.markdown("---")

                # Section recettes faisables
                st.markdown("### 🍽️ Recettes Faisables")

                if st.button("🔍 Suggérer des recettes", use_container_width=True):
                    with st.spinner("🤖 Recherche de recettes..."):
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                            recettes = loop.run_until_complete(
                                suggerer_recettes_avec_stock(agent, df_full, nb=5)
                            )

                            st.session_state["recettes_suggerees"] = recettes
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")

                if "recettes_suggerees" in st.session_state:
                    recettes = st.session_state["recettes_suggerees"]

                    for recette in recettes:
                        with st.expander(f"🍽️ {recette.get('nom', 'Sans nom')}", expanded=False):
                            col_r1, col_r2 = st.columns([2, 1])

                            with col_r1:
                                st.write(f"**Raison :** {recette.get('raison', '')}")
                                st.write(f"**Ingrédients utilisés :** {', '.join(recette.get('ingredients_utilises', []))}")

                            with col_r2:
                                st.metric("Faisabilité", f"{recette.get('faisabilite', 0)}%")
                                st.caption(f"⏱️ {recette.get('temps_total', 0)}min")

    # ===================================
    # TAB 3 : AJOUTER/MODIFIER
    # ===================================

    with tab3:
        st.subheader("➕ Ajouter ou modifier un article")

        mode = st.radio("Mode", ["➕ Ajouter nouveau", "✏️ Modifier existant"], horizontal=True)

        if mode == "✏️ Modifier existant":
            # Mode modification
            df_all = charger_inventaire()

            if df_all.empty:
                st.info("Aucun article à modifier")
            else:
                article_select = st.selectbox(
                    "Article à modifier",
                    df_all["nom"].tolist()
                )

                row = df_all[df_all["nom"] == article_select].iloc[0]

                with st.form("form_edit"):
                    st.markdown("#### Modifier les informations")

                    col_e1, col_e2 = st.columns(2)

                    with col_e1:
                        nom = st.text_input("Nom *", value=row["nom"])
                        categorie = st.selectbox("Catégorie", CATEGORIES, index=CATEGORIES.index(row["categorie"]) if row["categorie"] in CATEGORIES else 0)
                        quantite = st.number_input("Quantité *", 0.0, 10000.0, float(row["quantite"]), 0.1)
                        unite = st.selectbox("Unité", UNITES, index=UNITES.index(row["unite"]) if row["unite"] in UNITES else 0)

                    with col_e2:
                        seuil = st.number_input("Seuil d'alerte", 0.0, 1000.0, float(row["seuil"]), 0.1)
                        emplacement = st.selectbox("Emplacement", EMPLACEMENTS, index=EMPLACEMENTS.index(row["emplacement"]) if row["emplacement"] in EMPLACEMENTS else 0)

                        try:
                            date_peremption = datetime.strptime(row["peremption"], "%d/%m/%Y").date() if row["peremption"] != "—" else None
                        except:
                            date_peremption = None

                        peremption = st.date_input("Date de péremption (optionnel)", value=date_peremption)

                    col_submit1, col_submit2 = st.columns(2)

                    with col_submit1:
                        if st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True):
                            ajouter_ou_modifier_article(
                                nom=nom,
                                categorie=categorie,
                                quantite=quantite,
                                unite=unite,
                                seuil=seuil,
                                emplacement=emplacement,
                                peremption=peremption,
                                article_id=row["id"]
                            )
                            st.success(f"✅ {nom} mis à jour")
                            st.rerun()

                    with col_submit2:
                        if st.form_submit_button("❌ Annuler", use_container_width=True):
                            st.rerun()

        else:
            # Mode ajout
            with st.form("form_add"):
                st.markdown("#### Ajouter un nouvel article")

                col_a1, col_a2 = st.columns(2)

                with col_a1:
                    nom = st.text_input("Nom de l'article *", placeholder="Ex: Tomates")
                    categorie = st.selectbox("Catégorie *", CATEGORIES)
                    quantite = st.number_input("Quantité *", 0.0, 10000.0, 1.0, 0.1)
                    unite = st.selectbox("Unité *", UNITES)

                with col_a2:
                    seuil = st.number_input("Seuil d'alerte", 0.0, 1000.0, 1.0, 0.1, help="Quantité minimale avant alerte")
                    emplacement = st.selectbox("Emplacement", EMPLACEMENTS)
                    peremption = st.date_input("Date de péremption (optionnel)", value=None)

                if st.form_submit_button("➕ Ajouter à l'inventaire", type="primary", use_container_width=True):
                    if not nom:
                        st.error("❌ Le nom est obligatoire")
                    else:
                        ajouter_ou_modifier_article(
                            nom=nom,
                            categorie=categorie,
                            quantite=quantite,
                            unite=unite,
                            seuil=seuil,
                            emplacement=emplacement,
                            peremption=peremption
                        )
                        st.success(f"✅ {nom} ajouté à l'inventaire")
                        st.balloons()
                        st.rerun()

        st.markdown("---")

        # Section import rapide
        st.markdown("### ⚡ Import Rapide")
        st.info("💡 Fonctionnalité future : importer depuis un fichier CSV ou scan de ticket")

    # ===================================
    # TAB 4 : STATISTIQUES
    # ===================================

    with tab4:
        st.subheader("📊 Statistiques de l'inventaire")

        df_stats = charger_inventaire()

        if df_stats.empty:
            st.info("Pas de statistiques sans articles")
        else:
            # Métriques principales
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)

            nb_total = len(df_stats)
            nb_categories = df_stats["categorie"].nunique()
            nb_emplacements = df_stats["emplacement"].nunique()

            # Calculer sous seuil
            nb_sous_seuil = len([
                True for _, row in df_stats.iterrows()
                if row["quantite"] < row["seuil"]
            ])

            # Calculer péremption proche
            nb_peremption = len([
                True for _, row in df_stats.iterrows()
                if get_jours_avant_peremption(row["peremption"]) is not None
                   and 0 <= get_jours_avant_peremption(row["peremption"]) <= JOURS_PEREMPTION_ALERTE
            ])

            with col_m1:
                st.metric("Total articles", nb_total)

            with col_m2:
                st.metric("Catégories", nb_categories)

            with col_m3:
                st.metric("Stock bas", nb_sous_seuil, delta_color="inverse")

            with col_m4:
                st.metric("Péremption proche", nb_peremption, delta_color="inverse")

            st.markdown("---")

            # Graphiques
            col_g1, col_g2 = st.columns(2)

            with col_g1:
                st.markdown("### 📈 Répartition par catégorie")

                cat_counts = df_stats["categorie"].value_counts().reset_index()
                cat_counts.columns = ["Catégorie", "Nombre"]

                st.bar_chart(cat_counts.set_index("Catégorie"))

            with col_g2:
                st.markdown("### 📍 Répartition par emplacement")

                loc_counts = df_stats["emplacement"].value_counts().reset_index()
                loc_counts.columns = ["Emplacement", "Nombre"]

                st.bar_chart(loc_counts.set_index("Emplacement"))

            st.markdown("---")

            # Top/Bottom
            col_top1, col_top2 = st.columns(2)

            with col_top1:
                st.markdown("### 🔝 Articles les plus stockés")

                top10 = df_stats.nlargest(10, "quantite")[["nom", "quantite", "unite", "categorie"]]
                st.dataframe(top10, use_container_width=True, hide_index=True)

            with col_top2:
                st.markdown("### 📉 Articles en stock bas")

                bas = df_stats[df_stats["quantite"] < df_stats["seuil"]][["nom", "quantite", "seuil", "unite"]]

                if not bas.empty:
                    st.dataframe(bas, use_container_width=True, hide_index=True)
                else:
                    st.success("✅ Aucun article sous le seuil")

            st.markdown("---")

            # Export
            st.markdown("### 📤 Export")

            if st.button("📥 Télécharger l'inventaire (CSV)", use_container_width=True):
                csv = df_stats.to_csv(index=False)
                st.download_button(
                    "💾 Télécharger",
                    csv,
                    "inventaire.csv",
                    "text/csv",
                    use_container_width=True
                )

            st.markdown("---")

            # Vérification recettes
            st.markdown("### 🍽️ Vérifier une recette")

            with get_db_context() as db:
                recettes = db.query(Recette).order_by(Recette.nom).all()

            if recettes:
                recette_select = st.selectbox(
                    "Sélectionner une recette",
                    [r.nom for r in recettes]
                )

                if st.button("🔍 Vérifier faisabilité", use_container_width=True):
                    recette_id = next(r.id for r in recettes if r.nom == recette_select)
                    faisable, manquants = verifier_faisabilite_recette(recette_id)

                    if faisable:
                        st.success(f"✅ '{recette_select}' est réalisable avec le stock actuel")

                        if st.button("📦 Déduire du stock", type="primary"):
                            with st.spinner("Mise à jour du stock..."):
                                succes, message = deduire_recette_du_stock(recette_id)

                                if succes:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                    else:
                        st.error(f"❌ Stock insuffisant pour '{recette_select}'")
                        st.markdown("**Articles manquants :**")
                        for manquant in manquants:
                            st.write(f"• {manquant}")
            else:
                st.info("Aucune recette disponible")