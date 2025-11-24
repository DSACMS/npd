import uuid
import datetime

from ..models import (
    Individual,
    IndividualToName,
    FhirNameUse,
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
    Endpoint,
    EndpointInstance,
    EndpointConnectionType,
    EndpointType,
    PayloadType,
    LegalEntity,
    OtherIdType,
    OrganizationToOtherId,
    OrganizationToTaxonomy,
    ClinicalOrganization,
    Nucc
)

def _ensure_name_use():
    return FhirNameUse.objects.get_or_create(value="usual")[0]


def create_practitioner(
    first_name="Alice",
    last_name="Smith",
    gender="F",
    birth_date=datetime.date(1990, 1, 1),
    npi_value=None,
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

    return provider

def create_legal_entity(dba_name="Sample Legal Entity"):
    
    legal_entity = LegalEntity.objects.create(
        ein_id=uuid.uuid4(),
        dba_name=dba_name
    )

    return legal_entity

def create_other_id_type(name="Sample Other ID"):
    other_id = OtherIdType.objects.create(
        value=name
    )

    return other_id

def create_organization(
    name="Test Org",
    authorized_official_first_name="Alice",
    authorized_official_last_name="Smith",
    legal_entity=None,
    other_id_type=None,
    npi_value=None,
    other_id_name='testMBI',
    other_state_code='NY',
    other_issuer='New York State Medicaid',
    organization_type=None
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

    org = Organization.objects.create(
            id=uuid.uuid4(),
            authorized_official=ind,
            ein=legal_entity,
        )

    if other_id_type or organization_type or npi_value:
        

        npi = Npi.objects.create(
            npi=npi_value or int(str(uuid.uuid4().int)[:10]),
            entity_type_code=1,
            enumeration_date=datetime.date(2000, 1, 1),
            last_update_date=datetime.date(2020, 1, 1),
        )

        clinical_organization = ClinicalOrganization.objects.create(
            organization=org,
            npi=npi
        )

        if other_id_type:
            org_other_id = OrganizationToOtherId.objects.create(
                npi=clinical_organization,
                other_id=other_id_name,
                other_id_type=other_id_type,
                state_code=other_state_code,
                issuer=other_issuer
            )

        if organization_type:
            code = Nucc.objects.create(
                code='TEST',
                display_name=organization_type,
                definition='SAMPLE'
            )

            taxonomy = OrganizationToTaxonomy.objects.create(
                npi = clinical_organization,
                nucc_code=code
            )

    
    OrganizationToName.objects.create(
        organization=org,
        name=name,
        is_primary=True,
    )

    return org

def create_location(
    organization=None,
    name="Test Location",
    city="Albany",
    state="NY",
    zipcode="12207",
):
    """
    Creates AddressUs → Address → Location.
    """
    organization = organization or create_organization()

    addr_us = AddressUs.objects.create(
        id=str(uuid.uuid4())[:10],
        delivery_line_1="123 Main St",
        city_name=city,
        state_code_id='36',
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
):
    """
    Creates EndpointType, EndpointConnectionType, EndpointInstance, Endpoint.
    """
    organization = organization or create_organization()

    etype, ctype, payload = _ensure_endpoint_base_types()

    instance = EndpointInstance.objects.create(
        id=uuid.uuid4(),
        ehr_vendor_id=uuid.uuid4(),  # fake vendor
        address=url,
        endpoint_connection_type=ctype,
        name=name,
    )

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
        individual=provider,   # special FK uses Provider.individual_id
        organization=org,
        relationship_type=rel_type,
        active=True,
    )

    pr = ProviderToLocation.objects.create(
        id=uuid.uuid4(),
        provider_to_organization=pto_org,
        location=loc,
        provider_role_code=role_code,
        active=True,
    )

    return pr
