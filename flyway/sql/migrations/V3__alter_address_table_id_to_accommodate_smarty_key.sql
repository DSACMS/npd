
-- Due to the geocoding, the unique identifiers for the specific address records are smarty keys, which have the type varchar(10). This change alters the id field in each specific address table to accommodate the smarty key. It also cleans up a few unnecessary columns.
alter table npd.address drop constraint fk_address_address_international_id;
alter table npd.address_international alter column id type varchar(10);
alter table npd.address alter column address_international_id type varchar(10);
alter table npd.address add constraint fk_address_address_international_id foreign key (address_international_id) references npd.address_international(id);
alter table npd.address_international drop column input_id;

alter table npd.address drop constraint fk_address_address_nonstandard_id;
alter table npd.address_nonstandard alter column id type varchar(10);
alter table npd.address alter column address_nonstandard_id type varchar(10);
alter table npd.address add constraint fk_address_address_nonstandard_id foreign key (address_nonstandard_id) references npd.address_nonstandard(id);
alter table npd.address_nonstandard drop column input_id;
alter table npd.address_nonstandard drop column input_index;
alter table npd.address_nonstandard drop column candidate_index;

alter table npd.address drop constraint fk_address_address_us_id;
alter table npd.address_us alter column id type varchar(10);
alter table npd.address alter column address_us_id type varchar(10);
alter table npd.address add constraint fk_address_address_us_id foreign key (address_us_id) references npd.address_us(id);
alter table npd.address_us drop column input_id;
alter table npd.address_us drop column input_index;
alter table npd.address_us drop column candidate_index;

alter table npd.address_us alter column delivery_line_1 set not null;
alter table npd.address_us alter column primary_number drop not null;
alter table npd.address_us alter column street_name drop not null;
alter table npd.address_us alter column county_code drop not null;