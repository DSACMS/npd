from fhir.resources.R4B.address import Address
from fhir.resources.R4B.reference import Reference
from rest_framework.test import APIClient
from django.urls import reverse
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.types import OpenApiTypes

def SmartyStreetstoFHIR(address):
    addressLine1 = f"{address.address_us.primary_number} {address.address_us.street_predirection} {address.address_us.street_name} {address.address_us.postdirection} {address.address_us.street_suffix}"
    addressLine2 = f"{address.address_us.secondary_designator} {address.address_us.secondary_number}"
    addressLine3 = f"{address.address_us.extra_secondary_designator} {address.address_us.extra_secondary_number}"
    cityStateZip = f"f{address.address_us.city_name}, {address.address_us.fips_state.state_abbreviation} {address.address_us.zipcode}"
    return Address(
        line=[addressLine1, addressLine2, addressLine3, cityStateZip],
        use=address.address_type.value
    )

def get_schema_data(url_name):
    client = APIClient()
    schema_url = reverse(url_name)
    response = client.get(schema_url)
    return response.data

def genReference(url_name, identifier, request):
    reference = request.build_absolute_uri(
        reverse(url_name, kwargs={'pk': identifier}))
    reference = Reference(
        reference=reference)
    return reference

def parse_identifier_query(identifier_value):
    """
    Parse an identifier search parameter that should be in the format of "value" OR "system|value".
    Currently only supporting NPI search "NPI|123455".
    """
    if '|' in identifier_value:
        parts = identifier_value.split('|', 1)
        return (parts[0], parts[1])

    return (None, identifier_value)

def generate_filter_parameters(filterset_class):
    parameters = []
    mappings = getattr(filterset_class, 'filter_mappings', {})

    # Implement page related parameters
    parameters.extend([
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            description='Page number for pagination'
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            description='Number of results per page (max 100)'
        ),
    ])
    
    # Get declared filters from the FilterSet
    for filter_name, filter_field in filterset_class.declared_filters.items():
        help_text = getattr(filter_field, 'help_text', None) or f'Filter by {filter_name}'
        
        enum_values = None
        if filter_name in mappings:
            enum_values = list(mappings[filter_name].keys('fhir'))
        
        param = OpenApiParameter(
            name=filter_name,
            type=OpenApiTypes.STR,
            description=help_text,
            enum=enum_values
        )
        parameters.append(param)
    
    return parameters