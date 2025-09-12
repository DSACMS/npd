# FIPS County ETL Pipeline

An automated ETL pipeline that extracts US county FIPS codes from the Census Bureau, transforms the data, and loads it into a PostgreSQL database.

## Setup

1. Install dependencies within the /loadFIPS directory*
```bash
pip install -r requirements.txt
```

2. Create `.env` file using `env.example` as a template
```
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
MAX_RETRIES=3
```

## Usage

```bash
python loadFIPS.py
```

## Output Schema

| Column | Type | Description |
|--------|------|-------------|
| id | string | Combined STATEFP + COUNTYFP (5 digits) |
| name | string | County name |
| fips_state_id | string | 2-digit state FIPS code |
