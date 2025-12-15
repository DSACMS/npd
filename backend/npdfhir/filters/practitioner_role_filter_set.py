from django_filters import rest_framework as filters
from django.contrib.postgres.search import SearchVector
from django.db.models import Q

from ..models import ProviderToLocation
from ..mappings import genderMapping


class PractitionerRoleFilterSet(filters.FilterSet):
    practitioner_name = filters.CharFilter(
        method="filter_practitioner_name",
        help_text="Filter by practitioner name (first, last, or full name)",
    )

    practitioner_gender = filters.ChoiceFilter(
        method="filter_practitioner_gender",
        choices=genderMapping.to_choices(),
        help_text="Filter by practitioner gender",
    )

    practitioner_type = filters.CharFilter(
        method="filter_practitioner_type", help_text="Filter by practitioner type/taxonomy"
    )

    organization_name = filters.CharFilter(
        method="filter_organization_name", help_text="Filter by organization name"
    )

    organization_type = filters.CharFilter(
        method="filter_organization_type",
        help_text="Filter by organization type"
    )

    active = filters.BooleanFilter(
        field_name="active",
        help_text="Filter by active status"
    )

    identifier = filters.CharFilter(
        method="filter_practitioner_identifer", help_text="Filter by practioner identifer"
    )

    role = filters.CharFilter(
        field_name="provider_role_code",
        lookup_expr="iexact",
        help_text="Filter by provider role code"
    )

    specialty = filters.CharFilter(
        method="filter_code",
        help_text="Filter by Nucc/Snomed specialty code"
    )

    endpoint_connection_type = filters.CharFilter(
        method="filter_connection_type",
        help_text="Filter providers by endpoint connection type"
    )

    endpoint_payload_type = filters.CharFilter(
        method="filter_payload_type",
        help_text="Filter providers by endpoint payload type"
    )

    #TODO: endpoint status is currently not implemented

    endpoint_organization_id = filters.UUIDFilter(
        method="filter_endpoint_organization_id",
        help_text="Filter by the UUID of the organization associated with endpoints"
    )

    endpoint_organization_name = filters.CharFilter(
        method="filter_endpoint_organization_name",
        help_text="Filter by the name of the organization associated with endpoints"
    )


    class Meta:
        model = ProviderToLocation
        fields = [
            "practitioner_name",
            "practitioner_gender",
            "practitioner_type",
            "organization_name",
            "organization_type",
            "active",
            "identifier",
            "role",
            "specialty",
            "endpoint_connection_type",
            "endpoint_payload_type",
            "endpoint_organization_id",
            "endpoint_organization_name"
        ]

    def filter_practitioner_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "provider_to_organization__individual__individual__individualtoname__first_name",
                "provider_to_organization__individual__individual__individualtoname__last_name",
                "provider_to_organization__individual__individual__individualtoname__middle_name",
            )
        ).filter(search=value)

    def filter_practitioner_gender(self, queryset, name, value):
        if value in genderMapping.keys():
            gender = genderMapping.toNPD(value)
            return queryset.filter(provider_to_organization__individual__individual__gender=gender)
        return queryset

    def filter_practitioner_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "provider_to_organization__providertotaxonomy__nucc_code__display_name"
            )
        ).filter(search=value)

    def filter_organization_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("provider_to_organization__organization__organizationtoname__name")
        ).filter(search=value)
    
    def filter_organization_type(self, queryset, name, value):
        return queryset.filter(
            Q(provider_to_organization__organization__clinicalorganization__organizationtotaxonomy_set__nucc_code__code=value) 
            | Q(
                provider_to_organization__organization__clinicalorganization__organizationtootherid_set__other_id=value
            ).distinct()
        )

    def filter_practitioner_idef filter_connection_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "other_endpoint__endpoint_instance__endpoint_connection_type__id"
            )
        ).filter(search=value)dentifer(self, queryset, name, value):
        return queryset.filter(
            Q(provider_to_organization__individual__npi__npi=value)
            | Q(
                provider_to_organization__individual__providertootherid__other_id__icontains=value
            )
        ).distinct()
    
    def filter_code(self, queryset, name, value):
        return queryset.filter(
            Q(provider_to_organization__individual__providertotaxonomy__nucc_code__code__iexact=value=value)
            | Q(provider_role_code__iexact=value)
        ).distinct()

    def filter_connection_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "other_endpoint__endpoint_instance__endpoint_connection_type__id"
            )
        ).filter(search=value)
    
    def filter_payload_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "location__locationtoendpointinstance__endpoint_instance__endpoint_instance_type__value"
            )
        ).filter(search=value)
    
    def filter_endpoint_organization_id(self, queryset, name, value):
        #The parent of the organization that owns the location the endpoint is attached to
        return queryset.filter(
            location__organization__parent__id=value
        )
    
    def filter_endpoint_organization_name(self, queryset, name, value):
        #The parent of the organization that owns the location the endpoint is attached to
        return queryset.filter(
            location__organization__parent__organizationtoname__name=value
        )