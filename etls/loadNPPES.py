import zipfile
import os
from dotenv import load_dotenv
import pandas as pd
import datetime
import requests
import io
import os
import uuid
from dbHelpers import createEngine
import time
from sqlalchemy import text
import warnings

warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)
warnings.simplefilter(
    action='ignore', category=pd.errors.SettingWithCopyWarning)


# Load environment variables
load_dotenv()
working_dir = os.getenv('WORKING_DIR')

# Create database engine
engine = createEngine()

# Get NPPES CSV version
current_date = datetime.datetime.now()
current_month = current_date.strftime("%B")
current_year = current_date.year
csv_version = f'{current_month}_{current_year}_V2'

# Download and unzip the NPPES CSV files
# zipData = requests.get(f'https://download.cms.gov/nppes/NPPES_Data_Dissemination_{csv_version}.zip').content
# with zipfile.ZipFile(io.BytesIO(zipData), 'r') as zip_file:
#    zip_file.extractall(working_dir)

state_abbreviation_to_fips = {'nan': '00', 'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08', 'CT': '09', 'DE': '10', 'DC': '11', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24', 'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31',
                              'NV': '32', 'NH': '33', 'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56', 'AS': '60', 'FM': '64', 'GU': '66', 'MH': '68', 'MP': '69', 'PW': '70', 'PR': '72', 'UM': '74', 'VI': '78'}


def getFIPSCode(val):
    if val in state_abbreviation_to_fips.keys():
        return state_abbreviation_to_fips[val]
    else:
        return '00'


primary_to_bool = {'Y': True, 'N': False}


def convertBool(val):
    if val in primary_to_bool.keys():
        return primary_to_bool[val]
    else:
        return False


unzipped_files = os.listdir(working_dir)
main_file = [
    f for f in unzipped_files if 'npidata_pfile' in f and '_fileheader' not in f][0]


def loadTaxonomy(df, npitype):
    tax_list = []
    for i in range(1, 16):
        tax_columns = [f'Healthcare Provider Taxonomy Code_{i}', f'Provider License Number State Code_{i}',
                       f'Provider License Number_{i}', f'Healthcare Provider Primary Taxonomy Switch_{i}', 'npi']
        tax_df = df[tax_columns].dropna(how='all')

        tax_df[f'Provider License Number State Code_{i}'] = tax_df[f'Provider License Number State Code_{i}'].apply(
            lambda x: getFIPSCode(str(x)))
        primary_to_bool = {'Y': True, 'N': False}
        tax_df[f'Healthcare Provider Primary Taxonomy Switch_{i}'] = tax_df[f'Healthcare Provider Primary Taxonomy Switch_{i}'].apply(
            lambda x: convertBool(x))
        tax_df.rename(
            columns={
                f'Healthcare Provider Taxonomy Code_{i}': 'nucc_code',
                f'Provider License Number_{i}': 'license_number',
                f'Provider License Number State Code_{i}': 'state_id',
                f'Healthcare Provider Primary Taxonomy Switch_{i}': 'is_primary'
            }, inplace=True)
        tax_df['license_number'] = [str(l)
                                    for l in tax_df['license_number']]
        tax_list.append(tax_df)
    tax_concat = pd.concat(tax_list).sort_values(by='is_primary', ascending=False)[
        ['npi', 'nucc_code', 'is_primary']].drop_duplicates(subset='nucc_code').dropna(subset='nucc_code')
    tax_concat.to_sql(f'{npitype}_to_taxonomy',
                      con=engine, if_exists='append', schema='npd', index=False)


def loadIdentifier(df, npitype):
    identifier_list = []
    for i in range(1, 51):
        identifier_columns = [f'Other Provider Identifier_{i}', f'Other Provider Identifier Type Code_{i}',
                              f'Other Provider Identifier State_{i}', f'Other Provider Identifier Issuer_{i}', 'npi']
        identifier_df = df[identifier_columns].dropna(how='any')
        identifier_df[f'Other Provider Identifier State_{i}'] = identifier_df[f'Other Provider Identifier State_{i}'].apply(
            lambda x: getFIPSCode(str(x)))
        identifier_df[f'Other Provider Identifier Type Code_{i}'] = identifier_df[f'Other Provider Identifier Type Code_{i}'].apply(
            lambda x: int(x))
        identifier_df.rename(
            columns={
                f'Other Provider Identifier_{i}': 'other_id',
                f'Other Provider Identifier Type Code_{i}': 'other_id_type_id',
                f'Other Provider Identifier State_{i}': 'state_code',
                f'Other Provider Identifier Issuer_{i}': 'issuer'
            }, inplace=True)
        identifier_df['issuer'] = [
            str(l) for l in identifier_df['issuer']]
        identifier_df['other_id'] = [str(l)
                                     for l in identifier_df['other_id']]
        identifier_list.append(identifier_df)
    identifier_concat = pd.concat(identifier_list).drop_duplicates()
    identifier_concat.to_sql(
        f'{npitype}_to_other_id', con=engine, if_exists='append', schema='npd', index=False)


def loadNPI(df):
    npi_columns = ['NPI', 'Entity Type Code', 'Replacement NPI', 'Provider Enumeration Date', 'Last Update Date',
                   'NPI Deactivation Reason Code', 'NPI Deactivation Date', 'NPI Reactivation Date', 'Certification Date']
    npi_df = df[npi_columns].dropna(how='all')
    npi_df.rename(columns={
        'NPI': 'npi',
        'Entity Type Code': 'entity_type_code',
        'Replacement NPI': 'replacement_npi',
        'Provider Enumeration Date': 'enumeration_date',
        'Last Update Date': 'last_update_date',
        'NPI Deactivation Reason Code': 'deactivation_reason_code',
        'NPI Deactivation Date': 'deactivation_date',
        'NPI Reactivation Date': 'reactivation_date',
        'Certification Date': 'certification_date'
    }, inplace=True)
    npi_df.drop_duplicates().to_sql('npi', con=engine, index=False,
                                    if_exists='append', schema='npd')
    return npi_df


# Read in Organization data
c = 0
for chunk in pd.read_csv(os.path.join(working_dir, main_file), chunksize=10000):
    start = time.time()
    if c == 0:
        print("We're doing it")
        try:
            start = time.time()
            chunk = chunk.loc[chunk['Entity Type Code'] == 2]
            authorized_official_columns = ['Authorized Official Last Name',
                                           'Authorized Official First Name',
                                           'Authorized Official Middle Name',
                                           'Authorized Official Title or Position',
                                           'Authorized Official Telephone Number',
                                           'Authorized Official Name Prefix Text',
                                           'Authorized Official Name Suffix Text']
            ao_df = chunk[authorized_official_columns].dropna(
                how='all').drop_duplicates()
            ao_df.rename(columns={
                'Authorized Official Last Name': 'last_name',
                'Authorized Official First Name': 'first_name',
                'Authorized Official Middle Name': 'middle_name',
                'Authorized Official Telephone Number': 'phone_number',
                'Authorized Official Name Prefix Text': 'prefix',
                'Authorized Official Name Suffix Text': 'suffix'
            }, inplace=True)
            ao_df['id'] = [uuid.uuid4() for i in ao_df.index]
            ao_df['id'].to_sql('individual', con=engine,
                               index=False, if_exists='append', schema='npd')
            ao_df['individual_id'] = ao_df['id']
            ao_df['name_use_id'] = 2
            ao_df[['individual_id', 'prefix', 'first_name', 'middle_name', 'last_name', 'suffix', 'name_use_id']].to_sql('individual_to_name', con=engine,
                                                                                                                         index=False, if_exists='append', schema='npd')
            ao_df['phone_use_id'] = 2
            ao_df[['individual_id', 'phone_number', 'phone_use_id']].to_sql('individual_to_phone', con=engine,
                                                                            index=False, if_exists='append', schema='npd')
            merged_chunk = chunk.merge(ao_df[['last_name', 'first_name', 'middle_name', 'phone_number', 'prefix', 'suffix', 'individual_id']], left_on=['Authorized Official Last Name',
                                                                                                                                                        'Authorized Official First Name',
                                                                                                                                                        'Authorized Official Middle Name',
                                                                                                                                                        'Authorized Official Telephone Number',
                                                                                                                                                        'Authorized Official Name Prefix Text',
                                                                                                                                                        'Authorized Official Name Suffix Text'], right_on=['last_name', 'first_name', 'middle_name', 'phone_number', 'prefix', 'suffix'], how='left')
            merged_chunk = merged_chunk.drop_duplicates(subset='NPI')
            merged_chunk['id'] = [uuid.uuid4() for i in merged_chunk.index]
            merged_chunk['authorized_official_id'] = merged_chunk['individual_id']
            merged_chunk[['id', 'authorized_official_id']].to_sql('organization', con=engine,
                                                                  index=False, if_exists='append', schema='npd')
            npi_df = loadNPI(merged_chunk)
            merged_chunk.rename(columns={'id': 'organization_id',
                                         'NPI': 'npi',
                                         'Provider Organization Name (Legal Business Name)': 'name'}, inplace=True)
            merged_chunk[['organization_id', 'name']].to_sql('organization_to_name', con=engine,
                                                             index=False, if_exists='append', schema='npd')
            merged_chunk[['npi', 'organization_id']].drop_duplicates().to_sql(
                'clinical_organization', con=engine, index=False, if_exists='append', schema='npd')
            merged_chunk.set_index('organization_id', inplace=True)
            loadTaxonomy(merged_chunk, 'organization')
            loadIdentifier(merged_chunk, 'organization')
        except:
            print('Houston we have a problem')
            raise
        c += 1
    else:
        b+1

# Read in Practitioner data
c = 100
for chunk in pd.read_csv(os.path.join(working_dir, main_file), chunksize=10000):
    start = time.time()
    if c == 0:
        print("We're doing it")
        try:
            start = time.time()
            chunk = chunk.loc[chunk['Entity Type Code'] == 1]
            chunk['id'] = [uuid.uuid4() for i in chunk.index]
            chunk['ssn'] = None
            chunk['gender_code'] = None
            chunk['birth_date'] = None
            chunk[['ssn', 'gender_code', 'birth_date', 'id']].to_sql(
                'individual', con=engine, index=False, if_exists='append', schema='npd')
            npi_df = loadNPI(chunk)
            chunk.rename(columns={'id': 'individual_id',
                         'NPI': 'npi'}, inplace=True)
            chunk[['npi', 'individual_id']].to_sql(
                'provider', con=engine, index=False, if_exists='append', schema='npd')
            chunk.set_index('individual_id', inplace=True)
            name_fields = ['Provider Last Name (Legal Name)', 'Provider First Name',
                           'Provider Middle Name', 'Provider Name Prefix Text', 'Provider Name Suffix Text']
            name = chunk[name_fields]
            name['fhir_name_use_id'] = 1
            name.rename(columns={'Provider Last Name (Legal Name)': 'last_name',
                                 'Provider First Name': 'first_name',
                                 'Provider Middle Name': 'middle_name',
                                 'Provider Name Prefix Text': 'prefix',
                                 'Provider Name Suffix Text': 'suffix'}, inplace=True)
            name_2 = chunk[[f.replace('Provider', 'Provider Other') if 'Legal Name' not in f else 'Provider Other Last Name' for f in name_fields] + [
                'Provider Other Last Name Type Code']].dropna(how='all')
            fhir_name_type_mapping = {
                1: 6,
                2: 2,
                5: 4
            }
            name_2['Provider Other Last Name Type Code'] = name_2['Provider Other Last Name Type Code'].apply(
                lambda x: int(fhir_name_type_mapping[x]))
            name_2.rename(columns={'Provider Other Last Name': 'last_name',
                                   'Provider Other First Name': 'first_name',
                                   'Provider Other Middle Name': 'middle_name',
                                   'Provider Other Name Prefix Text': 'prefix',
                                   'Provider Other Name Suffix Text': 'suffix',
                                   'Provider Other Last Name Type Code': 'fhir_name_use_id'}, inplace=True)
            names = pd.concat([name, name_2])
            names['effective_date'] = '1900-01-01'
            names.to_sql('individual_to_name', con=engine,
                         if_exists='append', schema='npd')
            loadTaxonomy(chunk, 'provider')
            loadIdentifier(chunk, 'provider')
        except:
            print('Houston we have a problem')
            ids = tuple([str(i) for i in chunk.index])
            npis = tuple(npi_df['npi'].values)
            with engine.connect() as con:
                res = con.execute(
                    text(f'delete from ndh.individual where id in {ids}'))
                print(res)
                res2 = con.execute(
                    text(f'delete from ndh.npi where npi in {npis}'))
                print(res2)
            raise
    else:
        b+1
    c += 1
    end = time.time()
    print(f'Chunk {c} ran in {end-start} seconds')

    # We got through chunk 93
