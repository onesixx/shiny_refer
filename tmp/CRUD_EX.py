import duckdb
duckdb.sql("SELECT 42").show()

r1 = duckdb.sql("SELECT 42 AS i")
duckdb.sql("SELECT i*2 AS k FROM r1").show()

import duckdb
import pandas as pd
import pydataset as ds
# ["coal", "nuclear", "Journals", "cabbages", "AustralianElectionPolling", "Bundesliga"]

# Create a connection to DuckDB
conn = duckdb.connect('a_database.db')  # in-memory database
conn.execute("SHOW TABLES").fetchdf()
# conn.colse()
# C 
# 테이블 생성
conn.execute('''
CREATE TABLE daily(
    date DATE,
    name VARCHAR,
    saved BOOLEAN,
    UNIQUE(date, name)
);
''')

# 데이터 삽입
conn.execute('''
INSERT INTO daily (date, name, saved) VALUES
('2024-05-04', 'Daily', True),
('2024-05-05', 'Daily', False);
''')
###### R
# 데이터 조회
result0= conn.query('SELECT * FROM daily').to_df()       # prepare query & excute DataFrame
result1= conn.execute('SELECT * FROM daily').fetchdf()   # excutes & fetch DataFrame
result2= conn.execute('SELECT * FROM daily').fetchall()  # list of tuples

###### U 
# 데이터 갱신
conn.execute('''
UPDATE daily
SET saved = False
WHERE date = '2024-05-04';
''')

conn.execute('''
INSERT INTO daily (date, name, saved)
VALUES ('2024-05-04', 'Daily', TRUE)
ON CONFLICT (date, name)
DO UPDATE SET saved = excluded.saved;
''')

# insert Dataframe
data = {
    'date': ['2024-05-06', '2024-05-07'],
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

for index, row in df.iterrows():
    conn.execute('''
    INSERT INTO daily (date, name, saved)
    VALUES (?, ?, ?)
    ON CONFLICT (date, name)
    DO UPDATE SET saved = excluded.saved;
    ''', (row['date'], row['name'], row['saved']))

###### D
conn.execute('''
DELETE FROM daily
WHERE name = 'Jane Doe';
''')

conn.execute('''
Drop TABLE daily;
''')


#--------------------------------
conn.execute("""
SELECT table_name 
FROM information_schema.tables 
WHERE table_type = 'VIEW'
""").fetchdf()


# conn = duckdb.connect(':memory:')

# conn.execute("CREATE SEQUENCE seq_personid START 1;")
# conn.execute('''
#     create table customer(
#         id integer primary key default nextval('seq_personid'),
#         name varchar,
#         email varchar,
#         age int
#     )   
# ''')

sample_dataframe = ds.data('AustralianElectionPolling')
conn.execute("select * from sample_dataframe").fetchdf()
conn.register('sample_dataframe_view', sample_dataframe)

conn.execute("CREATE TABLE my_table AS SELECT * FROM sample_dataframe_view")
conn.execute(f"select * from my_table").fetchdf()

conn.execute(f"SELECT * FROM my_table").fetchall()

def run_sql(sql):
    result = conn.execute(sql)
    return result.fetchall()
column_metadata = run_sql(f'PRAGMA table_info (my_table);')
columnNm = [col[1] for col in column_metadata]

result = conn.execute(f"SELECT * FROM my_table")
df = pd.DataFrame(result.fetchall(), columns=columnNm)

df.equals(sample_dataframe) # False
# df None , sample_dataframe NaN


df_sorted               = df.sort_values(by=df.columns.tolist()).reset_index(drop=True)
sample_dataframe_sorted = sample_dataframe.sort_values(by=sample_dataframe.columns.tolist()).reset_index(drop=True)
are_data_same = df_sorted.equals(sample_dataframe_sorted)

