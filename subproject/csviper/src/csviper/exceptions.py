"""
Custom exceptions for CSViper with specific error categories.
"""


class CSViperError(Exception):
    """Base exception for all CSViper errors."""
    
    def __init__(self, message: str, stage: str | None = None):
        super().__init__(message)
        self.stage = stage or "Unknown"
        self.message = message
    
    def __str__(self):
        return f"{self.stage}: {self.message}"


class CSVFileError(CSViperError):
    """Errors related to CSV file access and validation."""
    
    def __init__(self, message: str, file_path: str | None = None):
        super().__init__(message, "CSV File Error")
        self.file_path = file_path


class CSVParsingError(CSViperError):
    """Errors related to CSV parsing and format detection."""
    
    def __init__(self, message: str, file_path: str | None = None, line_number: int | None = None):
        super().__init__(message, "CSV Parsing Error")
        self.file_path = file_path
        self.line_number = line_number


class CSVEncodingError(CSViperError):
    """Errors related to CSV file encoding issues."""
    
    def __init__(self, message: str, file_path: str | None = None, encoding: str | None = None):
        super().__init__(message, "CSV Encoding Error")
        self.file_path = file_path
        self.encoding = encoding


class CSVValidationError(CSViperError):
    """Errors related to CSV data validation."""
    
    def __init__(self, message: str, file_path: str | None = None, line_number: int | None = None):
        super().__init__(message, "CSV Validation Error")
        self.file_path = file_path
        self.line_number = line_number


class MetadataError(CSViperError):
    """Errors related to metadata extraction and processing."""
    
    def __init__(self, message: str):
        super().__init__(message, "Metadata Error")


class SQLGenerationError(CSViperError):
    """Errors related to SQL script generation."""
    
    def __init__(self, message: str, db_type: str | None = None):
        super().__init__(message, "SQL Generation Error")
        self.db_type = db_type


class ImportScriptError(CSViperError):
    """Errors related to import script generation."""
    
    def __init__(self, message: str, db_type: str | None = None):
        super().__init__(message, "Import Script Error")
        self.db_type = db_type


class FileSystemError(CSViperError):
    """Errors related to file system operations."""
    
    def __init__(self, message: str, operation: str | None = None):
        super().__init__(message, "File System Error")
        self.operation = operation


class CacheError(CSViperError):
    """Errors related to caching operations."""
    
    def __init__(self, message: str):
        super().__init__(message, "Cache Error")


class ImportExecutionError(CSViperError):
    """Errors related to import script execution."""
    
    def __init__(self, message: str, script_type: str | None = None, original_error: Exception | None = None):
        super().__init__(message, "Import Execution Error")
        self.script_type = script_type
        self.original_error = original_error
        
    def __str__(self):
        base_msg = super().__str__()
        if self.script_type:
            base_msg = f"{base_msg} (Script Type: {self.script_type})"
        if self.original_error:
            base_msg = f"{base_msg}\nOriginal Error: {type(self.original_error).__name__}: {self.original_error}"
        return base_msg


class ConfigurationError(CSViperError):
    """Errors related to configuration and environment setup."""
    
    def __init__(self, message: str, config_type: str | None = None):
        super().__init__(message, "Configuration Error")
        self.config_type = config_type
        
    def __str__(self):
        base_msg = super().__str__()
        if self.config_type:
            base_msg = f"{base_msg} (Config Type: {self.config_type})"
        return base_msg


class DatabaseConnectionError(CSViperError):
    """Errors related to database connections."""
    
    def __init__(self, message: str, db_type: str | None = None, connection_details: dict | None = None):
        super().__init__(message, "Database Connection Error")
        self.db_type = db_type
        self.connection_details = connection_details or {}
        
    def __str__(self):
        base_msg = super().__str__()
        if self.db_type:
            base_msg = f"{base_msg} (Database Type: {self.db_type})"
        if self.connection_details:
            # Only show safe connection details (no passwords)
            safe_details = {k: v for k, v in self.connection_details.items() 
                          if k.lower() not in ['password', 'passwd', 'pwd']}
            if safe_details:
                base_msg = f"{base_msg}\nConnection Details: {safe_details}"
        return base_msg
