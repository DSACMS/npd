ALTER TABLE npd.address DROP smarty_key IF EXISTS;
ALTER TABLE npd.address DROP barcode_delivery_code IF EXISTS;
ALTER TABLE npd.address_nonstandard DROP addressee IF EXISTS;
ALTER TABLE npd.address_us DROP addressee IF EXISTS;
ALTER TABLE npd.clinical_organization DROP endpoint_instance_id IF EXISTS;
