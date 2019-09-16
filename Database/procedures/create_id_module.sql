CREATE PROCEDURE teh6_2019_summer_project.create_id_module(
	school_name VARCHAR(127),
	module_code VARCHAR(6), module_name VARCHAR(255), academic_year VARCHAR(9),
	scotcat_credits INT(3) UNSIGNED, semester_number TINYINT(1) UNSIGNED,
	module_desc VARCHAR(2047), is_reassessable BOOL
)
BEGIN
	DECLARE module_prefix VARCHAR(2);
	DECLARE school_id_var TYPE OF teh6_2019_summer_project.school.`id`;

	SELECT SUBSTRING(module_code FROM 1 FOR 2) INTO module_prefix;

	-- make sure the module is indeed an inter-disciplinary module
	IF NOT (module_prefix <=> 'ID')
	THEN
		SIGNAL SQLSTATE '45001' SET message_text = "This procedure is only for use with inter-disciplinary (ID) modules.";
	END IF;

	-- make sure the module's school exists, otherwise we cannot find its ID 
	IF school_name NOT IN (SELECT `name` FROM teh6_2019_summer_project.school)
	THEN
		SIGNAL SQLSTATE '45001' SET message_text = "The specified school does not exist, please check the name or create it.";
	END IF;

	-- create the year if it does not already exist
	INSERT IGNORE INTO teh6_2019_summer_project.academic_year
	VALUES
	(academic_year);

	-- find the relevant school id
	SELECT school.`id` INTO school_id_var FROM teh6_2019_summer_project.school WHERE school.`name` <=> school_name;

	-- create the module if it does not already exist
	IF module_code IN (SELECT `code` FROM teh6_2019_summer_project.module)
	THEN
		-- custom warning
		SIGNAL SQLSTATE '01000' SET message_text = "The module already exists. Adding new `taught_in` entry.";
	ELSE 
		INSERT INTO teh6_2019_summer_project.module
		(code, name, description, credit_worth, re_assessable, external_requirement, school_id)
		VALUES
		(module_code, module_name, module_desc, scotcat_credits, is_reassessable, NULL, school_id_var);
	END IF;

	-- assign it to a semester
	INSERT INTO teh6_2019_summer_project.taught_in
	VALUES
	(module_code, semester_number, academic_year);
END