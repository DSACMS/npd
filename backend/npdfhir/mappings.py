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


genderMapping = Mapping(
    {
        "F": "Female",
        "M": "Male",
        "O": "Other"
    }
)
