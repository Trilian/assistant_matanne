# assistant_matanne/modules/jardin.py

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("🌿 Jardin")
    st.subheader("Suivi des plantations, semis et récoltes (Suivi de Jules)")

    # créer les tables si manquent
    create_all_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------
    # Formulaire : ajouter / modifier un élément
    # -----------------------
    with st.expander("➕ Ajouter / Mettre à jour un élément du jardin"):
        name = st.text_input("Nom de la plante ou du semis")
        category = st.selectbox("Catégorie", ["Légume", "Fruit", "Fleur", "Aromatique", "Autre"])
        quantity = st.number_input("Quantité (plants, sachets, etc.)", min_value=0.0, step=1.0, value=1.0)
        unit = st.text_input("Unité (ex: plants, sachets)", value="plants")
        planting_date = st.date_input("Date de plantation (facultatif)", value=date.today())
        harvest_date = st.date_input("Date de récolte prévue (facultatif)", value=date.today())
        watering_freq = st.number_input("Fréquence d'arrosage (jours) — laisser 0 si pas défini", min_value=0, step=1, value=2)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Enregistrer / Ajouter"):
                if not name:
                    st.error("Le nom est requis.")
                else:
                    # essayer de voir si l'item existe -> update sinon insert
                    cursor.execute("SELECT id FROM garden_items WHERE name = ?", (name.strip(),))
                    row = cursor.fetchone()
                    if row:
                        item_id = row[0]
                        cursor.execute(
                            """UPDATE garden_items SET category=?, quantity=?, unit=?, planting_date=?, harvest_date=?, watering_frequency_days=?
                               WHERE id = ?""",
                            (category, quantity, unit, planting_date.isoformat(), harvest_date.isoformat(), int(watering_freq), item_id)
                        )
                        conn.commit()
                        st.success(f"{name} mis(e) à jour dans le jardin.")
                    else:
                        cursor.execute(
                            """INSERT INTO garden_items (name, category, quantity, unit, planting_date, harvest_date, watering_frequency_days)
                               VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (name.strip(), category, quantity, unit, planting_date.isoformat(), harvest_date.isoformat(), int(watering_freq))
                        )
                        conn.commit()
                        st.success(f"{name} ajouté(e) au jardin 🌱")
                    # si une fréquence d'arrosage est fournie, créer un rappel initial
                    if watering_freq and watering_freq > 0:
                        cursor.execute("SELECT id FROM garden_items WHERE name = ?", (name.strip(),))
                        iid = cursor.fetchone()[0]
                        next_date = (datetime.combine(planting_date, datetime.min.time()) + timedelta(days=watering_freq)).date().isoformat()
                        cursor.execute(
                            """INSERT INTO garden_reminders (item_id, reminder_type, scheduled_date, status)
                               VALUES (?, ?, ?, ?)""",
                            (iid, "arrosage", next_date, "pending")
                        )
                        conn.commit()
                        st.info(f"Rappel d'arrosage initial planifié le {next_date} pour {name}.")
        with col2:
            if st.button("❌ Supprimer (nom exact requis)"):
                if not name:
                    st.error("Indique le nom exact de l'élément à supprimer.")
                else:
                    cursor.execute("DELETE FROM garden_items WHERE name = ?", (name.strip(),))
                    conn.commit()
                    st.success(f"{name} supprimé du jardin (si existant).")

    # -----------------------
    # Récupération et affichage principal (conserve l'existant)
    # -----------------------
    df = pd.read_sql("SELECT id, name, category, quantity, unit, planting_date, harvest_date, watering_frequency_days FROM garden_items", conn)

    if df.empty:
        st.info("Aucune donnée enregistrée dans le jardin.")
    else:
        st.subheader("Inventaire du jardin")
        st.dataframe(df)

        # Export existant (conservé)
        if st.button("📦 Exporter les données du jardin"):
            csv = df.to_csv(index=False)
            st.download_button("Télécharger CSV", csv, "jardin.csv", "text/csv")

    # -----------------------
    # Générer les alertes / rappels pour aujourd'hui
    # -----------------------
    st.markdown("### 🔔 À faire aujourd'hui")
    today = date.today().isoformat()

    # s'assurer que la table reminders existe et récupérer les rappels à date
    reminders = pd.read_sql("SELECT r.id, r.item_id, r.reminder_type, r.scheduled_date, r.status, g.name FROM garden_reminders r LEFT JOIN garden_items g ON r.item_id = g.id WHERE r.status = 'pending' ORDER BY r.scheduled_date ASC", conn)
    due = reminders[reminders["scheduled_date"] <= today] if not reminders.empty else pd.DataFrame()

    if not due.empty:
        for _, row in due.iterrows():
            item_id = int(row["item_id"])
            name = row["name"] or "—"
            r_type = row["reminder_type"]
            sched = row["scheduled_date"]
            col_a, col_b = st.columns([3,1])
            with col_a:
                st.markdown(f"- **{name}** — {r_type} (prévu le {sched})")
            with col_b:
                if st.button(f"✅ Fait ({name} {r_type})", key=f"done_{row['id']}"):
                    # log action
                    cursor.execute(
                        "INSERT INTO garden_logs (item_id, action, date, notes) VALUES (?, ?, ?, ?)",
                        (item_id, r_type, datetime.now().isoformat(), f"Action marquée comme faite via UI")
                    )
                    cursor.execute("UPDATE garden_reminders SET status = 'done' WHERE id = ?", (row["id"],))
                    # si arrosage, replanifier suivant frequency
                    if r_type == "arrosage":
                        cursor.execute("SELECT watering_frequency_days FROM garden_items WHERE id = ?", (item_id,))
                        freq_row = cursor.fetchone()
                        if freq_row and freq_row[0]:
                            next_dt = (datetime.strptime(sched, "%Y-%m-%d") + timedelta(days=int(freq_row[0]))).date().isoformat()
                            cursor.execute(
                                "INSERT INTO garden_reminders (item_id, reminder_type, scheduled_date, status) VALUES (?, ?, ?, ?)",
                                (item_id, "arrosage", next_dt, "pending")
                            )
                    conn.commit()
                    st.experimental_rerun()
    else:
        st.info("Aucun rappel urgent pour aujourd'hui.")

    # -----------------------
    # Historique et stats (conservés / extensibles)
    # -----------------------
    st.markdown("---")
    st.subheader("Historique des actions")
    df_logs = pd.read_sql("SELECT l.id, g.name as item_name, l.action, l.date, l.notes FROM garden_logs l LEFT JOIN garden_items g ON l.item_id = g.id ORDER BY l.date DESC LIMIT 200", conn)
    if df_logs.empty:
        st.info("Aucun historique disponible.")
    else:
        st.dataframe(df_logs)

    # Statistiques simples
    st.markdown("### 📊 Statistiques")
    total_items = len(df) if not df.empty else 0
    total_logs = len(df_logs) if not df_logs.empty else 0
    st.write(f"Plantes / éléments suivis : **{total_items}**")
    st.write(f"Actions enregistrées : **{total_logs}**")

    # Export combiné : items + reminders + logs
    if st.button("📥 Export combiné (items + reminders + logs)"):
        df_rem = pd.read_sql("SELECT r.id, g.name as item, r.reminder_type, r.scheduled_date, r.status FROM garden_reminders r LEFT JOIN garden_items g ON r.item_id = g.id", conn)
        csv_all = "-- items --\n" + df.to_csv(index=False) + "\n\n-- reminders --\n" + df_rem.to_csv(index=False) + "\n\n-- logs --\n" + df_logs.to_csv(index=False)
        st.download_button("Télécharger CSV combiné", csv_all, "jardin_combine.csv", "text/csv")

    conn.close()
