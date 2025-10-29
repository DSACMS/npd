# Glue Overview

Glue is a platform-as-a-service offering from AWS for implementing repeatable, scalable ETL processes. It supports reading and writing data from AWS services (including S3, RDS, and Kinesis) and third-party services (SAP HANA, Oracle, Snowflake, etc). 

## Concepts

### Jobs

An ETL process defined using a drag-and-drop visual editor or Python/PySpark code. Job runs can be started automatically on a schedule, in response to a cloud event, or manually from the AWS Glue console.

#### Visual Editor

The visual job editor allows a user to build an ETL process by placing nodes and edges on a graph. Nodes represent:

- Sources (Where does the data come from?)
- Transforms (How is the data processed? How is this data combined with data from other sources?)
- Targets (Where is the data going? What format is it being saved in?)

There are dozens of built-in transformations defined in the visual editor, and the author can preview results of transformation at each step. Example transformations include:

- Join data from two tables
- Drop duplicate rows
- Assess data quality
- Detect PII
- Aggregate values
- Rename columns, drop columns, etc
- Implement a custom transformation using SQL or Python

The output of the visual editor is a PySpark job (written in Python) which can be previewed during development. The PySpark script can be modified/tracked in source control (but after export, the PySpark script can't be re-imported and visualized by the editor).

#### PySpark Jobs

PySpark Jobs are the core Glue product; they handle workloads at various scales, but the economics / parallel execution environment of running Spark favor use with medium-to-large datasets (gigabytes to petabytes of data). PySpark jobs running in Glue have AWS-specific abstractions for reading, writing, and transforming data:

- [DynamicFrame](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-extensions-dynamic-frame.html): similar to a Spark DataFrame, but is self-describing (does not require a schema to be defined ahead of time). It maps to a table in a relational database. Generally, data transformations are specified at the DynamicFrame (rather than DynamicRecord) level. DynamicFrames can be converted to Spark DataFrames and back again.
- DynamicRecord: An individual record within a DynamicFrame
- [DynamicFrameReader](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-extensions-dynamic-frame-reader.html): an abstraction that reads CSV/JSON/Database/etc into a consistent DynamicFrame format
- [DynamicFrameWriter](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-extensions-dynamic-frame-writer.html): an abstraction that writes the contents of a DynamicFrame into CSV/JSON/DB Table

PySpark jobs can be authored in a Jupyter Notebook interface using AWS Glue Studio.

**Use case**: Complex, ETL jobs ingesting frequently updated, large datasets from NPPES/PECOS via IDR

##### Capacity / Billing

Glue bills for usage in DPU increments (data processing unit) per hour, with a 1-minute minimum. A single DPU costs $0.44 for an hour.

A single DPU includes 4 vCPUs and 16 GB of RAM. The minimum DPUs that can be specified for a PySpark job is 2 (one DPU is required for coordinating parallel execution, while the other nodes perform the ETL work).

| DPUs | Execution Time | Math | Cost | Notes |
|-|-|-|-|-|
| 2 | 30s | 2 * 1/60 * $0.44 | $0.01 | Minimum billed time is 1 minute |
| 2 | 10m | 2 * 1/6 * $0.44 | $0.15 | |
| 10 | 10m | 10 * 1/6 * $0.44 | $0.73 | 10 is the default DPU allocation for PySpark jobs |
| 100 | 10m | 100 * 1/6 * $0.44 | $7.33 | |

##### Local Development

AWS provides a Docker image that emulates the 

#### Python Shell

Python Shell jobs run in a Python 3.9 environment meant to be used for small-to-medium ETL workloads (megabytes to gigabytes) running on a single instance. Python Shell covers workloads that might otherwise be implemented with AWS Lambda or Fargate, while keeping the job history, logging information, etc within the AWS Glue interface.

**Use case**: Updating NUCC taxonomy / FIPS codes in our database periodically

##### Capacity / Billing

Like PySpark jobs, Pythonshell jobs are billed at $0.44 per DPU/hour with a 1 minute minimum run, but a single or fractional DPU can be used to run the job. By default, pythonshell jobs have 1/16 DPU.

| DPUs | Execution Time | Math | Cost | Notes | 
|-|-|-|-|-|
| 1/16 | 30s | 1/16 * 1/60 * $0.44 | $0.0004 | Minimum execution time is 1 minute |
| 1/16 | 10m | 1/16 * 1/6 * $0.44 | $0.004 
| 1    | 30s | 1 * 1/60 * $0.44 | $0.007 | Minimum execution time is 1 minute | 
| 1    | 10m | 1 * 1/6 * $0.44 | $0.07 | | 

### Data Catalog

Data Catalog is a service that tracks metadata for various datasets, including those in CSVs, JSON, and in relational databases. Tracking metadata in Data Catalog makes it easier to ingest structured flat files.

#### Billing

- First million objects stored in data catalog are free
- $1.00 per 100,000 aditional objects stored
- First million requests are free
- $1.00 per million additional requests

#### Crawler

A crawler is an automated process that analyzes datasets to determine their schema, populating tables the data catalog. The crawler works with data in flat files (CSV, JSON, Parquet, etc) and data in relational databases.

#### Billing

- $0.44 per DPU-Hour, billed per second, with a 10-minute minimum per crawler run

### Connections

AWS Glue is able to connect to S3 natively, but connecting to JDBC datasets requires additional network configuration to access the database

### Bookmarks

Glue uses job bookmarks to keep track of what data has already been ingested to avoid reprocessing data. Bookmarks are implemented for JDBC (e.g. Postgres on RDS) and some S3 datasets (JSON, CSV, Apache Avro, XML, Parquet, ORC). This is especially helpful for case where a dataset is updated regularly.

- For S3 datasources, bookmarks rely on an object's last-modified property to determine what needs to be reingested
- For JDBC datasources, the primary key is used by default, but one or more columns can be specified to be used for the bookmark.

### Data Quality

Glue uses the open source library library [deequ](https://github.com/awslabs/deequ) to define "unit tests for data" in a Spark environment. Tests can be defined using Python or the DQDL domain-specific language.

## Glue and Infrastructure-as-Code

- AWS Glue [jobs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_job), [connections](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_connection), [crawlers](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_crawler), etc are well supported by Terraform.
- Terraform supports packaging locally-authored ETL scripts and deploying to either PySpark or Pythonshell environments

## Glue and Local Development

- Pythonshell jobs are just Python 3.9 
- PySpark jobs can be authored locally using a docker container that [emulates the glue environment](https://docs.aws.amazon.com/glue/latest/dg/develop-local-docker-image.html) 

## Glue alternatives to consider

### Apache Spark on EMR

AWS EMR is an infrastructure-as-a-service offering that supports running Spark workloads and also integrates with the data catalog, which could be a more portable / open-source alternative to using Glue directly

Pros:
- Less tied to AWS ecosystem / more portable 

Cons:
- We take on responsibility of provision / monitoring servers, different billing model to consider
- Lose convenience / integrations of the Glue ecosystem

### Fargate / Lambda

Lambda / Fargate could also be used for long-running single-node ETL workloads while still delegating infrastructure management to AWS.

Pros:
- Orders of magnitude cheaper than Glue PySpark / Pythonshell jobs per job: 

Assuming we run a 10 minute process once a day for a month:

| Service | Requests/month | Duration | vCPU | RAM | Storage | Monthly Cost | Note |
|-|-|-|-|-|-|-|-|
| Glue Pythonshell | 30 | 10m | 4 | 16GB | 20GB | $4.40 | Minimum 1 DPUs | |
| Glue PySpark | 30 | 10m | 8 | 16GB | 20GB | $2.20 | Minimum 2 DPUs |
| Lambda | 30 | 10m | 6 | 10GB | 10GB | [$0.05](https://calculator.aws/#/createCalculator/Lambda) | Lambda maxes out at 10GB RAM and 10 GB ephemeral storage |
| Fargate | 30 | 10m | 4 | 16GB | 20GB | [$1.42](https://calculator.aws/#/createCalculator/Fargate) | | 

- Less tied to AWS ecosystem / more portable

Cons:
- Lose convenience / integrations included with the Glue ecosystem

## Conclusion

Glue is a reasonable choice for implementing and orchestrating ETL processes importing data from NPPES and PECOS, datasets that range from tens of gigabytes to hundreds of gigabytes and are updated frequently.

If only considering cost, Glue seems less attractive than Fargate / Lambda, but if we elect to use Fargate / Lambda we lose (or need to find alternatives to):

- Automated schema determination
- Abstractions that handle reading and writing flat files, writing to databases
- Parallel processing of large datasets
- A large library of reusable transformations
- Integration with Jupyter notebook and visual editor for authoring / documenting ETL jobs
- Consistent run history / logging

All of which are resources we need to leverage to meet our aggressive timelines.
