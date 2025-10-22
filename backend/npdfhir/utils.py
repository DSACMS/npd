from fhir.resources.address import Address


def SmartyStreetstoFHIR(address):
    addressLine1=f"{address.address_us.primary_number} {address.address_us.street_predirection} {address.address_us.street_name} {address.address_us.postdirection} {address.address_us.street_suffix}"
    addressLine2=f"{address.address_us.secondary_designator} {address.address_us.secondary_number}"
    addressLine3=f"{address.address_us.extra_secondary_designator} {address.address_us.extra_secondary_number}"
    cityStateZip=f"f{address.address_us.city_name}, {address.address_us.fips_state.state_abbreviation} {address.address_us.zipcode}"
    return Address(
        line=[addressLine1, addressLine2, addressLine3, cityStateZip],
        use=address.address_type.value
    )
