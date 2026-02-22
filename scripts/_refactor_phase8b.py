"""Phase 8 refactoring script - Part 2: weekend/components + suivi_perso + jules + age_utils."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def refactor_weekend_components():
    """Refactor weekend/components.py - replace DB blocks with service calls."""
    fp = ROOT / "src" / "modules" / "famille" / "weekend" / "components.py"
    content = fp.read_text(encoding="utf-8")

    # Find and replace the add_activity DB block
    # Match the actual file content exactly
    old_add = """                try:
                    with obtenir_contexte_db() as db:
                        activity = WeekendActivity(
                            titre=titre,
                            type_activite=type_activite,
                            date_prevue=date_prevue,
                            heure_debut=heure.strftime("%H:%M") if heure else None,
                            duree_estimee_h=duree,
                            lieu=lieu or None,
                            cout_estime=cout if cout > 0 else None,
                            meteo_requise=meteo or None,
                            description=description or None,
                            adapte_jules=adapte_jules,
                            statut="planifie",
                            participants=["Anne", "Mathieu", "Jules"],
                        )
                        db.add(activity)
                        db.commit()"""

    new_add = """                try:
                    obtenir_service_weekend().ajouter_activite(
                        titre=titre,
                        type_activite=type_activite,
                        date_prevue=date_prevue,
                        heure=heure.strftime("%H:%M") if heure else None,
                        duree=duree,
                        lieu=lieu or None,
                        cout_estime=cout if cout > 0 else None,
                        meteo_requise=meteo or None,
                        description=description or None,
                        adapte_jules=adapte_jules,
                    )"""

    assert old_add in content, "add_activity block not found in weekend components"
    content = content.replace(old_add, new_add)

    # Replace the noter_sortie DB block
    old_noter = """    try:
        with obtenir_contexte_db() as db:
            # Activites terminees non notees
            activities = (
                db.query(WeekendActivity)
                .filter(WeekendActivity.statut == "termine", WeekendActivity.note_lieu.is_(None))
                .all()
            )

            if not activities:"""

    new_noter = """    try:
        service = obtenir_service_weekend()
        activities = service.get_activites_non_notees()

        if not activities:"""

    assert old_noter in content, "noter_sortie first block not found"
    content = content.replace(old_noter, new_noter)

    # Replace the save button block inside noter_sortie
    old_save = """                    if st.button("\U0001f4be Sauvegarder", key=f"save_{act.id}"):
                        act.note_lieu = note
                        act.a_refaire = a_refaire
                        act.cout_reel = cout_reel if cout_reel > 0 else None
                        act.commentaire = commentaire or None
                        db.commit()"""

    new_save = """                    if st.button("\U0001f4be Sauvegarder", key=f"save_{act.id}"):
                        service.noter_sortie(
                            activity_id=act.id,
                            note=note,
                            a_refaire=a_refaire,
                            cout_reel=cout_reel if cout_reel > 0 else None,
                            commentaire=commentaire or None,
                        )"""

    assert old_save in content, "noter_sortie save block not found"
    content = content.replace(old_save, new_save)

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

    # Find get_user_data function start and end
    marker_start = "def get_user_data(username: str) -> dict:"
    marker_end = "\n\ndef get_food_logs_today"

    idx_start = content.index(marker_start)
    idx_end = content.index(marker_end, idx_start)
    old_func = content[idx_start:idx_end]

    new_func = (
        "def get_user_data(username: str) -> dict:\n"
        '    """R\u00e9cup\u00e8re les donn\u00e9es compl\u00e8tes de l\'utilisateur"""\n'
        "    try:\n"
        "        return obtenir_service_suivi_perso().get_user_data(username)\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        "        return {}"
    )
    content = content.replace(old_func, new_func)

    # Find and replace get_food_logs_today
    marker_start2 = "def get_food_logs_today(username: str) -> list:"
    idx_start2 = content.index(marker_start2)
    # This function goes to the end of file
    old_func2 = content[idx_start2:].rstrip()

    new_func2 = (
        "def get_food_logs_today(username: str) -> list:\n"
        '    """R\u00e9cup\u00e8re les logs alimentation du jour"""\n'
        "    try:\n"
        "        return obtenir_service_suivi_perso().get_food_logs_today(username)\n"
        "    except Exception as e:\n"
        '        logger.debug(f"Erreur ignor\u00e9e: {e}")\n'
        "        return []"
    )
    content = content[:idx_start2] + new_func2 + "\n"

    assert (
        "obtenir_contexte_db" not in content
    ), "Still has obtenir_contexte_db in suivi_perso/utils!"
    fp.write_text(content, encoding="utf-8")
    print("  OK suivi_perso/utils.py")


def refactor_suivi_perso_settings():
    """Refactor suivi_perso/settings.py"""
    fp = ROOT / "src" / "modules" / "famille" / "suivi_perso" / "settings.py"
    content = fp.read_text(encoding="utf-8")

    # Find the save objectives block
    old_save = """    if st.button("\U0001f4be Sauvegarder objectifs"):
        try:
            with obtenir_contexte_db() as db:
                u = db.query(UserProfile).filter_by(id=user.id).first()
                u.objectif_pas_quotidien = new_pas
                u.objectif_calories_brulees = new_cal
                u.objectif_minutes_actives = new_min
                db.commit()"""

    new_save = """    if st.button("\U0001f4be Sauvegarder objectifs"):
        try:
            from src.services.famille.suivi_perso import obtenir_service_suivi_perso
            obtenir_service_suivi_perso().sauvegarder_objectifs(
                user_id=user.id,
                objectif_pas=new_pas,
                objectif_calories=new_cal,
                objectif_minutes=new_min,
            )"""

    assert old_save in content, "Settings objectives block not found"
    content = content.replace(old_save, new_save)

    # Remove obtenir_contexte_db from imports
    if "    obtenir_contexte_db,\n" in content:
        content = content.replace("    obtenir_contexte_db,\n", "")
    if "    UserProfile,\n" in content:
        # Check if UserProfile is still used elsewhere
        remaining = content.replace("    UserProfile,\n", "", 1)
        if "UserProfile" not in remaining:
            content = remaining

    assert "obtenir_contexte_db" not in content, "Still has obtenir_contexte_db in settings!"
    fp.write_text(content, encoding="utf-8")
    print("  OK suivi_perso/settings.py")


def refactor_suivi_perso_alimentation():
    """Refactor suivi_perso/alimentation.py"""
    fp = ROOT / "src" / "modules" / "famille" / "suivi_perso" / "alimentation.py"
    content = fp.read_text(encoding="utf-8")

    # Replace the food_form DB block
    old_form = """                try:
                    with obtenir_contexte_db() as db:
                        user = db.query(UserProfile).filter_by(username=username).first()
                        if not user:
                            user = get_or_create_user(
                                username, "Anne" if username == "anne" else "Mathieu", db=db
                            )

                        log = FoodLog(
                            user_id=user.id,
                            date=date.today(),
                            heure=datetime.now(),
                            repas=repas[0],
                            description=description,
                            calories_estimees=calories if calories > 0 else None,
                            qualite=qualite,
                            notes=notes or None,
                        )
                        db.add(log)
                        db.commit()"""

    new_form = """                try:
                    from src.services.famille.suivi_perso import obtenir_service_suivi_perso
                    obtenir_service_suivi_perso().ajouter_food_log(
                        username=username,
                        repas=repas[0],
                        description=description,
                        calories=calories if calories > 0 else None,
                        qualite=qualite,
                        notes=notes or None,
                    )"""

    assert old_form in content, "Food form block not found in alimentation"
    content = content.replace(old_form, new_form)

    # Remove unused imports from .utils
    if "    obtenir_contexte_db,\n" in content:
        content = content.replace("    obtenir_contexte_db,\n", "")

    # Check and remove unused model imports
    for imp_name in ["FoodLog", "UserProfile"]:
        imp_line = f"    {imp_name},\n"
        if imp_line in content:
            temp = content.replace(imp_line, "", 1)
            if imp_name not in temp:
                content = temp

    # Remove get_or_create_user if unused
    if "    get_or_create_user,\n" in content:
        temp = content.replace("    get_or_create_user,\n", "", 1)
        if "get_or_create_user" not in temp:
            content = temp

    # Remove datetime if unused
    if "    datetime,\n" in content:
        temp = content.replace("    datetime,\n", "", 1)
        if "datetime" not in temp:
            content = temp

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
    old = '''def get_achats_jules_en_attente() -> list:
    """Recupère les achats Jules en attente"""
    try:
        with obtenir_contexte_db() as db:
            return (
                db.query(FamilyPurchase)
                .filter(
                    FamilyPurchase.achete == False,
                    FamilyPurchase.categorie.in_(
                        ["jules_vetements", "jules_jouets", "jules_equipement"]
                    ),
                )
                .order_by(FamilyPurchase.priorite)
                .all()
            )
    except Exception as e:
        logger.debug(f"Erreur ignor\u00e9e: {e}")
        return []'''

    new = '''def get_achats_jules_en_attente() -> list:
    """Recupère les achats Jules en attente"""
    try:
        categories = ["jules_vetements", "jules_jouets", "jules_equipement"]
        return obtenir_service_achats_famille().lister_par_groupe(categories, achete=False)
    except Exception as e:
        logger.debug(f"Erreur ignor\u00e9e: {e}")
        return []'''

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

    # Add service import at the top
    content = content.replace(
        "from .ai_service import JulesAIService\nfrom .utils import (",
        "from src.services.famille.achats import obtenir_service_achats_famille\n\nfrom .ai_service import JulesAIService\nfrom .utils import (",
    )

    # Replace afficher_achats_categorie
    old_cat = '''def afficher_achats_categorie(categorie: str):
    """Affiche les achats d'une categorie"""
    try:
        with obtenir_contexte_db() as db:
            achats = (
                db.query(FamilyPurchase)
                .filter(FamilyPurchase.categorie == categorie, FamilyPurchase.achete == False)
                .order_by(FamilyPurchase.priorite)
                .all()
            )

            if not achats:
                st.caption("Aucun article en attente")
                return

            for achat in achats:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        prio_emoji = {
                            "urgent": "\U0001f534",
                            "haute": "\U0001f7e0",
                            "moyenne": "\U0001f7e1",
                            "basse": "\U0001f7e2",
                        }.get(achat.priorite, "\u26aa")
                        st.markdown(f"**{prio_emoji} {achat.nom}**")
                        if achat.taille:
                            st.caption(f"Taille: {achat.taille}")
                        if achat.description:
                            st.caption(achat.description)

                    with col2:
                        if achat.prix_estime:
                            st.write(f"~{achat.prix_estime:.0f}\u20ac")

                    with col3:
                        if st.button("\u2705", key=f"buy_{achat.id}"):
                            achat.achete = True
                            achat.date_achat = date.today()
                            db.commit()
                            st.success("Achete!")
                            st.rerun()
    except Exception as e:
        st.error(f"Erreur: {e}")'''

    new_cat = '''def afficher_achats_categorie(categorie: str):
    """Affiche les achats d'une categorie"""
    try:
        achats = obtenir_service_achats_famille().lister_par_categorie(categorie, achete=False)

        if not achats:
            st.caption("Aucun article en attente")
            return

        for achat in achats:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    prio_emoji = {
                        "urgent": "\U0001f534",
                        "haute": "\U0001f7e0",
                        "moyenne": "\U0001f7e1",
                        "basse": "\U0001f7e2",
                    }.get(achat.priorite, "\u26aa")
                    st.markdown(f"**{prio_emoji} {achat.nom}**")
                    if achat.taille:
                        st.caption(f"Taille: {achat.taille}")
                    if achat.description:
                        st.caption(achat.description)

                with col2:
                    if achat.prix_estime:
                        st.write(f"~{achat.prix_estime:.0f}\u20ac")

                with col3:
                    if st.button("\u2705", key=f"buy_{achat.id}"):
                        obtenir_service_achats_famille().marquer_achete(achat.id)
                        st.success("Achete!")
                        st.rerun()
    except Exception as e:
        st.error(f"Erreur: {e}")'''

    assert old_cat in content, "afficher_achats_categorie not found in jules components"
    content = content.replace(old_cat, new_cat)

    # Replace afficher_form_ajout_achat
    old_form = """                try:
                    with obtenir_contexte_db() as db:
                        achat = FamilyPurchase(
                            nom=nom,
                            categorie=categorie[0],
                            priorite=priorite,
                            prix_estime=prix if prix > 0 else None,
                            taille=taille or None,
                            url=url or None,
                            description=description or None,
                            suggere_par="manuel",
                        )
                        db.add(achat)
                        db.commit()"""

    new_form = """                try:
                    obtenir_service_achats_famille().ajouter_achat(
                        nom=nom,
                        categorie=categorie[0],
                        priorite=priorite,
                        prix_estime=prix if prix > 0 else None,
                        taille=taille or None,
                        url=url or None,
                        description=description or None,
                        suggere_par="manuel",
                    )"""

    assert old_form in content, "jules form block not found"
    content = content.replace(old_form, new_form)

    assert (
        "obtenir_contexte_db" not in content
    ), "Still has obtenir_contexte_db in jules/components!"
    fp.write_text(content, encoding="utf-8")
    print("  OK jules/components.py")


def refactor_jules_planning():
    """Refactor jules_planning.py - remove unused imports"""
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

    old_func = '''def _obtenir_date_naissance() -> date:
    """Interroge la BD pour la date de naissance, fallback JULES_NAISSANCE."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ChildProfile

        with obtenir_contexte_db() as db:
            jules = db.query(ChildProfile).filter_by(name="Jules", actif=True).first()
            if jules and jules.date_of_birth:
                return jules.date_of_birth
    except Exception:
        logger.debug("BD indisponible pour l'\u00e2ge de Jules, utilisation du fallback")

    return JULES_NAISSANCE'''

    new_func = '''def _obtenir_date_naissance() -> date:
    """Interroge la BD pour la date de naissance, fallback JULES_NAISSANCE."""
    try:
        from src.services.famille.jules import obtenir_service_jules
        result = obtenir_service_jules().get_date_naissance_jules()
        if result:
            return result
    except Exception:
        logger.debug("BD indisponible pour l'\u00e2ge de Jules, utilisation du fallback")

    return JULES_NAISSANCE'''

    assert old_func in content, "_obtenir_date_naissance not found in age_utils"
    content = content.replace(old_func, new_func)

    assert "obtenir_contexte_db" not in content, "Still has obtenir_contexte_db in age_utils!"
    fp.write_text(content, encoding="utf-8")
    print("  OK age_utils.py")


if __name__ == "__main__":
    print("Phase 8 - Part 2: remaining refactoring")
    print("=" * 60)

    refactor_weekend_components()
    refactor_suivi_perso_utils()
    refactor_suivi_perso_settings()
    refactor_suivi_perso_alimentation()
    refactor_jules_utils()
    refactor_jules_components()
    refactor_jules_planning()
    refactor_age_utils()

    print("=" * 60)
    print("All remaining files refactored!")
