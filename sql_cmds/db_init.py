from datetime import datetime
import logging

from .sql_cmds import create_db_conn, execute_sql_script, Path, execute_sql_command
from .calendar_cmds import create_rolling_calendar

logger = logging.getLogger(__name__)

home_dir = Path(__file__).parent.parent
data_dir = home_dir / "data"
db_path = data_dir / "daylio.db"
sql_dir = home_dir / "sql"
create_tables_script = sql_dir / "create_tables.sql"
create_views_script = sql_dir / "create_views.sql"



def create_tables(db_conn=create_db_conn(str(db_path))):
    logger.info("Executing script to create sql tables in db")
    execute_sql_script(db_conn, str(create_tables_script))

    logger.info("Creating rolling calendar to-date and loading into sql db")
    rolling_calendar = create_rolling_calendar()

    rolling_calendar.to_sql('calendar', db_conn, if_exists="replace", index=False)
    
    db_conn.commit()
    db_conn.close()
    
def create_views(db_conn=create_db_conn(str(db_path))):
    logger.info("Executing script to create requisite views for data charting")
    execute_sql_script(db_conn, str(create_views_script))
    db_conn.commit()
    db_conn.close()
    
def insert_prefs(prefs_dict, db_conn=create_db_conn(str(db_path))):
    insert_query = '''
    INSERT INTO prefs 
    (AUTO_BACKUP_IS_ON, LAST_DAYS_IN_ROWS_NUMBER, DAYS_IN_ROW_LONGEST_CHAIN, LAST_ENTRY_CREATION_TIME) 
    VALUES (?, ?, ?, ?)
    '''
    bckup = next(filter(lambda x: x['key'] == 'AUTO_BACKUP_IS_ON', prefs_dict))['value']
    last_days_inarow = next(filter(lambda x: x['key'] == 'LAST_DAYS_IN_ROWS_NUMBER', prefs_dict))['value']
    longest_days_inarow = next(filter(lambda x: x['key'] == 'DAYS_IN_ROW_LONGEST_CHAIN', prefs_dict))['value']
    last_entry_time = next(filter(lambda x: x['key'] == 'LAST_ENTRY_CREATION_TIME', prefs_dict))['value']
    last_entry_time = datetime.fromtimestamp(last_entry_time/1000)
    
    vals = [bckup, last_days_inarow, longest_days_inarow, last_entry_time]
    
    logger.info("Creating and inserting 'prefs' table and values")
    
    execute_sql_command(db_conn, insert_query, vals)
    db_conn.commit()
    db_conn.close()
