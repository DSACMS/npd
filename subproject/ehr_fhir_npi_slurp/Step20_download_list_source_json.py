#!/usr/bin/env python3
"""
This file accepts the csv file output by Step10_extract_list_source_from_lantern_csv.py
And then downloads all of the source list files (which are usually json files) and puts them into 
./data/source_list_json/

The structure of the input file (which is listed in the first line of the CSV) is: 

list_source,certified_api_developer_name,distinct_url_count

This script should create a good filename for each download file, by creating a 'safe_file_name_string' from the certified_api_developer_name column. 
To do this replace all special characters with spaces. Then convert all groups of spaces into underscores. and then convert all of the letters to lower-case.

Then rename the downloaded json file to ./data/source_list_json/new_safe_ehr_vendor_name.json 

Do this for every list_source in the --input_file
"""

import argparse
import pandas as pd
import requests
import re
import os
import sys
import time
from urllib.parse import urlparse

def create_safe_filename(vendor_name):
    """
    Create a safe filename from the vendor name by:
    1. Replacing special characters with spaces
    2. Converting groups of spaces to underscores
    3. Converting to lowercase
    """
    # Replace all non-alphanumeric characters with spaces
    safe_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', vendor_name)
    
    # Convert multiple spaces to single spaces, then to underscores
    safe_name = re.sub(r'\s+', '_', safe_name.strip())
    
    # Convert to lowercase
    safe_name = safe_name.lower()
    
    return safe_name

def download_json_file(url, output_path, timeout=30):
    """
    Download a JSON file from the given URL and save it to output_path
    Returns True if successful, False otherwise
    """
    try:
        # Add headers to mimic a real browser request, but don't request compression
        # to avoid issues with automatic decompression
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, verify=True)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the content to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {str(e)}")
        return False
    except Exception as e:
        print(f"Error saving file {output_path}: {str(e)}")
        return False

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Download JSON files from list_source URLs')
    parser.add_argument('--input_file', required=True, help='Input CSV file path (output from Step10)')
    parser.add_argument('--output_dir', default='./data/source_list_json/', help='Output directory for downloaded JSON files')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between downloads in seconds (default: 1.0)')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds (default: 30)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        sys.exit(1)
    
    # Expected column headers
    expected_headers = ['list_source', 'certified_api_developer_name', 'distinct_url_count']
    
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
        
        print(f"Processing {len(df)} entries from '{args.input_file}'")
        print(f"Output directory: {args.output_dir}")
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        successful_downloads = 0
        failed_downloads = 0
        
        # Process each row
        for row_num, (idx, row) in enumerate(df.iterrows()):
            list_source = row['list_source']
            vendor_name = row['certified_api_developer_name']
            
            # Skip rows with missing data - convert to string and check
            list_source_str = str(list_source)
            vendor_name_str = str(vendor_name)
            
            if list_source_str in ['nan', 'None', ''] or list_source_str.lower() == 'nan':
                print(f"Skipping row {row_num + 1}: Missing list_source")
                failed_downloads += 1
                continue
                
            if vendor_name_str in ['nan', 'None', ''] or vendor_name_str.lower() == 'nan':
                print(f"Skipping row {row_num + 1}: Missing vendor_name")
                failed_downloads += 1
                continue
            
            # Create safe filename
            safe_filename = create_safe_filename(str(vendor_name))
            output_path = os.path.join(args.output_dir, f"{safe_filename}.json")
            
            print(f"[{row_num + 1}/{len(df)}] Downloading from: {list_source}")
            print(f"  Vendor: {vendor_name}")
            print(f"  Output: {output_path}")
            
            # Download the file
            if download_json_file(str(list_source), output_path, args.timeout):
                print(f"  ✓ Success")
                successful_downloads += 1
            else:
                print(f"  ✗ Failed")
                failed_downloads += 1
            
            # Add delay between requests to be respectful to servers
            if row_num < len(df) - 1:  # Don't delay after the last request
                time.sleep(args.delay)
        
        print(f"\nDownload Summary:")
        print(f"  Successful: {successful_downloads}")
        print(f"  Failed: {failed_downloads}")
        print(f"  Total: {len(df)}")
        
        if failed_downloads > 0:
            print(f"\nNote: {failed_downloads} downloads failed. Check the URLs and network connectivity.")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
