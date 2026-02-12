"""
Module Loto - Opérations CRUD (création/mise à jour)
"""

from ._common import (
    st, date, obtenir_contexte_db, TirageLoto, GrilleLoto,
    COUT_GRILLE, verifier_grille
)


def ajouter_tirage(date_t: date, numeros: list, chance: int, jackpot: int = None):
    """Ajoute un nouveau tirage"""
    try:
        if len(numeros) != 5:
            st.error("Il faut exactement 5 numéros")
            return False
        
        numeros = sorted(numeros)
        
        with obtenir_contexte_db() as session:
            tirage = TirageLoto(
                date_tirage=date_t,
                numero_1=numeros[0],
                numero_2=numeros[1],
                numero_3=numeros[2],
                numero_4=numeros[3],
                numero_5=numeros[4],
                numero_chance=chance,
                jackpot_euros=jackpot
            )
            session.add(tirage)
            session.commit()
            
            # Mettre à jour les grilles en attente
            grilles = session.query(GrilleLoto).filter(
                GrilleLoto.tirage_id == None
            ).all()
            
            for grille in grilles:
                grille_data = {
                    "numeros": grille.numeros,
                    "numero_chance": grille.numero_chance
                }
                resultat = verifier_grille(grille_data, {
                    "numero_1": numeros[0],
                    "numero_2": numeros[1],
                    "numero_3": numeros[2],
                    "numero_4": numeros[3],
                    "numero_5": numeros[4],
                    "numero_chance": chance,
                    "jackpot_euros": jackpot or 2_000_000
                })
                
                grille.tirage_id = tirage.id
                grille.numeros_trouves = resultat["bons_numeros"]
                grille.chance_trouvee = resultat["chance_ok"]
                grille.rang = resultat["rang"]
                grille.gain = resultat["gain"]
            
            session.commit()
            st.success(f"✅ Tirage du {date_t} enregistré!")
            return True
            
    except Exception as e:
        st.error(f"❌ Erreur ajout tirage: {e}")
        return False


def enregistrer_grille(numeros: list, chance: int, source: str = "manuel", 
                       est_virtuelle: bool = True):
    """Enregistre une nouvelle grille"""
    try:
        if len(numeros) != 5:
            st.error("Il faut exactement 5 numéros")
            return False
        
        numeros = sorted(numeros)
        
        with obtenir_contexte_db() as session:
            grille = GrilleLoto(
                numero_1=numeros[0],
                numero_2=numeros[1],
                numero_3=numeros[2],
                numero_4=numeros[3],
                numero_5=numeros[4],
                numero_chance=chance,
                source_prediction=source,
                est_virtuelle=est_virtuelle,
                mise=COUT_GRILLE
            )
            session.add(grille)
            session.commit()
            st.success(f"✅ Grille enregistrée: {'-'.join(map(str, numeros))} + N°{chance}")
            return True
            
    except Exception as e:
        st.error(f"❌ Erreur enregistrement grille: {e}")
        return False

