from bidict import bidict


class Mapping():
    def __init__(self, mapping: dict):
        self.mapping = bidict(mapping)

    def toFHIR(self, npdValue):
        if npdValue is None:
            return npdValue
        else:
            return self.mapping[npdValue]

    def toNPD(self, fhirValue):
        if fhirValue is None:
            return fhirValue
        else:
            return self.mapping.inverse[fhirValue]

    def keys(self, which='fhir'):
        if which == 'npd':
            return list(self.mapping.keys())
        else:
            return list(self.mapping.inverse.keys())
        
    def to_choices(self):
        fhir_values = self.keys(which='fhir')
        return [(v, v) for v in fhir_values]

genderMapping = Mapping(
    {
        "F": "Female",
        "M": "Male",
        "O": "Other"
    }
)

addressUseMapping = Mapping(
    {
        1: "home",
        2: "work",
        3: "temp",
        4: "old",
        5: "billing"
    }
)
