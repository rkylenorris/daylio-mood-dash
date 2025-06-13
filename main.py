from pathlib import Path
from daylio_prep import DaylioPickup, DaylioTable, get_table_info, create_entry_tags, create_mood_groups
from sql_cmds import create_tables, create_views, insert_prefs, create_db_conn
from fitbit_sleep import get_fitbit_sleep_data, clean_sleep_data
import json
import pandas as pd
import streamlit as st
import altair as alt


def daylio_data_prep():
    from log_setup import logger
    logger.info("Starting Daylio data extraction process...")

    pickup = DaylioPickup()
    pickup.extract_backup()
    pickup.save_to_json(pickup.decode_backup_to_json())
    pickup.archive_json()

    logger.info("Daylio data extraction process completed.")

    data_dir = Path.cwd() / "data"
    daylio_data_path = data_dir / "daylio.json"
    logger.info(f"Daylio data saved to {daylio_data_path}")

    daylio_data = json.loads(daylio_data_path.read_text())
    logger.info(f"Daylio data loaded from {daylio_data_path}")

    tables = [table.strip() for table in (
        data_dir / 'tables_needed.txt').read_text().split('\n')]

    logger.info(f"Tables to be processed: {", ".join(tables)}")

    daylio_tables = []

    for table_name in tables:
        if table_name == 'prefs':
            continue
        daylio_table_df = pd.DataFrame(daylio_data[table_name])
        column_info = get_table_info(table_name)
        logger.info(
            f"Creating table {table_name} with {len(daylio_table_df)} rows and {len(column_info)} columns")
        daylio_table = DaylioTable(table_name, daylio_table_df, column_info)
        daylio_tables.append(daylio_table)
        if daylio_table.name == 'dayEntries':
            columns = get_table_info('entry_tags')
            daylio_tables.append(
                create_entry_tags(daylio_table, columns)
            )

    mood_groups_columns = get_table_info('mood_groups')
    daylio_tables.append(
        create_mood_groups(mood_groups_columns)
    )
    
    create_tables()

    for table in daylio_tables:
        with create_db_conn() as db_conn:
            table.to_sql(db_conn)
            logger.info(f"Table {table.name} written to database")
            db_conn.commit()
            

    insert_prefs(daylio_data['prefs'])


def update_fitbit_sleep():
    from log_setup import logger
    logger.info("Starting Fitbit sleep data update...")
    
    sleep_data = get_fitbit_sleep_data()
    if len(sleep_data) == 0:
        logger.warning("No Fitbit sleep data found. Skipping update.")
        return

    cleaned_sleep_data = clean_sleep_data(sleep_data)

    with create_db_conn() as db_conn:
        cleaned_sleep_data.to_sql('fitbit_sleep', db_conn, if_exists='replace', index=False)
        logger.info("Fitbit sleep data updated in database.")

    logger.info("Fitbit sleep data update completed.")


def create_streamlit_app():
    from log_setup import logger
    logger.info("Starting Streamlit app...")
    if "initialized" not in st.session_state:
        logger.info("Initializing Daylio Mood Dashboard...")
        daylio_data_prep()
        update_fitbit_sleep()
        create_views()
        logger.info("Initialization complete.")
        st.session_state["initialized"] = True

    logger.info("Generating dashboard...")
    st.title("Daylio Mood Dashboard")
    
    with create_db_conn() as db_conn:
        last_update = pd.read_sql("SELECT LAST_ENTRY_CREATION_TIME from prefs", db_conn).iloc[0, 0]
    
    st.subheader(f"Last Data Update: {last_update}")
    
    st.subheader("📈 Daily Mood Average (Last 90 Days)")
    logger.info("Loading daily mood averages from database...")
    with create_db_conn() as db_conn:
        df_avg = pd.read_sql("SELECT * FROM v_daily_avgs", db_conn)
    df_avg['day'] = pd.to_datetime(df_avg['day'])

    # Altair chart with trend line
    logger.info("Creating Altair chart for daily mood averages...")
    chart = alt.Chart(df_avg).mark_line(point=True).encode(
        x='day:T',
        y='avg_mood_value:Q'
    ).properties(
        width=700,
        height=300
    )

    trend = chart.transform_regression(
        'day', 'avg_mood_value', method='linear'
    ).mark_line(color='red', strokeDash=[4, 2])

    st.altair_chart(chart + trend, use_container_width=True)
    
    # mood entries
    if st.checkbox("Show Mood Entries"):
        logger.info("Loading mood entries from database...")
        query = "SELECT * from v_entry_details where date(day) > date('now', '-14 days') order by entry_datetime desc"
        with create_db_conn() as conn:
            df_moods = pd.read_sql(query, conn)
        
        df_moods['day'] = pd.to_datetime(df_moods['day'])
        st.subheader("📅 Mood Entries (Last 14 Days)")
        logger.info("Displaying mood entries in Streamlit table...")
        st.table(df_moods)
    

    st.subheader("🏷️ Top Activities (Interactive Drilldown)")
    logger.info("Loading activity summary from database...")
    with create_db_conn() as conn:
        df_acts = pd.read_sql("SELECT * FROM v_activity_summary", conn)

    # Altair requires no NaNs in category columns
    logger.info("Creating interactive activity drilldown...")
    df_acts = df_acts.dropna(subset=["group", "activity"])

    # Step 1: Dropdown to select group
    group_list = df_acts["group"].unique().tolist()
    selected_group = st.selectbox("Select Activity Group", group_list)

    # Step 2: Filter for that group
    filtered_df = df_acts[df_acts["group"] == selected_group]

    # Step 3: Plot
    chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X("count:Q", title="Frequency"),
        y=alt.Y("activity:N", sort="-x", title="Activity"),
        tooltip=["activity", "count"]
    ).properties(
        width=600,
        height=400,
        title=f"Top Activities in '{selected_group}' Group"
    )

    st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    create_streamlit_app()
    