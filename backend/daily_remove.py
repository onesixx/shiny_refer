import os
import time
from datetime import datetime
import argparse
from pathlib import Path

from rose.log import setup_logging
from rose.log import logger
from rose import DATA_DIR, BACKEND_DIR

import pandas as pd
import duckdb

setup_logging('app_backend.log')
logger.info("daily remove Start")

parser = argparse.ArgumentParser(description='remove paquet.')
parser.add_argument('--from', dest='FROM_str', required=True)
args = parser.parse_args()

argFROM = args.FROM_str
# argFROM = '20240902'
FROM_date = datetime.strptime(argFROM, '%Y%m%d') # datetime(2024, 9, 1, 0, 0)

date_str = FROM_date.strftime('%Y-%m-%d') # '2024-09-01'
date_str_flat = FROM_date.strftime('%Y%m%d') # '20240901'

def removeFileInFolder(folder_path, from_str, FROM, test=False):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = Path(root)/file
            if from_str in str(file_path):
                if test:
                    print(file_path)
                else:
                    if file_path.is_file():
                        file_path.unlink()
        if test:
            print(f"FROM : {FROM}")
        else:
            conn = duckdb.connect(str(DATA_DIR.joinpath("db/buda.db")), read_only=False)
            conn.execute(f"""
                DELETE FROM daily
                WHERE date = '{FROM}';
            """)
            conn.close()

removeFileInFolder(
    DATA_DIR.joinpath('process'),
    date_str_flat,
    date_str,
    test=False
)
