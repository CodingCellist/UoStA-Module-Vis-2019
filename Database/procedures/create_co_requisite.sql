CREATE PROCEDURE teh6_2019_summer_project.create_co_requisite(
	source_module_code VARCHAR(6), target_module_code VARCHAR(6),
	academic_level_concerned VARCHAR(3),
	academic_year_concerned VARCHAR(9), semester_concerned TINYINT(1) UNSIGNED
)
BEGIN
	DECLARE new_requisite_id INT UNSIGNED;
	DECLARE new_disjunctive_group_id INT UNSIGNED;

	-- make sure both modules exist
	IF target_module_code NOT IN (SELECT `code` FROM teh6_2019_summer_project.`module`)
	THEN
		SIGNAL SQLSTATE '45001' SET message_text = "The target module does not exist. Please verify the code or create the module.";
	END IF;
	IF source_module_code NOT IN (SELECT `code` FROM teh6_2019_summer_project.`module`)
	THEN
		SIGNAL SQLSTATE '45001' SET message_text = "The source module does not exist. Please verify the code or create the module.";
	END IF;

	-- make sure both modules exist
	/*
	IF (source_module_code NOT IN (SELECT code FROM teh6_2019_summer_project.module))
	THEN
		SIGNAL SQLSTATE '45001' SET message_text = "The source module does not exist. Please create it.";
	ELSEIF (target_module_code NOT IN (SELECT code FROM teh6_2019_summer_project.module))
	THEN
		SIGNAL SQLSTATE '45001' SET message_text = "The target module does not exist. Please create it.";
	END IF;
	*/
	
	-- check if the requisite already exists
	-- FixMe: doesn't work, need to cross-reference with every relevant group...
	/*
	IF (source_module_code IN (SELECT source_module FROM teh6_2019_summer_project.requisite WHERE
								(requisite.academic_year = academic_year_concerned
								AND requisite.semester_number = semester_concerned
								AND requisite.academic_level = academic_level_concerned
								AND requisite.`type` = 'Co'
								)
							 )
	 	)
 	THEN
 		SIGNAL SQLSTATE '45001' SET message_text = "A co-requisite for that module, in that year and semester, and at that level already exists. Perhaps you meant to modify one of those, or add an alternative co-requisite?";
 	END IF;
 	*/
 
 	-- create the requisite
 	INSERT INTO teh6_2019_summer_project.requisite
	(academic_year, semester_number, academic_level, `type`, source_module)
	VALUES
	(academic_year_concerned, semester_concerned, academic_level_concerned, 'Co', source_module_code);

	SELECT LAST_INSERT_ID() INTO new_requisite_id;

	-- create the requisite group
	INSERT INTO teh6_2019_summer_project.requisite_group
	(requisite_id)
	VALUES
	(new_requisite_id);

	SELECT LAST_INSERT_ID() INTO new_disjunctive_group_id;

	-- make sure the group contains at least one module
	INSERT INTO teh6_2019_summer_project.disjunctive_group
	(group_id, module_code)
	VALUES(new_disjunctive_group_id, target_module_code);
END