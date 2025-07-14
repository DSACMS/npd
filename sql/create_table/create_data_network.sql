


CREATE TABLE ndh.data_network (
    -- marketplace/network-puf.NetworkID
    id SERIAL PRIMARY KEY,
    -- marketplace/network-puf.NetworkName
    data_network_name varchar(100)   NOT NULL,
    -- marketplace/network-puf.NetworkURL
    data_network_blurb TEXT DEFAULT NULL,
    data_network_url varchar(500)   DEFAULT NULL,
    data_network_logo_url varchar(500)   DEFAULT NULL,
    CONSTRAINT uc_data_network_name UNIQUE (
        data_network_name
    )        
);

CREATE TABLE ndh.npi_data_network (
    id SERIAL PRIMARY KEY,
    npi_id BIGINT   NOT NULL,
    data_network_id INT   NOT NULL
);