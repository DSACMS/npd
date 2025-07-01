-- MySQL Post-Import: Create Indexes
-- Test file for CSViper post-import SQL functionality

-- Create index on first column for better query performance
CREATE INDEX idx_test_column1 ON REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME (column1);

-- Create index on second column
CREATE INDEX idx_test_column2 ON REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME (column2);

-- Show table status after index creation
SHOW INDEX FROM REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME;
