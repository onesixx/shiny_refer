from pathlib import Path
import duckdb
import pandas as pd
import numpy as np

DATA_PATH = Path(__file__).parent.parent.joinpath("dataset")
db_file = DATA_PATH.joinpath("weather.db")
csv_file = DATA_PATH.joinpath("weather_forecasts.csv")

conn = duckdb.connect(str(db_file), read_only=True)


con.execute(f"CREATE TABLE weather_csv AS SELECT * FROM read_csv_auto('{csv_file}')")
### 테이블과 csv비교 ###
con.execute("SHOW TABLES").fetchdf()
dd_duck = con.execute("SELECT * FROM weather").fetchdf()
dd_panda = pd.read_csv(csv_file)

dd_panda.equals(dd_duck) # False
# 1. 컬럼 이름 확인 및 순서 일치
dd_panda.columns.equals(dd_duck.columns)

# 2. 데이터 타입 일치
dd_panda.dtypes.equals(dd_duck.dtypes)

dtype_diff = {}
for col in dd_duck.columns:
    if dd_panda[col].dtype != dd_duck[col].dtype:
        dtype_diff[col] = (dd_panda[col].dtype, dd_duck[col].dtype)

# 3. 결측치
dd_panda.isnull().sum() #NaN
dd_duck.isnull().sum()  #NA
# dd_duck.replace("NA", np.nan, inplace=True)
