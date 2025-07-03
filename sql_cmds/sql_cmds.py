import sqlite3
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def create_db_conn(db_path: str = "data/daylio.db") -> sqlite3.Connection:
    """
    creates a new database connection to the SQLite database
    :return:
    """
    return sqlite3.connect(db_path)

def execute_sql_command(conn: sqlite3.Connection, command: str, commit: bool = True, *args):
    with conn:
        cursor = conn.cursor()
        if args:
            cursor.execute(command, *args)
        else:
            cursor.execute(command)
            
        if commit:
            conn.commit()
        else:
            return cursor.fetchall()

def execute_sql_script(conn: sqlite3.Connection, script_path: str):
    with conn:
        script = Path(script_path)
        if not script.exists():
            logger.error(f"SQL script {script_path} does not exist.")
            return
        logger.info(f"Executing script: {script.name}")
        cursor = conn.cursor()
        script_text = script.read_text()
        cursor.executescript(script_text)
    
def read_sql_view_to_df(conn: sqlite3.Connection, view_name: str) -> pd.DataFrame:
    logger.info(f"Retrieving data from view {view_name}...")
    query = f"SELECT * FROM {view_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df