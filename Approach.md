# National Health Directory Approach and Strategy

## Strategy

### Foundational Technology Strategy

 • No Proprietary Lock-in: Avoid proprietary technologies, platforms, or services.
 • Long-Term Sustainability: Plan for a 50-year timeline using mature, widely adopted technologies.
 • Preference for Old and Stable Tools: Prioritize tools with 10+ years of proven utility.

### Data Processing and Integration

 • Universal Execution Contexts: Ensure support in Python, Jupyter Notebooks, Unix CLI, and SAS.
 • SQL-Centric Processing: Use plain SQL for transformations, interleaved with Python.

### Scalability and Accessibility

 • Dual Schema Design: Separate public and private schemas.
 • Downloadable Data: Support bulk access with moderate API load.

### Compatibility Requirements

 • Full NPES Backward Compatibility:
 • Reproduce NPES flat files
 • Maintain entity types, Medicare codes, and NUCC taxonomy
 • Claims & Regulatory Continuity:
 • Support Medicaid, ACOs, QHPs, FQHCs, and legacy systems

### FHIR Compliance

 • Strict Schema Alignment: Must pass validation against FHIR schemas.
 • Correct Resource Use: Use FHIR elements per spec (e.g., PractitionerRole).

### Data Quality and Feedback

 • Validate When Possible: Fully validate or track confidence levels.
 • User Feedback Channels:
 • Patient-facing UX for data accuracy
 • Token-limited write-back API for structured corrections

### Decision-Making Heuristics

 • Reliable > Experimental: Use proven tools.
 • Preserve the Past, Enable the Future: Ensure backward/future compatibility.

## Engineering Process Philosophy

### Git-Based Collaboration

 • Use Git/GitHub workflows.
 • Clean, small PRs preferred, but large PRs accepted when necessary.
 • Emphasize clarity and forward momentum.

### Test-Driven Expectations

 • Expectations Before APIs: Define tests before implementation.
 • Test-Driven Data Models: Built alongside ETLs with validations.
 • ETL Resilience by Design:
 • Validate assumptions
 • Break early and loudly on errors

### Anti-Fragile Infrastructure

 • Fail Loudly, Recover Quickly: Small, fragile components improve system robustness.
 • Continuous Feedback Loops: Tests and checks detect degradations early.

### Legacy Respect: The Joel on Software Principle

 • No Clean Slate Rebuilds: Avoid rewrites; understand existing code first.
 • Inherited Code is Knowledge: Features represent hard-earned lessons.
 • Respect Before Refactor: Prior design is valid until proven otherwise.
 • Avoid Reinventing Mistakes: Rewrites risk losing key insights.
 • Evolve, Don’t Replace: Improve incrementally.

## FHIR and NDH Implementation Summary

### FHIR Standards and Schema Validation

 • Validate against:
 • FHIR Core
 • US Core (minimum required)
 • FAST NDH Profiles
 • Understand profile hierarchy: FHIR Core → US Core → NDH
 • Key HL7 profile tabs:
 • Differential: What’s changed
 • Snapshot: Full schema view
 • Key Elements: Essential fields

### Terminologies & Functional Coding

 • Use SNOMED codes in PractitionerRole for services
 • Continue using NUCC taxonomy for classifications

### Account Access

 • Ensure team members have:
 • VSAC (Value Set Authority Center) access
 • Active UMLS credentials

### Direct Address Representation

 • List direct addresses in:
 • telecom field
 • endpoint resource

### Available Time & Scheduling

 • Use availableTime in PractitionerRole
 • Link availableTime to specific Location
 • Investigate dynamic scheduling endpoint integration

### Location vs Organization Modeling

 • Use Location for places of care
 • Strategy:
 • Deduplicate locations across organizations
 • Link PractitionerRoles via Locations to simplify API

### Practitioner Names & Status

 • PractitionerRole requires full-text name
 • NDH requires all records active
 • Consider inactive NPIs for completeness

### Telecom Enhancements

 • telecom fields can have time-bound validity

### Location Geocoding

 • Not currently supported
 • Use extension for geocoding in this version

### Verification Object

 • verificationResult = whole-resource confidence
 • No sub-element confidence standard exists
 • Plan custom extension for sub-element confidence

### PractitionerRole & Licensing Strategy

 • Licensing is state-specific
 • Modeling strategy:
 • Create Location per state
 • Link PractitionerRole to correct state Location
 • Assign appropriate taxonomies

### Required Extensions

 • Geolocation support (extension)
 • Sub-element confidence (extension)
 • Aligned program participation tracking
