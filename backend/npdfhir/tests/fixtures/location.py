import datetime
import uuid

from ...models import Address, AddressUs, FipsState, Location
from .organization import create_organization


def create_location(
    organization=None,
    name="Test Location",
    city="Albany",
    state="NY",
    zipcode="12207",
    addr_line_1="123 Main St",
):
    """
    Creates AddressUs → Address → Location.
    """
    organization = organization or create_organization()

    fips_code = FipsState.objects.get(abbreviation=state)
    addr_us = AddressUs.objects.create(
        id=str(uuid.uuid4())[:10],
        delivery_line_1=addr_line_1,
        city_name=city,
        state_code_id=fips_code.id,
        zipcode=zipcode,
    )

    address = Address.objects.create(
        id=uuid.uuid4(),
        address_us=addr_us,
    )

    loc = Location.objects.create(
        id=uuid.uuid4(),
        name=name,
        organization=organization,
        address=address,
        active=True,
    )

    return loc
