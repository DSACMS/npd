import math

from django.urls import reverse
from rest_framework import status

from geopy.distance import geodesic

from .api_test_case import APITestCase
from .fixtures.practitioner import create_full_practitionerrole
from .fixtures.location import create_location
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    # extract_resource_ids,
)


class PractitionerRoleViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # (location_name, uuid)
        cls.orgs = [
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
        cls.locations = [
            create_location(
                id="3719c831-a4b7-4a7f-bb47-465a024384fc",
                name="ABACUS BUSINESS CORPORATION GROUP INC.",
                organization_name=cls.orgs[0],
                city="San Diego",
                state="CA",
                zipcode="55555",
                addr_line_1="404 Great Amazing Avenue",
                x=32.824056,
                y=-117.437397,
            ),
            create_location(
                id="7c7a433b-fca7-4fb2-9283-dc764fb0ed5c",
                name="ABBY D CENTER, INC.",
                organization_name=cls.orgs[1],
                city="Seattle",
                state="WA",
                zipcode="77777",
                addr_line_1="333 Grunge Blvd.",
                address_use="home",
                x=47.608597,
                y=-122.5046021,
            ),
            create_location(
                id="6df24407-ebe0-4f0b-9a75-bdfee486f0df",
                name="ABC DURABLE MEDICAL EQUIPMENT INC",
                organization_name=cls.orgs[0],
                city="St. Louis",
                state="MO",
                zipcode="89898",
                addr_line_1="66 Arch Lane",
                x=38.6219297,
                y=-90.182935,
            ),
            create_location(
                id="c1fc1ada-841a-4b92-9e8e-37f4d17b65d4",
                name="ABC HOME MEDICAL SUPPLY, INC.",
                organization_name=cls.orgs[0],
                city="St. Louis",
                state="MO",
                zipcode="65313",
                addr_line_1="City Museum Rd.",
                x=38.6336745,
                y=-90.2032725,
            ),
            create_location(
                id="b7517cc7-b406-4932-9856-6983ac4ec308",
                name="A BEAUTIFUL SMILE DENTISTRY, L.L.C.",
                organization_name=cls.orgs[0],
                city="Ft. Lauderdale",
                state="FL",
                zipcode="43433",
                addr_line_1="789 Palmetto Road",
                x=26.1412097,
                y=-80.1910040,
            ),
        ]

        locs = cls.locations + cls.locations
        cls.roles = []

        for i, loc_name in enumerate(cls.orgs):
            # You can vary practitioner data a bit to avoid collisions
            first = f"Test{i}"
            last = f"Practitioner{i}"
            npi = 1000000000 + i

            location = locs[i]

            role = create_full_practitionerrole(
                first_name=first,
                last_name=last,
                gender="M" if i % 2 == 0 else "F",
                npi_value=npi,
                location_id=location.id,
                org_name=cls.orgs[math.floor(i / 2)],
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
    """def test_list_in_proper_order(self):
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
        )"""

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
        response = self.client.get(url, {"organization_name": "MEDICAL"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_filter_by_distance_with_km(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 3
        units = "km"
        near_query = f"{lat}|{lon}|{distance}|{units}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]
        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            position = (
                returned_location["position"]["longitude"],
                returned_location["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).km, distance)

    def test_filter_by_distance_with_mi(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 1
        units = "mi"
        near_query = f"{lat}|{lon}|{distance}|{units}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            position = (
                returned_location["position"]["longitude"],
                returned_location["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).miles, distance)

    def test_filter_by_distance_with_ft(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 5000
        units = "ft"
        near_query = f"{lat}|{lon}|{distance}|{units}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            position = (
                returned_location["position"]["longitude"],
                returned_location["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).feet, distance)

    def test_filter_by_distance_witout_units(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 3
        near_query = f"{lat}|{lon}|{distance}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            position = (
                returned_location["position"]["longitude"],
                returned_location["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).km, distance)

    def test_filter_by_distance_none_nearby(self):
        lat = 64
        lon = 12
        distance = 30.5
        units = "km"
        near_query = f"{lon}|{lat}|{distance}|{units}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]["entry"]), 0)

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
