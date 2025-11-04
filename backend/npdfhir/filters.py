from django_filters import rest_framework as filters
from django.contrib.postgres.search import SearchVector
from django.db.models import Q

from .mappings import addressUseMapping, genderMapping
from .utils import parse_identifier
from .models import (
    EndpointInstance,
    ProviderToLocation,
    Organization,
    Provider,
    Location
)

class EndpointFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Filter by name'
    )
    
    connection_type=filters.CharFilter(
        field_name='endpoint_connection_type__id',
        lookup_expr='icontains',
        help_text='Filter by connection type'
    )

    payload_type=filters.CharFilter(
        field_name='endpointinstancetopayload__payload_type__id',
        lookup_expr='icontains',
        help_text='Filter by payload type'
    )

    status=filters.CharFilter(
        method='filter_status',
        help_text='Filter by status'
    )

    organization=filters.CharFilter(
        method='filter_organization',
        help_text='Filter by organization'
    )

    class Meta:
        model = EndpointInstance
        fields = ['name', 'connection_type', 'payload_type', 'status', 'organization']

    def filter_status(self, queryset, name, value):
        # needs to be implemented
        return queryset 

    def filter_organization(self, queryset, name, value):
        # needs to be implemented
        return queryset
    
class PractitionerFilterSet(filters.FilterSet):
    identifier = filters.CharFilter(
        method='filter_identifier',
        help_text='Filter by identifier (NPI or other). Format: value or system|value'
    )
    
    name = filters.CharFilter(
        method='filter_name',
        help_text='Filter by practitioner name (first, last, or full name)'
    )
    
    gender = filters.CharFilter(
        method='filter_gender',
        help_text='Filter by gender'
    )
    
    practitioner_type = filters.CharFilter(
        method='filter_practitioner_type',
        help_text='Filter by practitioner type/taxonomy'
    )
    
    address = filters.CharFilter(
        method='filter_address',
        help_text='Filter by any part of address'
    )
    
    address_city = filters.CharFilter(
        method='filter_address_city',
        help_text='Filter by city name'
    )
    
    address_state = filters.CharFilter(
        method='filter_address_state',
        help_text='Filter by state (2-letter abbreviation)'
    )
    
    address_postalcode = filters.CharFilter(
        method='filter_address_postalcode',
        help_text='Filter by postal code/zip code'
    )
    
    address_use = filters.CharFilter(
        method='filter_address_use',
        help_text='Filter by address use type'
    )

    class Meta:
        model = Provider
        fields = ['identifier', 'name', 'gender', 'practitioner_type', 
                  'address', 'address_city', 'address_state', 
                  'address_postalcode', 'address_use']

    def filter_gender(self, queryset, name, value):
        if value in genderMapping.keys():
            value = genderMapping.toNPD(value)
        
        return queryset.filter(individual__gender=value)
    
    def filter_identifier(self, queryset, name, value):
        system, identifier_id = parse_identifier(value)
        queries = Q(pk__isnull=True)

        if system:  # specific identifier search requested
            if system.upper() == 'NPI':
                try:
                    queries = Q(npi__npi=int(identifier_id))
                except (ValueError, TypeError):
                    pass
        else:  # general identifier search requested
            try:
                queries |= Q(npi__npi=int(identifier_id))
            except (ValueError, TypeError):
                pass

            queries |= Q(providertootherid__other_id=identifier_id)

        return queryset.filter(queries).distinct()

    def filter_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'individual__individualtoname__first_name',
                'individual__individualtoname__last_name',
                'individual__individualtoname__middle_name'
            )
        ).filter(search=value)

    def filter_practitioner_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector('providertotaxonomy__nucc_code__display_name')
        ).filter(search=value)

    def filter_address(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'individual__individualtoaddress__address__address_us__delivery_line_1',
                'individual__individualtoaddress__address__address_us__delivery_line_2',
                'individual__individualtoaddress__address__address_us__city_name',
                'individual__individualtoaddress__address__address_us__state_code__abbreviation',
                'individual__individualtoaddress__address__address_us__zipcode'
            )
        ).filter(search=value)

    def filter_address_city(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'individual__individualtoaddress__address__address_us__city_name'
            )
        ).filter(search=value)

    def filter_address_state(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'individual__individualtoaddress__address__address_us__state_code__abbreviation'
            )
        ).filter(search=value)

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'individual__individualtoaddress__address__address_us__zipcode'
            )
        ).filter(search=value)

    def filter_address_use(self, queryset, name, value):
        if value in addressUseMapping.keys():
            value = addressUseMapping.toNPD(value)
        else:
            value = -1
        return queryset.filter(
            individual__individualtoaddress__address_use_id=value
        )


class PractitionerRoleFilterSet(filters.FilterSet):
    practitioner_name = filters.CharFilter(
        method='filter_practitioner_name',
        help_text='Filter by practitioner name (first, last, or full name)'
    )
    
    practitioner_gender = filters.CharFilter(
        method='filter_practitioner_gender',
        help_text='Filter by practitioner gender'
    )
    
    practitioner_type = filters.CharFilter(
        method='filter_practitioner_type',
        help_text='Filter by practitioner type/taxonomy'
    )
    
    organization_name = filters.CharFilter(
        method='filter_organization_name',
        help_text='Filter by organization name'
    )

    class Meta:
        model = ProviderToLocation
        fields = ['practitioner_name', 'practitioner_gender', 
                  'practitioner_type', 'organization_name']

    def filter_practitioner_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'provider_to_organization__individual__individual__individualtoname__first_name',
                'provider_to_organization__individual__individual__individualtoname__last_name',
                'provider_to_organization__individual__individual__individualtoname__middle_name'
            )
        ).filter(search=value)

    def filter_practitioner_gender(self, queryset, name, value):
        if value in genderMapping.keys():
            gender = genderMapping.toNPD(value)
            return queryset.filter(
                provider_to_organization__individual__individual__gender=gender
            )
        return queryset

    def filter_practitioner_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector('provider_to_organization__providertotaxonomy__nucc_code__display_name')
        ).filter(search=value)

    def filter_organization_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'provider_to_organization__organization__organizationtoname__name'
            )
        ).filter(search=value)


class OrganizationFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        method='filter_name',
        help_text='Filter by organization name'
    )
    
    identifier = filters.CharFilter(
        method='filter_identifier',
        help_text='Filter by identifier (NPI, EIN, or other). Format: value or system|value'
    )
    
    organization_type = filters.CharFilter(
        method='filter_organization_type',
        help_text='Filter by organization type/taxonomy'
    )
    
    address = filters.CharFilter(
        method='filter_address',
        help_text='Filter by any part of address'
    )
    
    address_city = filters.CharFilter(
        method='filter_address_city',
        help_text='Filter by city name'
    )
    
    address_state = filters.CharFilter(
        method='filter_address_state',
        help_text='Filter by state (2-letter abbreviation)'
    )
    
    address_postalcode = filters.CharFilter(
        method='filter_address_postalcode',
        help_text='Filter by postal code/zip code'
    )
    
    address_use = filters.CharFilter(
        method='filter_address_use',
        help_text='Filter by address use type'
    )

    class Meta:
        model = Organization
        fields = ['name', 'identifier', 'organization_type', 'address', 
                  'address_city', 'address_state', 'address_postalcode', 'address_use']

    def filter_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector('organizationtoname__name')
        ).filter(search=value).distinct()

    def filter_identifier(self, queryset, name, value):
        from uuid import UUID
        
        system, identifier_id = parse_identifier(value)
        queries = Q(pk__isnull=True)

        if system: # specific identifier search requested
            if system.upper() == 'NPI':
                try:
                    queries = Q(clinicalorganization__npi__npi=int(identifier_id))
                except (ValueError, TypeError):
                    pass # TODO: implement validationerror to show users that NPI must be an int
        else: # general identifier search requested
            try:
                queries |= Q(clinicalorganization__npi__npi=int(identifier_id))
            except (ValueError, TypeError):
                pass

            try:
                UUID(identifier_id)
                queries |= Q(ein__ein_id=identifier_id)
            except (ValueError, TypeError):
                pass

            queries |= Q(clinicalorganization__organizationtootherid__other_id=identifier_id)

        return queryset.filter(queries).distinct()

    def filter_organization_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'clinicalorganization__organizationtotaxonomy__nucc_code__display_name'
            )
        ).filter(search=value)

    def filter_address(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'organizationtoaddress__address__address_us__delivery_line_1',
                'organizationtoaddress__address__address_us__delivery_line_2',
                'organizationtoaddress__address__address_us__city_name',
                'organizationtoaddress__address__address_us__state_code__abbreviation',
                'organizationtoaddress__address__address_us__zipcode'
            )
        ).filter(search=value)

    def filter_address_city(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'organizationtoaddress__address__address_us__city_name'
            )
        ).filter(search=value)

    def filter_address_state(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'organizationtoaddress__address__address_us__state_code__abbreviation'
            )
        ).filter(search=value)

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'organizationtoaddress__address__address_us__zipcode'
            )
        ).filter(search=value)

    def filter_address_use(self, queryset, name, value):
        if value in addressUseMapping.keys():
            value = addressUseMapping.toNPD(value)
        else:
            value = -1
        return queryset.filter(
            organizationtoaddress__address_use_id=value
        )


class LocationFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='exact',
        help_text='Filter by location name'
    )

    organization_type = filters.CharFilter(
        method="filter_organization_type",
        help_text="Filter by organization type"
    )
    
    address = filters.CharFilter(
        method='filter_address',
        help_text='Filter by any part of address'
    )
    
    address_city = filters.CharFilter(
        method='filter_address_city',
        help_text='Filter by city name'
    )
    
    address_state = filters.CharFilter(
        method='filter_address_state',
        help_text='Filter by state (2-letter abbreviation)'
    )
    
    address_postalcode = filters.CharFilter(
        method='filter_address_postalcode',
        help_text='Filter by postal code/zip code'
    )
    
    address_use = filters.CharFilter(
        method='filter_address_use',
        help_text='Filter by address use type'
    )

    class Meta:
        model = Location
        fields = ['name', 'address', 'address_city', 'address_state', 
                  'address_postalcode', 'address_use']
        
    def filter_organization_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
              'organizationtotaxonomy__nucc_code__display_name')
        ).filter(search=value)

    def filter_address(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'address__address_us__delivery_line_1',
                'address__address_us__delivery_line_2',
                'address__address_us__city_name',
                'address__address_us__state_code__abbreviation',
                'address__address_us__zipcode'
            )
        ).filter(search=value)

    def filter_address_city(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector('address__address_us__city_name')
        ).filter(search=value)

    def filter_address_state(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                'address__address_us__state_code__abbreviation'
            )
        ).filter(search=value)

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector('address__address_us__zipcode')
        ).filter(search=value)

    def filter_address_use(self, queryset, name, value):
        if value in addressUseMapping.keys():
            value = addressUseMapping.toNPD(value)
        else:
            value = -1
        return queryset.filter(address_id=value)
