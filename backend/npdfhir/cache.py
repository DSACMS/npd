from django.core.cache import cache
import json
from .models import OtherIdType, FhirNameUse, Nucc, FhirPhoneUse
import sys


def cacheData(model):
    name = model.__name__
    data = cache.get(name)
    if not data:
        data = {}
        for obj in model.objects.all():
            if hasattr(obj, 'display_name'):
                data[str(obj.code)] = obj.display_name
            else:
                data[str(obj.id)] = obj.value
        json_data = json.dumps(data)
        cache.set(name, json_data, timeout=60 * 5)
    else:
        data = json.loads(data)
    return data


if 'runserver' or 'test' in sys.argv:
    other_identifier_type = cacheData(OtherIdType)
    fhir_name_use = cacheData(FhirNameUse)
    nucc_taxonomy_codes = cacheData(Nucc)
    fhir_phone_use = cacheData(FhirPhoneUse)
