# CSViper Specification

## Purpose

The `CSViper` system automates the process of analyzing a CSV file and generating SQL scripts and a runnable Python program to load the data into a relational database. It supports multiple backends (MySQL and PostgreSQL) and assumes that the database is hosted remotely, while the CSV file resides on the local machine.

## Structure

As much as possible please design the system using class files that contain multiple static functions, using named keyword arguments.
Each of these "static function holder" class files should have one function that is the entrypoint, and that function should call other static functions
inside the class as needed. These other static functions should be prefixed with an underscore to communicate that they are not for outside consumption.
When it actually makes sense to have a class that should be instantiated as an Object and have object-level functions.. that is fine.
But there should be a specific reason why this is done. And the default should be a functional-style and unix-style "do one thing well" approach with the static function holding classes.

This will be a Command Line Interface (CLI) tool. It should use the python "click" library to handle the arguments.

One of the arguments to the command will be the output dir. If it is not specified, then the program should create a new directory with the same name as the .csv file, but with the .csv removed.
If that directory already exists, it should just be used.

Note: a current implementation of this can be found in [CSVRawImport.py](../../nppest2/CSVRawImport.py). This file needs to be broken up to seperate concerns. But you should read it next to ensure that the purpose is well-understood.

## Running the code

The code should have `#!/usr/bin/env python3` as its first line for eventual use as a stand-alone python CLI tool.

For now, the code will be run using:

```bash
> python3 csviper full_compile --from_csv={csv_file_name.csv} --output_dir={./your_output_dir/} --overwrite_previous=1
```

That code will run all three of the build steps. However, each stage should also be runnable seperately using the following commands:

```bash
> python3 csviper extract_metadata --from_csv={csv_file_name.csv} --output_dir={./your_output_dir/} --overwrite_previous=1
> python3 csviper build_sql --from_metadata_json={schema_metadata.json} --output_dir={./your_output_dir/} --overwrite_previous=1
> python3 csviper build_import_script --from_resource_dir={output_dir_from_previous_stages} --output_dir={./your_output_dir/} --overwrite_previous=1
```

## Phase 1: CSV Metadata Analysis (Shared)

### Package Name: csviper

### Class: `CSVMetadataExtractor`

#### Static Method: `fromFileToMetadata`

- **Input:**  
  - `full_path_to_csv_file` (string): Absolute path to the local CSV file.

- **Functionality:**
  1. **File validation**:  
     - Check that the file exists and is readable.
     - Confirm it contains at least two lines: a header row and one row of data.
     - Raise appropriate errors if any validation fails.
     - Use `csv.Sniffer` to detect the CSV's delimiter, quote character, and general format. If this does not work, the file is not valid.

  2. **Column name inference**:  
     - Extract column names from the header row.
     - Normalize column names using the `safe_column_renamer` method.

  3. **Column width analysis**:  
     - Read all data rows and track the maximum observed string length for each column.
     - Ensure each row has the same number of columns as the header.

  4. **Metadata output**:  
     - Write a metadata JSON file (`{output_dir}/<filename>.metadata.json`) containing:
       - Filename
       - Detected delimiter
       - Quote character
       - Normalized column names
       - Max length per column in the current file

---

## Phase 2: SQL Generation (Backend-Specific) Classes

Separate modules for **MySQL** and **PostgreSQL** read the shared metadata and generate SQL files accordingly.

### Modules:
- `MySQLSchemaGenerator.py`
- `PostgreSQLSchemaGenerator.py`

### Inputs for each module: 
* The metadata JSON file generated in the previous step

### Outputs for Each Module:
- A SQL file  containing:
  1. The create_table sql files should contain: 
     1. `CREATE DATABASE IF NOT EXISTS REPLACE_ME_DB_NAME`
     2. `DROP TABLE IF EXISTS REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME`
     3. `CREATE TABLE` using normalized column names and `VARCHAR(n)` types
        - Each `VARCHAR(n)` is sized as one character longer than the longest value in the column.
        - Always fully qualify the table name using `REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME`.
     4. Write out to: (`{output_dir}/<csv_file>.create_table_mysql.sql` or `{output_dir}/<csv_file>.create_table_postgres.sql`)
     5. SQL statements should be seperated by semicolons and newlines and be designed for human readablility

  
  2. A `LOAD DATA` (for MySQL) or `COPY` (for PostgreSQL) statement using placeholders for:
     - Database name: `REPLACE_ME_DB_NAME`
     - Table name: `REPLACE_ME_TABLE_NAME`
     - CSV path: `REPLACE_ME_CSV_FULL_PATH`
     - Should be saved to: `{output_dir}/
  3. Write out to: (`{output_dir}/<csv_file>.import_data_mysql.sql` or `{output_dir}/<csv_file>.import_data_postgres.sql`)

---

## Phase 3: Data Loader Script Generation (Backend-Specific)

Instead of directly executing data loads, the system generates a standalone Python script that can later be run to perform the actual import.

### Modules:
- `generate_mysql_gen_code.py`
- `generate_postgres_gen_code.py`

### Output:
- A generated Python script called go.py that lives in the {output_dir} directory and references the other files within the same directory

This script should support: 

```bash
>python go.py --env_file_location={./path/to/.env} --csv_file={./path/to/csv_file_to_import.csv} --db_schema_name={db_schema} --table_name={table_name} --trample=1 
```

The --trample flag will overwrite the previous import of the data with this new one.

## Phase 4: Post Import SQL

Underneath the {output_dir} there should be a directory full of SQL files that are numbered in the order they should be executed.

Add a new stage of the sql import process that happens after data upload, which is the "post_import_sql" stage. This will allow for tasks like data calculations, indexing and data transformations to occur. This should take the form of a new directory, full of numerically ordered SQL files, using the REPLACE_ME_DATABASE_NAME and REPLACE_ME_TABLE_NAME templating approach. Look in ./nppest2/post_import_sql/nppes_npidata_21f8c89f23754346123596e3f6c66417 for an example. When the numeric prefix of the files are the same, then can be run in an order, larger numbers should be run later on. So all of the 01_something steps, should complete before the 05_something steps, which are in front of the 12_something steps etc.

### Behavior of Generated Script

1. **Environment Setup**:
   - Loads database credentials from a local `.env` file using `dotenv`.
     - The go.py script should confirm that the .env file is excluded in the local .gitignore
     - Then go.py should look in the local directory for this file.
     - Then go.py should look in the parent directory for this file.
   - Required variables: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`.
   - DB_NAME is just used to connect to the database, if the --db_schema_name and --table_name arguments are missing the program should refuse to run.

2. **Sense Checking**:
    -Verify that the header of the metadata.json file matches the values found in the first row of the csv data. Generate an appropriate error and quit if this happens.

3. **SQL Loading**:
   - Reads the cached `CREATE TABLE` SQL script.
   - Replaces placeholders (`REPLACE_ME_DB_NAME`, `REPLACE_ME_TABLE_NAME`, `REPLACE_ME_CSV_FULL_PATH`) with actual values.

4. **Database Connection**:
   - Connects to the **remote database** using the appropriate Python adapter:
     - `pymysql` for MySQL
     - `psycopg2` for PostgreSQL

5. **Table Setup**:
   - Executes the `DROP TABLE` (if it exists) and `CREATE TABLE` statements on the remote database. Makings sure there is a "schema" that exists, and removing the previous table if --trample=1

6. **Data Loading**:
   - For **MySQL**: executes `LOAD DATA LOCAL INFILE` pointing to the local CSV file. Note that this assumes the CSV file is in the same place on the client and server systems.. for now.
   - For **PostgreSQL**: uses `psycopg2.copy_expert()` to execute the `COPY FROM STDIN` command, streaming the local CSV file into the remote database.

7. **Post Import SQL**:
   1. This stage should load all of the data in the correct order from {output_dir}/post_import_sql/*.sql 
   2. Then, this should the database connection to loop over these SQL: 
   3. For each SQL statement replace the REPLACE_ME_DATABASE_NAME and REPLACE_ME_TABLE_NAME with the schema and table names respectively
   4. Then execute each SQL statement, crashing when any of them fail with the corresponding error message from the database engine.
---

## Shared Utility Class: Column Name Normalization

## Method: `rename_column_list`
- **Input** a list of column names

- **Behavior**
  - Repeatidly call safe_column_renamer to get SQL safe column names. 
  - In the event that two column names with different inputs return the same 60 character result begin numbering them as this_long_column_name_002, this_long_column_name_003 etc.

- **Output**
  - A python dictionary of the original names as keys, mapping to the new safe column names. 

### Method: `safe_column_renamer`

- **Input:** A string (column name from the CSV header)

- **Behavior:**
  1. Replace all special characters (including spaces) with underscores.
  2. If the string starts with a digit, prefix it with an underscore.
  3. Truncate the result to 60 characters.


- **Output:** A sanitized, SQL-safe column name.
