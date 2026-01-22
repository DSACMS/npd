from django.contrib.postgres.search import SearchVector
from django_filters import rest_framework as filters

from ..mappings import genderMapping
from ..models import ProviderToLocation


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

    class Meta:
        model = ProviderToLocation
        fields = [
            "practitioner_name",
            "practitioner_gender",
            "practitioner_type",
            "organization_name",
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
