Scrape Medicare Part C Plans
===================

Every Medicare Part C plan is required to expose a FHIR directory endpoint for their plan, which publishes the network information in that plan.
This project will use SERPapi.com to conduct searches (see example python in AI_Instructions/serp_api_example.py) in order create a CSV file of plans,
their FHIR directory "landing page", as well as the FHIR url that returns the JSON list of FHIR URLS.

Here are the steps in the phase I process:

* create a file called phase_I_serp_scrape.py. Inside that file:
* import source_data/2025_partc_star_ratings.csv into a python list.
* The csv data starts on the third row and the second row has the column headers.
* The csv has columns called "Organization Marketing Name", create a list of the unique values in this column of data.
* Using each value of this list as the variable marketing_name, create a value for the 'q' parameter using the following f string format:
  * f"{marketing_name} PROVIDER API FHIR"
* use the serpapi as described in AI_Instructions/serp_api_example.py to query using the q parameter we just defined
* replace all special characerts in marketing_name and call the new variable safe_marketing_name, and create a file name in the following format
  * f"./scrape_results/{safe_marketing_name}.search_results.json"
* save the resulting scrape data to this file
* move on to the next unique marketing_name until all of the marketing_names are done
