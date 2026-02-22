"""Fix settings.py and alimentation.py DB blocks."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def fix_settings():
    fp = ROOT / "src" / "modules" / "famille" / "suivi_perso" / "settings.py"
    content = fp.read_text(encoding="utf-8")

    old = """    if st.button("\U0001f4be Sauvegarder objectifs"):
        try:
            with obtenir_contexte_db() as db:
                u = db.query(UserProfile).filter_by(id=user.id).first()
                u.objectif_pas_quotidien = new_pas
                u.objectif_calories_brulees = new_cal
                u.objectif_minutes_actives = new_min
                db.commit()
                st.success("\u2705 Objectifs mis \u00e0 jour!")
                st.rerun()
        except Exception as e:
            st.error(f"Erreur: {e}")"""

    new = """    if st.button("\U0001f4be Sauvegarder objectifs"):
        try:
            from src.services.famille.suivi_perso import obtenir_service_suivi_perso
            obtenir_service_suivi_perso().sauvegarder_objectifs(
                user_id=user.id,
                objectif_pas=new_pas,
                objectif_calories=new_cal,
                objectif_minutes=new_min,
            )
            st.success("\u2705 Objectifs mis \u00e0 jour!")
            st.rerun()
        except Exception as e:
            st.error(f"Erreur: {e}")"""

    assert old in content, "Settings save block not found"
    content = content.replace(old, new)

    assert "obtenir_contexte_db" not in content
    fp.write_text(content, encoding="utf-8")
    print("  OK settings.py")


def fix_alimentation():
    fp = ROOT / "src" / "modules" / "famille" / "suivi_perso" / "alimentation.py"
    content = fp.read_text(encoding="utf-8")

    old = """                try:
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
                        db.commit()
                        st.success("\u2705 Repas enregistre!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")"""

    new = """                try:
                    from src.services.famille.suivi_perso import obtenir_service_suivi_perso
                    obtenir_service_suivi_perso().ajouter_food_log(
                        username=username,
                        repas=repas[0],
                        description=description,
                        calories=calories if calories > 0 else None,
                        qualite=qualite,
                        notes=notes or None,
                    )
                    st.success("\u2705 Repas enregistre!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")"""

    assert old in content, "Alimentation food form block not found"
    content = content.replace(old, new)

    # Clean imports
    if "    obtenir_contexte_db,\n" in content:
        content = content.replace("    obtenir_contexte_db,\n", "")
    # Check for unused FoodLog, UserProfile, get_or_create_user, datetime
    for name in ["FoodLog", "UserProfile", "get_or_create_user", "datetime"]:
        imp_line = f"    {name},\n"
        if imp_line in content:
            temp = content.replace(imp_line, "", 1)
            if name not in temp:
                content = temp

    assert "obtenir_contexte_db" not in content
    fp.write_text(content, encoding="utf-8")
    print("  OK alimentation.py")


def fix_jules_utils():
    fp = ROOT / "src" / "modules" / "famille" / "jules" / "utils.py"
    content = fp.read_text(encoding="utf-8")

    # Replace import
    content = content.replace(
        "from src.core.db import obtenir_contexte_db\n",
        "from src.services.famille.achats import obtenir_service_achats_famille\n",
    )

    # Remove from __all__
    content = content.replace('    "obtenir_contexte_db",\n', "")

    # Replace get_achats_jules_en_attente
    old = '''def get_achats_jules_en_attente() -> list:
    """Recup\u00e8re les achats Jules en attente"""
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
    """Recup\u00e8re les achats Jules en attente"""
    try:
        categories = ["jules_vetements", "jules_jouets", "jules_equipement"]
        return obtenir_service_achats_famille().lister_par_groupe(categories, achete=False)
    except Exception as e:
        logger.debug(f"Erreur ignor\u00e9e: {e}")
        return []'''

    assert old in content, "jules get_achats not found"
    content = content.replace(old, new)

    assert "obtenir_contexte_db" not in content
    fp.write_text(content, encoding="utf-8")
    print("  OK jules/utils.py")


def fix_jules_components():
    fp = ROOT / "src" / "modules" / "famille" / "jules" / "components.py"
    content = fp.read_text(encoding="utf-8")

    # Replace imports
    content = content.replace(
        "    obtenir_contexte_db,\n    st,\n",
        "    st,\n",
    )
    content = content.replace(
        "from .ai_service import JulesAIService\nfrom .utils import (",
        "from src.services.famille.achats import obtenir_service_achats_famille\n\nfrom .ai_service import JulesAIService\nfrom .utils import (",
    )

    # Replace afficher_achats_categorie - the with block
    old_db_block = """    try:
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
        st.error(f"Erreur: {e}")"""

    new_db_block = """    try:
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
        st.error(f"Erreur: {e}")"""

    assert old_db_block in content, "jules achats_categorie block not found"
    content = content.replace(old_db_block, new_db_block)

    # Replace form
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
                        db.commit()
                        st.success(f"\u2705 {nom} ajoute!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")"""

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
                    )
                    st.success(f"\u2705 {nom} ajoute!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")"""

    assert old_form in content, "jules form block not found"
    content = content.replace(old_form, new_form)

    assert "obtenir_contexte_db" not in content
    fp.write_text(content, encoding="utf-8")
    print("  OK jules/components.py")


def fix_jules_planning():
    fp = ROOT / "src" / "modules" / "famille" / "jules_planning.py"
    content = fp.read_text(encoding="utf-8")

    content = content.replace(
        "from src.core.db import obtenir_contexte_db\nfrom src.core.models import ChildProfile\n",
        "",
    )

    assert "obtenir_contexte_db" not in content
    fp.write_text(content, encoding="utf-8")
    print("  OK jules_planning.py")


def fix_age_utils():
    fp = ROOT / "src" / "modules" / "famille" / "age_utils.py"
    content = fp.read_text(encoding="utf-8")

    old = '''def _obtenir_date_naissance() -> date:
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

    new = '''def _obtenir_date_naissance() -> date:
    """Interroge la BD pour la date de naissance, fallback JULES_NAISSANCE."""
    try:
        from src.services.famille.jules import obtenir_service_jules
        result = obtenir_service_jules().get_date_naissance_jules()
        if result:
            return result
    except Exception:
        logger.debug("BD indisponible pour l'\u00e2ge de Jules, utilisation du fallback")

    return JULES_NAISSANCE'''

    assert old in content, "age_utils _obtenir_date_naissance not found"
    content = content.replace(old, new)

    assert "obtenir_contexte_db" not in content
    fp.write_text(content, encoding="utf-8")
    print("  OK age_utils.py")


if __name__ == "__main__":
    print("Phase 8 - Fixing remaining files")
    print("=" * 50)
    fix_settings()
    fix_alimentation()
    fix_jules_utils()
    fix_jules_components()
    fix_jules_planning()
    fix_age_utils()
    print("=" * 50)
    print("Done!")
