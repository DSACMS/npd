from rest_framework import serializers
from fhir.resources.practitioner import Practitioner
from fhir.resources.bundle import Bundle
from .models import Npi, OrganizationToName, IndividualToPhone
from fhir.resources.practitioner import Practitioner, PractitionerQualification
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.period import Period
from fhir.resources.meta import Meta
from fhir.resources.address import Address
from fhir.resources.organization import Organization
import sys
if 'runserver' or 'test' in sys.argv:
    from .cache import other_identifier_type, fhir_name_use, nucc_taxonomy_codes, fhir_phone_use


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

    class Meta:
        fields = ['delivery_line_1', 'delivery_line_2',
                  'city_name', 'state_abbreviation', 'zipcode']

    def to_representation(self, instance):
        address = instance.address.address_us
        address_list = [address.delivery_line_1]
        if address.delivery_line_2 is not None:
            address_list.append(address.delivery_line_2)
        address = Address(
            line=address_list,
            city=address.city_name,
            state=address.state_code.abbreviation,
            postalCode=address.zipcode,
            use=instance.address_use.value,
            country='US'
        )
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


class OrganizationSerializer(serializers.Serializer):
    name = OrganizationNameSerializer(
        source='organizationtoname_set', many=True, read_only=True)
    authorized_official = IndividualSerializer(read_only=True)
    address = address = AddressSerializer(
        source='organizationtoaddress_set', many=True, read_only=True)

    class Meta:
        model = Organization
        fields = '__all__'


class ClinicalOrganizationSerializer(serializers.Serializer):
    npi = NPISerializer()
    organization = OrganizationSerializer()
    identifier = OtherIdentifierSerializer(
        source='organizationtootheridentifier_set', many=True, read_only=True
    )
    taxonomy = TaxonomySerializer(
        source='organizationtotaxonomy_set', many=True, read_only=True
    )

    class Meta:
        fields = ['npi', 'name', 'identifier', 'taxonomy']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        organization = Organization()
        organization.id = str(instance.npi.npi)
        organization.meta = Meta(
            profile=[
                "http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization"]
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
        organization.identifier = [npi_identifier]
        if 'identifier' in representation.keys():
            organization.identifier += representation['identifier']
        name = [name['name'] for name in representation['organization']
                ['name'] if name['is_primary']]
        alias = [name['name'] for name in representation['organization']
                 ['name'] if not name['is_primary']]
        organization.name = name[0]
        if alias != []:
            organization.alias = [name['name'] for name in alias]
        authorized_official = representation['organization']['authorized_official']
        if representation['organization']['address'] != []:
            authorized_official['address'] = representation['organization']['address'][0]
        else:
            del authorized_official['address']
        organization.contact = [authorized_official]
        if 'taxonomy' in representation.keys():
            organization.qualification = representation['taxonomy']
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
        practitioner.id = str(instance.npi.npi)
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
        if representation['individual']['address'] != []:
            practitioner.address = representation['individual']['address']
        practitioner.identifier = [npi_identifier]
        if 'identifier' in representation.keys():
            practitioner.identifier += representation['identifier']
        practitioner.name = representation['individual']['name']
        if 'taxonomy' in representation.keys():
            practitioner.qualification = representation['taxonomy']
        return practitioner.model_dump()


class BundleSerializer(serializers.Serializer):
    """
    Serializer for FHIR Bundle resource
    """
    class Meta:
        model = Bundle

    def to_representation(self, instance):
        entries = []

        for resource in instance.data:
            # Get the resource type (Patient, Practitioner, etc.)
            resource_type = resource['resourceType']
            id = resource['id']

            # Create an entry for this resource
            entry = {
                "fullUrl": f"{resource_type}/{id}",
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
