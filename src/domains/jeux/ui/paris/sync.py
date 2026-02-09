"""
Fonctions de synchronisation avec l'API Football-Data.
"""

from ._common import (
    date, Dict, logger,
    get_session, Equipe, Match,
    CHAMPIONNATS,
    api_charger_classement, api_charger_matchs_a_venir, charger_matchs_termines,
)


def sync_equipes_depuis_api(championnat: str) -> int:
    """
    Synchronise TOUTES les équipes d'un championnat depuis l'API.
    Ajoute les nouvelles, met à jour les existantes.
    
    Returns:
        Nombre d'équipes ajoutées/mises à jour
    """
    try:
        logger.info(f"🔄 Synchronisation des équipes: {championnat}")
        
        classement = api_charger_classement(championnat)
        if not classement:
            msg = f"⚠️ Impossible de charger {championnat} via API.\n💡 Conseil: Configurer FOOTBALL_DATA_API_KEY dans .env pour synchroniser depuis l'API Football-Data.org"
            logger.warning(msg)
            return 0
        
        count = 0
        with get_session() as session:
            for equipe_api in classement:
                try:
                    # Chercher si équipe existe déjà
                    equipe = session.query(Equipe).filter(
                        Equipe.nom == equipe_api["nom"],
                        Equipe.championnat == championnat
                    ).first()
                    
                    if equipe:
                        # Mettre à jour les stats
                        equipe.matchs_joues = equipe_api.get("matchs_joues", equipe.matchs_joues)
                        equipe.victoires = equipe_api.get("victoires", equipe.victoires)
                        equipe.nuls = equipe_api.get("nuls", equipe.nuls)
                        equipe.defaites = equipe_api.get("defaites", equipe.defaites)
                        equipe.buts_marques = equipe_api.get("buts_marques", equipe.buts_marques)
                        equipe.buts_encaisses = equipe_api.get("buts_encaisses", equipe.buts_encaisses)
                    else:
                        # Créer nouvelle équipe
                        equipe = Equipe(
                            nom=equipe_api["nom"],
                            championnat=championnat,
                            matchs_joues=equipe_api.get("matchs_joues", 0),
                            victoires=equipe_api.get("victoires", 0),
                            nuls=equipe_api.get("nuls", 0),
                            defaites=equipe_api.get("defaites", 0),
                            buts_marques=equipe_api.get("buts_marques", 0),
                            buts_encaisses=equipe_api.get("buts_encaisses", 0)
                        )
                        session.add(equipe)
                    count += 1
                except Exception as e:
                    logger.debug(f"Erreur équipe {equipe_api.get('nom')}: {e}")
                    continue
            
            try:
                session.commit()
            except Exception as e:
                logger.error(f"Erreur commit équipes: {e}")
                session.rollback()
        
        return count
    except Exception as e:
        logger.error(f"❌ Erreur sync équipes: {e}")
        return 0


def sync_tous_championnats() -> Dict[str, int]:
    """Synchronise TOUS les championnats d'un coup."""
    resultats = {}
    for champ in CHAMPIONNATS:
        count = sync_equipes_depuis_api(champ)
        resultats[champ] = count
    return resultats


def sync_matchs_a_venir(jours: int = 7) -> Dict[str, int]:
    """
    Synchronise les matchs à venir depuis l'API pour tous les championnats.
    
    Returns:
        Dictionnaire {championnat: nb_matchs_ajoutés}
    """
    resultats = {}
    
    try:
        with get_session() as session:
            for champ in CHAMPIONNATS:
                try:
                    matchs_api = api_charger_matchs_a_venir(champ, jours=jours)
                    count = 0
                    
                    for match_api in matchs_api:
                        # Chercher les équipes
                        dom_nom = match_api.get("equipe_domicile", "")
                        ext_nom = match_api.get("equipe_exterieur", "")
                        date_match = match_api.get("date")
                        
                        if not dom_nom or not ext_nom or not date_match:
                            continue
                        
                        dom = session.query(Equipe).filter(
                            Equipe.nom.ilike(f"%{dom_nom}%"),
                            Equipe.championnat == champ
                        ).first()
                        
                        ext = session.query(Equipe).filter(
                            Equipe.nom.ilike(f"%{ext_nom}%"),
                            Equipe.championnat == champ
                        ).first()
                        
                        if not dom or not ext:
                            continue
                        
                        # Vérifier si match existe déjà
                        existing = session.query(Match).filter(
                            Match.equipe_domicile_id == dom.id,
                            Match.equipe_exterieur_id == ext.id,
                            Match.date_match == date_match
                        ).first()
                        
                        if existing:
                            continue
                        
                        # Créer le match
                        nouveau_match = Match(
                            equipe_domicile_id=dom.id,
                            equipe_exterieur_id=ext.id,
                            championnat=champ,
                            date_match=date_match,
                            heure=match_api.get("heure"),
                            cote_dom=match_api.get("cote_domicile"),
                            cote_nul=match_api.get("cote_nul"),
                            cote_ext=match_api.get("cote_exterieur"),
                            joue=False
                        )
                        session.add(nouveau_match)
                        count += 1
                        logger.debug(f"  ➕ {dom_nom} vs {ext_nom} ({date_match})")
                        
                except Exception as e:
                    logger.debug(f"Erreur sync {champ}: {e}")
                    continue
                
                resultats[champ] = count
            
            session.commit()
            total = sum(resultats.values())
            logger.info(f"✅ {total} nouveaux matchs synchronisés")
            
    except Exception as e:
        logger.error(f"❌ Erreur sync matchs: {e}")
    
    return resultats


def refresh_scores_matchs() -> int:
    """
    Met à jour les scores des matchs terminés depuis l'API Football-Data.
    
    Returns:
        Nombre de matchs mis à jour
    """
    try:
        count = 0
        with get_session() as session:
            # Matchs non joués dans le passé
            matchs_a_maj = session.query(Match).filter(
                Match.joue == False,
                Match.date_match < date.today()
            ).all()
            
            if not matchs_a_maj:
                logger.info("✅ Tous les matchs sont à jour")
                return 0
            
            logger.info(f"ℹ️ {len(matchs_a_maj)} matchs non terminés à vérifier")
            
            # Récupérer les scores depuis l'API pour chaque championnat
            for champ in CHAMPIONNATS:
                try:
                    matchs_api = charger_matchs_termines(champ, jours=14)
                    
                    for match_bd in matchs_a_maj:
                        if match_bd.championnat != champ:
                            continue
                        
                        dom_nom = match_bd.equipe_domicile.nom if match_bd.equipe_domicile else ""
                        ext_nom = match_bd.equipe_exterieur.nom if match_bd.equipe_exterieur else ""
                        
                        for match_api in matchs_api:
                            api_dom = match_api.get("equipe_domicile", "")
                            api_ext = match_api.get("equipe_exterieur", "")
                            
                            if (dom_nom.lower() in api_dom.lower() or api_dom.lower() in dom_nom.lower()) and \
                               (ext_nom.lower() in api_ext.lower() or api_ext.lower() in ext_nom.lower()):
                                score_d = match_api.get("score_domicile")
                                score_e = match_api.get("score_exterieur")
                                
                                if score_d is not None and score_e is not None:
                                    match_bd.score_domicile = score_d
                                    match_bd.score_exterieur = score_e
                                    match_bd.joue = True
                                    count += 1
                                    logger.info(f"✅ {dom_nom} vs {ext_nom}: {score_d}-{score_e}")
                                break
                                
                except Exception as e:
                    logger.debug(f"Erreur API {champ}: {e}")
                    continue
            
            if count > 0:
                session.commit()
                logger.info(f"✅ {count} matchs mis à jour avec scores")
            else:
                logger.info("ℹ️ Aucun score trouvé dans l'API")
            
            return count
            
    except Exception as e:
        logger.error(f"❌ Erreur refresh scores: {e}")
        return 0


__all__ = [
    "sync_equipes_depuis_api",
    "sync_tous_championnats",
    "sync_matchs_a_venir",
    "refresh_scores_matchs",
]
