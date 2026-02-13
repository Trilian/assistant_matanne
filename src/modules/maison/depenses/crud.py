"""
Module Depenses Maison - Fonctions CRUD et statistiques
"""

from .utils import (
    CATEGORIES_AVEC_CONSO,
    MOIS_FR,
    CategorieDepense,
    FactureMaison,
    HouseExpense,
    List,
    Optional,
    date,
    get_budget_service,
    obtenir_contexte_db,
)


def get_depenses_mois(mois: int, annee: int) -> List[HouseExpense]:
    """Recupère les depenses d'un mois"""
    try:
        with obtenir_contexte_db() as db:
            return (
                db.query(HouseExpense)
                .filter(HouseExpense.mois == mois, HouseExpense.annee == annee)
                .order_by(HouseExpense.categorie)
                .all()
            )
    except Exception:
        return []


def get_depenses_annee(annee: int) -> List[HouseExpense]:
    """Recupère toutes les depenses d'une annee"""
    try:
        with obtenir_contexte_db() as db:
            return (
                db.query(HouseExpense)
                .filter(HouseExpense.annee == annee)
                .order_by(HouseExpense.mois, HouseExpense.categorie)
                .all()
            )
    except Exception:
        return []


def get_depense_by_id(depense_id: int) -> Optional[HouseExpense]:
    """Recupère une depense par ID"""
    try:
        with obtenir_contexte_db() as db:
            return db.query(HouseExpense).filter(HouseExpense.id == depense_id).first()
    except Exception:
        return None


def create_depense(data: dict) -> HouseExpense:
    """Cree une nouvelle depense - utilise le service budget si categorie energie."""
    # Pour gaz/elec/eau, passer par le service budget unifie
    if data.get("categorie") in CATEGORIES_AVEC_CONSO:
        service = get_budget_service()
        facture = FactureMaison(
            categorie=CategorieDepense(data["categorie"]),
            montant=data["montant"],
            consommation=data.get("consommation"),
            unite_consommation=data.get("unite", ""),
            mois=data["mois"],
            annee=data["annee"],
            date_facture=data.get("date_facture"),
            fournisseur=data.get("fournisseur", ""),
            numero_facture=data.get("numero_facture", ""),
            note=data.get("note", ""),
        )
        service.ajouter_facture_maison(facture)

    # Toujours creer aussi dans HouseExpense pour compatibilite
    with obtenir_contexte_db() as db:
        depense = HouseExpense(**data)
        db.add(depense)
        db.commit()
        db.refresh(depense)
        return depense


def update_depense(depense_id: int, data: dict) -> Optional[HouseExpense]:
    """Met à jour une depense"""
    with obtenir_contexte_db() as db:
        depense = db.query(HouseExpense).filter(HouseExpense.id == depense_id).first()
        if depense:
            for key, value in data.items():
                setattr(depense, key, value)
            db.commit()
            db.refresh(depense)
        return depense


def delete_depense(depense_id: int) -> bool:
    """Supprime une depense"""
    with obtenir_contexte_db() as db:
        depense = db.query(HouseExpense).filter(HouseExpense.id == depense_id).first()
        if depense:
            db.delete(depense)
            db.commit()
            return True
        return False


def get_stats_globales() -> dict:
    """Calcule les statistiques globales"""
    today = date.today()

    # Ce mois
    depenses_mois = get_depenses_mois(today.month, today.year)
    total_mois = sum(float(d.montant) for d in depenses_mois)

    # Mois precedent
    if today.month == 1:
        mois_prec, annee_prec = 12, today.year - 1
    else:
        mois_prec, annee_prec = today.month - 1, today.year

    depenses_prec = get_depenses_mois(mois_prec, annee_prec)
    total_prec = sum(float(d.montant) for d in depenses_prec)

    # Delta
    delta = total_mois - total_prec if total_prec > 0 else 0
    delta_pct = (delta / total_prec * 100) if total_prec > 0 else 0

    # Moyenne mensuelle (12 derniers mois)
    depenses_annee = get_depenses_annee(today.year)
    depenses_annee_prec = get_depenses_annee(today.year - 1)
    all_depenses = depenses_annee + depenses_annee_prec

    # Grouper par mois
    par_mois = {}
    for d in all_depenses:
        key = f"{d.annee}-{d.mois:02d}"
        if key not in par_mois:
            par_mois[key] = 0
        par_mois[key] += float(d.montant)

    moyenne = sum(par_mois.values()) / len(par_mois) if par_mois else 0

    return {
        "total_mois": total_mois,
        "total_prec": total_prec,
        "delta": delta,
        "delta_pct": delta_pct,
        "moyenne_mensuelle": moyenne,
        "nb_categories": len(set(d.categorie for d in depenses_mois)),
    }


def get_historique_categorie(categorie: str, nb_mois: int = 12) -> List[dict]:
    """Recupère l'historique d'une categorie"""
    today = date.today()
    result = []

    for i in range(nb_mois):
        mois = today.month - i
        annee = today.year
        while mois <= 0:
            mois += 12
            annee -= 1

        with obtenir_contexte_db() as db:
            depense = (
                db.query(HouseExpense)
                .filter(
                    HouseExpense.categorie == categorie,
                    HouseExpense.mois == mois,
                    HouseExpense.annee == annee,
                )
                .first()
            )

        result.append(
            {
                "mois": mois,
                "annee": annee,
                "label": f"{MOIS_FR[mois][:3]} {annee}",
                "montant": float(depense.montant) if depense else 0,
                "consommation": float(depense.consommation)
                if depense and depense.consommation
                else 0,
            }
        )

    return list(reversed(result))
