#!/usr/bin/env python3
"""
Payer Provider Network Stage Slurp
==========

This program should load the csv file good_payer_endpoints.csv and loop over the payer endpoints there. For each endpoint:

* Load the {base_url}/PractitionerRole endpoint and continue loading the "next" page until all entry data is loaded into memory. 
* Create a directory payer_slurp_results/{payer_stub}/ for saving the endpoint data
* For each entry, recurse the FHIR endpoints included for Practicioner, Location, and Organization
* Write out seperate CSV file for the following data points, adding many rows as nessecary for each data point, linking back to the source PracticionerRole endpoint as the first column in each data file: 
 * org_to_pr.csv - Organization to Practicionerrole file
 * org.csv - Organization file should only have one row per organization
 * location_to_pr.csv - Location to PracticionerRole File
 * location.csv - Location file should only have one row per location
 * p_to_pr.csv - Practicioner to PracticionerRole (there should be only one for each PracticionerRole entry.. throw an error if this is not true) add a column here called npi, set to 0 if it is missing. Also add a column is_npi_invalid set to '?" for now. 
 * spec_to_pr.csv - Speciality to PractitioionerRole (just record the code here) 
 * tele_to_pr.csv - Telecom to PracticionerRole (these are inline in the PracticitonerRole record)

Take a look at the following files to understand how to properly dereference the FHIR data elements: 
* json_example/PracticionerRole.json
* json_example/Practicioner.pp.json
* json_example/Location.pp.json
* json_example/Organization.pp.json


The program should always overwrite previous results. 
Print progress to the terminal. 


"""

import os
import csv
import json
import requests
import time
import argparse
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Any, Optional

def load_payer_endpoints(filename: str) -> List[Dict[str, str]]:
    """Load payer endpoints from CSV file."""
    payers = []
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            payers.append(row)
    return payers

def fetch_fhir_resource(url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """Fetch a FHIR resource with retry logic."""
    # Set headers to request JSON format
    headers = {
        'Accept': 'application/fhir+json',
        'Content-Type': 'application/fhir+json'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"  Fetching: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {url} (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"  Failed to fetch {url} after {max_retries} attempts")
                return None

def fetch_all_practitioner_roles(base_url: str, test_mode: bool = False, test_limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch all PractitionerRole entries with pagination."""
    all_entries = []
    # Ensure base_url ends with slash to preserve directory structure
    if not base_url.endswith('/'):
        base_url = base_url + '/'
    # Use _count parameter to get 100 results per request for better efficiency
    next_url = urljoin(base_url, "PractitionerRole?_count=100")
    
    if test_mode:
        print(f"TEST MODE: Limiting results to first {test_limit} entries")
    
    while next_url:
        print(f"Fetching PractitionerRole page: {next_url}")
        bundle = fetch_fhir_resource(next_url)
        if not bundle:
            break
            
        # Extract entries from bundle
        entries = bundle.get('entry', [])
        for entry in entries:
            resource = entry.get('resource', {})
            if resource.get('resourceType') == 'PractitionerRole':
                all_entries.append(resource)
                
                # In test mode, stop after reaching the limit
                if test_mode and len(all_entries) >= test_limit:
                    print(f"  TEST MODE: Reached limit of {test_limit} entries, stopping pagination")
                    break
        
        print(f"  Retrieved {len(entries)} entries, total so far: {len(all_entries)}")
        
        # In test mode, stop after reaching the limit
        if test_mode and len(all_entries) >= test_limit:
            break
        
        # Find next link
        next_url = None
        for link in bundle.get('link', []):
            if link.get('relation') == 'next':
                next_url = link.get('url')
                break
    
    print(f"Total PractitionerRole entries fetched: {len(all_entries)}")
    return all_entries

def extract_npi_from_practitioner(practitioner_data: Dict[str, Any]) -> str:
    """Extract NPI from practitioner identifiers."""
    if not practitioner_data:
        return "0"
    
    identifiers = practitioner_data.get('identifier', [])
    for identifier in identifiers:
        type_info = identifier.get('type', {})
        coding = type_info.get('coding', [])
        for code in coding:
            if code.get('code') == 'NPI':
                return identifier.get('value', '0')
    return "0"

def extract_practitioner_name(practitioner_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract name information from practitioner."""
    if not practitioner_data:
        return {'family': '', 'given': ''}
    
    names = practitioner_data.get('name', [])
    if names:
        name = names[0]  # Take first name
        family = name.get('family', '')
        given = name.get('given', [])
        given_str = ' '.join(given) if given else ''
        return {'family': family, 'given': given_str}
    return {'family': '', 'given': ''}

def extract_organization_info(org_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract organization information."""
    if not org_data:
        return {'name': '', 'type': '', 'address': ''}
    
    name = org_data.get('name', '')
    
    # Extract type
    org_type = ''
    types = org_data.get('type', [])
    if types:
        coding = types[0].get('coding', [])
        if coding:
            org_type = coding[0].get('display', coding[0].get('code', ''))
    
    # Extract address
    addresses = org_data.get('address', [])
    address_str = ''
    if addresses:
        addr = addresses[0]
        line = addr.get('line', [])
        city = addr.get('city', '')
        state = addr.get('state', '')
        postal = addr.get('postalCode', '')
        address_parts = []
        if line:
            address_parts.extend(line)
        if city:
            address_parts.append(city)
        if state:
            address_parts.append(state)
        if postal:
            address_parts.append(postal)
        address_str = ', '.join(address_parts)
    
    return {'name': name, 'type': org_type, 'address': address_str}

def extract_location_info(location_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract location information."""
    if not location_data:
        return {'name': '', 'status': '', 'address': ''}
    
    name = location_data.get('name', '')
    status = location_data.get('status', '')
    
    # Extract address
    address = location_data.get('address', {})
    address_parts = []
    
    line = address.get('line', [])
    if line:
        address_parts.extend(line)
    
    city = address.get('city', '')
    if city:
        address_parts.append(city)
    
    state = address.get('state', '')
    if state:
        address_parts.append(state)
    
    postal = address.get('postalCode', '')
    if postal:
        address_parts.append(postal)
    
    address_str = ', '.join(address_parts)
    
    return {'name': name, 'status': status, 'address': address_str}

def process_payer(payer: Dict[str, str], test_mode: bool = False, test_limit: int = 100) -> None:
    """Process a single payer's provider network."""
    payer_name = payer['payer_name']
    payer_stub = payer['payer_stub']
    base_url = payer['payer_provider_directory_fhir_url']
    
    # Ensure base_url ends with slash to preserve directory structure
    if not base_url.endswith('/'):
        base_url = base_url + '/'
    
    print(f"\n=== Processing payer: {payer_name} ({payer_stub}) ===")
    print(f"Base URL: {base_url}")
    
    # Create output directory - use test directory when in test mode
    if test_mode:
        output_dir = f"payer_slurp_test_results/{payer_stub}"
    else:
        output_dir = f"payer_slurp_results/{payer_stub}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Fetch all PractitionerRole entries
    practitioner_roles = fetch_all_practitioner_roles(base_url, test_mode, test_limit)
    
    if not practitioner_roles:
        print(f"No PractitionerRole entries found for {payer_name}")
        return
    
    # Data storage
    organizations = {}  # id -> org_data
    locations = {}  # id -> location_data
    practitioners = {}  # id -> practitioner_data
    
    # CSV data
    org_to_pr_rows = []
    location_to_pr_rows = []
    p_to_pr_rows = []
    spec_to_pr_rows = []
    tele_to_pr_rows = []
    
    print(f"Processing {len(practitioner_roles)} PractitionerRole entries...")
    
    for i, pr in enumerate(practitioner_roles):
        pr_id = pr.get('id', '')
        print(f"Processing PractitionerRole {i+1}/{len(practitioner_roles)}: {pr_id}")
        
        # Process Organization references (from extension network-reference)
        extensions = pr.get('extension', [])
        for ext in extensions:
            if ext.get('url') == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/network-reference':
                org_ref = ext.get('valueReference', {}).get('reference', '')
                if org_ref.startswith('Organization/'):
                    org_id = org_ref.split('/')[-1]
                    if org_id not in organizations:
                        org_url = urljoin(base_url, org_ref)
                        org_data = fetch_fhir_resource(org_url)
                        if org_data:
                            organizations[org_id] = org_data
                    
                    org_to_pr_rows.append({
                        'practitioner_role_fhir_url': urljoin(base_url, f'PractitionerRole/{pr_id}'),
                        'organization_fhir_url': urljoin(base_url, org_ref),
                        'organization_reference': org_ref
                    })
        
        # Process direct organization reference if present
        org_ref = pr.get('organization', {}).get('reference', '')
        if org_ref and org_ref.startswith('Organization/'):
            org_id = org_ref.split('/')[-1]
            if org_id not in organizations:
                org_url = urljoin(base_url, org_ref)
                org_data = fetch_fhir_resource(org_url)
                if org_data:
                    organizations[org_id] = org_data
            
            org_to_pr_rows.append({
                'practitioner_role_fhir_url': urljoin(base_url, f'PractitionerRole/{pr_id}'),
                'organization_fhir_url': urljoin(base_url, org_ref),
                'organization_reference': org_ref
            })
        
        # Process Practitioner reference
        practitioner_ref = pr.get('practitioner', {}).get('reference', '')
        if practitioner_ref and practitioner_ref.startswith('Practitioner/'):
            practitioner_id = practitioner_ref.split('/')[-1]
            if practitioner_id not in practitioners:
                practitioner_url = urljoin(base_url, practitioner_ref)
                practitioner_data = fetch_fhir_resource(practitioner_url)
                if practitioner_data:
                    practitioners[practitioner_id] = practitioner_data
            
            # Extract NPI and name info
            practitioner_data = practitioners.get(practitioner_id, {})
            npi = extract_npi_from_practitioner(practitioner_data)
            name_info = extract_practitioner_name(practitioner_data)
            
            p_to_pr_rows.append({
                'practitioner_role_fhir_url': urljoin(base_url, f'PractitionerRole/{pr_id}'),
                'practitioner_fhir_url': urljoin(base_url, practitioner_ref),
                'practitioner_reference': practitioner_ref,
                'npi': npi,
                'is_npi_invalid': '?',
                'family_name': name_info['family'],
                'given_name': name_info['given']
            })
        
        # Process Location references
        location_refs = pr.get('location', [])
        for loc_ref_obj in location_refs:
            loc_ref = loc_ref_obj.get('reference', '')
            if loc_ref and loc_ref.startswith('Location/'):
                loc_id = loc_ref.split('/')[-1]
                if loc_id not in locations:
                    loc_url = urljoin(base_url, loc_ref)
                    loc_data = fetch_fhir_resource(loc_url)
                    if loc_data:
                        locations[loc_id] = loc_data
                
                location_to_pr_rows.append({
                    'practitioner_role_fhir_url': urljoin(base_url, f'PractitionerRole/{pr_id}'),
                    'location_fhir_url': urljoin(base_url, loc_ref),
                    'location_reference': loc_ref
                })
        
        # Process Specialties
        specialties = pr.get('specialty', [])
        for specialty in specialties:
            codings = specialty.get('coding', [])
            for coding in codings:
                code = coding.get('code', '')
                display = coding.get('display', '')
                system = coding.get('system', '')
                
                spec_to_pr_rows.append({
                    'practitioner_role_fhir_url': urljoin(base_url, f'PractitionerRole/{pr_id}'),
                    'specialty_code': code,
                    'specialty_display': display,
                    'specialty_system': system
                })
        
        # Process Telecom
        telecoms = pr.get('telecom', [])
        for telecom in telecoms:
            system = telecom.get('system', '')
            value = telecom.get('value', '')
            use = telecom.get('use', '')
            
            tele_to_pr_rows.append({
                'practitioner_role_fhir_url': urljoin(base_url, f'PractitionerRole/{pr_id}'),
                'telecom_system': system,
                'telecom_value': value,
                'telecom_use': use
            })
    
    print(f"Writing CSV files to {output_dir}...")
    
    # Write org_to_pr.csv
    with open(f"{output_dir}/org_to_pr.csv", 'w', newline='', encoding='utf-8') as f:
        if org_to_pr_rows:
            writer = csv.DictWriter(f, fieldnames=['practitioner_role_fhir_url', 'organization_fhir_url', 'organization_reference'])
            writer.writeheader()
            writer.writerows(org_to_pr_rows)
    
    # Write org.csv
    org_rows = []
    for org_id, org_data in organizations.items():
        org_info = extract_organization_info(org_data)
        org_rows.append({
            'organization_fhir_url': urljoin(base_url, f'Organization/{org_id}'),
            'name': org_info['name'],
            'type': org_info['type'],
            'address': org_info['address']
        })
    
    with open(f"{output_dir}/org.csv", 'w', newline='', encoding='utf-8') as f:
        if org_rows:
            writer = csv.DictWriter(f, fieldnames=['organization_fhir_url', 'name', 'type', 'address'])
            writer.writeheader()
            writer.writerows(org_rows)
    
    # Write location_to_pr.csv
    with open(f"{output_dir}/location_to_pr.csv", 'w', newline='', encoding='utf-8') as f:
        if location_to_pr_rows:
            writer = csv.DictWriter(f, fieldnames=['practitioner_role_fhir_url', 'location_fhir_url', 'location_reference'])
            writer.writeheader()
            writer.writerows(location_to_pr_rows)
    
    # Write location.csv
    location_rows = []
    for loc_id, loc_data in locations.items():
        loc_info = extract_location_info(loc_data)
        location_rows.append({
            'location_fhir_url': urljoin(base_url, f'Location/{loc_id}'),
            'name': loc_info['name'],
            'status': loc_info['status'],
            'address': loc_info['address']
        })
    
    with open(f"{output_dir}/location.csv", 'w', newline='', encoding='utf-8') as f:
        if location_rows:
            writer = csv.DictWriter(f, fieldnames=['location_fhir_url', 'name', 'status', 'address'])
            writer.writeheader()
            writer.writerows(location_rows)
    
    # Write p_to_pr.csv
    with open(f"{output_dir}/p_to_pr.csv", 'w', newline='', encoding='utf-8') as f:
        if p_to_pr_rows:
            writer = csv.DictWriter(f, fieldnames=['practitioner_role_fhir_url', 'practitioner_fhir_url', 'practitioner_reference', 'npi', 'is_npi_invalid', 'family_name', 'given_name'])
            writer.writeheader()
            writer.writerows(p_to_pr_rows)
    
    # Write spec_to_pr.csv
    with open(f"{output_dir}/spec_to_pr.csv", 'w', newline='', encoding='utf-8') as f:
        if spec_to_pr_rows:
            writer = csv.DictWriter(f, fieldnames=['practitioner_role_fhir_url', 'specialty_code', 'specialty_display', 'specialty_system'])
            writer.writeheader()
            writer.writerows(spec_to_pr_rows)
    
    # Write tele_to_pr.csv
    with open(f"{output_dir}/tele_to_pr.csv", 'w', newline='', encoding='utf-8') as f:
        if tele_to_pr_rows:
            writer = csv.DictWriter(f, fieldnames=['practitioner_role_fhir_url', 'telecom_system', 'telecom_value', 'telecom_use'])
            writer.writeheader()
            writer.writerows(tele_to_pr_rows)
    
    print(f"Completed processing {payer_name}:")
    print(f"  - Organizations: {len(organizations)}")
    print(f"  - Locations: {len(locations)}")
    print(f"  - Practitioners: {len(practitioners)}")
    print(f"  - PractitionerRoles: {len(practitioner_roles)}")
    print(f"  - Organization-PR relationships: {len(org_to_pr_rows)}")
    print(f"  - Location-PR relationships: {len(location_to_pr_rows)}")
    print(f"  - Practitioner-PR relationships: {len(p_to_pr_rows)}")
    print(f"  - Specialty relationships: {len(spec_to_pr_rows)}")
    print(f"  - Telecom relationships: {len(tele_to_pr_rows)}")

def main():
    """Main function."""
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description='Payer Provider Network FHIR Data Slurp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 Step70_SlurpPayerProviderNetworks.py
  python3 Step70_SlurpPayerProviderNetworks.py --test
  python3 Step70_SlurpPayerProviderNetworks.py --test --limit 50
        """
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode - limits results to first 100 PractitionerRole entries'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Number of PractitionerRole entries to process in test mode (default: 100)'
    )
    
    args = parser.parse_args()
    
    print("Starting Payer Provider Network Slurp...")
    
    if args.test:
        print(f"*** RUNNING IN TEST MODE - LIMITED TO {args.limit} ENTRIES ***")
    
    # Load payer endpoints
    payers = load_payer_endpoints('good_payer_endpoints.csv')
    print(f"Loaded {len(payers)} payer endpoints")
    
    # Process each payer
    for payer in payers:
        try:
            process_payer(payer, test_mode=args.test, test_limit=args.limit)
        except Exception as e:
            print(f"Error processing payer {payer.get('payer_name', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nCompleted Payer Provider Network Slurp!")

if __name__ == "__main__":
    main()
