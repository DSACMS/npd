#!/usr/bin/env python3
"""
Phase I SERP Scrape Script

This script reads Medicare Part C plan data from a CSV file, extracts unique parent
organizations, and uses SERPapi to search for FHIR provider API information for each
organization. The search results are saved as JSON files in the configured output directory.

Configuration:
- All file and directory paths are configurable variables in the main() function
- Change INPUT_CSV_FILE and OUTPUT_DIRECTORY variables to modify paths
"""

import csv
import json
import os
import re
from dotenv import load_dotenv
from serpapi import GoogleSearch

def read_csv_data(file_path):
    """
    Read the CSV file and return the data as a list of dictionaries.
    Skip the first two rows (the first row is the title, the second row is the column headers).
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        print("Raw CSV file contents:")
        for line in csvfile:
            print(line.strip())
        csvfile.seek(0)  # Reset file pointer to beginning
        
        # Skip the first two rows
        next(csvfile)  # Skip title row
        next(csvfile)  # Skip header row
        
        # Read the rest of the file line by line
        for line in csvfile:
            line = line.strip()
            if line:
                row = line.split(',')
                row_dict = {
                    'Parent Organization': row[0],
                    'Contract Name': row[1],
                    'Organization Marketing Name': row[2]
                }
                data.append(row_dict)
        
        print(f"Data list: {data}")
    
    return data

def get_unique_parent_organizations(data):
    """
    Extract unique parent organizations from the data.
    """
    parent_organizations = set()
    for row in data:
        parent_org = row.get('Parent Organization')
        if parent_org and parent_org.strip():
            parent_organizations.add(parent_org.strip().lower())
    
    print(f"Found {len(parent_organizations)} unique parent organizations.")
    return sorted(list(parent_organizations))

def sanitize_filename(name):
    """
    Replace special characters in the name to create a safe filename.
    """
    # Replace any character that's not alphanumeric, underscore, or hyphen with an underscore
    return re.sub(r'[^\w\-]', '_', name)

def search_serp_api(parent_org, api_key):
    """
    Use SERPapi to search for the parent organization + PROVIDER API FHIR.
    """
    params = {
        "engine": "google",
        "q": f"{parent_org} Medicare Advantage \"PROVIDER DIRECTORY\" API \"FHIR\" -fire.ly -linkedin.com -google.com ",
        "location": "United States",
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "num": "10",
        "safe": "active",
        "api_key": api_key
    }
    
    search = GoogleSearch(params)
    return search.get_dict()

def main():
    # Configuration - All directory and file paths in one place
    INPUT_CSV_FILE = "search_these.csv"
    OUTPUT_DIRECTORY = "scrape_results"
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        print("Error: SERP_API_KEY not found in .env file")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    
    # Read the CSV data
    print(f"Reading CSV data from {INPUT_CSV_FILE}...")
    data = read_csv_data(INPUT_CSV_FILE)
    print(f"CSV data: {data}")
    
    # Get unique parent organizations
    print("Extracting unique parent organizations...")
    parent_organizations = get_unique_parent_organizations(data)
    print(f"Found {len(parent_organizations)} unique parent organizations.")
    
    # Search for each parent organization and save results
    print("Starting searches...")
    for i, parent_org in enumerate(parent_organizations):
        print(f"Processing {i+1}/{len(parent_organizations)}: {parent_org}")
        
        # Create safe filename
        safe_parent_org = sanitize_filename(parent_org)
        output_file = f"./{OUTPUT_DIRECTORY}/{safe_parent_org}.search_results.json"
        
        # Check if we already have results for this parent organization
        if os.path.exists(output_file):
            print(f"  Results already exist for {parent_org}, skipping...")
            continue
        
        try:
            # Search using SERPapi
            print(f"  Searching for: {parent_org}")
            results = search_serp_api(parent_org, api_key)
            
            # Save results to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            print(f"  Results saved to {output_file}")
        except Exception as e:
            print(f"  Error processing {parent_org}: {str(e)}")
    
    print("Search process completed.")

if __name__ == "__main__":
    main()
