import streamlit as st
import pandas as pd
from core.test_manager import (
    run_all_tests,
    open_test_dashboard,
    get_test_report,
)
from core.helpers import log_function, log_event


@log_function
def app():

    st.title("🧪 Mode Test – Vérification des modules")
    st.markdown("Ce panneau permet de lancer les tests automatiques de l’application.")

    st.info("💡 Astuce : avant un déploiement, lance toujours tous les tests.")

    # --- Bouton de lancement ---
    if st.button("🚀 Lancer tous les tests"):
        with st.spinner("Exécution des tests…"):
            results = run_all_tests()
            dashboard = open_test_dashboard(results)
            report = get_test_report(results)

        st.success("Tests terminés ✔️")

        # --- Dashboard résumé ---
        st.header("📊 Résumé global")
        col1, col2, col3 = st.columns(3)
        col1.metric("Modules testés", dashboard["total"])
        col2.metric("Réussis", dashboard["success_count"])
        col3.metric("Échecs", dashboard["fail_count"])

        # --- Tableau des résultats ---
        st.subheader("Détails des modules")
        df = pd.DataFrame(report)
        st.dataframe(df)

        # --- Graphique (réussite par module) ---
        st.subheader("📈 Graphique succès / échec")
        graph_df = pd.DataFrame({
            "module": [r["module"] for r in report],
            "success": [1 if r["success"] else 0 for r in report]
        }).set_index("module")

        st.bar_chart(graph_df)

        # --- Détails par module ---
        st.subheader("🔍 Explorer les erreurs")
        for r in report:
            with st.expander(f"🧩 {r['module']} – {'OK' if r['success'] else 'ÉCHEC'}"):
                st.write(f"⏱ Temps : {r['duration']:.2f}s")

                if r["errors"]:
                    st.error("Erreurs détectées :")
                    for err in r["errors"]:
                        st.code(err)
                else:
                    st.success("Aucune erreur ✓")

    else:
        st.warning("Clique sur **Lancer tous les tests** pour commencer.")