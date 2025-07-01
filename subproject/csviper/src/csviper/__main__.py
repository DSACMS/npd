#!/usr/bin/env python3
"""
CSViper CLI - Main entry point
"""

import os
import sys
import click
from .metadata_extractor import CSVMetadataExtractor
from .exceptions import CSViperError


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    CSViper - CSV to SQL import tool
    
    Analyzes CSV files and generates SQL scripts and Python import programs
    for loading data into relational databases (MySQL and PostgreSQL).
    """
    pass


@cli.command()
@click.option('--from_csv', required=True, type=click.Path(exists=True), 
              help='Path to the CSV file to analyze')
@click.option('--output_dir', type=click.Path(), 
              help='Output directory (defaults to CSV filename without extension)')
@click.option('--overwrite_previous', is_flag=True, default=False,
              help='Overwrite existing output files')
def extract_metadata(from_csv, output_dir, overwrite_previous):
    """
    Extract metadata from a CSV file.
    
    Analyzes the CSV file structure, normalizes column names, and determines
    maximum column widths. Saves results to a metadata JSON file.
    """
    try:
        # Convert to absolute path
        csv_path = os.path.abspath(from_csv)
        
        # Determine output directory if not specified
        if not output_dir:
            csv_basename = os.path.basename(csv_path)
            output_dir = os.path.splitext(csv_basename)[0]
        
        output_dir = os.path.abspath(output_dir)
        
        
        click.echo(f"Extracting metadata from: {csv_path}")
        click.echo(f"Output directory: {output_dir}")
        
        # Extract metadata
        metadata = CSVMetadataExtractor.fromFileToMetadata(csv_path, output_dir, overwrite_previous)
        
        click.echo(f"✓ Successfully extracted metadata for {metadata['total_columns']} columns")
        click.echo(f"✓ File size: {metadata['file_size_bytes']:,} bytes")
        click.echo(f"✓ Delimiter: '{metadata['delimiter']}'")
        click.echo(f"✓ Quote character: '{metadata['quote_character']}'")
        
    except CSViperError as e:
        click.echo(f"{e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--from_metadata_json', required=True, type=click.Path(exists=True),
              help='Path to the metadata JSON file')
@click.option('--output_dir', type=click.Path(),
              help='Output directory (defaults to metadata file directory)')
@click.option('--overwrite_previous', is_flag=True, default=False,
              help='Overwrite existing output files')
def build_sql(from_metadata_json, output_dir, overwrite_previous):
    """
    Generate SQL scripts from metadata JSON file.
    
    Creates CREATE TABLE and data import SQL scripts for both MySQL and PostgreSQL
    based on the metadata extracted from a CSV file.
    """
    try:
        from .mysql_schema_generator import MySQLSchemaGenerator
        from .postgresql_schema_generator import PostgreSQLSchemaGenerator
        
        # Convert to absolute path
        metadata_path = os.path.abspath(from_metadata_json)
        
        # Determine output directory if not specified
        if not output_dir:
            output_dir = os.path.dirname(metadata_path)
        
        output_dir = os.path.abspath(output_dir)
        
        click.echo(f"Generating SQL scripts from: {metadata_path}")
        click.echo(f"Output directory: {output_dir}")
        
        # Generate MySQL SQL scripts
        click.echo("\n--- Generating MySQL SQL scripts ---")
        mysql_files = MySQLSchemaGenerator.fromMetadataToSQL(
            metadata_path, output_dir, overwrite_previous
        )
        
        # Generate PostgreSQL SQL scripts
        click.echo("\n--- Generating PostgreSQL SQL scripts ---")
        postgres_files = PostgreSQLSchemaGenerator.fromMetadataToSQL(
            metadata_path, output_dir, overwrite_previous
        )
        
        click.echo(f"\n✓ Successfully generated SQL scripts:")
        click.echo(f"  MySQL CREATE TABLE: {os.path.basename(mysql_files['create_table_sql'])}")
        click.echo(f"  MySQL IMPORT DATA: {os.path.basename(mysql_files['import_data_sql'])}")
        click.echo(f"  PostgreSQL CREATE TABLE: {os.path.basename(postgres_files['create_table_sql'])}")
        click.echo(f"  PostgreSQL IMPORT DATA: {os.path.basename(postgres_files['import_data_sql'])}")
        
    except CSViperError as e:
        click.echo(f"{e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--from_resource_dir', required=True, type=click.Path(exists=True),
              help='Directory containing metadata and SQL files from previous stages')
@click.option('--output_dir', type=click.Path(),
              help='Output directory (defaults to resource directory)')
@click.option('--overwrite_previous', is_flag=True, default=False,
              help='Overwrite existing output files')
def build_import_script(from_resource_dir, output_dir, overwrite_previous):
    """
    Generate Python import scripts from resource directory.
    
    Creates standalone Python scripts (go.mysql.py and go.postgresql.py) that can be used to import
    CSV data into databases using the generated SQL scripts.
    """
    try:
        from .mysql_import_script_generator import MySQLImportScriptGenerator
        from .postgresql_import_script_generator import PostgreSQLImportScriptGenerator
        
        # Convert to absolute path
        resource_dir = os.path.abspath(from_resource_dir)
        
        # Determine output directory if not specified
        if not output_dir:
            output_dir = resource_dir
        
        output_dir = os.path.abspath(output_dir)
        
        click.echo(f"Generating import scripts from: {resource_dir}")
        click.echo(f"Output directory: {output_dir}")
        
        # Generate MySQL import script
        click.echo("\n--- Generating MySQL import script ---")
        mysql_script_path = MySQLImportScriptGenerator.fromResourceDirToScript(
            resource_dir, output_dir, overwrite_previous
        )
        
        # Generate PostgreSQL import script
        click.echo("\n--- Generating PostgreSQL import script ---")
        postgresql_script_path = PostgreSQLImportScriptGenerator.fromResourceDirToScript(
            resource_dir, output_dir, overwrite_previous
        )
        
        click.echo(f"\n✓ Successfully generated import scripts:")
        click.echo(f"  MySQL: {os.path.basename(mysql_script_path)}")
        click.echo(f"  PostgreSQL: {os.path.basename(postgresql_script_path)}")
        click.echo(f"\nTo use the scripts:")
        click.echo(f"  python {os.path.basename(mysql_script_path)} --csv_file=<csv> [--db_schema_name=<schema>] [--table_name=<table>]")
        click.echo(f"  python {os.path.basename(postgresql_script_path)} --csv_file=<csv> [--db_schema_name=<schema>] [--table_name=<table>]")
        click.echo(f"\nNote: Schema and table names can be set via DB_SCHEMA and DB_TABLE environment variables")
        
    except CSViperError as e:
        click.echo(f"{e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--from_csv', required=True, type=click.Path(exists=True), 
              help='Path to the CSV file to process')
@click.option('--output_dir', type=click.Path(), 
              help='Output directory (defaults to CSV filename without extension)')
@click.option('--overwrite_previous', is_flag=True, default=False,
              help='Overwrite existing output files')
@click.pass_context
def full_compile(ctx, from_csv, output_dir, overwrite_previous):
    """
    Run all compilation stages in sequence.
    
    Performs the complete CSViper workflow:
    1. Extract metadata from CSV file
    2. Generate SQL scripts from metadata
    3. Generate Python import scripts
    
    This is equivalent to running extract_metadata, build_sql, and build_import_script
    in sequence with the same parameters.
    """
    try:
        # Convert to absolute path
        csv_path = os.path.abspath(from_csv)
        
        # Determine output directory if not specified
        if not output_dir:
            csv_basename = os.path.basename(csv_path)
            output_dir = os.path.splitext(csv_basename)[0]
        
        output_dir = os.path.abspath(output_dir)
        
        click.echo("=" * 60)
        click.echo("CSViper Full Compilation")
        click.echo("=" * 60)
        click.echo(f"Input CSV: {csv_path}")
        click.echo(f"Output directory: {output_dir}")
        click.echo(f"Overwrite existing files: {overwrite_previous}")
        click.echo()
        
        # Stage 1: Extract metadata
        click.echo("STAGE 1: Extracting metadata from CSV file")
        click.echo("-" * 40)
        ctx.invoke(extract_metadata, 
                  from_csv=from_csv, 
                  output_dir=output_dir, 
                  overwrite_previous=overwrite_previous)
        
        # Stage 2: Generate SQL scripts
        click.echo(f"\nSTAGE 2: Generating SQL scripts from metadata")
        click.echo("-" * 40)
        metadata_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(csv_path))[0]}.metadata.json")
        ctx.invoke(build_sql, 
                  from_metadata_json=metadata_path, 
                  output_dir=output_dir, 
                  overwrite_previous=overwrite_previous)
        
        # Stage 3: Generate import scripts
        click.echo(f"\nSTAGE 3: Generating Python import scripts")
        click.echo("-" * 40)
        ctx.invoke(build_import_script, 
                  from_resource_dir=output_dir, 
                  output_dir=output_dir, 
                  overwrite_previous=overwrite_previous)
        
        # Final summary
        click.echo(f"\n" + "=" * 60)
        click.echo("FULL COMPILATION COMPLETE")
        click.echo("=" * 60)
        click.echo(f"All files generated in: {output_dir}")
        
    except CSViperError as e:
        click.echo(f"{e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
