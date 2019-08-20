
-- CALL teh6_2019_summer_project.add_alt_pre_req_by_existing_pre_req(
--    :source_module_code,
--    :existing_target_module_code,:existing_target_academic_level,:existing_target_academic_year,:existing_target_semester_number,
--    :new_alternative_target_module_code);

CALL teh6_2019_summer_project.add_alt_pre_req_by_existing_pre_req(
	'CS3050',
	'CS2001', 'UG', '2019-2020', 1,
	'CS2101'
);
