alter table npd.address_us add column geolocation point;
alter table npd.address_international add column geolocation point;
alter table npd.address_nonstandard add column geolocation point;

update npd.address_us set geolocation = '(' || longitude || ', ' || latitude || ')' ;
update npd.address_international set geolocation = '(' || longitude || ', ' || latitude || ')' ;
update npd.address_nonstandard set geolocation = '(' || longitude || ', ' || latitude || ')' ;