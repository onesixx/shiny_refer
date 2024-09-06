"""
this script is for creating a database and tables, inserting data, and reading data.
"""
import sys
from pathlib import Path
import pandas as pd

import pydataset as ds
import duckdb
from rose import DATA_DIR

### ------  Append the project root directory to sys.path ------
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
#=================================================================

conn = duckdb.connect(str(DATA_DIR.joinpath("db/buda.db")), read_only=False)
conn.execute("""
    CREATE TABLE daily(date DATE, name VARCHAR, saved BOOLEAN, UNIQUE(date, name));
""")
conn.query("""
    SELECT * FROM daily ORDER BY date;
""").to_df()
conn.close()

#=================================================================
### ------ Create database of DuckDB ------
db_file = DATA_DIR.joinpath("db/job.db")
# db_file = DATA_DIR.joinpath("db/csv.db")
conn = duckdb.connect(str(db_file), read_only=False)
conn.execute("SHOW TABLES").fetchdf()

### ------ create table ------
C_SQL = '''
CREATE TABLE daily(
    date DATE,
    name VARCHAR,
    saved BOOLEAN
    UNIQUE(date, name)
);
'''
conn.execute(C_SQL)

# create table with df
df = ds.data('AustralianElectionPolling')
conn.register('polling', df)


# insert data
I_SQL = """
INSERT INTO daily (date, name, saved) VALUES
('2024-05-04', 'Daily', True),
('2024-05-05', 'Daily', False),
('2024-05-06', 'Daily', True),
"""
conn.execute(I_SQL)

I2_SQL = """
INSERT INTO daily (date, name, saved)
VALUES ('2024-05-06', 'Daily', TRUE)
ON CONFLICT (date, name)
DO UPDATE SET saved = excluded.saved;
"""
conn.execute(I2_SQL)

data = {
    'date': ['2024-05-07', '2024-05-08'],
    'name': ['Daily', 'Daily'],
    'saved': [True, False]
}
df = pd.DataFrame(data)
for index, row in df.iterrows():
    query = f'''
    INSERT INTO daily (date, name, saved)
    VALUES ('{row['date']}', '{row['name']}', {row['saved']})
    ON CONFLICT (date, name)
    DO UPDATE SET saved = excluded.saved;
    '''
    conn.execute(query)

# read data
R_SQL = 'SELECT * FROM daily'
conn.query(R_SQL).to_df()       # prepare query & excute DataFrame
conn.execute(R_SQL).fetchdf()   # excutes & fetch DataFrame
conn.execute(R_SQL).fetchall()  # list of tuples

# update data
U_SQL = '''
UPDATE daily
SET saved = False
WHERE date = '2024-05-07';
'''
conn.execute(U_SQL)

# delete data
D_SQL = '''
DELETE FROM daily
WHERE date = '2024-05-08';
'''
conn.execute(D_SQL)

# conn.execute('''
# Drop TABLE daily;
# ''')

conn.close()
# --------------------------------------------

# def load_csv(con, csv_name, table_name):
#     csv_url = f"https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-12-20/{csv_name}.csv"
#     local_file_path = DATA_DIR.joinpath(f"{csv_name}.csv")
#     urllib.request.urlretrieve(csv_url, local_file_path)
#     con.sql(
#         f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{local_file_path}')"
#     )

# if not Path.exists(db_file):
#     con = duckdb.connect(str(db_file), read_only=False)
#     load_csv(con, "weather_forecasts", "weather")
#     load_csv(con, "cities", "cities")
#     con.close()

# con = duckdb.connect(str(db_file), read_only=True)

# --------------------------------------------
