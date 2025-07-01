#!/usr/bin/env python3
"""
Domain-Based SERP Scrape Script

This script reads domain names from plan_domain_names.csv and uses SERPapi to search 
for FHIR provider API information for each domain. The search results are saved as 
JSON files in the email_scrape_results directory.
"""

import csv
import json
import os
import re
from dotenv import load_dotenv
from serpapi import GoogleSearch

def read_domain_csv(file_path):
    """
    Read the domain CSV file and return the domains as a list.
    """
    domains = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                domain = row.get('domain', '').strip()
                if domain:
                    domains.append(domain)
        
        print(f"Read {len(domains)} domains from {file_path}")
        return domains
        
    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}")
        print("Please run Step30_extract_email_domains.py first to create the domain list.")
        return []

def sanitize_filename(name):
    """
    Replace special characters in the name to create a safe filename.
    """
    # Replace any character that's not alphanumeric, underscore, or hyphen with an underscore
    return re.sub(r'[^\w\-]', '_', name)

def search_serp_api(domain, api_key):
    """
    Use SERPapi to search for the domain + PROVIDER API FHIR.
    """
    # Extract the main organization name from domain for better search results
    # e.g., aetna.com -> aetna, bcbsm.com -> bcbsm
    org_name = domain.split('.')[0]
    
    params = {
        "engine": "google",
        "q": f'site:{domain} "PROVIDER DIRECTORY"  "FHIR" -fire.ly -linkedin.com -google.com',
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
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment variable
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        print("Error: SERP_API_KEY not found in .env file")
        print("Please create a .env file with your SERPapi key:")
        print("SERP_API_KEY=your_api_key_here")
        return
    
    # Path to the domain CSV file
    domain_csv_path = "plan_domain_names.csv"
    
    # Create email_scrape_results directory if it doesn't exist
    os.makedirs("email_scrape_results", exist_ok=True)
    
    # Read the domain data
    print(f"Reading domain data from {domain_csv_path}...")
    domains = read_domain_csv(domain_csv_path)
    
    if not domains:
        return
    
    print(f"Found {len(domains)} domains to search.")
    
    # Search for each domain and save results
    print("Starting domain-based searches...")
    for i, domain in enumerate(domains):
        print(f"Processing {i+1}/{len(domains)}: {domain}")
        
        # Create safe filename
        safe_domain = sanitize_filename(domain)
        output_file = f"./email_scrape_results/{safe_domain}.search_results.json"
        
        # Check if we already have results for this domain
        if os.path.exists(output_file):
            print(f"  Results already exist for {domain}, skipping...")
            continue
        
        try:
            # Search using SERPapi
            print(f"  Searching for: {domain}")
            results = search_serp_api(domain, api_key)
            
            # Save results to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            print(f"  Results saved to {output_file}")
            
            # Check if we found any organic results
            organic_results = results.get('organic_results', [])
            if organic_results:
                print(f"  Found {len(organic_results)} organic results")
            else:
                print(f"  No organic results found for {domain}")
                
        except Exception as e:
            print(f"  Error processing {domain}: {str(e)}")
    
    print("Domain-based search process completed.")
    print(f"Results saved in ./email_scrape_results/ directory")

if __name__ == "__main__":
    main()
