"""
Module that contains functionality to easily validate fhir json.

Uses Pydantic to validate the json schema as well as added methods
that make sure that the codes and identifiers present are valid.
"""

import re
from fhir.resources.valueset import ValueSet
from fhir.resources.practitioner import Practitioner
from pydantic import ValidationError
from django.db import connection



def verify_codes(cls,data):
        """
        Verifies the code items present in the valueset 

        Args:
            data (dict): json dictionary representing fhir data

        Raises:
            ValidationError: raises a validationError if the codes are not part of a 
            known valid code
        """

        def parse_codes_into_dicts(db_result):
            """
            Parses a db cursor result into a dict with proper keys

            Args:
                db_result: A list of tuples representing the result of a select

            Returns:
                dict: Returns a mapping of the codes to what they correspond to in the db
            """
            codes = {}
            for code_record in db_result:
                codes[code_record[0]] = code_record[1]

            return codes

        def get_nucc_codes_from_db():
            """
            Function that fetches nucc codes from the db
            """

            query = """
                SELECT nucc_code, display_name, nucc_grouping_id
                FROM npd.nucc_classification;
            """

            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

            return parse_codes_into_dicts(results)

        def get_c80_codes_from_db():
            """
            Function that fetches c80 codes from db
            """

            query = """
                SELECT code, display_name
                FROM npd.c80_practice_codes;
            """

            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

            return parse_codes_into_dicts(results)

        nucc_codes = get_nucc_codes_from_db()
        c80_codes = get_c80_codes_from_db()

        for include_index, code_item in enumerate(data['compose']['include']):
            #Check if code in ValueSet is part of nucc

            for concept_index, code_value in enumerate(code_item['concept']):
                try:
                    if "nucc.org/provider-taxonomy" in code_item['system']:
                        assert code_value['code'] in nucc_codes
                    elif "snomed.info/sct" in code_item['system']:
                        assert code_value['code'] in c80_codes
                except AssertionError as e:
                    print(f"Code {code_value['code']} is not a valid {code_value['system']} code!")
                    raise ValidationError(
                        [
                            {
                                "type": "assertion_error",
                                "loc": (
                                    'compose',
                                    'include',
                                    include_index,
                                    'concept',
                                    concept_index,
                                    'code',
                                ),
                                "msg": str(e)
                            }
                        ],
                        model=self.fhir_resource_type,
                    ) from e

ValueSet.add_root_validator(verify_codes, pre=False)


def verify_identifier_code_from_data(cls,data):
    """
    Iterates through json data and verifies the identifiers present

    Args:
        data (dict): json dictionary representing fhir data
    """

    def verify_npi(self,npi,position):
        """
        Checks the npi code against various checks and throws errors if they fail.

        Args:
            npi (str): npi identifier string
            position (int): index where npi is found in the json

        Raises:
            ValidationError: Error thrown when npi value is out of range
            ValidationError: Error thrown when npi value fails luhn algo
        """

        def is_valid_npi_format(npi_value):
            """
            Checks npi value string for correct range and digits

            Args:
                npi_value (str): npi identifier string

            Returns:
                bool: True if value is valid
            """

            digits_only = re.sub(r'\D', '', str(npi_value))
            npi_num = int(digits_only)
            return 999999999 <= npi_num <= 10000000000

        #NPI luhn algo defined here:
        #https://build.fhir.org/ig/HL7/US-Core/StructureDefinition-us-core-practitioner.profile.json.html
        def npi_check_luhn_algorithm(npi_value):
            """
            Checks npi value string based on given luhn algorithm

            Transforms every other digit and sums them together plus 24

            If the result is divisible by 10 then the npi value is valid

            Args:
                npi_value (str): npi identifier string
            """

            def transform(d):
                return d * 2 if d < 5 else d * 2 - 9

            digits_only = re.sub(r'\D', '', str(npi_value))

            digits = [int(ch) for ch in digits_only[:10]]

            total = sum(
                transform(d) if i % 2 == 0 else d
                for i, d in enumerate(digits)
            ) + 24

            return total % 10 == 0

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

    for identifier_index, identifier in enumerate(data['identifier']):
        if "hl7.org/fhir/sid/us-npi" in identifier['system']:
            self.verify_npi(identifier['value'],identifier_index)

Practitioner.add_root_validator(verify_identifier_code_from_data, pre=False)
