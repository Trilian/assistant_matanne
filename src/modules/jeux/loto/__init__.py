"""
Module Loto - Analyse statistique et simulation de stratÃegies

âš ï¸ DISCLAIMER: Le Loto est un jeu de hasard pur.
Aucune stratÃegie ne peut prÃedire les rÃesultats.
Ce module est Ã  but Ãeducatif et de divertissement.

FonctionnalitÃes:
- Historique des tirages avec statistiques
- Analyse des frÃequences (curiositÃe mathÃematique)
- GÃenÃeration de grilles selon diffÃerentes stratÃegies
- Suivi des "paris virtuels" pour tester les stratÃegies
- Simulation et backtesting
"""

from ._common import st

# Import des fonctions pour exposer l'API publique
from .sync import sync_tirages_loto
from .utilitaires import charger_tirages, charger_grilles_utilisateur
from .crud import ajouter_tirage, enregistrer_grille
from .statistiques import (
    afficher_dernier_tirage,
    afficher_statistiques_frequences,
    afficher_esperance
)
from .generateur import afficher_generateur_grilles, afficher_mes_grilles
from .simulation import afficher_simulation, afficher_gestion_tirages


def app():
    """Point d'entrÃee du module Loto"""
    
    st.title("ðŸŽ° Loto - Analyse & Simulation")
    st.caption("Analysez les statistiques et testez vos stratÃegies (virtuellement)")
    
    # Avertissement
    with st.expander("âš ï¸ Avertissement important", expanded=False):
        st.markdown("""
        **Le Loto est un jeu de hasard pur.**
        
        - Chaque tirage est **totalement indÃependant** des prÃecÃedents
        - Un numÃero "en retard" n'a **pas plus de chances** de sortir
        - Aucune stratÃegie ne peut **prÃedire** les rÃesultats
        - L'espÃerance mathÃematique est **nÃegative** (vous perdez en moyenne)
        
        Ce module est Ã  but **Ãeducatif et de divertissement**. 
        Ne jouez que ce que vous pouvez vous permettre de perdre.
        """)
    
    # Charger donnÃees
    tirages = charger_tirages(limite=200)
    
    # Tabs principaux
    tabs = st.tabs([
        "ðŸ“Š Statistiques", 
        "ðŸŽ² GÃenÃerer Grille",
        "ðŸŽ« Mes Grilles",
        "ðŸ”¬ Simulation",
        "ðŸ“ Maths",
        "âš™ï¸ Tirages"
    ])
    
    # TAB 1: STATISTIQUES
    with tabs[0]:
        afficher_dernier_tirage(tirages)
        st.divider()
        afficher_statistiques_frequences(tirages)
    
    # TAB 2: GÉNÉRATION
    with tabs[1]:
        afficher_generateur_grilles(tirages)
    
    # TAB 3: MES GRILLES
    with tabs[2]:
        afficher_mes_grilles()
    
    # TAB 4: SIMULATION
    with tabs[3]:
        afficher_simulation()
    
    # TAB 5: MATHÉMATIQUES
    with tabs[4]:
        afficher_esperance()
    
    # TAB 6: GESTION TIRAGES
    with tabs[5]:
        afficher_gestion_tirages()


# Alias
def main():
    app()


__all__ = [
    # Entry point
    "app",
    "main",
    # Sync
    "sync_tirages_loto",
    # Helpers
    "charger_tirages",
    "charger_grilles_utilisateur",
    # CRUD
    "ajouter_tirage",
    "enregistrer_grille",
    # UI
    "afficher_dernier_tirage",
    "afficher_statistiques_frequences",
    "afficher_esperance",
    "afficher_generateur_grilles",
    "afficher_mes_grilles",
    "afficher_simulation",
    "afficher_gestion_tirages",
]
