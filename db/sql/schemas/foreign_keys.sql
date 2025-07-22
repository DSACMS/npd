
--
-- Name: address address_address_us_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.address
    ADD CONSTRAINT address_address_us_id_fkey FOREIGN KEY (address_us_id) REFERENCES ndh.address_us(id);


--
-- Name: address address_address_international_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.address
    ADD CONSTRAINT address_address_international_id_fkey FOREIGN KEY (address_international_id) REFERENCES ndh.address_international(id);


--
-- Name: address address_address_nonstandard_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.address
    ADD CONSTRAINT address_address_nonstandard_id_fkey FOREIGN KEY (address_nonstandard_id) REFERENCES ndh.address_nonstandard(id);


--
-- Name: address_us address_us_county_code_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.address_us
    ADD CONSTRAINT address_us_county_code_fkey FOREIGN KEY (county_code) REFERENCES ndh.fips_county(id);


--
-- Name: address_us address_us_state_code_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.address_us
    ADD CONSTRAINT address_us_state_code_fkey FOREIGN KEY (state_code) REFERENCES ndh.fips_state(id);


--
-- Name: fips_county fips_county_fips_state_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.fips_county
    ADD CONSTRAINT fips_county_fips_state_id_fkey FOREIGN KEY (fips_state_id) REFERENCES ndh.fips_state(id);


--
-- Name: fips_county fips_county_fips_state_id_fkey1; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.fips_county
    ADD CONSTRAINT fips_county_fips_state_id_fkey1 FOREIGN KEY (fips_state_id) REFERENCES ndh.fips_state(id);


--
-- Name: individual_to_address individual_to_address_address_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_address
    ADD CONSTRAINT individual_to_address_address_id_fkey FOREIGN KEY (address_id) REFERENCES ndh.address(id);


--
-- Name: individual_to_address individual_to_address_address_type_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_address
    ADD CONSTRAINT individual_to_address_address_type_id_fkey FOREIGN KEY (address_type_id) REFERENCES ndh.fhir_address_type(id) ON DELETE CASCADE;


--
-- Name: individual_to_address individual_to_address_individual_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_address
    ADD CONSTRAINT individual_to_address_individual_id_fkey FOREIGN KEY (individual_id) REFERENCES ndh.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_clinical_credential individual_to_clinical_credential_clinical_credential_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_clinical_credential
    ADD CONSTRAINT individual_to_clinical_credential_clinical_credential_id_fkey FOREIGN KEY (clinical_credential_id) REFERENCES ndh.clinical_credential(id) ON UPDATE CASCADE;


--
-- Name: individual_to_email_address individual_to_email_address_individual_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_email_address
    ADD CONSTRAINT individual_to_email_address_individual_id_fkey FOREIGN KEY (individual_id) REFERENCES ndh.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_language_spoken individual_to_language_spoken_individual_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_language_spoken
    ADD CONSTRAINT individual_to_language_spoken_individual_id_fkey FOREIGN KEY (individual_id) REFERENCES ndh.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_language_spoken individual_to_language_spoken_language_spoken_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_language_spoken
    ADD CONSTRAINT individual_to_language_spoken_language_spoken_id_fkey FOREIGN KEY (language_spoken_id) REFERENCES ndh.language_spoken(id) ON UPDATE CASCADE;


--
-- Name: individual_to_name individual_to_name_fhir_name_type_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_name
    ADD CONSTRAINT individual_to_name_fhir_name_type_id_fkey FOREIGN KEY (fhir_name_type_id) REFERENCES ndh.fhir_name_type(id);


--
-- Name: individual_to_name individual_to_name_individual_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_name
    ADD CONSTRAINT individual_to_name_individual_id_fkey FOREIGN KEY (individual_id) REFERENCES ndh.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_nucc_taxonomy_code individual_to_nucc_taxonomy_code_individual_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_nucc_taxonomy_code
    ADD CONSTRAINT individual_to_nucc_taxonomy_code_individual_id_fkey FOREIGN KEY (individual_id) REFERENCES ndh.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_nucc_taxonomy_code individual_to_nucc_taxonomy_code_nucc_taxonomy_code_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_nucc_taxonomy_code
    ADD CONSTRAINT individual_to_nucc_taxonomy_code_nucc_taxonomy_code_id_fkey FOREIGN KEY (nucc_taxonomy_code_id) REFERENCES ndh.nucc_taxonomy_code(id);


--
-- Name: individual_to_other_identifier individual_to_other_identifier_individual_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_other_identifier
    ADD CONSTRAINT individual_to_other_identifier_individual_id_fkey FOREIGN KEY (individual_id) REFERENCES ndh.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_other_identifier individual_to_other_identifier_other_identifier_type_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_other_identifier
    ADD CONSTRAINT individual_to_other_identifier_other_identifier_type_id_fkey FOREIGN KEY (other_identifier_type_id) REFERENCES ndh.other_identifier_type(id);


--
-- Name: individual_to_other_identifier individual_to_other_identifier_state_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_other_identifier
    ADD CONSTRAINT individual_to_other_identifier_state_id_fkey FOREIGN KEY (state_id) REFERENCES ndh.fips_state(id);


--
-- Name: individual_to_phone_number individual_to_phone_number_individual_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_phone_number
    ADD CONSTRAINT individual_to_phone_number_individual_id_fkey FOREIGN KEY (individual_id) REFERENCES ndh.individual(id) ON DELETE CASCADE;


--
-- Name: individual_to_phone_number individual_to_phone_number_phone_number_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_phone_number
    ADD CONSTRAINT individual_to_phone_number_phone_number_id_fkey FOREIGN KEY (phone_number_id) REFERENCES ndh.phone_number(id);


--
-- Name: individual_to_phone_number individual_to_phone_number_phone_type_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.individual_to_phone_number
    ADD CONSTRAINT individual_to_phone_number_phone_type_id_fkey FOREIGN KEY (phone_type_id) REFERENCES ndh.phone_type(id);


--
-- Name: nucc_taxonomy_code nucc_taxonomy_code_parent_id_fkey; Type: FK CONSTRAINT; Schema: ndh; Owner: ndh
--

ALTER TABLE ONLY ndh.nucc_taxonomy_code
    ADD CONSTRAINT nucc_taxonomy_code_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES ndh.nucc_taxonomy_code(id) ON UPDATE CASCADE;

