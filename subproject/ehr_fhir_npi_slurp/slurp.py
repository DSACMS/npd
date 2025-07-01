#!/usr/bin/env python3
"""
hti1_probe.py  –  Probe FHIR base URLs for HTI-1 organisational metadata.

INPUT
  1. Lantern-style CSV whose only required column is  "url"
     (the column may actually be called "resolves" in some Lantern exports)

OUTPUT
  A new CSV with columns
      url, npi, org_name, status, failure_reason
"""

import sys, csv, json, re, time, argparse, os
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from tqdm import tqdm

# ---------- configuration ----------
TIMEOUT = 15               # seconds per request
HEADERS = {"Accept": "application/fhir+json"}
NPI_SYSTEMS = {
    "http://hl7.org/fhir/sid/us-npi",
    "2.16.840.1.113883.4.6",          # OID form
}
# ------------------------------------

def save_json_cache(data, filename, base_url):
    """Save JSON data to cache directory with pretty printing"""
    if not data:
        return
    
    # Create cache directory if it doesn't exist
    cache_dir = "data/json_data_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create a safe filename from the base URL
    parsed_url = urlparse(base_url)
    safe_domain = re.sub(r'[^\w\-_.]', '_', parsed_url.netloc)
    cache_filename = f"{safe_domain}_{filename}.json"
    cache_path = os.path.join(cache_dir, cache_filename)
    
    # Save with pretty printing
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def safe_get(url):
    """GET URL and return (status, seconds, json_or_None, text)"""
    t0 = time.time()
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        elapsed = time.time() - t0
        try:
            js = r.json()
        except Exception:
            js = None
        return r.status_code, elapsed, js, r.text[:120]
    except Exception as e:
        return None, None, None, str(e)

def find_npi_in_resource(resource):
    """Return (npi, org_name) tuple or (None, None)."""
    if not isinstance(resource, dict):
        return (None, None)
    # 1) look for identifier with NPI system
    for ident in resource.get("identifier", []):
        if ident.get("system") in NPI_SYSTEMS:
            return ident.get("value"), resource.get("name")
    # 2) heuristic: any 10-digit number labelled NPI
    npi_regex = re.compile(r"\b\d{10}\b")
    for k, v in resource.items():
        if isinstance(v, str) and ("npi" in k.lower() or "npi" in v.lower()):
            m = npi_regex.search(v)
            if m:
                return m.group(), resource.get("name")
    return (None, None)

def probe_base(base_url):
    base_url = base_url.rstrip("/") + "/"   # normalise
    results = []  # Will collect multiple results, one per Organization
    
    base_outcome = {
        "url": base_url,
        "npi": "",
        "org_name": "",
        "status": "failure",
        "failure_reason": "",
    }

    # STEP 1 – /metadata
    meta_url = urljoin(base_url, "metadata")
    status, _, cap, txt = safe_get(meta_url)
    if status != 200 or not cap or cap.get("resourceType") != "CapabilityStatement":
        base_outcome["failure_reason"] = f"/metadata status {status or 'timeout'}"
        return [base_outcome]

    # Cache the CapabilityStatement metadata
    save_json_cache(cap, "metadata", base_url)

    # Try to find NPI directly in CapabilityStatement
    npi, org_name = find_npi_in_resource(cap)
    if npi:
        cap_outcome = base_outcome.copy()
        cap_outcome.update({
            "npi": npi, 
            "org_name": org_name or "", 
            "status": "success",
            "source": "CapabilityStatement"
        })
        results.append(cap_outcome)

    # STEP 2 – search Endpoint
    ep_search = urljoin(base_url, "Endpoint?_count=10")
    status, _, bundle, txt = safe_get(ep_search)
    if status != 200 or not bundle or bundle.get("resourceType") != "Bundle":
        if not results:  # Only return failure if we didn't find anything in CapabilityStatement
            base_outcome["failure_reason"] = f"/Endpoint search status {status or 'timeout'}"
            return [base_outcome]
        else:
            return results  # Return what we found in CapabilityStatement

    # Cache the Endpoint search bundle
    save_json_cache(bundle, "endpoint_bundle", base_url)

    # Collect all unique managingOrganization references
    org_refs = set()
    for entry in bundle.get("entry", []):
        ep = entry.get("resource", {})
        if ep.get("resourceType") != "Endpoint":
            continue
        org_ref = ep.get("managingOrganization", {}).get("reference")
        if org_ref:
            org_refs.add(org_ref)

    # Process each Organization
    organizations_processed = 0
    for org_ref in org_refs:
        # STEP 3 – follow Organization link
        org_url = urljoin(base_url, org_ref)
        status, _, org, txt = safe_get(org_url)
        
        org_outcome = base_outcome.copy()
        org_outcome["source"] = f"Organization/{org_ref}"
        
        if status != 200 or not org or org.get("resourceType") != "Organization":
            org_outcome["failure_reason"] = f"Org {org_ref} status {status or 'timeout'}"
            results.append(org_outcome)
            continue
        
        # Cache the Organization resource
        org_id = org_ref.replace('Organization/', '')  # Extract ID for filename
        save_json_cache(org, f"organization_{org_id}", base_url)
        
        npi, org_name = find_npi_in_resource(org)
        if npi:
            org_outcome.update({
                "npi": npi, 
                "org_name": org_name or "", 
                "status": "success"
            })
        else:
            org_outcome["failure_reason"] = "Organization exists, but no NPI identifier"
        
        results.append(org_outcome)
        organizations_processed += 1

    # If we didn't find any Organizations and didn't find anything in CapabilityStatement
    if not results:
        if organizations_processed == 0:
            base_outcome["failure_reason"] = "No managingOrganization in any Endpoint"
        return [base_outcome]
    
    return results

def main(src_csv, dst_csv, row_limit=None):
    df = pd.read_csv(src_csv)
    # Lantern sometimes labels the column "resolves" instead of "url"
    if "url" not in df.columns and "resolves" in df.columns:
        df.rename(columns={"resolves": "url"}, inplace=True)

    # Apply row limit if specified
    if row_limit is not None:
        df = df.head(row_limit)
        print(f"Processing limited to {row_limit} rows")

    all_results = []
    for url in tqdm(df["url"], desc="Checking"):
        url_results = probe_base(url)  # Returns a list of results
        all_results.extend(url_results)  # Add all results to the main list

    pd.DataFrame(all_results).to_csv(dst_csv, index=False)
    print(f"\nWritten report to {dst_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Probe FHIR base URLs for HTI-1 organisational metadata")
    parser.add_argument("input_csv", help="Input CSV file with URLs")
    parser.add_argument("output_csv", help="Output CSV file for results")
    parser.add_argument("-l", "--limit", type=int, metavar="N", 
                       help="Limit processing to N rows (e.g., -l 100 or --limit 100)")
    
    # Handle the special case of -NUMBER format (e.g., -100)
    # We need to check for arguments that start with dash followed by digits
    modified_args = []
    i = 0
    while i < len(sys.argv):
        arg = sys.argv[i]
        # Check if argument matches -NUMBER pattern (dash followed by digits)
        if re.match(r'^-\d+$', arg):
            # Convert -100 to --limit 100
            modified_args.extend(['--limit', arg[1:]])  # Remove the dash and use as limit value
        else:
            modified_args.append(arg)
        i += 1
    
    args = parser.parse_args(modified_args[1:])  # Skip script name
    main(args.input_csv, args.output_csv, args.limit)
