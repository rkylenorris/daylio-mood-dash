from log_setup import logger
from pathlib import Path
from daylio_prep import DaylioPickup, DaylioTable, get_table_info, create_entry_tags, create_mood_groups
from sql_cmds import create_tables, create_views, insert_prefs, create_db_conn
import json
import pandas as pd

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

tables = [table.strip() for table in (data_dir / 'tables_needed.txt').read_text().split('\n')]

logger.info(f"Tables to be processed: {", ".join(tables)}")

daylio_tables = []

for table_name in tables:
    if table_name == 'prefs':
        continue
    daylio_table_df = pd.DataFrame(daylio_data[table_name])
    column_info = get_table_info(table_name)
    logger.info(f"Creating table {table_name} with {len(daylio_table_df)} rows and {len(column_info)} columns")
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
