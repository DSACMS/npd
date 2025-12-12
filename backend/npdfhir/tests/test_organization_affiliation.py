import uuid

from django.urls import reverse
from rest_framework import status
from ..models import Organization, OtherIdType, Nucc, EhrVendor, LocationToEndpointInstance, EndpointInstance
from .api_test_case import APITestCase
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_resource_names,
)

from .fixtures import create_organization, create_legal_entity, create_location, create_endpoint


class OrganizationAffiliationViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Creates a mix of organizations:
        - Some that SHOULD match the query
        - Some that SHOULD NOT match the query
        """

        # -----------------------------
        # Reference data
        # -----------------------------
        legal_entity = create_legal_entity("Good Health EIN")
        other_id_type = OtherIdType.objects.get(value="MEDICAID")

        nucc = Nucc.objects.get(code="261Q00000X")

        ehr_vendor = EhrVendor.objects.create(
            id=uuid.uuid4(),
            name="Epic",
            is_cms_aligned_network=True,
        )

        # =========================================================
        # ✅ MATCHING ORGANIZATION #1 (FULLY QUALIFIED)
        # =========================================================
        org_good_1 = create_organization(
            name="Good Clinical Org 1",
            legal_entity=legal_entity,
            other_id_type=other_id_type,
            organization_type=nucc.code,
        )

        loc_good_1 = create_location(
            organization=org_good_1,
            name="Good Location 1",
        )

        endpoint_good_1 = create_endpoint(
            organization=org_good_1,
            name="Good Endpoint 1",
            ehr=ehr_vendor,
        )

        LocationToEndpointInstance.objects.create(
            location=loc_good_1,
            endpoint_instance=endpoint_good_1.endpoint_instance,
        )

        # =========================================================
        # ✅ MATCHING ORGANIZATION #2 (MULTIPLE LOCATIONS / ENDPOINTS)
        # =========================================================
        org_good_2 = create_organization(
            name="Good Clinical Org 2",
            legal_entity=legal_entity,
        )

        loc_good_2a = create_location(organization=org_good_2, name="Location A")
        loc_good_2b = create_location(organization=org_good_2, name="Location B")

        endpoint_good_2a = create_endpoint(
            organization=org_good_2,
            name="Endpoint A",
            ehr=ehr_vendor,
        )

        endpoint_good_2b = create_endpoint(
            organization=org_good_2,
            name="Endpoint B",
            ehr=ehr_vendor,
        )

        LocationToEndpointInstance.objects.create(
            location=loc_good_2a,
            endpoint_instance=endpoint_good_2a.endpoint_instance,
        )
        LocationToEndpointInstance.objects.create(
            location=loc_good_2b,
            endpoint_instance=endpoint_good_2b.endpoint_instance,
        )

        # =========================================================
        # ❌ NON-MATCHING #1 — NO LOCATION
        # =========================================================
        create_organization(
            name="No Location Org",
            legal_entity=legal_entity,
        )

        # =========================================================
        # ❌ NON-MATCHING #2 — LOCATION BUT NO ENDPOINT
        # =========================================================
        org_no_endpoint = create_organization(name="No Endpoint Org")
        create_location(organization=org_no_endpoint)


        # =========================================================
        # ❌ NON-MATCHING #4 — ENDPOINT NOT LINKED TO LOCATION
        # =========================================================
        org_unlinked = create_organization(name="Unlinked Endpoint Org")
        create_location(organization=org_unlinked)

        create_endpoint(
            organization=org_unlinked,
            name="Dangling Endpoint",
            ehr=ehr_vendor,
        )

        return super().setUpTestData()

    def setUp(self):
        super().setUp()
        self.org_without_authorized_official = Organization.objects.create(
            id="26708690-19d6-499e-b481-cebe05b98f08", authorized_official_id=None
        )

    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

        print(response.data)
