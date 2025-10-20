INSERT INTO npd.individual (id, gender, birth_date) VALUES ('11111111-1111-1111-1111-111111111111', 'F', '1738-06-07') ON CONFLICT DO NOTHING;
INSERT INTO npd.individual_to_name (individual_id, first_name, last_name, name_use_id) VALUES ('11111111-1111-1111-1111-111111111111', 'Jersey', 'Joe', 1) ON CONFLICT DO NOTHING;
INSERT INTO npd.legal_entity (ein_id, dba_name) VALUES ('22222222-2222-2222-2222-222222222222', 'Joe Administrative Services LLC') ON CONFLICT DO NOTHING;
INSERT INTO npd.organization (id, authorized_official_id, ein_id, parent_id) VALUES ('33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', NULL) ON CONFLICT DO NOTHING;
INSERT INTO npd.organization_to_name (organization_id, name, is_primary) VALUES ('33333333-3333-3333-3333-333333333333', 'Joe Health Incorporated', true) ON CONFLICT DO NOTHING;
INSERT INTO npd.address_us (id, delivery_line_1, city_name, state_code, zipcode) VALUES ('TEST00001', '123 Joe Street', 'Buffalo', '36', '14201') ON CONFLICT DO NOTHING;
INSERT INTO npd.address (id, address_us_id) VALUES ('55555555-5555-5555-5555-555555555555', 'TEST00001') ON CONFLICT DO NOTHING;
INSERT INTO npd.organization_to_address (organization_id, address_id, address_use_id) VALUES ('33333333-3333-3333-3333-333333333333', '55555555-5555-5555-5555-555555555555', 1) ON CONFLICT DO NOTHING;
INSERT INTO npd.individual_to_phone (individual_id, phone_number, phone_use_id) VALUES ('11111111-1111-1111-1111-111111111111', '5551234567', 1) ON CONFLICT DO NOTHING;