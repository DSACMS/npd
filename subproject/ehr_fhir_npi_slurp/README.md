# EHR FHIR Entity Slurp

# TODO 
* We need to streamline the whole process to account for the fact that some entry blocks, like 
data/service_json/athena-fhir-service-base-urls/entry_a1c9c7fe-6d45-5a92-922c-7bfcd55a062d.json
"forget" the URL they are sourced from. We need to figure out how to retain that information from a previous step so that we can keep everything in https. 


A comprehensive data processing pipeline for extracting, analyzing, and normalizing EHR (Electronic Health Records) FHIR endpoint data from healthcare providers. This tool helps assess HTI-2 compliance and generates normalized datasets for healthcare interoperability analysis.

## Overview

This project processes FHIR endpoint data through a multi-step pipeline:

1. **Extract List Sources** - Analyzes Lantern CSV data to identify unique EHR vendor service endpoints
2. **Download Service Data** - Retrieves FHIR Bundle JSON files from EHR vendors
3. **Parse FHIR Bundles** - Breaks down large FHIR bundles into individual resource files
4. **Extract & Normalize** - Creates normalized CSV datasets with proper data validation

## Features

- **NPI Validation**: Real-time validation against CMS NPI Registry API
- **Phone Number Normalization**: International phone number parsing and validation
- **Address Standardization**: Structured address parsing and normalization  
- **Data Deduplication**: Hash-based deduplication for efficient storage
- **Error Handling**: Comprehensive error tracking and reporting
- **Test Mode**: Limited processing for development and validation
- **Progress Tracking**: Visual progress indicators for long-running operations

## Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ehr_fhir_npi_slurp

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run the complete pipeline
./go.sh

# Or run individual steps:
python Step10_extract_list_source_from_lantern_csv.py --input_file prod_data/fhir_endpoints.csv --output_file prod_data/list_sources_summary.csv
python Step20_download_list_source_json.py --input_file prod_data/list_sources_summary.csv --output_dir ./data/service_json/
python Step30_parse_source_bundle.py --input_dir ./data/service_json/
python Step40_extract_csv_data.py
```

### Test Mode

For development and validation, use test mode to process only a subset of data:

```bash
python Step40_extract_csv_data.py --test
```

## Pipeline Steps

### Step 1: Extract List Sources
**File**: `Step10_extract_list_source_from_lantern_csv.py`

Processes Lantern FHIR endpoint CSV files to extract unique service list sources by EHR vendor.

**Input**: CSV with FHIR endpoint data
**Output**: Summary CSV with distinct list sources and URL counts

### Step 2: Download Service Data  
**File**: `Step20_download_list_source_json.py`

Downloads FHIR Bundle JSON files from EHR vendor service endpoints.

**Features**:
- Respectful rate limiting
- Safe filename generation
- Error handling and retry logic
- Progress tracking

### Step 3: Parse FHIR Bundles
**File**: `Step30_parse_source_bundle.py`

Breaks down large FHIR Bundle files into individual resource entries for easier processing.

**Features**:
- Batch processing of multiple files
- Resource type categorization
- Progress reporting
- Error handling

### Step 4: Extract & Normalize Data
**File**: `Step40_extract_csv_data.py`

Creates normalized CSV datasets from FHIR Organization resources.

**Output Files**:
- `distinct_organizations.csv` - Unique organizations with counts
- `distinct_addresses.csv` - Normalized address data
- `distinct_endpoints.csv` - FHIR endpoint references
- `distinct_phones.csv` - Validated phone numbers
- `distinct_contact_urls.csv` - Contact URLs and emails
- `org_to_*.csv` - Relationship mapping files
- `processing_errors.csv` - Error log

## Data Validation

### NPI Validation
- Format validation (10-digit requirement)
- API validation against CMS NPI Registry (currently disabled for performance)
- Validation columns preserved with placeholder values ('?') for future implementation
- Invalid NPI flagging based on format validation

### Phone Number Validation
- International format parsing using `phonenumbers` library
- Extension extraction and normalization
- Country code standardization
- Validation status tracking

### Data Quality Requirements
Organizations must have:
- At least one valid NPI identifier
- At least one FHIR endpoint
- Valid organizational name

## Configuration

### Environment Variables
```bash
# Optional: Set custom timeout for API requests
export FHIR_REQUEST_TIMEOUT=30

# Optional: Set custom delay between downloads
export DOWNLOAD_DELAY=1.0
```

### Command Line Options

**Step 2 - Download Options**:
```bash
--delay 2.0          # Delay between downloads (seconds)
--timeout 60         # Request timeout (seconds)
--output_dir ./data  # Custom output directory
```

**Step 4 - Processing Options**:
```bash
--test               # Process only first 1000 files per vendor
--input_dir ./data   # Custom input directory
--output_dir ./out   # Custom output directory
```

## Output Data Structure

### Organizations Table
- `org_id` - FHIR Organization ID
- `org_name` - Organization name
- `vendor_name` - EHR vendor name
- `active` - Organization status
- `*_count` - Counts of related data elements

### Relationship Tables
Link organizations to their associated data:
- NPIs (with validation status)
- Addresses (normalized)
- Phone numbers (validated)
- Endpoints (FHIR references)
- Contact information

## Error Handling

The pipeline includes comprehensive error handling:
- File processing errors logged to `processing_errors.csv`
- API validation errors tracked per NPI
- Network timeout handling with retries
- Malformed data detection and reporting

## Performance Considerations

- **Memory Usage**: Large FHIR bundles are processed incrementally
- **API Rate Limiting**: Built-in delays for NPI validation API
- **Disk Space**: Intermediate files can be large; monitor disk usage
- **Processing Time**: Full pipeline may take several hours for large datasets

## Development

### Code Style
```bash
# Format code
black *.py

# Lint code  
flake8 *.py
```

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.
```

### Adding New Steps
1. Create new `StepXX_description.py` file
2. Follow existing patterns for argument parsing
3. Add comprehensive error handling
4. Update `go.sh` script
5. Document in README

## Troubleshooting

### Common Issues

**Memory Errors**:
- Use test mode for development
- Process smaller batches
- Monitor system resources

**API Rate Limiting**:
- Increase delays between requests
- Check network connectivity
- Verify API endpoint availability

**File Permission Errors**:
- Check directory permissions
- Ensure sufficient disk space
- Verify file paths are correct

### Debug Mode
Enable verbose logging by setting:
```bash
export DEBUG=1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run code formatting and linting
5. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues and questions:
1. Check existing GitHub issues
2. Review troubleshooting section
3. Create new issue with detailed description

---

**Note**: This tool processes healthcare data. Ensure compliance with relevant privacy regulations (HIPAA, etc.) when handling real patient data.
