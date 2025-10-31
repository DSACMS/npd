from fhir.resources.R4B.address import Address
from fhir.resources.R4B.reference import Reference
from rest_framework.test import APIClient
from django.urls import reverse
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django_filters import filters

def SmartyStreetstoFHIR(address):
    addressLine1 = f"{address.address_us.primary_number} {address.address_us.street_predirection} {address.address_us.street_name} {address.address_us.postdirection} {address.address_us.street_suffix}"
    addressLine2 = f"{address.address_us.secondary_designator} {address.address_us.secondary_number}"
    addressLine3 = f"{address.address_us.extra_secondary_designator} {address.address_us.extra_secondary_number}"
    cityStateZip = f"f{address.address_us.city_name}, {address.address_us.fips_state.state_abbreviation} {address.address_us.zipcode}"
    return Address(
        line=[addressLine1, addressLine2, addressLine3, cityStateZip],
        use=address.address_type.value
    )

def get_schema_data(url_name, additional_args=None):
    client = APIClient()
    schema_url = reverse(url_name, kwargs=additional_args)
    response = client.get(schema_url)
    return response.data

def genReference(url_name, identifier, request):
    reference = request.build_absolute_uri(
        reverse(url_name, kwargs={'pk': identifier}))
    reference = Reference(
        reference=reference)
    return reference

def parse_identifier(identifier_value):
    """
    Parse an identifier search parameter that should be in the format of "value" OR "system|value".
    Currently only supporting NPI search "NPI|123455".
    """
    if '|' in identifier_value:
        parts = identifier_value.split('|', 1)
        return (parts[0], parts[1])

    return (None, identifier_value)

def get_filter_parameters(filterset_class):
    parameters = []
    filterset = filterset_class()
    
    for field_name, filter_field in filterset.filters.items():
        param = OpenApiParameter(
            name=field_name,
            type=get_openapi_type(filter_field),
            location=OpenApiParameter.QUERY,
            description=filter_field.extra.get('help_text', ''),
            required=filter_field.extra.get('required', False),
            enum=get_choices(filter_field),
        )
        parameters.append(param)
    
    return parameters

def get_openapi_type(filter_field):
    type_map = {
        filters.CharFilter: OpenApiTypes.STR,
        filters.BooleanFilter: OpenApiTypes.BOOL,
        filters.NumberFilter: OpenApiTypes.NUMBER,
        filters.DateFilter: OpenApiTypes.DATE,
        filters.DateTimeFilter: OpenApiTypes.DATETIME,
        filters.UUIDFilter: OpenApiTypes.UUID,
        filters.ChoiceFilter: OpenApiTypes.STR,
    }
    
    for filter_class, api_type in type_map.items():
        if isinstance(filter_field, filter_class):
            return api_type

def get_choices(filter_field):
    choices = filter_field.extra.get('choices')
    if choices:
        return [choice[0] for choice in choices]
    return None
