"""
Scraper FDJ Loto pour récupérer les historiques de tirages

Source: https://www.fdj.fr/jeux/loto (web scraping)
Alternative API: Les résultats sont également disponibles via scraping
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)


class ScraperLotoFDJ:
    """Scraper pour les données de Loto FDJ"""
    
    BASE_URL = "https://www.fdj.fr"
    LOTO_URL = "https://www.fdj.fr/jeux/loto"
    TIRAGE_API = "https://www.fdj.fr/api/v1/loto"  # API non-officielle
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def charger_derniers_tirages(self, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Charge les derniers tirages de Loto
        
        Args:
            limite: Nombre de tirages à récupérer
            
        Returns:
            Liste des tirages [date, numeros, numero_chance, gains]
        """
        try:
            # Essayer via l'API FDJ
            return self._charger_via_api(limite)
        except Exception as e:
            logger.warning(f"❌ Erreur API Loto: {e}, passage au scraping web")
            try:
                return self._charger_via_web(limite)
            except Exception as e2:
                logger.error(f"❌ Scraping web échoué: {e2}")
                return []
    
    def _charger_via_api(self, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Charge via l'API FDJ (plus fiable)
        
        Format de l'API FDJ (non-officielle mais stable):
        https://www.fdj.fr/api/v1/loto/results?pageSize=50
        """
        try:
            url = f"{self.TIRAGE_API}/results"
            params = {"pageSize": min(limite, 100)}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            tirages = []
            
            # Structure de réponse FDJ (peut varier)
            results = data.get("results", data.get("tirage", []))
            
            for tirage in results:
                try:
                    # Extraire les numéros
                    nums_str = tirage.get("numeroGagnants") or tirage.get("numerosGagnants") or ""
                    numeros = [int(n.strip()) for n in nums_str.split() if n.strip().isdigit()]
                    
                    # Extraire le numéro chance
                    num_chance = None
                    if "numeroBall" in tirage:
                        num_chance = int(tirage["numeroBall"])
                    elif "boule" in tirage:
                        num_chance = int(tirage["boule"])
                    
                    # Date du tirage
                    date_str = tirage.get("datetirage") or tirage.get("date") or ""
                    
                    if numeros and len(numeros) >= 5:
                        tirages.append({
                            "date": date_str,
                            "numeros": sorted(numeros[:5]),  # 5 numéros principaux
                            "numero_chance": num_chance,
                            "gains": tirage.get("gains", {}),
                            "source": "FDJ API"
                        })
                
                except Exception as e:
                    logger.debug(f"Erreur parsing tirage: {e}")
                    continue
            
            logger.info(f"✅ {len(tirages)} tirages chargés via API FDJ")
            return tirages
        
        except Exception as e:
            raise e
    
    def _charger_via_web(self, limite: int = 50) -> List[Dict[str, Any]]:
        """
        Fallback: scrape le site FDJ directement (plus lent)
        """
        try:
            response = self.session.get(self.LOTO_URL, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            tirages = []
            
            # Chercher les conteneurs de tirages
            # Structure peut changer - chercher par attributs communs
            tirage_containers = soup.find_all("div", class_=re.compile(r"tirage|result|draw", re.I))
            
            for container in tirage_containers[:limite]:
                try:
                    # Extraire date
                    date_elem = container.find(class_=re.compile(r"date", re.I))
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    
                    # Extraire numéros
                    nums_elem = container.find_all(class_=re.compile(r"numero|ball|number", re.I))
                    numeros = []
                    
                    for elem in nums_elem:
                        text = elem.get_text(strip=True)
                        if text.isdigit():
                            numeros.append(int(text))
                    
                    if numeros and len(numeros) >= 5:
                        tirages.append({
                            "date": date_str,
                            "numeros": sorted(numeros[:5]),
                            "numero_chance": numeros[5] if len(numeros) > 5 else None,
                            "source": "FDJ Web"
                        })
                
                except Exception as e:
                    logger.debug(f"Erreur scraping tirage: {e}")
                    continue
            
            logger.info(f"✅ {len(tirages)} tirages chargés via web")
            return tirages
        
        except Exception as e:
            raise e
    
    def calculer_statistiques_historiques(
        self,
        tirages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcule les statistiques sur l'historique des tirages
        
        Args:
            tirages: Liste des tirages
            
        Returns:
            Dictionnaire avec fréquences, tendances, etc
        """
        if not tirages:
            return {}
        
        tous_numeros = []
        tous_chances = []
        paires = []
        
        for tirage in tirages:
            numeros = tirage.get("numeros", [])
            num_chance = tirage.get("numero_chance")
            
            tous_numeros.extend(numeros)
            if num_chance:
                tous_chances.append(num_chance)
            
            # Compter les paires
            for i, n1 in enumerate(numeros):
                for n2 in numeros[i+1:]:
                    paires.append(tuple(sorted([n1, n2])))
        
        # Fréquences
        freq_numeros = dict(Counter(tous_numeros))
        freq_chances = dict(Counter(tous_chances))
        freq_paires = dict(Counter(paires))
        
        # Identifier chauds/froids
        moy_freq = sum(freq_numeros.values()) / len(freq_numeros) if freq_numeros else 0
        numeros_chauds = [n for n, f in freq_numeros.items() if f > moy_freq * 1.5]
        numeros_froids = [n for n, f in freq_numeros.items() if f < moy_freq * 0.5]
        
        return {
            "nombre_tirages": len(tirages),
            "periode": f"{tirages[-1].get('date')} à {tirages[0].get('date')}",
            "frequences_numeros": freq_numeros,
            "frequences_chances": freq_chances,
            "paires_frequentes": sorted(freq_paires.items(), key=lambda x: x[1], reverse=True)[:10],
            "numeros_chauds": sorted(numeros_chauds),
            "numeros_froids": sorted(numeros_froids),
            "moyenne_frequence": round(moy_freq, 2)
        }
    
    def obtenir_dernier_tirage(self) -> Optional[Dict[str, Any]]:
        """Obtient uniquement le dernier tirage"""
        tirages = self.charger_derniers_tirages(limite=1)
        return tirages[0] if tirages else None
    
    def obtenir_tirage_du_jour(self) -> Optional[Dict[str, Any]]:
        """Obtient le tirage du jour s'il existe"""
        tirages = self.charger_derniers_tirages(limite=10)
        
        aujourd_hui = date.today().strftime("%Y-%m-%d")
        
        for tirage in tirages:
            # Essayer de parser la date
            try:
                date_tirage = tirage.get("date")
                if isinstance(date_tirage, str):
                    # Normaliser le format
                    if "/" in date_tirage:
                        date_obj = datetime.strptime(date_tirage, "%d/%m/%Y").date()
                    else:
                        date_obj = datetime.fromisoformat(date_tirage).date()
                    
                    if str(date_obj) == aujourd_hui:
                        return tirage
            except:
                continue
        
        return None


# ═══════════════════════════════════════════════════════════
# INTERFACE SIMPLE
# ═══════════════════════════════════════════════════════════

def charger_tirages_loto(limite: int = 50) -> List[Dict[str, Any]]:
    """
    Charge les tirages Loto FDJ
    
    Usage:
        tirages = charger_tirages_loto(100)
        for tirage in tirages:
            print(f"{tirage['date']}: {tirage['numeros']} + {tirage['numero_chance']}")
    """
    scraper = ScraperLotoFDJ()
    return scraper.charger_derniers_tirages(limite)


def obtenir_statistiques_loto(limite: int = 50) -> Dict[str, Any]:
    """Obtient les statistiques sur les derniers tirages"""
    scraper = ScraperLotoFDJ()
    tirages = scraper.charger_derniers_tirages(limite)
    return scraper.calculer_statistiques_historiques(tirages)


def obtenir_dernier_tirage_loto() -> Optional[Dict[str, Any]]:
    """Obtient le dernier tirage"""
    scraper = ScraperLotoFDJ()
    return scraper.obtenir_dernier_tirage()


# ═══════════════════════════════════════════════════════════
# INTEGRATION BD
# ═══════════════════════════════════════════════════════════

def inserer_tirages_en_bd(limite: int = 50):
    """
    Charge les tirages FDJ et les insère dans la BD
    
    À appeler périodiquement (ex: cron job quotidien)
    """
    try:
        from src.core.database import get_db_context
        from src.core.models import TirageLoto, StatistiquesLoto
        import json
        
        scraper = ScraperLotoFDJ()
        tirages = scraper.charger_derniers_tirages(limite)
        stats = scraper.calculer_statistiques_historiques(tirages)
        
        with get_db_context() as session:
            for tirage_data in tirages:
                # Vérifier si le tirage existe déjà
                existing = session.query(TirageLoto).filter(
                    TirageLoto.date == tirage_data["date"]
                ).first()
                
                if not existing:
                    tirage = TirageLoto(
                        date=tirage_data["date"],
                        numeros=tirage_data["numeros"],
                        numero_chance=tirage_data.get("numero_chance"),
                        source=tirage_data.get("source", "FDJ API")
                    )
                    session.add(tirage)
            
            # Mettre à jour les statistiques
            stats_entry = StatistiquesLoto(
                type_stat="frequences",
                donnees_json=stats
            )
            session.add(stats_entry)
            
            session.commit()
            logger.info(f"✅ {len(tirages)} tirages insérés en BD")
            return True
    
    except Exception as e:
        logger.error(f"❌ Erreur insertion BD: {e}")
        return False
