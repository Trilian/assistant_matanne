"""
Module Loto - Fonctions helper (DB queries)
"""

from ._common import st, obtenir_contexte_db, TirageLoto, GrilleLoto


def charger_tirages(limite: int = 100):
    """Charge l'historique des tirages"""
    try:
        with obtenir_contexte_db() as session:
            tirages = session.query(TirageLoto).order_by(
                TirageLoto.date_tirage.desc()
            ).limit(limite).all()
            
            return [
                {
                    "id": t.id,
                    "date_tirage": t.date_tirage,
                    "numero_1": t.numero_1,
                    "numero_2": t.numero_2,
                    "numero_3": t.numero_3,
                    "numero_4": t.numero_4,
                    "numero_5": t.numero_5,
                    "numero_chance": t.numero_chance,
                    "jackpot_euros": t.jackpot_euros,
                    "numeros": t.numeros,
                    "numeros_str": t.numeros_str
                }
                for t in tirages
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement tirages: {e}")
        return []


def charger_grilles_utilisateur():
    """Charge les grilles de l'utilisateur"""
    try:
        with obtenir_contexte_db() as session:
            grilles = session.query(GrilleLoto).order_by(
                GrilleLoto.date_creation.desc()
            ).limit(50).all()
            
            return [
                {
                    "id": g.id,
                    "numeros": g.numeros,
                    "numeros_str": g.numeros_str,
                    "numero_chance": g.numero_chance,
                    "source": g.source_prediction,
                    "est_virtuelle": g.est_virtuelle,
                    "mise": g.mise,
                    "tirage_id": g.tirage_id,
                    "numeros_trouves": g.numeros_trouves,
                    "chance_trouvee": g.chance_trouvee,
                    "rang": g.rang,
                    "gain": g.gain,
                    "date": g.date_creation
                }
                for g in grilles
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement grilles: {e}")
        return []

