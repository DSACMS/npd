from django.urls import reverse
from rest_framework import status
from .api_test_case import APITestCase
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_practitioner_names,
    get_female_npis
)

from .fixtures import create_practitioner


class PractitionerViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.prac1 = create_practitioner(last_name='AADALEN', first_name='KIRK')
        cls.prac2 = create_practitioner(last_name='ABBAS', first_name='ASAD')
        cls.prac3 = create_practitioner(last_name='ABBOTT', first_name='BRUCE')
        cls.prac4 = create_practitioner(last_name='ABBOTT', first_name='PHILIP')
        cls.prac5 = create_practitioner(last_name='ABDELHALIM', first_name='AHMED')
        cls.prac6 = create_practitioner(last_name='ABDELHAMED', first_name='ABDELHAMED')
        cls.prac7 = create_practitioner(last_name='ABDEL NOUR', first_name='MAGDY')
        cls.prac8 = create_practitioner(last_name='ABEL', first_name='MICHAEL')
        cls.prac9 = create_practitioner(last_name='ABELES', first_name='JENNIFER')
        cls.prac10 = create_practitioner(last_name='ABELSON', first_name='MARK')

        cls.prac11 = create_practitioner(last_name='CUTLER', first_name='A')
        cls.prac12 = create_practitioner(last_name='NIZAM', first_name='A')
        cls.prac13 = create_practitioner(last_name='SALAIS', first_name='A')
        cls.prac14 = create_practitioner(last_name='JANOS', first_name='AARON')
        cls.prac15 = create_practitioner(last_name='NOONBERG', first_name='AARON')
        cls.prac16 = create_practitioner(last_name='PITNEY', first_name='AARON')
        cls.prac17 = create_practitioner(last_name='SOLOMON', first_name='AARON')
        cls.prac18 = create_practitioner(last_name='STEIN', first_name='AARON')
        cls.prac19 = create_practitioner(last_name='ALI', first_name='ABBAS')
        cls.prac20 = create_practitioner(last_name='JAFRI', first_name='ABBAS')

        cls.prac21 = create_practitioner(last_name='ZWERLING', first_name='HAYWARD')
        cls.prac22 = create_practitioner(last_name='ZUROSKE', first_name='GLEN')
        cls.prac23 = create_practitioner(last_name='ZUCKERBERG', first_name='EDWARD')
        cls.prac24 = create_practitioner(last_name='ZUCKER', first_name='WILLIAM')
        cls.prac25 = create_practitioner(last_name='ZUCCALA', first_name='SCOTT')
        cls.prac26 = create_practitioner(last_name='ZOVE', first_name='DANIEL')
        cls.prac27 = create_practitioner(last_name='ZORN', first_name='GUNNAR')
        cls.prac28 = create_practitioner(last_name='ZOOG', first_name='EUGENE')
        cls.prac29 = create_practitioner(last_name='ZOLMAN', first_name='MARK')
        cls.prac30 = create_practitioner(last_name='ZOLLER', first_name='DAVID')

        return super().setUpTestData()

    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-practitioner-list")  # /Practitioner/
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

    # Sorting tests
    def test_list_in_default_order(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # print(response.data["results"]["entry"][0]['resource']['name'][0])

        # for name in response.data["results"]["entry"]:
        #    print(name['resource']['name'][-1])

        # Extract names
        names = extract_practitioner_names(response)

        sorted_names = [
            ('AADALEN', 'KIRK'),
            ('ABBAS', 'ASAD'),
            ('ABBOTT', 'BRUCE'),
            ('ABBOTT', 'PHILIP'),
            ('ABDELHALIM', 'AHMED'),
            ('ABDELHAMED', 'ABDELHAMED'),
            ('ABDEL NOUR', 'MAGDY'),
            ('ABEL', 'MICHAEL'),
            ('ABELES', 'JENNIFER'),
            ('ABELSON', 'MARK')
        ]

        self.assertEqual(
            names, sorted_names, f"Expected fhir practitioners sorted by family then first name but got {names}\n Sorted: {sorted_names}")

    def test_list_in_alternate_order(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url,  {"_sort": 'primary_first_name,primary_last_name'})
        assert_fhir_response(self, response)

        # print(response.data["results"]["entry"][0]['resource']['name'][0])

        # for name in response.data["results"]["entry"]:
        #    print(name['resource']['name'][-1])

        # Extract names
        names = extract_practitioner_names(response)

        sorted_names = [
            ('CUTLER', 'A'),
            ('NIZAM', 'A'),
            ('SALAIS', 'A'),
            ('JANOS', 'AARON'),
            ('NOONBERG', 'AARON'),
            ('PITNEY', 'AARON'),
            ('SOLOMON', 'AARON'),
            ('STEIN', 'AARON'),
            ('ALI', 'ABBAS'),
            ('JAFRI', 'ABBAS')
        ]

        self.assertEqual(
            names, sorted_names, f"Expected fhir practitioners sorted by first then family name but got {names}\n Sorted: {sorted_names}")

    def test_list_in_descending_order(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url,  {"_sort": '-primary_last_name,-primary_first_name'})
        assert_fhir_response(self, response)

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_practitioner_names(response)

        sorted_names = [
            ('ZWERLING', 'HAYWARD'),
            ('ZUROSKE', 'GLEN'),
            ('ZUCKERBERG', 'EDWARD'),
            ('ZUCKER', 'WILLIAM'),
            ('ZUCCALA', 'SCOTT'),
            ('ZOVE', 'DANIEL'),
            ('ZORN', 'GUNNAR'),
            ('ZOOG', 'EUGENE'),
            ('ZOLMAN', 'MARK'),
            ('ZOLLER', 'DAVID')
        ]

        self.assertEqual(
            names, sorted_names, f"Expected fhir practitioners sorted by family then first name in descending but got {names}\n Sorted: {sorted_names}")
    
    # Pagination tests
    def test_list_with_custom_page_size(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 2)

    def test_list_with_greater_than_max_page_size(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"page_size": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_pagination_limit(self, response)

    # Basic Filter tests
    def test_list_filter_by_gender(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"gender": "Male"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert all required fields are present to get npi id
        assert_has_results(self, response)
        self.assertIn("entry", response.data['results'])

        npi_ids = []
        for practitioner_entry in response.data['results']['entry']:
            self.assertIn("resource", practitioner_entry)
            self.assertIn("id", practitioner_entry['resource'])
            npi_id = practitioner_entry['resource']['id']
            npi_ids.append(int(npi_id))

        # Check to make sure no female practitioners were fetched by mistake
        should_be_empty = get_female_npis(npi_ids)
        self.assertFalse(should_be_empty)

    def test_list_filter_by_name(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"name": "Smith"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_practitioner_type(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"practitioner_type": "Nurse"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    # Identifiers Filter tests
    def test_list_filter_by_npi_general(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"identifier": "1234567890"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_npi_specific(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"identifier": "NPI|1234567890"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    # Address Filter tests
    def test_list_filter_by_address(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"address": "Street"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_address_city(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"address_city": "Springfield"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_address_state(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"address_state": "CA"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_address_postalcode(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"address_postalcode": "12345"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_address_use(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"address_use": "home"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    # Retrieve tests
    def test_retrieve_nonexistent(self):
        url = reverse("fhir-practitioner-detail", args=['999999'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_uuid(self):
        url = reverse("fhir-practitioner-detail",
                      args=["12300000-0000-0000-0000-000000000123"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_pracitioner(self):
        id = self.prac1.individual.id
        url = reverse("fhir-practitioner-detail",
                      args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(id))
