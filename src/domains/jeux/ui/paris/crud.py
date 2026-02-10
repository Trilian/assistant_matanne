"""
Fonctions CRUD pour les paris, équipes et matchs.
"""

from ._common import (
    st, date, Decimal, logger,
    obtenir_contexte_db, Equipe, Match, PariSportif,
)


def enregistrer_pari(match_id: int, prediction: str, cote: float, 
                     mise: float = 0, est_virtuel: bool = True):
    """Enregistre un nouveau pari"""
    try:
        with obtenir_contexte_db() as session:
            pari = PariSportif(
                match_id=match_id,
                type_pari="1N2",
                prediction=prediction,
                cote=cote,
                mise=Decimal(str(mise)),
                est_virtuel=est_virtuel,
                statut="en_attente"
            )
            session.add(pari)
            session.commit()
            return True
    except Exception as e:
        st.error(f"❌ Erreur enregistrement pari: {e}")
        return False


def ajouter_equipe(nom: str, championnat: str):
    """Ajoute une nouvelle équipe"""
    try:
        with obtenir_contexte_db() as session:
            equipe = Equipe(
                nom=nom,
                championnat=championnat
            )
            session.add(equipe)
            session.commit()
            st.success(f"✅ Équipe '{nom}' ajoutée!")
            return True
    except Exception as e:
        st.error(f"❌ Erreur ajout équipe: {e}")
        return False


def ajouter_match(equipe_dom_id: int, equipe_ext_id: int, 
                  championnat: str, date_match: date, heure: str = None):
    """Ajoute un nouveau match"""
    try:
        with obtenir_contexte_db() as session:
            match = Match(
                equipe_domicile_id=equipe_dom_id,
                equipe_exterieur_id=equipe_ext_id,
                championnat=championnat,
                date_match=date_match,
                heure=heure,
                joue=False
            )
            session.add(match)
            session.commit()
            st.success("✅ Match ajouté!")
            return True
    except Exception as e:
        st.error(f"❌ Erreur ajout match: {e}")
        return False


def enregistrer_resultat_match(match_id: int, score_dom: int, score_ext: int):
    """Enregistre le résultat d'un match"""
    try:
        with obtenir_contexte_db() as session:
            match = session.query(Match).get(match_id)
            if match:
                match.score_domicile = score_dom
                match.score_exterieur = score_ext
                match.joue = True
                
                # Déterminer le résultat
                if score_dom > score_ext:
                    match.resultat = "1"
                elif score_ext > score_dom:
                    match.resultat = "2"
                else:
                    match.resultat = "N"
                
                # Mettre à jour les paris liés
                for pari in match.paris:
                    if pari.statut == "en_attente":
                        if pari.prediction == match.resultat:
                            pari.statut = "gagne"
                            pari.gain = pari.mise * Decimal(str(pari.cote))
                        else:
                            pari.statut = "perdu"
                            pari.gain = Decimal("0")
                
                session.commit()
                st.success(f"✅ Résultat enregistré: {score_dom}-{score_ext}")
                return True
    except Exception as e:
        st.error(f"❌ Erreur enregistrement résultat: {e}")
        return False


def supprimer_match(match_id: int) -> bool:
    """
    Supprime un match et ses paris associés.
    
    Args:
        match_id: ID du match à supprimer
        
    Returns:
        True si suppression réussie
    """
    try:
        with obtenir_contexte_db() as session:
            match = session.query(Match).get(match_id)
            if match:
                # Supprimer d'abord les paris liés
                for pari in match.paris:
                    session.delete(pari)
                
                # Puis le match
                session.delete(match)
                session.commit()
                logger.info(f"🗑️ Match {match_id} supprimé")
                return True
            else:
                logger.warning(f"Match {match_id} non trouvé")
                return False
    except Exception as e:
        logger.error(f"❌ Erreur suppression match: {e}")
        return False


__all__ = [
    "enregistrer_pari",
    "ajouter_equipe",
    "ajouter_match",
    "enregistrer_resultat_match",
    "supprimer_match",
]

