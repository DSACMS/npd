create extension postgis;

alter table npd.address_us add column geolocation geometry;
alter table npd.address_international add column geolocation geometry;
alter table npd.address_nonstandard add column geolocation geometry;

update npd.address_us set geolocation = ST_point(longitude, latitude);
update npd.address_international set geolocation = ST_point(longitude, latitude);
update npd.address_nonstandard set geolocation = ST_point(longitude, latitude);