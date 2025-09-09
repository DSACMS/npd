import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from pathlib import Path
import uuid
from django.test.runner import DiscoverRunner
from django.db import connection
from .cache import cacheData


class SchemaTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        old_config = super().setup_databases(**kwargs)

        # Apply unmanaged tables
        with connection.cursor() as cursor:
            cursor.execute(open("../db/sql/schemas/npd.sql").read())
            cursor.execute(open("../db/sql/inserts/sample_data.sql").read())

        return old_config


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


class BasicViewsTestCase(APITestCase):

    def test_index_view(self):
        url = reverse("index")  # maps to "/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.content.decode(),
            "Connection to npd database: successful"
        )

    def test_health_view(self):
        url = reverse("healthCheck")  # maps to "/healthCheck"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), "healthy")


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
