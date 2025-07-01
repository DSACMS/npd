-- MySQL Post-Import: Data Validation
-- Test file for CSViper post-import SQL functionality

-- Validate row count
SELECT 'Total Rows' as validation_type, COUNT(*) as count FROM REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME;

-- Check for null values in first column
SELECT 'Null Values in Column1' as validation_type, COUNT(*) as count 
FROM REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME 
WHERE column1 IS NULL OR column1 = '';

-- Check for null values in second column
SELECT 'Null Values in Column2' as validation_type, COUNT(*) as count 
FROM REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME 
WHERE column2 IS NULL OR column2 = '';

-- Show sample data
SELECT 'Sample Data' as validation_type, column1, column2 
FROM REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME 
LIMIT 5;
