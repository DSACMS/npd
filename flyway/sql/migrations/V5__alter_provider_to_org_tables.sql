create table npd.provider_role (
	code varchar(10) primary key,
	system varchar(100) not null,
	display varchar(100) not null,
	description varchar(200)
);

delete from npd.provider_to_organization where 1=1;
delete from npd.provider_to_taxonomy where 1=1;

alter table npd.individual_to_phone add id uuid not null;
alter table npd.individual_to_phone drop constraint pk_individual_to_phone;
alter table npd.individual_to_phone add constraint pk_individual_to_phone primary key (id);
alter table npd.individual_to_phone add constraint uc_individual_to_phone_individual_id_phone_number unique (individual_id, phone_number, phone_use_id);

alter table npd.provider_to_location drop constraint fk_provider_to_location_individual_id_organization_id;
alter table npd.provider_to_credential drop constraint fk_provider_to_credential_npi_nucc_code;

alter table npd.provider_to_organization add id uuid not null;
alter table npd.provider_to_organization drop column endpoint_id;
alter table npd.provider_to_organization drop constraint pk_provider_to_organization;
alter table npd.provider_to_organization add constraint pk_provider_to_organization primary key (id);
-- Note: this is a naive unique constraint that we will likely expand based on the real data
alter table npd.provider_to_organization add constraint uc_provider_to_organization_individual_id_organization_id unique (individual_id, organization_id, relationship_type_id);

alter table npd.provider_to_location add provider_role_code varchar(10); 
alter table npd.provider_to_location add other_phone_id uuid;
alter table npd.provider_to_location add other_endpoint_id uuid;
alter table npd.provider_to_location add constraint fk_provider_to_location_endpoint_id foreign key (other_endpoint_id) references npd.endpoint(id);
alter table npd.provider_to_location add constraint fk_individual_to_other_phone_id foreign key (other_phone_id) references npd.individual_to_phone(id);


alter table npd.organization_to_phone add id uuid not null;
alter table npd.organization_to_phone drop constraint pk_organization_to_phone;
alter table npd.organization_to_phone add constraint pk_organization_to_phone primary key (id);
alter table npd.organization_to_phone add constraint uc_organization_to_phone_organization_id_phone_number unique (organization_id, phone_number, extension, phone_use_id);

alter table npd.location add phone_id uuid;

alter table npd.location add constraint fk_location_phone_id foreign key (phone_id)
references npd.organization_to_phone(id);

alter table npd.provider_to_location add provider_to_organization_id uuid not null;
alter table npd.provider_to_location add constraint fk_provider_to_location_provider_to_organization_id foreign key (provider_to_organization_id) references npd.provider_to_organization(id);
alter table npd.provider_to_location drop column organization_id;
alter table npd.provider_to_location drop column individual_id;

alter table npd.provider_to_taxonomy add id uuid not null;
alter table npd.provider_to_taxonomy drop constraint pk_provider_to_taxonomy;
alter table npd.provider_to_taxonomy add constraint pk_provider_to_taxonomy primary key (id);
alter table npd.provider_to_taxonomy add constraint uc_provider_to_taxonomy unique(npi, nucc_code);

alter table npd.provider_to_credential add column provider_to_taxonomy_id uuid not null;
alter table npd.provider_to_credential add constraint fk_provider_to_credential_provider_to_taxonomy_id foreign key (provider_to_taxonomy_id) references npd.provider_to_taxonomy(id);
alter table npd.provider_to_credential drop column npi;
alter table npd.provider_to_credential drop column nucc_code;