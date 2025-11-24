from django.urls import reverse
from rest_framework import status
from .api_test_case import APITestCase
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_resource_names
)

from .fixtures import create_location, create_organization



class LocationViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.org1 = create_organization(name="Alpha Org")
        cls.org2 = create_organization(name="Beta Org")

        cls.loc1 = create_location(name="Main Clinic", organization=cls.org1)
        cls.loc2 = create_location(name='1ST CHOICE MEDICAL DISTRIBUTORS, LLC', organization=cls.org1)
        cls.loc3 = create_location(name='986 INFUSION PHARMACY #1 INC.', organization=cls.org2)
        cls.loc4 = create_location(name='A & A MEDICAL SUPPLY COMPANY', organization=cls.org2)
        cls.loc5 = create_location(name='ABACUS BUSINESS CORPORATION GROUP INC.', organization=cls.org1)
        cls.loc6 = create_location(name='ABBY D CENTER, INC.', organization=cls.org2)
        cls.loc7 = create_location(name='ABC DURABLE MEDICAL EQUIPMENT INC', organization=cls.org1)
        cls.loc8 = create_location(name='ABC HOME MEDICAL SUPPLY, INC.', organization=cls.org1)
        cls.loc9 = create_location(name='A BEAUTIFUL SMILE DENTISTRY, L.L.C.', organization=cls.org1)
        cls.loc10 = create_location(name='A & B HEALTH CARE, INC.', organization=cls.org1)
        cls.loc11 = create_location(name='ABILENE HELPING HANDS INC', organization=cls.org1)


        cls.loc12 = create_location(name='ZEELAND COMMUNITY HOSPITAL', organization=cls.org1)
        cls.loc13 = create_location(name='YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD', organization=cls.org1)
        cls.loc14 = create_location(name='YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD', organization=cls.org2)
        cls.loc15 = create_location(name='YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD', organization=cls.org2)
        cls.loc16 = create_location(name='YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD', organization=cls.org2)
        cls.loc17 = create_location(name='YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD', organization=cls.org2)
        cls.loc18 = create_location(name='YOUNG C. BAE, M.D.')
        cls.loc19 = create_location(name='YORKTOWN EMERGENCY MEDICAL SERVICE')
        cls.loc20 = create_location(name='YODORINCMISSIONPLAZAPHARMACY', organization=cls.org1)
        cls.loc21 = create_location(name='YOAKUM COMMUNITY HOSPITAL', organization=cls.org1)

        cls.loc22 = create_location(name='FROEDTERT MEMORIAL LUTHERAN HOSPITAL, INC.', organization=cls.org2)
        cls.loc23 = create_location(name='AMBER ENTERPRISES INC.', organization=cls.org1)
        cls.loc24 = create_location(name='COUNTY OF KOOCHICHING', organization=cls.org1)
        cls.loc25 = create_location(name='OCEAN HOME HEALTH SUPPLY, LLC', organization=cls.org1)
        cls.loc26 = create_location(name='PULMONARY MANAGEMENT, INC.', organization=cls.org1)
        cls.loc27 = create_location(name='MEDICATION MANAGEMENT CENTER, LLC.', organization=cls.org2)
        cls.loc28 = create_location(name='HENDRICKS COUNTY HOSPITAL', organization=cls.org2)
        cls.loc29 = create_location(name='BAY AREA REHABILITATION MEDICAL GROUP', organization=cls.org2)
        cls.loc30 = create_location(name='PROHAB REHABILITATION SERVICES, INC.', organization=cls.org2)

        return super().setUpTestData()


    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

    # Sorting tests
    def test_list_in_default_order(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # print(response.data["results"]["entry"][0]['resource']['name'])

        # Extract names
        names = extract_resource_names(response)

        sorted_names = [
            '1ST CHOICE MEDICAL DISTRIBUTORS, LLC',
            '986 INFUSION PHARMACY #1 INC.',
            'A & A MEDICAL SUPPLY COMPANY',
            'ABACUS BUSINESS CORPORATION GROUP INC.',
            'ABBY D CENTER, INC.',
            'ABC DURABLE MEDICAL EQUIPMENT INC',
            'ABC HOME MEDICAL SUPPLY, INC.',
            'A BEAUTIFUL SMILE DENTISTRY, L.L.C.',
            'A & B HEALTH CARE, INC.',
            'ABILENE HELPING HANDS INC'
        ]

        self.assertEqual(
            names, sorted_names, f"Expected fhir locations sorted by name but got {names}\n Sorted: {sorted_names}")

    def test_list_in_descending_order(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url,  {"_sort": '-name'})
        assert_fhir_response(self, response)

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_resource_names(response)

        sorted_names = [
            'ZEELAND COMMUNITY HOSPITAL',
            'YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD',
            'YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD',
            'YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD',
            'YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD',
            'YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD',
            'YOUNG C. BAE, M.D.',
            'YORKTOWN EMERGENCY MEDICAL SERVICE',
            'YODORINCMISSIONPLAZAPHARMACY',
            'YOAKUM COMMUNITY HOSPITAL'
        ]

        self.assertEqual(
            names, sorted_names, f"Expected locations list sorted by name in descending but got {names}\n Sorted: {sorted_names}")

    def test_list_in_order_by_address(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url,  {"_sort": 'address_full'})
        assert_fhir_response(self, response)

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_resource_names(response)

        #Names correspond to following addresses
        #10000 W Bluemound Rd, Wauwatosa, WI 53226
        #10004 S 152nd St, Omaha, NE 68138
        #1000 5th St, International Falls, MN 56649
        #1000 Airport Rd, Lakewood, NJ 8701
        #1000 E Center St, Kingsport, TN 37660
        #1000 E Main St, Danville, IN 46122
        #1000 Greenley Rd, Sonora, CA 95370
        #1000 Regency Ct, Toledo, OH 43623


        sorted_names = [
            'OCEAN HOME HEALTH SUPPLY, LLC',
            'COUNTY OF KOOCHICHING',
            'AMBER ENTERPRISES INC.',
            'YOAKUM COMMUNITY HOSPITAL',
            'YODORINCMISSIONPLAZAPHARMACY',
            'YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD',
            'ZEELAND COMMUNITY HOSPITAL',
            'ABILENE HELPING HANDS INC',
            'A & B HEALTH CARE, INC.',
            'PULMONARY MANAGEMENT, INC.'
        ]

        self.assertEqual(
            names, sorted_names, f"Expected locations list sorted by address ascending but got {names}\n Sorted: {sorted_names}")

    # Pagination tests
    def test_list_with_custom_page_size(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 2)

    def test_list_with_greater_than_max_page_size(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"page_size": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_pagination_limit(self, response)

    # Filter tests
    def test_list_filter_by_name(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"name": "Cumberland"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_address(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address": "Avenue"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_address_city(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address_city": "Seattle"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_address_state(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address_state": "TX"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_address_postalcode(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address_postalcode": "90210"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    def test_list_filter_by_address_use(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address_use": "work"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

    # Retrieve tests
    def test_retrieve_nonexistent(self):
        url = reverse("fhir-location-detail",
                      args=['00000000-0000-0000-0000-000000000000'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_location(self):
        id = self.loc1.id
        url = reverse("fhir-location-detail",
                      args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(id))
