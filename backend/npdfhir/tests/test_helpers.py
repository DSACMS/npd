from django.db import connection


# Database query helpers
def get_female_npis(npi_list):
    """
    Given a list of NPI numbers, return the subset that are female.
    """
    query = """
        SELECT p.npi, i.gender
        FROM npd.provider p
        JOIN npd.individual i ON p.individual_id = i.id
        WHERE p.npi = ANY(%s)
          AND i.gender = 'F'
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [npi_list])
        results = cursor.fetchall()

    return results

# FHIR response assertion helpers
def assert_fhir_response(test_case, response, expected_status=200):
    """
    Helper to assert common FHIR response properties.
    """
    test_case.assertEqual(response.status_code, expected_status)
    test_case.assertEqual(response["Content-Type"], "application/fhir+json")

def assert_has_results(test_case, response):
    """
    Helper to assert response has results key.
    """
    test_case.assertIn("results", response.data)

def assert_fhir_bundle_structure(test_case, response):
    """
    Helper to assert response is a valid FHIR bundle with entries.
    """
    assert_fhir_response(test_case, response)
    bundle = response.data["results"]
    test_case.assertIn("entry", bundle)
    return bundle

def assert_pagination_limit(test_case, response, max_size=100):
    """
    Helper to assert pagination doesn't exceed maximum.
    """
    bundle = response.data["results"]
    test_case.assertLessEqual(len(bundle["entry"]), max_size)

# Data extraction helpers
def extract_resource_names(response):
    """
    Extract names from FHIR bundle entries.
    """
    return [
        d['resource'].get('name', {})
        for d in response.data["results"]["entry"]
    ]

def extract_practitioner_names(response):
    """
    Extract practitioner names (family, given) from FHIR bundle entries.
    """
    return [
        (d['resource']['name'][-1].get('family', {}),
         d['resource']['name'][-1]['given'][0])
        for d in response.data["results"]["entry"]
    ]

def extract_resource_ids(response):
    """
    Extract IDs from FHIR bundle entries.
    """
    return [
        d['resource'].get('id', {})
        for d in response.data["results"]["entry"]
    ]
