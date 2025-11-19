from django.urls import reverse
from rest_framework import status
from .test_base import APITestCase
from .test_helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_resource_ids
)


class PractitionerRoleViewSetTestCase(APITestCase):
    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)
    
    # Sorting tests
    def test_list_in_proper_order(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # Extract ids
        ids = extract_resource_ids(response)

        #Corresponds to the following location name order
        """
        A BEAUTIFUL SMILE DENTISTRY, L.L.C.
        ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC
        ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC
        ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC
        ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC
        ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC
        ADR LLC
        ADR LLC
        ADR LLC
        ADR LLC
        """
        sorted_ids = [
            'e9554c87-6e4e-4df6-93fb-88ee4bc4e5be',
            '9f50dfd8-098a-4e6d-a4ad-ded2175a5321',
            '90011f74-1c0d-4461-95b5-cb346cdbc64b',
            '874c25e0-44fd-48e9-832a-a80f1d07491a',
            '0ba12b55-05e1-450f-8a2c-454a93425a34',
            '38eac005-9373-44ab-bf5d-57b84bca7cb4',
            'cd3fe6b7-02b0-4136-8db8-4c3867aab131',
            '093091b7-aba7-4acb-8338-65996de10813',
            '2e18cd31-4a89-475b-82be-71ad75011713',
            '59ef9dd6-60e8-4a64-a52c-6f44c540184f'
        ]
        
        self.assertEqual(
            ids, sorted_ids, f"Expected Practitioner roles sorted by order of location name but got {ids}\n Sorted: {sorted_ids}")

    # Pagination tests
    def test_list_with_custom_page_size(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 2)

    def test_list_with_greater_than_max_page_size(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"page_size": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_pagination_limit(self, response)

    # Filter tests
    def test_list_filter_by_name(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"name": "Cumberland"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_practitioner_gender(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"practitioner_gender": "Female"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_organization_name(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"organization_name": "Hospital"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    # Retrieve tests
    def test_retrieve_nonexistent_uuid(self):
        url = reverse("fhir-practitionerrole-detail",
                      args=["12300000-0000-0000-0000-000000000124"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_npi(self):
        url = reverse("fhir-practitionerrole-detail", args=["999999"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_pracitionerrole(self):
        id = "3ac7bd1e-a698-4905-9731-ca650de2dcb0"
        url = reverse("fhir-practitionerrole-detail",
                      args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], id)
