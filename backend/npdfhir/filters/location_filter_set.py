from django_filters import rest_framework as filters
from django.contrib.postgres.search import SearchVector

from ..models import Location
from ..mappings import addressUseMapping


class LocationFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name", lookup_expr="exact", help_text="Filter by location name"
    )

    organization_type = filters.CharFilter(
        method="filter_organization_type", help_text="Filter by organization type"
    )

    address = filters.CharFilter(method="filter_address", help_text="Filter by any part of address")

    address_city = filters.CharFilter(method="filter_address_city", help_text="Filter by city name")

    address_state = filters.CharFilter(
        method="filter_address_state", help_text="Filter by state (2-letter abbreviation)"
    )

    address_postalcode = filters.CharFilter(
        method="filter_address_postalcode", help_text="Filter by postal code/zip code"
    )

    address_use = filters.ChoiceFilter(
        method="filter_address_use",
        choices=addressUseMapping.to_choices(),
        help_text="Filter by address use type",
    )

    class Meta:
        model = Location
        fields = [
            "name",
            "address",
            "address_city",
            "address_state",
            "address_postalcode",
            "address_use",
        ]

    def filter_organization_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("organizationtotaxonomy__nucc_code__display_name")
        ).filter(search=value)

    def filter_address(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "address__address_us__delivery_line_1",
                "address__address_us__delivery_line_2",
                "address__address_us__city_name",
                "address__address_us__state_code__abbreviation",
                "address__address_us__zipcode",
            )
        ).filter(search=value)

    def filter_address_city(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("address__address_us__city_name")).filter(
            search=value
        )

    def filter_address_state(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("address__address_us__state_code__abbreviation")
        ).filter(search=value)

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("address__address_us__zipcode")).filter(
            search=value
        )

    def filter_address_use(self, queryset, name, value):
        if value in addressUseMapping.keys():
            value = addressUseMapping.toNPD(value)
        else:
            value = -1
        return queryset.filter(address_id=value)
