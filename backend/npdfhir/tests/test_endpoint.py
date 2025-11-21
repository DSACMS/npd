from django.urls import reverse
from rest_framework import status
from fhir.resources.R4B.bundle import Bundle
from .api_test_case import APITestCase
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_resource_names,
)


class EndpointViewSetTestCase(APITestCase):
    # Basic tests
    def setUp(self):
        super().setUp()
        self.list_url = reverse("fhir-endpoint-list")

    def test_list_default(self):
        response = self.client.get(self.list_url)

        assert_fhir_response(self, response)
        assert_has_results(self, response)

    # Sorting tests
    def test_list_in_default_order(self):
        url = self.list_url
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # print(response.data["results"]["entry"][0]['resource']['name'])

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_resource_names(response)

        sorted_names = [
            "88 MEDICINE LLC",
            "AAIA of Tampa Bay, LLC",
            "ABC Healthcare Service Base URL",
            "A Better Way LLC",
            "Abington Surgical Center",
            "Access Mental Health Agency",
            "ADHD & Autism Psychological Services PLLC",
            "Adolfo C FernandezObregon Md",
            "Advanced Anesthesia, LLC",
            "Advanced Cardiovascular Center",
        ]

        self.assertEqual(
            names,
            sorted_names,
            f"Expected endpoints list sorted by name but got {names}\n Sorted: {sorted_names}",
        )

    # Bundle Validation tests
    def test_list_returns_fhir_bundle(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        bundle = Bundle.model_validate(data["results"])

        self.assertEqual(bundle.__resource_type__, "Bundle")

    def test_list_entries_are_fhir_endpoints(self):
        response = self.client.get(self.list_url)

        bundle = response.data["results"]
        self.assertGreater(len(bundle["entry"]), 0)

        first_entry = bundle["entry"][0]
        self.assertIn("resource", first_entry)

        endpoint_resource = first_entry["resource"]
        self.assertEqual(endpoint_resource["resourceType"], "Endpoint")
        self.assertIn("id", endpoint_resource)
        self.assertIn("status", endpoint_resource)
        self.assertIn("connectionType", endpoint_resource)
        self.assertIn("address", endpoint_resource)

    # Pagination tests
    def test_pagination_custom_page_size(self):
        response = self.client.get(self.list_url, {"page_size": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bundle = response.data["results"]
        self.assertLessEqual(len(bundle["entry"]), 2)

    def test_pagination_enforces_maximum(self):
        response = self.client.get(self.list_url, {"page_size": 5000})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_pagination_limit(self, response)

    # Filter tests
    def test_filter_by_name(self):
        response = self.client.get(self.list_url, {"name": "Kansas City Psychiatric Group"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bundle = response.data["results"]

        self.assertGreater(len(bundle["entry"]), 0)

        first_endpoint = bundle["entry"][0]["resource"]

        self.assertIn("name", first_endpoint)
        self.assertIn("Kansas City", first_endpoint["name"])

    def test_filter_by_connection_type(self):
        connection_type = "hl7-fhir-rest"
        response = self.client.get(self.list_url, {"endpoint_connection_type": connection_type})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bundle = response.data["results"]

        entries = bundle.get("entry", [])
        self.assertGreater(len(entries), 0)

        first_endpoint = entries[0]["resource"]
        self.assertIn("connectionType", first_endpoint)

        code = first_endpoint["connectionType"]["code"]
        self.assertEqual(connection_type, code)

    def test_filter_by_payload_type(self):
        payload_type = "ccda-structuredBody:1.1"
        response = self.client.get(self.list_url, {"payload_type": payload_type})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bundle = response.data["results"]

        entries = bundle.get("entry", [])
        self.assertGreater(len(entries), 0)

        first_endpoint = entries[0]["resource"]
        self.assertIn("payloadType", first_endpoint)

        code = first_endpoint["payloadType"][0]["coding"][0]["display"]
        self.assertEqual(payload_type, code)

    def test_filter_returns_empty_for_nonexistent_name(self):
        response = self.client.get(self.list_url, {"name": "NonexistentEndpointName12345"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bundle = response.data["results"]
        self.assertEqual(len(bundle["entry"]), 0)

    # Retrieve tests
    def test_retrieve_specific_endpoint(self):
        list_response = self.client.get(self.list_url, {"page_size": 1})
        first_endpoint = list_response.data["results"]["entry"][0]["resource"]

        endpoint_id = first_endpoint["id"]
        detail_url = reverse("fhir-endpoint-detail", args=[endpoint_id])

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        endpoint = response.data
        self.assertEqual(endpoint["resourceType"], "Endpoint")
        self.assertEqual(endpoint["id"], endpoint_id)
        self.assertIn("status", endpoint)
        self.assertIn("connectionType", endpoint)
        self.assertIn("address", endpoint)

    def test_retrieve_nonexistent_endpoint(self):
        detail_url = reverse("fhir-endpoint-detail", args=["12300000-0000-0000-0000-000000000123"])
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_endpoint(self):
        id = "82cc98bb-afd0-4835-ada9-1437dfca8255"
        url = reverse("fhir-endpoint-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], id)
