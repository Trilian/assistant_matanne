"""
Validators - Validation données cuisine
"""

from ..constants import DIFFICULTES, PRIORITES_COURSES, SAISONS, TYPES_REPAS, UNITES_MESURE


def validate_recipe(data: dict) -> tuple[bool, list[str]]:
    """
    Valide données recette

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Champs requis
    required = ["nom", "temps_preparation", "temps_cuisson", "portions"]
    for field in required:
        if field not in data or data[field] is None:
            errors.append(f"{field} requis")

    # Validation nom
    if "nom" in data:
        if not isinstance(data["nom"], str) or len(data["nom"]) < 3:
            errors.append("nom doit faire au moins 3 caractères")
        if len(data["nom"]) > 200:
            errors.append("nom trop long (max 200)")

    # Validation temps
    for field in ["temps_preparation", "temps_cuisson"]:
        if field in data:
            try:
                val = int(data[field])
                if val < 0 or val > 600:
                    errors.append(f"{field} doit être entre 0 et 600 min")
            except (ValueError, TypeError):
                errors.append(f"{field} doit être un nombre")

    # Validation portions
    if "portions" in data:
        try:
            val = int(data["portions"])
            if val < 1 or val > 50:
                errors.append("portions doit être entre 1 et 50")
        except (ValueError, TypeError):
            errors.append("portions doit être un nombre")

    # Validation difficulté
    if "difficulte" in data and data["difficulte"] not in DIFFICULTES:
        errors.append(f"difficulte doit être dans {DIFFICULTES}")

    # Validation saison
    if "saison" in data and data["saison"] not in SAISONS:
        errors.append(f"saison doit être dans {SAISONS}")

    # Validation type repas
    if "type_repas" in data and data["type_repas"] not in TYPES_REPAS:
        errors.append(f"type_repas doit être dans {TYPES_REPAS}")

    return len(errors) == 0, errors


def validate_ingredient(data: dict) -> tuple[bool, list[str]]:
    """
    Valide données ingrédient

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Champs requis
    if "nom" not in data or not data["nom"]:
        errors.append("nom requis")
    else:
        if len(data["nom"]) < 2:
            errors.append("nom doit faire au moins 2 caractères")
        if len(data["nom"]) > 100:
            errors.append("nom trop long (max 100)")

    # Validation unité
    if "unite" not in data or not data["unite"]:
        errors.append("unite requise")
    elif data["unite"] not in UNITES_MESURE:
        errors.append(f"unite doit être dans {UNITES_MESURE}")

    return len(errors) == 0, errors


def validate_inventory_item(data: dict) -> tuple[bool, list[str]]:
    """
    Valide article inventaire

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Champs requis
    required = ["ingredient_id", "quantite"]
    for field in required:
        if field not in data or data[field] is None:
            errors.append(f"{field} requis")

    # Validation quantité
    if "quantite" in data:
        try:
            val = float(data["quantite"])
            if val < 0:
                errors.append("quantite doit être >= 0")
        except (ValueError, TypeError):
            errors.append("quantite doit être un nombre")

    # Validation seuil
    if "quantite_min" in data:
        try:
            val = float(data["quantite_min"])
            if val < 0:
                errors.append("quantite_min doit être >= 0")
        except (ValueError, TypeError):
            errors.append("quantite_min doit être un nombre")

    return len(errors) == 0, errors


def validate_shopping_item(data: dict) -> tuple[bool, list[str]]:
    """
    Valide article courses

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Champs requis
    required = ["ingredient_id", "quantite_necessaire"]
    for field in required:
        if field not in data or data[field] is None:
            errors.append(f"{field} requis")

    # Validation quantité
    if "quantite_necessaire" in data:
        try:
            val = float(data["quantite_necessaire"])
            if val <= 0:
                errors.append("quantite_necessaire doit être > 0")
        except (ValueError, TypeError):
            errors.append("quantite_necessaire doit être un nombre")

    # Validation priorité
    if "priorite" in data and data["priorite"] not in PRIORITES_COURSES:
        errors.append(f"priorite doit être dans {PRIORITES_COURSES}")

    return len(errors) == 0, errors


def validate_meal(data: dict) -> tuple[bool, list[str]]:
    """
    Valide données repas

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Champs requis
    required = ["planning_id", "jour_semaine", "date", "type_repas"]
    for field in required:
        if field not in data or data[field] is None:
            errors.append(f"{field} requis")

    # Validation jour_semaine
    if "jour_semaine" in data:
        try:
            val = int(data["jour_semaine"])
            if not (0 <= val <= 6):
                errors.append("jour_semaine doit être entre 0 et 6")
        except (ValueError, TypeError):
            errors.append("jour_semaine doit être un nombre")

    # Validation type repas
    if "type_repas" in data and data["type_repas"] not in TYPES_REPAS:
        errors.append(f"type_repas doit être dans {TYPES_REPAS}")

    # Validation portions
    if "portions" in data:
        try:
            val = int(data["portions"])
            if val < 1 or val > 50:
                errors.append("portions doit être entre 1 et 50")
        except (ValueError, TypeError):
            errors.append("portions doit être un nombre")

    return len(errors) == 0, errors
