from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.test.runner import DiscoverRunner
from django.test import TestCase
from django.db import connection
from .cache import cacheData # I can't explain why, but we need to import cacheData here. I think we can remove this once we move to the docker db setup
from fhir.resources.bundle import Bundle
from pydantic import ValidationError
from .models import Nucc, C80PracticeCodes
from .validators import NPDValueSet, NPDPractitioner
from fhir.resources.valueset import ValueSet
from fhir.resources.practitioner import Practitioner



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


class EndpointViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("fhir-endpoint-list")

    def test_list_default(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/fhir+json")
        self.assertIn("results", response.data)
    
    def test_list_returns_fhir_bundle(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        bundle = Bundle.model_validate(data['results'])

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

    def test_pagination_custom_page_size(self):
        response = self.client.get(self.list_url, {"page_size": 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bundle = response.data["results"]
        self.assertLessEqual(len(bundle["entry"]), 2)
    
    def test_pagination_enforces_maximum(self):
        response = self.client.get(self.list_url, {"page_size": 5000})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bundle = response.data["results"]
        self.assertLessEqual(len(bundle["entry"]), 1000)

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

        code = first_endpoint["connectionType"][0]["coding"][0]["code"]
        self.assertEqual(connection_type, code)
    
    def test_filter_returns_empty_for_nonexistent_name(self):
        response = self.client.get(self.list_url, {"name": "NonexistentEndpointName12345"})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        bundle = response.data["results"]
        self.assertEqual(len(bundle["entry"]), 0)

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


class BasicViewsTestCase(APITestCase):

    def test_health_view(self):
        url = reverse("healthCheck")  # maps to "/healthCheck"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), "healthy")


class OrganizationViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_default(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/fhir+json")
        self.assertIn("results", response.data)

    def test_list_with_custom_page_size(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 2)

    def test_list_with_greater_than_max_page_size(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"page_size": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 1000)

    def test_list_filter_by_name(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"name": "Cumberland"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_list_filter_by_organization_type(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"organization_type": "Hospital"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_retrieve_nonexistent(self):
        url = reverse("fhir-organization-detail", args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PractitionerViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_default(self):
        url = reverse("fhir-practitioner-list")  # /Practitioner/
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/fhir+json")
        self.assertIn("results", response.data)

    def test_list_with_custom_page_size(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 2)

    def test_list_with_greater_than_max_page_size(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"page_size": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 1000)

    def test_list_filter_by_gender(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"gender": "Male"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert all required fields are present to get npi id
        self.assertIn("results", response.data)
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
        self.assertIn("results", response.data)

    def test_list_filter_by_practitioner_type(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"practitioner_type": "Nurse"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_retrieve_nonexistent(self):
        url = reverse("fhir-practitioner-detail", args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class NPDValueSetValidatorTests(TestCase):

    def test_verify_codes_valid(self):
        """✅ Should pass when all codes exist in the DB."""

        data = {
            "resourceType" : "ValueSet",
            "id" : "FHIR-version",
            "meta" : {
                "lastUpdated" : "2025-10-16T16:45:52.699+00:00",
                "profile" : ["http://hl7.org/fhir/StructureDefinition/shareablevalueset"]
            },
            "text" : {
                "status" : "generated",
                "div" : "<div xmlns=\"http://www.w3.org/1999/xhtml\"><p class=\"res-header-id\"><b>Generated Narrative: ValueSet FHIR-version</b></p><a name=\"FHIR-version\"> </a><a name=\"hcFHIR-version\"> </a><div style=\"display: inline-block; background-color: #d9e0e7; padding: 6px; margin: 4px; border: 1px solid #8da1b4; border-radius: 5px; line-height: 60%\"><p style=\"margin-bottom: 0px\"/><p style=\"margin-bottom: 0px\">Profile: <a href=\"shareablevalueset.html\">Shareable ValueSet</a></p></div><ul><li>Include all codes defined in <a href=\"codesystem-FHIR-version.html\"><code>http://hl7.org/fhir/FHIR-version</code></a> version <span title=\"Version is not explicitly stated, which means it is fixed to the version provided in this specification\">&#x1F4E6;6.0.0-ballot3</span></li></ul></div>"
            },
            "extension" : [{
                "url" : "http://hl7.org/fhir/StructureDefinition/structuredefinition-wg",
                "valueCode" : "fhir"
            },
            {
                "url" : "http://hl7.org/fhir/StructureDefinition/structuredefinition-standards-status",
                "valueCode" : "normative"
            },
            {
                "url" : "http://hl7.org/fhir/StructureDefinition/structuredefinition-normative-version",
                "valueCode" : "4.0.0"
            },
            {
                "url" : "http://hl7.org/fhir/StructureDefinition/structuredefinition-fmm",
                "valueInteger" : 5
            }],
            "url" : "http://hl7.org/fhir/ValueSet/FHIR-version",
            "identifier" : [{
                "system" : "urn:ietf:rfc:3986",
                "value" : "urn:oid:2.16.840.1.113883.4.642.3.1309"
            }],
            "version" : "6.0.0-ballot3",
            "name" : "FHIRVersion",
            "title" : "FHIRVersion",
            "status" : "active",
            "experimental" : False,
            "date" : "2025-10-16T16:45:52+00:00",
            "publisher" : "HL7 International / FHIR Infrastructure",
            "contact" : [{
                "telecom" : [{
                "system" : "url",
                "value" : "http://www.hl7.org/Special/committees/fiwg"
                }]
            }],
            "description" : "All published FHIR Versions.",
            "jurisdiction" : [{
                "coding" : [{
                "system" : "http://unstats.un.org/unsd/methods/m49/m49.htm",
                "code" : "001",
                "display" : "World"
                }]
            }],
            "immutable" : True,
            "compose": {
                "include": [
                    {
                        "system": "http://nucc.org/provider-taxonomy",
                        "concept": [{"code": "101Y00000X"}],
                    },
                    {
                        "system": "http://snomed.info/sct",
                        "concept": [{"code": "419772000"}],
                    },
                ]
            },
        }

        model = NPDValueSet(**data)

        self.assertIsInstance(model, ValueSet)

    def test_verify_codes_invalid(self):
        """🚫 Should raise ValueError when a code is not found."""
        data = {
            "resourceType": "ValueSet",
            "compose": {
                "include": [
                    {
                        "system": "http://nucc.org/provider-taxonomy",
                        "concept": [{"code": "BAD_CODE"}],
                    }
                ]
            },
        }

        with self.assertRaises(ValidationError) as ctx:
            NPDValueSet(**data)