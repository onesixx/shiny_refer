import time
from datetime import datetime
import argparse

import pandas as pd
import subprocess

from rose import BACKEND_DIR
from rose.log import setup_logging
from rose.log import logger

setup_logging('app_backend.log')
logger.info("Backend Batch Start")

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--from', dest='FROM_str', required=True) #, type=int, default=0, help='cpu usage')
parser.add_argument('--to', dest='TO_str', required=False, help='date like 20240819')
args = parser.parse_args()

argFROM = args.FROM_str
argTO = args.TO_str
# argFROM = '20240901' #args.FROM
# argTO = '20240902' #args.TO
FROM_date = datetime.strptime(argFROM, '%Y%m%d')
TO_date   = datetime.strptime(argTO,   '%Y%m%d')

date_range = [FROM_date + pd.DateOffset(days=i) for i in range((TO_date-FROM_date).days+1)]

for date in date_range:
    FROM_str = date.strftime('%Y%m%d')
    logger.info(f"FROM : {FROM_str}")
    pgm = BACKEND_DIR.joinpath("daily_remove.py")
    subprocess.run(['python', str(pgm), '--from', FROM_str])
    time.sleep(6)