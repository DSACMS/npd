# Puffin ETL Importers

[See Original](https://github.com/DSACMS/npd_Puffin/blob/main/ImportReadMe.md)

## [CEHRT FHIR Endpoints Importer Project](./CEHRT_FHIR_endpoints)

The CHERT FHIR Endpoints are the result of the ehr_fhir_npi_slurp repo, which documents how to create these CSV files

### Data Source Summary

The Lantern dataset is a public-use file derived from certified EHR vendor APIs that expose FHIR endpoint data, as required under the 21st Century Cures Act. Maintained by the Assistant Secretary for Technology Policy (formerly the ONC) Lantern’s core purpose is to test the technical conformity and availability of public FHIR endpoints associated with Electronic Health Record (EHR) systems. Each certified EHR vendor must publish a FHIR bulk data endpoint listing their customers’ individual endpoints, along with corresponding organizational NPIs.

Although Lantern itself is not the canonical source of this data, it offers a convenient and regularly updated snapshot in downloadable CSV format. This raw file enables downstream projects to easily integrate and test endpoint reachability and standards compliance. In this project, we use a separate scraper to parse and extract FHIR endpoint records from Lantern’s publication, storing them as CSV files for ingestion into the NDH data warehouse.

[The Lantern code is available on github.](https://github.com/onc-healthit/lantern-back-end)

### Data Source Details

* Schema Target: lantern_ehr_fhir_raw
* Table Target: ehr_fhir_url
* Download URL: REPLACE ME WITH NEW DSAC EHR SLURP URL
* Create Table Statement: [clean_npi_to_org_fhir_url.create_table_postgres.sql](./CEHRT_FHIR_endpoints/clean_npi_to_org_fhir_url.create_table_postgres.sql)


## [AHRQ CHSP Compendium Importer Project](./ahrq_chsp_compendium)

AHRQ Files are sourced from https://www.ahrq.gov/chsp/data-resources/compendium-2023.html

### Data Source Summary

The AHRQ Compendium of U.S. Health Systems is maintained by the Agency for Healthcare Research and Quality ([AHRQ](https://www.ahrq.gov/)) and provides a curated list of healthcare systems in the United States. It describes affiliations between hospitals, group practices, outpatient sites, nursing homes, and home health agencies within larger health systems. The compendium is derived from a merger of two commercial datasets: the American Hospital Association ([AHA](https://www.aha.org/)) Annual Survey and IQVIA’s [OneKey](https://www.iqvia.com/solutions/commercialization/data-and-information-management/onekey) dataset, which together offer the most comprehensive view of health system structure currently available.

Although the data has a significant lag—typically updated annually and often released nearly two years later—it remains a valuable reference due to the relative stability of system affiliations. The compendium includes two main files: one describing systems and another describing their constituent hospitals, which are identified using CMS Certification Numbers (CCNs). While CCNs do not directly link to organizational NPIs or Tax Identification Numbers (TINs), a supplemental VRDC dataset is under development to map these relationships and enhance interoperability.

This dataset is the main file that lists the systems.

### Data Source Details

* Schema Target: ahrq_chsp_raw
* Table Target: compendium
* Download URL https://www.ahrq.gov/chsp/data-resources/compendium-2023.html
* Create Table Statement: [chsp-compendium-2023.create_table_postgres.sql](./ahrq_chsp_compendium/chsp-compendium-2023.create_table_postgres.sql)


## [AHRQ CHSP Linkage Importer Project](./ahrq_chsp_linage)

AHRQ Files are sourced from https://www.ahrq.gov/chsp/data-resources/compendium-2023.html

### Data Source Summary

This is the Linkage file for the AHRQ Compendium. 


### Data Source Details

* Schema Target: ahrq_chsp_raw
* Table Target: compendium_linkage
* Download URL https://www.ahrq.gov/chsp/data-resources/compendium-2023.html
* Create Table Statement: [chsp-hospital-linkage-2023.create_table_postgres.sql](./ahrq_chsp_linage/chsp-hospital-linkage-2023.create_table_postgres.sql)


## [HHA All Owners Importer Project](./hha_all_owners)

There are several PECOS ownership files that are found here: https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy

### Data Source Summary

See the documentation for the Hospital Owners data for details. 

### Data Source Details

* Schema Target: pecos_raw
* Table Target: hha_all_owners
* Download URL https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy
* Create Table Statement: [HHA_All_Owners_2025.07.01.create_table_postgres.sql](./hha_all_owners/HHA_All_Owners_2025.07.01.create_table_postgres.sql)


## [Hospice All Owners Importer Project](./hospice_all_owners)

There are several PECOS ownership files that are found here: https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy

### Data Source Summary

See the documentation for the Hospital Owners data for details.

### Data Source Details

* Schema Target: pecos_raw
* Table Target: hospice_all_owners
* Download URL https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy
* Create Table Statement: [Hospice_All_Owners_2025.07.01.create_table_postgres.sql](./hospice_all_owners/Hospice_All_Owners_2025.07.01.create_table_postgres.sql)


## [Hospital All Owners Importer Project](./hospital_all_owners)

There are several PECOS ownership files that are found here: https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy

### Data Source Summary
The PECOS All Owners dataset is a recently released, publicly available resource derived from the CMS Provider Enrollment, Chain, and Ownership System (PECOS). It comprises multiple files, each corresponding to a healthcare facility type—such as hospitals, clinics, skilled nursing facilities, home health agencies, rural health clinics, hospice, and federally qualified health centers. Of these, the hospital and clinic ownership files are the most crucial for our purposes, as they reveal associations between organizational NPIs that are effectively part of the same corporate entity.

Central to this dataset is the concept of the PAC ID (PECOS Associate Control ID), a 10-digit identifier that groups entities at the tax identification number (TIN) level. The PAC ID acts as a precursor to our internal “V10” model and may represent either organizations or individuals. Relationships between owning and owned entities are recorded as links between PAC IDs, with metadata such as ownership roles and percentage stakes sometimes included.

Additionally, the dataset includes Enrollment IDs, which describe the specific billing relationships each PAC ID holds with Medicare. While more complex joins across enrollment and ownership data may be necessary in other PECOS-derived datasets, the All Owners files themselves are relatively straightforward—primarily documenting direct ownership relationships.

This dataset enables us to enrich our organizational models by identifying when two or more organizational NPIs functionally belong to the same system or ownership group, which is essential for accurate healthcare system mapping and for supporting use cases like plan-participation modeling and endpoint federation.

### Data Source Details

* Schema Target: pecos_raw
* Table Target: hospital_all_owners
* Download URL https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy
* Create Table Statement: [Hospital_All_Owners_2025.07.01.create_table_postgres.sql](./hospital_all_owners/Hospital_All_Owners_2025.07.01.create_table_postgres.sql)


## [NPPES Endpoint Importer Project](./nppes_endpoint)

Download the NPPES files from https://download.cms.gov/nppes/NPI_Files.html download the V2 version

### Data Source Summary
The NPPES Endpoint file is a relatively recent addition to the NPPES data suite, released after years of delay despite its early prioritization by the interoperability community. This file provides structured metadata about electronic endpoints associated with healthcare organizations and providers, intended to support interoperability through FHIR and other standards.

Each row includes:
	•	Endpoint type and description
	•	The actual endpoint address (e.g., a URL or URI)
	•	Legal business name of the affiliated organization
	•	Intended use and use description, with an “other use” field for nonstandard purposes
	•	Content type and content description
	•	Associated location/address, typically identifying the organization’s address—even when endpoints are cloud-hosted and physically decoupled from that address

Despite its intended importance, this dataset is notoriously unreliable. It includes unvalidated and inconsistent entries such as personal email addresses and outdated or misconfigured URLs. Data quality is a major concern, and the lack of automated or manual validation by CMS makes this file challenging to use without additional cleaning.
### Data Source Details

* Schema Target: nppes_raw
* Table Target: endpoint_file
* Download URL https://download.cms.gov/nppes/NPI_Files.html
* Create Table Statement: [endpoint_pfile_20050523-20250608.create_table_postgres.sql](./nppes_endpoint/endpoint_pfile_20050523-20250608.create_table_postgres.sql)


## [NPPES Main Importer Project](./nppes_main)

Download the NPPES files from https://download.cms.gov/nppes/NPI_Files.html download the V2 version

### Data Source Summary

The NPPES main file (National Plan and Provider Enumeration System) is the most structurally complex dataset in the NDH data ingestion pipeline. It represents a flat, unnormalized CSV file that includes detailed enumeration records for both individual and organizational healthcare providers. The key differentiator between these two provider types is the Entity Type Code, which allows the file to serve as a merged schema for two logically distinct record types.

For individuals, the file includes personal name components (first, last, middle, suffix, prefix, credentials) as well as “other last names” with type codes, which are frequently used for aliases such as maiden names. For organizations, the file provides a legal business name and typically one “other name,” often the DBA. Only organizations have a designated authorized official, whose name and credentials are included in the far-right columns of the file—added in a backward-compatible way over time.

Both individuals and organizations are assigned:
	•	Mailing and practice addresses
	•	Taxonomy codes and state licenses, encoded using NUCC taxonomy codes and repeated across multiple flat columns (e.g., Taxonomy_1, Taxonomy_2, etc.)
	•	Identifiers, such as state Medicaid or license numbers, organized per state. Though originally intended to consolidate identifiers across systems, this block is now less useful due to decreasing reliance on external IDs.
	•	Provider type metadata, such as “Is Sole Proprietor” and “Subpart” flags.

Sensitive fields such as Tax ID and Parent Organization Tax ID have been redacted in the public version, though Parent Organization Legal Name remains and can be used for limited relationship modeling.

The dataset design prioritizes wide, flat CSV compatibility over normalization, resulting in repetitive column structures that are difficult to parse. Despite its complexity and partial redaction, the NPPES main file remains the foundational source for enumerating U.S. healthcare providers.

There is a data documentation pdf that accompanies the download which contains most of this information and there is also a "codeset" pdf which has the various nppes codesets in the file (things like "other name type")

### Data Source Details

* Schema Target: nppes_raw
* Table Target: main_file
* Download URL https://download.cms.gov/nppes/NPI_Files.html
* Create Table Statement: [npidata_pfile_20050523-20250608.create_table_postgres.sql](./nppes_main/npidata_pfile_20050523-20250608.create_table_postgres.sql)


## [NPPES Othername Importer Project](./nppes_othername)

Download the NPPES files from https://download.cms.gov/nppes/NPI_Files.html download the V2 version

### Data Source Summary

The NPPES Other Name file is the simplest of the supplemental NPPES datasets. It contains only three columns:
	•	NPI
	•	OtherOrganizationName
	•	OtherOrganizationNameType

This file exclusively applies to organizational NPIs (Type 2) and does not include any information about individual providers (Type 1). It captures alternate names that an organization may operate under, such as “doing business as” (DBA) names, previous names, or other known aliases, with a corresponding type classification. Its minimal structure and focused scope make it straightforward to work with compared to other NPPES files.
Data Source Details
### 

* Schema Target: nppes_raw
* Table Target: othername_file
* Download URL https://download.cms.gov/nppes/NPI_Files.html
* Create Table Statement: [othername_pfile_20050523-20250608.create_table_postgres.sql](./nppes_othername/othername_pfile_20050523-20250608.create_table_postgres.sql)


## [NPPES PL Importer Project](./nppes_pl)

Download the NPPES files from https://download.cms.gov/nppes/NPI_Files.html download the V2 version

### Data Source Summary

The NPPES Practice Location file lists additional practice locations for providers beyond the primary address required in the main NPPES file. Introduced more recently, this file benefits from improved data quality due to NPPES’s adoption of U.S. Postal Service APIs for address validation. As a result, the address data in this file tends to be cleaner and more reliable. However, it only includes providers—individuals or organizations—who have opted to register multiple practice locations, so it does not represent a complete view of all provider addresses.

### Data Source Details

* Schema Target: nppes_raw
* Table Target: pl_file
* Download URL https://download.cms.gov/nppes/NPI_Files.html
* Create Table Statement: [pl_pfile_20050523-20250608.create_table_postgres.sql](./nppes_pl/pl_pfile_20050523-20250608.create_table_postgres.sql)


## [NUCC Importer Project](./nucc)

This is the output of the nucc_slurp repository

### Data Source Summary

The NUCC Provider Taxonomy is maintained by the National Uniform Claim Committee (NUCC) and provides standardized codes for classifying healthcare providers. The taxonomy is hierarchical and distinguishes between individual and organizational (non-individual) providers. However, the structure is inconsistent—subcategories like “groups of individuals” appear under the “individual” branch, leading to confusion.

Each taxonomy code is a string (e.g., 207L00000X for anesthesiology), and many specialties (such as addiction medicine) appear under multiple parent types (e.g., anesthesiology, psychiatry, pediatrics), without clear disambiguation. This reflects the training path rather than a coherent hierarchy—specialties appear under the branch where their prerequisite training lies.

Despite being hierarchical in concept, the taxonomy is not normalized: not all branches have their own codes, and a provider’s presence under a sub-branch doesn’t guarantee affiliation with its parent category. Furthermore, the taxonomy system is independent of the NPPES entity type system, so enforcement of organizational or individual classification is weak.

Data from NUCC comes in multiple forms:
	•	A free CSV file with basic codes and descriptions
	•	A paid CSV version with additional metadata
	•	The official NUCC website, which includes the parent-child structure not present in the CSV files

Because the free CSV lacks hierarchy metadata, we merge data scraped from the website with the CSV in a separate repository. That combined dataset is used to generate a cleaned CSV for import into Puffin.

### Data Source Details

* Schema Target: nucc_raw
* Table Target: nucc_merged_file
* Download URL: 
* Create Table Statement: [merged_nucc_data.create_table_postgres.sql](./nucc/merged_nucc_data.create_table_postgres.sql)


## [NUCC Ancestor Importer Project](./nucc_ancestor)

This is the output of the nucc_slurp repository

### Data Source Summary

The NUCC Ancestor Data file represents the second part of the NUCC provider taxonomy dataset. While the primary NUCC taxonomy file lists provider types and codes, the ancestor file defines the parent-child relationships between them—crucial for reconstructing the taxonomy hierarchy.

Unlike the main taxonomy file, which uses alphanumeric codes (e.g., 207L00000X), this file operates on numeric identifiers assigned to each taxonomy node. These numeric IDs are extracted from the NUCC website because not all intermediate branches in the taxonomy tree are assigned taxonomy codes—some internal nodes exist only as named groupings without associated codes. Thus, the numeric ID is the only reliable way to reconstruct the full tree structure.

We scrape these identifiers and relationships from the NUCC website to form a complete hierarchical model of the taxonomy, which cannot be built from the CSV files alone. This enriched structure is critical for applications that need to reason about provider specialties in a tree-like fashion.

### Data Source Details

* Schema Target: nucc_raw
* Table Target: nucc_ancestor
* Download URL:
* Create Table Statement:


## [NUCC Sources Importer Project](./nucc_sources)

This is the output of the nucc_slurp repository

### Data Source Summary

The NUCC Sources dataset is derived by scraping the notes section of the NUCC provider taxonomy website. While the downloadable CSV file lacks this information, the NUCC website often includes textual references to authoritative governing bodies—such as the American Board of Pediatrics or the American Board of Internal Medicine—that oversee particular taxonomy types.

Because these references are embedded informally within the notes field, we extract them using regex-based parsing, producing a structured dataset that links taxonomy codes to their associated certifying organizations. In some cases, multiple sources may be listed for a single taxonomy type.

Although syntactically inconsistent, this extracted data offers long-term potential for use in credential verification workflows, such as mapping provider specialties to legitimate board certifications and supporting ground truth validation of provider types.

### Data Source Details

* Schema Target: nucc_raw
* Table Target: nucc_sources
* Download URL: 
* Create Table Statement:


## [PECOS Assignment Importer Project](./pecos_assignment)

The PECOS Enrollment and Assignment data is downloaded here https://data.cms.gov/provider-characteristics/medicare-provider-supplier-enrollment/medicare-fee-for-service-public-provider-enrollment

### Data Source Summary

The PECOS Assignment dataset records instances where an individual provider assigns their Medicare payments to another entity, such as a group practice, clinic, or health system. This is common in outpatient billing, where Medicare reimbursement is calculated at the individual provider level, but the actual payment is directed to an affiliated organization.

The dataset is critical for mapping individual NPIs to organizational PAC IDs that receive payment on their behalf, revealing real-world employment or affiliation structures in Medicare billing. It captures one of the two meanings of “assignment” in healthcare: the provider-to-organization payment assignment (as opposed to patient-to-provider benefit assignment). Understanding these assignments provides key insights into financial and operational relationships within provider networks.

Assignment is on a per-enrollment basis and has the be used with the original assignment file to reduce down to PAC to PAC associations, which represent the underlying relationships.

### Data Source Details

* Schema Target: pecos_raw
* Table Target: pecos_reassignment
* Download URL: https://data.cms.gov/provider-characteristics/medicare-provider-supplier-enrollment/medicare-fee-for-service-public-provider-enrollment
* Create Table Statement:


## [PECOS Enrollment Importer Project](./pecos_enrollment)

The PECOS Enrollment and Assignment data is downloaded here https://data.cms.gov/provider-characteristics/medicare-provider-supplier-enrollment/medicare-fee-for-service-public-provider-enrollment

### Data Source Summary

The PECOS Enrollment dataset maps Medicare/Medicaid billing privileges—referred to as enrollments—to healthcare entities identified by PAC IDs. A PAC ID represents either an individual or organization and is tied to a Tax Identification Number (TIN). Each enrollment represents a specific approval to bill Medicare or Medicaid for a particular service type.

This file provides a one-to-many relationship between PAC IDs and enrollments, allowing insight into which entities are actively participating in government programs. It also includes demographic and organizational details such as legal business names, making it a valuable source for validating provider identity and organizational structure within the PECOS system.

### Data Source Details

* Schema Target: pecos_raw
* Table Target: pecos_enrollment
* Download URL: https://data.cms.gov/provider-characteristics/medicare-provider-supplier-enrollment/medicare-fee-for-service-public-provider-enrollment
* Create Table Statement:


## [PECOS Ownership Importer Project](./pecos_ownership)

There are several PECOS ownership files that are found here: https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy

### Data Source Summary

These have now been split into different directories. 

### Data Source Details

* Schema Target: pecos_raw
* Table Target: hha_all_owners, hospice_all_owners, hospital_all_owners, rhc_all_owners, snf_all_owners
* Download URL: https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy
* Create Table Statement:


## [RHC All Owners Importer Project](./rhc_all_owners)

There are several PECOS ownership files that are found here: https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy

### Data Source Summary

See the documentation for the Hospital Owners data for details. 

### Data Source Details

* Schema Target: pecos_raw
* Table Target: rhc_all_owners
* Download URL: https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy
* Create Table Statement:


## [SNF All Owners Importer Project](./snf_all_owners)

There are several PECOS ownership files that are found here: https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy

### Data Source Summary

See the documentation for the Hospital Owners data for details. 

### Data Source Details

* Schema Target: pecos_raw
* Table Target: snf_all_owners
* Download URL: https://data.cms.gov/search?keywords=All%20Owners&sort=Relevancy
* Create Table Statement:


