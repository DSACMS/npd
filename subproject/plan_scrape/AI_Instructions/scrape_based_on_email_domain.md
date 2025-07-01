This is a project to use SERP API to search for Payer FHIR endpoints.

See Step20_Serp_Scrape.py for details on how the previous implementation worked.

In this generation I would like to write two scripts:

* The first script will read in the file source_data/MA_Contract_directory_2025_06.csv and process the emails in the "Directory Contact Email column in order to create a list of distinct domain names. So info@aetna.com and customer_service@aetna.com just collapose to 'aetna.com'. Then these should be written out to a single column csv file called: plan_domain_names.csv
* The second file will accept the contents of plan_domain_names.csv and then use a SERP API call to do a search for "site:that_payer_domain.com FHIR Provider" and put the resulting JSON files in the ./email_scrape_results/ directory.
