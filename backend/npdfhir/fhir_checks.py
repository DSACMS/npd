import re
from fhir.resources.valueset import ValueSet
from fhir.resources.practitioner import Practitioner 
from pydantic import ValidationError
from django.db import connection


def parse_nucc_codes_into_dicts(db_result):
    codes = {}
    for nucc_code_record in db_result:
        codes[nucc_code_record[0]] = nucc_code_record[1]
    
    return codes

def get_nucc_codes_from_db():
    query = """
        SELECT nucc_code, display_name, nucc_grouping_id
        FROM npd.nucc_classification;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    return parse_nucc_codes_into_dicts(results)

def is_valid_npi_format(npi_value):

    digits_only = re.sub(r'\D', '', str(npi_value))
    npi_num = int(digits_only)
    return 999999999 <= npi_num <= 10000000000

#NPI luhn algo defined here: 
#https://build.fhir.org/ig/HL7/US-Core/StructureDefinition-us-core-practitioner.profile.json.html
def npi_check_luhn_algorithm(npi_value):
    def transform(d):
        return d * 2 if d < 5 else d * 2 - 9
    
    digits_only = re.sub(r'\D', '', str(npi_value))

    digits = [int(ch) for ch in digits_only[:10]]

    total = sum(
        transform(d) if i % 2 == 0 else d
        for i, d in enumerate(digits)
    ) + 24

    return total % 10 == 0


class BaseVerifier:
    """
        Class that uses pydantic to verify the FHIR schema as
        pulled from the fhir.resources package.

        fhir_resource_type : attribute that determines the fhir schema to validate.
    """
    def __init__(self,fhir_obj):
        self.fhir_resource_type = fhir_obj

    def fhir_resource_validate_schema(self,data):
        #Use pydantic and fhir resources to validate the schema
        try:
            _ = self.fhir_resource_type.model_validate_json(data)
        except ValidationError as e:
            print(f"Data was found that violates {self.fhir_resource_type.__name__} schema:")
            print(f"Data: {data}")
            raise e
    
    def verification_steps(self,data):
        """
        Method that can be overwritten with the validation steps for differant schemas
        """
        self.fhir_resource_validate_schema(data)


    def bulk_verify(self, entry_list):
        """
        Pass the 'entry' list from a bundle fhir object into entry_list

        Args:
            entry_list (list): list of fhir entities to validate
        """

        errors = []
        for entry in entry_list:
            try:
                self.verification_steps(entry)
            except ValidationError as e:
                errors.append(e)
        
        if len(errors) > 0:
            print(f"Found {len(errors)} validation errors!")
            #Requires python 3.11+
            raise ExceptionGroup("Validation Errors Summary", errors)

class FHIRValueSetVerifier(BaseVerifier):
    """
        Class that uses pydantic to verify the FHIR schema as
        pulled from the fhir.resources package. 

        Is meant to be specific to ValueSet to validate nucc codes
        as taken from the database. 
    """
    def __init__(self):
        self.fhir_resource_type = ValueSet
    
    def verify_codes(self,data):
        nucc_codes = get_nucc_codes_from_db()

        for include_index, codeItem in enumerate(data['compose']['include']):
            #Check if code in ValueSet is part of nucc
            if "nucc.org/provider-taxonomy" in codeItem['system']:
                for concept_index, codeValue in enumerate(codeItem['concept']):
                    try:
                        assert codeValue['code'] in nucc_codes.keys()
                    except AssertionError as e:
                        print(f"Code {codeValue['code']} is not a valid nucc code!")
                        raise ValidationError(
                            [
                                {
                                    "type": "assertion_error",
                                    "loc": ('compose','include',include_index,'concept', concept_index,'code',),
                                    "msg": str(e)
                                }
                            ],
                            model=self.fhir_resource_type,
                        )
            elif "snomed.info/sct" in codeItem['system']:
                raise NotImplementedError
            
    
    def verification_steps(self,data):
        self.fhir_resource_validate_schema(data)
        self.verify_codes(data)


class PractitionerVerifier(BaseVerifier):
    def __init__(self):
        self.fhir_resource_type = Practitioner

    def verify_npi(self,npi,position):
        if not is_valid_npi_format(npi):
            raise ValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ('identifier',position,'value',),
                        "msg": "Npi value is not valid because of format!"
                    }
                ],
                model=self.fhir_resource_type
            )
        if not npi_check_luhn_algorithm(npi):
            raise ValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ('identifier',position,'value',),
                        "msg": "Npi value is not valid because of luhn algo failing!"
                    }
                ],
                model=self.fhir_resource_type
            )
