"""
Base Import Script Generator for CSViper
Contains shared functionality between database-specific import script generators.
"""

import os
import json
from datetime import datetime


class BaseImportScriptGenerator:
    """
    Base class for database-specific import script generators.
    Contains shared functionality for generating standalone Python import scripts.
    """
    
    @staticmethod
    def fromResourceDirToScript(resource_dir, output_dir=None, overwrite_previous=False, 
                               db_type=None, generator_class=None):
        """
        Generate a database-specific import script from resource directory.
        
        Args:
            resource_dir (str): Directory containing metadata.json and SQL files
            output_dir (str): Output directory for script (defaults to resource_dir)
            overwrite_previous (bool): Whether to overwrite existing script file
            db_type (str): Database type identifier ('mysql' or 'postgresql')
            generator_class: The specific generator class with database-specific methods
            
        Returns:
            str: Path to the generated script file
            
        Raises:
            FileNotFoundError: If required files are not found
            ValueError: If metadata is invalid
        """
        resource_dir = os.path.abspath(resource_dir)
        
        if output_dir is None:
            output_dir = resource_dir
        else:
            output_dir = os.path.abspath(output_dir)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Find metadata file
        metadata_file = BaseImportScriptGenerator._find_metadata_file(resource_dir)
        if not metadata_file:
            raise FileNotFoundError(f"No metadata JSON file found in {resource_dir}")
        
        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Validate required SQL files exist
        generator_class._validate_sql_files(resource_dir, metadata)
        
        # Generate script
        script_filename = f'go.{db_type}.py'
        go_script_path = os.path.join(output_dir, script_filename)
        
        if os.path.exists(go_script_path) and not overwrite_previous:
            raise FileExistsError(f"{script_filename} already exists: {go_script_path}. Use overwrite_previous=True to overwrite.")
        
        script_content = generator_class._generate_script_content(metadata)
        
        with open(go_script_path, 'w') as f:
            f.write(script_content)
        
        # Make the script executable
        os.chmod(go_script_path, 0o755)
        
        return go_script_path
    
    @staticmethod
    def _find_metadata_file(resource_dir):
        """Find the metadata JSON file in the resource directory."""
        for filename in os.listdir(resource_dir):
            if filename.endswith('.metadata.json'):
                return os.path.join(resource_dir, filename)
        return None
    
    @staticmethod
    def _get_timestamp():
        """Get current timestamp for script generation."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def _generate_shared_functions():
        """Generate shared Python functions used by all database import scripts."""
        return '''
def find_post_import_sql_files(script_dir, db_type):
    """
    Find and return post-import SQL files in execution order.
    
    Args:
        script_dir (str): Directory containing the script
        db_type (str): Database type ('mysql' or 'postgresql')
        
    Returns:
        List[Tuple[int, str]]: List of (order, filepath) tuples sorted by order
    """
    import glob
    
    post_import_dir = os.path.join(script_dir, 'post_import_sql')
    if not os.path.exists(post_import_dir):
        return []
    
    files_with_order = []
    
    # Look for SQL files in subdirectories
    for root, dirs, files in os.walk(post_import_dir):
        for filename in files:
            # First, look for database-specific files
            if filename.endswith(f'.{db_type}.sql'):
                # Extract numeric prefix
                try:
                    order_str = filename.split('_')[0]
                    order = int(order_str)
                    filepath = os.path.join(root, filename)
                    files_with_order.append((order, filepath))
                except (ValueError, IndexError):
                    # Skip files that don't follow the naming convention
                    continue
    
    # If no database-specific files found, look for generic .sql files
    if not files_with_order:
        other_db_extension = 'postgresql' if db_type == 'mysql' else 'mysql'
        for root, dirs, files in os.walk(post_import_dir):
            for filename in files:
                if filename.endswith('.sql') and not filename.endswith(f'.{other_db_extension}.sql'):
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


def find_env_file():
    """
    Find .env file in current directory or parent directory.
    
    Returns:
        str: Path to .env file or None if not found
    """
    # Check current directory
    current_dir_env = os.path.join(os.getcwd(), '.env')
    if os.path.exists(current_dir_env):
        return current_dir_env
    
    # Check parent directory
    parent_dir_env = os.path.join(os.path.dirname(os.getcwd()), '.env')
    if os.path.exists(parent_dir_env):
        return parent_dir_env
    
    return None


def check_gitignore_for_env():
    """
    Check if .env is excluded in local .gitignore file.
    Warns if .env is not properly excluded.
    """
    gitignore_path = os.path.join(os.getcwd(), '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
            if '.env' not in gitignore_content:
                click.echo("Warning: .env file should be added to .gitignore to avoid committing credentials")
    else:
        click.echo("Warning: No .gitignore file found. Consider creating one and adding .env to it")


def validate_csv_header(csv_file, expected_columns):
    """
    Validate that CSV header matches expected columns from metadata.
    
    Args:
        csv_file (str): Path to CSV file
        expected_columns (list): Expected column names from metadata
        
    Raises:
        ValueError: If headers don't match
    """
    with open(csv_file, 'r', newline='') as f:
        reader = csv.reader(f)
        actual_header = next(reader)
    
    if len(actual_header) != len(expected_columns):
        raise ValueError(f"Column count mismatch: Expected {len(expected_columns)}, got {len(actual_header)}")
    
    for i, (expected, actual) in enumerate(zip(expected_columns, actual_header)):
        if expected != actual:
            raise ValueError(f"Column {i+1} mismatch: Expected '{expected}', got '{actual}'")


def load_sql_file(filename):
    """
    Load SQL content from file.
    
    Args:
        filename (str): SQL filename
        
    Returns:
        str: SQL content
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, filename)
    
    if not os.path.exists(sql_path):
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    
    with open(sql_path, 'r') as f:
        return f.read()


def replace_sql_placeholders(sql_content, db_name, table_name, csv_path):
    """
    Replace placeholders in SQL content with actual values.
    
    Args:
        sql_content (str): SQL content with placeholders
        db_name (str): Database/schema name
        table_name (str): Table name
        csv_path (str): Full path to CSV file
        
    Returns:
        str: SQL content with placeholders replaced
    """
    return sql_content.replace('REPLACE_ME_DB_NAME', db_name) \\
                     .replace('REPLACE_ME_TABLE_NAME', table_name) \\
                     .replace('REPLACE_ME_CSV_FULL_PATH', csv_path)
'''
