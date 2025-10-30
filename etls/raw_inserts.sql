--insert into npd.npi (npi, entity_type_code, replacement_npi, enumeration_date, last_update_date, deactivation_reason_code, deactivation_date, reactivation_date, certification_date) select npi, case when entity_type_code='' then null else entity_type_code::smallint end as entity_type_code, replacement_npi, enumeration_date, last_update_date, deactivation_reason_code, deactivation_date, reactivation_date, certification_date from silver_nppes.npidetail where entity_type_code is not null and entity_type_code not like '';

--insert into npd.address_us (id, delivery_line_1, delivery_line_2, last_line, delivery_point_barcode, urbanization, primary_number, street_name, street_predirection, street_postdirection, street_suffix, secondary_number, secondary_designator, extra_secondary_number, extra_secondary_designator, pmb_designator, pmb_number, city_name, default_city_name, state_code, zipcode, plus4_code, delivery_point, delivery_point_check_digit, record_type, zip_type, county_code, ews_match, carrier_route, congressional_district, building_default_indicator, rdi, elot_sequence, elot_sort, latitude, longitude, coordinate_license, geo_precision, time_zone, utc_offset, dst, dpv_match_code, dpv_footnotes, dpv_cmra, dpv_vacant, dpv_no_stat, active, footnotes, lacslink_code, lacslink_indicator, suitelink_match, enhanced_match) 
--select smarty_key as id, delivery_line_1, delivery_line_2, last_line, delivery_point_barcode, urbanization, primary_number, street_name, street_predirection, street_postdirection, street_suffix, secondary_number, secondary_designator, extra_secondary_number, extra_secondary_designator, pmb_designator, pmb_number, city_name, default_city_name, fs.id as state_code, zipcode, plus4_code, delivery_point, delivery_point_check_digit, record_type, zip_type, county_fips as county_code, ews_match, carrier_route, congressional_district, building_default_indicator, rdi, elot_sequence, elot_sort, latitude, longitude, coordinate_license, geo_precision, time_zone, utc_offset, dst, dpv_match_code, dpv_footnotes, dpv_cmra, dpv_vacant, dpv_no_stat, active, footnotes, lacslink_code, lacslink_indicator, suitelink_match, enhanced_match
--	FROM silver_address.address_us a
--	LEFT JOIN npd.fips_state fs on fs.abbreviation = a.state_abbreviation;

--insert into npd.address (id, address_us_id) select gen_random_uuid(), id from npd.address_us;

--alter table silver_nppes.npidetail add uuid_id uuid default gen_random_uuid();

--insert into npd.individual (id) select uuid_id from silver_nppes.npidetail where entity_type_code like '1';

insert into npd.provider (individual_id, npi) select uuid_id as individual_id, npi from silver_nppes.npidetail where entity_type_code like '1';

insert into npd.organization (id) select uuid_id from silver_nppes.npidetail where entity_type_code like '2';

insert into npd.clinical_organization (organization_id, npi) select uuid_id as organization_id, npi from silver_nppes.npidetail where entity_type_code like '2';

insert into npd.individual_to_name (individual_id, prefix, first_name, middle_name, last_name, suffix, name_use_id) select n.uuid as individual_id, prefix, first_name, middle_name, last_name, suffix, 1 as name_use_id from silver_nppes.npi_individual i left join silver_nppes.npidetail n on i.npi = n.npi;

insert into npd.organization_to_name (organization_id, name, is_primary) select organization_id, organization_name as name from npd.clinical_organization co left join silver_nppes.orgname o on co.npi = o.npi;