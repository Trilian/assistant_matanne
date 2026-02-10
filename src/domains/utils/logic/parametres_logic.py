"""
Logique métier du module Paramètres (configuration) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from typing import Optional, Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# VALIDATION PARAMÃˆTRES
# ═══════════════════════════════════════════════════════════

def valider_parametres(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valide les paramètres de configuration.
    
    Args:
        data: Dictionnaire de paramètres
        
    Returns:
        Tuple (valide, liste_erreurs)
    """
    erreurs = []
    
    # Nom famille
    if "nom_famille" in data:
        nom = data["nom_famille"]
        if not nom or len(nom) < 2:
            erreurs.append("Le nom de famille doit contenir au moins 2 caractères")
        elif len(nom) > 50:
            erreurs.append("Le nom de famille ne peut pas dépasser 50 caractères")
    
    # Email
    if "email" in data:
        email = data["email"]
        if email and "@" not in email:
            erreurs.append("Email invalide (doit contenir @)")
        if email and "." not in email.split("@")[-1]:
            erreurs.append("Email invalide (domaine incorrect)")
    
    # Devise
    if "devise" in data:
        devise = data["devise"]
        devises_supportees = ["EUR", "USD", "GBP", "CHF", "CAD"]
        if devise not in devises_supportees:
            erreurs.append(f"Devise non supportée. Valeurs acceptées: {', '.join(devises_supportees)}")
    
    # Langue
    if "langue" in data:
        langue = data["langue"]
        langues_supportees = ["fr", "en", "es", "de"]
        if langue not in langues_supportees:
            erreurs.append(f"Langue non supportée. Valeurs acceptées: {', '.join(langues_supportees)}")
    
    # Thème
    if "theme" in data:
        theme = data["theme"]
        themes_supportes = ["light", "dark", "auto"]
        if theme not in themes_supportes:
            erreurs.append(f"Thème non supporté. Valeurs acceptées: {', '.join(themes_supportes)}")
    
    return len(erreurs) == 0, erreurs


def valider_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Valide une adresse email.
    
    Args:
        email: Email à valider
        
    Returns:
        Tuple (valide, message_erreur)
    """
    if not email:
        return False, "Email vide"
    
    if "@" not in email:
        return False, "Email doit contenir @"
    
    parties = email.split("@")
    if len(parties) != 2:
        return False, "Email invalide (trop de @)"
    
    local, domaine = parties
    
    if not local or len(local) < 1:
        return False, "Partie locale vide"
    
    if not domaine or "." not in domaine:
        return False, "Domaine invalide"
    
    if len(email) > 254:
        return False, "Email trop long (max 254 caractères)"
    
    return True, None


# ═══════════════════════════════════════════════════════════
# CONFIGURATION PAR DÉFAUT
# ═══════════════════════════════════════════════════════════

def generer_config_defaut() -> Dict[str, Any]:
    """Génère une configuration par défaut."""
    return {
        "nom_famille": "Ma Famille",
        "email": "",
        "devise": "EUR",
        "langue": "fr",
        "theme": "light",
        "notifications_actives": True,
        "notifications_email": False,
        "sync_calendrier": False,
        "format_date": "DD/MM/YYYY",
        "fuseau_horaire": "Europe/Paris",
        "afficher_tutoriels": True,
        "mode_compact": False
    }


def fusionner_config(config_actuelle: Dict[str, Any], nouveaux_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne la config actuelle avec de nouveaux paramètres.
    
    Args:
        config_actuelle: Configuration actuelle
        nouveaux_params: Nouveaux paramètres
        
    Returns:
        Configuration fusionnée
    """
    config_fusionnee = config_actuelle.copy()
    config_fusionnee.update(nouveaux_params)
    return config_fusionnee


# ═══════════════════════════════════════════════════════════
# VERSIONS
# ═══════════════════════════════════════════════════════════

def comparer_versions(version_actuelle: str, version_cible: str) -> int:
    """
    Compare deux versions.
    
    Args:
        version_actuelle: Version actuelle (ex: "1.2.3")
        version_cible: Version cible (ex: "1.3.0")
        
    Returns:
        -1 si actuelle < cible, 0 si égales, 1 si actuelle > cible
    """
    def parse_version(v: str) -> List[int]:
        return [int(x) for x in v.split(".")]
    
    try:
        v1 = parse_version(version_actuelle)
        v2 = parse_version(version_cible)
        
        # Comparer élément par élément
        for a, b in zip(v1, v2):
            if a < b:
                return -1
            elif a > b:
                return 1
        
        # Si même longueur et mêmes valeurs
        if len(v1) == len(v2):
            return 0
        
        # Si longueurs différentes
        return -1 if len(v1) < len(v2) else 1
        
    except (ValueError, AttributeError):
        return 0


def version_est_superieure(version_actuelle: str, version_minimale: str) -> bool:
    """
    Vérifie si version actuelle >= version minimale.
    
    Args:
        version_actuelle: Version actuelle
        version_minimale: Version minimale requise
        
    Returns:
        True si version actuelle >= minimale
    """
    return comparer_versions(version_actuelle, version_minimale) >= 0


def formater_version(version: str) -> str:
    """
    Formate une version pour l'affichage.
    
    Args:
        version: Version brute (ex: "1.2.3")
        
    Returns:
        Version formatée (ex: "v1.2.3")
    """
    if not version.startswith("v"):
        return f"v{version}"
    return version


# ═══════════════════════════════════════════════════════════
# PRÉFÉRENCES UTILISATEUR
# ═══════════════════════════════════════════════════════════

def get_preferences_par_categorie(preferences: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Groupe les préférences par catégorie.
    
    Args:
        preferences: Dictionnaire de préférences
        
    Returns:
        Préférences groupées par catégorie
    """
    categories = {
        "general": ["nom_famille", "langue", "fuseau_horaire"],
        "affichage": ["theme", "format_date", "mode_compact"],
        "notifications": ["notifications_actives", "notifications_email"],
        "integration": ["sync_calendrier", "api_externe"],
        "confidentialite": ["email", "partage_donnees"]
    }
    
    groupees = {}
    
    for cat, cles in categories.items():
        groupees[cat] = {}
        for cle in cles:
            if cle in preferences:
                groupees[cat][cle] = preferences[cle]
    
    return groupees


def exporter_config(config: Dict[str, Any], format: str = "json") -> str:
    """
    Exporte la configuration dans un format donné.
    
    Args:
        config: Configuration à exporter
        format: Format d'export (json, yaml, ini)
        
    Returns:
        Configuration exportée en string
    """
    if format == "json":
        import json
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    elif format == "yaml":
        # Simulation YAML simple
        lignes = []
        for cle, valeur in config.items():
            if isinstance(valeur, bool):
                valeur = str(valeur).lower()
            elif isinstance(valeur, str):
                valeur = f'"{valeur}"'
            lignes.append(f"{cle}: {valeur}")
        return "\n".join(lignes)
    
    elif format == "ini":
        # Simulation INI simple
        lignes = ["[config]"]
        for cle, valeur in config.items():
            lignes.append(f"{cle} = {valeur}")
        return "\n".join(lignes)
    
    else:
        return str(config)


# ═══════════════════════════════════════════════════════════
# SANTÉ DE L'APPLICATION
# ═══════════════════════════════════════════════════════════

def verifier_sante_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Vérifie la santé de la configuration.
    
    Args:
        config: Configuration à vérifier
        
    Returns:
        Rapport de santé
    """
    problemes = []
    avertissements = []
    
    # Vérifier paramètres obligatoires
    obligatoires = ["nom_famille", "devise", "langue"]
    for param in obligatoires:
        if param not in config or not config[param]:
            problemes.append(f"Paramètre obligatoire manquant: {param}")
    
    # Vérifier cohérence
    if config.get("notifications_email") and not config.get("email"):
        avertissements.append("Notifications email activées mais pas d'email configuré")
    
    if config.get("sync_calendrier") and not config.get("api_externe"):
        avertissements.append("Sync calendrier activée mais pas d'API configurée")
    
    # Statut global
    if problemes:
        statut = "Erreur"
    elif avertissements:
        statut = "Avertissement"
    else:
        statut = "OK"
    
    return {
        "statut": statut,
        "problemes": problemes,
        "avertissements": avertissements,
        "score": 100 - (len(problemes) * 30) - (len(avertissements) * 10)
    }


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════

def formater_parametre_affichage(cle: str, valeur: Any) -> str:
    """
    Formate un paramètre pour l'affichage.
    
    Args:
        cle: Clé du paramètre
        valeur: Valeur du paramètre
        
    Returns:
        Texte formaté
    """
    if isinstance(valeur, bool):
        return "✅ Activé" if valeur else "❌ Désactivé"
    elif cle == "devise":
        symboles = {"EUR": "€", "USD": "$", "GBP": "Â£", "CHF": "CHF"}
        return f"{valeur} ({symboles.get(valeur, '')})"
    elif cle == "langue":
        langues = {"fr": "📅Ÿ‡· Français", "en": "👶Ÿ‡§ Anglais", "es": "💡Ÿ‡¸ Espagnol", "de": "🎯Ÿ‡ª Allemand"}
        return langues.get(valeur, valeur)
    else:
        return str(valeur)
