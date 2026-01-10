from ...models import FhirNameUse


def _ensure_name_use():
    return FhirNameUse.objects.get_or_create(value="usual")[0]

def _set_location_coords(location, lat, lon):
    """
    Utility to force lat/lon on a role's location.
    """

    address_us = location.address.address_us
    address_us.latitude = lat
    address_us.longitude = lon
    address_us.save(update_fields=["latitude", "longitude"])