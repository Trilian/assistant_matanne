# [Précédent code inchangé jusqu'à la section "Ajout Manuel"]

# ===================================
# TAB 3 : AJOUT MANUEL
# ===================================
with tab3:
    st.subheader("➕ Ajouter une recette manuellement")

    with st.form("manual_recipe"):
        # Infos de base
        st.markdown("### 📝 Informations de base")

        col_m1, col_m2 = st.columns(2)

        with col_m1:
            name = st.text_input("Nom de la recette *", placeholder="Ex: Pâtes à la carbonara")
            description = st.text_area(
                "Description",
                placeholder="Décris brièvement la recette...",
                height=100
            )

        with col_m2:
            image_url = st.text_input(
                "URL de l'image (optionnel)",
                placeholder="https://..."
            )
            if image_url:
                st.image(image_url, width=200)

        # Temps et portions
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)

        with col_t1:
            prep_time = st.number_input("Préparation (min)", 0, 300, 15, 5)
        with col_t2:
            cook_time = st.number_input("Cuisson (min)", 0, 300, 30, 5)
        with col_t3:
            servings = st.number_input("Portions", 1, 20, 4)
        with col_t4:
            difficulty = st.selectbox("Difficulté", ["easy", "medium", "hard"])

        # Catégories
        st.markdown("### 🏷️ Catégories et tags")

        col_c1, col_c2 = st.columns(2)

        with col_c1:
            meal_type = st.selectbox("Type de repas", [m.value for m in MealTypeEnum])
            season = st.selectbox("Saison", [s.value for s in SeasonEnum])
            category = st.text_input("Catégorie", placeholder="Végétarien, Italien, etc.")

        with col_c2:
            is_quick = st.checkbox("⚡ Rapide")
            is_balanced = st.checkbox("🥗 Équilibré")
            is_baby_friendly = st.checkbox("👶 Compatible bébé")
            is_batch_friendly = st.checkbox("🍳 Compatible batch")
            is_freezable = st.checkbox("❄️ Congélable")

        # Ingrédients
        st.markdown("### 🥕 Ingrédients")

        if "manual_ingredients" not in st.session_state:
            st.session_state.manual_ingredients = []

        col_ing1, col_ing2, col_ing3, col_ing4 = st.columns([2, 1, 1, 1])

        with col_ing1:
            ing_name = st.text_input("Ingrédient", key="ing_name")
        with col_ing2:
            ing_qty = st.number_input("Quantité", 0.0, 10000.0, 1.0)
        with col_ing3:
            ing_unit = st.text_input("Unité", key="ing_unit", placeholder="g, ml, etc.")
        with col_ing4:
            ing_optional = st.checkbox("Optionnel", key="ing_optional")

        if st.button("➕ Ajouter l'ingrédient", key="add_ingredient"):
            if ing_name:
                st.session_state.manual_ingredients.append({
                    "name": ing_name,
                    "quantity": ing_qty,
                    "unit": ing_unit,
                    "optional": ing_optional
                })
                st.rerun()

        # Afficher les ingrédients ajoutés
        if st.session_state.manual_ingredients:
            st.markdown("**Ingrédients ajoutés :**")
            for idx, ing in enumerate(st.session_state.manual_ingredients):
                col_ing_d1, col_ing_d2, col_ing_d3 = st.columns([4, 1, 1])
                with col_ing_d1:
                    st.write(f"{ing['quantity']} {ing['unit']} de {ing['name']}")
                with col_ing_d2:
                    if ing['optional']:
                        st.caption("Optionnel")
                with col_ing_d3:
                    if st.button("❌", key=f"del_ing_{idx}"):
                        st.session_state.manual_ingredients.pop(idx)
                        st.rerun()

        # Étapes de préparation
        st.markdown("### 📝 Étapes de préparation")

        if "manual_steps" not in st.session_state:
            st.session_state.manual_steps = []

        col_step1, col_step2, col_step3 = st.columns([3, 1, 1])

        with col_step1:
            step_desc = st.text_area("Description de l'étape", key="step_desc", height=80)
        with col_step2:
            step_order = st.number_input("Ordre", 1, 20, len(st.session_state.manual_steps)+1)
        with col_step3:
            step_duration = st.number_input("Durée (min)", 0, 120, 0)

        if st.button("➕ Ajouter l'étape", key="add_step"):
            if step_desc:
                st.session_state.manual_steps.append({
                    "order": step_order,
                    "description": step_desc,
                    "duration": step_duration
                })
                st.rerun()

        # Afficher les étapes ajoutées
        if st.session_state.manual_steps:
            st.markdown("**Étapes ajoutées :**")
            for idx, step in enumerate(sorted(st.session_state.manual_steps, key=lambda x: x['order'])):
                col_step_d1, col_step_d2, col_step_d3 = st.columns([4, 1, 1])
                with col_step_d1:
                    st.write(f"{step['order']}. {step['description']}")
                with col_step_d2:
                    if step['duration']:
                        st.caption(f"{step['duration']}min")
                with col_step_d3:
                    if st.button("❌", key=f"del_step_{idx}"):
                        st.session_state.manual_steps = [s for i, s in enumerate(st.session_state.manual_steps) if i != idx]
                        st.rerun()

        # Versions spéciales
        st.markdown("### 🔄 Versions spéciales (optionnel)")

        with st.expander("👶 Version bébé"):
            baby_instructions = st.text_area(
                "Instructions spécifiques pour bébé",
                placeholder="Ex: Mixer finement, éviter le sel...",
                height=100,
                key="baby_instructions"
            )
            baby_notes = st.text_input(
                "Précautions pour bébé",
                placeholder="Ex: Pas avant 12 mois, risque d'étouffement...",
                key="baby_notes"
            )

        with st.expander("🍳 Version batch cooking"):
            batch_parallel = st.text_area(
                "Étapes parallélisables (une par ligne)",
                placeholder="Ex: Éplucher les légumes\nPréchauffer le four...",
                height=100,
                key="batch_parallel"
            )
            batch_time = st.number_input(
                "Temps optimisé (min)",
                0,
                600,
                key="batch_time"
            )

        # Soumission
        st.markdown("---")
        submitted = st.form_submit_button("➕ Ajouter la recette", type="primary")

        if submitted:
            if not name:
                st.error("Le nom de la recette est obligatoire")
            elif not st.session_state.manual_ingredients:
                st.error("Ajoute au moins un ingrédient")
            elif not st.session_state.manual_steps:
                st.error("Ajoute au moins une étape")
            else:
                # Préparer les données de la recette
                recipe_data = {
                    "name": name,
                    "description": description,
                    "prep_time": prep_time,
                    "cook_time": cook_time,
                    "servings": servings,
                    "difficulty": difficulty,
                    "meal_type": meal_type,
                    "season": season,
                    "category": category,
                    "is_quick": is_quick,
                    "is_balanced": is_balanced,
                    "is_baby_friendly": is_baby_friendly,
                    "is_batch_friendly": is_batch_friendly,
                    "is_freezable": is_freezable,
                    "ai_generated": False,
                    "image_url": image_url,
                    "ingredients": st.session_state.manual_ingredients,
                    "steps": st.session_state.manual_steps
                }

                # Préparer les versions
                version_data = None
                if baby_instructions or baby_notes:
                    version_data = {
                        RecipeVersionEnum.BABY: {
                            "modified_instructions": baby_instructions,
                            "baby_notes": baby_notes
                        }
                    }

                if batch_parallel or batch_time:
                    if version_data is None:
                        version_data = {}
                    version_data[RecipeVersionEnum.BATCH_COOKING] = {
                        "parallel_steps": [s.strip() for s in batch_parallel.split('\n') if s.strip()],
                        "optimized_time": batch_time
                    }

                # Sauvegarder
                recipe_id = save_recipe(recipe_data, version_data)

                # Nettoyer le formulaire
                del st.session_state.manual_ingredients
                del st.session_state.manual_steps

                st.success(f"✅ Recette '{name}' ajoutée avec succès !")
                st.balloons()
                st.rerun()
