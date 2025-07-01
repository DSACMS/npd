"""
PostgreSQL Schema Generator for CSViper
"""

from typing import Dict, Any
from .base_schema_generator import BaseSchemaGenerator


class PostgreSQLSchemaGenerator(BaseSchemaGenerator):
    """
    Generates PostgreSQL-specific SQL scripts from CSV metadata.
    """
    
    @staticmethod
    def fromMetadataToSQL(metadata_json_path: str, output_dir: str, overwrite_previous: bool = False) -> Dict[str, str]:
        """
        Generate PostgreSQL SQL scripts from metadata JSON file.
        
        Args:
            metadata_json_path (str): Path to the metadata JSON file
            output_dir (str): Output directory for SQL files
            overwrite_previous (bool): Whether to overwrite existing files
            
        Returns:
            Dict[str, str]: Dictionary with paths to generated SQL files
            
        Raises:
            FileNotFoundError: If metadata JSON file does not exist
            ValueError: If metadata JSON is invalid
        """
        return BaseSchemaGenerator.fromMetadataToSQL(
            metadata_json_path, output_dir, overwrite_previous, 'postgresql', PostgreSQLSchemaGenerator
        )
    
    @staticmethod
    def _generate_create_table_sql(metadata: Dict[str, Any]) -> str:
        """
        Generate PostgreSQL-specific CREATE TABLE SQL statement.
        
        Args:
            metadata (Dict[str, Any]): CSV metadata
            
        Returns:
            str: PostgreSQL CREATE TABLE SQL statement
        """
        sql_parts = []
        
        # Note: CREATE DATABASE is not included here as it cannot run inside a transaction
        # The database should already exist when connecting
        
        # DROP TABLE statement
        sql_parts.append("DROP TABLE IF EXISTS REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME;")
        sql_parts.append("")
        
        # CREATE TABLE statement
        create_table_sql = "CREATE TABLE REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME (\n"
        
        column_definitions = []
        for col_name in metadata['normalized_column_names']:
            # Find the original column name that maps to this normalized name
            original_col = None
            for orig, norm in metadata['column_name_mapping'].items():
                if norm == col_name:
                    original_col = orig
                    break
            
            if original_col is None:
                raise ValueError(f"Could not find original column name for normalized column '{col_name}'")
            
            # Look up max length using the original column name
            if original_col not in metadata['max_column_lengths']:
                raise ValueError(f"Column '{original_col}' not found in max_column_lengths")
            
            # Add 1 to max length to ensure there's room for the data
            varchar_length = metadata['max_column_lengths'][original_col] + 1
            column_definitions.append(f"    \"{col_name}\" VARCHAR({varchar_length})")
        
        create_table_sql += ",\n".join(column_definitions)
        create_table_sql += "\n);"
        
        sql_parts.append(create_table_sql)
        
        return "\n".join(sql_parts)
    
    @staticmethod
    def _generate_import_sql(metadata: Dict[str, Any]) -> str:
        """
        Generate PostgreSQL COPY SQL statement.
        
        Args:
            metadata (Dict[str, Any]): CSV metadata
            
        Returns:
            str: COPY SQL statement
        """
        delimiter = metadata.get('delimiter', ',')
        quote_char = metadata.get('quote_character', '"')
        
        # Build COPY statement
        sql_parts = []
        
        sql_parts.append("\\COPY REPLACE_ME_DB_NAME.REPLACE_ME_TABLE_NAME FROM 'REPLACE_ME_CSV_FULL_PATH'")
        sql_parts.append("WITH (")
        sql_parts.append("    FORMAT csv,")
        sql_parts.append("    HEADER true,")
        sql_parts.append(f"    DELIMITER '{delimiter}',")
        sql_parts.append(f"    QUOTE '{quote_char}',")
        sql_parts.append("    NULL '',")
        sql_parts.append("    ENCODING 'UTF8'")
        sql_parts.append(");")
        
        return "\n".join(sql_parts)
