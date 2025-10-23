ALTER TABLE npd.address DROP COLUMN IF EXISTS smarty_key;
ALTER TABLE npd.address DROP COLUMN IF EXISTS barcode_delivery_code;
ALTER TABLE npd.address_nonstandard DROP COLUMN IF EXISTS addressee;
ALTER TABLE npd.address_us DROP COLUMN IF EXISTS addressee;
ALTER TABLE npd.clinical_organization DROP COLUMN IF EXISTS endpoint_instance_id;
