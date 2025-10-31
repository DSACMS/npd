from drf_spectacular.utils import OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

def get_endpoint_response_example():
    example_data = {
        "count": 1,
        "next": "http://localhost:8000/fhir/Endpoint/?page=2",
        "previous": None,
        "results": {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 1,
            "entry": [
                {
                    "fullUrl": "http://localhost:8000/fhir/Endpoint/12300000-0000-0000-0000-000000000123",
                    "resource": {
                        "resourceType": "Endpoint",
                        "id": "12300000-0000-0000-0000-000000000123",
                        "identifier": [
                            {
                                "use": "official",
                                "system": "https://resources.systems.fhir-org-list.json",
                                "value": "123456789",
                                "assigner": {
                                    "display": "12300000-0000-0000-0000-000000000123"
                                }
                            }
                        ],
                        "status": "active",
                        "connectionType": {
                            "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                            "code": "hl7-fhir-rest",
                            "display": "HL7 FHIR"
                        },
                        "name": "EXAMPLE HEALTH CLINIC",
                        "payloadType": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/endpoint-payload-type",
                                        "code": "hl7-org",
                                        "display": "ccda"
                                    }
                                ]
                            }
                        ],
                        "address": "email@health.org",
                        "header": [
                            "application/fhir"
                        ]
                    }
                }
            ]
        }
    }
    
    return {
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description='Successful response with FHIR Bundle containing Endpoint resources',
            examples=[
                OpenApiExample(
                    name='FHIR Endpoint Bundle',
                    value=example_data,
                    response_only=True,
                )
            ]
        )
    }
