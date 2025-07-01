#!/bin/bash

# EHR FHIR NPI Slurp Pipeline
# Complete data processing pipeline for FHIR endpoint analysis

set -e  # Exit on any error

echo "Starting EHR FHIR NPI Slurp Pipeline..."
echo "========================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Warning: Virtual environment not detected. Consider running:"
    echo "source source_me_to_get_venv.sh"
    echo ""
fi

# Step 1: Extract list sources from Lantern CSV
echo "Step 1: Extracting list sources from Lantern CSV..."
python Step10_extract_list_source_from_lantern_csv.py \
    --input_file prod_data/fhir_endpoints.csv \
    --output_file prod_data/list_sources_summary.csv

echo "✓ Step 1 completed"
echo ""

# Step 2: Download service JSON files
echo "Step 2: Downloading service JSON files..."
python Step20_download_list_source_json.py \
    --input_file ./prod_data/list_sources_summary.csv \
    --output_dir ./data/service_json/ \
    --delay 1.0

echo "✓ Step 2 completed"
echo ""

# Step 3: Parse FHIR bundles
echo "Step 3: Parsing FHIR bundles..."
python Step30_parse_source_bundle.py --input_dir ./data/service_json/

echo "✓ Step 3 completed"
echo ""

# Step 4: Extract and normalize CSV data
echo "Step 4: Extracting and normalizing CSV data..."
python Step40_extract_csv_data.py

echo "✓ Step 4 completed"
echo ""

echo "========================================"
echo "Pipeline completed successfully!"
echo ""
echo "Output files are available in:"
echo "  - ./data/normalized_csv_files/"
echo ""


echo "Additional options:"
echo "  - Run tests: python test_pipeline.py"
echo "  - Test mode (faster): python Step40_extract_csv_data.py --test"
