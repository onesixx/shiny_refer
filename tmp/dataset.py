from pydataset import data


for datasetNm in data().dataset_id[:5]:
    df = data(f'{datasetNm}')
    print(df.dtypes)


# Initialize a list to hold dataset names with date columns
datasets_with_date_columns = []

for datasetNm in data().dataset_id:
    df = data(f'{datasetNm}')
    # Check if any column in the dataframe is of datetime type
    if any(df.dtypes == 'bool'):
        datasets_with_date_columns.append(datasetNm)

# Print the names of datasets that have date columns
print(datasets_with_date_columns)


dataset_list = ['DoctorContacts', 'Treatment', 'ca2006', 'iraqVote', 'presidentialElections', 'nwtco', 'mastectomy', 'Mammals']
datasets_with_date_columns = []

for datasetNm in dataset_list:
    df = data(f'{datasetNm}')
    print(f"datasetNm: {datasetNm}\n")
    print(df)


    # Check if any column in the dataframe is of datetime type
    if any(df.dtypes == 'bool'):
        datasets_with_date_columns.append(datasetNm)

# Print the names of datasets that have date columns
print(datasets_with_date_columns)


import seaborn as sns
dataset_list=sns.get_dataset_names()


import pandas as pd
from pydataset import data

# Example dataset names for demonstration
dataset_list = ['AirPassengers', 'co2', 'UKgas', 'USAccDeaths', 'discoveries']

# Initialize a list to hold dataset names with date columns
datasets_with_date_columns = []

for datasetNm in dataset_list:
    df = data(datasetNm)
    # Check if any column in the dataframe is of datetime type
    if any(df.dtypes == 'datetime64[ns]'):
        datasets_with_date_columns.append(datasetNm)

# Print the names of datasets that have date columns
print(datasets_with_date_columns)



