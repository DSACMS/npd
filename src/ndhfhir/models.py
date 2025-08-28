# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Address(models.Model):
    barcode_delivery_code = models.CharField(max_length=12, blank=True, null=True)
    smarty_key = models.CharField(max_length=10, blank=True, null=True)
    address_us = models.ForeignKey('AddressUs', models.DO_NOTHING, blank=True, null=True)
    address_international = models.ForeignKey('AddressInternational', models.DO_NOTHING, blank=True, null=True)
    address_nonstandard = models.ForeignKey('AddressNonstandard', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'address'


class AddressInternational(models.Model):
    address_id = models.IntegerField()
    input_id = models.CharField(max_length=36, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    geocode = models.CharField(max_length=4, blank=True, null=True)
    local_language = models.CharField(max_length=6, blank=True, null=True)
    freeform = models.CharField(max_length=512, blank=True, null=True)
    address1 = models.CharField(max_length=64, blank=True, null=True)
    address2 = models.CharField(max_length=64, blank=True, null=True)
    address3 = models.CharField(max_length=64, blank=True, null=True)
    address4 = models.CharField(max_length=64, blank=True, null=True)
    organization = models.CharField(max_length=64, blank=True, null=True)
    locality = models.CharField(max_length=64, blank=True, null=True)
    administrative_area = models.CharField(max_length=32, blank=True, null=True)
    postal_code = models.CharField(max_length=16, blank=True, null=True)
    administrative_area_iso2 = models.CharField(max_length=8, blank=True, null=True)
    sub_administrative_area = models.CharField(max_length=64, blank=True, null=True)
    country_iso_3 = models.CharField(max_length=3, blank=True, null=True)
    premise = models.CharField(max_length=64, blank=True, null=True)
    premise_number = models.CharField(max_length=64, blank=True, null=True)
    thoroughfare = models.CharField(max_length=64, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    geocode_precision = models.CharField(max_length=32, blank=True, null=True)
    max_geocode_precision = models.CharField(max_length=32, blank=True, null=True)
    address_format = models.CharField(max_length=128, blank=True, null=True)
    verification_status = models.CharField(max_length=32, blank=True, null=True)
    address_precision = models.CharField(max_length=32, blank=True, null=True)
    max_address_precision = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'address_international'


class AddressNonstandard(models.Model):
    address_id = models.IntegerField()
    input_id = models.CharField(max_length=36, blank=True, null=True)
    input_index = models.IntegerField(blank=True, null=True)
    candidate_index = models.IntegerField(blank=True, null=True)
    addressee = models.CharField(max_length=64, blank=True, null=True)
    delivery_line_1 = models.CharField(max_length=64, blank=True, null=True)
    delivery_line_2 = models.CharField(max_length=64, blank=True, null=True)
    last_line = models.CharField(max_length=64, blank=True, null=True)
    address_type = models.CharField(max_length=32, blank=True, null=True)
    address_format = models.CharField(max_length=128, blank=True, null=True)
    raw_address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'address_nonstandard'


class AddressUs(models.Model):
    address_id = models.IntegerField()
    input_id = models.CharField(max_length=36, blank=True, null=True)
    input_index = models.IntegerField(blank=True, null=True)
    candidate_index = models.IntegerField(blank=True, null=True)
    addressee = models.CharField(max_length=64, blank=True, null=True)
    delivery_line_1 = models.CharField(max_length=64, blank=True, null=True)
    delivery_line_2 = models.CharField(max_length=64, blank=True, null=True)
    last_line = models.CharField(max_length=64, blank=True, null=True)
    delivery_point_barcode = models.CharField(max_length=12, blank=True, null=True)
    urbanization = models.CharField(max_length=64, blank=True, null=True)
    primary_number = models.CharField(max_length=30, blank=True, null=True)
    street_name = models.CharField(max_length=64, blank=True, null=True)
    street_predirection = models.CharField(max_length=16, blank=True, null=True)
    street_postdirection = models.CharField(max_length=16, blank=True, null=True)
    street_suffix = models.CharField(max_length=16, blank=True, null=True)
    secondary_number = models.CharField(max_length=32, blank=True, null=True)
    secondary_designator = models.CharField(max_length=16, blank=True, null=True)
    extra_secondary_number = models.CharField(max_length=32, blank=True, null=True)
    extra_secondary_designator = models.CharField(max_length=16, blank=True, null=True)
    pmb_designator = models.CharField(max_length=16, blank=True, null=True)
    pmb_number = models.CharField(max_length=16, blank=True, null=True)
    city_name = models.CharField(max_length=64, blank=True, null=True)
    default_city_name = models.CharField(max_length=64, blank=True, null=True)
    state_code = models.ForeignKey('FipsState', models.DO_NOTHING, db_column='state_code', blank=True, null=True)
    zipcode = models.CharField(max_length=5, blank=True, null=True)
    plus4_code = models.CharField(max_length=4, blank=True, null=True)
    delivery_point = models.CharField(max_length=2, blank=True, null=True)
    delivery_point_check_digit = models.CharField(max_length=1, blank=True, null=True)
    record_type = models.CharField(max_length=1, blank=True, null=True)
    zip_type = models.CharField(max_length=32, blank=True, null=True)
    county_code = models.ForeignKey('FipsCounty', models.DO_NOTHING, db_column='county_code', blank=True, null=True)
    ews_match = models.CharField(max_length=5, blank=True, null=True)
    carrier_route = models.CharField(max_length=4, blank=True, null=True)
    congressional_district = models.CharField(max_length=2, blank=True, null=True)
    building_default_indicator = models.CharField(max_length=1, blank=True, null=True)
    rdi = models.CharField(max_length=12, blank=True, null=True)
    elot_sequence = models.CharField(max_length=4, blank=True, null=True)
    elot_sort = models.CharField(max_length=4, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    coordinate_license = models.IntegerField(blank=True, null=True)
    geo_precision = models.CharField(max_length=18, blank=True, null=True)
    time_zone = models.CharField(max_length=48, blank=True, null=True)
    utc_offset = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    dst = models.CharField(max_length=5, blank=True, null=True)
    dpv_match_code = models.CharField(max_length=1, blank=True, null=True)
    dpv_footnotes = models.CharField(max_length=32, blank=True, null=True)
    dpv_cmra = models.CharField(max_length=1, blank=True, null=True)
    dpv_vacant = models.CharField(max_length=1, blank=True, null=True)
    dpv_no_stat = models.CharField(max_length=1, blank=True, null=True)
    active = models.CharField(max_length=1, blank=True, null=True)
    footnotes = models.CharField(max_length=24, blank=True, null=True)
    lacslink_code = models.CharField(max_length=2, blank=True, null=True)
    lacslink_indicator = models.CharField(max_length=1, blank=True, null=True)
    suitelink_match = models.CharField(max_length=5, blank=True, null=True)
    enhanced_match = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'address_us'


class ClinicalCredential(models.Model):
    acronym = models.CharField(max_length=20)
    name = models.CharField(max_length=100, blank=True, null=True)
    source_url = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clinical_credential'


class ClinicalSchool(models.Model):
    name = models.CharField(max_length=20)
    url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clinical_school'


class FhirAddressUse(models.Model):
    value = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'fhir_address_use'


class FhirNameUse(models.Model):
    value = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'fhir_name_use'


class FhirPhoneSystem(models.Model):
    value = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fhir_phone_system'


class FhirPhoneUse(models.Model):
    value = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'fhir_phone_use'


class FipsCounty(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=200)
    fips_state = models.ForeignKey('FipsState', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'fips_county'


class FipsState(models.Model):
    id = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(unique=True, max_length=100)
    abbreviation = models.CharField(unique=True, max_length=2)

    class Meta:
        managed = False
        db_table = 'fips_state'


class Individual(models.Model):
    ssn = models.CharField(max_length=10, blank=True, null=True)
    gender_code = models.CharField(max_length=1, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    id = models.UUIDField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'individual'


class IndividualToAddress(models.Model):
    pk = models.CompositePrimaryKey('individual_id', 'address_id')
    address_use = models.ForeignKey(FhirAddressUse, models.DO_NOTHING)
    address = models.ForeignKey(Address, models.DO_NOTHING)
    individual = models.ForeignKey(Individual, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'individual_to_address'


class IndividualToEmailAddress(models.Model):
    email_address = models.CharField(primary_key=True, max_length=300)
    individual = models.ForeignKey(Individual, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'individual_to_email_address'


class IndividualToLanguageSpoken(models.Model):
    pk = models.CompositePrimaryKey('individual_id', 'language_spoken_id')
    language_spoken = models.ForeignKey('LanguageSpoken', models.DO_NOTHING)
    individual = models.ForeignKey(Individual, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'individual_to_language_spoken'


class IndividualToName(models.Model):
    pk = models.CompositePrimaryKey('individual_id', 'fhir_name_use_id', 'effective_date')
    last_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=21, blank=True, null=True)
    prefix = models.CharField(max_length=6, blank=True, null=True)
    suffix = models.CharField(max_length=6, blank=True, null=True)
    fhir_name_use = models.ForeignKey(FhirNameUse, models.DO_NOTHING)
    effective_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    individual = models.ForeignKey(Individual, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'individual_to_name'


class IndividualToPhoneNumber(models.Model):
    pk = models.CompositePrimaryKey('individual_id', 'phone_number_id', 'fhir_phone_use_id')
    fhir_phone_use = models.ForeignKey(FhirPhoneUse, models.DO_NOTHING)
    phone_number = models.ForeignKey('PhoneNumber', models.DO_NOTHING)
    extension = models.CharField(max_length=10, blank=True, null=True)
    fhir_phone_system = models.ForeignKey(FhirPhoneSystem, models.DO_NOTHING, blank=True, null=True)
    individual = models.ForeignKey(Individual, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'individual_to_phone_number'


class LanguageSpoken(models.Model):
    id = models.CharField(primary_key=True, max_length=2)
    value = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'language_spoken'


class MedicareProviderType(models.Model):
    value = models.CharField(unique=True)

    class Meta:
        managed = False
        db_table = 'medicare_provider_type'


class Npi(models.Model):
    npi = models.BigIntegerField(primary_key=True)
    entity_type_code = models.SmallIntegerField()
    replacement_npi = models.BigIntegerField(blank=True, null=True)
    enumeration_date = models.DateField()
    last_update_date = models.DateField()
    deactivation_reason_code = models.CharField(max_length=3, blank=True, null=True)
    deactivation_date = models.DateField(blank=True, null=True)
    reactivation_date = models.DateField(blank=True, null=True)
    certification_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'npi'


class NuccClassification(models.Model):
    nucc_taxonomy_code = models.ForeignKey('NuccTaxonomyCode', models.DO_NOTHING, blank=True, null=True)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    nucc_grouping = models.ForeignKey('NuccGrouping', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nucc_classification'


class NuccGrouping(models.Model):
    display_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nucc_grouping'


class NuccSpecialization(models.Model):
    nucc_taxonomy_code = models.ForeignKey('NuccTaxonomyCode', models.DO_NOTHING, blank=True, null=True)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    nucc_classification = models.ForeignKey(NuccClassification, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nucc_specialization'


class NuccTaxonomyCode(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    display_name = models.TextField()
    definition = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    certifying_board_name = models.TextField(blank=True, null=True)
    certifying_board_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nucc_taxonomy_code'


class NuccTaxonomyCodeToMedicareProviderType(models.Model):
    medicare_provider_type_id = models.IntegerField()
    nucc_taxonomy_code_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'nucc_taxonomy_code_to_medicare_provider_type'


class OtherIdentifierType(models.Model):
    value = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'other_identifier_type'


class PhoneNumber(models.Model):
    value = models.CharField(unique=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'phone_number'


class Provider(models.Model):
    npi = models.OneToOneField(Npi, models.DO_NOTHING, db_column='npi', primary_key=True)
    individual = models.OneToOneField(Individual, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'provider'


class ProviderToClinicalCredential(models.Model):
    pk = models.CompositePrimaryKey('individual_id', 'clinical_credential_id')
    clinical_credential = models.ForeignKey(ClinicalCredential, models.DO_NOTHING)
    receipt_date = models.DateField(blank=True, null=True)
    clinical_school_id = models.IntegerField(blank=True, null=True)
    individual = models.ForeignKey(Provider, models.DO_NOTHING, to_field='individual_id')

    class Meta:
        managed = False
        db_table = 'provider_to_clinical_credential'


class ProviderToNuccTaxonomyCode(models.Model):
    pk = models.CompositePrimaryKey('individual_id', 'nucc_taxonomy_code_id')
    nucc_taxonomy_code = models.ForeignKey(NuccTaxonomyCode, models.DO_NOTHING)
    is_primary = models.BooleanField()
    individual = models.ForeignKey(Provider, models.DO_NOTHING, to_field='individual_id')

    class Meta:
        managed = False
        db_table = 'provider_to_nucc_taxonomy_code'


class ProviderToOtherIdentifier(models.Model):
    pk = models.CompositePrimaryKey('individual_id', 'state_id', 'value', 'other_identifier_type_id', 'issuer_name')
    value = models.CharField(max_length=21)
    other_identifier_type = models.ForeignKey(OtherIdentifierType, models.DO_NOTHING)
    state = models.ForeignKey(FipsState, models.DO_NOTHING)
    issuer_name = models.CharField(max_length=81)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    individual = models.ForeignKey(Provider, models.DO_NOTHING, to_field='individual_id')

    class Meta:
        managed = False
        db_table = 'provider_to_other_identifier'
