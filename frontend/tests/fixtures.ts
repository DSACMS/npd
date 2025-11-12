export const DEFAULT_FRONTEND_SETTINGS: FrontendSettings = {
  require_authentication: false,
  user: { is_anonymous: false, username: "testuser" },
  feature_flags: {},
}

export const DEFAULT_ORGANIZATION: FhirOrganization = {
  resourceType: "Organization",
  id: "3ac907f0-c7d0-484e-ad0e-653dd011a55b",
  meta: {
    profile: [
      "http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization",
    ],
  },
  identifier: [
    {
      use: "official",
      type: {
        coding: [
          {
            system: "http://terminology.hl7.org/CodeSystem/v2-0203",
            code: "PRN",
            display: "Provider number",
          },
        ],
      },
      system: "http://terminology.hl7.org/NamingSystem/npi",
      value: "1679576367",
      period: {
        start: "2005-05-27T00:00:00",
      },
    },
  ],
  name: "1ST CHOICE HOME HEALTH CARE INC",
  contact: [
    {
      name: {
        use: "official",
        text: "REBECCA CARNELL",
        family: "CARNELL",
        given: ["REBECCA", null],
        prefix: [null],
        suffix: [null],
        period: {},
      },
      telecom: [
        {
          system: "phone",
          value: "9072605959",
          use: "work",
        },
      ],
    },
  ],
}
