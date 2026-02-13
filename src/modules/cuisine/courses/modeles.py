"""
Gestion des modèles de listes récurrentes.
"""

from ._common import get_courses_service, logger, st


def render_modeles():
    """Gestion des modèles de listes récurrentes (Phase 2: Persistance BD)"""
    st.subheader("ðŸ“„ Modèles de listes - Phase 2")

    service = get_courses_service()

    try:
        # Récupérer modèles depuis BD (Phase 2)
        modeles = service.get_modeles(utilisateur_id=None)  # TODO: user_id depuis auth

        tab_mes_modeles, tab_nouveau = st.tabs(["ðŸ“‹ Mes modèles", "âž• Nouveau"])

        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # ONGLET: MES MODÈLES (affichage et actions)
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

        with tab_mes_modeles:
            st.write("**Modèles sauvegardés en BD**")

            if not modeles:
                st.info("⏰ Aucun modèle sauvegardé. Créez-en un dans l'onglet 'Nouveau'!")
            else:
                for modele in modeles:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 1, 1])

                        with col1:
                            st.write(f"**ðŸ“‹ {modele['nom']}**")
                            if modele.get("description"):
                                st.caption(f"ðŸ“ {modele['description']}")
                            st.caption(
                                f"ðŸ“¦ {len(modele.get('articles', []))} articles | ðŸ“… {modele.get('cree_le', '')[:10]}"
                            )

                        with col2:
                            if st.button(
                                "ðŸ“¥ Charger",
                                key=f"modele_load_{modele['id']}",
                                use_container_width=True,
                                help="Charger ce modèle dans la liste",
                            ):
                                try:
                                    # Appliquer le modèle (crée articles courses)
                                    article_ids = service.appliquer_modele(modele["id"])
                                    if not article_ids:
                                        st.warning("âš ï¸ Modèle chargé mais aucun article trouvé")
                                    else:
                                        st.success(
                                            f"âœ… Modèle chargé ({len(article_ids)} articles)!"
                                        )
                                        st.session_state.courses_refresh += 1
                                        st.rerun()
                                except Exception as e:
                                    import traceback

                                    st.error(f"âŒ Erreur: {str(e)}")
                                    with st.expander("ðŸ“‹ Détails d'erreur"):
                                        st.code(traceback.format_exc())

                        with col3:
                            if st.button(
                                "ðŸ—‘ï¸ Supprimer",
                                key=f"modele_del_{modele['id']}",
                                use_container_width=True,
                                help="Supprimer ce modèle",
                            ):
                                try:
                                    service.delete_modele(modele["id"])
                                    st.success("âœ… Modèle supprimé!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"âŒ Erreur: {str(e)}")

                        # Afficher les articles du modèle
                        with st.expander(f"ðŸ‘ï¸ Voir {len(modele.get('articles', []))} articles"):
                            for article in modele.get("articles", []):
                                priorite_emoji = (
                                    "ðŸ”´"
                                    if article["priorite"] == "haute"
                                    else ("ðŸŸ¡" if article["priorite"] == "moyenne" else "ðŸŸ¢")
                                )
                                st.write(
                                    f"{priorite_emoji} **{article['nom']}** - {article['quantite']} {article['unite']} ({article['rayon']})"
                                )
                                if article.get("notes"):
                                    st.caption(f"ðŸ“Œ {article['notes']}")

        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # ONGLET: CRÉER NOUVEAU MODÈLE
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

        with tab_nouveau:
            st.write("**Sauvegarder la liste actuelle comme modèle réutilisable**")

            # Récupérer liste actuelle
            liste_actuelle = service.get_liste_courses(achetes=False)

            if not liste_actuelle:
                st.warning("âš ï¸ La liste est vide. Ajoutez des articles d'abord!")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    nom_modele = st.text_input(
                        "Nom du modèle",
                        placeholder="ex: Courses hebdomadaires",
                        max_chars=100,
                        key="new_modele_name",
                    )

                with col2:
                    description = st.text_area(
                        "Description (optionnel)",
                        placeholder="ex: Courses standard pour 4 personnes",
                        max_chars=500,
                        height=50,
                        key="new_modele_desc",
                    )

                st.divider()

                # Aperçu des articles à sauvegarder
                st.subheader(f"ðŸ“¦ Articles ({len(liste_actuelle)})")
                for i, article in enumerate(liste_actuelle):
                    priorite_emoji = (
                        "ðŸ”´"
                        if article["priorite"] == "haute"
                        else ("ðŸŸ¡" if article["priorite"] == "moyenne" else "ðŸŸ¢")
                    )
                    st.write(
                        f"{i+1}. {priorite_emoji} **{article['ingredient_nom']}** - {article['quantite_necessaire']} {article['unite']} ({article['rayon_magasin']})"
                    )

                st.divider()

                if st.button(
                    "ðŸ’¾ Sauvegarder comme modèle", use_container_width=True, type="primary"
                ):
                    if not nom_modele or nom_modele.strip() == "":
                        st.error("âš ï¸ Entrez un nom pour le modèle")
                    else:
                        try:
                            # Préparer les données articles
                            articles_data = [
                                {
                                    "ingredient_id": a.get("ingredient_id"),
                                    "nom": a.get("ingredient_nom"),
                                    "quantite": float(a.get("quantite_necessaire", 1.0)),
                                    "unite": a.get("unite", "pièce"),
                                    "rayon": a.get("rayon_magasin", "Autre"),
                                    "priorite": a.get("priorite", "moyenne"),
                                    "notes": a.get("notes"),
                                }
                                for a in liste_actuelle
                            ]

                            # Sauvegarder en BD (Phase 2)
                            modele_id = service.create_modele(
                                nom=nom_modele.strip(),
                                articles=articles_data,
                                description=description.strip() if description else None,
                                utilisateur_id=None,  # TODO: user_id depuis auth
                            )

                            st.success(f"âœ… Modèle '{nom_modele}' créé et sauvegardé en BD!")
                            st.balloons()
                            st.rerun()
                        except Exception as e:
                            st.error(f"âŒ Erreur lors de la sauvegarde: {str(e)}")
                            logger.error(f"Erreur create_modele: {e}")

    except Exception as e:
        st.error(f"âŒ Erreur: {str(e)}")
        logger.error(f"Erreur render_modeles: {e}")


__all__ = ["render_modeles"]
