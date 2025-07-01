#!/usr/bin/env python3
"""
This file accepts a fhir_endpoints.csv file, and outputs a new file which is the distinct "list_source" URLS in the data. 
The structure of that file is: 

list_source,certified_api_developer_name,distinct_url_count

as matching the source fhir_endpints.csv file header which has the file headers: 
"url","api_information_source_name","created_at","updated","list_source","certified_api_developer_name","capability_fhir_version","format","http_response","http_response_time_second","smart_http_response","errors","cap_stat_exists","kind","requested_fhir_version","is_chpl"

The first thing to do is verify that the --input_file parameter has a first line of column headers that matches the above.. and error out if does not. 

Then this script uses pandas to query the table (in sql style) with 

SELECT
    list_source,
    certified_api_developer_name,
    COUNT(DISTINCT(url)) AS distinct_url_count
FROM input_csv_file

and writes the results out to the --output_file file as a CSV file. 
"""

import argparse
import pandas as pd
import sys
import os

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract distinct list_source URLs from FHIR endpoints CSV')
    parser.add_argument('--input_file', required=True, help='Input CSV file path')
    parser.add_argument('--output_file', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Expected column headers
    expected_headers = [
        "url", "api_information_source_name", "created_at", "updated", 
        "list_source", "certified_api_developer_name", "capability_fhir_version", 
        "format", "http_response", "http_response_time_second", "smart_http_response", 
        "errors", "cap_stat_exists", "kind", "requested_fhir_version", "is_chpl"
    ]
    
    try:
        # Read the CSV file
        df = pd.read_csv(args.input_file)
        
        # Verify headers match expected format
        actual_headers = list(df.columns)
        if actual_headers != expected_headers:
            print("Error: CSV headers do not match expected format.")
            print(f"Expected: {expected_headers}")
            print(f"Actual: {actual_headers}")
            sys.exit(1)
        
        # Group by list_source and certified_api_developer_name, count distinct URLs
        result = df.groupby(['list_source', 'certified_api_developer_name'])['url'].nunique().reset_index()
        result.rename(columns={'url': 'distinct_url_count'}, inplace=True)
        
        # Sort by list_source for consistent output
        result = result.sort_values('list_source')
        
        # Write results to output file
        result.to_csv(args.output_file, index=False)
        
        print(f"Successfully processed {len(df)} rows from '{args.input_file}'")
        print(f"Generated {len(result)} distinct list_source entries in '{args.output_file}'")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
