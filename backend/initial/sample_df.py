import pandas as pd
import numpy as np

N = 1000

area_range = ['Area_A', 'Area_B', 'Area_C', 'Area_D']
random_area_ids = np.random.choice(area_range, size=N, replace=True)

date_range = pd.date_range(start='2024-09-01', end='2024-09-30', freq='d')
random_dates = np.random.choice(date_range, size=N, replace=True)

machine_ids = [f'Machine_{i}' for i in range(1, 6)]
random_machine_ids = np.random.choice(machine_ids, size=N, replace=True)

load_cnt = np.random.randint(1, 100, size=N)

start_times = pd.to_datetime(np.random.randint(0, 24*60*60, size=N), unit='s').time
end_times   = pd.to_datetime(np.random.randint(0, 24*60*60, size=N), unit='s').time
for i in range(N):
    if end_times[i] <= start_times[i]:
        end_times[i] = (pd.to_datetime(start_times[i].strftime('%H:%M:%S')) + pd.Timedelta(minutes=np.random.randint(1, 60))).time()

# 데이터프레임 생성
df = pd.DataFrame({
    'area_id': random_area_ids,
    'date': random_dates,
    'machine_id': random_machine_ids,
    'load_cnt': load_cnt,
    'start_time': start_times,
    'end_time': end_times
})

duration = pd.to_datetime(df['end_time'].astype(str)) - pd.to_datetime(df['start_time'].astype(str))
df['duration'] = duration.dt.total_seconds() / 60

ratios = np.random.dirichlet(np.ones(3), size=N)
df['assign']  = df['duration'] * ratios[:, 0]
df['acquire'] = df['duration'] * ratios[:, 1]
df['deposit'] = df['duration'] * ratios[:, 2]

df.to_csv('./sample_log.csv', index=False)