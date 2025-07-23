### This script loads NUCC taxonomy codes from NUCC
### NUCC codes update every 6 months, on 1/1 and 7/1

import pandas as pd
import datetime
from .dbHelpers import createEngine

# Create database engine
engine = createEngine()

# Find the current NUCC CSV version based on the current date
current_date = datetime.date.today()
current_month = current_date.month
current_year = current_date.year
if current_month > 6:
    dot_version = 1
else:
    dot_version = 0
csv_version = f'{current_year-2000}{dot_version}'

# Read the latest NUCC CSV
df = pd.read_csv(f'http://www.nucc.org/images/stories/CSV/nucc_taxonomy_{csv_version}.csv')

def unpackNUCC(df, hierarchy):
    level=1
    output=[]
    while level<len(hierarchy)+1:
        index = hierarchy[:level]
        field = hierarchy[level-1]
        subset = df[index].drop_duplicates().dropna(subset=field).reset_index(drop=True)
        subset = df[index].drop_duplicates().reset_index(drop=True)
        subset.index.name = 'id'
        swapped = subset.reset_index().set_index(index)
        if level<len(hierarchy):
            code=df[index+['Code']].loc[df[hierarchy[level]].isna()]
        else:
            code=df[index+['Code']]
        subset = pd.concat([code, subset]).drop_duplicates(index)
        subset['id'] = subset[index].apply(lambda x: swapped.loc[*x], axis = 1)
        df[field] = df[index].apply(lambda x: swapped.loc[*x], axis = 1)
        subset = subset.dropna(how='all', axis=1).rename(columns = {field: 'display_name', 'Code': 'nucc_taxonomy_code_id'}).rename(columns = {field: f'nucc_{field.lower()}_id' for field in hierarchy})
        subset = subset.dropna(subset = 'display_name')
        output.append(subset)
        level+=1
    return tuple(output)

groups, classifications, specializations = unpackNUCC(nuccDF, ['Grouping', 'Classification', 'Specialization'])

groups.to_sql('nucc_grouping', if_exists = 'append', con = engine, index=False)
classifications.to_sql('nucc_classification', if_exists = 'append', con = engine, index=False)
specializations.drop('nucc_grouping_id', axis=1).to_sql('nucc_specialization', if_exists = 'append', con = engine, index=False)

df['Grouping'].drop_duplicates()

# Find the parent elements (where there is a Classification and no Specialization)
parents = df.loc[df['Specialization'].isna()][['Code', 'Grouping', 'Classification']]
parents.set_index(['Grouping', 'Classification'], inplace=True)

# Find the parent for each row, where there is a specialization. Use the Specialization as the display name for children and the Classification as the display name for parents
df['parent_id'] = None
df['display_name'] = None
for i, row in df.iterrows():
    if not pd.isna(row['Specialization']):
        parent_index = (row['Grouping'], row['Classification'])
        try:
            df.loc[i,'parent_id'] = parents.loc[parent_index,'Code']
        except KeyError:
            pass
        df.loc[i,'display_name'] = row['Specialization']
    else:
        df.loc[i,'display_name'] = row['Classification']

# Rename the columns to match the db columns
df = df.rename(columns={'Code':'id', 'Definition':'definition', 'Notes': 'notes'})

# Load the renamed columns to the nucc_taxonomy_code table in SQL
df[['id', 'display_name', 'parent_id', 'definition', 'notes']].to_sql('nucc_taxonomy_code', schema = 'ndh', con = engine, if_exists='append', index=False)

# TODO: Make the load an upsert instead of an append