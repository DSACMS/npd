"""
OpenAPI schemas for FHIR resources needed to populate response examples within our OpenAPI 3.0 documentation which is generated using drf-spectacular

Edits made to the final FHIR return objects for each endpoint must be reflected here. 
"""

# Im assuming that this can be automated to a degree when we bolster our testing with the addition of fixtures and factories 


ENDPOINT_SCHEMA = {
    "type": "object",
    "properties": {
        "resourceType": {"type": "string", "example": "Endpoint"},
        "id": {"type": "string", "format": "uuid"},
        "identifier": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string"},
                    "value": {"type": "string"}
                }
            }
        },
        "status": {"type": "string", "enum": ["active", "suspended", "error", "off", "entered-in-error", "test"]},
        "connectionType": {
            "type": "object",
            "properties": {
                "system": {"type": "string"},
                "code": {"type": "string"},
                "display": {"type": "string"}
            }
        },
        "name": {"type": "string"},
        "payloadType": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "coding": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "system": {"type": "string"},
                                "code": {"type": "string"},
                                "display": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "address": {"type": "string", "format": "uri"},
        "header": {"type": "array", "items": {"type": "string"}}
    }
}


PRACTITIONER_SCHEMA = {
    "type": "object",
    "properties": {
        "resourceType": {"type": "string", "example": "Practitioner"},
        "id": {"type": "string", "format": "uuid"},
        "identifier": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string"},
                    "value": {"type": "string"}
                }
            }
        },
        "active": {"type": "boolean"},
        "name": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "use": {"type": "string"},
                    "text": {"type": "string"},
                    "family": {"type": "string"},
                    "given": {"type": "array", "items": {"type": "string"}},
                    "prefix": {"type": "array", "items": {"type": "string"}},
                    "suffix": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "telecom": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string"},
                    "value": {"type": "string"},
                    "use": {"type": "string"}
                }
            }
        },
        "address": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "line": {"type": "array", "items": {"type": "string"}},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "postalCode": {"type": "string"},
                    "country": {"type": "string"}
                }
            }
        },
        "gender": {"type": "string"},
        "qualification": {
            "type": "array",
            "items": {"type": "object"}
        }
    }
}


PRACTITIONER_ROLE_SCHEMA = {
    "type": "object",
    "properties": {
        "resourceType": {"type": "string", "example": "PractitionerRole"},
        "id": {"type": "string", "format": "uuid"},
        "active": {"type": "boolean"},
        "practitioner": {
            "type": "object",
            "properties": {
                "reference": {"type": "string"},
                "display": {"type": "string"}
            }
        },
        "organization": {
            "type": "object",
            "properties": {
                "reference": {"type": "string"},
                "display": {"type": "string"}
            }
        },
        "location": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "reference": {"type": "string"},
                    "display": {"type": "string"}
                }
            }
        },
        "telecom": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string"},
                    "value": {"type": "string"}
                }
            }
        }
    }
}


ORGANIZATION_SCHEMA = {
    "type": "object",
    "properties": {
        "resourceType": {"type": "string", "example": "Organization"},
        "id": {"type": "string", "format": "uuid"},
        "identifier": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string"},
                    "value": {"type": "string"}
                }
            }
        },
        "active": {"type": "boolean"},
        "type": {"type": "array", "items": {"type": "object"}},
        "name": {"type": "string"},
        "alias": {"type": "array", "items": {"type": "string"}},
        "telecom": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string"},
                    "value": {"type": "string"}
                }
            }
        },
        "address": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "line": {"type": "array", "items": {"type": "string"}},
                    "city": {"type": "string"},
                    "state": {"type": "string"},
                    "postalCode": {"type": "string"}
                }
            }
        }
    }
}


LOCATION_SCHEMA = {
    "type": "object",
    "properties": {
        "resourceType": {"type": "string", "example": "Location"},
        "id": {"type": "string", "format": "uuid"},
        "status": {"type": "string"},
        "name": {"type": "string"},
        "telecom": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string"},
                    "value": {"type": "string"}
                }
            }
        },
        "address": {
            "type": "object",
            "properties": {
                "line": {"type": "array", "items": {"type": "string"}},
                "city": {"type": "string"},
                "state": {"type": "string"},
                "postalCode": {"type": "string"}
            }
        },
        "managingOrganization": {
            "type": "object",
            "properties": {
                "reference": {"type": "string"}
            }
        }
    }
}


CAPABILITY_STATEMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "resourceType": {"type": "string", "example": "CapabilityStatement"},
        "url": {"type": "string"},
        "version": {"type": "string"},
        "name": {"type": "string"},
        "title": {"type": "string"},
        "status": {"type": "string"},
        "date": {"type": "string", "format": "date-time"},
        "publisher": {"type": "string"},
        "description": {"type": "string"},
        "kind": {"type": "string"},
        "fhirVersion": {"type": "string"},
        "format": {"type": "array", "items": {"type": "string"}},
        "rest": {"type": "array", "items": {"type": "object"}}
    }
}
