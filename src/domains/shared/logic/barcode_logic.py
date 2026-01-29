"""
Logique mÃ©tier du module Barcode (scan codes-barres) - SÃ©parÃ©e de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from typing import Optional, Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION CODE-BARRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_code_barres(code: str) -> Tuple[bool, Optional[str]]:
    """
    Valide un code-barres.
    
    Args:
        code: Code-barres Ã  valider
        
    Returns:
        Tuple (valide, message_erreur)
    """
    if not code:
        return False, "Code-barres vide"
    
    # Nettoyer le code
    code = code.strip()
    
    if len(code) < 8:
        return False, "Code-barres trop court (minimum 8 caractÃ¨res)"
    
    if not code.isdigit():
        return False, "Code-barres doit contenir uniquement des chiffres"
    
    # VÃ©rifier longueurs standards
    longueurs_valides = [8, 12, 13, 14]
    if len(code) not in longueurs_valides:
        return False, f"Longueur invalide: {len(code)} (attendu: {', '.join(map(str, longueurs_valides))})"
    
    return True, None


def valider_checksum_ean13(code: str) -> bool:
    """
    Valide le checksum d'un code EAN-13.
    
    Args:
        code: Code EAN-13 Ã  valider
        
    Returns:
        True si le checksum est valide
    """
    if len(code) != 13:
        return False
    
    try:
        # Somme des chiffres en positions impaires (1, 3, 5, ...) Ã— 1
        somme_impaires = sum(int(code[i]) for i in range(0, 12, 2))
        
        # Somme des chiffres en positions paires (2, 4, 6, ...) Ã— 3
        somme_paires = sum(int(code[i]) * 3 for i in range(1, 12, 2))
        
        # Total
        total = somme_impaires + somme_paires
        
        # Checksum = 10 - (total % 10), ou 0 si total % 10 == 0
        checksum_calcule = (10 - (total % 10)) % 10
        checksum_code = int(code[12])
        
        return checksum_calcule == checksum_code
    except (ValueError, IndexError):
        return False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DÃ‰TECTION TYPE CODE-BARRES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def detecter_type_code_barres(code: str) -> str:
    """
    DÃ©tecte le type de code-barres.
    
    Args:
        code: Code-barres Ã  analyser
        
    Returns:
        Type de code (EAN-8, EAN-13, UPC-A, ITF-14, Inconnu)
    """
    longueur = len(code)
    
    if longueur == 8:
        return "EAN-8"
    elif longueur == 12:
        return "UPC-A"
    elif longueur == 13:
        return "EAN-13"
    elif longueur == 14:
        return "ITF-14"
    else:
        return "Inconnu"


def detecter_pays_origine(code: str) -> Optional[str]:
    """
    DÃ©tecte le pays d'origine Ã  partir d'un code EAN-13.
    
    Args:
        code: Code EAN-13
        
    Returns:
        Nom du pays ou None
    """
    if len(code) != 13:
        return None
    
    # PrÃ©fixe GS1 (3 premiers chiffres)
    prefixe = code[:3]
    
    pays_map = {
        ("300", "379"): "France",
        ("400", "440"): "Allemagne",
        ("450", "459"): "Japon",
        ("460", "469"): "Russie",
        ("470",): "Kirghizistan",
        ("471",): "TaÃ¯wan",
        ("474",): "Estonie",
        ("475",): "Lettonie",
        ("476",): "AzerbaÃ¯djan",
        ("477",): "Lituanie",
        ("478",): "OuzbÃ©kistan",
        ("479",): "Sri Lanka",
        ("480", "489"): "Philippines",
        ("490", "499"): "Japon",
        ("500", "509"): "Royaume-Uni",
        ("520", "521"): "GrÃ¨ce",
        ("528",): "Liban",
        ("529",): "Chypre",
        ("530",): "Albanie",
        ("531",): "MacÃ©doine",
        ("535",): "Malte",
        ("539",): "Irlande",
        ("540", "549"): "Belgique/Luxembourg",
        ("560",): "Portugal",
        ("569",): "Islande",
        ("570", "579"): "Danemark",
        ("590",): "Pologne",
        ("594",): "Roumanie",
        ("599",): "Hongrie",
        ("600", "601"): "Afrique du Sud",
        ("603",): "Ghana",
        ("608",): "BahreÃ¯n",
        ("609",): "Maurice",
        ("611",): "Maroc",
        ("613",): "AlgÃ©rie",
        ("615",): "Nigeria",
        ("616",): "Kenya",
        ("618",): "CÃ´te d'Ivoire",
        ("619",): "Tunisie",
        ("621",): "Syrie",
        ("622",): "Ã‰gypte",
        ("624",): "Libye",
        ("625",): "Jordanie",
        ("626",): "Iran",
        ("627",): "KoweÃ¯t",
        ("628",): "Arabie saoudite",
        ("629",): "Ã‰mirats arabes unis",
        ("640", "649"): "Finlande",
        ("690", "699"): "Chine",
        ("700", "709"): "NorvÃ¨ge",
        ("729",): "IsraÃ«l",
        ("730", "739"): "SuÃ¨de",
        ("740",): "Guatemala",
        ("741",): "Salvador",
        ("742",): "Honduras",
        ("743",): "Nicaragua",
        ("744",): "Costa Rica",
        ("745",): "Panama",
        ("746",): "RÃ©publique dominicaine",
        ("750",): "Mexique",
        ("754", "755"): "Canada",
        ("759",): "Venezuela",
        ("760", "769"): "Suisse",
        ("770", "771"): "Colombie",
        ("773",): "Uruguay",
        ("775",): "PÃ©rou",
        ("777",): "Bolivie",
        ("778", "779"): "Argentine",
        ("780",): "Chili",
        ("784",): "Paraguay",
        ("786",): "Ã‰quateur",
        ("789", "790"): "BrÃ©sil",
        ("800", "839"): "Italie",
        ("840", "849"): "Espagne",
        ("850",): "Cuba",
        ("858",): "Slovaquie",
        ("859",): "RÃ©publique tchÃ¨que",
        ("860",): "Serbie",
        ("865",): "Mongolie",
        ("867",): "CorÃ©e du Nord",
        ("868", "869"): "Turquie",
        ("870", "879"): "Pays-Bas",
        ("880",): "CorÃ©e du Sud",
        ("884",): "Cambodge",
        ("885",): "ThaÃ¯lande",
        ("888",): "Singapour",
        ("890",): "Inde",
        ("893",): "Vietnam",
        ("896",): "Pakistan",
        ("899",): "IndonÃ©sie",
        ("900", "919"): "Autriche",
        ("930", "939"): "Australie",
        ("940", "949"): "Nouvelle-ZÃ©lande",
    }
    
    try:
        prefixe_int = int(prefixe)
        
        for ranges, pays in pays_map.items():
            for r in ranges:
                if len(r) == 3 and prefixe == r:
                    return pays
                elif prefixe_int >= int(r[:3]) and (len(ranges) > 1 and prefixe_int <= int(ranges[1][:3])):
                    return pays
    except ValueError:
        pass
    
    return None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_code_barres(code: str) -> str:
    """
    Formate un code-barres pour l'affichage.
    
    Args:
        code: Code-barres Ã  formater
        
    Returns:
        Code formatÃ© avec espaces
    """
    code = code.strip()
    
    # EAN-13: XXX XXXX XXXXX X
    if len(code) == 13:
        return f"{code[:3]} {code[3:7]} {code[7:12]} {code[12]}"
    
    # UPC-A: X XXXXX XXXXX X
    elif len(code) == 12:
        return f"{code[0]} {code[1:6]} {code[6:11]} {code[11]}"
    
    # EAN-8: XXXX XXXX
    elif len(code) == 8:
        return f"{code[:4]} {code[4:]}"
    
    # ITF-14: XX XXXXXX XXXXX X
    elif len(code) == 14:
        return f"{code[:2]} {code[2:8]} {code[8:13]} {code[13]}"
    
    else:
        return code


def nettoyer_code_barres(code: str) -> str:
    """
    Nettoie un code-barres (supprime espaces, tirets).
    
    Args:
        code: Code brut
        
    Returns:
        Code nettoyÃ©
    """
    return "".join(c for c in code if c.isdigit())


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ANALYSE PRODUIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def extraire_infos_produit(code: str) -> Dict[str, Any]:
    """
    Extrait les informations d'un code-barres.
    
    Args:
        code: Code-barres
        
    Returns:
        Dictionnaire avec infos extraites
    """
    valide, erreur = valider_code_barres(code)
    
    if not valide:
        return {
            "valide": False,
            "erreur": erreur
        }
    
    type_code = detecter_type_code_barres(code)
    pays = None
    checksum_valide = None
    
    if type_code == "EAN-13":
        pays = detecter_pays_origine(code)
        checksum_valide = valider_checksum_ean13(code)
    
    return {
        "valide": True,
        "code": code,
        "code_formate": formater_code_barres(code),
        "type": type_code,
        "pays_origine": pays,
        "checksum_valide": checksum_valide,
        "longueur": len(code)
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SUGGESTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def suggerer_categorie_produit(code: str) -> Optional[str]:
    """
    SuggÃ¨re une catÃ©gorie de produit basÃ©e sur le prÃ©fixe.
    (SimplifiÃ© - en production, utiliser une API comme Open Food Facts)
    
    Args:
        code: Code EAN-13
        
    Returns:
        CatÃ©gorie suggÃ©rÃ©e
    """
    if len(code) != 13:
        return None
    
    # PrÃ©fixes courants (approximatif)
    prefixe = code[:3]
    
    # France (300-379)
    if 300 <= int(prefixe) <= 379:
        return "Produit franÃ§ais"
    
    return "Produit importÃ©"

