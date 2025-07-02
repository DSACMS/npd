#!/usr/bin/env python3
"""
CSV Data extractor

This loops over all of the broken apart json data that lives in the subdirectorys under ./data/service_json/*/*
And creates a normalized series of CSV files with the following data: 

* Distinct Address File
* Distinct Organization File - This one should have the "counts" of linked data. Like: 'address_count', 'endpoint_count', 'npi_count' etc . To be valid, a record must a least have one npi and one fhir endpoint.
* Distinct Endpoint File
* Distinct Phone File
* Distinct Contact URL
* Organization to NPI field - this should note when there is an NPI that is not 10 digits with is_invalid_NPI = 1 
* Organization to Phone 
* Organization to Address
* Oragnization to Endpoint
* Organization to Contact URL
* Error file. In the event that it is not possible to open and parse a file at all, list the filename here, along with the error encountered opening the file. 

NPI records live inside "identifier" blocks. Normally there is only one per organizational record, but there could be many. 
NPIs are always 10 digits and usually have the "system" value of "http://hl7.org/fhir/sid/us-npi". 

Put all of the resulting csv files in ./data/normalized_csv_files

NPI Validation:
NPIs are currently validated for format only (10-digit requirement).
API validation against the CMS NPI Registry has been disabled for performance reasons.
The validation columns (api_error, result_count) contain placeholder values ('?') for future implementation.
Format validation results are included in the is_invalid_npi field (0=valid format, 1=invalid format).

Test Mode:
Use the --test flag to run in test mode, which only processes the first 1000 files per EHR vendor.
This is useful for validation and testing without processing the entire dataset.

Usage:
  python Step40_extract_csv_data.py                    # Process all files
  python Step40_extract_csv_data.py --test             # Test mode: first 1000 files per vendor


"""

import json
import os
import csv
import re
import argparse
from pathlib import Path
from collections import defaultdict
import hashlib
import requests
import time
import phonenumbers
from phonenumbers import NumberParseException

def is_valid_npi_format(npi_value):
    """Check if NPI is exactly 10 digits"""
    if not npi_value:
        return False
    # Remove any non-digit characters and check if it's exactly 10 digits
    digits_only = re.sub(r'\D', '', str(npi_value))
    return len(digits_only) == 10

def validate_npi_via_api(npi_value, max_retries=3, delay=0.1):
    """
    Validate NPI against the CMS NPI Registry API
    Returns dict with validation results
    """
    if not is_valid_npi_format(npi_value):
        return {
            'is_valid_format': False,
            'is_valid_api': False,
            'api_error': 'Invalid NPI format',
            'result_count': 0
        }
    
    # Clean the NPI value to digits only
    clean_npi = re.sub(r'\D', '', str(npi_value))
    
    url = f"https://npiregistry.cms.hhs.gov/api/?version=2.1&number={clean_npi}"
    
    for attempt in range(max_retries):
        try:
            # Add a small delay to be respectful to the API
            if attempt > 0:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result_count = data.get('result_count', 0)
            
            return {
                'is_valid_format': True,
                'is_valid_api': result_count > 0,
                'api_error': None,
                'result_count': result_count
            }
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:  # Last attempt
                return {
                    'is_valid_format': True,
                    'is_valid_api': False,
                    'api_error': f"API request failed: {str(e)}",
                    'result_count': 0
                }
            # Continue to next attempt
            continue
        except Exception as e:
            return {
                'is_valid_format': True,
                'is_valid_api': False,
                'api_error': f"Unexpected error: {str(e)}",
                'result_count': 0
            }
    
    return {
        'is_valid_format': True,
        'is_valid_api': False,
        'api_error': "Max retries exceeded",
        'result_count': 0
    }

def extract_npi_identifiers(identifiers):
    """Extract NPI identifiers from identifier array"""
    npis = []
    if not identifiers:
        return npis
    
    for identifier in identifiers:
        system = identifier.get('system', '')
        value = identifier.get('value', '')
        
        # Check for NPI system or if value looks like an NPI (10 digits)
        if ('us-npi' in system.lower() or 
            'npi' in system.lower() or 
            is_valid_npi_format(value)):
            
            # Skip API validation for now - use placeholder values for future implementation
            # api_result = validate_npi_via_api(value)  # Commented out for performance
            
            npi_record = {
                'system': system,
                'value': value,
                'is_valid': '?',  # Placeholder - will be implemented in future phase
                'api_error': None,
                'result_count': '?'  # Placeholder - will be implemented in future phase
            }
            
            npis.append(npi_record)
            
            # No delay needed since we're not making API calls
            # time.sleep(0.1)  # Commented out since no API calls
    
    return npis

def normalize_phone_number(phone_value):
    """
    Normalize phone number using phonenumbers library
    Returns dict with normalized number, extension, and validation info
    """
    if not phone_value:
        return {
            'original_value': phone_value,
            'normalized_number': '',
            'extension': '',
            'country_code': '',
            'is_valid': False,
            'parse_error': 'Empty phone number'
        }
    
    # Clean the input - remove common prefixes and formatting
    cleaned_value = str(phone_value).strip()
    
    # Try to extract extension first (common patterns)
    extension = ''
    extension_patterns = [
        r'\s*(?:ext\.?|extension|x)\s*(\d+)$',
        r'\s*#(\d+)$',
        r'\s*,\s*(\d+)$'
    ]
    
    for pattern in extension_patterns:
        match = re.search(pattern, cleaned_value, re.IGNORECASE)
        if match:
            extension = match.group(1)
            cleaned_value = re.sub(pattern, '', cleaned_value, flags=re.IGNORECASE).strip()
            break
    
    try:
        # Try parsing as US number first (most common case)
        try:
            parsed_number = phonenumbers.parse(cleaned_value, "US")
        except NumberParseException:
            # If US parsing fails, try without region
            parsed_number = phonenumbers.parse(cleaned_value, None)
        
        # Validate the parsed number
        is_valid = phonenumbers.is_valid_number(parsed_number)
        
        # Format the number in international format
        if is_valid:
            normalized_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            country_code = f"+{parsed_number.country_code}"
        else:
            normalized_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            country_code = f"+{parsed_number.country_code}" if hasattr(parsed_number, 'country_code') else ''
        
        return {
            'original_value': phone_value,
            'normalized_number': normalized_number,
            'extension': extension,
            'country_code': country_code,
            'is_valid': is_valid,
            'parse_error': None
        }
        
    except NumberParseException as e:
        return {
            'original_value': phone_value,
            'normalized_number': '',
            'extension': extension,
            'country_code': '',
            'is_valid': False,
            'parse_error': str(e)
        }
    except Exception as e:
        return {
            'original_value': phone_value,
            'normalized_number': '',
            'extension': extension,
            'country_code': '',
            'is_valid': False,
            'parse_error': f"Unexpected error: {str(e)}"
        }

def extract_addresses(addresses):
    """Extract and normalize address information"""
    address_list = []
    if not addresses:
        return address_list
    
    for addr in addresses:
        # Extract address lines separately
        lines = addr.get('line', [])
        address_line1 = lines[0] if len(lines) > 0 else ''
        address_line2 = lines[1] if len(lines) > 1 else ''
        
        # Create a normalized address record
        address_record = {
            'type': addr.get('type', ''),
            'text': addr.get('text', ''),
            'address_line1': address_line1,
            'address_line2': address_line2,
            'city': addr.get('city', ''),
            'state': addr.get('state', ''),
            'postal_code': addr.get('postalCode', ''),
            'country': addr.get('country', ''),
            'use': addr.get('use', '')
        }
        address_list.append(address_record)
    
    return address_list

def extract_telecoms(telecoms):
    """Extract phone, contact URL, and email information"""
    phones = []
    contact_urls = []
    emails = []
    
    if not telecoms:
        return phones, contact_urls, emails
    
    for telecom in telecoms:
        system = telecom.get('system', '').lower()
        value = telecom.get('value', '')
        use = telecom.get('use', '')
        
        if system == 'phone':
            # Normalize the phone number
            normalized_phone = normalize_phone_number(value)
            phones.append({
                'original_value': normalized_phone['original_value'],
                'normalized_number': normalized_phone['normalized_number'],
                'extension': normalized_phone['extension'],
                'country_code': normalized_phone['country_code'],
                'is_valid': normalized_phone['is_valid'],
                'parse_error': normalized_phone['parse_error'],
                'use': use
            })
        elif system == 'email':
            emails.append({
                'value': value,
                'use': use
            })
        elif system == 'url':
            contact_urls.append({
                'system': system,
                'value': value,
                'use': use
            })
    
    return phones, contact_urls, emails

def extract_endpoints(endpoints, endpoint_reference_to_url=None):
    """Extract endpoint references and URLs"""
    endpoint_list = []
    if not endpoints:
        return endpoint_list
    
    if endpoint_reference_to_url is None:
        endpoint_reference_to_url = {}
    
    for endpoint in endpoints:
        reference = endpoint.get('reference', '')
        # Resolve the reference to actual URL using the mapping
        url = endpoint_reference_to_url.get(reference, reference)
        
        endpoint_list.append({
            'reference': reference,
            'url': url
        })
    
    return endpoint_list

def generate_hash_id(data_dict):
    """Generate a hash ID for deduplication"""
    # Create a string representation of the data for hashing
    data_str = json.dumps(data_dict, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()[:16]

def process_organization_file(file_path, vendor_name, endpoint_reference_to_url=None):
    """Process a single organization JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        resource = data.get('resource', {})
        if resource.get('resourceType') != 'Organization':
            return None
        
        # Use fullUrl as the primary identifier
        full_url = data.get('fullUrl', '')
        if not full_url:
            # Skip entries that don't have fullUrl
            return None
        
        org_id = full_url
        org_name = resource.get('name', '')
        active = resource.get('active', False)
        
        # Extract various data elements
        identifiers = resource.get('identifier', [])
        addresses = resource.get('address', [])
        telecoms = resource.get('telecom', [])
        endpoints = resource.get('endpoint', [])
        
        # Process each data type
        npis = extract_npi_identifiers(identifiers)
        address_list = extract_addresses(addresses)
        phones, contact_urls, emails = extract_telecoms(telecoms)
        endpoint_list = extract_endpoints(endpoints, endpoint_reference_to_url)
        
        return {
            'org_id': org_id,
            'org_name': org_name,
            'vendor_name': vendor_name,
            'active': active,
            'npis': npis,
            'addresses': address_list,
            'phones': phones,
            'contact_urls': contact_urls,
            'emails': emails,
            'endpoints': endpoint_list,
            'file_path': str(file_path)
        }
        
    except Exception as e:
        return {'error': str(e), 'file_path': str(file_path)}

def process_endpoint_file(file_path, vendor_name):
    """Process a single endpoint JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        resource = data.get('resource', {})
        if resource.get('resourceType') != 'Endpoint':
            return None
        
        # Use fullUrl as the primary identifier, but only if it's https
        full_url = data.get('fullUrl', '')
        if not full_url.startswith('https://'):
            # Skip entries that don't have https fullUrl
            return None
        
        endpoint_id = full_url
        endpoint_name = resource.get('name', '')
        endpoint_address = resource.get('address', '')
        status = resource.get('status', '')
        
        return {
            'endpoint_id': endpoint_id,
            'endpoint_name': endpoint_name,
            'endpoint_address': endpoint_address,
            'status': status,
            'vendor_name': vendor_name,
            'file_path': str(file_path)
        }
        
    except Exception as e:
        return {'error': str(e), 'file_path': str(file_path)}

def main():
    parser = argparse.ArgumentParser(description='Extract CSV data from FHIR Organization JSON files')
    parser.add_argument('--input_dir', default='./data/service_json', 
                       help='Input directory containing vendor subdirectories with JSON files')
    parser.add_argument('--output_dir', default='./output_data/normalized_csv_files',
                       help='Output directory for CSV files')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: only process first 1000 files per vendor for validation')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Data collections for deduplication
    distinct_addresses = {}
    distinct_organizations = {}
    distinct_endpoints = {}
    distinct_phones = {}
    distinct_contact_urls = {}
    distinct_emails = {}
    
    # Relationship tables
    org_to_npi = []
    org_to_phone = []
    org_to_address = []
    org_to_endpoint = []
    org_to_contact_url = []
    org_to_email = []
    
    # Error tracking
    errors = []
    
    # Endpoint reference to URL mapping
    endpoint_reference_to_url = {}
    
    print(f"Processing files from: {input_path}")
    print(f"Output directory: {output_path}")
    if args.test:
        print("*** TEST MODE: Only processing first 1000 files per vendor ***")
    
    # Process each vendor directory
    vendor_dirs = [d for d in input_path.iterdir() if d.is_dir()]
    total_files = 0
    processed_files = 0
    
    # PASS 1: Process all files to build endpoint reference mapping
    print("\nPass 1: Building endpoint reference mapping...")
    for vendor_dir in vendor_dirs:
        vendor_name = vendor_dir.name
        json_files = list(vendor_dir.glob('*.json'))
        
        # In test mode, limit to first 1000 files per vendor
        if args.test and len(json_files) > 1000:
            json_files = json_files[:1000]
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                resource = data.get('resource', {})
                if resource.get('resourceType') == 'Endpoint':
                    full_url = data.get('fullUrl', '')
                    endpoint_id = resource.get('id', '')
                    endpoint_address = resource.get('address', '')
                    
                    if endpoint_address:
                        # Map both fullUrl and Endpoint/id formats
                        if full_url:
                            endpoint_reference_to_url[full_url] = endpoint_address
                        if endpoint_id:
                            endpoint_reference_to_url[f'Endpoint/{endpoint_id}'] = endpoint_address
                        
            except Exception as e:
                # Skip files that can't be processed in pass 1
                continue
    
    print(f"Found {len(endpoint_reference_to_url)} endpoint mappings")
    
    # PASS 2: Process organization files with endpoint resolution
    print("\nPass 2: Processing organizations with endpoint resolution...")
    for vendor_dir in vendor_dirs:
        vendor_name = vendor_dir.name
        print(f"\nProcessing vendor: {vendor_name}")
        
        # Process JSON files in vendor directory
        json_files = list(vendor_dir.glob('*.json'))
        
        # In test mode, limit to first 1000 files per vendor
        if args.test and len(json_files) > 1000:
            json_files = json_files[:1000]
            print(f"  TEST MODE: Limited to first 1000 files (out of {len(list(vendor_dir.glob('*.json')))} total)")
        
        total_files += len(json_files)
        
        for json_file in json_files:
            result = process_organization_file(json_file, vendor_name, endpoint_reference_to_url)
            
            if result is None:
                continue
                
            if 'error' in result:
                errors.append({
                    'file_path': result['file_path'],
                    'error': result['error']
                })
                continue
            
            processed_files += 1
            
            # Extract organization data
            org_data = {
                'org_id': result['org_id'],
                'org_name': result['org_name'],
                'vendor_name': result['vendor_name'],
                'active': result['active'],
                'address_count': len(result['addresses']),
                'endpoint_count': len(result['endpoints']),
                'npi_count': len(result['npis']),
                'phone_count': len(result['phones']),
                'contact_url_count': len(result['contact_urls']),
                'email_count': len(result['emails'])
            }
            
            # Only include organizations with at least one NPI and one endpoint
            if org_data['npi_count'] > 0 and org_data['endpoint_count'] > 0:
                org_hash = generate_hash_id(org_data)
                distinct_organizations[org_hash] = org_data
                
                # Process addresses
                for addr in result['addresses']:
                    addr_hash = generate_hash_id(addr)
                    distinct_addresses[addr_hash] = addr
                    
                    org_to_address.append({
                        'org_id': result['org_id'],
                        'address_hash': addr_hash
                    })
                
                # Process NPIs
                for npi in result['npis']:
                    # Since we're not doing API validation, use format validation for is_invalid_npi
                    is_invalid = 0 if is_valid_npi_format(npi['value']) else 1
                    
                    org_to_npi.append({
                        'org_id': result['org_id'],
                        'npi_system': npi['system'],
                        'npi_value': npi['value'],
                        'is_invalid_npi': is_invalid,
                        'api_error': npi['api_error'],
                        'result_count': npi['result_count']
                    })
                
                # Process phones
                for phone in result['phones']:
                    phone_hash = generate_hash_id(phone)
                    distinct_phones[phone_hash] = phone
                    
                    org_to_phone.append({
                        'org_id': result['org_id'],
                        'phone_hash': phone_hash
                    })
                
                # Process contact URLs
                for contact_url in result['contact_urls']:
                    url_hash = generate_hash_id(contact_url)
                    distinct_contact_urls[url_hash] = contact_url
                    
                    org_to_contact_url.append({
                        'org_id': result['org_id'],
                        'contact_url_hash': url_hash
                    })
                
                # Process emails
                for email in result['emails']:
                    email_hash = generate_hash_id(email)
                    distinct_emails[email_hash] = email
                    
                    org_to_email.append({
                        'org_id': result['org_id'],
                        'email_hash': email_hash
                    })
                
                # Process endpoints
                for endpoint in result['endpoints']:
                    endpoint_hash = generate_hash_id(endpoint)
                    distinct_endpoints[endpoint_hash] = endpoint
                    
                    org_to_endpoint.append({
                        'org_id': result['org_id'],
                        'endpoint_hash': endpoint_hash
                    })
            

            print_pip_every = 10

            # Progress indicator
            if processed_files % print_pip_every == 0:
                print('.', end='', flush=True)
            if processed_files % 1000 == 0:
                print(f"\n  Processed {processed_files} files in total...")
    
    print(f"\nProcessing complete!")
    if args.test:
        print("*** TEST MODE RESULTS ***")
    print(f"Total files processed: {total_files}")
    print(f"Successfully processed: {processed_files}")
    print(f"Errors encountered: {len(errors)}")
    print(f"Valid organizations (with NPI + endpoint): {len(distinct_organizations)}")
    
    # Write CSV files
    print("\nWriting CSV files...")
    
    # Distinct Organizations
    with open(output_path / 'distinct_organizations.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['org_id', 'org_name', 'vendor_name', 'active', 'address_count', 'endpoint_count', 'npi_count', 'phone_count', 'contact_url_count', 'email_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if distinct_organizations:
            writer.writerows(distinct_organizations.values())
    
    # Distinct Addresses
    with open(output_path / 'distinct_addresses.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['address_hash', 'type', 'text', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'use']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if distinct_addresses:
            for addr_hash, addr_data in distinct_addresses.items():
                row = {'address_hash': addr_hash}
                row.update(addr_data)
                writer.writerow(row)
    
    # Distinct Endpoints
    with open(output_path / 'distinct_endpoints.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['endpoint_hash', 'reference', 'url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if distinct_endpoints:
            for endpoint_hash, endpoint_data in distinct_endpoints.items():
                row = {'endpoint_hash': endpoint_hash}
                row.update(endpoint_data)
                writer.writerow(row)
    
    # Distinct Phones
    with open(output_path / 'distinct_phones.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['phone_hash', 'original_value', 'normalized_number', 'extension', 'country_code', 'is_valid', 'parse_error', 'use']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if distinct_phones:
            for phone_hash, phone_data in distinct_phones.items():
                row = {'phone_hash': phone_hash}
                row.update(phone_data)
                writer.writerow(row)
    
    # Distinct Contact URLs
    with open(output_path / 'distinct_contact_urls.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['contact_url_hash', 'system', 'value', 'use']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if distinct_contact_urls:
            for url_hash, url_data in distinct_contact_urls.items():
                row = {'contact_url_hash': url_hash}
                row.update(url_data)
                writer.writerow(row)
    
    # Distinct Contact Emails
    with open(output_path / 'distinct_contact_emails.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['email_hash', 'value', 'use']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if distinct_emails:
            for email_hash, email_data in distinct_emails.items():
                row = {'email_hash': email_hash}
                row.update(email_data)
                writer.writerow(row)
    
    # Organization to NPI relationships
    with open(output_path / 'org_to_npi.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['org_id', 'npi_system', 'npi_value', 'is_invalid_npi', 'api_error', 'result_count'])
        writer.writeheader()
        if org_to_npi:
            writer.writerows(org_to_npi)
    
    # Organization to Phone relationships
    with open(output_path / 'org_to_phone.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['org_id', 'phone_hash'])
        writer.writeheader()
        if org_to_phone:
            writer.writerows(org_to_phone)
    
    # Organization to Address relationships
    with open(output_path / 'org_to_address.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['org_id', 'address_hash'])
        writer.writeheader()
        if org_to_address:
            writer.writerows(org_to_address)
    
    # Organization to Endpoint relationships
    with open(output_path / 'org_to_endpoint.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['org_id', 'endpoint_hash'])
        writer.writeheader()
        if org_to_endpoint:
            writer.writerows(org_to_endpoint)
    
    # Organization to Contact URL relationships
    with open(output_path / 'org_to_contact_url.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['org_id', 'contact_url_hash'])
        writer.writeheader()
        if org_to_contact_url:
            writer.writerows(org_to_contact_url)
    
    # Organization to Email relationships
    with open(output_path / 'org_to_email.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['org_id', 'email_hash'])
        writer.writeheader()
        if org_to_email:
            writer.writerows(org_to_email)
    
    # Error file
    with open(output_path / 'processing_errors.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['file_path', 'error'])
        writer.writeheader()
        writer.writerows(errors)
    
    print(f"CSV files written to: {output_path}")
    print(f"- distinct_organizations.csv: {len(distinct_organizations)} records")
    print(f"- distinct_addresses.csv: {len(distinct_addresses)} records")
    print(f"- distinct_endpoints.csv: {len(distinct_endpoints)} records")
    print(f"- distinct_phones.csv: {len(distinct_phones)} records")
    print(f"- distinct_contact_urls.csv: {len(distinct_contact_urls)} records")
    print(f"- distinct_contact_emails.csv: {len(distinct_emails)} records")
    print(f"- org_to_npi.csv: {len(org_to_npi)} records")
    print(f"- org_to_phone.csv: {len(org_to_phone)} records")
    print(f"- org_to_address.csv: {len(org_to_address)} records")
    print(f"- org_to_endpoint.csv: {len(org_to_endpoint)} records")
    print(f"- org_to_contact_url.csv: {len(org_to_contact_url)} records")
    print(f"- org_to_email.csv: {len(org_to_email)} records")
    print(f"- processing_errors.csv: {len(errors)} records")

if __name__ == "__main__":
    main()
