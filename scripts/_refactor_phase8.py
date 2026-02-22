"""Phase 8 refactoring script - Replace obtenir_contexte_db with service calls."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def refactor_achats_components():
    """Refactor achats_famille/components.py"""
    fp = ROOT / "src" / "modules" / "famille" / "achats_famille" / "components.py"
    content = fp.read_text(encoding="utf-8")

    # Replace the dashboard DB block
    old = (
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
        "            urgents = (\n"
        "                db.query(FamilyPurchase)\n"
        "                .filter(\n"
        '                    FamilyPurchase.achete == False, FamilyPurchase.priorite.in_(["urgent", "haute"])\n'
        "                )\n"
        "                .order_by(FamilyPurchase.priorite)\n"
        "                .limit(5)\n"
        "                .all()\n"
        "            )\n"
        "\n"
        "            if urgents:\n"
        "                for p in urgents:\n"
        '                    cat_info = CATEGORIES.get(p.categorie, {"emoji": "\U0001f4e6"})\n'
        '                    prio_info = PRIORITES.get(p.priorite, {"emoji": "\u26aa"})\n'
        "\n"
        "                    col1, col2 = st.columns([4, 1])\n"
        "                    with col1:\n"
        "                        st.write(f\"{prio_info['emoji']} {cat_info['emoji']} **{p.nom}**\")\n"
        "                    with col2:\n"
        "                        if p.prix_estime:\n"
        '                            st.write(f"~{p.prix_estime:.0f}\u20ac")\n'
        "            else:\n"
        '                st.success("\u2705 Rien d\'urgent!")\n'
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        '        etat_vide("Aucun achat urgent", "\U0001f4b3")'
    )

    new = (
        "    try:\n"
        "        urgents = obtenir_service_achats_famille().get_urgents(limit=5)\n"
        "\n"
        "        if urgents:\n"
        "            for p in urgents:\n"
        '                cat_info = CATEGORIES.get(p.categorie, {"emoji": "\U0001f4e6"})\n'
        '                prio_info = PRIORITES.get(p.priorite, {"emoji": "\u26aa"})\n'
        "\n"
        "                col1, col2 = st.columns([4, 1])\n"
        "                with col1:\n"
        "                    st.write(f\"{prio_info['emoji']} {cat_info['emoji']} **{p.nom}**\")\n"
        "                with col2:\n"
        "                    if p.prix_estime:\n"
        '                        st.write(f"~{p.prix_estime:.0f}\u20ac")\n'
        "        else:\n"
        '            st.success("\u2705 Rien d\'urgent!")\n'
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        '        etat_vide("Aucun achat urgent", "\U0001f4b3")'
    )

    assert old in content, "Dashboard block not found in achats components"
    content = content.replace(old, new)

    # Replace the add_form DB block
    old_form = (
        "                try:\n"
        "                    with obtenir_contexte_db() as db:\n"
        "                        purchase = FamilyPurchase(\n"
        "                            nom=nom,\n"
        "                            categorie=categorie,\n"
        "                            priorite=priorite,\n"
        "                            prix_estime=prix if prix > 0 else None,\n"
        "                            taille=taille or None,\n"
        "                            magasin=magasin or None,\n"
        "                            url=url or None,\n"
        "                            description=description or None,\n"
        "                            age_recommande_mois=age_recommande,\n"
        '                            suggere_par="manuel",\n'
        "                        )\n"
        "                        db.add(purchase)\n"
        "                        db.commit()\n"
        '                        st.success(f"\u2705 {nom} ajoute!")\n'
        "                        st.rerun()\n"
        "                except Exception as e:\n"
        '                    st.error(f"Erreur: {e}")'
    )

    new_form = (
        "                try:\n"
        "                    obtenir_service_achats_famille().ajouter_achat(\n"
        "                        nom=nom,\n"
        "                        categorie=categorie,\n"
        "                        priorite=priorite,\n"
        "                        prix_estime=prix if prix > 0 else None,\n"
        "                        taille=taille or None,\n"
        "                        magasin=magasin or None,\n"
        "                        url=url or None,\n"
        "                        description=description or None,\n"
        "                        age_recommande_mois=age_recommande,\n"
        '                        suggere_par="manuel",\n'
        "                    )\n"
        '                    st.success(f"\u2705 {nom} ajoute!")\n'
        "                    st.rerun()\n"
        "                except Exception as e:\n"
        '                    st.error(f"Erreur: {e}")'
    )

    assert old_form in content, "Form block not found in achats components"
    content = content.replace(old_form, new_form)

    assert "obtenir_contexte_db" not in content, "Still has obtenir_contexte_db!"
    fp.write_text(content, encoding="utf-8")
    print("  OK achats_famille/components.py")


def refactor_weekend_utils():
    """Refactor weekend/utils.py"""
    fp = ROOT / "src" / "modules" / "famille" / "weekend" / "utils.py"
    content = fp.read_text(encoding="utf-8")

    # Replace import
    content = content.replace(
        "from src.core.db import obtenir_contexte_db\n",
        "from src.services.famille.weekend import obtenir_service_weekend\n",
    )

    # Remove obtenir_contexte_db from __all__
    content = content.replace(
        '    "obtenir_contexte_db",\n',
        "",
    )

    # Replace get_weekend_activities
    old = (
        "def get_weekend_activities(saturday, sunday) -> dict:\n"
        '    """Recup\u00e8re les activit\u00e9s du weekend"""\n'
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
        "            activities = (\n"
        "                db.query(WeekendActivity)\n"
        "                .filter(WeekendActivity.date_prevue.in_([saturday, sunday]))\n"
        "                .order_by(WeekendActivity.heure_debut)\n"
        "                .all()\n"
        "            )\n"
        "            return {\n"
        '                "saturday": [a for a in activities if a.date_prevue == saturday],\n'
        '                "sunday": [a for a in activities if a.date_prevue == sunday],\n'
        "            }\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        '        return {"saturday": [], "sunday": []}'
    )
    new = (
        "def get_weekend_activities(saturday, sunday) -> dict:\n"
        '    """Recup\u00e8re les activit\u00e9s du weekend"""\n'
        "    try:\n"
        "        return obtenir_service_weekend().lister_activites_weekend(saturday, sunday)\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        '        return {"saturday": [], "sunday": []}'
    )
    assert old in content, "get_weekend_activities not found"
    content = content.replace(old, new)

    # Replace get_budget_weekend
    old = (
        "def get_budget_weekend(saturday, sunday) -> dict:\n"
        '    """Calcule le budget du weekend"""\n'
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
        "            activities = (\n"
        "                db.query(WeekendActivity)\n"
        "                .filter(WeekendActivity.date_prevue.in_([saturday, sunday]))\n"
        "                .all()\n"
        "            )\n"
        "            return {\n"
        '                "estime": sum(a.cout_estime or 0 for a in activities),\n'
        '                "reel": sum(\n'
        '                    a.cout_reel or 0 for a in activities if a.statut == "termine"\n'
        "                ),\n"
        "            }\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        '        return {"estime": 0, "reel": 0}'
    )
    new = (
        "def get_budget_weekend(saturday, sunday) -> dict:\n"
        '    """Calcule le budget du weekend"""\n'
        "    try:\n"
        "        return obtenir_service_weekend().get_budget_weekend(saturday, sunday)\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        '        return {"estime": 0, "reel": 0}'
    )
    assert old in content, "get_budget_weekend not found"
    content = content.replace(old, new)

    # Replace get_lieux_testes
    old = (
        "def get_lieux_testes() -> list:\n"
        '    """Recup\u00e8re les lieux d\u00e9j\u00e0 test\u00e9s"""\n'
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
        "            return (\n"
        "                db.query(WeekendActivity)\n"
        "                .filter(\n"
        '                    WeekendActivity.statut == "termine",\n'
        "                    WeekendActivity.note_lieu.isnot(None),\n"
        "                )\n"
        "                .order_by(WeekendActivity.note_lieu.desc())\n"
        "                .all()\n"
        "            )\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        "        return []"
    )
    new = (
        "def get_lieux_testes() -> list:\n"
        '    """Recup\u00e8re les lieux d\u00e9j\u00e0 test\u00e9s"""\n'
        "    try:\n"
        "        return obtenir_service_weekend().get_lieux_testes()\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        "        return []"
    )
    assert old in content, "get_lieux_testes not found"
    content = content.replace(old, new)

    # Replace mark_activity_done
    old = (
        "def mark_activity_done(activity_id: int):\n"
        '    """Marque une activit\u00e9 comme termin\u00e9e"""\n'
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
        "            activity = db.get(WeekendActivity, activity_id)\n"
        "            if activity:\n"
        '                activity.statut = "termine"\n'
        "                db.commit()\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")'
    )
    new = (
        "def mark_activity_done(activity_id: int):\n"
        '    """Marque une activit\u00e9 comme termin\u00e9e"""\n'
        "    try:\n"
        "        obtenir_service_weekend().marquer_termine(activity_id)\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")'
    )
    assert old in content, "mark_activity_done not found"
    content = content.replace(old, new)

    assert "obtenir_contexte_db" not in content, "Still has obtenir_contexte_db in weekend/utils!"
    fp.write_text(content, encoding="utf-8")
    print("  OK weekend/utils.py")


def refactor_weekend_components():
    """Refactor weekend/components.py"""
    fp = ROOT / "src" / "modules" / "famille" / "weekend" / "components.py"
    content = fp.read_text(encoding="utf-8")

    # Replace import - remove obtenir_contexte_db
    content = content.replace(
        "    obtenir_contexte_db,\n    st,\n",
        "    st,\n",
    )

    # Add service import after the .utils import block
    content = content.replace(
        "from .ai_service import WeekendAIService\nfrom .utils import (",
        "from src.services.famille.weekend import obtenir_service_weekend\n\nfrom .ai_service import WeekendAIService\nfrom .utils import (",
    )

    # Replace the add_activity DB block
    old = (
        "                try:\n"
        "                    with obtenir_contexte_db() as db:\n"
        "                        activity = WeekendActivity(\n"
        "                            titre=titre,\n"
        "                            type_activite=type_activite,\n"
        "                            date_prevue=date_prevue,\n"
        '                            heure_debut=heure.strftime("%H:%M") if heure else None,\n'
        "                            duree_estimee_h=duree,\n"
        "                            lieu=lieu or None,\n"
        "                            cout_estime=cout if cout > 0 else None,\n"
        "                            meteo_requise=meteo or None,\n"
        "                            description=description or None,\n"
        "                            adapte_jules=adapte_jules,\n"
        '                            statut="planifie",\n'
        '                            participants=["Anne", "Mathieu", "Jules"],\n'
        "                        )\n"
        "                        db.add(activity)\n"
        "                        db.commit()\n"
        '                        st.success(f"\u2705 {titre} ajoute!")\n'
        "                        st.session_state.pop(SK.WEEKEND_ADD_DATE, None)\n"
        "                        st.rerun()\n"
        "                except Exception as e:\n"
        '                    st.error(f"Erreur: {e}")'
    )
    new = (
        "                try:\n"
        "                    obtenir_service_weekend().ajouter_activite(\n"
        "                        titre=titre,\n"
        "                        type_activite=type_activite,\n"
        "                        date_prevue=date_prevue,\n"
        '                        heure=heure.strftime("%H:%M") if heure else None,\n'
        "                        duree=duree,\n"
        "                        lieu=lieu or None,\n"
        "                        cout_estime=cout if cout > 0 else None,\n"
        "                        meteo_requise=meteo or None,\n"
        "                        description=description or None,\n"
        "                        adapte_jules=adapte_jules,\n"
        "                    )\n"
        '                    st.success(f"\u2705 {titre} ajoute!")\n'
        "                    st.session_state.pop(SK.WEEKEND_ADD_DATE, None)\n"
        "                    st.rerun()\n"
        "                except Exception as e:\n"
        '                    st.error(f"Erreur: {e}")'
    )
    assert old in content, "add_activity block not found in weekend components"
    content = content.replace(old, new)

    # Replace the noter_sortie DB block
    old_noter = (
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
        "            # Activites terminees non notees\n"
        "            activities = (\n"
        "                db.query(WeekendActivity)\n"
        '                .filter(WeekendActivity.statut == "termine", WeekendActivity.note_lieu.is_(None))\n'
        "                .all()\n"
        "            )\n"
        "\n"
        "            if not activities:\n"
        '                etat_vide("Aucune sortie \u00e0 noter", "\u2b50", "Les sorties termin\u00e9es appara\u00eetront ici")\n'
        "                return\n"
        "\n"
        "            for act in activities:\n"
        '                type_info = TYPES_ACTIVITES.get(act.type_activite, TYPES_ACTIVITES["autre"])\n'
        "\n"
        "                with st.container(border=True):\n"
        "                    st.markdown(f\"**{type_info['emoji']} {act.titre}**\")\n"
        "                    st.caption(f\"\U0001f4c5 {act.date_prevue.strftime('%d/%m/%Y')}\")\n"
        "\n"
        "                    col1, col2 = st.columns(2)\n"
        "\n"
        "                    with col1:\n"
        '                        note = st.slider("Note", 1, 5, 3, key=f"note_{act.id}")\n'
        '                        a_refaire = st.checkbox("\u00c0 refaire ?", key=f"refaire_{act.id}")\n'
        "\n"
        "                    with col2:\n"
        "                        cout_reel = st.number_input(\n"
        '                            "Co\u00fbt reel (\u20ac)", min_value=0.0, key=f"cout_{act.id}"\n'
        "                        )\n"
        '                        commentaire = st.text_input("Commentaire", key=f"comm_{act.id}")\n'
        "\n"
        '                    if st.button("\U0001f4be Sauvegarder", key=f"save_{act.id}"):\n'
        "                        act.note_lieu = note\n"
        "                        act.a_refaire = a_refaire\n"
        "                        act.cout_reel = cout_reel if cout_reel > 0 else None\n"
        "                        act.commentaire = commentaire or None\n"
        "                        db.commit()\n"
        '                        st.success("\u2705 Note!")\n'
        "                        st.rerun()\n"
        "\n"
        "    except Exception as e:\n"
        '        st.error(f"Erreur: {e}")'
    )
    new_noter = (
        "    try:\n"
        "        service = obtenir_service_weekend()\n"
        "        activities = service.get_activites_non_notees()\n"
        "\n"
        "        if not activities:\n"
        '            etat_vide("Aucune sortie \u00e0 noter", "\u2b50", "Les sorties termin\u00e9es appara\u00eetront ici")\n'
        "            return\n"
        "\n"
        "        for act in activities:\n"
        '            type_info = TYPES_ACTIVITES.get(act.type_activite, TYPES_ACTIVITES["autre"])\n'
        "\n"
        "            with st.container(border=True):\n"
        "                st.markdown(f\"**{type_info['emoji']} {act.titre}**\")\n"
        "                st.caption(f\"\U0001f4c5 {act.date_prevue.strftime('%d/%m/%Y')}\")\n"
        "\n"
        "                col1, col2 = st.columns(2)\n"
        "\n"
        "                with col1:\n"
        '                    note = st.slider("Note", 1, 5, 3, key=f"note_{act.id}")\n'
        '                    a_refaire = st.checkbox("\u00c0 refaire ?", key=f"refaire_{act.id}")\n'
        "\n"
        "                with col2:\n"
        "                    cout_reel = st.number_input(\n"
        '                        "Co\u00fbt reel (\u20ac)", min_value=0.0, key=f"cout_{act.id}"\n'
        "                    )\n"
        '                    commentaire = st.text_input("Commentaire", key=f"comm_{act.id}")\n'
        "\n"
        '                if st.button("\U0001f4be Sauvegarder", key=f"save_{act.id}"):\n'
        "                    service.noter_sortie(\n"
        "                        activity_id=act.id,\n"
        "                        note=note,\n"
        "                        a_refaire=a_refaire,\n"
        "                        cout_reel=cout_reel if cout_reel > 0 else None,\n"
        "                        commentaire=commentaire or None,\n"
        "                    )\n"
        '                    st.success("\u2705 Note!")\n'
        "                    st.rerun()\n"
        "\n"
        "    except Exception as e:\n"
        '        st.error(f"Erreur: {e}")'
    )
    assert old_noter in content, "noter_sortie block not found in weekend components"
    content = content.replace(old_noter, new_noter)

    assert (
        "obtenir_contexte_db" not in content
    ), "Still has obtenir_contexte_db in weekend/components!"
    fp.write_text(content, encoding="utf-8")
    print("  OK weekend/components.py")


def refactor_suivi_perso_utils():
    """Refactor suivi_perso/utils.py"""
    fp = ROOT / "src" / "modules" / "famille" / "suivi_perso" / "utils.py"
    content = fp.read_text(encoding="utf-8")

    # Replace import
    content = content.replace(
        "from src.core.db import obtenir_contexte_db\n",
        "from src.services.famille.suivi_perso import obtenir_service_suivi_perso\n",
    )

    # Remove obtenir_contexte_db from __all__
    content = content.replace(
        '    "obtenir_contexte_db",\n',
        "",
    )

    # Replace get_user_data
    old = (
        "def get_user_data(username: str) -> dict:\n"
        '    """R\u00e9cup\u00e8re les donn\u00e9es compl\u00e8tes de l\'utilisateur"""\n'
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
    )
    # Find the full function up to the next def
    idx = content.index(old)
    # Find where the function ends (next def or end of file)
    next_def = content.index("\ndef get_food_logs_today", idx)
    old_func = content[idx:next_def]

    new_func = (
        "def get_user_data(username: str) -> dict:\n"
        '    """R\u00e9cup\u00e8re les donn\u00e9es compl\u00e8tes de l\'utilisateur"""\n'
        "    try:\n"
        "        return obtenir_service_suivi_perso().get_user_data(username)\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignorée: {e}")\n'
        "        return {}\n"
    )
    content = content.replace(old_func, new_func)

    # Replace get_food_logs_today
    old = (
        "def get_food_logs_today(username: str) -> list:\n"
        '    """R\u00e9cup\u00e8re les logs alimentation du jour"""\n'
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
    )
    idx = content.index(old)
    # This is the last function in the file, so find the end
    # Find the end by looking for the end of the try/except block
    lines = content[idx:].split("\n")
    func_lines = []
    in_func = True
    for i, line in enumerate(lines):
        if i > 0 and line and not line.startswith(" ") and not line.startswith("\n"):
            break
        func_lines.append(line)
    # Remove trailing empty lines
    while func_lines and func_lines[-1].strip() == "":
        func_lines.pop()
    old_func = "\n".join(func_lines)

    new_func = (
        "def get_food_logs_today(username: str) -> list:\n"
        '    """R\u00e9cup\u00e8re les logs alimentation du jour"""\n'
        "    try:\n"
        "        return obtenir_service_suivi_perso().get_food_logs_today(username)\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignorée: {e}")\n'
        "        return []"
    )
    content = content.replace(old_func, new_func)

    assert (
        "obtenir_contexte_db" not in content
    ), "Still has obtenir_contexte_db in suivi_perso/utils!"
    fp.write_text(content, encoding="utf-8")
    print("  OK suivi_perso/utils.py")


def refactor_suivi_perso_settings():
    """Refactor suivi_perso/settings.py"""
    fp = ROOT / "src" / "modules" / "famille" / "suivi_perso" / "settings.py"
    content = fp.read_text(encoding="utf-8")

    # Replace the save objectives DB block
    old = (
        '    if st.button("\U0001f4be Sauvegarder objectifs"):\n'
        "        try:\n"
        "            with obtenir_contexte_db() as db:\n"
        "                u = db.query(UserProfile).filter_by(id=user.id).first()\n"
        "                u.objectif_pas_quotidien = new_pas\n"
        "                u.objectif_calories_brulees = new_cal\n"
        "                u.objectif_minutes_actives = new_min\n"
        "                db.commit()\n"
        '                st.success("\u2705 Objectifs mis \u00e0 jour!")\n'
        "                st.rerun()\n"
        "        except Exception as e:\n"
        '            st.error(f"Erreur: {e}")'
    )
    new = (
        '    if st.button("\U0001f4be Sauvegarder objectifs"):\n'
        "        try:\n"
        "            from src.services.famille.suivi_perso import obtenir_service_suivi_perso\n"
        "            obtenir_service_suivi_perso().sauvegarder_objectifs(\n"
        "                user_id=user.id,\n"
        "                objectif_pas=new_pas,\n"
        "                objectif_calories=new_cal,\n"
        "                objectif_minutes=new_min,\n"
        "            )\n"
        '            st.success("\u2705 Objectifs mis \u00e0 jour!")\n'
        "            st.rerun()\n"
        "        except Exception as e:\n"
        '            st.error(f"Erreur: {e}")'
    )
    assert old in content, "Settings objectives block not found"
    content = content.replace(old, new)

    # Remove the obtenir_contexte_db import from .utils
    # Check what's in the import from .utils
    if "obtenir_contexte_db" in content:
        content = content.replace("    obtenir_contexte_db,\n", "")
    # Also remove UserProfile import if it exists and is only used for the DB block
    if "    UserProfile,\n" in content and content.count("UserProfile") <= 2:
        content = content.replace("    UserProfile,\n", "")

    assert "obtenir_contexte_db" not in content, "Still has obtenir_contexte_db in settings!"
    fp.write_text(content, encoding="utf-8")
    print("  OK suivi_perso/settings.py")


def refactor_suivi_perso_alimentation():
    """Refactor suivi_perso/alimentation.py"""
    fp = ROOT / "src" / "modules" / "famille" / "suivi_perso" / "alimentation.py"
    content = fp.read_text(encoding="utf-8")

    # Replace the food_form DB block
    old = (
        "                try:\n"
        "                    with obtenir_contexte_db() as db:\n"
        "                        user = db.query(UserProfile).filter_by(username=username).first()\n"
        "                        if not user:\n"
        "                            user = get_or_create_user(\n"
        '                                username, "Anne" if username == "anne" else "Mathieu", db=db\n'
        "                            )\n"
        "\n"
        "                        log = FoodLog(\n"
        "                            user_id=user.id,\n"
        "                            date=date.today(),\n"
        "                            heure=datetime.now(),\n"
        "                            repas=repas[0],\n"
        "                            description=description,\n"
        "                            calories_estimees=calories if calories > 0 else None,\n"
        "                            qualite=qualite,\n"
        "                            notes=notes or None,\n"
        "                        )\n"
        "                        db.add(log)\n"
        "                        db.commit()\n"
        '                        st.success("\u2705 Repas enregistre!")\n'
        "                        st.rerun()\n"
        "                except Exception as e:\n"
        '                    st.error(f"Erreur: {e}")'
    )
    new = (
        "                try:\n"
        "                    from src.services.famille.suivi_perso import obtenir_service_suivi_perso\n"
        "                    obtenir_service_suivi_perso().ajouter_food_log(\n"
        "                        username=username,\n"
        "                        repas=repas[0],\n"
        "                        description=description,\n"
        "                        calories=calories if calories > 0 else None,\n"
        "                        qualite=qualite,\n"
        "                        notes=notes or None,\n"
        "                    )\n"
        '                    st.success("\u2705 Repas enregistre!")\n'
        "                    st.rerun()\n"
        "                except Exception as e:\n"
        '                    st.error(f"Erreur: {e}")'
    )
    assert old in content, "Food form block not found in alimentation"
    content = content.replace(old, new)

    # Remove obtenir_contexte_db import
    if "obtenir_contexte_db" in content:
        content = content.replace("    obtenir_contexte_db,\n", "")
    # Remove unused imports
    for imp in ["    FoodLog,\n", "    UserProfile,\n"]:
        if imp in content:
            # Count occurrences of the class name (excluding the import line)
            class_name = imp.strip().rstrip(",")
            if content.count(class_name) <= 1:
                content = content.replace(imp, "")

    # Remove get_or_create_user import if unused
    if "get_or_create_user" in content:
        # Count uses
        if content.count("get_or_create_user") <= 1:
            content = content.replace("    get_or_create_user,\n", "")

    # Remove datetime import if unused
    if content.count("datetime") <= 1:
        content = content.replace("    datetime,\n", "")

    assert "obtenir_contexte_db" not in content, "Still has obtenir_contexte_db in alimentation!"
    fp.write_text(content, encoding="utf-8")
    print("  OK suivi_perso/alimentation.py")


def refactor_jules_utils():
    """Refactor jules/utils.py"""
    fp = ROOT / "src" / "modules" / "famille" / "jules" / "utils.py"
    content = fp.read_text(encoding="utf-8")

    # Replace import
    content = content.replace(
        "from src.core.db import obtenir_contexte_db\n",
        "from src.services.famille.achats import obtenir_service_achats_famille\n",
    )

    # Remove obtenir_contexte_db from __all__
    content = content.replace(
        '    "obtenir_contexte_db",\n',
        "",
    )

    # Replace get_achats_jules_en_attente
    old = (
        "def get_achats_jules_en_attente() -> list:\n"
        '    """Recup\u00e8re les achats Jules en attente"""\n'
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
        "            return (\n"
        "                db.query(FamilyPurchase)\n"
        "                .filter(\n"
        "                    FamilyPurchase.achete == False,\n"
        "                    FamilyPurchase.categorie.in_(\n"
        '                        ["jules_vetements", "jules_jouets", "jules_equipement"]\n'
        "                    ),\n"
        "                )\n"
        "                .order_by(FamilyPurchase.priorite)\n"
        "                .all()\n"
        "            )\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        "        return []"
    )
    new = (
        "def get_achats_jules_en_attente() -> list:\n"
        '    """Recup\u00e8re les achats Jules en attente"""\n'
        "    try:\n"
        '        categories = ["jules_vetements", "jules_jouets", "jules_equipement"]\n'
        "        return obtenir_service_achats_famille().lister_par_groupe(categories, achete=False)\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        "        return []"
    )
    assert old in content, "get_achats_jules_en_attente not found"
    content = content.replace(old, new)

    assert "obtenir_contexte_db" not in content, "Still has obtenir_contexte_db in jules/utils!"
    fp.write_text(content, encoding="utf-8")
    print("  OK jules/utils.py")


def refactor_jules_components():
    """Refactor jules/components.py"""
    fp = ROOT / "src" / "modules" / "famille" / "jules" / "components.py"
    content = fp.read_text(encoding="utf-8")

    # Replace imports - remove obtenir_contexte_db
    content = content.replace(
        "    obtenir_contexte_db,\n    st,\n",
        "    st,\n",
    )

    # Add service import
    content = content.replace(
        "from .ai_service import JulesAIService\nfrom .utils import (",
        "from src.services.famille.achats import obtenir_service_achats_famille\n\nfrom .ai_service import JulesAIService\nfrom .utils import (",
    )

    # Replace afficher_achats_categorie
    old = (
        "def afficher_achats_categorie(categorie: str):\n"
        '    """Affiche les achats d\'une categorie"""\n'
        "    try:\n"
        "        with obtenir_contexte_db() as db:\n"
        "            achats = (\n"
        "                db.query(FamilyPurchase)\n"
        "                .filter(FamilyPurchase.categorie == categorie, FamilyPurchase.achete == False)\n"
        "                .order_by(FamilyPurchase.priorite)\n"
        "                .all()\n"
        "            )\n"
        "\n"
        "            if not achats:\n"
        '                st.caption("Aucun article en attente")\n'
        "                return\n"
        "\n"
        "            for achat in achats:\n"
        "                with st.container(border=True):\n"
        "                    col1, col2, col3 = st.columns([3, 1, 1])\n"
        "\n"
        "                    with col1:\n"
        "                        prio_emoji = {\n"
        '                            "urgent": "\U0001f534",\n'
        '                            "haute": "\U0001f7e0",\n'
        '                            "moyenne": "\U0001f7e1",\n'
        '                            "basse": "\U0001f7e2",\n'
        '                        }.get(achat.priorite, "\u26aa")\n'
        '                        st.markdown(f"**{prio_emoji} {achat.nom}**")\n'
        "                        if achat.taille:\n"
        '                            st.caption(f"Taille: {achat.taille}")\n'
        "                        if achat.description:\n"
        "                            st.caption(achat.description)\n"
        "\n"
        "                    with col2:\n"
        "                        if achat.prix_estime:\n"
        '                            st.write(f"~{achat.prix_estime:.0f}\u20ac")\n'
        "\n"
        "                    with col3:\n"
        '                        if st.button("\u2705", key=f"buy_{achat.id}"):\n'
        "                            achat.achete = True\n"
        "                            achat.date_achat = date.today()\n"
        "                            db.commit()\n"
        '                            st.success("Achete!")\n'
        "                            st.rerun()\n"
        "    except Exception as e:\n"
        '        st.error(f"Erreur: {e}")'
    )

    new = (
        "def afficher_achats_categorie(categorie: str):\n"
        '    """Affiche les achats d\'une categorie"""\n'
        "    try:\n"
        "        achats = obtenir_service_achats_famille().lister_par_categorie(categorie, achete=False)\n"
        "\n"
        "        if not achats:\n"
        '            st.caption("Aucun article en attente")\n'
        "            return\n"
        "\n"
        "        for achat in achats:\n"
        "            with st.container(border=True):\n"
        "                col1, col2, col3 = st.columns([3, 1, 1])\n"
        "\n"
        "                with col1:\n"
        "                    prio_emoji = {\n"
        '                        "urgent": "\U0001f534",\n'
        '                        "haute": "\U0001f7e0",\n'
        '                        "moyenne": "\U0001f7e1",\n'
        '                        "basse": "\U0001f7e2",\n'
        '                    }.get(achat.priorite, "\u26aa")\n'
        '                    st.markdown(f"**{prio_emoji} {achat.nom}**")\n'
        "                    if achat.taille:\n"
        '                        st.caption(f"Taille: {achat.taille}")\n'
        "                    if achat.description:\n"
        "                        st.caption(achat.description)\n"
        "\n"
        "                with col2:\n"
        "                    if achat.prix_estime:\n"
        '                        st.write(f"~{achat.prix_estime:.0f}\u20ac")\n'
        "\n"
        "                with col3:\n"
        '                    if st.button("\u2705", key=f"buy_{achat.id}"):\n'
        "                        obtenir_service_achats_famille().marquer_achete(achat.id)\n"
        '                        st.success("Achete!")\n'
        "                        st.rerun()\n"
        "    except Exception as e:\n"
        '        st.error(f"Erreur: {e}")'
    )
    assert old in content, "afficher_achats_categorie not found in jules components"
    content = content.replace(old, new)

    # Replace afficher_form_ajout_achat
    old_form = (
        "                try:\n"
        "                    with obtenir_contexte_db() as db:\n"
        "                        achat = FamilyPurchase(\n"
        "                            nom=nom,\n"
        "                            categorie=categorie[0],\n"
        "                            priorite=priorite,\n"
        "                            prix_estime=prix if prix > 0 else None,\n"
        "                            taille=taille or None,\n"
        "                            url=url or None,\n"
        "                            description=description or None,\n"
        '                            suggere_par="manuel",\n'
        "                        )\n"
        "                        db.add(achat)\n"
        "                        db.commit()\n"
        '                        st.success(f"\u2705 {nom} ajoute!")\n'
        "                        st.rerun()\n"
        "                except Exception as e:\n"
        '                    st.error(f"Erreur: {e}")'
    )
    new_form = (
        "                try:\n"
        "                    obtenir_service_achats_famille().ajouter_achat(\n"
        "                        nom=nom,\n"
        "                        categorie=categorie[0],\n"
        "                        priorite=priorite,\n"
        "                        prix_estime=prix if prix > 0 else None,\n"
        "                        taille=taille or None,\n"
        "                        url=url or None,\n"
        "                        description=description or None,\n"
        '                        suggere_par="manuel",\n'
        "                    )\n"
        '                    st.success(f"\u2705 {nom} ajoute!")\n'
        "                    st.rerun()\n"
        "                except Exception as e:\n"
        '                    st.error(f"Erreur: {e}")'
    )
    assert old_form in content, "jules form block not found"
    content = content.replace(old_form, new_form)

    assert (
        "obtenir_contexte_db" not in content
    ), "Still has obtenir_contexte_db in jules/components!"
    fp.write_text(content, encoding="utf-8")
    print("  OK jules/components.py")


def refactor_jules_planning():
    """Refactor jules_planning.py - just remove unused imports"""
    fp = ROOT / "src" / "modules" / "famille" / "jules_planning.py"
    content = fp.read_text(encoding="utf-8")

    content = content.replace(
        "from src.core.db import obtenir_contexte_db\n"
        "from src.core.models import ChildProfile\n",
        "",
    )

    assert "obtenir_contexte_db" not in content, "Still has obtenir_contexte_db in jules_planning!"
    fp.write_text(content, encoding="utf-8")
    print("  OK jules_planning.py")


def refactor_age_utils():
    """Refactor age_utils.py"""
    fp = ROOT / "src" / "modules" / "famille" / "age_utils.py"
    content = fp.read_text(encoding="utf-8")

    # Replace the _obtenir_date_naissance function
    old = (
        "def _obtenir_date_naissance() -> date:\n"
        '    """Interroge la BD pour la date de naissance, fallback JULES_NAISSANCE."""\n'
        "    try:\n"
        "        from src.core.db import obtenir_contexte_db\n"
        "        from src.core.models import ChildProfile\n"
        "\n"
        "        with obtenir_contexte_db() as db:\n"
        '            jules = db.query(ChildProfile).filter_by(name="Jules", actif=True).first()\n'
        "            if jules and jules.date_of_birth:\n"
        "                return jules.date_of_birth\n"
        "    except Exception:\n"
        '        logger.debug("BD indisponible pour l\'\u00e2ge de Jules, utilisation du fallback")\n'
        "\n"
        "    return JULES_NAISSANCE"
    )
    new = (
        "def _obtenir_date_naissance() -> date:\n"
        '    """Interroge la BD pour la date de naissance, fallback JULES_NAISSANCE."""\n'
        "    try:\n"
        "        from src.services.famille.jules import obtenir_service_jules\n"
        "        result = obtenir_service_jules().get_date_naissance_jules()\n"
        "        if result:\n"
        "            return result\n"
        "    except Exception:\n"
        '        logger.debug("BD indisponible pour l\'\u00e2ge de Jules, utilisation du fallback")\n'
        "\n"
        "    return JULES_NAISSANCE"
    )
    assert old in content, "_obtenir_date_naissance not found in age_utils"
    content = content.replace(old, new)

    assert "obtenir_contexte_db" not in content, "Still has obtenir_contexte_db in age_utils!"
    fp.write_text(content, encoding="utf-8")
    print("  OK age_utils.py")


if __name__ == "__main__":
    print("Phase 8 - Refactoring obtenir_contexte_db -> services")
    print("=" * 60)

    refactor_achats_components()
    refactor_weekend_utils()
    refactor_weekend_components()
    refactor_suivi_perso_utils()
    refactor_suivi_perso_settings()
    refactor_suivi_perso_alimentation()
    refactor_jules_utils()
    refactor_jules_components()
    refactor_jules_planning()
    refactor_age_utils()

    print("=" * 60)
    print("All files refactored successfully!")
