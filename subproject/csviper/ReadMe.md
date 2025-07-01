# CSViper

CSViper is a command-line tool that automates the process of analyzing CSV files and generating SQL scripts and Python programs to load the data into relational databases. It supports both MySQL and PostgreSQL backends and is designed for scenarios where the database is hosted remotely while the CSV file resides on the local machine.

## Features

- **CSV Analysis**: Automatically detects CSV format (delimiter, quote character) and analyzes column structure
- **Column Normalization**: Converts column names to SQL-safe identifiers with intelligent duplicate handling
- **Multi-Database Support**: Generates scripts for both MySQL and PostgreSQL
- **Modular Design**: Three-phase approach allows for flexible workflow management
- **Standalone Scripts**: Generates self-contained Python import scripts for easy deployment

## Installation

### From Source (Development)

1. Clone the repository:
```bash
git clone https://github.com/ftrotter/csviper.git
cd csviper
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install in development mode:
```bash
pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install csviper
```

## Usage

CSViper operates in three phases that can be run together or separately:

### Phase 1: Extract Metadata

Analyze a CSV file and extract column information:

```bash
python -m csviper extract_metadata --from_csv=data.csv --output_dir=./output/
```

Options:
- `--from_csv`: Path to the CSV file to analyze (required)
- `--output_dir`: Output directory (defaults to CSV filename without extension)
- `--overwrite_previous`: Overwrite existing output files

### Phase 2: Generate SQL Scripts (Coming Soon)

Generate CREATE TABLE and data import SQL scripts:

```bash
python -m csviper build_sql --from_metadata_json=output/data.metadata.json --output_dir=./output/
```

### Phase 3: Generate Import Script (Coming Soon)

Create a standalone Python script for data import:

```bash
python -m csviper build_import_script --from_resource_dir=./output/ --output_dir=./output/
```

### Running All Phases Together (Coming Soon)

```bash
python -m csviper extract_metadata --from_csv=data.csv --output_dir=./output/ --overwrite_previous
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Setting up the Development Environment

1. Clone the repository and navigate to the project directory
2. Source the virtual environment setup script:
```bash
source source_me_to_get_venv.sh
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
```

## Project Structure

```
csviper/
├── src/csviper/
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # CLI entry point
│   ├── column_normalizer.py     # Column name normalization utilities
│   ├── metadata_extractor.py    # CSV analysis and metadata extraction
│   ├── mysql_generator.py       # MySQL SQL generation (coming soon)
│   ├── postgresql_generator.py  # PostgreSQL SQL generation (coming soon)
│   └── script_generators/       # Python script generation (coming soon)
├── tests/                       # Test files
├── AI_Instructions/             # Development documentation
├── setup.py                     # Package setup configuration
├── requirements.txt             # Project dependencies
└── README.md                    # This file
```

## Output Files

CSViper generates several files during processing:

### Phase 1 Output
- `{filename}.metadata.json`: Contains CSV structure analysis, normalized column names, and column width information

### Phase 2 Output (Coming Soon)
- `{filename}.create_table_mysql.sql`: MySQL CREATE TABLE script
- `{filename}.create_table_postgres.sql`: PostgreSQL CREATE TABLE script
- `{filename}.import_data_mysql.sql`: MySQL data import script
- `{filename}.import_data_postgres.sql`: PostgreSQL data import script

### Phase 3 Output (Coming Soon)
- `go.py`: Standalone Python script for database import

## Example Workflow

1. **Analyze your CSV file**:
```bash
python -m csviper extract_metadata --from_csv=sales_data.csv
```

2. **Review the generated metadata** in `sales_data/sales_data.metadata.json`

3. **Generate SQL scripts** (coming soon):
```bash
python -m csviper build_sql --from_metadata_json=sales_data/sales_data.metadata.json
```

4. **Create import script** (coming soon):
```bash
python -m csviper build_import_script --from_resource_dir=sales_data/
```

5. **Use the generated script** to import data into your database

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [x] Phase 1: CSV metadata extraction and column normalization
- [ ] Phase 2: SQL script generation for MySQL and PostgreSQL
- [ ] Phase 3: Python import script generation
- [ ] Enhanced error handling and validation
- [ ] Progress bars for large file processing
- [ ] Configuration file support
- [ ] Additional database backend support

## Support

For questions, issues, or contributions, please visit the [GitHub repository](https://github.com/ftrotter/csviper).
