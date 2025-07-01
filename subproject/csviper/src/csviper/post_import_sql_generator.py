#!/usr/bin/env python3
"""
Post-Import SQL Generator for CSViper

Generates post-import SQL files for data calculations, indexing, and transformations
that occur after the initial CSV data import.
"""

import os
import json
import hashlib
import glob
from typing import Dict, Any, List, Tuple


class PostImportSQLGenerator:
    """
    Base class for generating post-import SQL files.
    Handles the common logic for creating numerically ordered SQL files
    with REPLACE_ME_DATABASE_NAME and REPLACE_ME_TABLE_NAME templating.
    """
    
    @staticmethod
    def fromMetadataToPostImportSQL(metadata_json_path: str, output_dir: str, 
                                   database_type: str, overwrite_previous: bool = False) -> Dict[str, Any]:
        """
        Generate post-import SQL files from metadata JSON file.
        
        Args:
            metadata_json_path (str): Path to the metadata JSON file
            output_dir (str): Output directory for SQL files
            database_type (str): Database type ('mysql' or 'postgresql')
            overwrite_previous (bool): Whether to overwrite existing files
            
        Returns:
            Dict[str, Any]: Dictionary with information about generated SQL files
            
        Raises:
            FileNotFoundError: If metadata JSON file does not exist
            ValueError: If metadata JSON is invalid or database_type is unsupported
        """
        # Validate database type
        if database_type not in ['mysql', 'postgresql']:
            raise ValueError(f"Unsupported database type: {database_type}")
        
        # Validate metadata file
        if not os.path.isfile(metadata_json_path):
            raise FileNotFoundError(f"Metadata JSON file not found: {metadata_json_path}")
        
        # Load metadata
        with open(metadata_json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Validate required metadata fields
        required_fields = ['filename_without_extension', 'normalized_column_names']
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Required metadata field missing: {field}")
        
        print(f"Generating {database_type.upper()} post-import SQL for: {metadata['filename_without_extension']}")
        
        # Create post-import SQL directory
        post_import_dir = os.path.join(output_dir, 'post_import_sql')
        os.makedirs(post_import_dir, exist_ok=True)
        
        # Generate MD5 hash for column structure caching
        column_names_str = ','.join([col.lower() for col in metadata['normalized_column_names']])
        column_md5_hash = hashlib.md5(column_names_str.encode()).hexdigest()
        
        # Generate post-import SQL files
        post_import_files = PostImportSQLGenerator._get_or_create_post_import_sql(
            metadata, post_import_dir, column_md5_hash, database_type, overwrite_previous
        )
        
        print(f"Generated {len(post_import_files)} post-import SQL files")
        
        return {
            'post_import_dir': post_import_dir,
            'post_import_files': post_import_files,
            'database_type': database_type
        }
    
    @staticmethod
    def _get_or_create_post_import_sql(metadata: Dict[str, Any], post_import_dir: str,
                                      column_md5_hash: str, database_type: str, 
                                      overwrite_previous: bool) -> List[str]:
        """
        Get post-import SQL files from cache or generate new ones.
        
        Args:
            metadata (Dict[str, Any]): CSV metadata
            post_import_dir (str): Post-import SQL directory path
            column_md5_hash (str): MD5 hash of column structure
            database_type (str): Database type ('mysql' or 'postgresql')
            overwrite_previous (bool): Whether to overwrite existing cache
            
        Returns:
            List[str]: List of generated post-import SQL file paths
        """
        # Create subdirectory for this specific table structure
        table_hash_dir = os.path.join(post_import_dir, f"{metadata['filename_without_extension']}_{column_md5_hash}")
        os.makedirs(table_hash_dir, exist_ok=True)
        
        # Look for existing post-import SQL files
        existing_files = glob.glob(os.path.join(table_hash_dir, f"*.{database_type}.sql"))
        
        if existing_files and not overwrite_previous:
            # Use existing files
            print(f"Using existing {database_type.upper()} post-import SQL files: {len(existing_files)} files")
            return sorted(existing_files)
        
        # Generate new post-import SQL files
        print(f"Generating new {database_type.upper()} post-import SQL files...")
        
        post_import_templates = PostImportSQLGenerator._get_post_import_templates(metadata, database_type)
        generated_files = []
        
        for template_info in post_import_templates:
            filename = f"{template_info['order']:02d}_{template_info['name']}.{database_type}.sql"
            filepath = os.path.join(table_hash_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template_info['sql'])
            
            generated_files.append(filepath)
            print(f"Generated: {filename}")
        
        return generated_files
    
    @staticmethod
    def _get_post_import_templates(metadata: Dict[str, Any], database_type: str) -> List[Dict[str, Any]]:
        """
        Get post-import SQL templates based on database type and metadata.
        
        Args:
            metadata (Dict[str, Any]): CSV metadata
            database_type (str): Database type ('mysql' or 'postgresql')
            
        Returns:
            List[Dict[str, Any]]: List of template dictionaries with 'order', 'name', and 'sql' keys
        """
        templates = []
        
        # Basic indexing template (runs first)
        if database_type == 'mysql':
            index_sql = PostImportSQLGenerator._generate_mysql_index_template(metadata)
        else:  # postgresql
            index_sql = PostImportSQLGenerator._generate_postgresql_index_template(metadata)
        
        templates.append({
            'order': 1,
            'name': 'create_indexes',
            'sql': index_sql
        })
        
        # Data validation template (runs after indexing)
        validation_sql = PostImportSQLGenerator._generate_validation_template(metadata, database_type)
        templates.append({
            'order': 5,
            'name': 'data_validation',
            'sql': validation_sql
        })
        
        # Statistics update template (runs last)
        if database_type == 'mysql':
            stats_sql = PostImportSQLGenerator._generate_mysql_stats_template(metadata)
        else:  # postgresql
            stats_sql = PostImportSQLGenerator._generate_postgresql_stats_template(metadata)
        
        templates.append({
            'order': 10,
            'name': 'update_statistics',
            'sql': stats_sql
        })
        
        return templates
    
    @staticmethod
    def _generate_mysql_index_template(metadata: Dict[str, Any]) -> str:
        """Generate MySQL index creation template."""
        sql_parts = []
        sql_parts.append("-- MySQL Post-Import: Create Indexes")
        sql_parts.append("-- Generated by CSViper")
        sql_parts.append("")
        
        # Create indexes on columns that might be commonly queried
        # This is a basic template - users can customize as needed
        for i, col_name in enumerate(metadata['normalized_column_names'][:5]):  # First 5 columns
            index_name = f"idx_{col_name}"[:64]  # MySQL index name limit
            sql_parts.append(f"CREATE INDEX `{index_name}` ON REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME (`{col_name}`);")
        
        sql_parts.append("")
        sql_parts.append("-- Add custom indexes below as needed")
        sql_parts.append("-- Example: CREATE INDEX idx_custom ON REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME (column1, column2);")
        
        return "\n".join(sql_parts)
    
    @staticmethod
    def _generate_postgresql_index_template(metadata: Dict[str, Any]) -> str:
        """Generate PostgreSQL index creation template."""
        sql_parts = []
        sql_parts.append("-- PostgreSQL Post-Import: Create Indexes")
        sql_parts.append("-- Generated by CSViper")
        sql_parts.append("")
        
        # Create indexes on columns that might be commonly queried
        # This is a basic template - users can customize as needed
        for i, col_name in enumerate(metadata['normalized_column_names'][:5]):  # First 5 columns
            index_name = f"idx_{col_name}"[:63]  # PostgreSQL index name limit
            sql_parts.append(f'CREATE INDEX "{index_name}" ON REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME ("{col_name}");')
        
        sql_parts.append("")
        sql_parts.append("-- Add custom indexes below as needed")
        sql_parts.append('-- Example: CREATE INDEX idx_custom ON REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME (column1, column2);')
        
        return "\n".join(sql_parts)
    
    @staticmethod
    def _generate_validation_template(metadata: Dict[str, Any], database_type: str) -> str:
        """Generate data validation template."""
        sql_parts = []
        sql_parts.append(f"-- {database_type.upper()} Post-Import: Data Validation")
        sql_parts.append("-- Generated by CSViper")
        sql_parts.append("")
        
        # Basic row count validation
        sql_parts.append("-- Validate row count")
        sql_parts.append("SELECT COUNT(*) as total_rows FROM REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME;")
        sql_parts.append("")
        
        # Check for null values in each column
        sql_parts.append("-- Check for null values by column")
        for col_name in metadata['normalized_column_names']:
            if database_type == 'mysql':
                sql_parts.append(f"SELECT '{col_name}' as column_name, COUNT(*) as null_count FROM REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME WHERE `{col_name}` IS NULL OR `{col_name}` = '';")
            else:  # postgresql
                sql_parts.append(f"SELECT '{col_name}' as column_name, COUNT(*) as null_count FROM REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME WHERE \"{col_name}\" IS NULL OR \"{col_name}\" = '';")
        
        sql_parts.append("")
        sql_parts.append("-- Add custom validation queries below as needed")
        
        return "\n".join(sql_parts)
    
    @staticmethod
    def _generate_mysql_stats_template(metadata: Dict[str, Any]) -> str:
        """Generate MySQL statistics update template."""
        sql_parts = []
        sql_parts.append("-- MySQL Post-Import: Update Statistics")
        sql_parts.append("-- Generated by CSViper")
        sql_parts.append("")
        
        sql_parts.append("-- Analyze table to update statistics")
        sql_parts.append("ANALYZE TABLE REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME;")
        sql_parts.append("")
        
        sql_parts.append("-- Add custom statistics or maintenance queries below as needed")
        sql_parts.append("-- Example: OPTIMIZE TABLE REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME;")
        
        return "\n".join(sql_parts)
    
    @staticmethod
    def _generate_postgresql_stats_template(metadata: Dict[str, Any]) -> str:
        """Generate PostgreSQL statistics update template."""
        sql_parts = []
        sql_parts.append("-- PostgreSQL Post-Import: Update Statistics")
        sql_parts.append("-- Generated by CSViper")
        sql_parts.append("")
        
        sql_parts.append("-- Analyze table to update statistics")
        sql_parts.append("ANALYZE REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME;")
        sql_parts.append("")
        
        sql_parts.append("-- Add custom statistics or maintenance queries below as needed")
        sql_parts.append("-- Example: VACUUM ANALYZE REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME;")
        
        return "\n".join(sql_parts)
    
    @staticmethod
    def load_readme_template(database_type: str, filename_base: str) -> str:
        """
        Load and format the README template for the specified database type.
        
        Args:
            database_type (str): Database type ('mysql' or 'postgresql')
            filename_base (str): Base filename for template substitution
            
        Returns:
            str: Formatted README content
            
        Raises:
            FileNotFoundError: If template file is not found
        """
        # Get the directory where this module is located
        module_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(module_dir, 'templates')
        
        # Load the appropriate template file
        template_file = os.path.join(template_dir, f"{database_type}.post_import_sql.ReadMe.md")
        
        if not os.path.exists(template_file):
            raise FileNotFoundError(f"README template not found: {template_file}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Format the template with the filename_base
        return template_content.format(filename_base=filename_base)
    
    @staticmethod
    def get_ordered_post_import_files(post_import_dir: str, database_type: str) -> List[Tuple[int, str]]:
        """
        Get post-import SQL files ordered by their numeric prefix.
        
        Args:
            post_import_dir (str): Directory containing post-import SQL files
            database_type (str): Database type ('mysql' or 'postgresql')
            
        Returns:
            List[Tuple[int, str]]: List of (order, filepath) tuples sorted by order
        """
        if not os.path.exists(post_import_dir):
            return []
        
        files_with_order = []
        
        # Look for SQL files in subdirectories
        for root, dirs, files in os.walk(post_import_dir):
            for filename in files:
                if filename.endswith(f'.{database_type}.sql'):
                    # Extract numeric prefix
                    try:
                        order_str = filename.split('_')[0]
                        order = int(order_str)
                        filepath = os.path.join(root, filename)
                        files_with_order.append((order, filepath))
                    except (ValueError, IndexError):
                        # Skip files that don't follow the naming convention
                        continue
        
        # Sort by order
        files_with_order.sort(key=lambda x: x[0])
        
        return files_with_order
