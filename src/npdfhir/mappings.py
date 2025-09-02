from bidict import bidict

class Mapping():
    def __init__(self, mapping: dict):
        self.mapping=bidict(mapping)
    def toFHIR(self, ndhValue):
        if ndhValue is None:
            return ndhValue
        else:
            return self.mapping[ndhValue]
    def toNDH(self, fhirValue):
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