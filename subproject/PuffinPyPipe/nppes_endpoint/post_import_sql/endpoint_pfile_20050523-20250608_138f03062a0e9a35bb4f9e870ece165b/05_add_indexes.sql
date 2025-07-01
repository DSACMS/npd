
CREATE INDEX endpoint_file_NPI_index
    on REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME (npi);

CREATE INDEX endpoint_file_NPI_endpoint
    on REPLACE_ME_DATABASE_NAME.REPLACE_ME_TABLE_NAME (npi, "endpoint");

