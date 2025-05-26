from log_setup import logger
from pathlib import Path
from daylio_prep import DaylioPickup, DaylioTable, get_table_info, create_entry_tags, create_mood_groups
from sql_cmds import create_tables, create_views, insert_prefs, create_db_conn
import json
import pandas as pd
import streamlit as st
import altair as alt


def daylio_data_prep():

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

    db_conn = create_db_conn()

    create_tables()

    for table in daylio_tables:
        table.to_sql(db_conn)
        logger.info(f"Table {table.name} written to database")

    db_conn.commit()
    insert_prefs(daylio_data['prefs'], db_conn)

    create_views()


def create_streamlit_app():
    conn = create_db_conn()
    st.title("Daylio Mood Dashboard")
    
    st.subheader("📈 Daily Mood Average (Last 90 Days)")

    df_avg = pd.read_sql("SELECT * FROM v_daily_avgs", conn)
    df_avg['day'] = pd.to_datetime(df_avg['day'])

    # Altair chart with trendline
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

    # # Daily Mood Trend
    # st.subheader("📈 Daily Mood Average (Last 90 Days)")
    # df_avg = pd.read_sql("SELECT * FROM v_daily_avgs", conn)
    # df_avg['day'] = pd.to_datetime(df_avg['day'])
    # st.line_chart(df_avg.set_index("day")["avg_mood_value"])
    
    # mood entries
    st.subheader("📊 Mood Entries by Day")
    df_moods = pd.read_sql("SELECT * from v_entry_details", conn)
    df_moods['day'] = pd.to_datetime(df_moods['day'])
    st.table(df_moods.tail(15))

    # Top Activities
    st.subheader("🏷️ Top Activities")
    df_acts = pd.read_sql("SELECT * FROM v_activity_summary", conn)
    st.bar_chart(df_acts.set_index("activity")["count"])

    # Sleep Quality Trend
    st.subheader("😴 Sleep Quality Trend")
    df_sleep = pd.read_sql("SELECT * FROM v_sleep_trend", conn)
    df_sleep['day'] = pd.to_datetime(df_sleep['day'])
    pivoted = df_sleep.pivot(index='day', columns='sleep_status', values='value')
    st.line_chart(pivoted)


if __name__ == "__main__":
    daylio_data_prep()
    create_streamlit_app()
    