CREATE PROCEDURE teh6_2019_summer_project.create_prefix_association(
	prefix_code VARCHAR(2), school_name VARCHAR(127)
)
BEGIN
	DECLARE school_id TYPE OF teh6_2019_summer_project.school.id;

	-- create the school if it doesn't exist
	IF school_name NOT IN (SELECT `name` FROM teh6_2019_summer_project.school)
	THEN
		INSERT INTO teh6_2019_summer_project.school
		(`name`)
		VALUES
		(school_name);

		SET school_id = LAST_INSERT_ID();
	ELSE
		SET school_id = (SELECT `id` FROM teh6_2019_summer_project.school WHERE school.`name` <=> school_name);
	END IF;

	-- associate the prefix with the school
	INSERT INTO teh6_2019_summer_project.prefix
	VALUES
	(prefix_code, school_id);
END