# assistant_matanne/modules/calendrier.py

import streamlit as st
import pandas as pd
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("Calendrier")
    st.subheader("Affichage des événements : routines, projets et repas")

    create_all_tables()
    conn = get_connection()
    try:
        # Routines et tâches
        df_routines = pd.read_sql(
            """SELECT r.id as routine_id, r.name as routine_name, t.task_name,
                      t.scheduled_time, t.status, c.name as child_name
               FROM routines r
                        LEFT JOIN routine_tasks t ON r.id = t.routine_id
                        LEFT JOIN child_profiles c ON r.child_id = c.id""", conn)
        if not df_routines.empty:
            st.subheader("Routines et tâches")
            st.dataframe(df_routines[['routine_name','task_name','scheduled_time','status','child_name']])
            if st.button("Exporter routines"):
                st.download_button("Télécharger CSV", df_routines.to_csv(index=False), "routines.csv", "text/csv")
        else:
            st.info("Aucune routine ou tâche programmée")

        # Projets maison
        df_projects = pd.read_sql(
            """SELECT p.id as project_id, p.name as project_name, p.start_date, p.end_date,
                      t.task_name, t.status
               FROM projects p
                        LEFT JOIN project_tasks t ON p.id = t.project_id""", conn)
        if not df_projects.empty:
            st.subheader("Projets maison")
            st.dataframe(df_projects[['project_name','task_name','start_date','end_date','status']])
            if st.button("Exporter projets"):
                st.download_button("Télécharger CSV", df_projects.to_csv(index=False), "projets.csv", "text/csv")
        else:
            st.info("Aucun projet en cours")

        # Repas planifiés
        df_meals = pd.read_sql(
            """SELECT b.id as batch_id, r.name as recipe_name, b.scheduled_date
               FROM batch_meals b
                        LEFT JOIN recipes r ON b.recipe_id = r.id""", conn)
        if not df_meals.empty:
            st.subheader("Repas planifiés")
            st.dataframe(df_meals[['recipe_name','scheduled_date']])
            if st.button("Exporter repas planifiés"):
                st.download_button("Télécharger CSV", df_meals.to_csv(index=False), "repas.csv", "text/csv")
        else:
            st.info("Aucun repas planifié")
    finally:
        conn.close()