import pandas as pd
import requests
import uuid
import numpy as np
# dbHelpers import createEngine

# 'https://lantern.healthit.gov/api/organizations/v1'
org_to_endpoint_url = '/Users/pr0i/Downloads/fhir_endpoint_organizations.csv'
# 'https://lantern.healthit.gov/api/daily/download'
endpoint_url = '/Users/pr0i/Downloads/fhir_endpoints.csv'


def loadSampleEndpointInfo(url):
    lantern_df = pd.read_csv(url)

    org_lists = lantern_df['list_source'].unique()

    done_lists = []
    endpoints = []
    organizations = []
    errors = []
    i = 0
    for item in org_lists:
        if item not in done_lists:
            if 1 == 1:
                try:
                    resp = requests.get(
                        item, verify='/Users/Shared/ca-certificates/ca-bundle.pem', timeout=60).json()
                    resp_entry = resp['entry']
                    if type(resp['entry']) != list:
                        resp_entry = list(resp_entry)
                    organizations += [{**entry['resource'], 'source': item}
                                      for entry in resp_entry if entry['resource']['resourceType'] == 'Organization']
                    endpoints += [{**entry['resource'], 'source': item}
                                  for entry in resp_entry if entry['resource']['resourceType'] == 'Endpoint']
                except Exception as e:
                    errors.append({'source': item, 'error': e})
                    print(e)
            done_lists.append(item)
        i += 1
        print(i)
    endpoint_df = pd.DataFrame(endpoints)
    endpoint_df['identifier'] = [{'system': endpoint_df.iloc[i]['source'], 'value': endpoint_df.iloc[i]
                                  ['id'], 'assigner': '<reference to EHR vendor>'} for i in endpoint_df.index]
    endpoint_df['id'] = [str(uuid.uuid4()) for i in endpoint_df.index]

    sampled_endpoints = endpoint_df.sample(n=1000, axis=0)
    sampled_endpoints['endpoint_connection_type_id'] = sampled_endpoints['connectionType'].apply(
        lambda x: x['code'] if type(x) == dict else np.nan)

    payloads = []
    for i, row in sampled_endpoints.iterrows():
        for payload in row['payloadType']:
            if 'coding' in payload.keys():
                payloads.append(
                    {'endpoint_instance_id': row['id'], 'payload_type_id': payload['coding'][0]['code']})
    payload_df = pd.DataFrame(payloads)

    api_devs = lantern_df[['certified_api_developer_name']].drop_duplicates()
    api_devs['id'] = [str(uuid.uuid4()) for i in api_devs.index]
    api_devs = api_devs.rename(
        columns={'certified_api_developer_name': 'name'})
    list_to_dev = {row['list_source']: api_devs.loc[api_devs['name'] == row['certified_api_developer_name']]['id'].iloc[0]
                   for i, row in lantern_df[['certified_api_developer_name', 'list_source']].drop_duplicates().iterrows()}

    identifiers = []
    for i, row in sampled_endpoints.iterrows():
        idents = row['identifier']
        if type(idents) != list:
            idents = [idents]
        for ident in idents:
            identifiers.append({'endpoint_instance_id': row['id'], 'other_id': ident['value'],
                               'system': row['source'], 'issuer_id': list_to_dev[row['source']]})
    identifiers_df = pd.DataFrame(identifiers)
    # engine = createEngine()

    api_devs.to_sql('ehr_vendor', if_exists='append',
                    index=False, schema='npd', con=engine)

    sampled_endpoints['environment_type_id'] = 'prod'
    sampled_endpoints['ehr_vendor_id'] = sampled_endpoints['source'].apply(
        lambda x: list_to_dev[x])
    sampled_endpoints.to_csv('endpoint_details.csv')
    # sampled_endpoints[['id', 'ehr_vendor_id', 'address', 'endpoint_connection_type_id', 'name']].to_sql('endpoint_instance', if_exists='append', index=False, schema='npd', con=engine)

    # payload_df.loc[payload_df['payload_type_id'].apply(lambda x: x not in ['NA', 'hl7-fhir-rest', 'Endpoint', 'CapabilityStatement'])].to_sql('endpoint_instance_to_payload', if_exists='append', index=False, schema='npd', con=engine)

    # identifiers_df.to_sql('endpoint_instance_to_other_id', if_exists='append', index=False, schema='npd', con=engine)


loadSampleEndpointInfo(endpoint_url)


def getOrgToEndpoint(url):
    # TODO
    download_url = url
    lantern_df = pd.read_csv(download_url)
    npis_df = lantern_df.loc[lantern_df['identifier_type'].apply(
        lambda x: 'npi' in str(x).lower())]
    npis_df['identifier_type'] = npis_df['identifier_type'].str.split('\n')
    npis_df['identifier_value'] = npis_df['identifier_value'].str.split('\n')
    normalized_ids = npis_df.explode(['identifier_type', 'identifier_value'])
    normalized_npis = normalized_ids.loc[normalized_ids['identifier_type'].str.lower(
    ) == 'npi']
    normalized_npis['fhir_endpoint_url'] = normalized_npis['fhir_endpoint_url'].str.split(
        '\n')
    normalized_endpoints = normalized_npis.explode('fhir_endpoint_url')
    normalized_endpoints.to_csv('endpoint_list.csv')


getOrgToEndpoint(org_to_endpoint_url)
