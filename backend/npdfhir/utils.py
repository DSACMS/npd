from fhir.resources.R4B.address import Address
from fhir.resources.R4B.reference import Reference
from rest_framework.test import APIClient
from django.urls import reverse

def SmartyStreetstoFHIR(address):
    addressLine1 = f"{address.address_us.primary_number} {address.address_us.street_predirection} {address.address_us.street_name} {address.address_us.postdirection} {address.address_us.street_suffix}"
    addressLine2 = f"{address.address_us.secondary_designator} {address.address_us.secondary_number}"
    addressLine3 = f"{address.address_us.extra_secondary_designator} {address.address_us.extra_secondary_number}"
    cityStateZip = f"f{address.address_us.city_name}, {address.address_us.fips_state.state_abbreviation} {address.address_us.zipcode}"
    return Address(
        line=[addressLine1, addressLine2, addressLine3, cityStateZip],
        use=address.address_type.value
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
    reference = request.build_absolute_uri(
        reverse(url_name, kwargs={'pk': identifier}))
    reference = Reference(
        reference=reference)
    return reference