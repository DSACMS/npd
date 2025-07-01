"""
CSV Import Executor - Shared functionality for database imports

This module contains the common functionality used by generated import scripts
for both MySQL and PostgreSQL databases.
"""

import os
import sys
import json
import csv
import click
from dotenv import load_dotenv


class Colors:
    """ANSI color codes for terminal output"""
    DARK_RED = '\033[31m'
    RESET = '\033[0m'
    
    @staticmethod
    def dark_red(text):
        """Format text in dark red color"""
        return f"{Colors.DARK_RED}{text}{Colors.RESET}"


class ImportExecutor:
    """
    Shared functionality for CSV database import operations.
    
    This class provides static methods that are common between MySQL and PostgreSQL
    import scripts, reducing code duplication and centralizing import logic.
    """
    
    @staticmethod
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
            other_db_type = 'postgresql' if db_type == 'mysql' else 'mysql'
            for root, dirs, files in os.walk(post_import_dir):
                for filename in files:
                    if filename.endswith('.sql') and not filename.endswith(f'.{other_db_type}.sql'):
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

    @staticmethod
    def execute_post_import_sql(connection, post_import_files, db_schema_name, table_name, use_colors=True):
        """
        Execute post-import SQL files in order.
        
        Args:
            connection: Database connection
            post_import_files (List[Tuple[int, str]]): List of (order, filepath) tuples
            db_schema_name (str): Database schema name
            table_name (str): Table name
            use_colors (bool): Whether to use colored output for errors
        """
        if not post_import_files:
            click.echo("No post-import SQL files found")
            return
        
        click.echo(f"Executing {len(post_import_files)} post-import SQL files...")
        
        with connection.cursor() as cursor:
            for order, filepath in post_import_files:
                filename = os.path.basename(filepath)
                click.echo(f"Executing post-import SQL: {filename}")
                
                # Read SQL file
                with open(filepath, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Replace placeholders
                sql_content = sql_content.replace('REPLACE_ME_DATABASE_NAME', db_schema_name) \
                                       .replace('REPLACE_ME_TABLE_NAME', table_name)
                
                # Split into individual statements and execute
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                for statement in statements:
                    if statement and not statement.startswith('--'):
                        try:
                            click.echo(f"  Executing: {statement}")
                            cursor.execute(statement)
                            connection.commit()
                        except Exception as e:
                            error_msg = f"Warning: Error executing statement in {filename}: {e}"
                            statement_msg = f"  Failed statement: {statement}"
                            if use_colors:
                                click.echo(Colors.dark_red(error_msg))
                                click.echo(Colors.dark_red(statement_msg))
                            else:
                                click.echo(error_msg)
                                click.echo(statement_msg)
                            # Continue with next statement
                            continue
        
        click.echo("✓ Post-import SQL execution completed")

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def validate_csv_header(csv_file, expected_columns, encoding='utf-8', use_colors=True):
        """
        Validate that CSV header matches expected columns from metadata.
        
        Args:
            csv_file (str): Path to CSV file
            expected_columns (list): Expected column names from metadata
            encoding (str): File encoding to use for reading CSV
            use_colors (bool): Whether to use colored output for errors
            
        Raises:
            ValueError: If headers don't match
        """
        with open(csv_file, 'r', newline='', encoding=encoding) as f:
            reader = csv.reader(f)
            actual_header = next(reader)
        
        if len(actual_header) != len(expected_columns):
            error_msg = f"Column count mismatch: Expected {len(expected_columns)}, got {len(actual_header)}"
            if use_colors:
                raise ValueError(Colors.dark_red(error_msg))
            else:
                raise ValueError(error_msg)
        
        for i, (expected, actual) in enumerate(zip(expected_columns, actual_header)):
            if expected != actual:
                error_msg = f"Column {i+1} mismatch: Expected '{expected}', got '{actual}'"
                if use_colors:
                    raise ValueError(Colors.dark_red(error_msg))
                else:
                    raise ValueError(error_msg)

    @staticmethod
    def load_sql_file(filename, script_dir=None, use_colors=True):
        """
        Load SQL content from file.
        
        Args:
            filename (str): SQL filename
            script_dir (str): Directory containing the SQL file (defaults to caller's directory)
            use_colors (bool): Whether to use colored output for errors
            
        Returns:
            str: SQL content
        """
        if script_dir is None:
            # Get the directory of the calling script by walking up the stack
            # to find the first frame that's not in the csviper package
            import inspect
            frame = inspect.currentframe()
            try:
                while frame:
                    frame = frame.f_back
                    if frame and '__file__' in frame.f_globals:
                        file_path = frame.f_globals['__file__']
                        # Skip frames from the csviper package itself
                        if 'csviper' not in file_path or file_path.endswith(('go.mysql.py', 'go.postgresql.py')):
                            script_dir = os.path.dirname(os.path.abspath(file_path))
                            break
            finally:
                del frame
        
        sql_path = os.path.join(script_dir, filename)
        
        if not os.path.exists(sql_path):
            error_msg = f"SQL file not found: {sql_path}"
            if use_colors:
                raise FileNotFoundError(Colors.dark_red(error_msg))
            else:
                raise FileNotFoundError(error_msg)
        
        with open(sql_path, 'r') as f:
            return f.read()

    @staticmethod
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
        return sql_content.replace('REPLACE_ME_DB_NAME', db_name) \
                         .replace('REPLACE_ME_TABLE_NAME', table_name) \
                         .replace('REPLACE_ME_CSV_FULL_PATH', csv_path)

    @staticmethod
    def load_and_validate_config(env_file_location, csv_file, db_schema_name, table_name, metadata_filename, use_colors=True):
        """
        Load environment configuration and validate inputs.
        
        Args:
            env_file_location (str): Path to .env file (optional)
            csv_file (str): Path to CSV file
            db_schema_name (str): Database schema name (optional)
            table_name (str): Table name (optional)
            metadata_filename (str): Name of metadata JSON file
            use_colors (bool): Whether to use colored output for errors
            
        Returns:
            tuple: (db_config, db_schema_name, table_name, metadata, encoding)
        """
        # Expand user path (handle ~ symbol)
        csv_file = os.path.expanduser(csv_file)
        
        # Validate CSV file exists
        if not os.path.exists(csv_file):
            error_msg = f"CSV file not found: {csv_file}"
            if use_colors:
                raise FileNotFoundError(Colors.dark_red(error_msg))
            else:
                raise FileNotFoundError(error_msg)
        
        # Find .env file
        if env_file_location:
            env_file_location = os.path.expanduser(env_file_location)
            if not os.path.exists(env_file_location):
                error_msg = f".env file not found: {env_file_location}"
                if use_colors:
                    raise FileNotFoundError(Colors.dark_red(error_msg))
                else:
                    raise FileNotFoundError(error_msg)
            env_file = env_file_location
        else:
            env_file = ImportExecutor.find_env_file()
            if not env_file:
                error_msg = "No .env file found. Specify --env_file_location or place .env in current/parent directory"
                if use_colors:
                    raise FileNotFoundError(Colors.dark_red(error_msg))
                else:
                    raise FileNotFoundError(error_msg)
        
        # Check .gitignore
        ImportExecutor.check_gitignore_for_env()
        
        # Load environment variables
        load_dotenv(env_file)
        
        # Get database configuration
        required_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        optional_vars = ['DB_SCHEMA', 'DB_TABLE', 'DEBUG', 'SECRET_KEY']
        db_config = {}
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                error_msg = f"Required environment variable not found: {var}"
                if use_colors:
                    raise ValueError(Colors.dark_red(error_msg))
                else:
                    raise ValueError(error_msg)
            db_config[var] = value
        
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                db_config[var] = value
        
        # Load metadata to validate CSV header
        # Get the directory of the calling script by walking up the stack
        # to find the first frame that's not in the csviper package
        import inspect
        frame = inspect.currentframe()
        script_dir = None
        try:
            while frame:
                frame = frame.f_back
                if frame and '__file__' in frame.f_globals:
                    file_path = frame.f_globals['__file__']
                    # Skip frames from the csviper package itself
                    if 'csviper' not in file_path or file_path.endswith(('go.mysql.py', 'go.postgresql.py')):
                        script_dir = os.path.dirname(os.path.abspath(file_path))
                        break
        finally:
            del frame
        
        metadata_file = os.path.join(script_dir, metadata_filename)
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Determine schema and table names
        if not db_schema_name:
            db_schema_name = db_config.get('DB_SCHEMA')
            if not db_schema_name:
                error_msg = "Database schema name must be provided via --db_schema_name or DB_SCHEMA environment variable"
                if use_colors:
                    raise ValueError(Colors.dark_red(error_msg))
                else:
                    raise ValueError(error_msg)
        
        if not table_name:
            table_name = db_config.get('DB_TABLE')
            if not table_name:
                error_msg = "Table name must be provided via --table_name or DB_TABLE environment variable"
                if use_colors:
                    raise ValueError(Colors.dark_red(error_msg))
                else:
                    raise ValueError(error_msg)
        
        # Get encoding from metadata, with fallback to utf-8
        encoding = metadata.get('encoding', 'utf-8')
        
        # Log encoding information
        if 'encoding' in metadata:
            click.echo(f"Using encoding from metadata: {encoding}")
            if 'encoding_notes' in metadata:
                click.echo(f"Encoding notes: {metadata['encoding_notes']}")
        else:
            click.echo(f"No encoding in metadata, using default: {encoding}")
        
        return db_config, db_schema_name, table_name, metadata, encoding

    @staticmethod
    def execute_postgresql_import(db_config, db_schema_name, table_name, csv_file, trample, create_table_sql_file, encoding='utf-8'):
        """
        Execute PostgreSQL import process.
        
        Args:
            db_config (dict): Database configuration
            db_schema_name (str): Database schema name
            table_name (str): Table name
            csv_file (str): Path to CSV file
            trample (bool): Whether to overwrite existing data
            create_table_sql_file (str): Name of the CREATE TABLE SQL file
            encoding (str): File encoding to use for reading CSV
        """
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError as e:
            from .exceptions import ImportExecutionError
            raise ImportExecutionError(
                "psycopg2 library is required for PostgreSQL imports. Install with: pip install psycopg2-binary",
                script_type="PostgreSQL",
                original_error=e
            )
        
        # Load SQL files
        create_table_sql = ImportExecutor.load_sql_file(create_table_sql_file)
        
        # Replace placeholders
        csv_full_path = os.path.abspath(csv_file)
        create_table_sql = ImportExecutor.replace_sql_placeholders(create_table_sql, db_schema_name, table_name, csv_full_path)
        
        # Connect to database
        try:
            connection = psycopg2.connect(
                host=db_config['DB_HOST'],
                port=int(db_config['DB_PORT']),
                user=db_config['DB_USER'],
                password=db_config['DB_PASSWORD'],
                database=db_config['DB_NAME']
            )
        except psycopg2.Error as e:
            from .exceptions import DatabaseConnectionError
            connection_details = {
                'host': db_config['DB_HOST'],
                'port': db_config['DB_PORT'],
                'user': db_config['DB_USER'],
                'database': db_config['DB_NAME']
            }
            raise DatabaseConnectionError(
                f"Failed to connect to PostgreSQL database: {str(e)}",
                db_type="PostgreSQL",
                connection_details=connection_details
            )
        except Exception as e:
            from .exceptions import DatabaseConnectionError
            raise DatabaseConnectionError(
                f"Unexpected error connecting to PostgreSQL database: {str(e)}",
                db_type="PostgreSQL"
            )
        
        try:
            with connection.cursor() as cursor:
                # Create schema if it doesn't exist
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {db_schema_name}")
                
                # Execute CREATE TABLE statements
                statements = [stmt.strip() for stmt in create_table_sql.split(';') if stmt.strip()]
                for statement in statements:
                    if statement:
                        click.echo(f"Executing: {statement}...")
                        cursor.execute(statement)
                
                # Import data using COPY FROM STDIN with progress bar
                click.echo("Importing data...")
                
                # Get file size for progress tracking
                file_size = os.path.getsize(csv_file)
                
                # Build the COPY command
                copy_sql = f"COPY {db_schema_name}.{table_name} FROM STDIN WITH CSV HEADER"
                
                # Create a progress bar wrapper for the file
                class ProgressFileWrapper:
                    def __init__(self, file_obj, file_size):
                        self.file_obj = file_obj
                        self.file_size = file_size
                        self.bytes_read = 0
                        self.progress_bar = click.progressbar(length=file_size, 
                                                            label='Uploading CSV data',
                                                            show_percent=True,
                                                            show_eta=True)
                        self.progress_bar.__enter__()
                    
                    def read(self, size=-1):
                        data = self.file_obj.read(size)
                        if data:
                            self.bytes_read += len(data)
                            self.progress_bar.update(len(data))
                        return data
                    
                    def readline(self):
                        line = self.file_obj.readline()
                        if line:
                            self.bytes_read += len(line)
                            self.progress_bar.update(len(line))
                        return line
                    
                    def __getattr__(self, name):
                        return getattr(self.file_obj, name)
                    
                    def close(self):
                        self.progress_bar.__exit__(None, None, None)
                        self.file_obj.close()
                
                with open(csv_file, 'r', encoding=encoding) as f:
                    progress_wrapper = ProgressFileWrapper(f, file_size)
                    try:
                        cursor.copy_expert(copy_sql, progress_wrapper)
                    finally:
                        progress_wrapper.close()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {db_schema_name}.{table_name}")
                row_count = cursor.fetchone()[0]
                click.echo(f"✓ Successfully imported {row_count:,} rows")
            
            connection.commit()
            
            # Execute post-import SQL files
            # Get the directory of the calling script by walking up the stack
            # to find the first frame that's not in the csviper package
            import inspect
            frame = inspect.currentframe()
            script_dir = None
            try:
                while frame:
                    frame = frame.f_back
                    if frame and '__file__' in frame.f_globals:
                        file_path = frame.f_globals['__file__']
                        # Skip frames from the csviper package itself
                        if 'csviper' not in file_path or file_path.endswith(('go.mysql.py', 'go.postgresql.py')):
                            script_dir = os.path.dirname(os.path.abspath(file_path))
                            break
            finally:
                del frame
            
            post_import_files = ImportExecutor.find_post_import_sql_files(script_dir, 'postgresql')
            ImportExecutor.execute_post_import_sql(connection, post_import_files, db_schema_name, table_name)
            
        finally:
            connection.close()

    @staticmethod
    def execute_mysql_import(db_config, db_schema_name, table_name, csv_file, trample, create_table_sql_file, import_data_sql_file):
        """
        Execute MySQL import process.
        
        Args:
            db_config (dict): Database configuration
            db_schema_name (str): Database schema name
            table_name (str): Table name
            csv_file (str): Path to CSV file
            trample (bool): Whether to overwrite existing data
            create_table_sql_file (str): Name of the CREATE TABLE SQL file
            import_data_sql_file (str): Name of the LOAD DATA SQL file
        """
        try:
            import pymysql
        except ImportError as e:
            from .exceptions import ImportExecutionError
            raise ImportExecutionError(
                "pymysql library is required for MySQL imports. Install with: pip install pymysql",
                script_type="MySQL",
                original_error=e
            )
        
        # Load SQL files
        create_table_sql = ImportExecutor.load_sql_file(create_table_sql_file)
        import_data_sql = ImportExecutor.load_sql_file(import_data_sql_file)
        
        # Replace placeholders
        csv_full_path = os.path.abspath(csv_file)
        create_table_sql = ImportExecutor.replace_sql_placeholders(create_table_sql, db_schema_name, table_name, csv_full_path)
        import_data_sql = ImportExecutor.replace_sql_placeholders(import_data_sql, db_schema_name, table_name, csv_full_path)
        
        # Connect to database
        try:
            connection = pymysql.connect(
                host=db_config['DB_HOST'],
                port=int(db_config['DB_PORT']),
                user=db_config['DB_USER'],
                password=db_config['DB_PASSWORD'],
                database=db_config['DB_NAME'],
                local_infile=True
            )
        except pymysql.Error as e:
            from .exceptions import DatabaseConnectionError
            connection_details = {
                'host': db_config['DB_HOST'],
                'port': db_config['DB_PORT'],
                'user': db_config['DB_USER'],
                'database': db_config['DB_NAME']
            }
            raise DatabaseConnectionError(
                f"Failed to connect to MySQL database: {str(e)}",
                db_type="MySQL",
                connection_details=connection_details
            )
        except Exception as e:
            from .exceptions import DatabaseConnectionError
            raise DatabaseConnectionError(
                f"Unexpected error connecting to MySQL database: {str(e)}",
                db_type="MySQL"
            )
        
        try:
            with connection.cursor() as cursor:
                # Execute CREATE TABLE statements
                statements = [stmt.strip() for stmt in create_table_sql.split(';') if stmt.strip()]
                for statement in statements:
                    if statement:
                        click.echo(f"Executing: {statement}...")
                        cursor.execute(statement)
                
                # Execute LOAD DATA statement
                click.echo("Importing data...")
                cursor.execute(import_data_sql)
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {db_schema_name}.{table_name}")
                row_count = cursor.fetchone()[0]
                click.echo(f"✓ Successfully imported {row_count:,} rows")
            
            connection.commit()
            
            # Execute post-import SQL files
            # Get the directory of the calling script by walking up the stack
            # to find the first frame that's not in the csviper package
            import inspect
            frame = inspect.currentframe()
            script_dir = None
            try:
                while frame:
                    frame = frame.f_back
                    if frame and '__file__' in frame.f_globals:
                        file_path = frame.f_globals['__file__']
                        # Skip frames from the csviper package itself
                        if 'csviper' not in file_path or file_path.endswith(('go.mysql.py', 'go.postgresql.py')):
                            script_dir = os.path.dirname(os.path.abspath(file_path))
                            break
            finally:
                del frame
            
            post_import_files = ImportExecutor.find_post_import_sql_files(script_dir, 'mysql')
            ImportExecutor.execute_post_import_sql(connection, post_import_files, db_schema_name, table_name, use_colors=False)
            
        finally:
            connection.close()
