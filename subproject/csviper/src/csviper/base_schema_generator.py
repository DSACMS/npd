"""
Base Schema Generator for CSViper
Contains shared functionality between database-specific schema generators.
"""

import os
import json
import hashlib
import glob
from typing import Dict, Any, List
from .post_import_sql_generator import PostImportSQLGenerator
from .exceptions import CSVFileError, MetadataError, SQLGenerationError, FileSystemError


class BaseSchemaGenerator:
    """
    Base class for database-specific schema generators.
    Contains shared functionality for caching, file operations, and metadata handling.
    """
    
    @staticmethod
    def fromMetadataToSQL(metadata_json_path: str, output_dir: str, overwrite_previous: bool = False, 
                         db_type: str = None, generator_class=None) -> Dict[str, str]:
        """
        Generate SQL scripts from metadata JSON file using database-specific generator.
        
        Args:
            metadata_json_path (str): Path to the metadata JSON file
            output_dir (str): Output directory for SQL files
            overwrite_previous (bool): Whether to overwrite existing files
            db_type (str): Database type identifier for file naming
            generator_class: The specific generator class with SQL generation methods
            
        Returns:
            Dict[str, str]: Dictionary with paths to generated SQL files
            
        Raises:
            FileNotFoundError: If metadata JSON file does not exist
            ValueError: If metadata JSON is invalid
        """
        # Validate metadata file
        if not os.path.isfile(metadata_json_path):
            raise FileNotFoundError(f"Metadata JSON file not found: {metadata_json_path}")
        
        # Load metadata
        with open(metadata_json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Validate that normalized column names are unique
        from .metadata_extractor import CSVMetadataExtractor
        CSVMetadataExtractor._validate_column_mapping_uniqueness(metadata)
        
        # Validate required metadata fields
        required_fields = ['filename_without_extension', 'normalized_column_names', 'max_column_lengths']
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Required metadata field missing: {field}")
        
        print(f"Generating {db_type.upper()} SQL for: {metadata['filename_without_extension']}")
        
        # Create cache directory for CREATE TABLE SQL
        cache_dir = os.path.join(output_dir, 'cache_create_table_sql')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate cascading MD5 hash for caching (CSV headers + metadata content)
        # This ensures SQL regeneration when either CSV headers or metadata content changes
        csv_headers_str = ','.join([col.lower() for col in metadata['original_column_names']])
        
        # Create a deterministic string representation of the metadata content
        # Include key fields that affect SQL generation
        metadata_content_parts = [
            ','.join(metadata['normalized_column_names']),
            ','.join([f"{k}:{v}" for k, v in sorted(metadata['max_column_lengths'].items())]),
            ','.join([f"{k}:{v}" for k, v in sorted(metadata['column_name_mapping'].items())]),
            metadata['delimiter'],
            metadata['quote_character']
        ]
        metadata_content_str = '|'.join(metadata_content_parts)
        
        # Combine CSV headers and metadata content for cascading hash
        combined_content = f"{csv_headers_str}#{metadata_content_str}"
        column_md5_hash = hashlib.md5(combined_content.encode()).hexdigest()
        
        # Check for cached CREATE TABLE SQL
        create_table_sql = BaseSchemaGenerator._get_or_create_table_sql(
            metadata, cache_dir, column_md5_hash, overwrite_previous, db_type, generator_class
        )
        
        # Generate data import SQL with caching
        import_sql = BaseSchemaGenerator._get_or_create_import_sql(
            metadata, output_dir, column_md5_hash, overwrite_previous, db_type, generator_class
        )
        
        # Write SQL files to output directory
        filename_base = metadata['filename_without_extension']
        
        # Determine file extensions based on database type
        db_extension = BaseSchemaGenerator._get_file_extension(db_type)
        create_table_file = os.path.join(output_dir, f"{filename_base}.create_table_{db_extension}.sql")
        import_data_file = os.path.join(output_dir, f"{filename_base}.import_data_{db_extension}.sql")
        
        # Write CREATE TABLE SQL
        with open(create_table_file, 'w', encoding='utf-8') as f:
            f.write(create_table_sql)
        
        # Write IMPORT DATA SQL
        with open(import_data_file, 'w', encoding='utf-8') as f:
            f.write(import_sql)
        
        print(f"Generated {db_type.upper()} CREATE TABLE SQL: {create_table_file}")
        print(f"Generated {db_type.upper()} IMPORT DATA SQL: {import_data_file}")
        
        # Create post-import SQL directory structure
        post_import_dir = os.path.join(output_dir, 'post_import_sql')
        os.makedirs(post_import_dir, exist_ok=True)
        
        # Create subdirectory for this specific table structure
        table_hash_dir = os.path.join(post_import_dir, f"{filename_base}_{column_md5_hash}")
        os.makedirs(table_hash_dir, exist_ok=True)
        
        # Create a README file explaining the post-import SQL structure
        readme_path = os.path.join(table_hash_dir, 'README.md')
        if not os.path.exists(readme_path):
            readme_content = PostImportSQLGenerator.load_readme_template(db_type, filename_base)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
        
        print(f"Created post-import SQL directory: {table_hash_dir}")
        
        return {
            'create_table_sql': create_table_file,
            'import_data_sql': import_data_file,
            'post_import_dir': table_hash_dir
        }
    
    @staticmethod
    def _get_file_extension(db_type: str) -> str:
        """
        Get the file extension for a given database type.
        
        Args:
            db_type (str): Database type identifier
            
        Returns:
            str: File extension for the database type
        """
        extension_map = {
            'mysql': 'mysql',
            'postgresql': 'postgres'
        }
        return extension_map.get(db_type, db_type)
    
    @staticmethod
    def _get_or_create_table_sql(metadata: Dict[str, Any], cache_dir: str, 
                                column_md5_hash: str, overwrite_previous: bool, 
                                db_type: str, generator_class) -> str:
        """
        Get CREATE TABLE SQL from cache or generate new one.
        
        Args:
            metadata (Dict[str, Any]): CSV metadata
            cache_dir (str): Cache directory path
            column_md5_hash (str): MD5 hash of column structure
            overwrite_previous (bool): Whether to overwrite existing cache
            db_type (str): Database type identifier
            generator_class: The specific generator class with SQL generation methods
            
        Returns:
            str: CREATE TABLE SQL statement
        """
        # Determine file extension based on database type
        db_extension = BaseSchemaGenerator._get_file_extension(db_type)
        
        # Look for cached CREATE TABLE SQL
        cache_pattern = os.path.join(cache_dir, f"{column_md5_hash}.*.{db_extension}.sql")
        cache_files = glob.glob(cache_pattern)
        
        if cache_files and not overwrite_previous:
            # Use cached version
            cache_file = cache_files[0]
            print(f"Using cached {db_type.upper()} CREATE TABLE SQL: {os.path.basename(cache_file)}")
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Generate new CREATE TABLE SQL
        print(f"Generating new {db_type.upper()} CREATE TABLE SQL...")
        
        # Use database-specific method to generate CREATE TABLE SQL
        full_sql = generator_class._generate_create_table_sql(metadata)
        
        # Cache the generated SQL
        filename_base = metadata.get('filename_without_extension', 'unknown')
        cache_file = os.path.join(cache_dir, f"{column_md5_hash}.create_table.{filename_base}.{db_extension}.sql")
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(full_sql)
        
        print(f"Cached {db_type.upper()} CREATE TABLE SQL: {os.path.basename(cache_file)}")
        
        return full_sql
    
    @staticmethod
    def _get_or_create_import_sql(metadata: Dict[str, Any], output_dir: str, 
                                 column_md5_hash: str, overwrite_previous: bool, 
                                 db_type: str, generator_class) -> str:
        """
        Get IMPORT DATA SQL from cache or generate new one.
        
        Args:
            metadata (Dict[str, Any]): CSV metadata
            output_dir (str): Output directory path
            column_md5_hash (str): MD5 hash of column structure
            overwrite_previous (bool): Whether to overwrite existing cache
            db_type (str): Database type identifier
            generator_class: The specific generator class with SQL generation methods
            
        Returns:
            str: IMPORT DATA SQL statement
        """
        # Create cache directory for import data SQL
        cache_dir = os.path.join(output_dir, 'cache_import_data_sql')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Determine file extension based on database type
        db_extension = BaseSchemaGenerator._get_file_extension(db_type)
        
        # Look for cached IMPORT DATA SQL
        cache_pattern = os.path.join(cache_dir, f"{column_md5_hash}.*.{db_extension}.sql")
        cache_files = glob.glob(cache_pattern)
        
        if cache_files and not overwrite_previous:
            # Use cached version
            cache_file = cache_files[0]
            print(f"Using cached {db_type.upper()} IMPORT DATA SQL: {os.path.basename(cache_file)}")
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Generate new IMPORT DATA SQL
        print(f"Generating new {db_type.upper()} IMPORT DATA SQL...")
        
        # Use database-specific method to generate IMPORT DATA SQL
        import_sql = generator_class._generate_import_sql(metadata)
        
        # Cache the generated SQL
        filename_base = metadata.get('filename_without_extension', 'unknown')
        cache_file = os.path.join(cache_dir, f"{column_md5_hash}.import_data.{filename_base}.{db_extension}.sql")
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(import_sql)
        
        print(f"Cached {db_type.upper()} IMPORT DATA SQL: {os.path.basename(cache_file)}")
        
        return import_sql
