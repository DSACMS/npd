from typing import Dict
from fhir.resources.organization import Organization
from fhir.resources.address import Address
from pydantic import ValidationError, BaseModel


def validate_address(cls, values: Dict):
    if not values:
        return values
    elif "address" not in values:
        return values
    elif type(values["address"]) != list:
        raise ValidationError("address must be of type list.")
    for i, address in enumerate(values["address"]):
        try:
            Address.model_validate_json(address)
        except:
            raise ValdationError(
                f"address at index {i} fails address validation")
    return values


NDHOrganization =
# We're adding an address list to Organization to conform with the NDH FHIR spec, which includes this while base FHIR does not.
Organization.add_root_validator(validate_address)
