import traceback
import re
import requests
import time
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
    return len(digits_only) == 10

def verify_npi_against_api(npi_value, max_retries = 3, delay = 0.1):
    clean_npi = re.sub(r'\D', '', str(npi_value))

    url = f"https://npiregistry.cms.hhs.gov/api/?version=2.1&number={clean_npi}"

    for attempt in range(max_retries):
        try:
            # Add a small delay to be respectful to the API
            if attempt > 0:
                time.sleep(delay * (2 ** attempt))
            
            response = requests.get(url,timeout=10)
            response.raise_for_status()

            data = response.json()
            result_count = data.get('result_count',0)

            return result_count > 0
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise requests.exceptions.RequestException("Not able to verify npi against the api!") from e
            
            continue
    
    print("Max retries exceeded!")
    raise Exception("Too many retries")


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
    
    def verify_nucc_codes(self,data):
        nucc_codes = get_nucc_codes_from_db()

        for codeItem in data['compose']['include']:
            #Check if code in ValueSet is part of nucc
            if "nucc.org/provider-taxonomy" in codeItem['system']:
                for codeValue in codeItem['concept']:
                    try:
                        assert codeValue['code'] in nucc_codes.keys()
                    except AssertionError as e:
                        print(f"Code {codeValue['code']} is not a valid nucc code!")
                        raise ValidationError from e
    
    def verification_steps(self,data):
        self.fhir_resource_validate_schema(data)
        self.verify_nucc_codes(data)


class PractitionerVerifier(BaseVerifier):
    def __init__(self):
        self.fhir_resource_type = Practitioner

    def verify_npi(self,npi):
        if not is_valid_npi_format(npi):
            raise ValidationError
        
        
        if not verify_npi_against_api(npi):
            raise ValidationError

