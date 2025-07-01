#!/bin/bash
python ./nppes_endpoint/go.postgresql.py --csv_file=/Users/ftrotter/Downloads/NPPES_Data_Dissemination_June_2025_V2/endpoint_pfile_20050523-20250608.csv --db_schema_name=nppes_raw --table_name=endpoint_file
