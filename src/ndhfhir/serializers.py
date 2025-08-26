from rest_framework import serializers
from fhir.resources.practitioner import Practitioner
from fhir.resources.bundle import Bundle
from .models import Npi, IndividualToEmailAddress, ProviderToOtherIdentifier, IndividualToName, Provider, Individual
from fhir.resources.practitioner import Practitioner, PractitionerQualification
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.period import Period
from fhir.resources.meta import Meta
from fhir.resources.address import Address
import sys
if 'runserver' in sys.argv:
    from .cache import other_identifier_type, fhir_name_use, nucc_taxonomy_codes


class AddressSerializer(serializers.Serializer):
    primary_number = serializers.CharField(
        source='addressus__primary_number', read_only=True)
    street_predirection = serializers.CharField(
        source='addressus__street_predirection', read_only=True)
    street_name = serializers.CharField(
        source='addressus_street_name', read_only=True)
    postdirection = serializers.CharField(
        source='addressus__postdirection', read_only=True)
    street_suffix = serializers.CharField(
        source='addressus__street_suffix', read_only=True)
    secondary_designator = serializers.CharField(
        source='addressus__secondary_designator', read_only=True)
    secondary_number = serializers.CharField(
        source='addressus__secondary_number', read_only=True)
    extra_secondary_designator = serializers.CharField(
        source='addressus__extra_secondary_designator', read_only=True)
    extra_secondary_number = serializers.CharField(
        source='addressus__extra_secondary_number', read_only=True)
    city_name = serializers.CharField(
        source='addressus__city_name', read_only=True)
    state_abbreviation = serializers.CharField(
        source='addressus__fipsstate__abbrev', read_only=True)
    zipcode = serializers.CharField(
        source='addressus__zipcode', read_only=True)

    class Meta:
        fields = ['primary_number', 'street_predirection', 'street_name', 'postdirection', 'street_suffix',
                  'secondary_designator', 'secondary_number', 'extra_secondary_designator', 'extra_secondary_number',
                  'city_name', 'state_abbreviation', 'zipcode']

    def to_representation(self, instance):
        addressLine1 = f"{instance.primary_number} {instance.street_predirection} {instance.street_name} {instance.postdirection} {instance.street_suffix}"
        addressLine2 = f"{instance.secondary_designator} {instance.secondary_number}"
        addressLine3 = f"{instance.extra_secondary_designator} {instance.extra_secondary_number}"
        cityStateZip = f"f{instance.city_name}, {instance.state_abbreviation} {instance.zipcode}"
        address = Address(
            line=[addressLine1, addressLine2, addressLine3, cityStateZip],
            use=address.address_type.value
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
    phone_number = serializers.CharField(
        source='phonenumber__value', read_only=True)
    system = serializers.CharField(
        source='fhirphonesystem__value', read_only=True)
    use = serializers.CharField(source='fhirphoneuse__value', read_only=True)
    extension = serializers.CharField(read_only=True)

    class Meta:
        fields = ['phone_number', 'system', 'use', 'extension']

    def to_representation(self, instance):
        phone_contact = ContactPoint(
            system=instance.system,
            use=instance.use,
            value=f"{instance.phone_number} ext. {instance.extension}"
        )
        return phone_contact.model_dump()


class TaxonomySerializer(serializers.Serializer):
    id = serializers.CharField(source='nucctaxonomycode__id', read_only=True)
    display_name = serializers.CharField(
        source='nucctaxonomycode__display_name', read_only=True)

    class Meta:
        fields = ['id', 'display_name']

    def to_representation(self, instance):
        code = CodeableConcept(
            coding=[Coding(
                system="http://nucc.org/provider-taxonomy",
                code=instance.nucc_taxonomy_code_id,
                display=nucc_taxonomy_codes[instance.nucc_taxonomy_code_id]
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
                    display=other_identifier_type[other_identifier_type_id]
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
                  'effective_date', 'end_date', 'prefix', 'suffix']

    def to_representation(self, name):
        name_parts = [part for part in [name.prefix, name.first_name,
                                        name.middle_name, name.last_name, name.suffix] if part != '' and part is not None]
        human_name = HumanName(
            use=fhir_name_use[name.fhir_name_use_id],
            text=' '.join(name_parts),
            family=name.last_name,
            given=[name.first_name, name.middle_name],
            prefix=[name.prefix],
            suffix=[name.suffix],
            period=Period(
                start=name.effective_date,
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

    class Meta:
        fields = ['name', 'email', 'phone']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        individual = {
            'name': representation['name']
        }
        telecom = []
        if 'phone' in representation.keys():
            telecom.append(representation['phone'])
        if 'email' in representation.keys():
            telecom.append(representation['email'])
        individual['telecom'] = telecom
        return individual


class PractitionerSerializer(serializers.Serializer):
    npi = NPISerializer()
    individual = IndividualSerializer(read_only=True)
    identifier = OtherIdentifierSerializer(
        source='providertootheridentifier_set', many=True, read_only=True)
    taxonomy = TaxonomySerializer(
        source='providertonucctaxonomycode_set', many=True, read_only=True)

    class Meta:
        fields = ['npi', 'name', 'email', 'phone', 'identifier', 'taxonomy']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # print(type(instance))
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
        practitioner.telecom = representation['individual']['telecom']
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
            print(resource)
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
