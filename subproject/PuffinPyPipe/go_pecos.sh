#!/bin/bash
csviper full-compile --from_csv ~/Downloads/Medicare_Fee-For-Service_Public_Provider_Enrollment/2025-Q1/PPEF_Enrollment_Extract_2025.04.01.csv --output_dir=./pecos_enrollment/ --overwrite_previous
python pecos_enrollment/go.postgresql.py --csv_file /Users/ftrotter/Downloads/Medicare_Fee-For-Service_Public_Provider_Enrollment/2025-Q1/PPEF_Enrollment_Extract_2025.04.01.csv --db_schema_name=pecos_raw --table_name=pecos_enrollment


csviper full-compile --from_csv ~/Downloads/Medicare_Fee-For-Service_Public_Provider_Enrollment/2025-Q1/PPEF_Reassignment_Extract_2025.04.01.csv --output_dir=./pecos_enrollment/ --overwrite_previous
python pecos_enrollment/go.postgresql.py --csv_file /Users/ftrotter/Downloads/Medicare_Fee-For-Service_Public_Provider_Enrollment/2025-Q1/PPEF_Reassignment_Extract_2025.04.01.csv --db_schema_name=pecos_raw --table_name=pecos_reasignment

