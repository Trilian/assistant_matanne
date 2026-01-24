"""
Configuration et intégration des modules Famille améliorés
Guide d'utilisation des helpers et caching pour une meilleure performance
"""

# ═══════════════════════════════════════════════════════════
# UTILISATION DES HELPERS
# ═══════════════════════════════════════════════════════════

"""
Dans chaque module (jules.py, sante.py, activites.py, shopping.py):

1. IMPORTER LES HELPERS:
   from src.modules.famille.helpers import (
       get_or_create_jules,
       calculer_age_jules,
       get_milestones_by_category,
       count_milestones_by_category,
       get_objectives_actifs,
       calculer_progression_objectif,
       get_budget_par_period,
       get_activites_semaine,
       get_routines_actives,
       get_stats_santé_semaine,
       clear_famille_cache
   )

2. UTILISER LE CACHE (automatique dans helpers):
   @st.cache_data(ttl=1800)  # TTL = 30 minutes
   
   # Les helpers utilisent déjà le cache!
   # Pas besoin de redéclarer dans les modules

3. TRY/EXCEPT:
   try:
       data = get_routines_actives()
       st.write(f"Trouvé {len(data)} routines")
   except Exception as e:
       st.error(f"❌ Erreur: {str(e)}")

4. CLEAR CACHE APRÈS MODIFICATIONS:
   if st.button("✅ Enregistrer"):
       ajouter_routine()
       clear_famille_cache()  # Vider le cache
       st.rerun()
"""

# ═══════════════════════════════════════════════════════════
# ARCHITECTURAL DECISIONS
# ═══════════════════════════════════════════════════════════

"""
✅ WHAT WAS ADDED:

1. HELPERS FILE (src/modules/famille/helpers.py):
   - get_or_create_jules(): Récupère ou crée Jules
   - calculer_age_jules(): Calcule l'âge en jours/semaines/mois
   - get_milestones_by_category(): Jalons groupés par catégorie
   - count_milestones_by_category(): Comptage par catégorie
   - calculer_progression_objectif(): % de progression
   - get_objectives_actifs(): Objectifs avec progression calculée
   - get_budget_par_period(): Budget par jour/semaine/mois
   - get_budget_mois_dernier(): Total budget mois précédent
   - get_activites_semaine(): Activités de la semaine
   - get_budget_activites_mois(): Dépenses activités du mois
   - get_routines_actives(): Routines de santé
   - get_stats_santé_semaine(): Stats hebdo (séances, minutes, calories, énergie, moral)
   - clear_famille_cache(): Vide le cache Streamlit

2. CACHING:
   - Tous les helpers "charger" utilisent @st.cache_data(ttl=1800)
   - TTL = 30 minutes = bon balance entre performance et fraîcheur
   - Cache auto-invalidé après modifications (clear_famille_cache())

3. ERROR HANDLING:
   - Try/except dans tous les helpers
   - Messages d'erreur clairs pour l'utilisateur
   - Retour de valeurs par défaut (listes vides, 0, etc)

4. IMPROVED SANTE.PY:
   - Graphiques Plotly pour progression (calories, durée, énergie, moral)
   - Forme moderne avec tabs bien organisées
   - All helpers intégrés
   - Try/except complètes

5. DATABASE RELATIONS:
   - ChildProfile.milestones (nouvelle relation)
   - Milestone.child avec back_populates

✅ READY FOR INTEGRATION:
- Jules module: À mettre à jour avec helpers
- Activités module: À mettre à jour avec helpers  
- Shopping module: À mettre à jour avec helpers
- Accueil module: À mettre à jour avec helpers

NEXT STEPS:
1. Intégrer les helpers dans les autres modules
2. Ajouter graphiques dans activites.py et shopping.py
3. Intégrer avec Cuisine (suggestions recettes + objectifs santé)
4. Intégrer avec Courses (shopping list pré-remplie)
5. Tests locaux complets avec pytest
"""

# ═══════════════════════════════════════════════════════════
# PATTERN: UTILISATION DANS LES MODULES
# ═══════════════════════════════════════════════════════════

"""
EXEMPLE 1: AFFICHAGE AVEC CACHE
─────────────────────────────────

def main():
    # Ces données sont automatiquement cachées 30 min
    routines = get_routines_actives()
    objectives = get_objectives_actifs()
    stats = get_stats_santé_semaine()
    
    # Affichage
    st.metric("Routines", len(routines))
    st.metric("Progression", f"{objectives[0]['progression']:.0f}%")


EXEMPLE 2: MODIFICATION AVEC CACHE CLEAR
──────────────────────────────────────────

def ajouter_routine():
    if st.button("Créer routine"):
        try:
            with get_session() as session:
                routine = HealthRoutine(...)
                session.add(routine)
                session.commit()
                st.success("✅ Créé!")
                clear_famille_cache()  # IMPORTANT!
                st.rerun()
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")


EXEMPLE 3: GRAPHIQUES
──────────────────────

import plotly.graph_objects as go

entries = charger_entrees_recentes(30)
df = pd.DataFrame(entries)
df['date'] = pd.to_datetime(df['date'])

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['date'], y=df['calories'], name='Calories'))
st.plotly_chart(fig, use_container_width=True)


EXEMPLE 4: ERROR HANDLING
──────────────────────────

try:
    objectives = get_objectives_actifs()
    if not objectives:
        st.info("Aucun objectif créé")
    else:
        for obj in objectives:
            st.write(f"{obj['titre']}: {obj['progression']:.0f}%")
except Exception as e:
    st.error(f"❌ Erreur chargement: {str(e)}")
"""

# ═══════════════════════════════════════════════════════════
# CHECKLIST DE COMPLETION
# ═══════════════════════════════════════════════════════════

"""
CRITIQUE (FAIT):
✅ Relations bidirectionnelles dans models.py
✅ Helpers avec caching et error handling
✅ Module sante.py amélioré avec graphiques
✅ Try/except everywhere

À FAIRE (FACILE - 30 min):
⏳ Intégrer helpers dans jules.py
⏳ Intégrer helpers dans activites.py  
⏳ Intégrer helpers dans shopping.py
⏳ Intégrer helpers dans accueil.py

À FAIRE (IMPORTANT - 1h):
⏳ Ajouter graphiques activites.py
⏳ Ajouter graphiques shopping.py
⏳ Tests locaux (pytest tests/test_famille.py)
⏳ Vérification sur Supabase

À FAIRE (BONUS - 2h):
⏳ Intégration Cuisine (suggestion recettes + objectifs)
⏳ Intégration Courses (pre-fill shopping)
⏳ Notifications rappels
⏳ Export CSV/PDF

QUICK START:
1. Vérifier que helpers.py existe et fonctionne
2. Vérifier que sante.py fonctionne localement
3. Copier le pattern helper dans autres modules
4. Tester: streamlit run src/app.py
5. Aller à Famille > Santé et cliquer partout

DÉPLOIEMENT:
1. Pousser code sur main/dev
2. Vérifier migrations Supabase OK
3. Tester en production
4. Enjoy! 🎉
"""
