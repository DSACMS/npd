#!/usr/bin/env python3
"""
Email Domain Extraction Script

This script reads Medicare Part C plan data from the CSV file, extracts email addresses
from the "Directory Contact Email" column, extracts unique domain names from those emails,
and writes them to a single column CSV file called plan_domain_names.csv.
"""

import csv
import re
from urllib.parse import urlparse

def extract_domain_from_email(email):
    """
    Extract domain name from email address.
    Example: info@aetna.com -> aetna.com
    """
    if not email or '@' not in email:
        return None
    
    # Split by @ and take the domain part
    domain = email.split('@')[1].strip().lower()
    
    # Remove any extra quotes or whitespace
    domain = domain.strip('"').strip("'").strip()
    
    return domain if domain else None

def read_csv_and_extract_domains(file_path):
    """
    Read the CSV file and extract unique domain names from email addresses.
    """
    domains = set()
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        # Use csv.DictReader to handle the CSV properly
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            email = row.get('Directory Contact Email', '').strip()
            if email:
                domain = extract_domain_from_email(email)
                if domain:
                    domains.add(domain)
    
    return sorted(list(domains))

def write_domains_to_csv(domains, output_file):
    """
    Write the domains to a single column CSV file.
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['domain'])
        
        # Write each domain
        for domain in domains:
            writer.writerow([domain])

def main():
    # Path to the input CSV file
    input_csv_path = "source_data/MA_Contract_directory_2025_06.csv"
    
    # Path to the output CSV file
    output_csv_path = "plan_domain_names.csv"
    
    print(f"Reading CSV data from {input_csv_path}...")
    
    try:
        # Extract unique domains from email addresses
        domains = read_csv_and_extract_domains(input_csv_path)
        
        print(f"Found {len(domains)} unique email domains:")
        for domain in domains[:10]:  # Show first 10 as preview
            print(f"  {domain}")
        if len(domains) > 10:
            print(f"  ... and {len(domains) - 10} more")
        
        # Write domains to output CSV
        write_domains_to_csv(domains, output_csv_path)
        
        print(f"Domain names written to {output_csv_path}")
        print("Domain extraction completed successfully.")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_csv_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
