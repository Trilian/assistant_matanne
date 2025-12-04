import streamlit as st
from dotenv import load_dotenv
import os
from src.core.database import get_db_context, check_connection
from src.core.models import Recette, IngrédientRecette, ÉtapeRecette, Produit
from src.services.ai_recette_service import AIRecetteService

# Chargement des variables d'environnement et initialisation
load_dotenv()
try:
    ai_service = AIRecetteService()
except Exception as e:
    st.error(f"❌ Impossible d'initialiser le service AI: {e}")
    ai_service = None  # Permet au reste du code de fonctionner

# Vérifie la connexion à la base de données au démarrage
# Test de connexion au démarrage
if not check_connection():
    st.error("❌ Impossible de se connecter à la base de données Supabase")
    st.write("Vérifie que :")
    st.write("- Tes secrets Streamlit sont bien configurés")
    st.write("- Ton projet Supabase est bien démarré")
    st.write("- Le mot de passe est correct")
    st.write("- L'IP de Streamlit Cloud est autorisée dans Supabase")
    st.stop()  # Arrête l'application si la connexion échoue

# Affiche les infos de connexion (pour débogage)
db_info = get_db_info()
st.write("🔌 Connexion à la base de données établie avec succès !")
st.write(f"📡 Connecté à : {db_info['host']}")
st.write(f"👤 Utilisateur : {db_info['user']}")
# =============================================
# FONCTIONS EXISTANTES (sans modification)
# =============================================
def afficher_recettes_existantes():
    """Affiche la liste des recettes existantes."""
    st.subheader("📚 Mes recettes")
    try:
        with get_db_context() as db:
            from src.core.models import Recette
            recettes = db.query(Recette).all()
        for recette in recettes:
            with st.expander(f"🍽️ {recette.nom}"):
                st.markdown(f"**Temps** : {recette.temps_preparation + recette.temps_cuisson} min | "
                            f"**Portions** : {recette.portions_adultes} adultes, {recette.portions_bébé} bébé(s)")
                if st.button(f"Modifier {recette.nom}"):
                    modifier_recette(recette.id)
                if st.button(f"Supprimer {recette.nom}"):
                    db.delete(recette)
                    db.commit()
                    st.rerun()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des recettes: {e}")

def ajouter_ingrédients_étapes(recette_id: int):
    """Ajoute les ingrédients et étapes pour une recette."""
    recette = db.query(Recette).get(recette_id)
    st.subheader(f"🥕 Ajouter ingrédients et étapes pour {recette.nom}")

    # Ajout des ingrédients
    with st.form("nouvel_ingrédient"):
        nom = st.text_input("Nom de l'ingrédient")
        quantité = st.number_input("Quantité", min_value=0.1, value=1.0)
        unité = st.text_input("Unité (g, L, unité, etc.)", value="g")
        submitted = st.form_submit_button("Ajouter l'ingrédient")
        if submitted:
            db.add(IngrédientRecette(
                recette_id=recette_id,
                nom=nom,
                quantité=quantité,
                unité=unité
            ))
            db.commit()
            st.rerun()

    # Ajout des étapes
    with st.form("nouvelle_étape"):
        description = st.text_area("Description de l'étape")
        ordre = st.number_input("Ordre", min_value=1, value=1)
        submitted = st.form_submit_button("Ajouter l'étape")
        if submitted:
            db.add(ÉtapeRecette(
                recette_id=recette_id,
                ordre=ordre,
                description=description
            ))
            db.commit()
            st.rerun()

    # Affichage des ingrédients et étapes existants
    st.markdown("### Ingrédients")
    for ingrédient in recette.ingrédients:
        st.markdown(f"- {ingrédient.quantité} {ingrédient.unité} de {ingrédient.nom}")

    st.markdown("### Étapes")
    for étape in sorted(recette.étapes, key=lambda x: x.ordre):
        st.markdown(f"{étape.ordre}. {étape.description}")

def modifier_recette(recette_id: int):
    """Modifie une recette existante."""
    recette = db.query(Recette).get(recette_id)
    with st.form(f"modifier_recette_{recette_id}"):
        nom = st.text_input("Nom de la recette", value=recette.nom)
        temps_prep = st.number_input("Temps de préparation (min)", value=recette.temps_preparation)
        temps_cuisson = st.number_input("Temps de cuisson (min)", value=recette.temps_cuisson)
        difficulté = st.selectbox("Difficulté", ["facile", "moyenne", "difficile"], index=["facile", "moyenne", "difficile"].index(recette.difficulté))
        submitted = st.form_submit_button("Enregistrer")
        if submitted:
            recette.nom = nom
            recette.temps_preparation = temps_prep
            recette.temps_cuisson = temps_cuisson
            recette.difficulté = difficulté
            db.commit()
            st.rerun()

# =============================================
# NOUVELLES FONCTIONNALITÉS (avec onglets)
# =============================================

def onglet_ajout_manuel():
    """Onglet pour l'ajout manuel d'une recette."""
    with st.form("nouvelle_recette"):
        nom = st.text_input("Nom de la recette")
        temps_prep = st.number_input("Temps de préparation (min)", min_value=1, value=15)
        temps_cuisson = st.number_input("Temps de cuisson (min)", min_value=0, value=20)
        difficulté = st.selectbox("Difficulté", ["facile", "moyenne", "difficile"])
        catégorie = st.selectbox("Catégorie", ["viande", "poisson", "végétarien", "végétalien", "sans gluten", "autre"])
        type_repas = st.selectbox("Type de repas", ["petit-déjeuner", "déjeuner", "dîner", "goûter"])
        portions_adultes = st.number_input("Portions adultes", min_value=1, value=2)
        portions_bébé = st.number_input("Portions bébé", min_value=0, value=0)

        col1, col2 = st.columns(2)
        with col1:
            compatible_bébé = st.checkbox("Compatible bébé")
            compatible_congélation = st.checkbox("Compatible congélation")
        with col2:
            tag_rapide = st.checkbox("Tag rapide")
            tag_équilibré = st.checkbox("Tag équilibré")
        saisonnalité = st.selectbox("Saisonnalité", ["", "printemps", "été", "automne", "hiver"])

        submitted = st.form_submit_button("Ajouter")
        if submitted:
            nouvelle_recette = Recette(
                nom=nom,
                temps_preparation=temps_prep,
                temps_cuisson=temps_cuisson,
                difficulté=difficulté,
                catégorie=catégorie,
                type_repas=type_repas,
                portions_adultes=portions_adultes,
                portions_bébé=portions_bébé,
                compatible_bébé=compatible_bébé,
                compatible_congélation=compatible_congélation,
                tag_rapide=tag_rapide,
                tag_équilibré=tag_équilibré,
                saisonnalité=saisonnalité
            )
            db.add(nouvelle_recette)
            db.commit()
            st.success("Recette ajoutée ! Ajoute maintenant les ingrédients et étapes.")
            ajouter_ingrédients_étapes(nouvelle_recette.id)

def onglet_génération_automatique():
    """Onglet pour générer des recettes avec filtres et versions."""
    with st.form("génération_recettes"):
        col1, col2 = st.columns(2)

        with col1:
            nombre_recettes = st.number_input("Nombre de recettes", min_value=1, max_value=5, value=3)
            type_plat = st.selectbox(
                "Type de plat",
                ["plat", "dessert", "entrée", "petit-déjeuner", "tous"]
            )
            saison = st.selectbox(
                "Saison",
                ["toutes", "printemps", "été", "automne", "hiver"]
            )

        with col2:
            version = st.selectbox(
                "Version",
                ["classique", "batch cooking", "adapté bébé"]
            )
            équilibré = st.checkbox("Recettes équilibrées")
            temps_max = st.number_input("Temps max (min)", min_value=10, max_value=120, value=60)

        ingrédients = st.text_input("Ingrédients à inclure (optionnel, séparés par des virgules)")

        submitted = st.form_submit_button("Générer les recettes")

        if submitted:
            try:
                ingrédients_list = [i.strip() for i in ingrédients.split(",")] if ingrédients else None

                with st.spinner("Génération des recettes en cours..."):
                    recettes = ai_service.générer_recettes(
                        nombre=nombre_recettes,
                        type_plat=type_plat if type_plat != "tous" else None,
                        saison=saison if saison != "toutes" else None,
                        ingrédients=ingrédients_list,
                        version=version.replace(" ", "_"),  # Remplace les espaces
                        temps_max=temps_max,
                        équilibré=équilibré
                    )

                    st.session_state.recettes_générées = {
                        "recettes": recettes,
                        "version": version
                    }
                    st.success(f"{len(recettes)} recettes générées avec succès!")

            except Exception as e:
                st.error(f"Erreur lors de la génération: {str(e)}")
                st.error("Vérifie ta clé API Mistral ou les paramètres de génération.")

    if "recettes_générées" in st.session_state:
        st.subheader(f"Recettes générées ({st.session_state.recettes_générées['version']})")

        selected_recipes = []
        for i, recette in enumerate(st.session_state.recettes_générées["recettes"]):
            with st.expander(f"🍽️ {recette.get('nom', 'Recette sans nom')}"):
                st.markdown(f"**{recette.get('description', '')}**")
                st.markdown(f"⏱️ {recette.get('temps_preparation', 0) + recette.get('temps_cuisson', 0)} min | 🍽️ {recette.get('portions', 2)} portions")

                # Affichage des ingrédients
                if "ingrédients" in recette:
                    st.markdown("**Ingrédients:**")
                    for ingr in recette["ingrédients"]:
                        st.markdown(f"- {ingr.get('quantité', '')} {ingr.get('unité', '')} de {ingr.get('nom', '')}")

                # Affichage des étapes
                if "étapes" in recette:
                    st.markdown("**Étapes:**")
                    for j, étape in enumerate(recette["étapes"], 1):
                        st.markdown(f"{j}. {étape}")

                # Version bébé
                if st.session_state.recettes_générées["version"] == "adapté bébé" and "adaptation_bébé" in recette:
                    with st.expander("👶 Version bébé"):
                        st.markdown("**Étapes adaptées:**")
                        for étape in recette["adaptation_bébé"].get("étapes", []):
                            st.markdown(f"- {étape}")

                # Batch cooking
                if st.session_state.recettes_générées["version"] == "batch cooking" and "batch_info" in recette:
                    with st.expander("🍳 Batch cooking"):
                        st.markdown(f"**Temps optimisé:** {recette['batch_info'].get('temps_optimisé', '')} min")
                        st.markdown("**Étapes parallèles:**")
                        for étape in recette["batch_info"].get("étapes_parallèles", []):
                            st.markdown(f"- {étape}")

                if st.checkbox(f"Sélectionner cette recette", key=f"recette_{i}"):
                    selected_recipes.append(recette)

        if selected_recipes and st.button("Ajouter les recettes sélectionnées"):
            for recette in selected_recipes:
                nouvelle_recette = Recette(
                    nom=recette.get("nom", "Recette sans nom"),
                    temps_preparation=recette.get("temps_preparation", 0),
                    temps_cuisson=recette.get("temps_cuisson", 0),
                    difficulté=recette.get("difficulté", "moyenne"),
                    portions_adultes=recette.get("portions", 2),
                    type_repas=recette.get("type", "plat"),
                    saisonnalité=recette.get("saison", "toute l'année")
                )
                db.add(nouvelle_recette)
                db.commit()

                # Ajoute les ingrédients SANS le champ optionnel
                if "ingrédients" in recette:
                    for ingr in recette["ingrédients"]:
                        db.add(IngrédientRecette(
                            recette_id=nouvelle_recette.id,
                            nom=ingr.get("nom", ""),
                            quantité=ingr.get("quantité", 0),
                            unité=ingr.get("unité", "")
                            # On ne mentionne pas 'optionnel' pour l'instant
                        ))
                    db.commit()

            st.success(f"✅ {len(selected_recipes)} recettes ajoutées à ta collection!")

# =============================================
# PAGE PRINCIPALE AVEC ONGLETS
# =============================================

def app():
    st.title("🍲 Gestion des recettes")

    # Onglets pour les recettes
    onglets = st.tabs(["Recettes existantes", "Ajouter une recette"])

    with onglets[0]:
        afficher_recettes_existantes()

    with onglets[1]:
        onglets_ajout = st.tabs(["Ajout manuel", "Génération automatique"])

        with onglets_ajout[0]:
            onglet_ajout_manuel()

        with onglets_ajout[1]:
            onglet_génération_automatique()

if __name__ == "__main__":
    main()