from fhir.resources.R4B.address import Address
from fhir.resources.R4B.reference import Reference
from rest_framework.test import APIClient
from django.urls import reverse


class FHIROrganizationSource:
    """
    Adapter that makes Organization and EhrVendor look the same to serializers
    """

    def __init__(self, *, organization=None, ehr_vendor=None):
        self.organization = organization
        self.ehr_vendor = ehr_vendor

        if not (organization or ehr_vendor):
            raise ValueError("Must provide organization or ehr_vendor")

    @property
    def id(self):
        if self.organization:
            return self.organization.id
        return self.ehr_vendor.id

    @property
    def parent_id(self):
        if self.organization:
            return self.organization.parent_id
        return None

    @property
    def organizationtoname_set(self):
        if self.organization:
            return self.organization.organizationtoname_set.all()

        # Map EhrVendor.name → OrganizationToName-like dict
        return [{
            "name": self.ehr_vendor.name,
            "is_primary": True,
        }]

    @property
    def name(self):
        if self.organization:
            # primary name first, fallback to first name
            names = self.organization.organizationtoname_set.all()
            primary = next((n for n in names if n.is_primary), None)
            return (primary.name if primary else names[0].name).lower() if names else ""
        
        return self.ehr_vendor.name

    @property
    def authorized_official(self):
        return self.organization.authorized_official if self.organization else None

    @property
    def organizationtoaddress_set(self):
        return self.organization.organizationtoaddress_set.all() if self.organization else []

    @property
    def clinicalorganization(self):
        return getattr(self.organization, "clinicalorganization", None)

    # Marker so serializer can branch
    @property
    def is_ehr_vendor(self):
        return self.ehr_vendor is not None


def SmartyStreetstoFHIR(address):
    addressLine1 = f"{address.address_us.primary_number} {address.address_us.street_predirection} {address.address_us.street_name} {address.address_us.postdirection} {address.address_us.street_suffix}"
    addressLine2 = (
        f"{address.address_us.secondary_designator} {address.address_us.secondary_number}"
    )
    addressLine3 = f"{address.address_us.extra_secondary_designator} {address.address_us.extra_secondary_number}"
    cityStateZip = f"f{address.address_us.city_name}, {address.address_us.fips_state.state_abbreviation} {address.address_us.zipcode}"
    return Address(
        line=[addressLine1, addressLine2, addressLine3, cityStateZip],
        use=address.address_type.value,
    )


def get_schema_data(request, url_name, additional_args=None):
    client = APIClient()
    if request.user:
        # reuse the authenticated user from the active request to make the
        # internal request to retrieve the current schema
        client.force_authenticate(user=request.user)
    schema_url = reverse(url_name, kwargs=additional_args)
    response = client.get(schema_url)
    return response.data


def genReference(url_name, identifier, request):
    reference = request.build_absolute_uri(reverse(url_name, kwargs={"pk": identifier}))
    reference = Reference(reference=reference)
    return reference


def parse_identifier_query(identifier_value):
    """
    Parse an identifier search parameter that should be in the format of "value" OR "system|value".
    Currently only supporting NPI search "NPI|123455".
    """
    if "|" in identifier_value:
        parts = identifier_value.split("|", 1)
        return (parts[0], parts[1])

    return (None, identifier_value)
