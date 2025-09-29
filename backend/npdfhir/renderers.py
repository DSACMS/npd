from rest_framework.renderers import JSONRenderer

class FHIRRenderer(JSONRenderer):
    """
    Custom renderer for FHIR resources that set the proper content type
    """

    media_type="application/fhir+json"
    format="fhir+json"
