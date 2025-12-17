from django.contrib.postgres.search import SearchVector
from django_filters import rest_framework as filters
from geopy.distance import geodesic

from ..mappings import genderMapping
from ..models import ProviderToLocation


def _bounding_box(lat, lon, distance_km):
    # Get a box defined by the provided distance from the given lat/long

    # Lat and long lines are every 111 km
    delta = distance_km / 111.0

    return {
        "min_lat": lat - delta,
        "max_lat": lat + delta,
        "min_lon": lon - delta,
        "max_lon": lon + delta,
    }


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

    latitude = filters.NumberFilter(
        method="filter_by_distance", help_text="Filter by latitude for lat/long filter"
    )
    longitude = filters.NumberFilter(
        method="filter_by_distance", help_text="Filter by longitude for lat/long filter"
    )
    distance = filters.NumberFilter(
        method="filter_by_distance", help_text="Filter by distance for lat/long filter"
    )
    units = filters.CharFilter(
        method="filter_by_distance", help_text="Specify distance units for lat/long filter"
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

    def filter_by_distance(self, queryset, name, value):
        data = self.data

        lat = data.get("latitude")
        lon = data.get("longitude")
        dist = data.get("distance")

        supplied = [lat is not None, lon is not None, dist is not None]

        # If ANY are supplied, ALL must be supplied
        if any(supplied) and not all(supplied):
            raise ValueError("latitude, longitude, and distance must be provided together")

        try:
            lat = float(lat)
            lon = float(lon)
            distance = float(dist)
        except (TypeError, ValueError):
            return queryset

        units = data.get("units", "mi")
        if units not in ("mi", "km"):
            return queryset.none()

        max_km = distance * 1.60934 if units == "mi" else distance

        # Filter by all locations in a box defined by the given lat and long
        box = _bounding_box(lat, lon, max_km)

        qs = queryset.filter(
            location__address__address_us__latitude__isnull=False,
            location__address__address_us__longitude__isnull=False,
            location__address__address_us__latitude__gte=box["min_lat"],
            location__address__address_us__latitude__lte=box["max_lat"],
            location__address__address_us__longitude__gte=box["min_lon"],
            location__address__address_us__longitude__lte=box["max_lon"],
        )

        # Use geopy to get the more precise distance inside the bounding box
        ids = []
        for obj in qs.select_related("location__address__address_us"):
            addr = obj.location.address.address_us
            if geodesic((lat, lon), (addr.latitude, addr.longitude)).km <= max_km:
                ids.append(obj.pk)

        return queryset.filter(pk__in=ids)
