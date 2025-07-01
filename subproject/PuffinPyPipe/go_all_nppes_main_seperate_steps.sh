#!/bin/bash
csviper extract-metadata --from_csv=/Users/ftrotter/Downloads/NPPES_Data_Dissemination_June_2025_V2/npidata_pfile_20050523-20250608.csv --output_dir=./nppes_main/ --overwrite_previous
csviper build-sql --from_metadata_json=./nppes/npidata_pfile_20050523-20250608.metadata.json --output_dir=./nppes_main/ --overwrite_previous
csviper build-import-script --from_resource_dir=./nppes_main/ --output_dir=./nppes_main/ --overwrite_previous
python ./nppes_main/go.postgresql.py --csv_file=/Users/ftrotter/Downloads/NPPES_Data_Dissemination_June_2025_V2/npidata_pfile_20050523-20250608.csv --db_schema_name=nppes_raw --table_name=main_file
