-- Generated PostgreSQL Foreign Key Statements
-- Source: DURC relational model
-- Generated on: 2025-07-02 03:39:26
-- Command: durc-mine-fkeys --input_json_file durc_config/DURC_relational_model.json --output_sql_file ./sql/foreign_key_sql/foreign_keys.sql

-- Database: ndh
ALTER TABLE ndh.address_us ADD CONSTRAINT fk_address_us_address_id FOREIGN KEY (address_id) REFERENCES ndh.address(id);
ALTER TABLE ndh.address_nonstandard ADD CONSTRAINT fk_address_nonstandard_address_id FOREIGN KEY (address_id) REFERENCES ndh.address(id);
ALTER TABLE ndh.npiaddress ADD CONSTRAINT fk_npiaddress_npi_id FOREIGN KEY (npi_id) REFERENCES ndh.npi(id);
ALTER TABLE ndh.npiaddress ADD CONSTRAINT fk_npiaddress_address_id FOREIGN KEY (address_id) REFERENCES ndh.address(id);
ALTER TABLE ndh.vtin ADD CONSTRAINT fk_vtin_clinicalorganization_id FOREIGN KEY (clinicalorganization_id) REFERENCES ndh.clinicalorganization(id);
ALTER TABLE ndh.address_international ADD CONSTRAINT fk_address_international_address_id FOREIGN KEY (address_id) REFERENCES ndh.address(id);
ALTER TABLE ndh.clinicalorganization ADD CONSTRAINT fk_clinicalorganization_authorizedofficial_individual_id FOREIGN KEY (authorizedofficial_individual_id) REFERENCES ndh.individual(id);
ALTER TABLE ndh.clinicalorganization ADD CONSTRAINT fk_clinicalorganization_primary_vtin_id FOREIGN KEY (primary_vtin_id) REFERENCES ndh.vtin(id);
ALTER TABLE ndh.orgname ADD CONSTRAINT fk_orgname_clinicalorganization_id FOREIGN KEY (clinicalorganization_id) REFERENCES ndh.clinicalorganization(id);
ALTER TABLE ndh.npiidentifier ADD CONSTRAINT fk_npiidentifier_npi_id FOREIGN KEY (npi_id) REFERENCES ndh.npi(id);
ALTER TABLE ndh.address ADD CONSTRAINT fk_address_address_us_id FOREIGN KEY (address_us_id) REFERENCES ndh.address_us(id);
ALTER TABLE ndh.address ADD CONSTRAINT fk_address_address_international_id FOREIGN KEY (address_international_id) REFERENCES ndh.address_international(id);
ALTER TABLE ndh.address ADD CONSTRAINT fk_address_address_nonstandard_id FOREIGN KEY (address_nonstandard_id) REFERENCES ndh.address_nonstandard(id);
ALTER TABLE ndh.ehrtonpi ADD CONSTRAINT fk_ehrtonpi_npi_id FOREIGN KEY (npi_id) REFERENCES ndh.npi(id);
ALTER TABLE ndh.ehrtonpi ADD CONSTRAINT fk_ehrtonpi_ehr_id FOREIGN KEY (ehr_id) REFERENCES ndh.ehr(id);
ALTER TABLE ndh.individualtocredential ADD CONSTRAINT fk_individualtocredential_individual_id FOREIGN KEY (individual_id) REFERENCES ndh.individual(id);
ALTER TABLE ndh.npitoendpoint ADD CONSTRAINT fk_npitoendpoint_npi_id FOREIGN KEY (npi_id) REFERENCES ndh.npi(id);
ALTER TABLE ndh.npi_to_individual ADD CONSTRAINT fk_npi_to_individual_npi_id FOREIGN KEY (npi_id) REFERENCES ndh.npi(id);
ALTER TABLE ndh.npi_to_individual ADD CONSTRAINT fk_npi_to_individual_individual_id FOREIGN KEY (individual_id) REFERENCES ndh.individual(id);
ALTER TABLE ndh.npi_to_clinicalorganization ADD CONSTRAINT fk_npi_to_clinicalorganization_npi_id FOREIGN KEY (npi_id) REFERENCES ndh.npi(id);
ALTER TABLE ndh.npi_to_clinicalorganization ADD CONSTRAINT fk_npi_to_clinicalorganization_clinicalorganization_id FOREIGN KEY (clinicalorganization_id) REFERENCES ndh.clinicalorganization(id);
ALTER TABLE ndh.npi_to_clinicalorganization ADD CONSTRAINT fk_npi_to_clinicalorganization_primaryauthorizedofficial_individual_id FOREIGN KEY (primaryauthorizedofficial_individual_id) REFERENCES ndh.individual(id);
ALTER TABLE ndh.organizationtohealthcarebrand ADD CONSTRAINT fk_organizationtohealthcarebrand_healthcarebrand_id FOREIGN KEY (healthcarebrand_id) REFERENCES ndh.healthcarebrand(id);
ALTER TABLE ndh.plannetworktoorg ADD CONSTRAINT fk_plannetworktoorg_plannetwork_id FOREIGN KEY (plannetwork_id) REFERENCES ndh.plannetwork(id);
ALTER TABLE ndh.npitophone ADD CONSTRAINT fk_npitophone_npi_id FOREIGN KEY (npi_id) REFERENCES ndh.npi(id);
ALTER TABLE ndh.npitophone ADD CONSTRAINT fk_npitophone_phonenumber_id FOREIGN KEY (phonenumber_id) REFERENCES ndh.phonenumber(id);
ALTER TABLE ndh.npitophone ADD CONSTRAINT fk_npitophone_phoneextension_id FOREIGN KEY (phoneextension_id) REFERENCES ndh.phoneextension(id);
ALTER TABLE ndh.nuccmedicareprovidertype ADD CONSTRAINT fk_nuccmedicareprovidertype_medicareprovidertype_id FOREIGN KEY (medicareprovidertype_id) REFERENCES ndh.medicareprovidertype(id);
ALTER TABLE ndh.nuccmedicareprovidertype ADD CONSTRAINT fk_nuccmedicareprovidertype_nucctaxonomycode_id FOREIGN KEY (nucctaxonomycode_id) REFERENCES ndh.nucctaxonomycode(id);
ALTER TABLE ndh.orgtointeropendpoint ADD CONSTRAINT fk_orgtointeropendpoint_interopendpoint_id FOREIGN KEY (interopendpoint_id) REFERENCES ndh.interopendpoint(id);
ALTER TABLE ndh.payertointeropendpoint ADD CONSTRAINT fk_payertointeropendpoint_payer_id FOREIGN KEY (payer_id) REFERENCES ndh.payer(id);
ALTER TABLE ndh.payertointeropendpoint ADD CONSTRAINT fk_payertointeropendpoint_interopendpoint_id FOREIGN KEY (interopendpoint_id) REFERENCES ndh.interopendpoint(id);
ALTER TABLE ndh.plan ADD CONSTRAINT fk_plan_payer_id FOREIGN KEY (payer_id) REFERENCES ndh.payer(id);
ALTER TABLE ndh.plan ADD CONSTRAINT fk_plan_marketcoverage_id FOREIGN KEY (marketcoverage_id) REFERENCES ndh.marketcoverage(id);
ALTER TABLE ndh.plan ADD CONSTRAINT fk_plan_servicearea_id FOREIGN KEY (servicearea_id) REFERENCES ndh.servicearea(id);
ALTER TABLE ndh.plan ADD CONSTRAINT fk_plan_plantype_id FOREIGN KEY (plantype_id) REFERENCES ndh.plantype(id);
ALTER TABLE ndh.plannetworktoplan ADD CONSTRAINT fk_plannetworktoplan_plan_id FOREIGN KEY (plan_id) REFERENCES ndh.plan(id);
ALTER TABLE ndh.plannetworktoplan ADD CONSTRAINT fk_plannetworktoplan_plannetwork_id FOREIGN KEY (plannetwork_id) REFERENCES ndh.plannetwork(id);
ALTER TABLE ndh.npitaxonomy ADD CONSTRAINT fk_npitaxonomy_npi_id FOREIGN KEY (npi_id) REFERENCES ndh.npi(id);
ALTER TABLE ndh.npitaxonomy ADD CONSTRAINT fk_npitaxonomy_nucctaxonomycode_id FOREIGN KEY (nucctaxonomycode_id) REFERENCES ndh.nucctaxonomycode(id);
ALTER TABLE ndh.useraccessrole ADD CONSTRAINT fk_useraccessrole_user_id FOREIGN KEY (user_id) REFERENCES ndh.user(id);
ALTER TABLE ndh.useraccessrole ADD CONSTRAINT fk_useraccessrole_npi_id FOREIGN KEY (npi_id) REFERENCES ndh.npi(id);

-- Database: nppes_normal
ALTER TABLE nppes_normal.npi_identifier ADD CONSTRAINT fk_npi_identifier_npidetail_id FOREIGN KEY (npidetail_id) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_identifier ADD CONSTRAINT fk_npi_identifier_npi FOREIGN KEY (npi) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_identifier ADD CONSTRAINT fk_npi_identifier_identifier_type_code FOREIGN KEY (identifier_type_code) REFERENCES nppes_normal.identifier_type_lut(id);
ALTER TABLE nppes_normal.npi_individual ADD CONSTRAINT fk_npi_individual_npidetail_id FOREIGN KEY (npidetail_id) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_individual ADD CONSTRAINT fk_npi_individual_npi FOREIGN KEY (npi) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_organization ADD CONSTRAINT fk_npi_organization_npidetail_id FOREIGN KEY (npidetail_id) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_organization ADD CONSTRAINT fk_npi_organization_npi FOREIGN KEY (npi) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.orgname ADD CONSTRAINT fk_orgname_npidetail_id FOREIGN KEY (npidetail_id) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.orgname ADD CONSTRAINT fk_orgname_npi FOREIGN KEY (npi) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.orgname ADD CONSTRAINT fk_orgname_orgname_type_code FOREIGN KEY (orgname_type_code) REFERENCES nppes_normal.orgname_type_lut(id);
ALTER TABLE nppes_normal.npi_address ADD CONSTRAINT fk_npi_address_npidetail_id FOREIGN KEY (npidetail_id) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_address ADD CONSTRAINT fk_npi_address_npi FOREIGN KEY (npi) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_address ADD CONSTRAINT fk_npi_address_state_id FOREIGN KEY (state_id) REFERENCES nppes_normal.state_code_lut(id);
ALTER TABLE nppes_normal.npi_endpoints ADD CONSTRAINT fk_npi_endpoints_npidetail_id FOREIGN KEY (npidetail_id) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_endpoints ADD CONSTRAINT fk_npi_endpoints_npi FOREIGN KEY (npi) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_endpoints ADD CONSTRAINT fk_npi_endpoints_state_id FOREIGN KEY (state_id) REFERENCES nppes_normal.state_code_lut(id);
ALTER TABLE nppes_normal.npi_phone ADD CONSTRAINT fk_npi_phone_npidetail_id FOREIGN KEY (npidetail_id) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_phone ADD CONSTRAINT fk_npi_phone_npi FOREIGN KEY (npi) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_taxonomy ADD CONSTRAINT fk_npi_taxonomy_npidetail_id FOREIGN KEY (npidetail_id) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_taxonomy ADD CONSTRAINT fk_npi_taxonomy_npi FOREIGN KEY (npi) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_identifiers ADD CONSTRAINT fk_npi_identifiers_npidetail_id FOREIGN KEY (npidetail_id) REFERENCES nppes_normal.npidetail(id);
ALTER TABLE nppes_normal.npi_identifiers ADD CONSTRAINT fk_npi_identifiers_npi FOREIGN KEY (npi) REFERENCES nppes_normal.npidetail(id);

