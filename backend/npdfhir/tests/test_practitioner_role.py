from django.urls import reverse
from rest_framework import status

from .api_test_case import APITestCase
from .fixtures import create_full_practitionerrole
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_resource_ids,
)


class PractitionerRoleViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # (location_name, uuid)
        cls.test_records_name = [
            "A BEAUTIFUL SMILE DENTISTRY, L.L.C.",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADR LLC",
            "ADR LLC",
            "ADR LLC",
            "ADR LLC",
        ]

        cls.roles = []

        for i, loc_name in enumerate(cls.test_records_name):
            # You can vary practitioner data a bit to avoid collisions
            first = f"Test{i}"
            last = f"Practitioner{i}"
            npi = 1000000000 + i

            role = create_full_practitionerrole(
                first_name=first,
                last_name=last,
                gender="M" if i % 2 == 0 else "F",
                npi_value=npi,
                location_name=loc_name,
                role_display="Clinician",
                role_code="MD",
            )

            cls.roles.append(role)

        cls.first_prac_id = cls.roles[0].id
        return super().setUpTestData()

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

        sorted_ids = [str(role.id) for role in self.roles]

        self.assertEqual(
            ids,
            sorted_ids,
            f"Expected Practitioner roles sorted by order of location name but got {ids}\n Sorted: {sorted_ids}",
        )

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
        url = reverse("fhir-practitionerrole-detail", args=["12300000-0000-0000-0000-000000000124"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_npi(self):
        url = reverse("fhir-practitionerrole-detail", args=["999999"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_pracitionerrole(self):
        id = self.first_prac_id
        url = reverse("fhir-practitionerrole-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(id))
