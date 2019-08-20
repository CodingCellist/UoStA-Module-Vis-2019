CREATE PROCEDURE teh6_2019_summer_project.add_alt_co_req_by_existing_co_req(
	source_module_code VARCHAR(6),
	existing_target_module_code VARCHAR(6), existing_target_academic_level VARCHAR(3),
	existing_target_academic_year VARCHAR(9), existing_target_semester_number TINYINT UNSIGNED,
	new_alternative_target_module_code VARCHAR(6)
)
BEGIN
	DECLARE existing_disjunctive_gid INT UNSIGNED;

	-- make sure the new alternative exists
	IF new_alternative_target_module_code NOT IN (SELECT `code` FROM teh6_2019_summer_project.`module`)
	THEN
		SIGNAL SQLSTATE '45001' SET message_text = "The new alternative module does not exist. Please verify the code or create the module.";
	END IF;

	-- find the GID for source->target
	SELECT DisjunctiveGroupID INTO existing_disjunctive_gid
	FROM teh6_2019_summer_project.complete_requisites
	WHERE
	(complete_requisites.source_module = source_module_code
	AND complete_requisites.academic_level = existing_target_academic_level
	AND complete_requisites.`type` = 'Co'
	AND complete_requisites.academic_year = existing_target_academic_year
	AND complete_requisites.semester_number = existing_target_semester_number
	AND complete_requisites.TargetModule = existing_target_module_code
	);

	-- make sure we actually got something back
	IF (existing_disjunctive_gid IS NULL) OR (existing_disjunctive_gid = 0)
	THEN
		SIGNAL SQLSTATE '45001' SET message_text = "There is no group to add to. Please check that all the given parameters are correct.";
	END IF;

	-- actually create the alternative
	INSERT INTO teh6_2019_summer_project.disjunctive_group
	(group_id, module_code)
	VALUES
	(existing_disjunctive_gid, new_alternative_target_module_code);
END