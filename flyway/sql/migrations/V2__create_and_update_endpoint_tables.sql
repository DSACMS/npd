alter table ${apiSchema}.endpoint add name varchar(200);

create table ${apiSchema}.endpoint_connection_type (
id varchar(20) primary key,
display varchar(20) not null,
definition varchar(200)
);

alter table ${apiSchema}.endpoint_instance drop column endpoint_instance_type_id;

alter table ${apiSchema}.endpoint_instance add endpoint_connection_type_id varchar(20);

alter table ${apiSchema}.endpoint_instance add constraint fk_endpoint_instance_endpoint_connection_type_id 
foreign key (endpoint_connection_type_id) references ${apiSchema}.endpoint_connection_type(id);

alter table ${apiSchema}.endpoint_instance add name varchar(200);

alter table ${apiSchema}.endpoint_instance add description varchar(1000);

create table ${apiSchema}.environment_type (
id varchar(10) primary key,
display varchar(20) not null,
definition varchar(200)
);

alter table ${apiSchema}.endpoint_instance add environment_type_id varchar(20);

alter table ${apiSchema}.endpoint_instance add constraint fk_endpoint_instance_environment_type_id 
foreign key (environment_type_id) references ${apiSchema}.environment_type(id);

create table ${apiSchema}.mime_type (
id serial primary key,
value varchar(200)
);

create table ${apiSchema}.payload_type (
id varchar(100) primary key,
value varchar(200),
description varchar(1000)
);

create table ${apiSchema}.endpoint_to_payload (
endpoint_id uuid,
mime_type_id int,
payload_type_id varchar(200),
primary key (endpoint_id, payload_type_id)
);

alter table ${apiSchema}.endpoint_to_payload add constraint fk_endpoint_to_payload_mime_type_id foreign key (mime_type_id) references ${apiSchema}.mime_type(id);
alter table ${apiSchema}.endpoint_to_payload add constraint fk_endpoint_to_payload_type_id foreign key (payload_type_id) references ${apiSchema}.payload_type(id);
alter table ${apiSchema}.endpoint_to_payload add constraint fk_endpoint_to_payload_endpoint_id foreign key (endpoint_id) references ${apiSchema}.endpoint(id);

create table ${apiSchema}.endpoint_instance_to_payload (
endpoint_instance_id uuid,
mime_type_id int,
payload_type_id varchar(200),
primary key (endpoint_instance_id, payload_type_id)
);

alter table ${apiSchema}.endpoint_instance_to_payload add constraint fk_endpoint_instance_to_payload_mime_type_id foreign key (mime_type_id) references ${apiSchema}.mime_type(id);
alter table ${apiSchema}.endpoint_instance_to_payload add constraint fk_endpoint_instance_to_payload_type_id foreign key (payload_type_id) references ${apiSchema}.payload_type(id);
alter table ${apiSchema}.endpoint_instance_to_payload add constraint fk_endpoint_instance_to_payload_endpoint_instance_id foreign key (endpoint_instance_id) references ${apiSchema}.endpoint_instance(id);

CREATE TABLE IF NOT EXISTS ${apiSchema}.endpoint_instance_to_other_id
(
    endpoint_instance_id uuid NOT NULL,
    other_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
	system varchar(200) not null,
    issuer_id uuid NOT NULL,
    CONSTRAINT pk_endpoint_instance_to_other_id PRIMARY KEY (endpoint_instance_id, other_id, issuer_id),
    CONSTRAINT fk_endpoint_instance_to_other_id_endpoint_instance_id FOREIGN KEY (endpoint_instance_id)
        REFERENCES ${apiSchema}.endpoint_instance (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ${apiSchema}.endpoint_to_other_id
(
    endpoint_id uuid NOT NULL,
    other_id character varying(100) COLLATE pg_catalog."default" NOT NULL,
	system varchar(200) not null,
    issuer_id uuid NOT NULL,
    CONSTRAINT pk_endpoint_to_other_id PRIMARY KEY (endpoint_id, other_id, issuer_id),
    CONSTRAINT fk_endpoint_to_other_id_endpoint_id FOREIGN KEY (endpoint_id)
        REFERENCES ${apiSchema}.endpoint (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
);
