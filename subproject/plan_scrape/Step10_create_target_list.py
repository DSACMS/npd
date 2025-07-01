import csv
from collections import defaultdict

def create_unique_parent_org_file(file1, file2, output_file, required_columns):
    """
    Create a new CSV file with unique parent organizations and required columns.
    """
    # Read the data from the input files
    data1 = read_csv_data(file1)
    data2 = read_csv_data(file2)

    # Extract unique parent organizations
    parent_orgs = set()
    for row in data1 + data2:
        parent_org = row.get('Parent Organization', '').strip()
        if parent_org:
            parent_orgs.add(parent_org)

    # Create a dictionary to store data for each parent organization
    parent_org_data = defaultdict(dict)
    for row in data1 + data2:
        parent_org = row.get('Parent Organization', '').strip()
        if parent_org:
            for col in required_columns:
                parent_org_data[parent_org][col] = row.get(col, '')

    # Write the data to the output file
    with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=required_columns)
        writer.writeheader()
        for parent_org, data in parent_org_data.items():
            writer.writerow(data)

def read_csv_data(file_path):
    """
    Read the CSV file and return the data as a list of dictionaries.
    Skip the first two rows (the first row is the title, the second row is the column headers).
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        # Skip the first row (title)
        next(csvfile)

        # Read the rest of the file with the second row as headers
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)

    return data

def main():
    # Input file paths
    file1 = 'source_data/2025_partc_star_ratings.csv'
    file2 = 'source_data/MA_Contract_directory_2025_06.csv'

    # Output file path
    output_file = 'search_these.csv'

    # Required columns
    required_columns = ['Parent Organization', 'Contract Name', 'Organization Marketing Name']

    # Create the unique parent organization file
    create_unique_parent_org_file(file1, file2, output_file, required_columns)
    print(f"Unique parent organization file saved to {output_file}")

if __name__ == "__main__":
    main()
