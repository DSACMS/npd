ALTER TABLE ${apiSchema}.address DROP COLUMN IF EXISTS smarty_key;
ALTER TABLE ${apiSchema}.address DROP COLUMN IF EXISTS barcode_delivery_code;
ALTER TABLE ${apiSchema}.address_nonstandard DROP COLUMN IF EXISTS addressee;
ALTER TABLE ${apiSchema}.address_us DROP COLUMN IF EXISTS addressee;
ALTER TABLE ${apiSchema}.clinical_organization DROP COLUMN IF EXISTS endpoint_instance_id;
