# Post-Import SQL Files for {filename_base}

This directory contains SQL files that will be executed after the CSV data import.

## File Naming Convention

Files should be named with a numeric prefix followed by a descriptive name:
- `01_create_indexes.postgresql.sql`
- `05_data_validation.postgresql.sql`
- `10_update_statistics.postgresql.sql`

## Execution Order

Files are executed in numeric order of their prefix:
- All `01_*` files run first
- Then all `05_*` files
- Then all `10_*` files, etc.

## Template Variables

Use these placeholders in your SQL files:
- `REPLACE_ME_DATABASE_NAME` - Will be replaced with the actual database name
- `REPLACE_ME_TABLE_NAME` - Will be replaced with the actual table name

## Example Files

Create your own SQL files in this directory for:
- Creating indexes
- Data validation queries
- Statistics updates
- Data transformations
- Custom calculations
