Good Payer FHIR Endpoint Definition
================

* No authentication or token required
* Allows search via InsurancePlan, Location, Organization, PractionerRole and Practicioner with no parameter. At least these.. but perhaps all of them?
* the web UI allows testing inline, swagger style. 
* There are NPIs in the results
* There are organizational NPIs in the organizations
* The NPIs in the results are valid
* The payer hosts the FHIR API on the same root domain name as they advertize to patients
* The payer hosts the FHIR API documentation on the same root domain as they advertize to patients
* If not on the same domain (i.e. hosting is outsourced) then the payers name should appear prominantly in the URL somewhere. In this case there is also need for the documentation to be on the patient-facing domain that links to the vendors API url. We should not have to guess which is the legitimate API for a given payer.
* None of the links on their developer website are broken
* The homepage of the FHIR API documenteation actually tells you what the base url is for the provider directory endpoint. 
* The URL is https with current certificates, in the major browser bundles (i.e. not self-signed)
* links to the swagger url is available in the docs if there is a swagger url
* links to the OpenAPI url is available in the docs if there is one 
* links to the capabilities statement and metadata links is available in the docs if there is one. 
* All query parameters in the capabilities statements should function as advertized
* All features more generatlly in the capabilities statement should be correct
* Addresses are in Location resources, and linked rather than inline. Rather than "address" items in the json
* PracticionerRole are connected to Organizations and Locations
* Resource is JSON by default not XML
* The resource does not cause a download of a file, but instead opens in a normal browser connection. 
* InsurancePlan needs to be connected to Networks which are connected to Locations and PractionerRoles and Orgs in order to do full plan modeling
* PractiionerRole needs to be igdentifical between Networks and InsurancePlans, they should be reused. 


IG Changes
-----------
* Currently there is a PlanNet IG spec that says there is one ProviderRole to one Network. A ProviderRole that is otherwise identical needs to be copied between networks. Payers have millions of practicionerroles. This is unreasonable. 



