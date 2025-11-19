import uuid
import datetime

from .models import (
    Organization, Individual, LegalEntity,
    Address, AddressUs, FipsState, FipsCounty, FhirAddressUse,
    Location, OrganizationToName, OrganizationToAddress,
    Endpoint, EndpointInstance, EndpointType, EndpointConnectionType,
    EhrVendor, EnvironmentType, PayloadType, MimeType,
    EndpointInstanceToPayload,
    Npi, Provider, IndividualToName, FhirNameUse,
    PractitionerRole, Nucc, NuccClassification, NuccGrouping,
)

def guid():
    return uuid.uuid4()

def today():
    return datetime.date.today()

def create_state_and_county(state_code: str):
    state_obj, _ = FipsState.objects.get_or_create(
        id=state_code,
        defaults={"name": state_code, "abbreviation": state_code},
    )

    county_obj, _ = FipsCounty.objects.get_or_create(
        id=f"{state_code}-001",
        defaults={"name": f"{state_code} County", "fips_state": state_obj},
    )

    return state_obj, county_obj


def create_address(city: str = "Boston", state: str = "MA", postal: str = "02118", street: str = "1 Main St"):
    state_obj, _ = FipsState.objects.get_or_create(
        id=state, defaults={"name": state, "abbreviation": state}
    )

    addr_us = AddressUs.objects.create(
        id=str(uuid.uuid4())[:10],
        delivery_line_1=street,
        city_name=city,
        state_code=state_obj,
        zipcode=postal,
    )
    return Address.objects.create(id=guid(), address_us=addr_us)


def create_organization(
    name: str = "Test Org",
    city: str = "Boston",
    state: str = "MA",
    postal: str = "02118",
    primary: bool = True,
    address_use: str = "work",
    org_id=None,
):

    address = create_address(city=city, state=state, postal=postal)

    indiv = Individual.objects.create(
        id=guid(),
        gender="M",
        birth_date=datetime.date(1980, 1, 1),
    )

    legal = LegalEntity.objects.create(
        ein_id=guid(),
        dba_name=name,
    )

    org = Organization.objects.create(
        id=org_id or guid(),
        authorized_official=indiv,
        ein=legal,
    )

    OrganizationToName.objects.create(
        organization=org,
        name=name,
        is_primary=primary,
    )

    use_obj, _ = FhirAddressUse.objects.get_or_create(value=address_use)

    OrganizationToAddress.objects.create(
        organization=org,
        address=address,
        address_use=use_obj,
    )

    return org

def create_location(
    name: str = "Test Location",
    org: Organization | None = None,
    city: str = "Seattle",
    state: str = "WA",
    postal: str = "98001",
    location_id=None,
):

    if org is None:
        org = create_organization()

    address = create_address(city=city, state=state, postal=postal)

    return Location.objects.create(
        id=location_id or guid(),
        name=name,
        organization=org,
        address=address,
        active=True,
    )

def create_endpoint(
    name: str = "Test Endpoint",
    address: str = "https://example.org/fhir",
    connection_type: str = "hl7-fhir-rest",
    payload: str = "ccda-structuredBody:1.1",
    env: str = "prod",
    vendor_name: str = "Test Vendor",
    endpoint_id=None,
):

    conn_type, _ = EndpointConnectionType.objects.get_or_create(
        id=connection_type,
        defaults={"display": connection_type},
    )

    payload_type, _ = PayloadType.objects.get_or_create(
        id=payload,
        defaults={"value": payload},
    )

    mime_type, _ = MimeType.objects.get_or_create(value="application/json")

    env_type, _ = EnvironmentType.objects.get_or_create(
        id=env,
        defaults={"display": env},
    )

    vendor, _ = EhrVendor.objects.get_or_create(
        id=guid(),
        defaults={"name": vendor_name, "is_cms_aligned_network": False},
    )

    instance = EndpointInstance.objects.create(
        id=guid(),
        ehr_vendor=vendor,
        address=address,
        endpoint_connection_type=conn_type,
        name=name,
        environment_type=env_type,
    )

    EndpointInstanceToPayload.objects.create(
        endpoint_instance=instance,
        mime_type=mime_type,
        payload_type=payload_type,
    )

    endpoint_type, _ = EndpointType.objects.get_or_create(value="fhir")

    return Endpoint.objects.create(
        id=endpoint_id or guid(),
        address=address,
        endpoint_type=endpoint_type,
        endpoint_instance=instance,
        name=name,
    )

def create_practitioner(
    first: str = "John",
    last: str = "Smith",
    gender: str = "M",
    npi_value: int = 1234567890,
):

    indiv = Individual.objects.create(
        id=guid(),
        gender=gender,
        birth_date=datetime.date(1977, 7, 7),
    )

    name_use, _ = FhirNameUse.objects.get_or_create(value="official")

    IndividualToName.objects.create(
        individual=indiv,
        first_name=first,
        last_name=last,
        name_use=name_use,
    )

    npi = Npi.objects.create(
        npi=npi_value,
        entity_type_code=1,
        enumeration_date=today(),
        last_update_date=today(),
    )

    provider = Provider.objects.create(
        npi=npi,
        individual=indiv,
    )

    return provider


def create_practitioner_role(
    practitioner: Provider | None = None,
    location: Location | None = None,
    role_display: str = "Physician",
    code: str = "MD",
    role_id=None,
):

    if practitioner is None:
        practitioner = create_practitioner()

    if location is None:
        location = create_location()

    grouping, _ = NuccGrouping.objects.get_or_create(display_name="Group")

    nucc_code, _ = Nucc.objects.get_or_create(
        code="207Q00000X",
        defaults={"display_name": role_display},
    )

    NuccClassification.objects.get_or_create(
        nucc_code=nucc_code,
        nucc_grouping=grouping,
        defaults={"display_name": role_display},
    )

    return PractitionerRole.objects.create(
        id=role_id or guid(),
        value=code,
    )


def create_multiple_organizations(count: int, name_prefix="Org"):
    return [
        create_organization(name=f"{name_prefix} {i}")
        for i in range(count)
    ]


def create_multiple_endpoints(count: int, name_prefix="Endpoint"):
    return [
        create_endpoint(name=f"{name_prefix} {i}")
        for i in range(count)
    ]


def create_sorted_endpoints(names: list[str]):
    return [create_endpoint(name=n) for n in names]


def create_multiple_practitioners(count: int, first_prefix="John", last_prefix="Smith"):
    return [
        create_practitioner(
            first=f"{first_prefix}{i}",
            last=f"{last_prefix}{i}",
            npi_value=1000000000 + i,
        )
        for i in range(count)
    ]
