"""
Module Suivi Perso - Paramètres Garmin et objectifs
"""

from .utils import UserProfile, get_garmin_service, obtenir_contexte_db, st


def afficher_garmin_settings(data: dict):
    """Affiche les paramètres Garmin"""
    st.subheader("⌚ Garmin Connect")

    user = data.get("user")
    if not user:
        return

    if data.get("garmin_connected"):
        st.success("✅ Garmin connecte")

        # Dernière sync
        if user.garmin_token and user.garmin_token.derniere_sync:
            st.caption(
                f"Dernière sync: {user.garmin_token.derniere_sync.strftime('%d/%m/%Y %H:%M')}"
            )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Synchroniser", type="primary"):
                with st.spinner("Synchronisation..."):
                    try:
                        service = get_garmin_service()
                        result = service.sync_user_data(user.id, days_back=7)
                        st.success(
                            f"✅ {result['activities_synced']} activites, {result['summaries_synced']} jours sync"
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur sync: {e}")

        with col2:
            if st.button("🔌 Deconnecter", type="secondary"):
                try:
                    service = get_garmin_service()
                    service.disconnect_user(user.id)
                    st.success("Garmin deconnecte")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")

    else:
        st.info("Connectez votre montre Garmin pour synchroniser vos donnees.")

        if st.button("🔗 Connecter Garmin", type="primary"):
            st.session_state["garmin_auth_user"] = user.id

            try:
                service = get_garmin_service()
                auth_url, request_token = service.get_authorization_url()

                st.session_state["garmin_request_token"] = request_token

                st.markdown(f"""
                ### Étapes de connexion:
                1. [Cliquez ici pour autoriser]({auth_url})
                2. Connectez-vous à Garmin Connect
                3. Autorisez l'accès
                4. Copiez le code de verification ci-dessous
                """)

                verifier = st.text_input("Code de verification")

                if st.button("✅ Valider"):
                    if verifier:
                        try:
                            service.complete_authorization(user.id, verifier, request_token)
                            st.success("✅ Garmin connecte!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur: {e}")
                    else:
                        st.error("Entrez le code de verification")

            except ValueError as e:
                st.error(str(e))
                st.info("""
                Pour configurer Garmin:
                1. Creez une app sur developer.garmin.com
                2. Ajoutez dans .env.local:
                   - GARMIN_CONSUMER_KEY=xxx
                   - GARMIN_CONSUMER_SECRET=xxx
                """)


def afficher_objectifs(data: dict):
    """Affiche et permet de modifier les objectifs"""
    st.subheader("🎯 Objectifs")

    user = data.get("user")
    if not user:
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        new_pas = st.number_input(
            "👣 Pas/jour",
            min_value=1000,
            max_value=50000,
            value=user.objectif_pas_quotidien,
            step=1000,
        )

    with col2:
        new_cal = st.number_input(
            "🔥 Calories actives/jour",
            min_value=100,
            max_value=2000,
            value=user.objectif_calories_brulees,
            step=50,
        )

    with col3:
        new_min = st.number_input(
            "⏱️ Minutes actives/jour",
            min_value=10,
            max_value=180,
            value=user.objectif_minutes_actives,
            step=5,
        )

    if st.button("💾 Sauvegarder objectifs"):
        try:
            with obtenir_contexte_db() as db:
                u = db.query(UserProfile).filter_by(id=user.id).first()
                u.objectif_pas_quotidien = new_pas
                u.objectif_calories_brulees = new_cal
                u.objectif_minutes_actives = new_min
                db.commit()
                st.success("✅ Objectifs mis à jour!")
                st.rerun()
        except Exception as e:
            st.error(f"Erreur: {e}")
