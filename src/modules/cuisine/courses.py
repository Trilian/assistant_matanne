"""
Module Courses Intelligent avec IA Proactive
Génération automatique, organisation par magasins, optimisation budget
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import asyncio
import json
from typing import List, Dict, Optional, Tuple

from src.core.database import get_db_context
from src.core.models import (
    ArticleCourses, Ingredient, ArticleInventaire,
    Recette, RecetteIngredient, RepasPlanning, PlanningHebdomadaire
)
from src.core.ai_agent import AgentIA

# ===================================
# CONSTANTES
# ===================================

MAGASINS = {
    "Grand Frais": {
        "rayons": [
            "Fruits & Légumes",
            "Boucherie",
            "Poissonnerie",
            "Fromage & Crèmerie",
            "Traiteur",
            "Boulangerie",
            "Epicerie",
            "Surgelés",
            "Boissons"
        ],
        "couleur": "#4CAF50"
    },
    "Thiriet": {
        "rayons": [
            "Entrées & Apéritifs",
            "Poissons & Crustacés",
            "Viandes & Volailles",
            "Plats Cuisinés",
            "Légumes",
            "Desserts & Glaces",
            "Pain & Viennoiseries"
        ],
        "couleur": "#2196F3"
    },
    "Cora": {
        "rayons": [
            "Fruits & Légumes",
            "Boucherie",
            "Poissonnerie",
            "Crèmerie",
            "Epicerie Salée",
            "Epicerie Sucrée",
            "Surgelés",
            "Boissons",
            "Hygiène & Entretien"
        ],
        "couleur": "#FF5722"
    },
    "Autre": {
        "rayons": [
            "Frais",
            "Sec",
            "Surgelés",
            "Boissons",
            "Autre"
        ],
        "couleur": "#9E9E9E"
    }
}

PRIORITE_COLORS = {
    "haute": "#dc3545",
    "moyenne": "#ffc107",
    "basse": "#28a745"
}

PRIORITE_ICONS = {
    "haute": "🔴",
    "moyenne": "🟡",
    "basse": "🟢"
}

# ===================================
# HELPERS - CRUD
# ===================================

def charger_liste_courses(achetes: bool = False) -> pd.DataFrame:
    """Charge la liste de courses"""
    with get_db_context() as db:
        query = db.query(
            ArticleCourses.id,
            Ingredient.nom,
            ArticleCourses.quantite_necessaire,
            Ingredient.unite,
            ArticleCourses.priorite,
            ArticleCourses.achete,
            ArticleCourses.suggere_par_ia,
            ArticleCourses.cree_le,
            ArticleCourses.achete_le
        ).join(
            Ingredient, ArticleCourses.ingredient_id == Ingredient.id
        ).filter(
            ArticleCourses.achete == achetes
        ).order_by(
            ArticleCourses.priorite.desc(),
            Ingredient.nom
        )

        items = query.all()

        return pd.DataFrame([{
            "id": i.id,
            "nom": i.nom,
            "quantite": i.quantite_necessaire,
            "unite": i.unite,
            "priorite": i.priorite,
            "ia": i.suggere_par_ia,
            "cree_le": i.cree_le,
            "achete_le": i.achete_le
        } for i in items])


def ajouter_article(
        nom: str,
        quantite: float,
        unite: str,
        priorite: str = "moyenne",
        rayon: str = None,
        magasin: str = None,
        ia_suggere: bool = False
) -> int:
    """Ajoute un article à la liste"""
    with get_db_context() as db:
        # Trouver ou créer ingrédient
        ingredient = db.query(Ingredient).filter(
            Ingredient.nom == nom
        ).first()

        if not ingredient:
            ingredient = Ingredient(nom=nom, unite=unite)
            db.add(ingredient)
            db.flush()

        # Vérifier si existe déjà
        existant = db.query(ArticleCourses).filter(
            ArticleCourses.ingredient_id == ingredient.id,
            ArticleCourses.achete == False
        ).first()

        if existant:
            # Fusion automatique
            existant.quantite_necessaire = max(
                existant.quantite_necessaire,
                quantite
            )
            article_id = existant.id
        else:
            # Création
            article = ArticleCourses(
                ingredient_id=ingredient.id,
                quantite_necessaire=quantite,
                priorite=priorite,
                suggere_par_ia=ia_suggere
            )
            db.add(article)
            db.flush()
            article_id = article.id

        db.commit()
        return article_id


def marquer_achete(article_id: int, ajouter_stock: bool = False):
    """Marque un article comme acheté"""
    with get_db_context() as db:
        article = db.query(ArticleCourses).filter(
            ArticleCourses.id == article_id
        ).first()

        if article:
            article.achete = True
            article.achete_le = datetime.now()

            # Ajouter au stock si demandé
            if ajouter_stock:
                stock = db.query(ArticleInventaire).filter(
                    ArticleInventaire.ingredient_id == article.ingredient_id
                ).first()

                if stock:
                    stock.quantite += article.quantite_necessaire
                    stock.derniere_maj = datetime.now()
                else:
                    # Créer entrée stock
                    stock = ArticleInventaire(
                        ingredient_id=article.ingredient_id,
                        quantite=article.quantite_necessaire,
                        quantite_min=1.0
                    )
                    db.add(stock)

            db.commit()


def supprimer_article(article_id: int):
    """Supprime un article"""
    with get_db_context() as db:
        db.query(ArticleCourses).filter(
            ArticleCourses.id == article_id
        ).delete()
        db.commit()


def nettoyer_achetes():
    """Supprime tous les articles achetés"""
    with get_db_context() as db:
        db.query(ArticleCourses).filter(
            ArticleCourses.achete == True
        ).delete()
        db.commit()


def modifier_quantite(article_id: int, nouvelle_quantite: float):
    """Modifie la quantité d'un article"""
    with get_db_context() as db:
        article = db.query(ArticleCourses).filter(
            ArticleCourses.id == article_id
        ).first()

        if article:
            article.quantite_necessaire = nouvelle_quantite
            db.commit()


# ===================================
# HELPERS - GÉNÉRATION AUTOMATIQUE
# ===================================

def generer_depuis_stock_bas() -> List[Dict]:
    """Génère articles depuis stock bas"""
    with get_db_context() as db:
        items = db.query(
            Ingredient.id,
            Ingredient.nom,
            Ingredient.unite,
            ArticleInventaire.quantite,
            ArticleInventaire.quantite_min
        ).join(
            ArticleInventaire,
            Ingredient.id == ArticleInventaire.ingredient_id
        ).filter(
            ArticleInventaire.quantite < ArticleInventaire.quantite_min
        ).all()

        suggestions = []
        for ing_id, nom, unite, qty, seuil in items:
            manque = max(seuil - qty, seuil)
            suggestions.append({
                "nom": nom,
                "quantite": manque,
                "unite": unite,
                "priorite": "haute",
                "raison": f"Stock actuel: {qty:.1f}, seuil: {seuil:.1f}"
            })

        return suggestions


def generer_depuis_repas_planifies() -> List[Dict]:
    """Génère articles depuis repas planifiés"""
    with get_db_context() as db:
        # Récupérer repas de la semaine
        today = date.today()
        week_end = today + timedelta(days=7)

        repas = db.query(
            Recette.id,
            Recette.nom
        ).join(
            RepasPlanning,
            Recette.id == RepasPlanning.recette_id
        ).join(
            PlanningHebdomadaire,
            RepasPlanning.planning_id == PlanningHebdomadaire.id
        ).filter(
            RepasPlanning.date.between(today, week_end),
            RepasPlanning.statut != "terminé"
        ).all()

        suggestions = []
        ingredients_consolides = {}

        for recette_id, recette_nom in repas:
            # Récupérer ingrédients
            ingredients = db.query(
                Ingredient.nom,
                RecetteIngredient.quantite,
                Ingredient.unite
            ).join(
                RecetteIngredient,
                Ingredient.id == RecetteIngredient.ingredient_id
            ).filter(
                RecetteIngredient.recette_id == recette_id
            ).all()

            for nom, qty, unite in ingredients:
                # Vérifier stock
                stock = db.query(ArticleInventaire).join(
                    Ingredient,
                    ArticleInventaire.ingredient_id == Ingredient.id
                ).filter(
                    Ingredient.nom == nom
                ).first()

                qty_dispo = stock.quantite if stock else 0
                manque = max(qty - qty_dispo, 0)

                if manque > 0:
                    # Consolider
                    key = f"{nom}_{unite}"
                    if key in ingredients_consolides:
                        ingredients_consolides[key]["quantite"] += manque
                        ingredients_consolides[key]["recettes"].append(recette_nom)
                    else:
                        ingredients_consolides[key] = {
                            "nom": nom,
                            "quantite": manque,
                            "unite": unite,
                            "priorite": "moyenne",
                            "recettes": [recette_nom]
                        }

        # Convertir en liste
        for item in ingredients_consolides.values():
            recettes_str = ", ".join(item["recettes"][:2])
            if len(item["recettes"]) > 2:
                recettes_str += f" +{len(item['recettes'])-2}"

            suggestions.append({
                "nom": item["nom"],
                "quantite": item["quantite"],
                "unite": item["unite"],
                "priorite": item["priorite"],
                "raison": f"Pour: {recettes_str}"
            })

        return suggestions


def generer_depuis_recettes_selectionnees(recette_ids: List[int]) -> List[Dict]:
    """Génère articles depuis recettes sélectionnées"""
    with get_db_context() as db:
        suggestions = []

        for recette_id in recette_ids:
            ingredients = db.query(
                Ingredient.nom,
                RecetteIngredient.quantite,
                Ingredient.unite
            ).join(
                RecetteIngredient,
                Ingredient.id == RecetteIngredient.ingredient_id
            ).filter(
                RecetteIngredient.recette_id == recette_id
            ).all()

            for nom, qty, unite in ingredients:
                suggestions.append({
                    "nom": nom,
                    "quantite": qty,
                    "unite": unite,
                    "priorite": "moyenne",
                    "raison": "Recette sélectionnée"
                })

        return suggestions


# ===================================
# HELPERS - IA
# ===================================

async def generer_liste_ia(
        agent: AgentIA,
        inclure_stock_bas: bool,
        inclure_repas: bool,
        recettes_selectionnees: List[int],
        magasin: str,
        budget_max: float
) -> Dict:
    """Génère une liste optimisée avec l'IA"""

    # Collecter suggestions de base
    suggestions = []

    if inclure_stock_bas:
        suggestions.extend(generer_depuis_stock_bas())

    if inclure_repas:
        suggestions.extend(generer_depuis_repas_planifies())

    if recettes_selectionnees:
        suggestions.extend(generer_depuis_recettes_selectionnees(recettes_selectionnees))

    # Consolider doublons
    consolide = {}
    for item in suggestions:
        key = item["nom"]
        if key in consolide:
            consolide[key]["quantite"] = max(
                consolide[key]["quantite"],
                item["quantite"]
            )
        else:
            consolide[key] = item

    suggestions = list(consolide.values())

    # Préparer prompt IA
    rayons = MAGASINS[magasin]["rayons"]

    prompt = f"""Tu dois optimiser cette liste de courses pour {magasin}.

ARTICLES À ACHETER:
{json.dumps(suggestions, indent=2, ensure_ascii=False)}

RAYONS DISPONIBLES: {', '.join(rayons)}

BUDGET MAXIMUM: {budget_max}€

Organise cette liste de manière optimale:
1. Classe chaque article dans le bon rayon
2. Détecte les doublons potentiels
3. Propose des alternatives économiques
4. Estime le coût total
5. Ajoute des conseils d'achat

Format JSON:
{{
  "par_rayon": {{
    "Rayon1": [
      {{
        "article": "nom",
        "quantite": 1.0,
        "unite": "kg",
        "priorite": "moyenne",
        "prix_estime": 2.5,
        "alternatives": ["alt1", "alt2"],
        "conseil": "Format familial recommandé"
      }}
    ]
  }},
  "doublons_detectes": [
    {{"articles": ["art1", "art2"], "conseil": "Grouper en un seul"}}
  ],
  "budget_estime": 50.0,
  "depasse_budget": false,
  "economies_possibles": 12.0,
  "conseils_globaux": ["conseil1", "conseil2"]
}}

UNIQUEMENT le JSON!"""

    try:
        response = await agent._call_mistral(
            prompt=prompt,
            system_prompt="Tu es un expert en courses alimentaires. Réponds UNIQUEMENT en JSON.",
            temperature=0.7,
            max_tokens=2000
        )

        cleaned = response.strip().replace("```json", "").replace("```", "")
        result = json.loads(cleaned)

        return result

    except Exception as e:
        st.error(f"Erreur IA: {e}")
        return {
            "par_rayon": {},
            "doublons_detectes": [],
            "budget_estime": 0,
            "conseils_globaux": []
        }


async def proposer_alternatives_ia(
        agent: AgentIA,
        article: str,
        magasin: str
) -> List[Dict]:
    """Propose des alternatives pour un article"""

    prompt = f"""Propose 3 alternatives pour cet article dans {magasin}:

Article: {article}

Critères:
- Prix similaire ou inférieur
- Même utilisation culinaire
- Disponible en magasin

Format JSON:
{{
  "alternatives": [
    {{
      "nom": "Alternative 1",
      "raison": "Moins cher et équivalent",
      "prix_relatif": "-20%",
      "disponibilite": "haute"
    }}
  ]
}}"""

    try:
        response = await agent._call_mistral(
            prompt=prompt,
            system_prompt="Expert courses. JSON uniquement.",
            temperature=0.8,
            max_tokens=500
        )

        cleaned = response.strip().replace("```json", "").replace("```", "")
        result = json.loads(cleaned)

        return result.get("alternatives", [])

    except:
        return []


# ===================================
# HELPERS - STATISTIQUES
# ===================================

def get_stats_historique(jours: int = 30) -> Dict:
    """Statistiques sur l'historique"""
    with get_db_context() as db:
        date_limite = datetime.now() - timedelta(days=jours)

        achetes = db.query(ArticleCourses).filter(
            ArticleCourses.achete == True,
            ArticleCourses.achete_le >= date_limite
        ).all()

        stats = {
            "total_achetes": len(achetes),
            "part_ia": len([a for a in achetes if a.suggere_par_ia]),
            "articles_frequents": {},
            "moyenne_par_semaine": 0
        }

        # Articles fréquents
        noms = {}
        for a in achetes:
            ing = db.query(Ingredient).get(a.ingredient_id)
            nom = ing.nom if ing else "Inconnu"
            noms[nom] = noms.get(nom, 0) + 1

        stats["articles_frequents"] = dict(
            sorted(noms.items(), key=lambda x: x[1], reverse=True)[:10]
        )

        # Moyenne par semaine
        nb_semaines = max(jours // 7, 1)
        stats["moyenne_par_semaine"] = len(achetes) / nb_semaines

        return stats


# ===================================
# UI - COMPOSANTS
# ===================================

def render_article_simple(row: pd.Series, key: str):
    """Affiche un article en mode simple (liste)"""
    icone_priorite = PRIORITE_ICONS[row["priorite"]]
    icone_ia = "🤖" if row["ia"] else ""

    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

    with col1:
        st.markdown(f"{icone_priorite} {icone_ia} **{row['nom']}**")

    with col2:
        st.write(f"{row['quantite']:.1f} {row['unite']}")

    with col3:
        if st.button("✅", key=f"check_{key}", help="Marquer acheté"):
            # Demander confirmation pour ajout stock
            st.session_state[f"confirming_{row['id']}"] = True
            st.rerun()

    with col4:
        if st.button("🗑️", key=f"del_{key}", help="Supprimer"):
            supprimer_article(row['id'])
            st.success(f"✓ {row['nom']} supprimé")
            st.rerun()

    # Modal confirmation
    if st.session_state.get(f"confirming_{row['id']}", False):
        with st.expander(f"Confirmer achat de {row['nom']}", expanded=True):
            st.write(f"**Quantité achetée:** {row['quantite']:.1f} {row['unite']}")

            ajouter_stock = st.checkbox(
                "Ajouter automatiquement au stock",
                value=True,
                key=f"stock_{key}"
            )

            col_c1, col_c2 = st.columns(2)

            with col_c1:
                if st.button("✅ Confirmer", key=f"confirm_{key}", type="primary"):
                    marquer_achete(row['id'], ajouter_stock)
                    del st.session_state[f"confirming_{row['id']}"]
                    st.success(f"✓ {row['nom']} acheté")
                    st.rerun()

            with col_c2:
                if st.button("❌ Annuler", key=f"cancel_{key}"):
                    del st.session_state[f"confirming_{row['id']}"]
                    st.rerun()


def render_article_carte(article: Dict, magasin: str, key: str):
    """Affiche un article en mode carte (IA)"""
    couleur = MAGASINS[magasin]["couleur"]

    with st.container():
        st.markdown(f"""
        <div style="border-left: 4px solid {couleur}; 
                    padding: 1rem; 
                    background: #f8f9fa; 
                    border-radius: 8px; 
                    margin-bottom: 1rem;">
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            priorite_icon = PRIORITE_ICONS.get(article.get("priorite", "moyenne"), "⚪")
            st.markdown(f"### {priorite_icon} {article['article']}")

            if article.get("conseil"):
                st.info(f"💡 {article['conseil']}")

        with col2:
            st.metric(
                "Quantité",
                f"{article['quantite']:.1f} {article['unite']}"
            )

            if article.get("prix_estime"):
                st.caption(f"💶 ~{article['prix_estime']:.2f}€")

        with col3:
            if st.button("➕ Ajouter", key=f"add_ia_{key}", use_container_width=True):
                ajouter_article(
                    nom=article['article'],
                    quantite=article['quantite'],
                    unite=article['unite'],
                    priorite=article.get('priorite', 'moyenne'),
                    ia_suggere=True
                )
                st.success("✓ Ajouté")
                st.rerun()

        # Alternatives
        if article.get("alternatives"):
            with st.expander("🔄 Voir alternatives"):
                for alt in article["alternatives"]:
                    st.write(f"• {alt}")


def render_suggestions_ia_section(
        agent: AgentIA,
        magasin: str,
        budget: float
):
    """Section génération IA"""
    st.markdown("### 🤖 Génération Automatique")

    with st.form("form_generation_ia"):
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            inclure_stock = st.checkbox("📦 Stock bas", value=True)
            inclure_repas = st.checkbox("📅 Repas planifiés", value=True)

        with col_g2:
            magasin_select = st.selectbox(
                "🏬 Magasin",
                list(MAGASINS.keys()),
                index=list(MAGASINS.keys()).index(magasin) if magasin in MAGASINS else 0
            )

            budget_max = st.number_input(
                "💶 Budget max (€)",
                0, 500, int(budget), 10
            )

        # Recettes optionnelles
        with get_db_context() as db:
            recettes = db.query(Recette).order_by(Recette.nom).all()

        if recettes:
            st.markdown("**📖 Recettes supplémentaires (optionnel)**")
            recettes_select = st.multiselect(
                "Sélectionner",
                [r.nom for r in recettes],
                key="recettes_ia"
            )
        else:
            recettes_select = []

        generer = st.form_submit_button(
            "✨ Générer avec l'IA",
            type="primary",
            use_container_width=True
        )

    if generer:
        with st.spinner("🤖 L'IA génère ta liste optimisée..."):
            try:
                # Récupérer IDs recettes
                recette_ids = []
                if recettes_select:
                    with get_db_context() as db:
                        recette_ids = [
                            r.id for r in db.query(Recette).filter(
                                Recette.nom.in_(recettes_select)
                            ).all()
                        ]

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                result = loop.run_until_complete(
                    generer_liste_ia(
                        agent,
                        inclure_stock,
                        inclure_repas,
                        recette_ids,
                        magasin_select,
                        budget_max
                    )
                )

                st.session_state["liste_ia"] = result
                st.session_state["magasin_ia"] = magasin_select
                st.success("✅ Liste générée !")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur: {e}")

    # Afficher résultats
    if "liste_ia" in st.session_state:
        result = st.session_state["liste_ia"]
        magasin_actif = st.session_state.get("magasin_ia", magasin)

        st.markdown("---")
        st.markdown("### 📋 Liste Générée")

        # Budget
        col_b1, col_b2, col_b3 = st.columns(3)

        with col_b1:
            st.metric("Budget estimé", f"{result.get('budget_estime', 0):.2f}€")

        with col_b2:
            if result.get("depasse_budget"):
                st.error("⚠️ Budget dépassé")
            else:
                st.success("✅ Dans le budget")

        with col_b3:
            if result.get("economies_possibles"):
                st.metric(
                    "Économies possibles",
                    f"{result['economies_possibles']:.2f}€"
                )

        # Doublons
        if result.get("doublons_detectes"):
            st.warning("⚠️ Doublons détectés")
            for doublon in result["doublons_detectes"]:
                st.write(f"• {doublon['conseil']}")

        st.markdown("---")

        # Liste par rayon
        st.markdown("### 🏪 Liste Organisée par Rayons")

        for rayon, articles in result.get("par_rayon", {}).items():
            with st.expander(f"📍 {rayon} ({len(articles)} articles)", expanded=True):
                for idx, article in enumerate(articles):
                    render_article_carte(
                        article,
                        magasin_actif,
                        f"{rayon}_{idx}"
                    )

        # Conseils
        if result.get("conseils_globaux"):
            st.markdown("---")
            st.markdown("### 💡 Conseils")

            for conseil in result["conseils_globaux"]:
                st.info(conseil)

        # Actions globales
        st.markdown("---")

        col_action1, col_action2 = st.columns(2)

        with col_action1:
            if st.button("✅ Tout ajouter à ma liste", type="primary", use_container_width=True):
                count = 0
                for articles in result.get("par_rayon", {}).values():
                    for article in articles:
                        ajouter_article(
                            nom=article['article'],
                            quantite=article['quantite'],
                            unite=article['unite'],
                            priorite=article.get('priorite', 'moyenne'),
                            ia_suggere=True
                        )
                        count += 1

                st.success(f"✅ {count} articles ajoutés !")
                del st.session_state["liste_ia"]
                st.balloons()
                st.rerun()

        with col_action2:
            if st.button("🗑️ Annuler", use_container_width=True):
                del st.session_state["liste_ia"]
                st.rerun()


# ===================================
# MODULE PRINCIPAL
# ===================================

def app():
    """Module Courses Intelligent - Point d'entrée"""

    st.title("🛒 Liste de Courses Intelligente")
    st.caption("Génération IA proactive, organisation par magasins, optimisation budget")

    # Récupérer agent IA
    agent: AgentIA = st.session_state.get("agent_ia")

    # ===================================
    # TABS PRINCIPAUX
    # ===================================

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Ma Liste",
        "🤖 Génération Auto",
        "➕ Ajouter",
        "📊 Historique"
    ])

    # ===================================
    # TAB 1 : MA LISTE
    # ===================================

    with tab1:
        st.subheader("Ma liste de courses")

        # Actions rapides
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)

        with col_a1:
            if st.button("🔄 Rafraîchir", use_container_width=True):
                st.rerun()

        with col_a2:
            if st.button("🗑️ Nettoyer achetés", use_container_width=True):
                nettoyer_achetes()
                st.success("✅ Liste nettoyée")
                st.rerun()

        with col_a3:
            # Génération rapide stock bas
            suggestions_stock = generer_depuis_stock_bas()
            if suggestions_stock:
                if st.button(f"⚡ Stock bas ({len(suggestions_stock)})", use_container_width=True):
                    count = 0
                    for item in suggestions_stock:
                        ajouter_article(
                            nom=item['nom'],
                            quantite=item['quantite'],
                            unite=item['unite'],
                            priorite=item['priorite'],
                            ia_suggere=True
                        )
                        count += 1
                    st.success(f"✅ {count} articles ajoutés")
                    st.rerun()

        with col_a4:
            # Génération rapide repas
            suggestions_repas = generer_depuis_repas_planifies()
            if suggestions_repas:
                if st.button(f"📅 Repas ({len(suggestions_repas)})", use_container_width=True):
                    count = 0
                    for item in suggestions_repas:
                        ajouter_article(
                            nom=item['nom'],
                            quantite=item['quantite'],
                            unite=item['unite'],
                            priorite=item['priorite'],
                            ia_suggere=True
                        )
                        count += 1
                    st.success(f"✅ {count} articles ajoutés")
                    st.rerun()

        st.markdown("---")

        # Charger liste
        df_actifs = charger_liste_courses(achetes=False)
        df_achetes = charger_liste_courses(achetes=True)

        if df_actifs.empty:
            st.info("📝 Liste vide. Utilise la génération automatique ou ajoute manuellement !")
        else:
            # Statistiques
            col_s1, col_s2, col_s3 = st.columns(3)

            with col_s1:
                st.metric("À acheter", len(df_actifs))

            with col_s2:
                prioritaires = len(df_actifs[df_actifs["priorite"] == "haute"])
                st.metric("Prioritaires", prioritaires, delta_color="inverse")

            with col_s3:
                ia_count = len(df_actifs[df_actifs["ia"] == True])
                st.metric("Suggérés IA", ia_count)

            st.markdown("---")

            # Organisation par priorité
            st.markdown("### 🔴 Haute Priorité")

            df_haute = df_actifs[df_actifs["priorite"] == "haute"]
            if not df_haute.empty:
                for idx, row in df_haute.iterrows():
                    render_article_simple(row, f"haute_{idx}")
            else:
                st.caption("Aucun article prioritaire")

            st.markdown("### 🟡 Priorité Moyenne")

            df_moyenne = df_actifs[df_actifs["priorite"] == "moyenne"]
            if not df_moyenne.empty:
                for idx, row in df_moyenne.iterrows():
                    render_article_simple(row, f"moyenne_{idx}")
            else:
                st.caption("Aucun article")

            st.markdown("### 🟢 Basse Priorité")

            df_basse = df_actifs[df_actifs["priorite"] == "basse"]
            if not df_basse.empty:
                for idx, row in df_basse.iterrows():
                    render_article_simple(row, f"basse_{idx}")
            else:
                st.caption("Aucun article")

        # Achetés (collapsé)
        if not df_achetes.empty:
            st.markdown("---")
            with st.expander(f"✅ Achetés ({len(df_achetes)})", expanded=False):
                for idx, row in df_achetes.iterrows():
                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.write(f"• {row['nom']}")

                    with col2:
                        st.caption(f"{row['quantite']:.1f} {row['unite']}")

                    with col3:
                        if row['achete_le']:
                            st.caption(row['achete_le'].strftime("%d/%m %H:%M"))

    # ===================================
    # TAB 2 : GÉNÉRATION AUTOMATIQUE
    # ===================================

    with tab2:
        if not agent:
            st.error("❌ Agent IA non disponible")
        else:
            render_suggestions_ia_section(
                agent=agent,
                magasin=st.session_state.get("magasin_prefere", "Cora"),
                budget=st.session_state.get("budget_prefere", 100)
            )

            st.markdown("---")

            # Détection automatique
            st.markdown("### 🔍 Détections Automatiques")

            col_d1, col_d2 = st.columns(2)

            with col_d1:
                st.markdown("#### 📦 Stock Bas")
                suggestions_stock = generer_depuis_stock_bas()

                if suggestions_stock:
                    for item in suggestions_stock[:5]:
                        st.write(f"• **{item['nom']}** : {item['raison']}")

                    if len(suggestions_stock) > 5:
                        st.caption(f"... et {len(suggestions_stock)-5} autres")
                else:
                    st.success("✅ Pas de stock bas")

            with col_d2:
                st.markdown("#### 📅 Repas Planifiés")
                suggestions_repas = generer_depuis_repas_planifies()

                if suggestions_repas:
                    for item in suggestions_repas[:5]:
                        st.write(f"• **{item['nom']}** : {item['raison']}")

                    if len(suggestions_repas) > 5:
                        st.caption(f"... et {len(suggestions_repas)-5} autres")
                else:
                    st.info("Aucun repas planifié")

            st.markdown("---")

            # Alternatives IA
            st.markdown("### 🔄 Trouver une Alternative")

            col_alt1, col_alt2 = st.columns([3, 1])

            with col_alt1:
                article_recherche = st.text_input(
                    "Article à remplacer",
                    placeholder="Ex: Crème fraîche"
                )

            with col_alt2:
                magasin_alt = st.selectbox(
                    "Magasin",
                    list(MAGASINS.keys()),
                    key="magasin_alt"
                )

            if st.button("🔍 Chercher alternatives", use_container_width=True):
                if article_recherche:
                    with st.spinner("🤖 Recherche..."):
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                            alternatives = loop.run_until_complete(
                                proposer_alternatives_ia(
                                    agent,
                                    article_recherche,
                                    magasin_alt
                                )
                            )

                            if alternatives:
                                st.markdown("#### 💡 Alternatives suggérées")
                                for alt in alternatives:
                                    with st.container():
                                        col1, col2 = st.columns([3, 1])

                                        with col1:
                                            st.markdown(f"**{alt['nom']}**")
                                            st.caption(alt['raison'])

                                            if alt.get('prix_relatif'):
                                                st.caption(f"💶 {alt['prix_relatif']}")

                                        with col2:
                                            if st.button("➕", key=f"alt_{alt['nom']}"):
                                                st.info("Ajouter manuellement dans l'onglet ➕")
                            else:
                                st.warning("Aucune alternative trouvée")

                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")

    # ===================================
    # TAB 3 : AJOUTER MANUELLEMENT
    # ===================================

    with tab3:
        st.subheader("➕ Ajouter un article")

        with st.form("form_ajout_manuel"):
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                nom = st.text_input("Nom de l'article *", placeholder="Ex: Tomates")
                quantite = st.number_input("Quantité *", 0.1, 100.0, 1.0, 0.1)
                unite = st.selectbox("Unité", ["pcs", "kg", "g", "L", "mL", "sachets", "boîtes", "botte"])

            with col_f2:
                priorite = st.selectbox("Priorité", ["basse", "moyenne", "haute"])
                magasin_cible = st.selectbox("Magasin", list(MAGASINS.keys()))

                rayons_dispo = MAGASINS[magasin_cible]["rayons"]
                rayon = st.selectbox("Rayon (optionnel)", ["—"] + rayons_dispo)

            notes = st.text_area("Notes (optionnel)", placeholder="Format, marque...")

            submitted = st.form_submit_button("➕ Ajouter", type="primary")

            if submitted:
                if not nom:
                    st.error("❌ Le nom est obligatoire")
                else:
                    ajouter_article(
                        nom=nom,
                        quantite=quantite,
                        unite=unite,
                        priorite=priorite,
                        rayon=rayon if rayon != "—" else None,
                        magasin=magasin_cible,
                        ia_suggere=False
                    )
                    st.success(f"✅ {nom} ajouté à la liste")
                    st.balloons()
                    st.rerun()

        st.markdown("---")

        # Ajout rapide depuis recettes
        st.markdown("### 🍽️ Depuis une Recette")

        with get_db_context() as db:
            recettes = db.query(Recette).order_by(Recette.nom).all()

        if recettes:
            recette_select = st.selectbox(
                "Sélectionner une recette",
                [r.nom for r in recettes],
                key="recette_add"
            )

            if st.button("➕ Ajouter ingrédients manquants", use_container_width=True):
                recette_id = next(r.id for r in recettes if r.nom == recette_select)
                suggestions = generer_depuis_recettes_selectionnees([recette_id])

                count = 0
                for item in suggestions:
                    ajouter_article(
                        nom=item['nom'],
                        quantite=item['quantite'],
                        unite=item['unite'],
                        priorite=item['priorite'],
                        ia_suggere=True
                    )
                    count += 1

                st.success(f"✅ {count} ingrédients ajoutés")
                st.rerun()
        else:
            st.info("Aucune recette disponible")

        st.markdown("---")

        # Ajout rapide depuis stock
        st.markdown("### 📦 Stock Bas Rapide")

        suggestions = generer_depuis_stock_bas()

        if suggestions:
            for item in suggestions[:10]:
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"• **{item['nom']}** : {item['raison']}")

                with col2:
                    if st.button("➕", key=f"quick_{item['nom']}", use_container_width=True):
                        ajouter_article(
                            nom=item['nom'],
                            quantite=item['quantite'],
                            unite=item['unite'],
                            priorite=item['priorite'],
                            ia_suggere=True
                        )
                        st.success(f"✅ {item['nom']} ajouté")
                        st.rerun()
        else:
            st.success("✅ Pas de stock bas")

    # ===================================
    # TAB 4 : HISTORIQUE & STATS
    # ===================================

    with tab4:
        st.subheader("📊 Historique & Statistiques")

        # Période
        periode = st.selectbox(
            "Période",
            ["7 derniers jours", "30 derniers jours", "90 derniers jours"],
            index=1
        )

        jours = {"7 derniers jours": 7, "30 derniers jours": 30, "90 derniers jours": 90}[periode]

        stats = get_stats_historique(jours)

        # Métriques principales
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)

        with col_h1:
            st.metric("Total acheté", stats["total_achetes"])

        with col_h2:
            st.metric("Suggérés IA", stats["part_ia"])

        with col_h3:
            st.metric(
                "Moyenne/semaine",
                f"{stats['moyenne_par_semaine']:.1f}"
            )

        with col_h4:
            taux_ia = (stats["part_ia"] / stats["total_achetes"] * 100) if stats["total_achetes"] > 0 else 0
            st.metric("% IA", f"{taux_ia:.0f}%")

        st.markdown("---")

        # Articles les plus achetés
        st.markdown("### 🏆 Top Articles")

        if stats["articles_frequents"]:
            df_top = pd.DataFrame([
                {"Article": nom, "Achats": count}
                for nom, count in stats["articles_frequents"].items()
            ])

            st.dataframe(df_top, use_container_width=True, hide_index=True)

            # Graphique
            st.bar_chart(df_top.set_index("Article"))
        else:
            st.info("Pas assez de données")

        st.markdown("---")

        # Historique détaillé
        st.markdown("### 📋 Historique Détaillé")

        df_hist = charger_liste_courses(achetes=True)

        if not df_hist.empty:
            # Filtrer par période
            date_limite = datetime.now() - timedelta(days=jours)
            df_hist = df_hist[df_hist["achete_le"] >= date_limite]

            df_hist = df_hist.sort_values("achete_le", ascending=False)

            st.dataframe(
                df_hist[["nom", "quantite", "unite", "priorite", "ia", "achete_le"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "nom": "Article",
                    "quantite": st.column_config.NumberColumn("Quantité", format="%.1f"),
                    "unite": "Unité",
                    "priorite": "Priorité",
                    "ia": st.column_config.CheckboxColumn("IA"),
                    "achete_le": st.column_config.DatetimeColumn("Acheté le", format="DD/MM/YYYY HH:mm")
                }
            )

            # Export
            st.markdown("---")

            if st.button("📥 Exporter (CSV)", use_container_width=True):
                csv = df_hist.to_csv(index=False)
                st.download_button(
                    "💾 Télécharger",
                    csv,
                    f"historique_courses_{jours}j.csv",
                    "text/csv",
                    use_container_width=True
                )
        else:
            st.info("Aucun historique")

        st.markdown("---")

        # Conseils IA basés sur l'historique
        if agent and stats["total_achetes"] > 10:
            st.markdown("### 🤖 Analyse IA de tes Habitudes")

            if st.button("🔍 Analyser mes habitudes", use_container_width=True):
                with st.spinner("🤖 Analyse en cours..."):
                    try:
                        articles_freq = list(stats["articles_frequents"].items())[:10]

                        prompt = f"""Analyse ces habitudes d'achat:

Articles les plus achetés: {articles_freq}
Total achats sur {jours} jours: {stats['total_achetes']}
Part IA: {stats['part_ia']}

Fournis 3-5 conseils personnalisés pour:
1. Optimiser les courses
2. Économiser
3. Mieux planifier

Format JSON:
{{
  "conseils": [
    {{"type": "optimisation", "conseil": "...", "impact": "moyen"}},
    {{"type": "economie", "conseil": "...", "impact": "haut"}}
  ],
  "opportunites": ["opp1", "opp2"]
}}"""

                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        response = loop.run_until_complete(
                            agent._call_mistral(
                                prompt=prompt,
                                system_prompt="Expert en gestion courses. JSON uniquement.",
                                temperature=0.7,
                                max_tokens=800
                            )
                        )

                        cleaned = response.strip().replace("```json", "").replace("```", "")
                        result = json.loads(cleaned)

                        st.session_state["analyse_habitudes"] = result
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Erreur: {e}")

            # Afficher résultats
            if "analyse_habitudes" in st.session_state:
                result = st.session_state["analyse_habitudes"]

                st.markdown("#### 💡 Conseils Personnalisés")

                for conseil in result.get("conseils", []):
                    impact_emoji = {"haut": "🔥", "moyen": "⚡", "bas": "💡"}
                    emoji = impact_emoji.get(conseil.get("impact", "moyen"), "💡")

                    st.info(f"{emoji} **{conseil.get('type', 'Conseil').capitalize()}**: {conseil.get('conseil', '')}")

                if result.get("opportunites"):
                    st.markdown("#### 🎯 Opportunités")
                    for opp in result["opportunites"]:
                        st.success(f"• {opp}")