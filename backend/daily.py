import os
import time
from datetime import datetime
import argparse

from rose.log import setup_logging
from rose.log import logger
from rose import DATA_DIR, BACKEND_DIR

import pandas as pd
import duckdb

setup_logging('app_backend.log')
logger.info("Backend Start")

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--from', dest='FROM_str', required=True)
args = parser.parse_args()

argFROM = args.FROM_str
# argFROM = '20240901'
FROM_date = datetime.strptime(argFROM, '%Y%m%d') # datetime(2024, 9, 1, 0, 0)
FROM_str = FROM_date.strftime('%Y-%m-%d') # '2024-09-01'
FROM_str_flat = FROM_date.strftime('%Y%m%d') # '20240901'

df = pd.read_csv(BACKEND_DIR.joinpath('initial','sample_log.csv'))
dt_detail = df[ df['date'] == FROM_str ]

# dt_compact = dt_detail.groupby(['area_id', 'date', 'machine_id']).mean().reset_index()
agg_dict = {
    'load_cnt': 'sum',
    'duration': 'mean',
    'assign':   'mean',
    'acquire':  'mean',
    'deposit':  'mean'
}
dt_compact = dt_detail.groupby(['area_id', 'date', 'machine_id']).agg(agg_dict).reset_index()


AREA_LIST = df['area_id'].unique()
DATA_PROCESSED_DIR = DATA_DIR.joinpath('process').resolve()

# create directory for each area
for area in AREA_LIST:
    area_dir = DATA_PROCESSED_DIR.joinpath(area)
    os.makedirs(area_dir, exist_ok=True)

# create data for each area
for area in AREA_LIST:
    print(area)
    filter_dt_compact = dt_compact[dt_compact['area_id'] == area]
    filter_dt_detail = dt_detail[ dt_detail['area_id'] == area]

    filter_dt_compact.to_parquet(DATA_PROCESSED_DIR.joinpath(area, f'dt_compact_{FROM_str_flat}.parquet'), index=False)
    filter_dt_detail.to_parquet(DATA_PROCESSED_DIR.joinpath(area, f'dt_detail_{FROM_str_flat}.parquet'), index=False)

conn = duckdb.connect(str(DATA_DIR.joinpath("db/buda.db")), read_only=False)
conn.execute(f"""
    INSERT INTO daily(date, name, saved)
    VALUES ('{FROM_str}', 'Daily', True)
    ON CONFLICT (date, name)
    DO UPDATE SET saved = excluded.saved;
""")
conn.close()
