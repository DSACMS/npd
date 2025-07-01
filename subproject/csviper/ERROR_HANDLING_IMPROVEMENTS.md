# CSViper Error Handling Improvements

## Overview

This document outlines the comprehensive improvements made to CSViper's error handling system to provide more detailed and actionable error information instead of vague error messages.

## Problem Addressed

The original issue was that CSViper was producing vague error messages like:
```
Error: too many values to unpack (expected 4)
```

This error provided no context about:
- What operation was failing
- What the underlying cause was
- How to fix the problem
- Which part of the system was affected

## Solutions Implemented

### 1. New Exception Classes

Added comprehensive exception classes in `src/csviper/exceptions.py`:

- **ImportExecutionError**: For errors during import script execution
- **ConfigurationError**: For configuration and environment setup issues
- **DatabaseConnectionError**: For database connection problems

Each exception includes:
- Detailed error messages
- Context information (script type, database type, etc.)
- Original error preservation
- Safe connection details (passwords excluded)

### 2. Fixed Tuple Unpacking Issue

**Root Cause**: The `load_and_validate_config` method returns 5 values:
```python
return db_config, db_schema_name, table_name, metadata, encoding
```

But generated scripts were trying to unpack only 4 values:
```python
db_config, db_schema_name, table_name, metadata = ImportExecutor.load_and_validate_config(...)
```

**Solution**: Updated both PostgreSQL and MySQL import script generators to:
1. Unpack the correct number of values (5 instead of 4)
2. Add specific error handling for unpacking issues
3. Provide clear guidance when version mismatches occur

### 3. Enhanced Database Connection Error Handling

Added detailed error handling for database connections that includes:
- Database type (PostgreSQL/MySQL)
- Connection parameters (excluding passwords)
- Specific error messages for common issues
- Installation instructions for missing libraries

### 4. Improved CSV Validation Errors

Enhanced CSV header validation to provide:
- Specific column mismatch information
- Expected vs actual column names
- Column position information
- Encoding context

## Before vs After Examples

### Before (Vague Error)
```
Error: too many values to unpack (expected 4)
```

### After (Detailed Error)
```
Error: Import Execution Error: Configuration loading failed due to version mismatch. 
This error typically occurs when the import script expects a different number of return values 
from the configuration loader. Please regenerate the import scripts. (Script Type: PostgreSQL)
Original Error: ValueError: too many values to unpack (expected 4)
```

### Database Connection Error Example
```
Error: Database Connection Error: Failed to connect to PostgreSQL database: connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused (Database Type: PostgreSQL)
Connection Details: {'host': 'localhost', 'port': '5432', 'user': 'testuser', 'database': 'testdb'}
```

### CSV Validation Error Example
```
Error: Import Execution Error: CSV header validation failed: Column 1 mismatch: Expected 'Name', got 'Full Name' (Script Type: PostgreSQL)
Original Error: ValueError: Column 1 mismatch: Expected 'Name', got 'Full Name'
```

## Files Modified

1. **src/csviper/exceptions.py**: Added new exception classes
2. **src/csviper/postgresql_import_script_generator.py**: Fixed unpacking and added error handling
3. **src/csviper/mysql_import_script_generator.py**: Fixed unpacking and added error handling
4. **src/csviper/import_executor.py**: Enhanced database connection error handling

## Regenerated Scripts

All existing import scripts need to be regenerated to benefit from these improvements:
- `test_complete/go.postgresql.py` - ✅ Regenerated
- `test_complete/go.mysql.py` - ✅ Regenerated
- `test_data/go.postgresql.py` - ✅ Regenerated
- `test_data/go.mysql.py` - ✅ Regenerated

## Benefits

1. **Actionable Error Messages**: Users now get specific instructions on how to fix problems
2. **Context Awareness**: Errors include information about which component failed
3. **Debugging Support**: Original errors are preserved for technical debugging
4. **Security**: Sensitive information (passwords) is excluded from error messages
5. **User Experience**: Clear guidance reduces frustration and support requests

## Usage

The improved error handling is automatically included in all newly generated import scripts. Existing scripts should be regenerated using:

```python
from csviper.postgresql_import_script_generator import PostgreSQLImportScriptGenerator
PostgreSQLImportScriptGenerator.fromResourceDirToScript('.', '.', overwrite_previous=True)
```

Or for MySQL:

```python
from csviper.mysql_import_script_generator import MySQLImportScriptGenerator
MySQLImportScriptGenerator.fromResourceDirToScript('.', '.', overwrite_previous=True)
