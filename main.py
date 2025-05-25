from log_setup import logger
from pathlib import Path
from daylio_prep import DaylioPickup


logger.info("Starting Daylio data extraction process...")

pickup = DaylioPickup()
pickup.extract_backup()
pickup.save_to_json(pickup.decode_backup_to_json())
pickup.archive_json()
logger.info("Daylio data extraction process completed.")
