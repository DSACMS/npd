import uuid
import datetime
import random

from math import radians

from ..models import (
    Individual,
    IndividualToName,
    IndividualToAddress,
    FhirNameUse,
    FhirAddressUse,
    FipsState,
    Npi,
    Provider,
    Organization,
    OrganizationToName,
    Address,
    AddressUs,
    Location,
    ProviderToOrganization,
    RelationshipType,
    ProviderToLocation,
    ProviderRole,
    ProviderToTaxonomy,
    Endpoint,
    EndpointInstance,
    EndpointConnectionType,
    EndpointInstanceToPayload,
    EndpointType,
    EnvironmentType,
    EhrVendor,
    PayloadType,
    LegalEntity,
    OtherIdType,
    OrganizationToOtherId,
    OrganizationToTaxonomy,
    ClinicalOrganization,
    Nucc,
    LocationToEndpointInstance
)


def _ensure_name_use():
    return FhirNameUse.objects.get_or_create(value="usual")[0]


def create_practitioner(
    first_name="Alice",
    last_name="Smith",
    gender="F",
    birth_date=datetime.date(1990, 1, 1),
    npi_value=None,
    practitioner_type=None,
    location=None,
    address_use="work",
):
    """
    Creates an Individual, Name (via IndividualToName), Npi, Provider.
    """
    individual = Individual.objects.create(
        id=uuid.uuid4(),
        gender=gender,
        birth_date=birth_date,
    )

    IndividualToName.objects.create(
        individual=individual,
        first_name=first_name,
        last_name=last_name,
        name_use=_ensure_name_use(),
    )

    if location:
        use = FhirAddressUse.objects.get(value=address_use)

        IndividualToAddress.objects.create(
            individual=individual, address=location.address, address_use=use
        )

    npi = Npi.objects.create(
        npi=npi_value or int(str(uuid.uuid4().int)[:10]),
        entity_type_code=1,
        enumeration_date=datetime.date(2000, 1, 1),
        last_update_date=datetime.date(2020, 1, 1),
    )

    provider = Provider.objects.create(
        npi=npi,
        individual=individual,
    )

    if practitioner_type:
        code = Nucc.objects.get(pk=practitioner_type)

        ProviderToTaxonomy.objects.create(npi=provider, nucc_code=code, id=uuid.uuid4())

        # display name
        # Nucc

    return provider


def create_legal_entity(dba_name="Sample Legal Entity"):
    legal_entity = LegalEntity.objects.create(ein_id=uuid.uuid4(), dba_name=dba_name)

    return legal_entity


def create_other_id_type(name="Sample Other ID"):
    other_id = OtherIdType.objects.create(value=name)

    return other_id


def create_organization(
    id=None,
    name="Test Org",
    parent_id=None,
    authorized_official_first_name="Alice",
    authorized_official_last_name="Smith",
    legal_entity=None,
    other_id_type=None,
    npi_value=None,
    other_id_name="testMBI",
    other_state_code="NY",
    other_issuer="New York State Medicaid",
    organization_type=None,
):
    """
    Creates an Organization + OrganizationToName.
    """
    # authorized_official cannot be null → create a dummy individual
    ind = Individual.objects.create(
        id=uuid.uuid4(),
        gender="U",
        birth_date=datetime.date(1980, 1, 1),
    )

    IndividualToName.objects.create(
        individual=ind,
        first_name=authorized_official_first_name,
        last_name=authorized_official_last_name,
        name_use=_ensure_name_use(),
    )

    if id is None:
        id = uuid.uuid4()

    org = Organization.objects.create(
        id=id, authorized_official=ind, ein=legal_entity, parent_id=parent_id
    )

    if other_id_type or organization_type or npi_value:
        npi = Npi.objects.create(
            npi=npi_value or int(str(uuid.uuid4().int)[:10]),
            entity_type_code=1,
            enumeration_date=datetime.date(2000, 1, 1),
            last_update_date=datetime.date(2020, 1, 1),
        )

        clinical_organization = ClinicalOrganization.objects.create(organization=org, npi=npi)

        if other_id_type:
            OrganizationToOtherId.objects.create(
                npi=clinical_organization,
                other_id=other_id_name,
                other_id_type=other_id_type,
                state_code=other_state_code,
                issuer=other_issuer,
            )

        if organization_type:
            code = Nucc.objects.get(pk=organization_type)

            OrganizationToTaxonomy.objects.create(npi=clinical_organization, nucc_code=code)

    OrganizationToName.objects.create(
        organization=org,
        name=name,
        is_primary=True,
    )

    return org

def _set_location_coords(location, lat, lon):
    """
    Utility to force lat/lon on a role's location.
    """

    address_us = location.address.address_us
    address_us.latitude = lat
    address_us.longitude = lon
    address_us.save(update_fields=["latitude", "longitude"])

def create_location(
    organization=None,
    name="Test Location",
    city="Albany",
    state="NY",
    zipcode="12207",
    addr_line_1="123 Main St",
    latitude=None,
    longitude=None
):
    """
    Creates AddressUs → Address → Location.
    """
    organization = organization or create_organization()

    fips_code = FipsState.objects.get(abbreviation=state)
    addr_us = AddressUs.objects.create(
        id=random.randint(-100000000000, 100000000000),
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

    if latitude and longitude:
        _set_location_coords(loc, latitude, longitude)

    return loc


def _ensure_endpoint_base_types():
    """
    Flyway inserts some reference values, but ensure minimal ones exist.
    """
    etype, _ = EndpointType.objects.get_or_create(value="rest")
    ctype, _ = EndpointConnectionType.objects.get_or_create(
        id="hl7-fhir-rest",
        defaults={"display": "FHIR REST", "definition": "FHIR REST endpoint"},
    )
    payload, _ = PayloadType.objects.get_or_create(
        id="fhir-json",
        defaults={"value": "application/fhir+json", "description": "FHIR JSON"},
    )
    return etype, ctype, payload


def create_endpoint(
    organization=None,
    url="https://example.org/fhir",
    name="Test Endpoint",
    ehr=None,
    payload_type=None,
):
    """
    Creates EndpointType, EndpointConnectionType, EndpointInstance, Endpoint.
    """
    organization = organization or create_organization()
    loc = create_location(organization=organization)

    etype, ctype, payload = _ensure_endpoint_base_types()

    if not ehr:
        new_vendor_id = uuid.uuid4()
        ehr_vendor = EhrVendor.objects.create(
            id=new_vendor_id, name=f"My Sample{new_vendor_id}", is_cms_aligned_network=True
        )
    else:
        ehr_vendor = ehr

    et = EnvironmentType.objects.get(pk="prod")

    pt = PayloadType.objects.get(pk=payload_type or "urn:hl7-org:sdwg:ccda-structuredBody:1.1")

    instance = EndpointInstance.objects.create(
        id=uuid.uuid4(),
        ehr_vendor_id=ehr_vendor.id,
        address=url,
        endpoint_connection_type=ctype,
        name=name,
        environment_type=et,
    )

    LocationToEndpointInstance.objects.create(
        location=loc,
        endpoint_instance=instance
    )

    EndpointInstanceToPayload.objects.create(endpoint_instance=instance, payload_type=pt)

    ep = Endpoint.objects.create(
        id=uuid.uuid4(),
        address=url,
        endpoint_type=etype,
        endpoint_instance=instance,
        name=name,
    )

    return ep


def _ensure_relationship_type():
    """
    Retrieve an existing relationship_type inserted by Flyway.
    Default: 'assigning' (id=2)
    """
    try:
        return RelationshipType.objects.get(value="assigning")
    except RelationshipType.DoesNotExist:
        # If Flyway hasn’t run (edge/dev case), create one safely
        return RelationshipType.objects.create(value="assigning")


def _ensure_provider_role(code="PRV", display="Provider Role"):
    return ProviderRole.objects.get_or_create(
        code=code,
        defaults={
            "system": "http://hl7.org/fhir/practitionerrole",
            "display": display,
        },
    )[0]


def create_full_practitionerrole(
    first_name="Alice",
    last_name="Smith",
    gender="F",
    npi_value=None,
    org_name="Test Org",
    location_name="Test Location",
    role_code="PRV",
    role_display="Provider Role",
    latitude=None,
    longitude=None
):
    """
    Creates:
        Practitioner (Provider)
        Organization
        Location
        ProviderToOrganization
        ProviderToLocation
    """
    provider = create_practitioner(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        npi_value=npi_value,
    )

    org = create_organization(name=org_name)
    loc = create_location(organization=org, name=location_name)

    # Ensure relationship + role codes exist
    rel_type = _ensure_relationship_type()
    _ensure_provider_role(role_code, role_display)

    pto_org = ProviderToOrganization.objects.create(
        id=uuid.uuid4(),
        individual=provider,  # special FK uses Provider.individual_id
        organization=org,
        relationship_type=rel_type,
        active=True,
    )

    if latitude and longitude:
        _set_location_coords(loc, latitude, longitude)

    pr = ProviderToLocation.objects.create(
        id=uuid.uuid4(),
        provider_to_organization=pto_org,
        location=loc,
        provider_role_code=role_code,
        active=True,
    )

    return pr
