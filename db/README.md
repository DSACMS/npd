This directory stores SQL code
=======
To add code here, please follow the [SQL Coding Standards](./tinman_SQL_schema_standard/README.md)
Please use the .sqlfluff file in your preferred development environment, and manually apply the other rules for now.

### Local Database Setup
1. Create a local postgres server
2. Create a database called npd
3. Execute the sql in `schemas/npd.sql` to create the npd schema and associated tables
4. Execute the sql in `inserts/sample_data.sql` to load sample data into the database.

