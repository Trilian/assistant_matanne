"""
Module Loto - Synchronisation des tirages
"""

from ._common import (
    datetime, logger, get_session, TirageLoto, charger_tirages_loto
)


def sync_tirages_loto(limite: int = 50) -> int:
    """
    Synchronise les derniers tirages du Loto FDJ depuis le web.
    
    Args:
        limite: Nombre de tirages à récupérer (max 100)
        
    Returns:
        Nombre de nouveaux tirages ajoutés
    """
    try:
        logger.info(f"🔄 Synchronisation Loto: récupération {limite} derniers tirages")
        
        # Charger les tirages depuis le web/API FDJ
        tirages_api = charger_tirages_loto(limite=limite)
        
        if not tirages_api:
            logger.warning("⚠️ Pas de données Loto trouvées")
            return 0
        
        count = 0
        with get_session() as session:
            for tirage_api in tirages_api:
                try:
                    # Vérifier si le tirage existe déjà
                    date_tirage = None
                    if isinstance(tirage_api.get("date"), str):
                        # Parser la date
                        try:
                            date_tirage = datetime.strptime(
                                tirage_api["date"], "%Y-%m-%d"
                            ).date()
                        except:
                            try:
                                date_tirage = datetime.strptime(
                                    tirage_api["date"], "%d/%m/%Y"
                                ).date()
                            except:
                                continue
                    else:
                        date_tirage = tirage_api.get("date")
                    
                    if not date_tirage:
                        continue
                    
                    # Chercher si tirage existe
                    existing = session.query(TirageLoto).filter(
                        TirageLoto.date_tirage == date_tirage
                    ).first()
                    
                    if existing:
                        logger.debug(f"Tirage du {date_tirage} existe déjà")
                        continue
                    
                    # Créer nouveau tirage
                    numeros = tirage_api.get("numeros", [])
                    numero_chance = tirage_api.get("numero_chance")
                    jackpot = tirage_api.get("jackpot", 0)
                    
                    if len(numeros) >= 5 and numero_chance:
                        numeros = sorted(numeros[:5])
                        
                        tirage = TirageLoto(
                            date_tirage=date_tirage,
                            numero_1=numeros[0],
                            numero_2=numeros[1],
                            numero_3=numeros[2],
                            numero_4=numeros[3],
                            numero_5=numeros[4],
                            numero_chance=numero_chance,
                            jackpot_euros=jackpot
                        )
                        session.add(tirage)
                        count += 1
                        logger.info(f"✅ Tirage {date_tirage}: {numeros} + {numero_chance}")
                
                except Exception as e:
                    logger.debug(f"Erreur tirage: {e}")
                    continue
            
            try:
                session.commit()
                logger.info(f"📊 {count} nouveaux tirages ajoutés")
            except Exception as e:
                logger.error(f"Erreur commit: {e}")
                session.rollback()
        
        return count
    
    except Exception as e:
        logger.error(f"❌ Erreur sync Loto: {e}")
        return 0
