#!/usr/bin/env python3
"""
FHIR Bundle Parser

This script parses a FHIR Bundle JSON file and extracts individual entries
into separate JSON files, organized by resource type and named by resource ID.

Features:
* Process a single file with --input_file
* Process all JSON files in a directory with --input_dir
* Automatically creates subdirectories with the same name as the input file (without .json extension)
* Extracts individual FHIR Bundle entries into separate JSON files

"""

import json
import os
from pathlib import Path
import sys
import argparse
import glob

def parse_fhir_bundle(input_file, output_dir):
    """
    Parse a FHIR Bundle and extract individual entries to separate files.
    
    Args:
        input_file (str): Path to the input FHIR Bundle JSON file
        output_dir (str): Directory to save individual entry files
    """
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading FHIR Bundle from: {input_file}")
    
    try:
        # Load the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            bundle = json.load(f)
        
        # Verify it's a FHIR Bundle
        if bundle.get('resourceType') != 'Bundle':
            print(f"Error: File is not a FHIR Bundle. Resource type: {bundle.get('resourceType')}")
            return False
        
        entries = bundle.get('entry', [])
        print(f"Found {len(entries)} entries in the bundle")
        
        # Statistics
        resource_counts = {}
        processed_count = 0
        error_count = 0
        
        # Process each entry
        for i, entry in enumerate(entries):
            try:
                resource = entry.get('resource', {})
                resource_type = resource.get('resourceType', 'Unknown')
                resource_id = resource.get('id', f'no_id_{i}')
                
                # Count resource types
                resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
                
                # Create filename: entry_{resource_id}.json
                filename = f"entry_{resource_id}.json"
                filepath = output_path / filename
                
                # Save the individual entry (including both resource and fullUrl if present)
                entry_data = {
                    'resource': resource
                }
                
                # Include fullUrl if present
                if 'fullUrl' in entry:
                    entry_data['fullUrl'] = entry['fullUrl']
                
                # Write to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(entry_data, f, indent=2, ensure_ascii=False)
                
                processed_count += 1
                
                # Progress indicator
                if processed_count % 1000 == 0:
                    print(f"Processed {processed_count} entries...")
                    
            except Exception as e:
                print(f"Error processing entry {i}: {e}")
                error_count += 1
                continue
        
        # Print summary
        print(f"\nProcessing complete!")
        print(f"Total entries processed: {processed_count}")
        print(f"Errors encountered: {error_count}")
        print(f"Output directory: {output_dir}")
        
        print(f"\nResource type breakdown:")
        for resource_type, count in sorted(resource_counts.items()):
            print(f"  {resource_type}: {count}")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def process_single_file(input_file):
    """
    Process a single FHIR Bundle file and create a subdirectory for its entries.
    
    Args:
        input_file (str): Path to the input FHIR Bundle JSON file
    
    Returns:
        bool: True if successful, False otherwise
    """
    input_path = Path(input_file)
    
    # Create output directory name by removing .json extension
    output_dir_name = input_path.stem
    output_dir = input_path.parent / output_dir_name
    
    print(f"\nProcessing: {input_file}")
    print(f"Output directory: {output_dir}")
    
    return parse_fhir_bundle(str(input_path), str(output_dir))

def main():
    """Main function to run the parser."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Parse FHIR Bundle JSON files and extract individual entries into separate JSON files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  %(prog)s --input_file bundle.json
  
  # Process all JSON files in a directory
  %(prog)s --input_dir ./data/service_json/
        """
    )
    
    # Create mutually exclusive group for input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    
    input_group.add_argument(
        '--input_file',
        type=str,
        help='Path to a single FHIR Bundle JSON file to process'
    )
    
    input_group.add_argument(
        '--input_dir',
        type=str,
        help='Directory containing FHIR Bundle JSON files to process'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    print("FHIR Bundle Parser")
    print("=" * 50)
    
    successful_files = 0
    failed_files = 0
    total_files = 0
    
    if args.input_file:
        # Process single file
        input_file = args.input_file
        
        print(f"Mode: Single file processing")
        print(f"Input file: {input_file}")
        
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' does not exist")
            sys.exit(1)
        
        # Check if it's a JSON file
        if not input_file.lower().endswith('.json'):
            print(f"Error: Input file must be a JSON file")
            sys.exit(1)
        
        total_files = 1
        if process_single_file(input_file):
            successful_files = 1
        else:
            failed_files = 1
            
    elif args.input_dir:
        # Process all JSON files in directory
        input_dir = args.input_dir
        
        print(f"Mode: Directory processing")
        print(f"Input directory: {input_dir}")
        
        # Check if input directory exists
        if not os.path.exists(input_dir):
            print(f"Error: Input directory '{input_dir}' does not exist")
            sys.exit(1)
        
        if not os.path.isdir(input_dir):
            print(f"Error: '{input_dir}' is not a directory")
            sys.exit(1)
        
        # Find all JSON files in the directory
        json_pattern = os.path.join(input_dir, "*.json")
        json_files = glob.glob(json_pattern)
        
        if not json_files:
            print(f"No JSON files found in directory: {input_dir}")
            sys.exit(1)
        
        # Sort files for consistent processing order
        json_files.sort()
        total_files = len(json_files)
        
        print(f"Found {total_files} JSON files to process")
        print()
        
        # Process each JSON file
        for i, json_file in enumerate(json_files, 1):
            print(f"[{i}/{total_files}] Processing: {os.path.basename(json_file)}")
            
            if process_single_file(json_file):
                successful_files += 1
                print("✓ Success")
            else:
                failed_files += 1
                print("✗ Failed")
    
    # Print final summary
    print("\n" + "=" * 50)
    print("PROCESSING SUMMARY")
    print("=" * 50)
    print(f"Total files processed: {total_files}")
    print(f"Successful: {successful_files}")
    print(f"Failed: {failed_files}")
    
    if failed_files > 0:
        print(f"\nWarning: {failed_files} files failed to process")
        sys.exit(1)
    else:
        print("\nAll files processed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
