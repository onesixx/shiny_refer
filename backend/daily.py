import argparse
import pandas as pd
from datetime import datetime
from rose import DATA_DIR
import os
import duckdb

from rose.log import setup_logging
setup_logging('app_backend.log')
from rose.log import logger
logger.info("Backend Start")

import time

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--from', dest='FROM', required=True) #, type=int, default=0, help='cpu usage')
args = parser.parse_args()

argFROM = args.FROM
# argFROM = '20240901' #args.FROM
date_str = datetime.strptime(argFROM, '%Y%m%d')

FROM = date_str.strftime('%Y-%m-%d')
# to_date = from_date + pd.DateOffset(days=1)
# TO = to_date.strftime('%Y-%m-%d')

df = pd.read_csv('initial/sample_log.csv')
df_dt = df[ df['date'] ==FROM ]

AREA_LIST = df['area_id'].unique()
DATA_PROCESSED_DIR = DATA_DIR.joinpath('process').resolve()
for area in AREA_LIST:
    area_dir = DATA_PROCESSED_DIR.joinpath(area)
    os.makedirs(area_dir, exist_ok=True)

# create data for each area
for area in AREA_LIST:
    print(area)
    filter_dt = df_dt[ df_dt['area_id'] == area ]
    filter_dt.to_parquet(DATA_PROCESSED_DIR.joinpath(area, f'dt_{date_str}.parquet'), index=False)

conn = duckdb.connect('buda.db')
conn.excute("""
    INSERT INTO daily(date, name, saved)
    VALUES ('{FROM}', 'Daily', True)
    ON CONFLICT (date, name)
    DO UPDATE SET saved = excluded.saved;
""")
conn.close()