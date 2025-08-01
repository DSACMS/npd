from django.core.cache import cache
import json
from .models import OtherIdentifierType, FhirNameUse, NuccTaxonomyCode


def cacheData(model):
    name = model.__name__
    data = cache.get(name)
    if not data:
        data = {}
        for obj in model.objects.all():
            if hasattr(obj, 'display_name'):
                data[obj.id] = obj.display_name
            else:
                data[obj.id] = obj.value
        json_data = json.dumps(data)
        cache.set(name, json_data, timeout=60 * 5)
    else:
        data = json.loads(data)
    return data


other_identifier_type = cacheData(OtherIdentifierType)
fhir_name_use = cacheData(FhirNameUse)
nucc_taxonomy_codes = cacheData(NuccTaxonomyCode)
