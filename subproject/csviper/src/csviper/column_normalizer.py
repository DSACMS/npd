"""
Column Name Normalization utilities for CSViper
"""

import re
from typing import List, Dict


class ColumnNormalizer:
    """
    Utility class for normalizing CSV column names to SQL-safe identifiers.
    """
    
    @staticmethod
    def rename_column_list(column_names: List[str]) -> List[str]:
        """
        Convert a list of column names to SQL-safe column names.
        Handles duplicate normalized names by adding numbered suffixes.
        
        Args:
            column_names (List[str]): List of original column names
            
        Returns:
            List[str]: List of normalized column names in the same order
        """
        result = []
        used_normalized_names = set()
        
        for original_name in column_names:
            # Get the base normalized name
            base_normalized = ColumnNormalizer.safe_column_renamer(original_name)
            
            # Check if this normalized name already exists
            if base_normalized in used_normalized_names:
                # Find the next available numbered version
                counter = 2
                while True:
                    suffix = f"_{counter:03d}"
                    if len(base_normalized) + len(suffix) > 60:
                        # Truncate the base name to make room for the suffix
                        truncated_base = base_normalized[:60 - len(suffix)]
                        final_normalized = f"{truncated_base}{suffix}"
                    else:
                        final_normalized = f"{base_normalized}{suffix}"
                    
                    if final_normalized not in used_normalized_names:
                        break
                    counter += 1
            else:
                # First occurrence of this normalized name - keep it as is
                final_normalized = base_normalized
            
            result.append(final_normalized)
            used_normalized_names.add(final_normalized)
        
        return result
    
    @staticmethod
    def safe_column_renamer(column_name: str) -> str:
        """
        Convert a string to a SQL-safe column name:
        - Replace all special characters (including spaces) with underscores
        - Prefix with underscore if the first character is a digit
        - Truncate to 60 characters
        
        Args:
            column_name (str): The original column name
            
        Returns:
            str: SQL-safe column name
        """
        if not column_name:
            return "_empty_column"
        
        # Replace all special characters and spaces with underscores
        normalized = re.sub(r'[^a-zA-Z0-9]', '_', column_name)
        
        # Remove consecutive underscores
        normalized = re.sub(r'_+', '_', normalized)
        
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        
        # If empty after cleaning, provide a default
        if not normalized:
            normalized = "unnamed_column"
        
        # Prefix with underscore if the first character is a digit
        if normalized and normalized[0].isdigit():
            normalized = '_' + normalized
        
        # Truncate to 60 characters and convert to lowercase
        return normalized[:60].lower()
