from pathlib import Path
from datetime import datetime
import os
import base64
import json
import zipfile as zf
import shutil
import logging

logger = logging.getLogger(__name__)

class DaylioPickup:
    """class designed for picking up backup data, decoding it, and saving it as json

    Raises:
        FileNotFoundError: 
        FileNotFoundError: 

    Returns:
        : 
    """
    
    expected_cwd: str = "MoodDashboard"
    
    def __init__(self, pickup_dir: str = Path.home() / "OneDrive/DaylioData"):
        logger.info("Checking CWD is set to MoodDashboard")
        self.__set_cwd()
        
        self.pickup_dir = pickup_dir
        self.pickup_path = self.__find_backup_file()
        
        self.data_dir = Path.cwd() / "data"
        self.json_path = self.data_dir / "daylio.json"
        
        selected_tables_path = self.data_dir / "tables_needed.txt"
        self.selected_tables = [table.strip() for table in selected_tables_path.read_text().split('\n')]
    
    def __set_cwd(self):
        if Path.cwd().name != self.expected_cwd:
            logger.info("CWD not 'MoodDashboard' searching for correct directory...")
            for folder in Path.home().rglob(self.expected_cwd):
                if folder.is_dir() and folder.name == self.expected_cwd:
                    logger.info("'MoodDashboard' directory found, changing working directory")
                    os.chdir(str(folder))
                    break
            else:
                logger.error("'MoodDashboard' does not exist on this system")
                raise FileNotFoundError(f'{self.expected_cwd} does not exist')
    
    def __find_backup_file(self):
        pickup_path = Path(self.pickup_dir, datetime.today().strftime('backup_%Y_%m_%d.daylio'))
        logger.info(f"Searching for todays backup file: {pickup_path.name}")
        if pickup_path.exists():
            logger.info('File found')
            return pickup_path
        else:
            logger.error(f"{pickup_path.name} does not exist in designated pickup directory: {self.pickup_dir}")
            raise FileNotFoundError(f"{pickup_path} does not exist")
    
    def extract_backup(self):
        logger.info("Extracting zipped data from backup file into data directory")
        with zf.ZipFile(self.pickup_path, 'r') as zr:
            zr.extractall(self.data_dir)
            # remove assets folder from extraction, it is not needed
            shutil.rmtree((self.data_dir / "assets"))
            
    
    def decode_backup_to_json(self):
        backup_path = self.data_dir / "backup.daylio"
        logger.info('Decoding backup from base64 to utf-8')
        with open(str(backup_path), 'r') as backup:
            contents = base64.b64decode(backup.read()).decode("utf-8")
            
        data = json.loads(contents)
        
        return data
    
    def save_to_json(self, daylio_data):
        selected_tables_data = {table: daylio_data[table] for table in self.selected_tables}
        if self.json_path.exists():
            os.remove(self.json_path)
        logger.info(f'Saving decoded data as json: {self.json_path}')
        with open(str(self.json_path), "w", encoding='utf-8') as j:
            json.dump(selected_tables_data, j, indent=4)
    
    def archive_json(self):
        
        date_str = datetime.today().strftime('%Y%m%d_%H%M')
        archive_path = self.data_dir / "archive" / f"daylio_{date_str}.json"
        logger.info(f"Creating archive copy of todays json file: {archive_path.name}")
        shutil.copy(self.json_path, archive_path)