"""
Module Jules - Activités adaptées, achats suggérés, conseils développement.

Fonctionnalités:
- 📊 Dashboard: âge, prochains achats suggérés
- 🎨 Activités du jour (adaptées 19 mois)
- 🛒 Shopping Jules (vêtements taille actuelle, jouets recommandés)
- 💡 Conseils (propreté, sommeil, alimentation) - IA
"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional

from src.core.database import get_db_context
from src.core.models import ChildProfile, Milestone, FamilyPurchase
from src.services.base_ai_service import BaseAIService
from src.core.ai import ClientIA


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

# Activités par tranche d'âge (mois)
ACTIVITES_PAR_AGE = {
    (18, 24): [
        {"nom": "Pâte à modeler", "emoji": "🎨", "duree": "20min", "interieur": True, "description": "Développe la motricité fine"},
        {"nom": "Lecture interactive", "emoji": "📚", "duree": "15min", "interieur": True, "description": "Pointer les images, nommer les objets"},
        {"nom": "Jeux d'eau", "emoji": "💧", "duree": "30min", "interieur": False, "description": "Transvaser, verser, éclabousser"},
        {"nom": "Cache-cache simplifié", "emoji": "🙈", "duree": "15min", "interieur": True, "description": "Se cacher derrière un rideau"},
        {"nom": "Danse et musique", "emoji": "🎵", "duree": "15min", "interieur": True, "description": "Bouger sur des comptines"},
        {"nom": "Dessin au doigt", "emoji": "✋", "duree": "20min", "interieur": True, "description": "Peinture au doigt sur grande feuille"},
        {"nom": "Tour de cubes", "emoji": "🧱", "duree": "15min", "interieur": True, "description": "Empiler et faire tomber"},
        {"nom": "Bulles de savon", "emoji": "🫧", "duree": "15min", "interieur": False, "description": "Attraper les bulles"},
        {"nom": "Promenade nature", "emoji": "🌳", "duree": "30min", "interieur": False, "description": "Observer, ramasser des feuilles"},
        {"nom": "Jeu de ballon", "emoji": "⚽", "duree": "15min", "interieur": False, "description": "Rouler, lancer doucement"},
    ],
    (24, 36): [
        {"nom": "Puzzle simple", "emoji": "🧩", "duree": "20min", "interieur": True, "description": "3-6 pièces"},
        {"nom": "Jeu de rôle", "emoji": "🎭", "duree": "20min", "interieur": True, "description": "Dînette, poupées, voitures"},
        {"nom": "Parcours moteur", "emoji": "🏃", "duree": "20min", "interieur": True, "description": "Coussins, tunnels, cerceaux"},
    ],
}

# Tailles vêtements par âge
TAILLES_PAR_AGE = {
    (12, 18): {"vetements": "80-86", "chaussures": "20-21"},
    (18, 24): {"vetements": "86-92", "chaussures": "22-23"},
    (24, 36): {"vetements": "92-98", "chaussures": "24-25"},
}

# Catégories de conseils
CATEGORIES_CONSEILS = {
    "proprete": {"emoji": "🚽", "titre": "Propreté", "description": "Apprentissage du pot"},
    "sommeil": {"emoji": "😴", "titre": "Sommeil", "description": "Routines et astuces"},
    "alimentation": {"emoji": "🍽️", "titre": "Alimentation", "description": "Diversification, autonomie"},
    "langage": {"emoji": "💬", "titre": "Langage", "description": "Stimuler la parole"},
    "motricite": {"emoji": "🏃", "titre": "Motricité", "description": "Développement physique"},
    "social": {"emoji": "👥", "titre": "Social", "description": "Interactions, émotions"},
}


# ═══════════════════════════════════════════════════════════
# SERVICE IA JULES
# ═══════════════════════════════════════════════════════════

class JulesAIService(BaseAIService):
    """Service IA pour suggestions Jules"""
    
    def __init__(self):
        super().__init__(
            client=ClientIA(),
            cache_prefix="jules",
            default_ttl=7200,
            service_name="jules_ai"
        )
    
    async def suggerer_activites(self, age_mois: int, meteo: str = "intérieur", nb: int = 3) -> str:
        """Suggère des activités adaptées à l'âge"""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère {nb} activités {meteo}.

Format pour chaque activité:
🎯 [Nom de l'activité]
⏱️ Durée: X min
📝 Description: Une phrase
✨ Bénéfice: Ce que ça développe

Activités adaptées à cet âge, stimulantes et réalisables à la maison."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en développement de la petite enfance. Réponds en français.",
            max_tokens=600
        )
    
    async def conseil_developpement(self, age_mois: int, theme: str) -> str:
        """Donne un conseil sur un thème de développement"""
        themes_detail = {
            "proprete": "l'apprentissage de la propreté et du pot",
            "sommeil": "le sommeil et les routines du coucher",
            "alimentation": "l'alimentation et l'autonomie à table",
            "langage": "le développement du langage et la parole",
            "motricite": "la motricité (marche, coordination, équilibre)",
            "social": "le développement social et la gestion des émotions",
        }
        
        detail = themes_detail.get(theme, theme)
        
        prompt = f"""Pour un enfant de {age_mois} mois, donne des conseils pratiques sur {detail}.

Inclure:
1. Ce qui est normal à cet âge
2. 3 conseils pratiques
3. Ce qu'il faut éviter
4. Quand consulter si besoin

Ton bienveillant, rassurant et pratique."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es pédiatre et expert en développement de l'enfant. Réponds en français de manière concise.",
            max_tokens=700
        )
    
    async def suggerer_jouets(self, age_mois: int, budget: int = 30) -> str:
        """Suggère des jouets adaptés à l'âge"""
        prompt = f"""Pour un enfant de {age_mois} mois, suggère 5 jouets éducatifs avec un budget de {budget}€ max par jouet.

Format:
🎁 [Nom du jouet]
💰 Prix estimé: X€
🎯 Développe: [compétence]
📝 Pourquoi: Une phrase

Jouets sûrs, éducatifs et adaptés à cet âge."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en jouets éducatifs pour enfants. Réponds en français.",
            max_tokens=600
        )


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def get_age_jules() -> dict:
    """Récupère l'âge de Jules"""
    try:
        with get_db_context() as db:
            jules = db.query(ChildProfile).filter_by(name="Jules", actif=True).first()
            if jules and jules.date_of_birth:
                today = date.today()
                delta = today - jules.date_of_birth
                mois = delta.days // 30
                semaines = delta.days // 7
                return {
                    "mois": mois,
                    "semaines": semaines,
                    "jours": delta.days,
                    "date_naissance": jules.date_of_birth
                }
    except:
        pass
    
    # Valeur par défaut si pas trouvé (Jules né le 22 juin 2024)
    default_birth = date(2024, 6, 22)
    delta = date.today() - default_birth
    return {
        "mois": delta.days // 30,
        "semaines": delta.days // 7,
        "jours": delta.days,
        "date_naissance": default_birth
    }


def get_activites_pour_age(age_mois: int) -> list[dict]:
    """Retourne les activités adaptées à l'âge"""
    for (min_age, max_age), activites in ACTIVITES_PAR_AGE.items():
        if min_age <= age_mois < max_age:
            return activites
    # Par défaut: 18-24 mois
    return ACTIVITES_PAR_AGE.get((18, 24), [])


def get_taille_vetements(age_mois: int) -> dict:
    """Retourne la taille de vêtements pour l'âge"""
    for (min_age, max_age), tailles in TAILLES_PAR_AGE.items():
        if min_age <= age_mois < max_age:
            return tailles
    return {"vetements": "86-92", "chaussures": "22-23"}


def get_achats_jules_en_attente() -> list:
    """Récupère les achats Jules en attente"""
    try:
        with get_db_context() as db:
            return db.query(FamilyPurchase).filter(
                FamilyPurchase.achete == False,
                FamilyPurchase.categorie.in_(["jules_vetements", "jules_jouets", "jules_equipement"])
            ).order_by(FamilyPurchase.priorite).all()
    except:
        return []


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════

def render_dashboard():
    """Affiche le dashboard Jules"""
    age = get_age_jules()
    tailles = get_taille_vetements(age["mois"])
    achats = get_achats_jules_en_attente()
    
    st.subheader("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🎂 Âge", f"{age['mois']} mois", f"{age['semaines']} semaines")
    
    with col2:
        st.metric("👕 Taille vêtements", tailles["vetements"])
    
    with col3:
        st.metric("👟 Pointure", tailles["chaussures"])
    
    # Achats suggérés
    if achats:
        st.markdown("---")
        st.markdown("**🛒 Achats suggérés:**")
        for achat in achats[:3]:
            emoji = "🔴" if achat.priorite in ["urgent", "haute"] else "🟡"
            st.write(f"{emoji} {achat.nom} ({achat.categorie.replace('jules_', '')})")


def render_activites():
    """Affiche les activités du jour"""
    age = get_age_jules()
    activites = get_activites_pour_age(age["mois"])
    
    st.subheader("🎨 Activités du jour")
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        filtre_lieu = st.selectbox("Lieu", ["Tous", "Intérieur", "Extérieur"], key="filtre_lieu")
    with col2:
        if st.button("🤖 Suggestions IA"):
            st.session_state["jules_show_ai_activities"] = True
    
    # Filtrer
    if filtre_lieu == "Intérieur":
        activites = [a for a in activites if a.get("interieur", True)]
    elif filtre_lieu == "Extérieur":
        activites = [a for a in activites if not a.get("interieur", True)]
    
    # Afficher
    for i, act in enumerate(activites):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{act['emoji']} {act['nom']}**")
                st.caption(f"⏱️ {act['duree']} • {'🏠' if act.get('interieur') else '🌳'}")
                st.write(act["description"])
            with col2:
                if st.button("✅ Fait", key=f"act_done_{i}"):
                    st.success("Super ! 🎉")
    
    # Suggestions IA
    if st.session_state.get("jules_show_ai_activities"):
        st.markdown("---")
        st.markdown("**🤖 Suggestions IA:**")
        
        with st.spinner("Génération en cours..."):
            try:
                import asyncio
                service = JulesAIService()
                meteo = "intérieur" if filtre_lieu != "Extérieur" else "extérieur"
                result = asyncio.run(service.suggerer_activites(age["mois"], meteo))
                st.markdown(result)
            except Exception as e:
                st.error(f"Erreur IA: {e}")
        
        if st.button("Fermer"):
            st.session_state["jules_show_ai_activities"] = False
            st.rerun()


def render_shopping():
    """Affiche le shopping Jules"""
    age = get_age_jules()
    tailles = get_taille_vetements(age["mois"])
    
    st.subheader("🛒 Shopping Jules")
    
    # Info tailles
    st.info(f"📏 Taille actuelle: **{tailles['vetements']}** • Pointure: **{tailles['chaussures']}**")
    
    # Tabs par catégorie
    tabs = st.tabs(["👕 Vêtements", "🧸 Jouets", "🛠️ Équipement", "➕ Ajouter"])
    
    with tabs[0]:
        render_achats_categorie("jules_vetements")
    
    with tabs[1]:
        render_achats_categorie("jules_jouets")
        
        # Suggestions IA jouets
        if st.button("🤖 Suggérer des jouets"):
            with st.spinner("Génération..."):
                try:
                    import asyncio
                    service = JulesAIService()
                    result = asyncio.run(service.suggerer_jouets(age["mois"]))
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Erreur: {e}")
    
    with tabs[2]:
        render_achats_categorie("jules_equipement")
    
    with tabs[3]:
        render_form_ajout_achat()


def render_achats_categorie(categorie: str):
    """Affiche les achats d'une catégorie"""
    try:
        with get_db_context() as db:
            achats = db.query(FamilyPurchase).filter(
                FamilyPurchase.categorie == categorie,
                FamilyPurchase.achete == False
            ).order_by(FamilyPurchase.priorite).all()
            
            if not achats:
                st.caption("Aucun article en attente")
                return
            
            for achat in achats:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        prio_emoji = {"urgent": "🔴", "haute": "🟠", "moyenne": "🟡", "basse": "🟢"}.get(achat.priorite, "⚪")
                        st.markdown(f"**{prio_emoji} {achat.nom}**")
                        if achat.taille:
                            st.caption(f"Taille: {achat.taille}")
                        if achat.description:
                            st.caption(achat.description)
                    
                    with col2:
                        if achat.prix_estime:
                            st.write(f"~{achat.prix_estime:.0f}€")
                    
                    with col3:
                        if st.button("✅", key=f"buy_{achat.id}"):
                            achat.achete = True
                            achat.date_achat = date.today()
                            db.commit()
                            st.success("Acheté!")
                            st.rerun()
    except Exception as e:
        st.error(f"Erreur: {e}")


def render_form_ajout_achat():
    """Formulaire d'ajout d'achat"""
    with st.form("add_purchase_jules"):
        nom = st.text_input("Nom de l'article *")
        
        col1, col2 = st.columns(2)
        with col1:
            categorie = st.selectbox("Catégorie", [
                ("jules_vetements", "👕 Vêtements"),
                ("jules_jouets", "🧸 Jouets"),
                ("jules_equipement", "🛠️ Équipement"),
            ], format_func=lambda x: x[1])
        
        with col2:
            priorite = st.selectbox("Priorité", ["moyenne", "haute", "urgent", "basse"])
        
        col3, col4 = st.columns(2)
        with col3:
            prix = st.number_input("Prix estimé (€)", min_value=0.0, step=5.0)
        with col4:
            taille = st.text_input("Taille (optionnel)")
        
        url = st.text_input("Lien (optionnel)")
        description = st.text_area("Notes", height=80)
        
        if st.form_submit_button("➕ Ajouter", type="primary"):
            if not nom:
                st.error("Nom requis")
            else:
                try:
                    with get_db_context() as db:
                        achat = FamilyPurchase(
                            nom=nom,
                            categorie=categorie[0],
                            priorite=priorite,
                            prix_estime=prix if prix > 0 else None,
                            taille=taille or None,
                            url=url or None,
                            description=description or None,
                            suggere_par="manuel"
                        )
                        db.add(achat)
                        db.commit()
                        st.success(f"✅ {nom} ajouté!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")


def render_conseils():
    """Affiche les conseils développement"""
    age = get_age_jules()
    
    st.subheader("💡 Conseils Développement")
    st.caption(f"Adaptés pour {age['mois']} mois")
    
    # Sélection du thème
    cols = st.columns(3)
    themes = list(CATEGORIES_CONSEILS.items())
    
    for i, (key, info) in enumerate(themes):
        col = cols[i % 3]
        with col:
            if st.button(f"{info['emoji']} {info['titre']}", key=f"conseil_{key}", use_container_width=True):
                st.session_state["jules_conseil_theme"] = key
    
    # Afficher le conseil sélectionné
    theme = st.session_state.get("jules_conseil_theme")
    if theme:
        st.markdown("---")
        info = CATEGORIES_CONSEILS[theme]
        st.markdown(f"### {info['emoji']} {info['titre']}")
        
        with st.spinner("Génération du conseil..."):
            try:
                import asyncio
                service = JulesAIService()
                result = asyncio.run(service.conseil_developpement(age["mois"], theme))
                st.markdown(result)
            except Exception as e:
                st.error(f"Erreur: {e}")


# ═══════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée du module Jules"""
    st.title("👶 Jules")
    
    age = get_age_jules()
    st.caption(f"🎂 {age['mois']} mois • Né le {age['date_naissance'].strftime('%d/%m/%Y')}")
    
    # Tabs principaux
    tabs = st.tabs(["📊 Dashboard", "🎨 Activités", "🛒 Shopping", "💡 Conseils"])
    
    with tabs[0]:
        render_dashboard()
    
    with tabs[1]:
        render_activites()
    
    with tabs[2]:
        render_shopping()
    
    with tabs[3]:
        render_conseils()
