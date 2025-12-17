from django.urls import reverse
from fhir.resources.R4B.bundle import Bundle
from rest_framework import status

from .api_test_case import APITestCase
from .fixtures import create_endpoint, create_organization
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_resource_names,
)


class EndpointViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.search_org_name = "Searchable"
        cls.searchable_org = create_organization(name=cls.search_org_name)

        cls.endpoints = [
            create_endpoint(name="88 MEDICINE LLC", organization=cls.searchable_org),
            create_endpoint(name="AAIA of Tampa Bay, LLC"),
            create_endpoint(name="ABC Healthcare Service Base URL"),
            create_endpoint(name="A Better Way LLC"),
            create_endpoint(name="Abington Surgical Center"),
            create_endpoint(name="Access Mental Health Agency"),
            create_endpoint(name="Abington Center Surgical"),
            create_endpoint(name="ADHD & Autism Psychological Services PLLC"),
            create_endpoint(name="Adolfo C FernandezObregon Md"),
            create_endpoint(name="Advanced Anesthesia, LLC"),
            create_endpoint(name="Advanced Cardiovascular Center"),
            create_endpoint(name="Kansas City Psychiatric Group"),
        ]

        return super().setUpTestData()

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
            "Abington Center Surgical",
            "Abington Surgical Center",
            "Access Mental Health Agency",
            "ADHD & Autism Psychological Services PLLC",
            "Adolfo C FernandezObregon Md",
            "Advanced Anesthesia, LLC",
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
        id = self.endpoints[0].endpoint_instance.id
        url = reverse("fhir-endpoint-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(id))

    def test_filter_by_organization_name(self):
        response = self.client.get(
            self.list_url,
            {"organization": self.search_org_name},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bundle = response.data["results"]
        entries = bundle.get("entry", [])

        self.assertGreater(len(entries), 0)

        result_ids = [entry["resource"]["id"] for entry in entries]

        self.assertIn(str(self.endpoints[0].endpoint_instance.id), result_ids)

    def test_filter_by_organization_id(self):
        response = self.client.get(
            self.list_url,
            {"organization_id": self.searchable_org.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bundle = response.data["results"]
        entries = bundle.get("entry", [])

        self.assertGreater(len(entries), 0)

        result_ids = [entry["resource"]["id"] for entry in entries]

        self.assertIn(str(self.endpoints[0].endpoint_instance.id), result_ids)
