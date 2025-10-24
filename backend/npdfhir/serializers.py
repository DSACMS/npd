import sys

from django.urls import reverse
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.location import Location as FHIRLocation
from fhir.resources.R4B.contactdetail import ContactDetail
from fhir.resources.R4B.meta import Meta
from fhir.resources.R4B.organization import Organization as FHIROrganization
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.practitioner import Practitioner, PractitionerQualification
from fhir.resources.R4B.practitionerrole import PractitionerRole
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.capabilitystatement import (
    CapabilityStatement,
    CapabilityStatementRest,
    CapabilityStatementRestResource,
    CapabilityStatementRestResourceSearchParam,
    CapabilityStatementImplementation
)
from datetime import datetime, timezone
from rest_framework import serializers
from .utils import getInternalEndpoint, genReference

from .models import (
    IndividualToPhone,
    Location,
    Npi,
    Organization,
    OrganizationToName,
    ProviderToOrganization,
)

if 'runserver' or 'test' in sys.argv:
    from .cache import (
        fhir_name_use,
        fhir_phone_use,
        nucc_taxonomy_codes,
        other_identifier_type,
    )


class AddressSerializer(serializers.Serializer):
    delivery_line_1 = serializers.CharField(
        source='addressus__delivery_line_1', read_only=True)
    delivery_line_2 = serializers.CharField(
        source='addressus__delivery_line_2', read_only=True)
    city_name = serializers.CharField(
        source='addressus__city_name', read_only=True)
    state_abbreviation = serializers.CharField(
        source='addressus__fipsstate__abbrev', read_only=True)
    zipcode = serializers.CharField(
        source='addressus__zipcode', read_only=True)
    use = serializers.CharField(
        source='address_use__value', read_only=True)

    class Meta:
        fields = ['delivery_line_1', 'delivery_line_2',
                  'city_name', 'state_abbreviation', 'zipcode', 'use']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if hasattr(instance, 'address'):
            address = instance.address.address_us
        else:
            address = instance.address_us
        address_list = [address.delivery_line_1]
        if address.delivery_line_2 is not None:
            address_list.append(address.delivery_line_2)
        address = Address(
            line=address_list,
            city=address.city_name,
            state=address.state_code.abbreviation,
            postalCode=address.zipcode,
            country='US'
        )
        if 'use' in representation.keys():
            address.use = representation['use'],
        return address.model_dump()


class EmailSerializer(serializers.Serializer):
    email_address = serializers.CharField(read_only=True)

    class Meta:
        fields = ['email_address']

    def to_representation(self, instance):
        email_contact = ContactPoint(
            system="email",
            value=instance.email_address,
            # use="work" TODO: add email use
        )
        return email_contact.model_dump()


class PhoneSerializer(serializers.Serializer):

    class Meta:
        model = IndividualToPhone
        fields = ['phone_number', 'phone_use_id', 'extension']

    def to_representation(self, instance):
        phone_contact = ContactPoint(
            system='phone',
            use=fhir_phone_use[str(instance.phone_use_id)],
            value=f"{instance.phone_number}"
        )
        if instance.extension is not None:
            phone_contact.value += f'ext. {instance.extension}'
        return phone_contact.model_dump()


class TaxonomySerializer(serializers.Serializer):
    id = serializers.CharField(source='nucc__code', read_only=True)
    display_name = serializers.CharField(
        source='nucc__display_name', read_only=True)

    class Meta:
        fields = ['id', 'display_name']

    def to_representation(self, instance):
        code = CodeableConcept(
            coding=[Coding(
                system="http://nucc.org/provider-taxonomy",
                code=instance.nucc_code_id,
                display=nucc_taxonomy_codes[str(instance.nucc_code_id)]
            )]
        )
        qualification = PractitionerQualification(
            identifier=[Identifier(
                value="test",
                type=code,  # TODO: Replace
                period=Period()
            )],
            code=code
        )
        return qualification.model_dump()


class OtherIdentifierSerializer(serializers.Serializer):
    value = serializers.CharField(read_only=True)
    issue_date = serializers.DateField(read_only=True)
    expiry_date = serializers.DateField(read_only=True)

    class Meta:
        fields = ['value', 'issue_date', 'expiry_date', 'other_identifier_type',
                  'other_identifier_type_id', 'other_identifier_type_value']

    def to_representation(self, id):

        other_identifier_type_id = id.other_identifier_type_id
        license_identifier = Identifier(
            # system="", TODO: Figure out how to associate a system with each identifier
            value=id.value,
            type=CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/v2-0203",
                    code=str(other_identifier_type_id),
                    display=other_identifier_type[str(
                        other_identifier_type_id)]
                )]
            ),
            # use="" TODO: Add use for other identifier
            period=Period(
                start=id.issue_date,
                end=id.expiry_date
            )
        )
        return license_identifier.model_dump()


class NameSerializer(serializers.Serializer):
    last_name = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    middle_name = serializers.CharField(read_only=True)
    effective_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)
    prefix = serializers.CharField(read_only=True)
    suffix = serializers.CharField(read_only=True)

    class Meta:
        fields = ['last_name', 'first_name', 'middle_name',
                  'start_date', 'end_date', 'prefix', 'suffix']

    def to_representation(self, name):

        name_parts = [part for part in [name.prefix, name.first_name,
                                        name.middle_name, name.last_name, name.suffix] if part != '' and part is not None]
        human_name = HumanName(
            use=fhir_name_use[str(name.name_use_id)],
            text=' '.join(name_parts),
            family=name.last_name,
            given=[name.first_name, name.middle_name],
            prefix=[name.prefix],
            suffix=[name.suffix],
            period=Period(
                start=name.start_date,
                end=name.end_date
            )
        )
        return human_name.model_dump()


class NPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Npi
        fields = '__all__'


class IndividualSerializer(serializers.Serializer):
    name = NameSerializer(
        source='individualtoname_set', read_only=True, many=True)
    email = EmailSerializer(
        source='individualtoemail_set', read_only=True, many=True)
    phone = PhoneSerializer(
        source='individualtophone_set', many=True, read_only=True)
    address = AddressSerializer(
        source='individualtoaddress_set', many=True, read_only=True)

    class Meta:
        fields = ['name', 'email', 'phone']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        individual = {
            'name': representation['name']
        }
        telecom = []
        if 'phone' in representation.keys():
            telecom += representation['phone']
        if 'email' in representation.keys():
            telecom += representation['email']
        individual['telecom'] = telecom
        if representation['address'] != []:
            individual['address'] = representation['address']
        return individual


class OrganizationNameSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    is_primary = serializers.BooleanField(read_only=True)

    class Meta:
        model = OrganizationToName
        fields = ['name', 'is_primary']


class EndpointPayloadSeriazlier(serializers.Serializer):
    class Meta:
        fields = ['type', 'mime_type']

    def to_representation(self, instance):
        payload_type = CodeableConcept(
            coding=[Coding(
                system="http://terminology.hl7.org/CodeSystem/endpoint-payload-type",
                code=instance.payload_type.id,
                display=instance.payload_type.value
            )]
        )

        return payload_type


class EndpointIdentifierSerialzier(serializers.Serializer):
    class Meta:
        fields = ['identifier', 'system', 'value', 'assigner']

    def to_representation(self, instance):
        endpoint_identifier = Identifier(
            use="official",
            system=instance.system,
            value=instance.other_id,
            # TODO: Replace with Organization reference
            assigner=Reference(display=str(instance.issuer_id))
        )

        return endpoint_identifier.model_dump()


class OrganizationSerializer(serializers.Serializer):
    name = OrganizationNameSerializer(
        source='organizationtoname_set', many=True, read_only=True)
    authorized_official = IndividualSerializer(read_only=True)
    address = AddressSerializer(
        source='organizationtoaddress_set', many=True, read_only=True)

    class Meta:
        model = Organization
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        organization = FHIROrganization()
        organization.id = str(instance.id)
        organization.meta = Meta(
            profile=[
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization"]
        )
        identifiers = []
        taxonomies = []

        if instance.ein:
            ein_identifier = Identifier(
                system="https://terminology.hl7.org/NamingSystem-USEIN.html",
                value=str(instance.ein.ein_id),
                type=CodeableConcept(
                    coding=[Coding(
                        system="http://terminology.hl7.org/CodeSystem/v2-0203",
                        code="TAX",
                        display="Tax ID number"
                    )]
                )
            )
            identifiers.append(ein_identifier)

        if hasattr(instance, "clinicalorganization"):
            clinical_org = instance.clinicalorganization
            if clinical_org and clinical_org.npi:
                npi_identifier = Identifier(
                    system="http://terminology.hl7.org/NamingSystem/npi",
                    value=str(clinical_org.npi.npi),
                    type=CodeableConcept(
                        coding=[Coding(
                            system="http://terminology.hl7.org/CodeSystem/v2-0203",
                            code="PRN",
                            display="Provider number"
                        )]
                    ),
                    use='official',
                    period=Period(
                        start=clinical_org.npi.enumeration_date,
                        end=clinical_org.npi.deactivation_date
                    )
                )
                identifiers.append(npi_identifier)

                for other_id in clinical_org.organizationtootherid_set.all():
                    other_identifier = Identifier(
                        system=str(other_id.other_id_type_id),
                        value=other_id.other_id,
                        type=CodeableConcept(
                            coding=[Coding(
                                system="http://terminology.hl7.org/CodeSystem/v2-0203",
                                code="test",  # do we define this based on the type of id it is?
                                display="test"  # same as above ^
                            )]
                        )
                    )
                    identifiers.append(other_identifier)

                for taxonomy in clinical_org.organizationtotaxonomy_set.all():
                    code = CodeableConcept(
                        coding=[Coding(
                            system="http://nucc.org/provider-taxonomy",
                            code=taxonomy.nucc_code_id,
                            display=nucc_taxonomy_codes[str(
                                taxonomy.nucc_code_id)]
                        )]
                    )
                    qualification = PractitionerQualification(
                        identifier=[Identifier(
                            value="test",
                            type=code,  # TODO: Replace
                            period=Period()
                        )],
                        code=code
                    )
                    taxonomies.append(qualification.model_dump())
                # TODO extend based on US core
                # if taxonomies:
                #    organization.qualification = taxonomies

        organization.identifier = identifiers

        names = representation.get('name', [])
        primary_names = [n['name'] for n in names if n['is_primary']]
        alias_names = [n['name'] for n in names if not n['is_primary']]

        if primary_names:
            organization.name = primary_names[0]
        elif names:
            organization.name = names[0]['name']

        if alias_names:
            organization.alias = alias_names

        authorized_official = representation['authorized_official']
        # r4 only allows one name for contact. TODO update to ndh
        authorized_official['name'] = authorized_official['name'][0]

        if representation['address'] != []:
            authorized_official['address'] = representation['address'][0]
        else:
            if 'address' in authorized_official.keys():
                del authorized_official['address']
        organization.contact = [authorized_official]

        return organization.model_dump()


class PractitionerSerializer(serializers.Serializer):
    npi = NPISerializer()
    individual = IndividualSerializer(read_only=True)
    identifier = OtherIdentifierSerializer(
        source='providertootheridentifier_set', many=True, read_only=True)
    taxonomy = TaxonomySerializer(
        source='providertotaxonomy_set', many=True, read_only=True)

    class Meta:
        fields = ['npi', 'name', 'email', 'phone', 'identifier', 'taxonomy']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        practitioner = Practitioner()
        practitioner.id = str(instance.individual.id)
        practitioner.meta = Meta(
            profile=[
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitioner"]
        )
        npi_identifier = Identifier(
            system="http://terminology.hl7.org/NamingSystem/npi",
            value=str(instance.npi.npi),
            type=CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/v2-0203",
                    code="PRN",
                    display="Provider number"
                )]
            ),
            use='official',
            period=Period(
                start=instance.npi.enumeration_date,
                end=instance.npi.deactivation_date
            )
        )
        if representation['individual']['telecom'] != []:
            practitioner.telecom = representation['individual']['telecom']
        if 'address' in representation['individual'].keys() and representation['individual']['address'] != []:
            practitioner.address = representation['individual']['address']
        practitioner.identifier = [npi_identifier]
        if 'identifier' in representation.keys():
            practitioner.identifier += representation['identifier']
        practitioner.name = representation['individual']['name']
        if 'taxonomy' in representation.keys():
            practitioner.qualification = representation['taxonomy']
        return practitioner.model_dump()


class LocationSerializer(serializers.Serializer):
    phone = PhoneSerializer(read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Location

    def to_representation(self, instance):
        request = self.context.get('request')
        representation = super().to_representation(instance)
        location = FHIRLocation()
        location.id = str(instance.id)
        if instance.active:
            location.status = 'active'
        else:
            location.status = 'inactive'
        location.name = instance.name
        # if 'phone' in representation.keys():
        #    location.telecom = representation['phone']
        if 'address' in representation.keys():
            location.address = representation['address']
        location.managingOrganization = genReference(
            'fhir-organization-detail', instance.organization_id, request)
        return location.model_dump()


class PractitionerRoleSerializer(serializers.Serializer):
    other_phone = PhoneSerializer(read_only=True)

    class Meta:
        model = ProviderToOrganization

    def to_representation(self, instance):
        request = self.context.get('request')
        representation = super().to_representation(instance)
        practitioner_role = PractitionerRole()
        practitioner_role.id = str(instance.id)
        practitioner_role.active = instance.active
        practitioner_role.practitioner = genReference(
            'fhir-practitioner-detail', instance.provider_to_organization.individual_id, request)
        practitioner_role.organization = genReference(
            'fhir-organization-detail', instance.provider_to_organization.organization_id, request)
        practitioner_role.location = [genReference(
            'fhir-location-detail', instance.location.id, request)]
        # These lines rely on the fhir.resources.R4B representation of PractitionerRole to be expanded to match the ndh FHIR definition. This is a TODO with an open ticket.
        # if 'other_phone' in representation.keys():
        #    practitioner_role.telecom = representation['other_phone']

        return practitioner_role.model_dump()


class EndpointSerializer(serializers.Serializer):
    payload = EndpointPayloadSeriazlier(
        source='endpointinstancetopayload_set', many=True, read_only=True)
    identifier = EndpointIdentifierSerialzier(
        source='endpointinstancetootherid_set', many=True, read_only=True
    )

    class Meta:
        fields = ['id', 'ehr_vendor', 'address', 'endpoint_connection_type',
                  'name', 'description' 'endpoint_instance']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        connection_type = Coding(
            system="http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
            code=instance.endpoint_connection_type.id,
            display=instance.endpoint_connection_type.display
        )

        environment_type = [CodeableConcept(
            coding=[Coding(
                system="https://hl7.org/fhir/valueset-endpoint-environment.html",
                code=instance.environment_type.id,
                display=instance.environment_type.display
            )]
        )]

        endpoint = Endpoint(
            id=str(instance.id),
            identifier=representation['identifier'],
            status="active",  # hardcoded for now
            connectionType=connection_type,
            name=instance.name,
            # TODO extend base fhir spec to ndh spec description=instance.description,
            # TODO extend base fhir spec to ndh spec environmentType=environment_type,
            # managingOrganization=Reference(managing_organization), ~ organization/npi or whatever we use as the organization identifier
            # contact=ContactPoint(contact), ~ still gotta figure this out
            # period=Period(period), ~ still gotta figure this out
            payloadType=representation['payload'],
            address=instance.address,
            header=["application/fhir"]  # hardcoded for now
        )

        return endpoint.model_dump()


class CapabilityStatementSerializer(serializers.Serializer):
    """
    Serializer for FHIR CapablityStatement resource
    """
    def to_representation(self, instance):
        request = self.context.get('request')
        baseURL = request.build_absolute_uri('/fhir')
        metadataURL = request.build_absolute_uri(reverse('fhir-metadata'))
        schemaData = getInternalEndpoint('schema-json', {'format': '.json'})

        capability_statement = CapabilityStatement(
            url=metadataURL,
            version="0.1.0",
            name="FHIRCapablityStatement",
            title="National Provider Directory FHIR Capablity Statement",
            status="active",
            date=datetime.now(timezone.utc),
            publisher="CMS",
            contact=[
                ContactDetail(
                    telecom=[
                        ContactPoint(
                            system="email",
                            value="npd@cms.hhs.gov"
                        )
                    ]
                )
            ],
            description="This CapabilityStatement describes the capabilities of the National Provider Directory FHIR API, including supported resources, search parameters, and operations.",
            kind="instance",
            implementation=CapabilityStatementImplementation(
                description=schemaData.info.description,
                url=baseURL
            ),
            fhirVersion="4.0.1",
            format=["fhir+json"],
            rest=[self.build_rest_components()]
        )

        return capability_statement.model_dump()
    
    def build_rest_components(self):
        """
        Building out each REST component describing our endpoint capabilities
        """
        schemaData = getInternalEndpoint('schema-json', {'format': '.json'})

        return CapabilityStatementRest(
            mode="server",
            documentation="All FHIR endpoints for the National Provider Directory",
            resource=[
                self.build_practitioner_resource(schemaData.paths["/Practitioner/"]),
                self.build_organization_resource(schemaData.paths["/Organization/"]),
                self.build_endpoint_resource(schemaData.paths["/Endpoint/"])
            ]
        )
    
    def build_practitioner_resource(self, schemaData):
        searchParams = []

        for param in schemaData["get"]["parameters"]:
            searchParams.append(
                CapabilityStatementRestResourceSearchParam(
                    name=param["name"],
                    type=param["type"],
                    documentation=param["description"]
                )
            )
            
        return CapabilityStatementRestResource(
            type="Practitioner",
            interaction=[
                {"code": "read"},
                {"code": "search-type"}
            ],
            searchParam=searchParams
        )

    def build_organization_resource(self, schemaData):
        searchParams = []

        for param in schemaData["get"]["parameters"]:
            searchParams.append(
                CapabilityStatementRestResourceSearchParam(
                    name=param["name"],
                    type=param["type"],
                    documentation=param["description"]
                )
            )

        return CapabilityStatementRestResource(
            type="Organization",
            interaction=[
                {"code": "read"},
                {"code": "search-type"}
            ],
            searchParam=searchParams
        )
    
    def build_endpoint_resource(self, schemaData):
        searchParams = []

        for param in schemaData["get"]["parameters"]:
            searchParams.append(
                CapabilityStatementRestResourceSearchParam(
                    name=param["name"],
                    type=param["type"],
                    documentation=param["description"]
                )
            )

        return CapabilityStatementRestResource(
            type="Endpoint",
            interaction=[
                {"code": "read"},
                {"code": "search-type"}
            ],
            searchParam=searchParams
        )


class BundleSerializer(serializers.Serializer):
    """
    Serializer for FHIR Bundle resource
    """
    class Meta:
        model = Bundle

    def to_representation(self, instance):
        entries = []

        for resource in instance.data:
            request = self.context.get('request')
            # Get the resource type (Patient, Practitioner, etc.)
            resource_type = resource['resourceType']
            id = resource['id']
            url_name = f'fhir-{resource_type.lower()}-detail'
            full_url = request.build_absolute_uri(
                reverse(url_name, kwargs={'pk': id}))
            # Create an entry for this resource
            entry = {
                "fullUrl": full_url,
                "resource": resource,
            }

            entries.append(entry)

        # Create the bundle
        bundle = Bundle(
            type="searchset",
            entry=entries,
            total=len(entries)
        )

        return bundle.model_dump()
