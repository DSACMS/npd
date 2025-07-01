"""
Configuration settings for EHR FHIR NPI Slurp pipeline
"""

import os
from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
PROD_DATA_DIR = PROJECT_ROOT / "prod_data"

# Data subdirectories
SERVICE_JSON_DIR = DATA_DIR / "service_json"
NORMALIZED_CSV_DIR = DATA_DIR / "normalized_csv_files"
JSON_CACHE_DIR = DATA_DIR / "json_data_cache"

# Input files
FHIR_ENDPOINTS_CSV = PROD_DATA_DIR / "fhir_endpoints.csv"
LIST_SOURCES_CSV = PROD_DATA_DIR / "list_sources_summary.csv"

# API Configuration
NPI_REGISTRY_BASE_URL = "https://npiregistry.cms.hhs.gov/api/"
NPI_API_VERSION = "2.1"
DEFAULT_REQUEST_TIMEOUT = int(os.getenv("FHIR_REQUEST_TIMEOUT", "30"))
DEFAULT_DOWNLOAD_DELAY = float(os.getenv("DOWNLOAD_DELAY", "1.0"))

# Processing limits
TEST_MODE_LIMIT = 1000  # Files per vendor in test mode
PROGRESS_UPDATE_INTERVAL = 10  # Show progress every N files

# Expected CSV headers for validation
LANTERN_CSV_HEADERS = [
    "url", "api_information_source_name", "created_at", "updated", 
    "list_source", "certified_api_developer_name", "capability_fhir_version", 
    "format", "http_response", "http_response_time_second", "smart_http_response", 
    "errors", "cap_stat_exists", "kind", "requested_fhir_version", "is_chpl"
]

LIST_SOURCES_CSV_HEADERS = [
    "list_source", "certified_api_developer_name", "distinct_url_count"
]

# NPI validation settings
NPI_SYSTEMS = {
    "http://hl7.org/fhir/sid/us-npi",
    "2.16.840.1.113883.4.6",  # OID form
}

# HTTP headers for requests
DEFAULT_HEADERS = {
    "Accept": "application/fhir+json",
    "User-Agent": "EHR-FHIR-NPI-Slurp/1.0"
}

DOWNLOAD_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
}

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Create directories if they don't exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        DATA_DIR,
        PROD_DATA_DIR,
        SERVICE_JSON_DIR,
        NORMALIZED_CSV_DIR,
        JSON_CACHE_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    # Test configuration
    ensure_directories()
    print("Configuration loaded successfully!")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Service JSON directory: {SERVICE_JSON_DIR}")
    print(f"Normalized CSV directory: {NORMALIZED_CSV_DIR}")
