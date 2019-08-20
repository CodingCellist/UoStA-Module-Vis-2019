CREATE TRIGGER max_100_percent_assessment_update
BEFORE UPDATE
ON graded_through FOR EACH ROW
BEGIN
	IF ((SELECT SUM(percentage) FROM graded_through WHERE
		graded_through.module_code = NEW.module_code AND
		graded_through.assessment_type = NEW.assessment_type AND
		graded_through.academic_year = NEW.academic_year) + NEW.percentage) > 100
	THEN
		SIGNAL SQLSTATE '45001' SET message_text = "The total assessment percentage of a module cannot be greater than 100%.";
	END IF;
END