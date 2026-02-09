"""
Module Jules - Fonctions helper
"""

from ._common import (
    date,
    get_db_context, ChildProfile, FamilyPurchase,
    ACTIVITES_PAR_AGE, TAILLES_PAR_AGE
)


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
